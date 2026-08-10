#!/usr/bin/env python3
"""Capture disclosure records with publication timestamps for safe backtests."""

import argparse
import multiprocessing

import config


def _collect_worker(ticker: str, output) -> None:
    try:
        import config
        from data_fetcher.manager import DataFetcher
        from disclosures import DisclosureSnapshotCollector, DisclosureStore

        store = DisclosureStore(config.DISCLOSURE_DB_PATH, config.DISCLOSURE_TIMEZONE)
        counts = DisclosureSnapshotCollector(DataFetcher(config), store).collect(ticker)
        output.send({"success": True, "counts": counts})
    except Exception as error:
        output.send({"success": False, "error": str(error)})
    finally:
        output.close()


def collect_with_timeout(ticker: str, timeout: float):
    context = multiprocessing.get_context("spawn")
    parent_output, child_output = context.Pipe(duplex=False)
    process = context.Process(target=_collect_worker, args=(ticker, child_output))
    process.start()
    child_output.close()
    process.join(timeout)
    if process.is_alive():
        process.terminate()
        process.join(5)
        parent_output.close()
        return {"success": False, "error": f"timed out after {timeout:g}s"}
    if parent_output.poll(1):
        result = parent_output.recv()
        parent_output.close()
        return result
    parent_output.close()
    return {
        "success": False,
        "error": f"collector exited with code {process.exitcode}",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture point-in-time disclosures")
    parser.add_argument("tickers", nargs="*", help="Ticker symbols; defaults to STOCK_POOL")
    parser.add_argument(
        "--timeout",
        type=float,
        default=config.DISCLOSURE_CAPTURE_TIMEOUT,
        help="Maximum seconds per ticker",
    )
    args = parser.parse_args()
    tickers = args.tickers or config.STOCK_POOL
    failures = 0
    for ticker in tickers:
        result = collect_with_timeout(ticker.upper(), max(1.0, args.timeout))
        if not result["success"]:
            failures += 1
            print(f"{ticker.upper()}: failed - {result['error']}")
            continue
        counts = result["counts"]
        print(
            f"{ticker.upper()}: holdings={counts['institutional_holdings']}, "
            f"shareholder_count={counts['shareholder_count']}"
        )
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
