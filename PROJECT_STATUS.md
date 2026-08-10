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
- Automated unit and integration tests

## Backtesting boundary

The backtesting MVP includes only price-volume and technical-indicator signals.
It deliberately excludes institutional holdings, shareholder disclosures, news,
and other structural inputs until point-in-time snapshots and publication dates
are available. This prevents current knowledge from leaking into historical
decisions.

## Active roadmap

- [ ] Add equity, drawdown, benchmark, and signal charts for backtest results
- [ ] Add persistent TTL caching across application processes
- [ ] Add bounded concurrent batch processing with provider-aware rate limits
- [ ] Add scheduled end-of-day scans and configurable alerts
- [ ] Add walk-forward/out-of-sample validation and parameter-sensitivity reports
- [ ] Add point-in-time disclosure storage before backtesting structural signals

## Deferred or out of scope

- Commercial Level 2 microstructure analysis remains an extension point until a
  licensed data feed is configured.
- Tick-level real-time monitoring is not a near-term goal for the current free
  end-of-day data stack; scheduled scans are the practical replacement.
- Generic machine-learning and community-sharing features have no acceptance
  criteria and are not part of the active roadmap.
