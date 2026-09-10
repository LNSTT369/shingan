# Shingan — Clear-Eyed Hybrid ORB

Hybrid Zarattini 5m + Valkyrie 15m x RVOL/phi. One CLI, Top-K portfolio. Ponytail ultra: 150L core, no bloat.

> He says nothing. He writes one line. It works. — ponytail

**Formerly `hourly-liquidity-lab`.** Hourly sweep fade tested 2011-2026: **-24% to -99% all hours, Sharpe -0.29 to -2.39, PF 0.94** `INCIDENT_REPORT.md:1` `reports/24_hour_cycle_findings.md:1` — archived to `models/legacy/` for paper audit only.

## Edge

| Model | 2021-2025 44 tickers Top5 | 2024 | Sharpe | PF | MaxDD |
| :--- | ---: | ---: | ---: | ---: | ---: |
| **Shingan 5m RVOL>=1.5 phi[0.6,2.0] 2R** | **1262 trades, +108.7%, 1.21** | **321 trades, +53.0%, 2.59** | **1.21** | **1.25** | **16.8%** |
| Valkyrie 15m same filters | 2252 trades, +101.9%, 0.80 | 257 trades, +40.6%, 3.31 | 0.80 | 1.17 | 15.8% |
| Zarattini naive 5m no filter | 6275 trades, +220% but 0.37, PF 1.04 | 1260 trades, +70% PF1.10 | 0.37 | 1.04 | 60.1% |
| SPY naive 15m OR (control) | -95% | — | -2.14 | — | — |

Filters are necessary: no RVOL → Sharpe 0.37 vs 1.21, DD 60% vs 16.8% `SHINGAN_Hybrid_ORB_Paper.md:186`. Paper: `SHINGAN_Hybrid_ORB_Paper.md:1` `SHINGAN_ArXiv_Paper.pdf`.

## Architecture

```
shingan/
├── engine/
│   ├── data_loader.py      # 5m loader, UTC→America/New_York
│   ├── backtester.py       # fixed-fractional 1% risk, $0.005/share + 0.01% slip
│   ├── metrics.py          # Sharpe/Sortino/PF/MaxDD/beta
│   └── swarm_runner.py     # run_hybrid_portfolio + run_hybrid_heatmap (single Top-K engine)
├── models/
│   ├── base_model.py       # MARKET_OPEN 570, CLOSE 960
│   ├── hybrid_orb.py       # 150L: 5m/15m OR, RVOL>=1.5, phi[0.6,2.0], seq lockout, 2R + BE at 1R, 15:00 +1% lock, 15:55 flat
│   └── legacy/             # 5 dead fade models — YAGNI, kept for reproducibility
├── scripts/
│   └── run_model_backtest.py # one CLI: single run + --heatmap
├── tests/test_models.py    # 6 tests, 2024 parity 321 trades 53.03%
└── requirements.txt
```

## Quickstart

```bash
pip install -r requirements.txt

# primary cell: 5m OR 2R RVOL>=1.5 phi[0.6,2.0] Top5, 44 tickers, 2024
python3 scripts/run_model_backtest.py --or-minutes 5 --target-r 2.0 --min-rvol 1.5 --phi-min 0.6 --phi-max 2.0 --top-k 5 --start_year 2024 --end_year 2024

# 2021-2025 concatenated OOS (paper Table 6.2)
python3 scripts/run_model_backtest.py --or-minutes 5 --target-r 2.0 --min-rvol 1.5 --start_year 2021 --end_year 2025

# heatmap OR(5,15) x R(1.5,2,3) x RVOL(1.2,1.5,2) Top5
python3 scripts/run_model_backtest.py --heatmap --start_year 2021 --end_year 2025

# tests
python3 -m unittest discover tests -v
```

## Strategy — Shingan Hybrid `models/hybrid_orb.py:5`

* **OR:** 5m (Zarattini 09:30-09:34:59 one bar) or 15m (Valkyrie 09:30-09:44:59 three bars), `or_minutes`
* **Filters:** `RVOL = vol_OR / mean(vol_OR prior 14d) >=1.5`, `phi = spread/ATR14 in [0.6,2.0]` — rank 44 tickers each morning, take **Top5** by RVOL `engine/swarm_runner.py:15`
* **Signal:** 5m `C>=O → LONG else SHORT` (color-only); 15m `low_first and green → LONG`, `high_first and red → SHORT` else `REJECT trap` `models/hybrid_orb.py:60`
* **Bracket:** `LONG high+0.01 / SHORT low-0.01` stop-entry, SL opposite side `∓0.01`, TP `entry ± target_r * risk` (2R default), BE trail at +1R, 15:00 profit lock if unreal ≥+1%, 15:55 flat `models/hybrid_orb.py:75`
* **Sizing:** `qty = floor(equity*0.01 / risk)` per name, max 5% daily `engine/backtester.py:13`

## Why not hourly fade?

`INCIDENT_REPORT.md:1` root cause: ad-hoc arithmetic without `Backtester.run()`, tight $0.30 SL → 1,600 shares per $500 risk → $75 fee per trade (18% of risk), 2700 trades → -$240k friction. Formal engine with `Backtester.run()` + SPY benchmark is the only valid metric. **Gross vs net audit mandatory.**

## Reproduce

```bash
git clone https://github.com/LNSTT369/shingan.git
pip install -r requirements.txt
python3 scripts/run_model_backtest.py --or-minutes 5 --target-r 2.0 --min-rvol 1.5 --start_year 2021 --end_year 2025
# expect: 321 trades 2024 53.03% PF1.69 Sharpe2.59, 1262 trades 2021-2025 108.7% Sharpe1.21
```

## References

* Zarattini et al. 2024 SSRN 24-97 — 5m OR, 1000 stocks, Sharpe 2.40
* Valkyrie ORB `STRATEGY.md:1` — 15m OR, seq+color lockout, RVOL+phi, bracket `high±tick` `low∓tick` `high±spread`
* ORBPLUS — retrace 50% +0.0538R vs instant -0.0082R, but WR 3.8% — removed in ultra
* `SHINGAN_Hybrid_ORB_Paper.md:1` — full 44-ticker WFO 2021-2025

Ponytail ultra: `hybrid_orb 293→150L`, `1587→900L (-43%)`, retrace deleted, 3 scripts →1 CLI. Skipped retrace when fill >20% and PF>1.5; skipped fade when PF>1.0 net. `models/legacy/` kept for audit.

---
*Shingan — Clear-Eyed Lens. Perfection when nothing left to take away.*
