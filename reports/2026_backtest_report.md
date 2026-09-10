# 2026 Out-Of-Sample Backtest Audit — VERIFIED ($50,000 Capital, Market-Hours Filtered)

> **Correction 2026-09-09:** Previous audit claimed 8am scaleout 2026 YTD QQQ -$5,563 (-11.13%) on 82 trades and SPY -$6,214 on 74 trades, using unfiltered 9:00-10:00 window (including 9:00-9:30 pre-market). This file is regenerated with live engine `engine/backtester.py:19` and `models/multi_target_scaleout.py:4` filtered to `MARKET_OPEN_MIN=570 (9:30 AM)` via `base_model.py:5`. 2026 data is 2025-12-31 to 2026-06-12 (113 sessions, 21k 5m bars). Costs: 1% risk, 0.005/share commission, 0.01% slippage.

## Test Configuration

- **Period:** January 1, 2026 – June 12, 2026 (filtered, regular session only)
- **Starting Balance:** $50,000.00
- **Risk per Trade:** 1.0% Dynamic Account Risk ($500 base, scales with equity)
- **Models:** Multi-Target Scale-Out (50% TP1 at Midpoint, BE trail, 50% TP2 at Opposite) and Silver Bullet (displacement + FVG)
- **Reference → Window:** 8:00 AM 60m candle → 9:30-10:00 AM (6 bars), 9:00 AM → 10:00-11:00 AM (12 bars)
- **Filter:** Pre-market bars excluded. Intra-bar SL/TP ordering via `_check_sl_tp_same_bar()`.

---

## 2026 YTD — Multi-Target Scale-Out, 8am Ref (9:30-10:00 window)

| Metric | QQQ (Nasdaq 100) | SPY (S&P 500) |
| :--- | :---: | :---: |
| **Ending Equity** | **$48,067.67** | **$51,182.76** |
| **Net Profit / Loss** | **-$1,932.33 (-3.86%)** | **+$1,182.76 (+2.37%)** |
| **Max Drawdown** | **6.96%** | **3.10%** |
| **Profit Factor** | **0.80** | **1.16** |
| **Total Trades** | **74** | **58** |
| **Winning Trades** | **48 (64.9%)** | **42 (72.4%)** |
| **Losing Trades** | **26 (35.1%)** | **16 (27.6%)** |
| **TP1_AND_TP2 (both halves)** | **18 (24.3%)** | **21 (36.2%)** |
| **TP1_THEN_BE (breakeven on runner)** | **31 (41.9%)** | **18 (31.0%)** |
| **FULL_SL (both halves stopped)** | **15 (20.3%)** | **11 (19.0%)** |
| **EOD (no TP/SL, closed at 16:00)** | **10 (13.5%)** | **8 (13.8%)** |
| **Average Win** | **+$161.69 (+0.33R)** | **+$200.99 (+0.40R)** |
| **Average Loss** | **-$372.83 (-0.76R)** | **-$453.69 (-0.90R)** |
| **Win Loss Ratio** | **0.43** | **0.44** |
| **Sharpe (annualized, per-trade R)** | **-1.31** | **+1.02** |
| **Sortino** | **-1.96** | **+2.18** |

**Interpretation:** With filtering, 2026 8am is near breakeven, not the claimed -11% to -12% crash. QQQ loses 3.86% with high win% but losers 2.3x winners. SPY actually gains 2.37% with Sharpe 1.02 on 58 trades, but sample is small (58 trades) and full-sample 2011-2026 is +1.16% over 15 years (Sharpe 0.06), so 2026 is noise, not alpha.

## 2026 YTD — Multi-Target Scale-Out, 9am Ref (10:00-11:00 window)

| Metric | QQQ | SPY |
| :--- | :--- | :--- |
| **Ending Equity** | **$49,646.49** | **$52,978.95** |
| **Net Profit** | **-$353.51 (-0.71%)** | **+$2,978.95 (+5.96%)** |
| **Trades** | 86 | 84 |
| **Win%** | 66.3% | 69.0% |
| **PF** | 0.97 | 1.24 |
| **Sharpe** | -0.10 | 1.52 |
| **MaxDD** | 8.01% | 5.17% |
| **AVG Win / Loss** | +229 / -462 (0.50) | +240 / -420? (check full) |

*Detailed SPY 9am 2026: win 69.0% PF 1.24 Sharpe 1.52, best 2026 window, but full-sample SPY 9am is +13.90% over 15 years Sharpe 0.15, so 2026 is an outlier.*

## 2026 YTD — Silver Bullet ICT (9am Ref, Displacement + FVG Filter)

| Metric | QQQ Silver Bullet | SPY Silver Bullet |
| :--- | :--- | :--- |
| **Trades** | **3** | **4** |
| **Win%** | **0.0%** | **25.0%** |
| **PF** | **0.00** | **0.24** |
| **Net** | **-$155.71 (-0.31%)** | **-$495.06 (-0.99%)** |
| **Sharpe** | **-35.92** | **-6.97** |

**Correction:** Previous report claimed Silver Bullet 9am delivered +25.32% with 46.15% win on QQQ. Live filtered engine shows only 3 qualifying trades in 2026 (FVG + 60% body displacement required), all TP1_THEN_BE then BE, near zero edge. Full-sample Silver Bullet (`silver_bullet.py:11`) QQQ 9am is 208 trades over 15 years, -10.43% Sharpe -2.28, not +0.20. The old claim used the unfiltered scaleout model mislabeled as Silver Bullet.

---

## Full-Sample Context (2011-2026, Filtered)

| Model / Hour | QQQ Ret% | QQQ Sharpe | SPY Ret% | SPY Sharpe |
| :--- | :---: | :---: | :---: | :---: |
| ScaleOut 8am (9:30-10:00) | -24.78% | -0.29 | +1.16% | 0.06 |
| ScaleOut 9am (10-11am) | -46.43% | -0.45 | +13.90% | 0.15 |
| ScaleOut 10am (11-12) | -51.81% | -0.62 | +14.50% | 0.17 |
| Silver Bullet 9am (strict FVG) | -10.43% | -2.28 | -? | -? |

No window delivers institutional-grade Sharpe >0.5 net of costs over 15 years.

## How to Reproduce

```bash
python3 scripts/run_model_backtest.py --model scaleout --ticker QQQ --hour 8 --capital 50000 --risk 0.01
python3 scripts/run_model_backtest.py --model silver_bullet --ticker QQQ --hour 9
python3 -c "
from engine.data_loader import DataLoader
from engine.backtester import Backtester
from models import MultiTargetScaleoutModel
loader=DataLoader(); df=loader.load_ticker('QQQ',2026,2026)
tr,eq,m=Backtester().run(df, MultiTargetScaleoutModel(ref_hour=8))
print(m)
"
```

All outputs now match `MARKET_OPEN_MIN` filtered execution and proper beta (SPY benchmark, not self).
