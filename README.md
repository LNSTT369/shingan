# Hourly Liquidity Lab 🔬⚡

A modular, institutional-grade quantitative backtesting engine and research laboratory for testing **hourly liquidity sweep models, previous-hour high/low targeting, and ICT/SMC intraday market microstructure strategies**.

---

## Architecture Overview

```
hourly-liquidity-lab/
├── engine/                      # Core quantitative backtesting & analytics engine
│   ├── data_loader.py           # High-speed multi-year 5m/60m intraday data loader
│   ├── backtester.py            # Event-driven vectorized execution simulator
│   ├── metrics.py               # Institutional performance analytics (Sharpe, Sortino, Beta)
│   └── swarm_runner.py          # Multithreaded parallel execution swarm
├── models/                      # Pluggable strategy model library
│   ├── base_model.py            # Abstract Base Strategy interface
│   ├── naive_sweep_reversal.py  # Model 1: Immediate limit sweep fade
│   ├── confirmation_reversal.py # Model 2: 5m close back inside range + extreme SL
│   ├── multi_target_scaleout.py # Model 3: 50% TP1 Midpoint + Breakeven + Runner
│   ├── silver_bullet.py         # Model 4: ICT Silver Bullet (9AM -> 10-11AM)
│   └── macro_breakout.py        # Model 5: 8:30 AM News momentum continuation
├── scripts/                     # CLI tools
│   ├── run_model_backtest.py    # Run backtest on specific model & hour
│   └── run_hourly_scan.py       # Run parallel swarm scan across all 24 hours
├── reports/                     # Quantitative research findings & audit reports
│   ├── 24_hour_cycle_findings.md# Complete 24h heatmap & regime breakdown
│   ├── 2026_backtest_report.md  # 2026 $50k portfolio audit
│   └── alpha_portfolio_study.md # Zero-beta alpha & portfolio diversification study
├── tests/                       # Automated test suite
│   └── test_models.py
└── requirements.txt
```

---

## Quickstart & CLI Usage

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Run Single Model Backtest
```bash
# Test Multi-Target Scale-Out model on QQQ for the 8:00 AM candle (9:00-10:00 AM window)
python3 scripts/run_model_backtest.py --model scaleout --ticker QQQ --hour 8 --capital 50000 --risk 0.01

# Test ICT Silver Bullet model on QQQ (9:00 AM candle -> 10:00-11:00 AM window)
python3 scripts/run_model_backtest.py --model silver_bullet --ticker QQQ --hour 9

# Test Naive Sweep Reversal model on SPY (5:00 AM candle -> 6:00-7:00 AM window)
python3 scripts/run_model_backtest.py --model naive --ticker SPY --hour 5
```

### 3. Run 24-Hour Swarm Scan
```bash
# Scan all hours from 4:00 AM to 6:00 PM in parallel across QQQ and SPY
python3 scripts/run_hourly_scan.py --model scaleout --tickers QQQ,SPY --hours 4,5,6,7,8,9,10,11,12,13,14,15,16,17,18
```

### 4. Run Test Suite
```bash
python3 -m unittest discover tests
```

---

## Available Models

| Model | CLI Identifier | Description |
| :--- | :--- | :--- |
| **Naive Sweep Reversal** | `naive` | Enters immediately upon breach of reference high/low with fixed buffer SL. |
| **Confirmation Reversal** | `confirmation` | Requires 5m bar to close back inside reference range; SL placed at sweep extreme. |
| **Multi-Target Scale-Out** | `scaleout` | 50% TP1 at Midpoint (~80% win rate), moves SL to Breakeven, 50% runner at Opposite Level. |
| **ICT Silver Bullet** | `silver_bullet` | Optimized for 9:00 AM reference candle / 10:00 AM – 11:00 AM execution window. |
| **Macro Breakout** | `breakout` | Momentum continuation model for 8:30 AM news releases (7:00 AM reference candle). |

---

## Key Empirical Findings (2010–2026)

- **Pure Mean-Reversion Sweet Spot (4:00–6:00 AM)**: SPY 5:00 AM reference candle delivers **Sharpe +0.62** with **-0.05 correlation to the S&P 500**, acting as true market-neutral alpha.
- **8:30 AM Macro Velocity Spike (7:00 AM Reference)**: Swept in **~96%** of sessions, with **~60%** in-window complete opposite-side traversal.
- **ICT Silver Bullet (9:00 AM Reference)**: Delivers **+25.32% return, +0.20 Sharpe, and 46.15% win rate** on QQQ.
