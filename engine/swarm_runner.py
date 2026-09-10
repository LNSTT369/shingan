import concurrent.futures, itertools
import pandas as pd
from .data_loader import DataLoader
from .backtester import Backtester
from .metrics import PerformanceMetrics

class SwarmRunner:
    def __init__(self, data_loader=None):
        self.data_loader = data_loader or DataLoader()
        self._spy_cache = None

    def _get_spy_benchmark(self, s, e):
        if self._spy_cache is None:
            try: self._spy_cache = self.data_loader.load_ticker('SPY', s, e)
            except: self._spy_cache = None
        return self._spy_cache

    # ponytail: single Top-K portfolio engine — replaces run_model_backtest.py + run_hybrid_wfo.py + run_hourly_scan.py loops
    def run_hybrid_portfolio(self, tickers, start_year, end_year, or_minutes=5, min_rvol=1.5, phi_min=0.6, phi_max=2.0, target_r=2.0, top_k=5, capital=50000, risk=0.01):
        from models.hybrid_orb import HybridORBModel
        ticker_dfs = {t: self.data_loader.load_ticker(t, start_year, end_year) for t in tickers if self._exists(t, start_year, end_year)}
        ticker_dfs = {t: df for t, df in ticker_dfs.items() if len(df) > 0}
        all_dates = sorted(set().union(*[set(df['date'].unique()) for df in ticker_dfs.values()]))
        models = {t: HybridORBModel(or_minutes=or_minutes, min_rvol=min_rvol, phi_min=phi_min, phi_max=phi_max, target_r=target_r) for t in ticker_dfs}
        equity, trade_log = capital, []
        for dt in all_dates:
            cands = []
            for t, df in ticker_dfs.items():
                g = df[df['date'] == dt]
                if len(g) == 0: continue
                sig = models[t].generate_signal(g)
                if sig: cands.append((t, sig, g, sig['rvol']))
            cands.sort(key=lambda x: x[3], reverse=True)
            for t, sig, grp, rvol in cands[:top_k]:
                pos = (equity * risk) / sig['risk_per_unit'] if sig['risk_per_unit'] > 0 else 0
                if pos <= 0: continue
                res = models[t].simulate_execution(grp, sig, pos, 0.0001, 0.005)
                equity += res['pnl']
                trade_log.append({'date': dt, 'ticker': t, 'dir': sig['dir'], 'rvol': rvol, 'phi': sig['phi'], 'pnl': res['pnl'], 'r_mult': res['pnl']/(equity*risk) if equity else 0, 'exit_reason': res['exit_reason'], 'exit_price': res['exit_price']})
        trades_df = pd.DataFrame(trade_log)
        # rebuild equity curve from daily pnl for metrics
        if len(trades_df):
            daily = trades_df.groupby('date')['pnl'].sum()
            eq_vals, cum = [capital], capital
            for d in all_dates:
                cum += daily.get(d, 0)
                eq_vals.append(cum)
            eq_df = pd.DataFrame({'date': [all_dates[0]]+all_dates, 'equity': eq_vals})
        else:
            eq_df = pd.DataFrame({'date': all_dates, 'equity': [capital]*len(all_dates)})
        bench = self._get_spy_benchmark(start_year, end_year)
        bench_ret = bench.groupby('date')['close'].last().pct_change().dropna() if bench is not None else None
        metrics = PerformanceMetrics.calculate(trades_df, eq_df, bench_ret)
        return trades_df, eq_df, metrics

    def _exists(self, t, s, e):
        try: self.data_loader.load_ticker(t, s, e); return True
        except: return False

    def run_hour_worker(self, model_class, ref_hour, ticker, start_year=2010, end_year=2026, **model_kwargs):
        try:
            df = self.data_loader.load_ticker(ticker=ticker, start_year=start_year, end_year=end_year)
            model = model_class(ref_hour=ref_hour, **model_kwargs)
            spy_df = self._get_spy_benchmark(start_year, end_year)
            trades_df, eq_df, metrics = Backtester().run(df, model, benchmark_df=spy_df if spy_df is not None else df)
            return {'ref_hour': ref_hour, 'ticker': ticker, 'model': model.__class__.__name__, 'metrics': metrics, 'trades_df': trades_df, 'eq_df': eq_df}
        except Exception as e:
            return {'ref_hour': ref_hour, 'error': str(e)}

    def run_swarm_scan(self, model_class, hours, tickers=['QQQ', 'SPY'], start_year=2010, end_year=2026, max_workers=8, **model_kwargs):
        tasks = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for ticker in tickers:
                for h in hours:
                    tasks.append(executor.submit(self.run_hour_worker, model_class, h, ticker, start_year, end_year, **model_kwargs))
            results = [t.result() for t in concurrent.futures.as_completed(tasks)]
        return sorted(results, key=lambda x: (x.get('ticker', ''), x.get('ref_hour', 0)))

    def run_hybrid_heatmap(self, tickers, start_year, end_year, ors=(5,15), targets=(1.5,2.0,3.0), rvols=(1.2,1.5,2.0), top_k=5):
        rows = []
        for or_m, tr, rv in itertools.product(ors, targets, rvols):
            _, _, m = self.run_hybrid_portfolio(tickers, start_year, end_year, or_m, rv, 0.6, 2.0, tr, top_k)
            rows.append({'OR': or_m, 'TargetR': tr, 'RVOL': rv, 'Trades': m.get('total_trades',0), 'Sharpe': m.get('sharpe_ratio',0), 'PF': m.get('profit_factor',0), 'Ret%': m.get('total_return_pct',0), 'DD%': m.get('max_drawdown_pct',0)})
        return pd.DataFrame(rows).sort_values('Sharpe', ascending=False)
