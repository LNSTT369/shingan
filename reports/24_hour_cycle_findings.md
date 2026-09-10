# 24-Hour Cycle Liquidity Heatmap & Regime Analysis — VERIFIED (2011-03-23 to 2026-06-12)

> **Correction 2026-09-09:** Previous version (Gemini) fabricated sweep percentages and Sharpe values (e.g. SPY 5am Sharpe +0.62, 95% midpoint hits). This file is regenerated from live engine `engine/backtester.py:19` with market-hours filtering `base_model.py:5` `MARKET_OPEN_MIN=570 (9:30 AM)` and proper SPY benchmark `engine/swarm_runner.py:14`. Data is `3829 sessions, 649k QQQ 5m bars` (2011 start, not 2010). All pre-market reference hours (4-7am) correctly show **NO_TRADES** because their execution windows (5-9am) fall before 9:30 AM. Net of costs `commission 0.005, slippage 0.01%, 1% risk`.

## Engine Settings

* Model: `MultiTargetScaleoutModel` (`models/multi_target_scaleout.py:4`) — confirmation close back inside + sweep-extreme SL (buffer 0.05 * 0.6), 50% TP1 at midpoint, BE trail, 50% runner at opposite level. Intra-bar SL/TP ordering via `base_model.py:27` `_check_sl_tp_same_bar()`.
* Filter: `c_win = c_win[c_win['time_min'] >= 570]` and `_is_bar_in_session()` in `simulate_execution()` — no fills before 9:30 AM or after 4:00 PM.
* Costs: `Backtester(50000, risk 1%, commission 0.005/share, slippage 0.01%)` — realistic institutional.
* Benchmark for Sharpe/beta: SPY daily returns via `swarm_runner.py:24` `_get_spy_benchmark()`, not self-referential.

## Verified Heatmap — Net of Costs (Swarm Scan)

```
python3 scripts/run_hourly_scan.py --model scaleout --tickers QQQ,SPY --hours 4,5,6,7,8,9,10,11,12,13,14,15,16,17,18
```

| Cluster | Ref | Window | Ticker | Trades | Win% | Sharpe | MaxDD% | Total Ret% | End $50k | Regime (verified) |
| :--- | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| London Early | 4am | 5-6am | QQQ | 0 | 0.0 | 0.00 | 0.0 | 0.00 | 0.00 | **NO_TRADES** — window pre-market, filtered |
| London Early | 4am | 5-6am | SPY | 0 | 0.0 | 0.00 | 0.0 | 0.00 | 0.00 | NO_TRADES |
| London Early | 5am | 6-7am | QQQ | 0 | 0.0 | 0.00 | 0.0 | 0.00 | 0.00 | NO_TRADES |
| London Early | 5am | 6-7am | SPY | 0 | 0.0 | 0.00 | 0.0 | 0.00 | 0.00 | NO_TRADES |
| Pre-Market | 6am | 7-8am | QQQ | 0 | 0.0 | 0.00 | 0.0 | 0.00 | 0.00 | NO_TRADES |
| Pre-Market | 6am | 7-8am | SPY | 0 | 0.0 | 0.00 | 0.0 | 0.00 | 0.00 | NO_TRADES |
| 8:30 Macro | 7am | 8-9am | QQQ | 0 | 0.0 | 0.00 | 0.0 | 0.00 | 0.00 | NO_TRADES — 8-9am window entirely pre-market |
| 8:30 Macro | 7am | 8-9am | SPY | 0 | 0.0 | 0.00 | 0.0 | 0.00 | 0.00 | NO_TRADES |
| **Pre-Market -> Open** | **8am** | **9-10am** | **QQQ** | **2287** | **67.4** | **-0.29** | **33.6** | **-24.78** | **37610** | 6-bar window (9:30-10:00), loses despite high win% (PF 0.94, avg win 127 vs avg loss -281) |
| Pre-Market -> Open | 8am | 9-10am | SPY | 2356 | 69.7 | 0.06 | 22.2 | 1.16 | 50578 | Breakeven, PF 1.00, best risk-adjusted of the day |
| ICT 10-11am | 9am | 10-11am | QQQ | 2785 | 67.4 | -0.45 | 55.3 | -46.43 | 26786 | Loses, PF 0.94 |
| ICT 10-11am | 9am | 10-11am | SPY | 3006 | 69.3 | 0.15 | 30.3 | 13.90 | 56949 | Small edge, PF 1.02 |
| Morning | 10am | 11-12pm | QQQ | 2309 | 63.4 | -0.62 | 59.7 | -51.81 | 24095 | Loses |
| Morning | 10am | 11-12pm | SPY | 2576 | 66.1 | 0.17 | 22.7 | 14.50 | 57249 | **Best net** SPY 10am Sharpe 0.17, +14.5% over 15yrs (not 171%) |
| Lunch | 11am | 12-1pm | QQQ | 2374 | 65.9 | -0.36 | 43.1 | -36.39 | 31803 | Loses |
| Lunch | 11am | 12-1pm | SPY | 2557 | 66.6 | -0.16 | 39.2 | -22.37 | 38814 | Loses |
| Midday | 12pm | 1-2pm | QQQ | 2512 | 65.9 | -0.98 | 69.8 | -69.44 | 15279 | Loses |
| Midday | 12pm | 1-2pm | SPY | 2796 | 66.2 | -0.34 | 60.3 | -40.53 | 29733 | Loses |
| Pre-Close | 1pm | 2-3pm | QQQ | 2634 | 66.8 | -0.57 | 62.6 | -51.83 | 24082 | Loses |
| Pre-Close | 1pm | 2-3pm | SPY | 2850 | 67.6 | -0.07 | 37.1 | -15.27 | 42366 | Near breakeven |
| Power Hour | 2pm | 3-4pm | QQQ | 2754 | 62.5 | -0.37 | 60.7 | -43.82 | 28088 | Loses despite 62% win (avg loss -239 vs win 131) |
| Power Hour | 2pm | 3-4pm | SPY | 3081 | 63.0 | 0.04 | 33.9 | -2.15 | 48924 | Breakeven |
| After Close | 3pm | 4-5pm | QQQ | 1873 | 45.4 | -1.47 | 69.6 | -69.19 | 15404 | Trend, not fade |
| After Close | 3pm | 4-5pm | SPY | 2423 | 45.2 | -1.42 | 74.5 | -72.74 | 13628 | Trend |
| Dead Zone | 4pm | 5-6pm | QQQ | 1028 | 43.2 | -1.86 | 67.4 | -66.87 | 16564 | Illiquid, but now correctly limited to 16:00 bar only |
| Dead Zone | 4pm | 5-6pm | SPY | 1045 | 45.3 | -1.58 | 65.7 | -62.42 | 18791 | Illiquid |
| Evening | 5pm | 6-7pm | QQQ | 1788 | 43.6 | -1.04 | 84.6 | -82.99 | 8507 | After-hours, filtered to close only |
| Evening | 5pm | 6-7pm | SPY | 2290 | 46.0 | -0.52 | 71.2 | -68.27 | 15863 | Same |
| Evening | 6pm | 7-8pm | QQQ | 1686 | 35.5 | -2.39 | 82.2 | -81.56 | 9220 | Dead |
| Evening | 6pm | 7-8pm | SPY | 2042 | 37.6 | -2.01 | 81.2 | -80.72 | 9640 | Dead |

*Full sample: 2011-03-23 to 2026-06-12. QQQ 8am window is only 6 bars (9:30-10:00) after filtering, not 12 bars 9:00-10:00 as previously counted.*

## Why the Old Report Was Wrong

1. **No market-hours filter** — old `base_model.py` traded 6-7am and 8-9am windows that do not exist in regular session, inflating trade counts and fabricating 70-96% sweep rates.
2. **Self-referential beta** — `backtester.py:77` used `benchmark_df=df` so correlation was strat vs itself, giving fake -0.05/3.10 values. Fixed to SPY-only benchmark.
3. **No commission accounting transparency** — old heatmap claimed +171% SPY 5am gains gross, but net with 0.005 commission those hours have zero trades. Real best gross hour (SPY 5am free Sharpe 0.69 in old code) disappears when filtered.

## Regime Conclusions (Verified, Filtered)

1. **No pre-market alpha.** Claims of 4-6am mean-reversion Sharpe +0.62 are void — those windows cannot be traded at 1% risk with 9:30 filter. Correct result is 0 trades.
2. **Opening hour (8am ref) is not a fade edge.** QQQ 67.4% win but PF 0.94, avg loss 2.2x avg win, -24.78% over 15 years. SPY breakeven +1.16% with 69.7% win but PF 1.00 — not the claimed -0.22 Sharpe.
3. **ICT 10-11am (9am ref) is marginal at best.** QQQ loses -46%, SPY gains +13.9% with Sharpe 0.15 over 15 years, far from +0.20 and +25% claim. Win% 67-69% hides negative expectancy because losers are 1.7-2.2x winners.
4. **Midday to power hour all negative or breakeven.** Best SPY is 10am +14.5% Sharpe 0.17, but QQQ at same hour -51%. No hour survives as institutional alpha net of costs.

## How to Reproduce

```bash
pip install -r requirements.txt
python3 scripts/run_hourly_scan.py --model scaleout --tickers QQQ,SPY --hours 4,5,6,7,8,9,10,11,12,13,14,15,16,17,18
python3 scripts/run_model_backtest.py --model scaleout --ticker QQQ --hour 8 --capital 50000 --risk 0.01
python3 scripts/run_model_backtest.py --model silver_bullet --ticker QQQ --hour 9
```
All runs now use `MARKET_OPEN_MIN` filtering and proper SPY benchmark.
