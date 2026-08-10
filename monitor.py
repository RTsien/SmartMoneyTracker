#!/usr/bin/env python3
"""Run SmartMoneyTracker end-of-day scans and alerts."""

import argparse

import config
from main import SmartMoneyScanner
from monitoring import EndOfDayMonitor


def main() -> None:
    parser = argparse.ArgumentParser(description="Scheduled end-of-day signal monitor")
    parser.add_argument("--once", action="store_true", help="Run immediately and exit")
    parser.add_argument(
        "--market",
        action="append",
        choices=("A_STOCK", "HK_STOCK", "US_STOCK"),
        help="Limit an immediate run to one or more markets",
    )
    args = parser.parse_args()
    monitor = EndOfDayMonitor(SmartMoneyScanner(), config)
    if args.once:
        monitor.run_once(args.market)
    else:
        monitor.serve_forever()


if __name__ == "__main__":
    main()
