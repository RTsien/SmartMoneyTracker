#!/usr/bin/env python3
"""Command-line entry point for SmartMoneyTracker signal backtests."""

import argparse
import json

import config
from backtesting import SignalBacktestConfig, SignalBacktester
from data_fetcher.manager import DataFetcher


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backtest SmartMoneyTracker signals with AkQuant"
    )
    parser.add_argument("ticker", help="Ticker such as 600519.SH, 0700.HK, or AAPL")
    parser.add_argument("--period", type=int, default=1000, help="Calendar lookback hint")
    parser.add_argument("--warmup", type=int, default=120, help="Signal warmup bars")
    parser.add_argument("--rebalance", type=int, default=1, help="Evaluate every N bars")
    parser.add_argument("--cash", type=float, default=1000000.0, help="Initial cash")
    parser.add_argument("--commission-bps", type=float, default=10.0)
    parser.add_argument("--slippage-bps", type=float, default=5.0)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = SignalBacktestConfig(
        initial_cash=args.cash,
        warmup_period=args.warmup,
        rebalance_every=args.rebalance,
        commission_bps=args.commission_bps,
        slippage_bps=args.slippage_bps,
    )
    run = SignalBacktester(config, DataFetcher(config)).run(
        ticker=args.ticker,
        period=args.period,
        settings=settings,
    )
    if args.json:
        print(json.dumps(run.to_dict(), ensure_ascii=False, indent=2))
        return

    summary = run.summary
    print(f"{run.ticker} backtest ({summary['start_date']} to {summary['end_date']})")
    print(f"Engine: AkQuant {summary['engine_version']} / next-open fills")
    print(f"Return: {summary['total_return']:.2%}")
    print(f"Buy & hold: {summary['benchmark_return']:.2%}")
    print(f"Excess return: {summary['excess_return']:.2%}")
    print(f"Sharpe ratio: {summary['sharpe_ratio']:.2f}")
    print(f"Max drawdown: {summary['max_drawdown']:.2%}")
    print(f"Win rate: {summary['win_rate']:.2%}")
    print(f"Closed trades: {summary['trade_count']}")


if __name__ == "__main__":
    main()
