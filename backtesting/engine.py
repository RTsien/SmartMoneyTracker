"""Point-in-time backtesting for SmartMoneyTracker signals.

Signals are evaluated from the current and preceding bars only. Orders are sent
to AkQuant and filled at the next bar's open, which keeps signal generation and
execution separated and avoids look-ahead bias.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, Optional

import numpy as np
import pandas as pd

from aggregator.scorer import SignalAggregator
from analysis.indicator_signals import IndicatorSignals
from analysis.price_volume_signals import PriceVolumeSignals

SignalEvaluator = Callable[[pd.DataFrame], Dict[str, Any]]


@dataclass(frozen=True)
class SignalBacktestConfig:
    """Execution and sampling settings for a single-symbol backtest."""

    initial_cash: float = 1_000_000.0
    warmup_period: int = 120
    rebalance_every: int = 1
    target_exposure: float = 0.95
    commission_bps: float = 10.0
    slippage_bps: float = 5.0
    risk_free_rate: float = 0.0

    def __post_init__(self) -> None:
        if self.initial_cash <= 0:
            raise ValueError("initial_cash must be positive")
        if self.warmup_period < 60:
            raise ValueError("warmup_period must be at least 60 bars")
        if self.rebalance_every < 1:
            raise ValueError("rebalance_every must be at least 1")
        if not 0 < self.target_exposure <= 1:
            raise ValueError("target_exposure must be in (0, 1]")
        if self.commission_bps < 0 or self.slippage_bps < 0:
            raise ValueError("transaction costs cannot be negative")


@dataclass
class BacktestRun:
    """A compact, serializable view over an AkQuant backtest result."""

    ticker: str
    config: SignalBacktestConfig
    summary: Dict[str, Any]
    signals: pd.DataFrame
    equity_curve: pd.Series
    orders: pd.DataFrame
    trades: pd.DataFrame
    raw_result: Any

    def to_dict(self, include_series: bool = False) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "ticker": self.ticker,
            "config": asdict(self.config),
            "summary": self.summary,
            "signals": self.signals.to_dict(orient="records"),
        }
        if include_series:
            result["equity_curve"] = [
                {"date": index.isoformat(), "equity": float(value)}
                for index, value in self.equity_curve.items()
            ]
            result["orders"] = self._records(self.orders)
            result["trades"] = self._records(self.trades)
        return result

    @staticmethod
    def _records(frame: pd.DataFrame) -> list[Dict[str, Any]]:
        if frame.empty:
            return []
        clean = frame.copy()
        for column in clean.columns:
            if pd.api.types.is_datetime64_any_dtype(clean[column]):
                clean[column] = clean[column].map(
                    lambda value: value.isoformat() if pd.notna(value) else None
                )
        return clean.replace({np.nan: None}).to_dict(orient="records")


class SignalBacktester:
    """Run price-volume and indicator signals through AkQuant."""

    REQUIRED_COLUMNS = ("date", "open", "high", "low", "close", "volume")

    def __init__(
        self,
        app_config: Any,
        data_fetcher: Any,
        evaluator: Optional[SignalEvaluator] = None,
    ) -> None:
        self.app_config = app_config
        self.data_fetcher = data_fetcher
        self.price_volume = PriceVolumeSignals(app_config)
        self.indicators = IndicatorSignals(app_config)
        self.aggregator = SignalAggregator(app_config)
        self.evaluator = evaluator or self._evaluate_signals

    def run(
        self,
        ticker: str,
        data: Optional[pd.DataFrame] = None,
        period: int = 1_000,
        settings: Optional[SignalBacktestConfig] = None,
    ) -> BacktestRun:
        """Run a long/cash strategy for one ticker.

        BUY and STRONG_BUY ratings target the configured long exposure. SELL and
        STRONG_SELL ratings move to cash. NEUTRAL keeps the existing target.
        Structural/disclosure signals are intentionally excluded because the
        current data layer does not yet provide point-in-time snapshots.
        """
        from akquant import __version__ as akquant_version
        from akquant.backtest import NextOpen, run_backtest

        settings = settings or SignalBacktestConfig()
        source = data if data is not None else self.data_fetcher.get_daily_data(
            ticker, period=period
        )
        frame = self._prepare_data(source, settings.warmup_period)
        signal_log: list[Dict[str, Any]] = []
        decision_count = 0
        target = 0.0

        def on_bar(context: Any, bar: Any) -> None:
            nonlocal decision_count, target
            decision_count += 1
            if (decision_count - 1) % settings.rebalance_every != 0:
                return

            history = self._history_frame(context, bar, settings.warmup_period)
            evaluation = self.evaluator(history)
            rating = str(evaluation.get("rating", "NEUTRAL"))
            score = float(evaluation.get("score", 0.0))
            desired_target = target
            if rating in {"BUY", "STRONG_BUY"}:
                desired_target = settings.target_exposure
            elif rating in {"SELL", "STRONG_SELL"}:
                desired_target = 0.0

            timestamp = pd.to_datetime(bar.timestamp, unit="ns", utc=True)
            signal_log.append({
                "date": timestamp.isoformat(),
                "score": score,
                "rating": rating,
                "target_exposure": desired_target,
                "signals": sorted(evaluation.get("triggered_signals", {}).keys()),
            })

            if desired_target != target:
                context.order_target_percent(
                    symbol=bar.symbol,
                    target_percent=desired_target,
                )
                target = desired_target

        result = run_backtest(
            data=frame,
            strategy=on_bar,
            symbols=ticker,
            initial_cash=settings.initial_cash,
            commission_rate=settings.commission_bps / 10_000.0,
            slippage={"type": "percent", "value": settings.slippage_bps / 10_000.0},
            history_depth=settings.warmup_period,
            warmup_period=settings.warmup_period,
            lot_size=100 if ticker.endswith((".SH", ".SZ")) else 1,
            t_plus_one=ticker.endswith((".SH", ".SZ")),
            fill_policy=NextOpen(),
            show_progress=False,
        )

        signals = pd.DataFrame(signal_log)
        equity = result.equity_curve
        orders = result.orders_df
        trades = result.trades_df
        summary = self._summarize(
            frame=frame,
            equity=equity,
            trades=trades,
            orders=orders,
            signals=signals,
            settings=settings,
            akquant_version=akquant_version,
        )
        return BacktestRun(
            ticker=ticker,
            config=settings,
            summary=summary,
            signals=signals,
            equity_curve=equity,
            orders=orders,
            trades=trades,
            raw_result=result,
        )

    def _evaluate_signals(self, history: pd.DataFrame) -> Dict[str, Any]:
        enriched = self.data_fetcher.calculate_technical_indicators(history)
        signals = self.price_volume.analyze(enriched)
        signals.update(self.indicators.analyze(enriched))
        return self.aggregator.calculate_score(signals)

    @classmethod
    def _prepare_data(cls, data: pd.DataFrame, warmup_period: int) -> pd.DataFrame:
        if data is None or data.empty:
            raise ValueError("No historical price data is available for this ticker")
        missing = [column for column in cls.REQUIRED_COLUMNS if column not in data.columns]
        if missing:
            raise ValueError(f"Historical data is missing columns: {', '.join(missing)}")

        frame = data.loc[:, cls.REQUIRED_COLUMNS].copy()
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
        for column in cls.REQUIRED_COLUMNS[1:]:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frame = (
            frame.dropna(subset=cls.REQUIRED_COLUMNS)
            .sort_values("date")
            .drop_duplicates("date", keep="last")
            .reset_index(drop=True)
        )
        if len(frame) <= warmup_period + 1:
            raise ValueError(
                f"At least {warmup_period + 2} valid bars are required; got {len(frame)}"
            )
        if (frame[["open", "high", "low", "close"]] <= 0).any().any():
            raise ValueError("OHLC prices must be positive")
        if (frame["volume"] < 0).any():
            raise ValueError("Volume cannot be negative")
        return frame

    @staticmethod
    def _history_frame(context: Any, bar: Any, count: int) -> pd.DataFrame:
        history = {
            field: context.get_history(count, symbol=bar.symbol, field=field)
            for field in ("open", "high", "low", "close", "volume")
        }
        frame = pd.DataFrame(history).dropna().reset_index(drop=True)
        end = pd.to_datetime(bar.timestamp, unit="ns", utc=True)
        frame["date"] = pd.date_range(end=end, periods=len(frame), freq="D")
        frame["amount"] = frame["close"] * frame["volume"]
        return frame

    @staticmethod
    def _summarize(
        frame: pd.DataFrame,
        equity: pd.Series,
        trades: pd.DataFrame,
        orders: pd.DataFrame,
        signals: pd.DataFrame,
        settings: SignalBacktestConfig,
        akquant_version: str,
    ) -> Dict[str, Any]:
        active_equity = equity.iloc[max(settings.warmup_period - 1, 0):].dropna()
        if active_equity.empty:
            active_equity = equity.dropna()
        returns = active_equity.pct_change().dropna()
        total_return = (
            float(active_equity.iloc[-1] / settings.initial_cash - 1.0)
            if not active_equity.empty else 0.0
        )
        periods = max(len(returns), 1)
        annualized_return = (1.0 + total_return) ** (252.0 / periods) - 1.0
        volatility = float(returns.std(ddof=1) * np.sqrt(252)) if len(returns) > 1 else 0.0
        daily_risk_free = settings.risk_free_rate / 252.0
        return_std = float(returns.std(ddof=1)) if len(returns) > 1 else 0.0
        sharpe = (
            float((returns.mean() - daily_risk_free) / return_std * np.sqrt(252))
            if return_std > 0 else 0.0
        )
        running_max = active_equity.cummax()
        drawdowns = active_equity / running_max - 1.0
        max_drawdown = float(drawdowns.min()) if not drawdowns.empty else 0.0

        benchmark_entry = min(settings.warmup_period, len(frame) - 1)
        benchmark_return = float(
            frame["close"].iloc[-1] / frame["open"].iloc[benchmark_entry] - 1.0
        )
        winning_trades = 0
        if not trades.empty:
            pnl_column = "net_pnl" if "net_pnl" in trades else "pnl"
            winning_trades = int((trades[pnl_column] > 0).sum())
        trade_count = int(len(trades))

        return {
            "engine": "akquant",
            "engine_version": str(akquant_version),
            "fill_policy": "next_open",
            "lookahead_safe": True,
            "start_date": frame["date"].iloc[benchmark_entry].date().isoformat(),
            "end_date": frame["date"].iloc[-1].date().isoformat(),
            "bars": int(len(frame) - benchmark_entry),
            "total_return": total_return,
            "benchmark_return": benchmark_return,
            "excess_return": total_return - benchmark_return,
            "annualized_return": float(annualized_return),
            "annualized_volatility": volatility,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_drawdown,
            "win_rate": winning_trades / trade_count if trade_count else 0.0,
            "trade_count": trade_count,
            "order_count": int(len(orders)),
            "signal_observations": int(len(signals)),
            "ending_equity": float(active_equity.iloc[-1]),
        }
