#!/usr/bin/env python3
"""Command-line entry point for SmartMoneyTracker signal backtests."""

import argparse
import json

import config
from backtesting import (
    SignalBacktestConfig,
    SignalBacktester,
    WalkForwardConfig,
    WalkForwardValidator,
)
from data_fetcher.manager import DataFetcher
from disclosures import DisclosureStore


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
    parser.add_argument("--walk-forward", action="store_true",
                        help="Run rolling out-of-sample validation")
    parser.add_argument("--train-bars", type=int, default=504)
    parser.add_argument("--test-bars", type=int, default=126)
    parser.add_argument("--step-bars", type=int, default=126)
    parser.add_argument("--candidates", default="1,5,20",
                        help="Comma-separated rebalance frequencies")
    parser.add_argument(
        "--include-structural",
        action="store_true",
        help="Use only point-in-time disclosures already captured in SQLite",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = SignalBacktestConfig(
        initial_cash=args.cash,
        warmup_period=args.warmup,
        rebalance_every=args.rebalance,
        commission_bps=args.commission_bps,
        slippage_bps=args.slippage_bps,
        include_structural=args.include_structural,
    )
    disclosure_store = (
        DisclosureStore(config.DISCLOSURE_DB_PATH, config.DISCLOSURE_TIMEZONE)
        if args.include_structural else None
    )
    backtester = SignalBacktester(
        config,
        DataFetcher(config),
        disclosure_store=disclosure_store,
    )
    if args.walk_forward:
        candidates = tuple(int(value) for value in args.candidates.split(',') if value)
        validation = WalkForwardConfig(
            train_bars=args.train_bars,
            test_bars=args.test_bars,
            step_bars=args.step_bars,
            rebalance_candidates=candidates,
        )
        run = WalkForwardValidator(backtester).run(
            ticker=args.ticker,
            period=args.period,
            settings=settings,
            validation=validation,
        )
        if args.json:
            print(json.dumps(run.to_dict(), ensure_ascii=False, indent=2))
            return
        print_walk_forward(run)
        return

    run = backtester.run(ticker=args.ticker, period=args.period, settings=settings)
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


def print_walk_forward(run) -> None:
    summary = run.summary
    print(f"{run.ticker} walk-forward validation "
          f"({summary['start_date']} to {summary['end_date']})")
    print(f"Out-of-sample folds: {summary['fold_count']}")
    print(f"Compounded return: {summary['total_return']:.2%}")
    print(f"Buy & hold: {summary['benchmark_return']:.2%}")
    print(f"Excess return: {summary['excess_return']:.2%}")
    print(f"Sharpe ratio: {summary['sharpe_ratio']:.2f}")
    print(f"Max drawdown: {summary['max_drawdown']:.2%}")
    print("\nOut-of-sample sensitivity:")
    print(run.sensitivity.to_string(index=False, formatters={
        'mean_total_return': '{:.2%}'.format,
        'mean_excess_return': '{:.2%}'.format,
        'mean_sharpe_ratio': '{:.2f}'.format,
        'worst_drawdown': '{:.2%}'.format,
    }))


if __name__ == "__main__":
    main()
