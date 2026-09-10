import numpy as np
from ..base_model import BaseLiquidityModel, MARKET_OPEN_MIN

class ConfirmationReversalModel(BaseLiquidityModel):
    """
    Model 2: Reversal Confirmation (False Breakout / Liquidity Trap)
    Waits for a 5m bar to close back inside the reference range.
    Stop Loss: Local sweep extreme (+ buffer). Target: Opposite reference level.
    """
    def __init__(self, ref_hour=8, buffer_pct=0.05, min_rr=0.0, **kwargs):
        super().__init__(ref_hour=ref_hour, **kwargs)
        self.buffer_pct = buffer_pct
        self.min_rr = min_rr

    def generate_signal(self, group):
        ref = self.get_reference_levels(group)
        if ref is None: return None
        c_win = group[(group['time_min'] >= self.win_start) & (group['time_min'] < self.win_end)]
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
                        sl = sweep_ext + self.buffer_pct * rref
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
                        sl = sweep_ext - self.buffer_pct * rref
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
        entry_p, sl_p, tp_p = signal['entry_price'], signal['sl_price'], signal['tp_price']
        is_short = signal['dir'] == 'SHORT'

        exit_p, exit_reason = None, None
        for _, r in post.iterrows():
            if not self._is_bar_in_session(r['time_min']):
                break
            exit_p, exit_reason = self._check_sl_tp_same_bar(r, sl_p, tp_p, is_short, slippage_pct)
            if exit_p is not None:
                break

        if exit_p is None:
            exit_p = post.iloc[-1]['close'] if len(post) > 0 else entry_p
            exit_reason = 'EOD'

        pnl = position_size * ((entry_p - exit_p) if is_short else (exit_p - entry_p)) - (commission * position_size * 2)
        return {'pnl': pnl, 'exit_price': exit_p, 'exit_reason': exit_reason}
