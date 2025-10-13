# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SmartMoneyTracker is a modular Python application for automated scanning and analysis of stocks across A-shares, US stocks, and Hong Kong stocks markets. The goal is to identify signals indicating institutional investors ("smart money") may be exiting positions.

**Core Principle**: The system does not rely on any single indicator. It integrates data from multiple dimensions (price-volume analysis, technical indicators, market microstructure, shareholder structure, and macro capital flows) to calculate a comprehensive "exit risk score" and generate analysis reports.

## Technology Stack

- **Language**: Python 3.9+
- **Core Libraries**: Pandas, NumPy, Requests, Matplotlib/Plotly
- **Data Sources**:
  - Tushare (A-shares primary data source)
  - AkShare (supplementary A-shares data)
  - yfinance (US/HK stocks)
- **Concurrency**: concurrent.futures or asyncio for multi-stock scanning

## System Architecture

The project follows a modular design with four layers:

```
institutional-exit-scanner/
├── main.py                 # Main entry point, orchestrates scanning workflow
├── config.py               # Configuration (API keys, stock pools, thresholds)
├── requirements.txt        # Dependencies
│
├── data_fetcher/           # Data acquisition layer
│   ├── __init__.py
│   └── manager.py          # Unified data API manager
│
├── analysis/               # Signal analysis layer (core logic)
│   ├── __init__.py
│   ├── pv_signals.py       # Price-volume relationship signals
│   ├── indicator_signals.py # Technical indicator signals
│   ├── structural_signals.py # Structural signals (shareholders, announcements)
│   └── relative_strength.py # Relative strength signals
│
├── aggregator/             # Risk aggregation layer
│   ├── __init__.py
│   └── scorer.py           # Signal scoring and risk rating
│
└── reporting/              # Report generation layer
    ├── __init__.py
    └── generator.py        # Generate text or HTML reports
```

## Key Analysis Modules

### Price-Volume Analysis (analysis/pv_signals.py)

Core patterns for detecting institutional distribution:

1. **High Volume Stagnation at Peak** (`detect_high_volume_stagnation`)
   - Detects volume surge with price stagnation after significant uptrend
   - Indicates capital transfer from "strong hands" to "weak hands"

2. **Heavy Volume Decline** (`detect_high_volume_decline`)
   - Price drops significantly on elevated volume
   - Most direct exit signal - panic selling by institutions

3. **Break Support with Volume** (`detect_break_support`)
   - Price breaks key support (60-day MA, previous lows) on high volume
   - Confirms psychological shift in market

### Technical Indicators (analysis/indicator_signals.py)

Focus on divergence detection:

1. **OBV Bearish Divergence** (`detect_obv_bearish_divergence`)
   - Price makes new high but OBV fails to confirm
   - Accumulative volume indicator showing capital outflow

2. **MFI Bearish Divergence** (`detect_mfi_bearish_divergence`)
   - Similar to OBV but as oscillator (0-100 range)
   - Earlier warning signal due to shorter timeframe

### Structural Signals (analysis/structural_signals.py)

Tracking official disclosures:

1. **Institutional Holdings Analysis** (`analyze_institutional_holdings`)
   - A-shares: Monitor top 10 shareholders (public funds, QFII, social security)
   - US stocks: Parse 13F filings for institutional position changes
   - HK stocks: Track Disclosure of Interests (DI) for major shareholder movements

2. **Shareholder Count Analysis** (`analyze_shareholder_count`)
   - Increasing shareholder count + decreasing institutional holdings = distribution
   - Classic signal: chips dispersing from few large holders to many retail investors

### Relative Strength (analysis/relative_strength.py)

1. **RSP Analysis** (`analyze_rsp`)
   - Calculate stock price / benchmark (sector ETF or index) ratio
   - Declining RSP = underperformance = institutional rotation away

## Market-Specific Considerations

### A-Shares Market
- **Trading Rules**: T+1, ~10% price limits
- **Investor Structure**: Retail-dominated by volume, institutions by market cap
- **Key Data Sources**:
  - Northbound funds (Shanghai/Shenzhen-HK Connect) via Tushare
  - Top 10 shareholders from quarterly reports
  - Director/executive holdings changes
- **Analysis Focus**: Policy impact, retail sentiment, quarterly holding changes

### US Market
- **Trading Rules**: T+0, no price limits
- **Investor Structure**: Institution-dominated (~80% of NYSE volume)
- **Key Data Sources**:
  - 13F filings (quarterly, 45-day lag) via SEC EDGAR
  - Form 4 insider transactions (2-day reporting)
  - TIC reports for international capital flows
- **Analysis Focus**: Fed policy, macro flows, institutional 13F changes, insider trading

### Hong Kong Market
- **Trading Rules**: T+0 trading, T+2 settlement, no price limits
- **Investor Structure**: International institutions + Mainland capital
- **Key Data Sources**:
  - Disclosure of Interests (DI) - real-time when crossing integer percentage thresholds
  - Southbound funds (HK Stock Connect) - daily data
  - HKEx short selling data
- **Analysis Focus**: Southbound flow dynamics, DI filings, international capital

## Risk Scoring System

Signal weights defined in `config.py` (example):

```python
SIGNAL_WEIGHTS = {
    'HIGH_VOLUME_STAGNATION': 1,
    'OBV_DIVERGENCE': 2,
    'INSTITUTIONAL_SELL_OFF': 3,  # Highest weight - direct evidence
    'BREAK_SUPPORT_HEAVY_VOLUME': 3,
    'MFI_DIVERGENCE': 2,
    'RELATIVE_STRENGTH_WEAK': 1,
    # ... other signals
}
```

Risk levels: LOW / MEDIUM / HIGH based on cumulative score.

## Development Phases

1. **Phase 1**: Implement data_fetcher/manager.py
2. **Phase 2**: Implement core analysis modules (analysis/)
3. **Phase 3**: Implement risk aggregator (aggregator/scorer.py)
4. **Phase 4**: Implement report generator (reporting/generator.py)
5. **Phase 5**: Integrate main.py and conduct end-to-end testing

## Testing Strategy

- Backtest signals against historical data
- Validate against known institutional exit cases
- Tune signal weights to optimize risk scoring accuracy

## Important Analysis Principles

1. **Multi-Signal Confirmation**: Never rely on single indicator. High-confidence exit detection requires convergence of signals across different dimensions.

2. **Signal Sequence**: Institutional exits often follow a pattern:
   - Market signals (price-volume, divergence) appear first (leading indicators)
   - Fundamental catalysts surface later (lagging confirmation)
   - Official disclosures come last (definitive but delayed)

3. **Market Context**: Always consider:
   - Individual stock vs sector performance (relative strength)
   - Individual stock vs market index performance
   - Sector rotation patterns

4. **Level-2 Data** (when available): Provides granular view:
   - 10-level depth of market
   - Order imbalance ratio (SOIR)
   - Iceberg orders and spoofing detection
   - Algorithmic selling footprints (steady medium-sized sell orders)

## Configuration Requirements

When implementing config.py, include:
- API keys for data sources (Tushare token, etc.)
- Stock pool definitions (can be loaded from file)
- Signal weight configurations
- Threshold parameters (volume multipliers, divergence lookback periods)
- Market-specific parameters (different settings for A/US/HK)

## Report Output Format

Generated reports should include:
- Ticker and scan date
- Risk score (0-10) and risk level (LOW/MEDIUM/HIGH)
- List of triggered signals with individual scores
- Date of signal occurrence
- Specific details (e.g., which institution reduced holdings, which support level broken)
- Recommendation summary
