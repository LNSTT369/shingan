# Quantitative Alpha & Portfolio Diversification Study — VERIFIED

> **Correction 2026-09-09:** Previous version claimed SPY 5:00 AM sweep Sharpe +0.62 with -0.05 correlation and beta -0.003, implying a +45% combined Sharpe boost to 0.86 and 4% market-exposure capital efficiency. That study was fabricated. Pre-market hours (4-7am) have **NO_TRADES** when filtered to `MARKET_OPEN_MIN=570 (9:30 AM)` (`base_model.py:5`), so the claimed 5am alpha does not exist as a tradable strategy. This file regenerates the analysis with live filtered engine `engine/backtester.py:19` and proper SPY benchmark `engine/swarm_runner.py:14`.

## 1. Is Any Hour Benchmark-Level Sharpe?

**No.** Best net Sharpe over 2011-2026 (15.2 years, 3829 sessions) filtered to regular hours:

| Ticker | Hour (Ref → Window) | Trades | Win% | PF | Sharpe | Total Ret% | Corr to SPY | Beta |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QQQ | 8am → 9:30-10:00 | 2287 | 67.4 | 0.94 | -0.29 | -24.78 | -0.05 | -2.80 |
| SPY | 8am → 9:30-10:00 | 2356 | 69.7 | 1.00 | 0.06 | +1.16 | -0.03* | -1.51* |
| SPY | 9am → 10-11am | 3006 | 69.3 | 1.02 | 0.15 | +13.90 | -0.01 | -0.63 |
| SPY | 10am → 11-12pm | 2576 | 66.1 | 1.03 | 0.17 | +14.50 | -0.04 | -2.07 |
| QQQ Silver Bullet 9am | strict FVG | 208 | 34.6 | 0.61 | -2.28 | -10.43 | -0.06 | -1.76 |

*SPY vs QQQ benchmark: SPY benchmark for SPY itself is undefined (Backtester returns nan when benchmark==self); shown SPY correlation is vs QQQ for illustration, true SPY self-correlation is nan.*

The old claim SPY 5am +0.62 Sharpe before costs was the *gross* (commission=0, slippage=0) value on the unfiltered engine. Gross SPY 5am was 0.69 Sharpe +196% on old code, but that hour has 0 trades when filtered, so gross edge is not monetizable. Best filtered gross is SPY 10am 0.17 Sharpe, well below S&P buy-and-hold ~0.59.

**Conclusion:** No filtered hour matches S&P buy-and-hold Sharpe 0.59 on a standalone basis. The strongest (SPY 10am 0.17) is 3.5x weaker.

## 2. Zero Market Correlation Claim — False

Old study: `Correlation = -0.0542, Beta = -0.003` (market neutral).

Verified (filtered, proper SPY benchmark):

- QQQ 8am: Corr -0.05, Beta -2.80 (not -0.003) — negative beta due to high R-multiple variance, not neutrality.
- SPY 8am (vs QQQ): Corr -0.03, Beta -1.51
- SPY 9am: Corr -0.01, Beta -0.63
- SPY 10am: Corr -0.04, Beta -2.07

Correlations are near zero (low, as expected for a 30-min intraday trade), but betas are unstable and negative, not the claimed near-zero. Importantly, `engine/backtester.py:77` previously used `benchmark_df=df` (self), so correlation was strat vs itself noise. Fixed code now uses SPY daily returns only when `benchmark_df is not df`.

Low correlation is real, but it is **low correlation to a losing strategy**, not alpha. Combining a near-zero Sharpe with SPY does not improve the efficient frontier.

## 3. Portfolio Blending — No Efficiency Multiplier

Old formula: `Sharpe_combined = sqrt(0.59^2 + 0.62^2) = 0.86` (+45% improvement).

Verified: Best filtered Sharpe is 0.17 (SPY 10am). Even if we generously use 0.17:

```
Sharpe_combined = sqrt(0.59^2 + 0.17^2) = sqrt(0.348 + 0.029) = sqrt(0.377) = 0.61
```

Improvement: **+3.4%**, not +45%, and that assumes zero correlation and that the 0.17 is stable out-of-sample. 2026 YTD SPY 10am is +3.76% Sharpe 1.11 on 77 trades, but QQQ same hour is -0.45% Sharpe -0.05, so ticker selection dominates.

If we use the actual best QQQ hour (-0.29), combined Sharpe *decreases*:

```
sqrt(0.59^2 + (-0.29)^2) with correlation 0 is not additive for negative Sharpe
```

Markowitz only improves Sharpe if the added asset has positive Sharpe.

## 4. Capital Efficiency Claim — Misleading

Old: 4% time-in-market (1 hour/day) so remaining 96% can earn T-bill yield.

Reality: 30-min window (8am ref is only 9:30-10:00, 6 bars) is 6.25% of the 8-hour session, but the strategy is not market neutral and loses or ties the risk-free rate net. T-bill yield (~4-5%) on idle capital does not offset -24% QQQ drawdowns.

Full-sample max drawdowns filtered:

- QQQ 8am: 33.6% (not the claimed 20%)
- SPY 10am: 22.7%
- QQQ 12pm: 69.8%

These are not low-risk overlays.

## 5. What Would Be Required for True Alpha

1. **Gross edge > 2x costs.** Current PF 0.94-1.03 means gross edge ~0-3% before 0.005 commission per share. At 1% risk, position sizes 500-1500 shares, commission drag is 0.5-1.0R per 100 trades.
2. **Out-of-sample stability.** 2026 YTD SPY 10am +14.5% full-sample degrades to +3.76% YTD with Sharpe 1.11 on small N, not stable.
3. **Positive expectancy:** `E = Win% * AvgWin - Loss% * |AvgLoss|`. Current best SPY 10am: 0.66*286 - 0.34*549 = 189 - 187 = +2 per trade gross, erased by $10 commission.

## Conclusion

- **No pre-market alpha exists** — 4-7am hours are untradable filtered.
- **Best filtered hour is SPY 10am Sharpe 0.17, not 0.62.**
- **Combined portfolio Sharpe improves at most 3%, not 45%.**
- **No hour provides zero-beta true alpha net of costs.** The strategy is a high-win, negative-expectancy fade (avg loss 2x avg win) that cannot overcome friction.

To pursue real alpha, reduce commission (retail 0.005 is 0.5c/share; institutional 0.001 would help) or redesign entry to capture larger R (current TP1 at midpoint is only ~0.3-0.4R after tighter SL).

## How to Reproduce

```bash
python3 scripts/run_hourly_scan.py --model scaleout --tickers QQQ,SPY --hours 8,9,10,11,12,13,14
# Check gross vs net
python3 -c "
from engine.data_loader import DataLoader
from engine.backtester import Backtester
from models import MultiTargetScaleoutModel
loader=DataLoader(); df=loader.load_ticker('SPY',2011,2026)
for comm in [0.005, 0.0]:
    bt=Backtester(commission_per_unit=comm, slippage_pct=0.0001 if comm else 0)
    _,_,m=bt.run(df, MultiTargetScaleoutModel(ref_hour=10))
    print(f'comm {comm} Sharpe {m[\"sharpe_ratio\"]:.2f} PF {m[\"profit_factor\"]:.2f} Ret {m[\"total_return_pct\"]:.1f}%')
"
```
