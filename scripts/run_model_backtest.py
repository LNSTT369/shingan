import argparse, sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from engine.data_loader import DataLoader
from engine.swarm_runner import SwarmRunner
from models.hybrid_orb import HybridORBModel

HYBRID_DEFAULT = "AAPL,ADBE,AMAT,AMD,AMGN,AMZN,ASML,AVGO,BKNG,CAT,CDNS,COIN,COST,FTNT,GE,GILD,GLD,GOOGL,GS,IWM,KLAC,LLY,LMT,LRCX,MA,MELI,META,MSFT,MU,NFLX,NVDA,PANW,PLTR,PYPL,QQQ,REGN,SNPS,SPY,SQQQ,TQQQ,TSLA,V,VOO,VRTX"

def main():
    p = argparse.ArgumentParser(description='Shingan Hybrid ORB — ponytail ultra: one CLI, Top-K portfolio')
    p.add_argument('--or-minutes', type=int, default=5, help='5 Zarattini or 15 Valkyrie')
    p.add_argument('--target-r', type=float, default=2.0)
    p.add_argument('--min-rvol', type=float, default=1.5)
    p.add_argument('--phi-min', type=float, default=0.6)
    p.add_argument('--phi-max', type=float, default=2.0)
    p.add_argument('--top-k', type=int, default=5)
    p.add_argument('--tickers', type=str, default=HYBRID_DEFAULT)
    p.add_argument('--capital', type=float, default=50000.0)
    p.add_argument('--risk', type=float, default=0.01)
    p.add_argument('--start_year', type=int, default=2021)
    p.add_argument('--end_year', type=int, default=2026)
    p.add_argument('--heatmap', action='store_true', help='OR(5,15) x R(1.5,2,3) x RVOL(1.2,1.5,2) sweep')
    args = p.parse_args()
    runner = SwarmRunner()
    tickers = [t.strip() for t in args.tickers.split(',')]
    if args.heatmap:
        df = runner.run_hybrid_heatmap(tickers, args.start_year, args.end_year, top_k=args.top_k)
        print(df.to_string(index=False))
        return
    print(f"Hybrid {args.or_minutes}m | {args.target_r}R | RVOL>={args.min_rvol} phi[{args.phi_min},{args.phi_max}] Top{args.top_k} | {len(tickers)} tickers {args.start_year}-{args.end_year}")
    trades, eq, m = runner.run_hybrid_portfolio(tickers, args.start_year, args.end_year, args.or_minutes, args.min_rvol, args.phi_min, args.phi_max, args.target_r, args.top_k, args.capital, args.risk)
    print('='*65)
    print(f"  SHINGAN HYBRID: OR {args.or_minutes}m {args.target_r}R RVOL>={args.min_rvol} Top{args.top_k} | {eq['date'].min()} to {eq['date'].max()} | {len(tickers)} tickers")
    print('='*65)
    for k, v in m.items():
        print(f"  {k:<28}: {v:>12.2f}" if isinstance(v, float) else f"  {k:<28}: {v:>12}")
    print('='*65)

if __name__ == '__main__':
    main()
