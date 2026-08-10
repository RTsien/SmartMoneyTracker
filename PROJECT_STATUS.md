# SmartMoneyTracker Project Status

Last updated: 2026-08-10

This file is a concise implementation snapshot. The bilingual README files are
the source of truth for setup, usage, and the public roadmap.

## Current capabilities

- Chinese A-share, US, and Hong Kong daily data with provider fallbacks
- AkQuant-backed SMA, OBV, RSI, MACD, and MFI calculations
- Bidirectional price-volume, indicator, structural, and relative-strength signals
- Weighted scoring from `STRONG_SELL` to `STRONG_BUY`
- English/Chinese web interface, defaulting to English
- Single-stock and batch analysis with in-memory daily-data caching
- Point-in-time signal backtesting on AkQuant with next-open execution
- Interactive equity, benchmark, drawdown, and signal-score charts
- Rolling out-of-sample validation and parameter-sensitivity reports
- Cross-process compressed TTL caching
- Bounded, provider-aware concurrent batch scanning
- Market-aware end-of-day scheduling and duplicate-safe alert delivery
- SQLite disclosure snapshots filtered by publication time in structural backtests
- Automated unit and integration tests

## Backtesting boundary

Price-volume and technical-indicator signals are always available to the
backtester. Structural signals are opt-in and can only read records already
captured in the publication-time SQLite store. Records without a trustworthy
publication date become visible from their actual collection time, never from a
guessed historical date.

## Completed roadmap

- [x] Add equity, drawdown, benchmark, and signal charts for backtest results
- [x] Add persistent TTL caching across application processes
- [x] Add bounded concurrent batch processing with provider-aware rate limits
- [x] Add scheduled end-of-day scans and configurable alerts
- [x] Add walk-forward/out-of-sample validation and parameter-sensitivity reports
- [x] Add point-in-time disclosure storage before backtesting structural signals

## Deferred or out of scope

- Commercial Level 2 microstructure analysis remains an extension point until a
  licensed data feed is configured.
- Tick-level real-time monitoring is not a near-term goal for the current free
  end-of-day data stack; scheduled scans are the practical replacement.
- Generic machine-learning and community-sharing features have no acceptance
  criteria and are not part of the active roadmap.
