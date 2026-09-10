import numpy as np
from .confirmation_reversal import ConfirmationReversalModel

class MultiTargetScaleoutModel(ConfirmationReversalModel):
    """
    Model 3: Multi-Target Scale-Out with Breakeven Trailing Stop
    50% position closed at TP1 (Midpoint).
    Stop loss on remaining 50% moved to Breakeven (Entry).
    50% runner closed at TP2 (Opposite Level).
    Stop placement uses 0.6 * range from sweep extreme to reduce full-SL rate.
    """
    def __init__(self, ref_hour=8, sl_range_mult=0.6, **kwargs):
        super().__init__(ref_hour=ref_hour, **kwargs)
        self.sl_range_mult = sl_range_mult

    def generate_signal(self, group):
        ref = self.get_reference_levels(group)
        if ref is None: return None
        c_win = group[(group['time_min'] >= self.win_start) & (group['time_min'] < self.win_end)]
        from ..base_model import MARKET_OPEN_MIN
        c_win = c_win[c_win['time_min'] >= MARKET_OPEN_MIN]
        if len(c_win) == 0: return None

        href, lref, rref = ref['h_ref'], ref['l_ref'], ref['range']
        sweep_occurred, sweep_dir, sweep_ext = False, None, None

        for idx, row in c_win.iterrows():
            if not sweep_occurred:
                if row['high'] > href: sweep_occurred, sweep_dir, sweep_ext = True, 'HIGH', row['high']
                elif row['low'] < lref: sweep_occurred, sweep_dir, sweep_ext = True, 'LOW', row['low']

            if sweep_occurred:
                if sweep_dir == 'HIGH':
                    sweep_ext = max(sweep_ext, row['high'])
                    if row['close'] < href:
                        entry = row['close']
                        # Tighter stop: sweep extreme + reduced buffer
                        sl = sweep_ext + self.sl_range_mult * self.buffer_pct * rref / 0.05
                        risk = sl - entry
                        tp = lref
                        if risk > 0.01 and ((entry - tp) / risk >= self.min_rr):
                            return {
                                'dir': 'SHORT', 'entry_time': row['dt'], 'entry_price': entry,
                                'sl_price': sl, 'tp_price': tp, 'tp1_price': ref['mid'], 'tp2_price': lref,
                                'risk_per_unit': risk, 'post_idx': idx + 1, 'ref': ref
                            }
                        break
                elif sweep_dir == 'LOW':
                    sweep_ext = min(sweep_ext, row['low'])
                    if row['close'] > lref:
                        entry = row['close']
                        sl = sweep_ext - self.sl_range_mult * self.buffer_pct * rref / 0.05
                        risk = entry - sl
                        tp = href
                        if risk > 0.01 and ((tp - entry) / risk >= self.min_rr):
                            return {
                                'dir': 'LONG', 'entry_time': row['dt'], 'entry_price': entry,
                                'sl_price': sl, 'tp_price': tp, 'tp1_price': ref['mid'], 'tp2_price': href,
                                'risk_per_unit': risk, 'post_idx': idx + 1, 'ref': ref
                            }
                        break
        return None

    def simulate_execution(self, group, signal, position_size, slippage_pct=0.0, commission=0.0):
        post = group.loc[signal['post_idx']:]
        entry_p, sl_p = signal['entry_price'], signal['sl_price']
        tp1_p, tp2_p = signal['tp1_price'], signal['tp2_price']
        is_short = signal['dir'] == 'SHORT'

        half_size = position_size / 2.0
        tp1_hit = False
        current_sl = sl_p

        exit1_p, exit2_p = None, None
        exit_reason = None

        for _, pr in post.iterrows():
            if not self._is_bar_in_session(pr['time_min']):
                break

            if is_short:
                # Check SL first
                sl_hit = pr['high'] >= current_sl
                tp1_hit_now = (not tp1_hit) and pr['low'] <= tp1_p
                tp2_hit = tp1_hit and pr['low'] <= tp2_p

                if sl_hit and not tp1_hit:
                    # Full SL: both halves stopped out
                    exit1_p = current_sl * (1 + slippage_pct)
                    exit2_p = current_sl * (1 + slippage_pct)
                    exit_reason = 'FULL_SL'
                    break
                elif sl_hit and tp1_hit:
                    # SL after TP1: second half at breakeven
                    exit2_p = entry_p
                    exit_reason = 'TP1_THEN_BE'
                    break

                if tp1_hit_now:
                    tp1_hit = True
                    exit1_p = tp1_p * (1 - slippage_pct)
                    current_sl = entry_p  # Move to Breakeven

                if tp1_hit and pr['low'] <= tp2_p:
                    exit2_p = tp2_p * (1 - slippage_pct)
                    exit_reason = 'TP1_AND_TP2'
                    break
            else:
                sl_hit = pr['low'] <= current_sl
                tp1_hit_now = (not tp1_hit) and pr['high'] >= tp1_p
                tp2_hit = tp1_hit and pr['high'] >= tp2_p

                if sl_hit and not tp1_hit:
                    exit1_p = current_sl * (1 - slippage_pct)
                    exit2_p = current_sl * (1 - slippage_pct)
                    exit_reason = 'FULL_SL'
                    break
                elif sl_hit and tp1_hit:
                    exit2_p = entry_p
                    exit_reason = 'TP1_THEN_BE'
                    break

                if tp1_hit_now:
                    tp1_hit = True
                    exit1_p = tp1_p * (1 + slippage_pct)
                    current_sl = entry_p

                if tp1_hit and pr['high'] >= tp2_p:
                    exit2_p = tp2_p * (1 + slippage_pct)
                    exit_reason = 'TP1_AND_TP2'
                    break

        last_c = post.iloc[-1]['close'] if len(post) > 0 else entry_p
        if exit1_p is None: exit1_p = last_c
        if exit2_p is None: exit2_p = last_c; exit_reason = 'EOD'

        pnl1 = half_size * ((entry_p - exit1_p) if is_short else (exit1_p - entry_p))
        pnl2 = half_size * ((entry_p - exit2_p) if is_short else (exit2_p - entry_p))
        # Commission charged per exit leg, not flat on full size
        total_pnl = pnl1 + pnl2 - (commission * half_size * 2) - (commission * half_size * 2)

        return {'pnl': total_pnl, 'exit_price': (exit1_p + exit2_p)/2.0, 'exit_reason': exit_reason}
