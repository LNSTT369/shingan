<div align="center">

  <p>
    <img src="assets/shingan_equity_curve.png" alt="Shingan equity curve" width="100%" style="border-radius:14px; border:1px solid #5A5E66;" />
  </p>

  <h1 style="font-family:'Inter Display',Inter,system-ui,sans-serif; font-size:42px; font-weight:800; letter-spacing:-1.5px; color:#0A0A0B; margin:18px 0 6px 0;">SHINGAN</h1>
  <p style="font-family:Inter,system-ui,sans-serif; font-size:13px; letter-spacing:4px; text-transform:uppercase; color:#5A5E66; margin:0;">Clear-Eyed Lens — Hybrid Opening Range Breakout</p>
  <p style="width:44px; height:2px; background:#C5FF3F; margin:14px auto;"></p>
  <p style="font-family:Inter,system-ui,sans-serif; font-size:14px; color:#3A3A3E; max-width:640px; margin:0 auto; line-height:1.6;">
    Zarattini 5m momentum &times; Valkyrie volatility normalization &times; ORBPLUS execution.<br/>
    150L core. One CLI. Top-K portfolio. No bloat.
  </p>

  <p style="margin:16px 0 0 0;">
    <img src="https://img.shields.io/badge/Sharpe-1.21-0A0A0B?style=for-the-badge&labelColor=0A0A0B&color=0A0A0B" alt="Sharpe 1.21" />
    <img src="https://img.shields.io/badge/PF-1.25-18220E?style=for-the-badge&labelColor=18220E&color=18220E" alt="PF 1.25" />
    <img src="https://img.shields.io/badge/2021--2025-%2B108.7%25-C5FF3F?style=for-the-badge&labelColor=0A0A0B&color=C5FF3F" alt="+108.7%" />
    <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge" alt="Python" />
    <img src="https://img.shields.io/badge/ponytail-ultra-9ED832?style=for-the-badge&labelColor=0A0A0B&color=9ED832" alt="ponytail ultra" />
  </p>

  <p style="font-family:'JetBrains Mono',monospace; font-size:11px; color:#5A5E66; margin:8px 0 0 0;">44 tickers &middot; Top5 by RVOL &middot; 1262 trades &middot; 16.8% MaxDD &middot; 6 tests OK</p>

</div>

---

<div align="center">

> *“Anything added dilutes everything else.”* — ponytail &nbsp;|&nbsp; *“Perfection when nothing left to take away.”* — Saint-Exupéry &nbsp;|&nbsp; *Formerly `hourly-liquidity-lab` — hourly fade was -95%, now archived to `models/legacy/`.*

</div>

---

### ● Edge — Why Hybrid Alone Survives

<div align="center">

| <sub style="color:#5A5E66;">MODEL</sub> | <sub style="color:#5A5E66;">2021-2025 &middot; 44 Top5</sub> | <sub style="color:#5A5E66;">2024</sub> | <sub style="color:#5A5E66;">SHARPE</sub> | <sub style="color:#5A5E66;">PF</sub> | <sub style="color:#5A5E66;">DD</sub> |
| :--- | ---: | ---: | ---: | ---: | ---: |
| **Shingan 5m &middot; RVOL≥1.5 φ[0.6,2.0] 2R** | **1262 &middot; +108.7%** | **321 &middot; +53.0%** | **1.21** | **1.25** | **16.8%** |
| Valkyrie 15m same filters | 2252 &middot; +101.9% | 257 &middot; +40.6% | 0.80 | 1.17 | 15.8% |
| Zarattini naive 5m no filter | 6275 &middot; +220% | 1260 &middot; +70% | 0.37 | 1.04 | 60.1% |
| SPY naive 15m (control) | -95% | — | -2.14 | — | — |

<sub>Filters are necessary: no RVOL → Sharpe 0.37 vs 1.21, DD 60% vs 16.8% — <code>SHINGAN_Hybrid_ORB_Paper.md:186</code>. Full WFO in <code>SHINGAN_ArXiv_Paper.pdf</code>.</sub>

</div>

<p align="center">
  <img src="assets/shingan_heatmap.png" alt="heatmap OR×R×RVOL" width="49%" style="border:1px solid #5A5E66; border-radius:10px;" />
  <img src="assets/shingan_drawdown.png" alt="drawdown" width="49%" style="border:1px solid #5A5E66; border-radius:10px;" />
</p>

---

### ● Architecture — One Engine, No Bloat

```text
shingan/
├── engine/
│   ├── data_loader.py      # 5m OHLCV, UTC → America/New_York
│   ├── backtester.py       # 1% risk, $0.005/share + 0.01% slip, SPY beta
│   ├── metrics.py          # Sharpe / Sortino / PF / MaxDD
│   └── swarm_runner.py     # run_hybrid_portfolio + run_hybrid_heatmap — single Top-K loop
├── models/
│   ├── base_model.py       # MARKET_OPEN 570 · CLOSE 960
│   ├── hybrid_orb.py       # 150L: 5m/15m OR · RVOL≥1.5 · φ[0.6,2.0] · seq trap lockout · 2R + BE@1R · 15:00 +1% lock · 15:55 flat
│   └── legacy/             # 5 dead fade models — YAGNI, kept for paper audit only
├── scripts/
│   └── run_model_backtest.py  # one CLI: single run + --heatmap
└── tests/test_models.py    # 6 tests · 2024 parity 321 trades 53.03%
```

Ponytail ultra: `293→150L` hybrid, `1587→900L (-43%)`, retrace deleted (WR 3.8% never fills), 3 scripts → 1 CLI.

---

### ● Strategy — `models/hybrid_orb.py:5`

| <sub style="color:#5A5E66;">LAYER</sub> | <sub style="color:#5A5E66;">RULE</sub> | <sub style="color:#5A5E66;">SOURCE</sub> |
| :--- | :--- | :--- |
| **OR** | 5m `09:30-09:34:59` one bar or 15m `09:30-09:44:59` three bars — `or_minutes` | Zarattini 5m / Valkyrie 15m |
| **RVOL** | `today_vol / mean(prior 14d same OR) ≥ 1.5` — rank 44 each open, take **Top5** | `engine/swarm_runner.py:15` |
| **φ** | `spread / ATR14 ∈ [0.6, 2.0]` — cuts chop & exhaustion | Valkyrie, ORBPLUS 0.1-1.6× |
| **Signal** | 5m: `C≥O → LONG else SHORT` · 15m: `low_first+green → LONG`, `high_first+red → SHORT` else `REJECT trap` | `models/hybrid_orb.py:60` |
| **Bracket** | `LONG high+0.01 / SHORT low-0.01` stop, SL opposite `∓0.01`, TP `entry ± 2R`, BE at +1R, 15:00 +1% lock, 15:55 flat | `models/hybrid_orb.py:75` |
| **Sizing** | `qty = floor(equity·0.01 / risk)` per name, max 5% daily | `engine/backtester.py:13` |

---

### ⚡ Quickstart

```bash
pip install -r requirements.txt

# primary cell — 2024 44 Top5
python3 scripts/run_model_backtest.py --or-minutes 5 --target-r 2.0 --min-rvol 1.5 --phi-min 0.6 --phi-max 2.0 --top-k 5 --start_year 2024 --end_year 2024
# → 321 trades · 53.03% · PF 1.69 · Sharpe 2.59 · DD 9.87%

# concatenated OOS 2021-2025 — paper Table 6.2
python3 scripts/run_model_backtest.py --or-minutes 5 --target-r 2.0 --min-rvol 1.5 --start_year 2021 --end_year 2025
# → 1262 trades · 108.7% · Sharpe 1.21

# full heatmap OR(5,15) × R(1.5,2,3) × RVOL(1.2,1.5,2)
python3 scripts/run_model_backtest.py --heatmap --start_year 2021 --end_year 2025

# tests
python3 -m unittest discover tests -v
```

<p align="center">
  <img src="assets/shingan_monthly.png" alt="monthly" width="100%" style="border:1px solid #5A5E66; border-radius:10px;" />
  <br/><sub style="color:#5A5E66;">Monthly — 1 trade/day across 44 names, β 0.05 to SPY, true intraday alpha.</sub>
</p>

---

### ● Why Not Hourly Fade?

`INCIDENT_REPORT.md:1` root cause: ad-hoc `r_mult` sum without `Backtester.run()`, tight $0.30 SL → 1,600 shares per $500 risk → $75 fee (18% of risk) → 2,700 trades → -$240k friction. Formal engine + SPY benchmark is the only valid metric. **Gross vs net audit mandatory.**

---

### ● Reproduce

```bash
git clone https://github.com/LNSTT369/shingan.git
pip install -r requirements.txt
python3 scripts/run_model_backtest.py --or-minutes 5 --target-r 2.0 --min-rvol 1.5 --start_year 2021 --end_year 2025
```

---

### ● References

* Zarattini et al. 2024 SSRN 24-97 — 5m OR, 1,000 stocks, Sharpe 2.40
* Valkyrie ORB `STRATEGY.md:1` — 15m OR, seq+color lockout, RVOL+phi
* ORBPLUS — retrace 50% +0.0538R vs instant -0.0082R, WR 3.8% removed in ultra
* `SHINGAN_Hybrid_ORB_Paper.md:1` · `SHINGAN_ArXiv_Paper.pdf` — full 44-ticker WFO

---

<div align="center">

  <p style="width:44px; height:2px; background:#C5FF3F; margin:12px auto;"></p>
  <p style="font-family:'Inter',system-ui,sans-serif; font-size:12px; letter-spacing:2px; text-transform:uppercase; color:#5A5E66;">SYSTEMS</p>

  <p style="font-family:'JetBrains Mono',monospace; font-size:11px; color:#5A5E66;">
    <a href="https://github.com/LNSTT369/valkyrie_orb" style="color:#F5F5F5; text-decoration:none; border:1px solid #5A5E66; padding:4px 8px; border-radius:6px;">VALKYRIE 15M</a>
    &nbsp;→&nbsp;
    <span style="color:#0A0A0B; background:#C5FF3F; padding:4px 10px; border-radius:6px; font-weight:700;">SHINGAN HYBRID</span>
    &nbsp;→&nbsp;
    <a href="https://github.com/LNSTT369/NightWatcher" style="color:#F5F5F5; text-decoration:none; border:1px solid #5A5E66; padding:4px 8px; border-radius:6px;">NIGHTWATCHER</a>
  </p>

  <p style="margin:18px 0 0 0;">
    <a href="https://chiranjeevportfolio.vercel.app/" style="text-decoration:none; border:1px solid #5A5E66; padding:8px 14px; border-radius:6px; color:#F5F5F5; font-family:'JetBrains Mono',monospace; font-size:12px;">Portfolio</a>
    <a href="https://linkedin.com/in/chiranjeevshah" style="text-decoration:none; border:1px solid #5A5E66; padding:8px 14px; border-radius:6px; color:#F5F5F5; font-family:'JetBrains Mono',monospace; font-size:12px; margin-left:6px;">LinkedIn</a>
    <a href="https://x.com/showtimeshah" style="text-decoration:none; border:1px solid #5A5E66; padding:8px 14px; border-radius:6px; color:#F5F5F5; font-family:'JetBrains Mono',monospace; font-size:12px; margin-left:6px;">Twitter</a>
    <a href="https://www.topmate.io/showtime/" style="text-decoration:none; border:1px solid #5A5E66; padding:8px 14px; border-radius:6px; color:#F5F5F5; font-family:'JetBrains Mono',monospace; font-size:12px; margin-left:6px;">Topmate</a>
    <a href="https://soundcloud.com/latenightwithshowtime" style="text-decoration:none; border:1px solid #5A5E66; padding:8px 14px; border-radius:6px; color:#F5F5F5; font-family:'JetBrains Mono',monospace; font-size:12px; margin-left:6px;">SoundCloud</a>
  </p>

  <p style="font-family:Inter,system-ui,sans-serif; font-size:11px; color:#5A5E66; margin:16px 0 0 0;"><em>Shingan — Clear-Eyed Lens. Perfection when nothing left to take away.</em></p>

</div>
