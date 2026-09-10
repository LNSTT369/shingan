import numpy as np
from collections import deque
from .base_model import BaseLiquidityModel, MARKET_OPEN_MIN, MARKET_CLOSE_MIN

class HybridORBModel(BaseLiquidityModel):
    """
    Hybrid Zarattini 5m + Valkyrie 15m x RVOL/phi + ORBPLUS 2R
    ponytail: 5m OR stop-entry only, RVOL>=1.5 phi[0.6,2.0] is the edge (not bloat)
    retrace removed: WR 3.8% never fills, 1.21 Sharpe is stop-entry (paper 6.2)
    """
    def __init__(self, or_minutes=5, min_rvol=1.5, phi_min=0.6, phi_max=2.0, target_r=2.0,
                 use_sequence=None, tick=0.01, **kwargs):
        super().__init__(ref_hour=9, slippage_pct=kwargs.get('slippage_pct', 0.0001), **kwargs)
        self.or_minutes = or_minutes
        self.or_start = MARKET_OPEN_MIN
        self.or_end = MARKET_OPEN_MIN + or_minutes
        self.min_rvol = min_rvol
        self.phi_min = phi_min
        self.phi_max = phi_max
        self.target_r = target_r
        self.use_sequence = use_sequence if use_sequence is not None else (or_minutes >= 15)
        self.tick = tick
        self._vol_history = deque(maxlen=14)
        self._atr_history = deque(maxlen=14)
        self._daily_highs = deque(maxlen=15)
        self._daily_lows = deque(maxlen=15)
        self._daily_closes = deque(maxlen=15)

    def _compute_atr14(self, group):
        d_high = group['high'].max()
        d_low = group['low'].min()
        d_close = group.iloc[-1]['close']
        prev_c = self._daily_closes[-1] if self._daily_closes else None
        tr = max(d_high - d_low, abs(d_high - prev_c), abs(d_low - prev_c)) if prev_c is not None else d_high - d_low
        self._daily_highs.append(d_high)
        self._daily_lows.append(d_low)
        self._daily_closes.append(d_close)
        if len(self._daily_highs) < 2:
            return 1.0
        # ponytail: one mean, not three branches — deque is 14 capped
        atr = float(np.mean(self._atr_history)) if self._atr_history else float(np.mean([h - l for h, l in zip(self._daily_highs, self._daily_lows) if h > l]) or 1.0)
        self._atr_history.append(tr)
        return atr if atr > 0.01 else 1.0

    def _get_or_bars(self, group):
        return group[(group['time_min'] >= self.or_start) & (group['time_min'] < self.or_end)].sort_values('time_min')

    def _compute_rvol(self, or_bars):
        today_vol = float(or_bars['volume'].sum()) if 'volume' in or_bars else 1000.0
        rvol = today_vol / max(1.0, float(np.mean(self._vol_history))) if self._vol_history else 1.0
        self._vol_history.append(today_vol)
        return rvol, today_vol

    def get_or_levels(self, group):
        or_bars = self._get_or_bars(group)
        if len(or_bars) == 0 or (self.or_minutes == 15 and len(or_bars) < 3):
            return None
        o = float(or_bars.iloc[0]['open'])
        h = float(or_bars['high'].max())
        l = float(or_bars['low'].min())
        c = float(or_bars.iloc[-1]['close'])
        spread = h - l
        if spread <= 0:
            return None
        h_time = int(or_bars[or_bars['high'] == h].iloc[0]['time_min'])
        l_time = int(or_bars[or_bars['low'] == l].iloc[0]['time_min'])
        return {'or_high': h, 'or_low': l, 'or_open': o, 'or_close': c, 'spread': spread,
                'h_time': h_time, 'l_time': l_time, 'is_green': c >= o, 'low_first': l_time < h_time, 'or_bars': or_bars}

    def _evaluate_signal(self, or_levels, rvol, phi):
        is_green, low_first = or_levels['is_green'], or_levels['low_first']
        if rvol < self.min_rvol:
            return None, f'RVOL {rvol:.2f} < {self.min_rvol}'
        if phi < self.phi_min or phi > self.phi_max:
            return None, f'phi {phi:.2f} outside [{self.phi_min},{self.phi_max}]'
        if self.use_sequence:
            if low_first and is_green:
                return 'LONG', 'confirmed'
            if not low_first and not is_green:
                return 'SHORT', 'confirmed'
            return None, 'trap lockout'
        return ('LONG' if is_green else 'SHORT'), 'confirmed'

    def generate_signal(self, group):
        atr14 = self._compute_atr14(group)
        or_levels = self.get_or_levels(group)
        if or_levels is None:
            return None
        rvol, _ = self._compute_rvol(or_levels['or_bars'])
        phi = or_levels['spread'] / max(atr14, 0.01)
        direction, _ = self._evaluate_signal(or_levels, rvol, phi)
        if direction is None:
            return None
        h, l = or_levels['or_high'], or_levels['or_low']
        if direction == 'LONG':
            entry_stop, sl = h + self.tick, l - self.tick
        else:
            entry_stop, sl = l - self.tick, h + self.tick
        risk = abs(entry_stop - sl)
        if risk <= 0.01:
            return None
        return {'dir': direction, 'entry_stop': entry_stop, 'sl_price': sl, 'risk_per_unit': risk,
                'or_high': h, 'or_low': l, 'spread': or_levels['spread'], 'rvol': rvol, 'phi': phi,
                'atr14': atr14, 'target_r': self.target_r, 'or_end': self.or_end,
                'ref': {'h_ref': h, 'l_ref': l, 'range': or_levels['spread'], 'mid': (h+l)/2}}

    def simulate_execution(self, group, signal, position_size, slippage_pct=0.0, commission=0.0):
        if signal is None:
            return {'pnl': 0.0, 'exit_price': 0.0, 'exit_reason': 'NO_SIGNAL'}
        entry_stop, sl, risk = signal['entry_stop'], signal['sl_price'], signal['risk_per_unit']
        is_long = signal['dir'] == 'LONG'
        tp = entry_stop + self.target_r * risk if is_long else entry_stop - self.target_r * risk
        post = group[group['time_min'] >= signal['or_end']].sort_values('time_min')
        if len(post) == 0:
            return {'pnl': 0.0, 'exit_price': entry_stop, 'exit_reason': 'NO_POST_BARS'}
        filled = False
        entry_price = entry_stop
        be_level = None
        for _, row in post.iterrows():
            tm = int(row['time_min'])
            if tm >= MARKET_CLOSE_MIN:
                break
            if not filled:
                triggered = (row['high'] >= entry_stop) if is_long else (row['low'] <= entry_stop)
                if not triggered:
                    continue
                entry_price = entry_stop * (1 + slippage_pct) if is_long else entry_stop * (1 - slippage_pct)
                filled = True
                be_level = entry_price
                continue
            if filled:
                if tm >= 900:
                    close = float(row['close'])
                    unreal = (close - entry_price)/entry_price*100 if is_long else (entry_price - close)/entry_price*100
                    if unreal >= 1.0:
                        pnl = position_size * ((close - entry_price) if is_long else (entry_price - close)) - commission * position_size * 2
                        return {'pnl': pnl, 'exit_price': close, 'exit_reason': 'PROFIT_LOCK_3PM'}
                if be_level is not None:
                    one_r = entry_price + risk if is_long else entry_price - risk
                    if (row['high'] >= one_r) if is_long else (row['low'] <= one_r):
                        sl = be_level
                exit_p, reason = self._check_sl_tp_same_bar(row, sl, tp, not is_long, slippage_pct)
                if exit_p is not None:
                    pnl = position_size * ((exit_p - entry_price) if is_long else (entry_price - exit_p)) - commission * position_size * 2
                    return {'pnl': pnl, 'exit_price': exit_p, 'exit_reason': reason}
        if not filled:
            return {'pnl': 0.0, 'exit_price': entry_stop, 'exit_reason': 'NO_FILL'}
        exit_price = float(post.iloc[-1]['close'])
        pnl = position_size * ((exit_price - entry_price) if is_long else (entry_price - exit_price)) - commission * position_size * 2
        return {'pnl': pnl, 'exit_price': exit_price, 'exit_reason': 'EOD'}
