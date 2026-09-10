import numpy as np
from ..base_model import BaseLiquidityModel, MARKET_OPEN_MIN

class NaiveSweepReversalModel(BaseLiquidityModel):
    """
    Model 1: Naive Limit Reversal
    Immediately enters short at ref_high breach (or long at ref_low breach).
    Stop Loss: fixed multiple of reference range. Target: Opposite reference level.
    """
    def __init__(self, ref_hour=8, sl_mult=1.0, **kwargs):
        super().__init__(ref_hour=ref_hour, **kwargs)
        self.sl_mult = sl_mult

    def generate_signal(self, group):
        ref = self.get_reference_levels(group)
        if ref is None:
            return None

        c_win = group[(group['time_min'] >= self.win_start) & (group['time_min'] < self.win_end)]
        # Filter to regular market hours only
        c_win = c_win[c_win['time_min'] >= MARKET_OPEN_MIN]
        if len(c_win) == 0:
            return None

        href, lref, rref = ref['h_ref'], ref['l_ref'], ref['range']

        for idx, row in c_win.iterrows():
            if row['high'] > href:
                # Realistic fill: assume worst-case fill within the bar (close or ref+slippage)
                entry = min(row['close'], href * (1 + self.slippage_pct))
                entry = max(entry, href)  # Cannot fill below the level we're shorting at
                sl = href + self.sl_mult * rref
                risk = sl - entry
                if risk <= 0.01:
                    continue
                return {
                    'dir': 'SHORT', 'entry_time': row['dt'], 'entry_price': entry,
                    'sl_price': sl, 'tp_price': lref, 'risk_per_unit': risk,
                    'post_idx': idx + 1, 'ref': ref
                }
            elif row['low'] < lref:
                entry = max(row['close'], lref * (1 - self.slippage_pct))
                entry = min(entry, lref)  # Cannot fill above the level we're longing at
                sl = lref - self.sl_mult * rref
                risk = entry - sl
                if risk <= 0.01:
                    continue
                return {
                    'dir': 'LONG', 'entry_time': row['dt'], 'entry_price': entry,
                    'sl_price': sl, 'tp_price': href, 'risk_per_unit': risk,
                    'post_idx': idx + 1, 'ref': ref
                }
        return None

    def simulate_execution(self, group, signal, position_size, slippage_pct=0.0, commission=0.0):
        post = group.loc[signal['post_idx']:]
        entry_p = signal['entry_price']
        sl_p = signal['sl_price']
        tp_p = signal['tp_price']
        is_short = signal['dir'] == 'SHORT'

        exit_p = None
        exit_reason = None

        for _, r in post.iterrows():
            if not self._is_bar_in_session(r['time_min']):
                break
            exit_p, exit_reason = self._check_sl_tp_same_bar(r, sl_p, tp_p, is_short, slippage_pct)
            if exit_p is not None:
                break

        if exit_p is None:
            exit_p = post.iloc[-1]['close'] if len(post) > 0 else entry_p
            exit_reason = 'EOD'

        pnl_per_unit = (entry_p - exit_p) if is_short else (exit_p - entry_p)
        total_pnl = position_size * pnl_per_unit - (commission * position_size * 2)
        return {'pnl': total_pnl, 'exit_price': exit_p, 'exit_reason': exit_reason}
