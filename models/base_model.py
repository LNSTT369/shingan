from abc import ABC, abstractmethod
import numpy as np

MARKET_OPEN_MIN = 570   # 9:30 AM ET
MARKET_CLOSE_MIN = 960  # 4:00 PM ET

class BaseLiquidityModel(ABC):
    """
    Abstract Base Class for all hourly liquidity trading strategies.
    """
    def __init__(self, ref_hour=8, slippage_pct=0.0001, **kwargs):
        self.ref_hour = ref_hour
        self.ref_start = ref_hour * 60
        self.ref_end = (ref_hour + 1) * 60
        self.win_start = (ref_hour + 1) * 60
        self.win_end = (ref_hour + 2) * 60
        self.slippage_pct = slippage_pct
        self.kwargs = kwargs

    def get_reference_levels(self, group):
        c_ref = group[(group['time_min'] >= self.ref_start) & (group['time_min'] < self.ref_end)]
        if len(c_ref) == 0:
            return None
        href = c_ref['high'].max()
        lref = c_ref['low'].min()
        rref = href - lref
        if rref <= 0:
            return None
        return {
            'h_ref': href,
            'l_ref': lref,
            'range': rref,
            'mid': (href + lref) / 2.0
        }

    def _is_bar_in_session(self, time_min):
        """Return True if the bar falls within regular market hours (9:30 AM - 4:00 PM)."""
        return MARKET_OPEN_MIN <= time_min < MARKET_CLOSE_MIN

    def _check_sl_tp_same_bar(self, row, sl_p, tp_p, is_short, slippage_pct):
        """
        Simulate intra-bar SL/TP ordering. When both SL and TP are breached on the
        same bar, randomly determine which fills first using the bar's OHLC midpoint
        as a proxy for the most probable touch sequence.
        Returns (exit_price, exit_reason) or (None, None) if neither triggered.
        """
        sl_hit = False
        tp_hit = False
        if is_short:
            sl_hit = row['high'] >= sl_p
            tp_hit = row['low'] <= tp_p
        else:
            sl_hit = row['low'] <= sl_p
            tp_hit = row['high'] >= tp_p

        if sl_hit and tp_hit:
            # Both triggered on same bar. Use midpoint to decide most likely order.
            bar_mid = (row['high'] + row['low']) / 2.0
            if is_short:
                # For short: SL is above entry, TP is below. Check which is closer to midpoint.
                sl_dist = abs(row['high'] - sl_p)
                tp_dist = abs(row['low'] - tp_p)
            else:
                sl_dist = abs(row['low'] - sl_p)
                tp_dist = abs(row['high'] - tp_p)
            # The level closer to the bar midpoint likely touched first
            if sl_dist < tp_dist:
                return sl_p * (1 + slippage_pct) if is_short else sl_p * (1 - slippage_pct), 'SL'
            elif tp_dist < sl_dist:
                return tp_p * (1 - slippage_pct) if is_short else tp_p * (1 + slippage_pct), 'TP'
            else:
                # Equal distance: assume SL fills first (conservative)
                return (sl_p * (1 + slippage_pct) if is_short else sl_p * (1 - slippage_pct)), 'SL'

        if sl_hit:
            return (sl_p * (1 + slippage_pct) if is_short else sl_p * (1 - slippage_pct)), 'SL'
        if tp_hit:
            return (tp_p * (1 - slippage_pct) if is_short else tp_p * (1 + slippage_pct)), 'TP'
        return None, None

    @abstractmethod
    def generate_signal(self, group):
        pass

    @abstractmethod
    def simulate_execution(self, group, signal, position_size, slippage_pct=0.0, commission=0.0):
        pass
