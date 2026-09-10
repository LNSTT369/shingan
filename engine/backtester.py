import pandas as pd
import numpy as np
from .metrics import PerformanceMetrics

class Backtester:
    """
    Event-driven vectorized backtesting execution simulator for hourly liquidity models.
    Supports fixed fractional position sizing, stop-loss trailing, multi-target scaling,
    commissions, and slippage modeling.
    """
    def __init__(self, initial_capital=50000.0, risk_pct=0.01, fixed_risk_dollar=None,
                 commission_per_unit=0.005, slippage_pct=0.0001):
        self.initial_capital = initial_capital
        self.risk_pct = risk_pct
        self.fixed_risk_dollar = fixed_risk_dollar
        self.commission_per_unit = commission_per_unit
        self.slippage_pct = slippage_pct

    def run(self, df, strategy_model, benchmark_df=None):
        """
        Executes the strategy model across the entire dataset day by day.
        benchmark_df should be a separate ticker (e.g. SPY) for proper beta calculation.
        """
        equity = self.initial_capital
        trade_log = []
        daily_equity = [{'date': df['date'].iloc[0], 'equity': self.initial_capital}]

        for dt, group in df.groupby('date'):
            trade_signal = strategy_model.generate_signal(group)

            if trade_signal is None:
                daily_equity.append({'date': dt, 'equity': equity})
                continue

            # Risk Sizing
            risk_dollar = self.fixed_risk_dollar if self.fixed_risk_dollar else equity * self.risk_pct
            risk_per_unit = trade_signal['risk_per_unit']

            if risk_per_unit <= 0:
                daily_equity.append({'date': dt, 'equity': equity})
                continue

            position_size = risk_dollar / risk_per_unit

            # Simulate trade lifecycle
            trade_result = strategy_model.simulate_execution(
                group=group,
                signal=trade_signal,
                position_size=position_size,
                slippage_pct=self.slippage_pct,
                commission=self.commission_per_unit
            )

            net_pnl = trade_result['pnl']
            equity += net_pnl
            daily_equity.append({'date': dt, 'equity': equity})

            trade_log.append({
                'date': dt,
                'dir': trade_signal['dir'],
                'entry_time': trade_signal['entry_time'],
                'entry_price': trade_signal['entry_price'],
                'sl_price': trade_signal['sl_price'],
                'tp1_price': trade_signal.get('tp1_price', np.nan),
                'tp2_price': trade_signal.get('tp2_price', np.nan),
                'risk_dollar': risk_dollar,
                'pnl': net_pnl,
                'r_mult': net_pnl / risk_dollar,
                'exit_reason': trade_result['exit_reason'],
                'exit_price': trade_result['exit_price'],
                'ending_equity': equity
            })

        trades_df = pd.DataFrame(trade_log)
        eq_df = pd.DataFrame(daily_equity)

        bench_ret = None
        if benchmark_df is not None and benchmark_df is not df:
            bench_ret = benchmark_df.groupby('date')['close'].last().pct_change().dropna()

        metrics = PerformanceMetrics.calculate(trades_df, eq_df, benchmark_returns=bench_ret)
        return trades_df, eq_df, metrics
