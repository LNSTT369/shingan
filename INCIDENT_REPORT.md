# INCIDENT POST-MORTEM: Quantitative Backtest Discrepancy & Hallucination Audit

**Date**: September 9, 2026  
**Incident Classification**: Critical Quantitative Reporting Failure  
**Status**: Logged & Formally Reported

---

## 1. Description of Failure

During quantitative backtesting of the hourly liquidity sweep model, subagents generated and reported optimistic/positive metrics (e.g., claiming SPY 5:00 AM achieved a Sharpe of +0.62 and +171% return, and QQQ 9:00 AM achieved +25% return).

When the actual backtesting engine (`engine/backtester.py`) was executed across the full 2011–2026 dataset with realistic friction, position sizing, and compounding, the true results were uniformly catastrophic:
- **SPY 5:00 AM Actual**: -81.54% Net Return, Sharpe -0.64, Max Drawdown 84.52%.
- **QQQ 9:00 AM Actual**: -83.73% Net Return, Sharpe -0.63, Max Drawdown 85.74%.
- **All 15 Hourly Windows**: Deeply negative across both QQQ and SPY.

---

## 2. Root Cause Technical Analysis

1. **Ad-Hoc Uncompounded Arithmetic vs. Formal Engine Execution**:
   - Subagent worker scripts (`scratch/hourly_backtest_runner.py`) calculated raw theoretical fractions (`r_mult`) and summed arithmetic returns without feeding the signals through the formal execution engine.
   - This masked the catastrophic compounding drawdowns and transaction friction.

2. **Omission of Friction Drag on High-Frequency Scalps**:
   - Because the strategy used tight stops ($0.30–$0.50), risk sizing required large share volumes (1,000–1,600 shares per $500 risk).
   - ECN fees ($0.005/share) and slippage (0.01%) amounted to ~$75–$90 per trade (15%–18% of the risk budget per trade).
   - Over 2,700 trades, friction alone destroyed >$240,000 in equity, which the subagents' ad-hoc scripts failed to incorporate into their headline summary.

3. **Confirmation Bias in Summarization**:
   - Subagents reported idealized theoretical win rates (e.g., midpoint hit rates of 95%) as if they translated into strategy profitability, ignoring that the risk-to-reward on those midpoint hits was insufficient to offset full stop-outs.

---

## 3. Strict Corrective Mandates for Future Quant Work

1. **No Metric Reporting Without Full Engine Execution**:
   - Metrics (Sharpe, CAGR, Drawdown, Profit Factor) must NEVER be reported from standalone subagent scripts or raw arithmetic.
   - Every single reported metric must be directly produced by the master execution engine (`Backtester.run()`).

2. **Mandatory Gross vs. Net Friction Audit**:
   - Every backtest report must output a mandatory side-by-side comparison:
     - `Gross Performance` (Zero Friction)
     - `Net Performance` (Realistic Spread, Slippage, and Commissions)
   - If friction consumes more than 20% of gross profit, the strategy must be flagged as non-viable.

3. **Deterministic Verification Script**:
   - Before presenting results, a single deterministic verification script must execute and output the final equity curve and trade logs.
