<div align="center">
  <h1>Shingan</h1>
  <p><em>Clear-Eyed Hybrid ORB — Zarattini 5m × Valkyrie φ · 150 lines, no bloat.</em></p>
</div>

<p align="center">
  <a href="https://github.com/LNSTT369/shingan/stargazers"><img src="https://img.shields.io/github/stars/LNSTT369/shingan?style=flat-square" alt="Stars" /></a>
  <a href="https://github.com/LNSTT369/shingan"><img src="https://img.shields.io/badge/python-3.12-3776AB?style=flat-square" alt="Python" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-black?style=flat-square" alt="License" /></a>
  <a href="SHINGAN_Hybrid_ORB_Paper.md"><img src="https://img.shields.io/badge/paper-arXiv_2512-black?style=flat-square" alt="Paper" /></a>
  <a href="https://github.com/DietrichGebert/ponytail"><img src="https://img.shields.io/badge/ponytail-ultra-9ED832?style=flat-square&labelColor=0A0A0B" alt="ponytail ultra" /></a>
</p>

<p align="center">
  <a href="assets/shingan_equity_curve.png"><img src="assets/shingan_equity_curve.png" alt="Figure 1 — Shingan equity curve 2021-2025, 44 tickers Top5, Sharpe 1.21" width="1000" /></a>
  <br/><sub><strong>Figure 1</strong> — Equity Curve (2021-2025, 44-ticker portfolio, Top-5 RVOL) — Shingan 5m/2R/1.5 Sharpe 1.21 · <a href="SHINGAN_Hybrid_ORB_Paper.md">Paper §6.2</a></sub>
</p>

> *Anything added dilutes everything else.* — tw93 &nbsp;&nbsp; *Perfection when nothing left to take away.* — Saint-Exupéry

Shingan is the hybrid that survives where hourly fade dies. Formerly `hourly-liquidity-lab`, the pure hourly sweep (2011-2026, 5m) loses **24% to 99% every hour, Sharpe -0.29 to -2.39, PF 0.94** — archived to [`models/legacy/`](models/legacy/) for audit only. See [`INCIDENT_REPORT.md`](INCIDENT_REPORT.md) and [`reports/24_hour_cycle_findings.md`](reports/24_hour_cycle_findings.md).

---

## Performance

| Model | 2021-2025 · 44 Top5 | 2024 | Sharpe | PF | MaxDD |
| :--- | ---: | ---: | ---: | ---: | ---: |
| **Shingan 5m · RVOL≥1.5 φ[0.6,2.0] 2R** | **1262 · +108.7%** | **321 · +53.0%** | **1.21** | **1.25** | **16.8%** |
| Valkyrie 15m same filters | 2252 · +101.9% | 257 · +40.6% | 0.80 | 1.17 | 15.8% |
| Zarattini naive 5m no filter | 6275 · +220% | 1260 · +70% | 0.37 | 1.04 | 60.1% |
| SPY naive 15m (control) | -95% | — | -2.14 | — | — |

Filters are the edge: no RVOL → Sharpe 0.37 vs 1.21, DD 60% vs 16.8% ([`SHINGAN_Hybrid_ORB_Paper.md:186`](SHINGAN_Hybrid_ORB_Paper.md#L186)). Full walk-forward in [`SHINGAN_Hybrid_ORB_Paper.md`](SHINGAN_Hybrid_ORB_Paper.md) and [`SHINGAN_ArXiv_Paper.pdf`](SHINGAN_ArXiv_Paper.pdf).

<table width="100%" cellpadding="0" cellspacing="0">
<tr>
<td width="50%" align="center" valign="top">
  <a href="assets/shingan_heatmap.png"><img src="assets/shingan_heatmap.png" alt="Figure 3 — Hybrid Parameter Heatmap: OR × TargetR × RVOL (2024, phi [0.6,2.0], Top5, 44 tickers) — 5m/2R/1.5 peak" width="100%" /></a>
  <br/><sub><strong>Figure 3</strong> — Heatmap: OR × TargetR × RVOL (2024, φ[0.6,2.0], Top5, 44 tickers) — 5m/2R/1.5 peak 2.69</sub>
</td>
<td width="50%" align="center" valign="top">
  <a href="assets/shingan_drawdown.png"><img src="assets/shingan_drawdown.png" alt="Figure 2 — Drawdown Comparison: Hybrid vs Parents (2021-2025, 44-ticker, Top-5 RVOL)" width="100%" /></a>
  <br/><sub><strong>Figure 2</strong> — Drawdown: Hybrid 16.8% vs Valkyrie 15.8% vs Naive 60.1%</sub>
</td>
</tr>
</table>

---

## Features

- **One core, one CLI**: `hybrid_orb.py` 150L + `swarm_runner.run_hybrid_portfolio` — 1587L → 900L (-43%), ponytail ultra, no `use_retrace` branch (WR 3.8% never fills)
- **Volatility-normalized selection**: `RVOL ≥ 1.5` and `φ = spread/ATR14 ∈ [0.6, 2.0]` — rank 44 liquid names each open, take Top5
- **Trap-aware signal**: 5m color-only (`C≥O → LONG`), 15m `low_first+green → LONG` else `REJECT` — Valkyrie sequence lockout cuts 34% false breakouts
- **Brackets that ship**: `high+0.01 / low-0.01` stop, SL opposite side, TP `entry ± 2R`, BE at +1R, 15:00 +1% lock, 15:55 flat — 100% cash by close
- **Fixed-fractional**: `qty = floor(equity·0.01 / risk)` per name, max 5% daily heat

## Quick Start

Requires `pandas`, `numpy`. Data: `data/intraday_5m/{year}/{ticker}.csv` or `ict mechanical/data/intraday_5m`.

```bash
pip install -r requirements.txt

# primary cell — 2024, 44 Top5, 5m 2R
python3 scripts/run_model_backtest.py --or-minutes 5 --target-r 2.0 --min-rvol 1.5 --top-k 5 --start_year 2024 --end_year 2024
# 321 trades · 53.03% · PF 1.69 · Sharpe 2.59 · DD 9.87%

# concatenated OOS 2021-2025 — paper Table 6.2
python3 scripts/run_model_backtest.py --or-minutes 5 --target-r 2.0 --min-rvol 1.5 --start_year 2021 --end_year 2025
# 1262 trades · +108.7% · Sharpe 1.21 · PF 1.25

# full sweep OR(5,15) × R(1.5,2,3) × RVOL(1.2,1.5,2)
python3 scripts/run_model_backtest.py --heatmap --start_year 2021 --end_year 2025

# tests — 6 tests, parity locked
python3 -m unittest discover tests -v
```

<p align="center">
  <a href="assets/shingan_monthly.png"><img src="assets/shingan_monthly.png" alt="Figure 4 — Monthly returns, 1 trade/day across 44 names, β 0.05 to SPY" width="1000" /></a>
  <br/><sub><strong>Figure 4</strong> — Monthly Returns — 1 trade/day across 44 names, β 0.05 to SPY, true intraday alpha</sub>
</p>

## Architecture

```text
shingan/
├── engine/
│   ├── data_loader.py      # 5m loader, UTC → America/New_York
│   ├── backtester.py       # 1% risk, $0.005/share + 0.01% slip
│   ├── metrics.py          # Sharpe / Sortino / PF / MaxDD / Beta
│   └── swarm_runner.py     # run_hybrid_portfolio + run_hybrid_heatmap
├── models/
│   ├── base_model.py       # MARKET_OPEN 570 · CLOSE 960
│   ├── hybrid_orb.py       # 150L — the only model that ships
│   └── legacy/             # 5 fade models — YAGNI, kept for reproducibility
├── scripts/run_model_backtest.py  # one CLI
└── tests/test_models.py    # 6 tests
```

## Strategy

`models/hybrid_orb.py:5` — `HybridORBModel(or_minutes=5, min_rvol=1.5, phi_min=0.6, phi_max=2.0, target_r=2.0)`

- **OR** `09:30-09:34:59` (5m) or `09:30-09:44:59` (15m)
- **Filters** `rvol` and `phi` gate every ticker; Top5 by `rvol` only trade
- **Signal** color + first-touch `h_time`/`l_time` — `trap lockout` when sequence and color disagree
- **Bracket** entry stop `high+tick` / `low-tick` — one `tick = 0.01`
- **Exits** `tp = entry ± target_r·risk` (2R), BE when `high ≥ entry+risk` or `low ≤ entry-risk`, profit lock at 900 min if unreal ≥1%

Why not hourly fade: tight $0.30 SL → 1,600 shares on $500 risk → $75 fee (18% of risk) → 2,700 trades → -$240k. Only the formal `Backtester.run()` with SPY benchmark counts. See [`INCIDENT_REPORT.md`](INCIDENT_REPORT.md).

## Reproduce

```bash
git clone https://github.com/LNSTT369/shingan.git
cd shingan
pip install -r requirements.txt
python3 scripts/run_model_backtest.py --or-minutes 5 --target-r 2.0 --min-rvol 1.5 --start_year 2021 --end_year 2025
```

## References

- Zarattini, C., Aziz, A., Barbon, A. 2024 — *Can Day Trading Really Be Profitable?* and *Beat the Market: An Effective Intraday Momentum Strategy for SPY.* Swiss Finance Institute Research Paper No. 24-97. SSRN [4824172](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4824172) and [4416622](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4416622) — 5m OR, 1,000 stocks, Sharpe 2.40
- Valkyrie ORB 2026 — [Strategy Specification](https://github.com/LNSTT369/valkyrie_orb/blob/main/STRATEGY.md) · [Live Executor](https://github.com/LNSTT369/valkyrie_orb/blob/main/strategies/live_orb_executor.py) · [Quant Audit](https://github.com/LNSTT369/valkyrie_orb/blob/main/QUANT_AUDIT_REPORT.md) — 15m OR, seq+color lockout, RVOL+phi
- ORBPLUS 2026 — [`ORBPLUS_BACKTEST_RESULTS.md`](https://github.com/LNSTT369/valkyrie_orb/blob/main/ORBPLUS_BACKTEST_RESULTS.md) — retrace 50% mean +0.0538R vs instant -0.0082R (WR 3.8% → removed in ultra `models/hybrid_orb.py:5`)
- Shingan 2026 — [`SHINGAN_Hybrid_ORB_Paper.md`](SHINGAN_Hybrid_ORB_Paper.md) · [`SHINGAN_Hybrid_ORB_Paper.pdf`](SHINGAN_Hybrid_ORB_Paper.pdf) · [`SHINGAN_ArXiv_Paper.pdf`](SHINGAN_ArXiv_Paper.pdf) — full 44-ticker WFO 2021-2025
- [`INCIDENT_REPORT.md`](INCIDENT_REPORT.md) · [`reports/24_hour_cycle_findings.md`](reports/24_hour_cycle_findings.md) · [`reports/alpha_portfolio_study.md`](reports/alpha_portfolio_study.md) — hourly fade audit, zero-beta portfolio

---

<div align="center">

*Shingan — Clear-Eyed Lens.*

[Valkyrie](https://github.com/LNSTT369/valkyrie_orb) · [NightWatcher](https://github.com/LNSTT369/NightWatcher) · [Portfolio](https://chiranjeevportfolio.vercel.app) · [LinkedIn](https://linkedin.com/in/chiranjeevshah) · [Topmate](https://www.topmate.io/showtime/)

</div>
