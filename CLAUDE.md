# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SmartMoneyTracker is a modular Python application for automated scanning and analysis of stocks across A-shares, US stocks, and Hong Kong stocks markets. The goal is to identify signals indicating institutional investors ("smart money") movements throughout the complete cycle from **accumulation (inflow)** to **distribution (outflow)**.

**Core Principle**: The system does not rely on any single indicator. It integrates data from multiple dimensions (price-volume analysis, technical indicators, market microstructure, shareholder structure, and macro capital flows) to calculate a comprehensive **"institutional movement score"** (ranging from -10 to +10) and generate analysis reports. Positive scores indicate accumulation/buying, while negative scores indicate distribution/selling.

## Technology Stack

- **Language**: Python 3.9+
- **Core Libraries**: Pandas, NumPy, Requests, Matplotlib/Plotly
- **Data Sources**:
  - **AkShare (default for A-shares)** - no token required, works out of box
  - Tushare (fallback for A-shares) - requires token
  - yfinance (US/HK stocks)
- **Concurrency**: concurrent.futures or asyncio for multi-stock scanning

## System Architecture

The project follows a modular design with four layers:

```
smart-money-tracker/
├── main.py                         # Main entry point, orchestrates scanning workflow
├── config.py                       # Configuration (API keys, stock pools, thresholds)
├── requirements.txt                # Dependencies
│
├── data_fetcher/                   # Data acquisition layer
│   ├── __init__.py
│   └── manager.py                  # Unified data API manager
│
├── analysis/                       # Signal analysis layer (core logic)
│   ├── __init__.py
│   ├── price_volume_signals.py    # Price-volume relationship signals (accumulation & distribution)
│   ├── indicator_signals.py       # Technical indicator signals (divergence, etc.)
│   ├── disclosure_signals.py      # Public disclosure signals (shareholders, announcements)
│   ├── microstructure_signals.py  # Market microstructure signals (Level-2 data)
│   └── relative_strength.py       # Relative strength signals
│
├── aggregator/                     # Signal aggregation layer
│   ├── __init__.py
│   └── scorer.py                  # Signal scoring and comprehensive rating
│
└── reporting/                      # Report generation layer
    ├── __init__.py
    └── generator.py               # Generate text or HTML reports
```

## Key Analysis Modules

### Price-Volume Analysis (analysis/price_volume_signals.py)

Core patterns for detecting institutional accumulation and distribution:

**Accumulation (Inflow) Signals:**

1. **Volume Breakout** (`detect_accumulation_breakout`)
   - Detects volume surge (>vol_multiplier × average) with upward breakout from consolidation
   - Indicates institutions beginning to push price higher after accumulation phase

2. **Wyckoff Spring/Shakeout** (`detect_wyckoff_spring`)
   - Price briefly breaks below support then quickly recovers on low volume
   - Classic institutional tactic to shake out weak hands before markup phase

**Distribution (Outflow) Signals:**

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

Focus on divergence detection and extreme readings:

**OBV (On-Balance Volume) Signals:**

1. **OBV Bullish Divergence** (`detect_obv_divergence`)
   - Price makes new low but OBV refuses to follow (forms higher low)
   - Accumulative volume indicator showing capital inflow despite price weakness
   - Strong accumulation signal

2. **OBV Bearish Divergence** (`detect_obv_divergence`)
   - Price makes new high but OBV fails to confirm (forms lower high)
   - Accumulative volume indicator showing capital outflow despite price strength
   - Strong distribution signal

**MFI (Money Flow Index) Signals:**

1. **MFI Bullish Signals** (`detect_mfi_signals`)
   - Bullish divergence: price new low, MFI higher low
   - Oversold condition: MFI < 20
   - Indicates buying pressure building

2. **MFI Bearish Signals** (`detect_mfi_signals`)
   - Bearish divergence: price new high, MFI lower high
   - Overbought condition: MFI > 80
   - Indicates selling pressure building

### Disclosure Signals (analysis/disclosure_signals.py)

Tracking official disclosures for both accumulation and distribution:

1. **Shareholder Structure Analysis** (`analyze_shareholder_structure`)

   **Accumulation Signals:**
   - New prominent institutions enter top 10 shareholders
   - Existing institutions increase positions significantly
   - Shareholder count decreases (chips concentrating from many to few)

   **Distribution Signals:**
   - Institutions reduce holdings or exit top 10 shareholders list
   - Shareholder count increases (chips dispersing from few to many)

   **Market-specific approaches:**
   - **A-shares**: Monitor top 10 shareholders (public funds, QFII, social security funds) quarterly
   - **US stocks**: Parse 13F filings for institutional position changes (quarterly, 45-day lag)
   - **HK stocks**: Track Disclosure of Interests (DI) for major shareholder movements (real-time when crossing integer % thresholds)

### Microstructure Signals (analysis/microstructure_signals.py)

Level-2 order book analysis:

1. **Order Book Analysis** (`analyze_order_book`)

   **Accumulation Signals:**
   - Persistent, genuine "bid walls" at key support levels
   - Large buy orders that actually get filled

   **Distribution Signals:**
   - Persistent, genuine "ask walls" at key resistance levels
   - Large sell orders continuously absorbing buying pressure

   **Important considerations:**
   - Watch for spoofing (orders placed but canceled before execution)
   - Distinguish iceberg orders (only partial order size displayed)
   - Focus on whether large orders are actually executed

### Relative Strength (analysis/relative_strength.py)

1. **RSP Analysis** (`analyze_rsp`)
   - Calculate stock price / benchmark (sector ETF or index) ratio
   - **Accumulation signal**: Rising RSP = outperformance = institutional rotation into the stock
   - **Distribution signal**: Declining RSP = underperformance = institutional rotation away from the stock
   - Most useful during market consolidation periods to identify where smart money is flowing

## Market-Specific Considerations

### A-Shares Market
- **Trading Rules**: T+1, ~10% price limits
- **Investor Structure**: Retail-dominated by volume, institutions by market cap
- **Key Data Sources**:
  - **AkShare (default)**: Daily prices, Northbound funds, shareholder data - no token required
  - Tushare (fallback): Same data with token
  - Top 10 shareholders from quarterly reports
  - Director/executive holdings changes
- **Analysis Focus**:
  - Policy impact and government guidance
  - Retail sentiment vs institutional positioning
  - Quarterly holding changes
  - Northbound capital flow trends (smart money proxy)

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

## Scoring System

Signal weights defined in `config.py` with bidirectional scoring:

```python
SIGNAL_WEIGHTS = {
    # Inflow Signals (Positive Score)
    'ACCUMULATION_BREAKOUT': 2,
    'WYCKOFF_SPRING': 2,
    'OBV_BULLISH_DIVERGENCE': 2,
    'MFI_OVERSOLD': 1,
    'MFI_BULLISH_DIVERGENCE': 2,
    'NEW_INSTITUTION': 3,          # Highest weight - direct evidence
    'SHAREHOLDER_COUNT_DECREASE': 1,
    'BID_WALL_SUPPORT': 1,
    'RSP_STRONG': 1,

    # Outflow Signals (Negative Score)
    'HIGH_VOLUME_STAGNATION': -2,
    'HIGH_VOLUME_DECLINE': -2,
    'BREAK_SUPPORT_HEAVY_VOLUME': -3,
    'OBV_BEARISH_DIVERGENCE': -2,
    'MFI_OVERBOUGHT': -1,
    'MFI_BEARISH_DIVERGENCE': -2,
    'INSTITUTIONAL_SELL_OFF': -3,  # Highest weight - direct evidence
    'SHAREHOLDER_COUNT_INCREASE': -1,
    'ASK_WALL_PRESSURE': -1,
    'RSP_WEAK': -1,
    # ... other signals
}
```

**Score Range**: -10 to +10

**Score-to-Rating Mapping**:
- **+6 to +10**: STRONG_BUY - Strong institutional accumulation
- **+2 to +5**: BUY - Moderate institutional accumulation
- **-1 to +1**: NEUTRAL - No clear directional bias
- **-5 to -2**: SELL - Moderate institutional distribution
- **-10 to -6**: STRONG_SELL - Strong institutional distribution

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

1. **The Two Sides of the Coin**: Institutional capital operates in a complete cycle from accumulation to distribution. Understanding both phases provides complete market insight - from quiet positioning at bottoms, through trend acceleration, to subtle distribution at tops, and finally clear exit signals.

2. **Multi-Signal Confirmation**: Never rely on single indicator. High-confidence detection (whether accumulation or distribution) requires convergence of signals across different dimensions.

3. **Signal Sequence**: Institutional movements often follow a pattern:
   - Market signals (price-volume, divergence) appear first (leading indicators)
   - Fundamental catalysts surface later (lagging confirmation)
   - Official disclosures come last (definitive but delayed)

4. **Market Context**: Always consider:
   - Individual stock vs sector performance (relative strength)
   - Individual stock vs market index performance
   - Sector rotation patterns

5. **Level-2 Data** (when available): Provides granular view:
   - 10-level depth of market
   - Order imbalance ratio (SOIR)
   - Iceberg orders and spoofing detection
   - Algorithmic trading footprints (steady medium-sized orders indicating institutional activity)

## Configuration Requirements

When implementing config.py, include:
- **Data source settings**:
  - A_STOCK_DATA_SOURCE: 'akshare' (default, no token) or 'tushare' (requires token)
  - AKSHARE_ENABLED: True/False
  - TUSHARE_TOKEN: API token (only needed for Tushare)
- Stock pool definitions (can be loaded from file)
- **Signal weight configurations** (bidirectional: positive for accumulation, negative for distribution)
- Threshold parameters (volume multipliers, divergence lookback periods)
- Market-specific parameters (different settings for A/US/HK)

## Report Output Format

Generated reports should include:
- Ticker and scan date
- **Overall score (-10 to +10)** and rating (STRONG_BUY/BUY/NEUTRAL/SELL/STRONG_SELL)
- **Separated sections**:
  - Inflow Signals Triggered (accumulation signals with positive scores)
  - Outflow Signals Triggered (distribution signals with negative scores)
- List of triggered signals with individual scores
- Date of signal occurrence
- Specific details (e.g., which institution entered/exited holdings, which support/resistance level broken)
- Recommendation summary (e.g., "High probability of institutional accumulation. Trend is bullish." or "Institution distribution probability high. Exercise caution.")
