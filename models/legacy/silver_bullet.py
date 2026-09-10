import numpy as np
from .multi_target_scaleout import MultiTargetScaleoutModel
from ..base_model import MARKET_OPEN_MIN

class SilverBulletModel(MultiTargetScaleoutModel):
    """
    Model 4: ICT Silver Bullet (9:00 AM Reference -> 10:00 AM - 11:00 AM Window)
    Requires:
      1. Liquidity sweep of reference high/low
      2. Displacement bar (body > 60% of range, closing strongly in reversal direction)
      3. Fair Value Gap (FVG) formed by the displacement (gap between candle 1 high and candle 3 low for short, vice versa for long)
    Entry on the close of the displacement bar if FVG exists.
    """
    def __init__(self, ref_hour=9, min_displacement_pct=0.60, **kwargs):
        super().__init__(ref_hour=ref_hour, **kwargs)
        self.min_displacement_pct = min_displacement_pct

    def _has_fvg(self, bars, is_short):
        """
        Check for a Fair Value Gap in the last 3 bars.
        For SHORT: bar1.high < bar3.low (bearish FVG above price)
        For LONG: bar1.low > bar3.high (bullish FVG below price)
        bars is a list of 3 consecutive rows (oldest to newest).
        """
        if len(bars) < 3:
            return False, 0.0
        bar1, bar2, bar3 = bars[-3], bars[-2], bars[-1]
        if is_short:
            # Bearish FVG: gap between bar1's low and bar3's high
            fvg_top = bar1['low']
            fvg_bottom = bar3['high']
            has_gap = fvg_top > fvg_bottom
            fvg_size = fvg_top - fvg_bottom if has_gap else 0.0
        else:
            # Bullish FVG: gap between bar1's high and bar3's low
            fvg_bottom = bar1['high']
            fvg_top = bar3['low']
            has_gap = fvg_top > fvg_bottom
            fvg_size = fvg_top - fvg_bottom if has_gap else 0.0
        return has_gap, fvg_size

    def _is_displacement(self, row, is_short):
        """Check if a bar shows displacement (strong directional move)."""
        bar_range = row['high'] - row['low']
        if bar_range <= 0:
            return False
        body = abs(row['close'] - row['open'])
        body_pct = body / bar_range

        if body_pct < self.min_displacement_pct:
            return False

        # Direction must align with the trade
        if is_short:
            return row['close'] < row['open']  # Bearish displacement
        else:
            return row['close'] > row['open']  # Bullish displacement

    def generate_signal(self, group):
        ref = self.get_reference_levels(group)
        if ref is None: return None
        c_win = group[(group['time_min'] >= self.win_start) & (group['time_min'] < self.win_end)]
        c_win = c_win[c_win['time_min'] >= MARKET_OPEN_MIN]
        if len(c_win) < 3: return None

        href, lref, rref = ref['h_ref'], ref['l_ref'], ref['range']
        sweep_occurred, sweep_dir, sweep_ext = False, None, None

        bars_buffer = []

        for idx, row in c_win.iterrows():
            bars_buffer.append(row)
            if len(bars_buffer) > 3:
                bars_buffer = bars_buffer[-3:]

            if not sweep_occurred:
                if row['high'] > href:
                    sweep_occurred, sweep_dir, sweep_ext = True, 'HIGH', row['high']
                elif row['low'] < lref:
                    sweep_occurred, sweep_dir, sweep_ext = True, 'LOW', row['low']

            if sweep_occurred:
                if sweep_dir == 'HIGH':
                    sweep_ext = max(sweep_ext, row['high'])
                    # Need sweep to have happened, then displacement + FVG confirmation
                    if row['close'] < href:
                        # Check for bearish displacement
                        if self._is_displacement(row, is_short=True):
                            # Check for FVG in last 3 bars
                            has_fvg, fvg_size = self._has_fvg(bars_buffer, is_short=True)
                            if has_fvg and fvg_size >= 0.10 * rref:
                                entry = row['close']
                                sl = sweep_ext + self.buffer_pct * rref
                                risk = sl - entry
                                tp = lref
                                if risk > 0.01 and ((entry - tp) / risk >= self.min_rr):
                                    return {
                                        'dir': 'SHORT', 'entry_time': row['dt'], 'entry_price': entry,
                                        'sl_price': sl, 'tp_price': tp, 'tp1_price': ref['mid'], 'tp2_price': lref,
                                        'risk_per_unit': risk, 'post_idx': idx + 1, 'ref': ref,
                                        'fvg_size': fvg_size
                                    }
                                break
                elif sweep_dir == 'LOW':
                    sweep_ext = min(sweep_ext, row['low'])
                    if row['close'] > lref:
                        if self._is_displacement(row, is_short=False):
                            has_fvg, fvg_size = self._has_fvg(bars_buffer, is_short=False)
                            if has_fvg and fvg_size >= 0.10 * rref:
                                entry = row['close']
                                sl = sweep_ext - self.buffer_pct * rref
                                risk = entry - sl
                                tp = href
                                if risk > 0.01 and ((tp - entry) / risk >= self.min_rr):
                                    return {
                                        'dir': 'LONG', 'entry_time': row['dt'], 'entry_price': entry,
                                        'sl_price': sl, 'tp_price': tp, 'tp1_price': ref['mid'], 'tp2_price': href,
                                        'risk_per_unit': risk, 'post_idx': idx + 1, 'ref': ref,
                                        'fvg_size': fvg_size
                                    }
                                break
        return None
