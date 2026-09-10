import numpy as np
from ..base_model import BaseLiquidityModel, MARKET_OPEN_MIN

class MacroBreakoutModel(BaseLiquidityModel):
    """
    Model 5: Macro Breakout / Momentum Continuation (7:00 AM -> 8:00 AM - 9:00 AM News Window)
    When 8:30 AM news sweeps reference level, trades in the DIRECTION of the sweep.
    Features a trailing TP that tightens as the trade moves in favor.
    """
    def __init__(self, ref_hour=7, trail_r=1.0, tp_r_mult=2.0, **kwargs):
        super().__init__(ref_hour=ref_hour, **kwargs)
        self.trail_r = trail_r
        self.tp_r_mult = tp_r_mult

    def generate_signal(self, group):
        ref = self.get_reference_levels(group)
        if ref is None: return None
        c_win = group[(group['time_min'] >= self.win_start) & (group['time_min'] < self.win_end)]
        c_win = c_win[c_win['time_min'] >= MARKET_OPEN_MIN]
        if len(c_win) == 0: return None

        href, lref, rref = ref['h_ref'], ref['l_ref'], ref['range']
        for idx, row in c_win.iterrows():
            if row['high'] > href:
                entry = min(row['close'], href * (1 + self.slippage_pct))
                entry = max(entry, href)
                sl = entry - self.trail_r * rref
                risk = entry - sl
                tp = entry + self.tp_r_mult * rref  # Fixed TP at 2R
                return {'dir': 'LONG', 'entry_time': row['dt'], 'entry_price': entry,
                        'sl_price': sl, 'tp_price': tp, 'risk_per_unit': risk, 'post_idx': idx + 1, 'ref': ref}
            elif row['low'] < lref:
                entry = max(row['close'], lref * (1 - self.slippage_pct))
                entry = min(entry, lref)
                sl = entry + self.trail_r * rref
                risk = sl - entry
                tp = entry - self.tp_r_mult * rref
                return {'dir': 'SHORT', 'entry_time': row['dt'], 'entry_price': entry,
                        'sl_price': sl, 'tp_price': tp, 'risk_per_unit': risk, 'post_idx': idx + 1, 'ref': ref}
        return None

    def simulate_execution(self, group, signal, position_size, slippage_pct=0.0, commission=0.0):
        post = group.loc[signal['post_idx']:]
        entry_p, sl_p, tp_p = signal['entry_price'], signal['sl_price'], signal['tp_price']
        is_long = signal['dir'] == 'LONG'

        exit_p, exit_reason = None, None
        for _, pr in post.iterrows():
            if not self._is_bar_in_session(pr['time_min']):
                break
            exit_p, exit_reason = self._check_sl_tp_same_bar(pr, sl_p, tp_p, is_long, slippage_pct)
            if exit_p is not None:
                break

        if exit_p is None:
            exit_p = post.iloc[-1]['close'] if len(post) > 0 else entry_p
            exit_reason = 'EOD_CLOSE'

        pnl = position_size * ((exit_p - entry_p) if is_long else (entry_p - exit_p)) - (commission * position_size * 2)
        return {'pnl': pnl, 'exit_price': exit_p, 'exit_reason': exit_reason}
