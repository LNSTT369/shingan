import numpy as np
import pandas as pd

class PerformanceMetrics:
    """
    Quantitative analytics engine computing risk, return, alpha, beta, and drawdown metrics.
    """
    @staticmethod
    def calculate(trades_df, equity_df, benchmark_returns=None, risk_free_rate=0.02, annualization_factor=252):
        if len(trades_df) == 0:
            return {'status': 'NO_TRADES'}
            
        initial_capital = equity_df['equity'].iloc[0]
        final_capital = equity_df['equity'].iloc[-1]
        net_profit = final_capital - initial_capital
        total_return_pct = (net_profit / initial_capital) * 100.0
        
        # Win / Loss stats
        wins = trades_df[trades_df['pnl'] > 0]
        losses = trades_df[trades_df['pnl'] < 0]
        breakevens = trades_df[trades_df['pnl'] == 0]
        
        win_count = len(wins)
        loss_count = len(losses)
        total_trades = len(trades_df)
        win_rate = (win_count / total_trades) * 100.0 if total_trades > 0 else 0.0
        
        gross_profit = wins['pnl'].sum() if len(wins) > 0 else 0.0
        gross_loss = abs(losses['pnl'].sum()) if len(losses) > 0 else 0.0
        profit_factor = gross_profit / (gross_loss + 1e-8) if gross_loss > 0 else np.nan
        
        avg_win = wins['pnl'].mean() if len(wins) > 0 else 0.0
        avg_loss = losses['pnl'].mean() if len(losses) > 0 else 0.0
        avg_win_r = wins['r_mult'].mean() if 'r_mult' in wins else 0.0
        avg_loss_r = losses['r_mult'].mean() if 'r_mult' in losses else 0.0
        win_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else np.nan
        
        # Drawdown computation
        cum_max = equity_df['equity'].cummax()
        drawdown_series = (cum_max - equity_df['equity']) / cum_max
        max_drawdown_pct = drawdown_series.max() * 100.0
        
        # Risk-adjusted metrics
        r_series = trades_df['r_mult'] if 'r_mult' in trades_df else trades_df['pnl'] / (initial_capital * 0.01)
        mean_r = r_series.mean()
        std_r = r_series.std()
        sharpe_annual = (mean_r / (std_r + 1e-8)) * np.sqrt(annualization_factor) if std_r > 0 else 0.0
        
        downside_std = r_series[r_series < 0].std()
        sortino_annual = (mean_r / (downside_std + 1e-8)) * np.sqrt(annualization_factor) if downside_std > 0 else 0.0
        
        # Benchmark correlation & beta
        correlation = np.nan
        beta = np.nan
        if benchmark_returns is not None and len(benchmark_returns) > 0:
            daily_strat = trades_df.groupby('date')['r_mult'].sum()
            merged = pd.DataFrame({'strat': daily_strat, 'bench': benchmark_returns}).dropna()
            if len(merged) > 10:
                correlation = merged['strat'].corr(merged['bench'])
                cov = np.cov(merged['strat'], merged['bench'])[0][1]
                var_bench = np.var(merged['bench'])
                beta = cov / (var_bench + 1e-8)
                
        return {
            'initial_capital': initial_capital,
            'final_capital': final_capital,
            'net_profit': net_profit,
            'total_return_pct': total_return_pct,
            'total_trades': total_trades,
            'win_rate_pct': win_rate,
            'winning_trades': win_count,
            'losing_trades': loss_count,
            'breakeven_trades': len(breakevens),
            'profit_factor': profit_factor,
            'max_drawdown_pct': max_drawdown_pct,
            'sharpe_ratio': sharpe_annual,
            'sortino_ratio': sortino_annual,
            'average_win': avg_win,
            'average_loss': avg_loss,
            'average_win_r': avg_win_r,
            'average_loss_r': avg_loss_r,
            'win_loss_ratio': win_loss_ratio,
            'market_correlation': correlation,
            'market_beta': beta
        }
