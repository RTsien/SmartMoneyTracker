# SmartMoneyTracker

**English** | [简体中文](README.zh-CN.md)

> Follow the smart money: identify the full institutional capital cycle—from accumulation to distribution—through multidimensional market analysis.

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 Overview

SmartMoneyTracker is a modular Python application that automatically scans and analyzes stocks across the **Chinese A-share, US, and Hong Kong markets**. It identifies signals throughout the full institutional capital cycle, from **entry and accumulation** to **exit and distribution**.

Institutional capital comes from mutual funds, pension funds, hedge funds, QFIIs, and high-net-worth investors. These participants follow different strategies, time horizons, and execution methods, leaving distinct footprints in the market. Identifying the complete cycle can help with:

- ✅ **Risk management** — avoid buying into institutional distribution
- ✅ **Opportunity discovery** — detect early signs of institutional accumulation
- ✅ **Tactical positioning** — align positioning with institutional sentiment
- ✅ **Trend anticipation** — identify potential trend breakouts and reversals

## 🎯 Key Features

### Multidimensional Analysis

The system **does not rely on a single indicator**. Instead, it combines bidirectional signals from several independent areas of analysis:

1. **Price and volume**
   - **Accumulation:** high-volume consolidation near a bottom, high-volume resistance breakouts, and Wyckoff accumulation patterns such as springs and last points of support (LPS)
   - **Distribution:** high-volume price stagnation near a top, high-volume support breakdowns, and low-volume rallies at elevated prices

2. **Technical indicators**
   - **Accumulation:** bullish OBV/MFI divergence and oversold MFI readings below 20
   - **Distribution:** bearish OBV/MFI divergence and overbought MFI readings above 80

3. **Market microstructure** ⚠️ *Requires a commercial Level 2 data feed*
   - **Accumulation:** persistent bid walls at key support levels
   - **Distribution:** persistent sell walls at key resistance levels
   - Level 2 order-book analysis, static order imbalance ratio (SOIR), and algorithmic execution footprint detection
   - **Note:** the module interfaces are implemented, but a commercial data provider such as Wind or Eastmoney Choice is required. The 20+ signals supported by the free AkShare, Tushare, and yfinance sources remain useful without this module.

4. **Ownership structure**
   - **Accumulation:** new institutional shareholders and a declining shareholder count
   - **Distribution:** institutional selling and a rising shareholder count
   - Changes in shareholdings by directors and senior executives

5. **Relative strength**
   - **Accumulation:** sustained RSP outperformance against a market or sector benchmark
   - **Distribution:** sustained RSP underperformance against a market or sector benchmark
   - Stock-to-sector comparisons and stock-to-market divergence detection

6. **Fundamental catalysts**
   - **Accumulation catalysts:** product launches, improving industry conditions, earnings beats, and favorable policies
   - **Distribution catalysts:** accounting fraud, executive misconduct, earnings warnings, and adverse regulation

### Bidirectional Scoring

- Weighted aggregation across multiple signals
- Composite directional score from **-10 to +10**:
  - **+6 to +10:** `STRONG_BUY` — strong accumulation signals
  - **+2 to +5:** `BUY` — moderate accumulation signals
  - **-1 to +1:** `NEUTRAL` — no clear direction
  - **-5 to -2:** `SELL` — moderate distribution signals
  - **-10 to -6:** `STRONG_SELL` — strong distribution signals
- Human-readable analysis reports

## 🏗️ Architecture

```text
SmartMoneyTracker/
├── app.py                         # Web application
├── main.py                        # CLI and scanner entry point
├── config.py                      # Configuration
├── requirements.txt               # Python dependencies
├── Dockerfile
├── docker-compose.yml
│
├── data_fetcher/                  # Data access layer
│   ├── __init__.py
│   └── manager.py                 # Unified data API manager
│
├── analysis/                      # Signal analysis layer
│   ├── __init__.py
│   ├── price_volume_signals.py    # Accumulation and distribution signals
│   ├── indicator_signals.py       # Technical indicator signals
│   ├── disclosure_signals.py      # Ownership and disclosure signals
│   ├── microstructure_signals.py  # Level 2 microstructure signals
│   └── relative_strength.py       # Relative-strength signals
│
├── aggregator/                    # Signal aggregation layer
│   ├── __init__.py
│   └── scorer.py                  # Scoring and composite ratings
│
├── reporting/                     # Reporting layer
│   ├── __init__.py
│   └── generator.py               # Text and HTML reports
│
├── static/                        # Web assets
├── templates/                     # Web templates
└── tests/                         # Test suite
```

## 🚀 Getting Started

### Docker (Recommended) 🐳

Run the application without configuring a local Python environment:

```bash
git clone https://github.com/RTsien/SmartMoneyTracker.git
cd SmartMoneyTracker

docker-compose up -d
```

Open [http://localhost:8001](http://localhost:8001) in your browser.

For more information, see the [Docker deployment guide](DOCKER.md) *(Chinese)*.

### Local Installation

#### Requirements

- Python 3.9 or later
- pip

#### Installation

```bash
git clone https://github.com/RTsien/SmartMoneyTracker.git
cd SmartMoneyTracker

pip install -r requirements.txt
```

API credentials are optional. If you want to use Tushare, add your token in `config.py` or provide it through the supported environment configuration.

### Usage

#### Web Interface 🌐

```bash
python app.py
```

Open [http://localhost:8001](http://localhost:8001) in your browser.

The web interface provides:

- 🎨 A modern user interface
- 📊 Real-time analysis results
- 📈 Visual scores and signals
- 🔄 Single-stock and batch analysis
- 📱 A responsive layout for desktop and mobile devices

#### Command Line and Python API

Run a scan directly from the command line:

```bash
python3 main.py 600519.SH
```

Or use the scanner from Python:

```python
from main import SmartMoneyScanner

scanner = SmartMoneyScanner()

# Scan one stock: Kweichow Moutai (A-share)
result = scanner.scan_stock("600519.SH")
if result["success"]:
    print(result["report"])

# Scan stocks across multiple markets
stocks = ["600519.SH", "AAPL", "0700.HK"]
results = scanner.scan_batch(stocks)

for ticker, result in results.items():
    if result["success"]:
        print(f"\n{ticker}:")
        print(f"Score: {result['score']:+.1f}/10")
        print(f"Rating: {result['rating']}")
```

### Example Output

#### Distribution Signal

```text
===== Smart Money Tracker Report =====
Ticker: 600519.SH
Date: 2025-10-13
Overall Score: -7/10 (SELL)

--- Outflow Signals Triggered ---
[-] HIGH_VOLUME_STAGNATION (Score: -2) on 2025-09-15
    Volume surged after a substantial rally, but price stopped advancing.

[-] MFI_BEARISH_DIVERGENCE (Score: -2)
    Price reached a new high while the Money Flow Index did not confirm it.

[-] INSTITUTIONAL_SELL_OFF (Score: -3)
    China Merchants Fund reduced its position by 5%.

[-] RSP_WEAK (Score: -1)
    The stock underperformed the CSI Liquor Index.

--- Inflow Signals Triggered ---
(None)

Recommendation:
The probability of institutional distribution is elevated. Exercise caution;
large holders may be selling into retail enthusiasm.
```

#### Accumulation Signal

```text
===== Smart Money Tracker Report =====
Ticker: 000858.SZ
Date: 2025-10-13
Overall Score: +7/10 (BUY)

--- Inflow Signals Triggered ---
[+] ACCUMULATION_BREAKOUT (Score: +2) on 2025-10-10
    Price broke out of a long consolidation range on 2.5x average volume.

[+] OBV_BULLISH_DIVERGENCE (Score: +2)
    Price reached a new low while OBV held above its previous low.

[+] NEW_INSTITUTION (Score: +3)
    China Merchants Fund entered the top-ten shareholder list.

[+] SHAREHOLDER_COUNT_DECREASE (Score: +1)
    The shareholder count declined 15% quarter over quarter.

--- Outflow Signals Triggered ---
(None)

Recommendation:
The probability of institutional accumulation is high and the trend is bullish.
Shares may be moving from retail investors to institutions.
```

## 📊 Supported Markets

| Market | Data sources | Highlights |
|---|---|---|
| **Chinese A-shares** | **AkShare (default)**, Tushare | Northbound capital flows, top-ten shareholder analysis, and shareholder count analysis |
| **US stocks** | yfinance | Institutional ownership and daily market data |
| **Hong Kong stocks** | yfinance, AkShare | Institutional ownership and Stock Connect holdings |

## 📈 Data Sources

- **Daily market data**
  - Chinese A-shares: **AkShare (default)** or Tushare
  - US and Hong Kong stocks: yfinance
- **Level 2 data** ⚠️ **Not included; a commercial API is required**
  - Potential providers: Eastmoney Choice, Wind, and similar vendors
  - Use case: microstructure signals such as bid-wall and sell-wall detection
  - The architecture exposes extension points for a compatible data feed
- **Institutional holdings**
  - Chinese A-shares: **AkShare (default)** or Tushare (`top10_holders`, `stk_holdernumber`)
  - US stocks: **yfinance**
  - Hong Kong stocks: **yfinance and AkShare**
- **Capital flows**
  - Northbound flows: **AkShare (default)** or Tushare (`hk_hold`)
  - Southbound flows: Eastmoney API
- **Disclosures and news:** CNInfo and official exchange websites

## 🔧 Configuration

Configure the application in `config.py`:

```python
# Data source
A_STOCK_DATA_SOURCE = "akshare"  # "akshare" (default) or "tushare"
AKSHARE_ENABLED = True
TUSHARE_TOKEN = "your_token_here"  # Required only for Tushare

# Stocks to scan
STOCK_POOL = [
    "600519.SH",  # Kweichow Moutai
    "AAPL",       # Apple
    "0700.HK",    # Tencent
]

# Bidirectional signal weights
SIGNAL_WEIGHTS = {
    # Accumulation signals (positive)
    "ACCUMULATION_BREAKOUT": 2,
    "OBV_BULLISH_DIVERGENCE": 2,
    "NEW_INSTITUTION": 3,
    "SHAREHOLDER_COUNT_DECREASE": 1,
    "RSP_STRONG": 1,

    # Distribution signals (negative)
    "HIGH_VOLUME_STAGNATION": -2,
    "OBV_BEARISH_DIVERGENCE": -2,
    "INSTITUTIONAL_SELL_OFF": -3,
    "BREAK_SUPPORT_HEAVY_VOLUME": -3,
    "RSP_WEAK": -1,
}

# Analysis parameters
LOOKBACK_PERIOD = 60
VOL_MULTIPLIER = 2.0
```

### Switching the A-share Data Source

```bash
# AkShare: the default; no token required
python3 main.py 600519.SH

# Tushare: requires TUSHARE_TOKEN
A_STOCK_DATA_SOURCE=tushare python3 main.py 600519.SH
```

## 📚 Methodology

The project is based on a detailed smart-money analysis framework:

- [Full methodology](PREREQUISITES.md) *(Chinese)* — a guide to the complete accumulation and distribution cycle
- [Technical specification](CODING_SPEC.md) *(Chinese)* — detailed implementation requirements

### Core Principles

1. **Two sides of the same cycle:** institutional accumulation and distribution form one complete capital cycle. Useful market insight comes from understanding the progression from position building through markup and, ultimately, exit.

2. **The capital-flow fallacy:** many conventional “main capital flow” indicators measure trade aggressiveness rather than the actual movement of capital.

3. **Signal convergence:** high-confidence conclusions require confirmation across independent dimensions. Any single indicator can be misleading.

4. **Signal sequencing:** institutional activity tends to reveal itself in stages:
   - Market signals such as price-volume behavior and divergences usually appear first
   - Fundamental catalysts emerge later as confirmation
   - Official disclosures provide strong but delayed evidence

5. **Market-specific behavior:** Chinese A-share, US, and Hong Kong markets differ in investor composition, trading rules, and disclosure regimes, so each requires a tailored analytical approach.

## 🛣️ Roadmap

### Phase 1: Foundations ✅

- [x] Architecture design
- [x] Methodology documentation
- [x] Technical specification

### Phase 2: Data Layer ✅

- [x] Unified data manager
- [x] AkShare integration as the default A-share source
- [x] Optional Tushare integration
- [x] yfinance integration for US and Hong Kong stocks
- [x] Intelligent data-source switching

### Phase 3: Analysis Layer ✅

- [x] Price-volume signals
- [x] Technical indicator signals
- [x] Structural signals
- [x] Relative-strength analysis
- [x] Institutional ownership data for US and Hong Kong stocks

### Phase 4: Aggregation and Reporting ✅

- [x] Risk-scoring system
- [x] Report generator
- [ ] Data visualizations

### Phase 5: Optimization and Expansion

- [ ] Data caching
- [ ] Concurrent processing
- [ ] Real-time monitoring
- [x] Web interface
- [x] Unit tests
- [ ] Backtesting

## 🧪 Testing

```bash
# Run the convenience script
./run_tests.sh

# Or run the test entry point directly
python3 tests/run_tests.py

# Run a specific test module
python3 -m unittest tests.test_app
```

See the [testing guide](tests/TESTING.md) *(Chinese)* for more details.

## 🤝 Contributing

Contributions are welcome:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/AmazingFeature`.
3. Commit your changes: `git commit -m 'Add some AmazingFeature'`.
4. Run the test suite: `./run_tests.sh`.
5. Push the branch: `git push origin feature/AmazingFeature`.
6. Open a pull request.

## ⚠️ Disclaimer

**This project is intended for educational and research purposes only. It does not constitute investment advice.**

- Past performance does not guarantee future results.
- Investing involves risk; make decisions carefully.
- You are solely responsible for decisions made using this software.
- Understand the meaning and limitations of each signal before relying on it.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Thanks to the Tushare, AkShare, and other open-data communities.
- The methodology draws on academic research and market practice.
- Thanks to everyone who has contributed to the project.

## 📞 Links

- [Project homepage](https://github.com/RTsien/SmartMoneyTracker)
- [Issue tracker](https://github.com/RTsien/SmartMoneyTracker/issues)
- [Discussions](https://github.com/RTsien/SmartMoneyTracker/discussions)

---

⭐ If you find this project useful, please consider giving it a star.

**The market is always telling a story. Smart-money footprints are hidden in price and volume, technical indicators, order-book activity, and ownership changes.**
