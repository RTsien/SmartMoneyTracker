"""Rolling out-of-sample validation for signal backtests."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any, Dict, Optional, Sequence

import numpy as np
import pandas as pd

from .engine import SignalBacktestConfig, SignalBacktester


@dataclass(frozen=True)
class WalkForwardConfig:
    """Chronological fold and parameter-selection settings."""

    train_bars: int = 504
    test_bars: int = 126
    step_bars: int = 126
    rebalance_candidates: tuple[int, ...] = (1, 5, 20)
    min_folds: int = 2

    def __post_init__(self) -> None:
        if self.train_bars < 60:
            raise ValueError("train_bars must be at least 60")
        if self.test_bars < 20:
            raise ValueError("test_bars must be at least 20")
        if self.step_bars < self.test_bars:
            raise ValueError("step_bars must be at least test_bars to avoid overlap")
        candidates = tuple(dict.fromkeys(self.rebalance_candidates))
        if not candidates or any(value < 1 or value > 20 for value in candidates):
            raise ValueError("rebalance candidates must be between 1 and 20")
        if self.min_folds < 1:
            raise ValueError("min_folds must be positive")
        object.__setattr__(self, "rebalance_candidates", candidates)


@dataclass
class WalkForwardRun:
    """Serializable walk-forward results and parameter sensitivity."""

    ticker: str
    config: WalkForwardConfig
    summary: Dict[str, Any]
    folds: pd.DataFrame
    sensitivity: pd.DataFrame

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ticker": self.ticker,
            "config": asdict(self.config),
            "summary": self.summary,
            "folds": self.folds.to_dict(orient="records"),
            "sensitivity": self.sensitivity.to_dict(orient="records"),
        }


class WalkForwardValidator:
    """Select parameters on past data and score them on unseen future folds."""

    def __init__(self, backtester: SignalBacktester) -> None:
        self.backtester = backtester

    def run(
        self,
        ticker: str,
        data: Optional[pd.DataFrame] = None,
        period: int = 2_000,
        settings: Optional[SignalBacktestConfig] = None,
        validation: Optional[WalkForwardConfig] = None,
    ) -> WalkForwardRun:
        settings = settings or SignalBacktestConfig()
        validation = validation or WalkForwardConfig()
        source = data if data is not None else self.backtester.data_fetcher.get_daily_data(
            ticker, period=period
        )
        frame = self.backtester._prepare_data(source, settings.warmup_period)
        folds = self._fold_boundaries(len(frame), settings.warmup_period, validation)
        if len(folds) < validation.min_folds:
            required = (
                settings.warmup_period + validation.train_bars
                + validation.test_bars
                + (validation.min_folds - 1) * validation.step_bars
            )
            raise ValueError(
                f"Walk-forward validation requires at least {required} valid bars "
                f"for {validation.min_folds} folds; got {len(frame)}"
            )

        fold_rows: list[Dict[str, Any]] = []
        sensitivity_rows: list[Dict[str, Any]] = []
        selected_returns: list[pd.Series] = []
        selected_trade_pnls: list[float] = []

        for fold_number, (test_start, test_end) in enumerate(folds, start=1):
            train_start = test_start - validation.train_bars - settings.warmup_period
            train_data = frame.iloc[train_start:test_start].reset_index(drop=True)
            test_data = frame.iloc[
                test_start - settings.warmup_period:test_end
            ].reset_index(drop=True)

            training_scores: Dict[int, tuple[float, float]] = {}
            for candidate in validation.rebalance_candidates:
                candidate_settings = replace(settings, rebalance_every=candidate)
                training_run = self.backtester.run(
                    ticker, data=train_data, settings=candidate_settings
                )
                training_scores[candidate] = (
                    float(training_run.summary["excess_return"]),
                    float(training_run.summary["sharpe_ratio"]),
                )

            selected = max(
                validation.rebalance_candidates,
                key=lambda candidate: training_scores[candidate],
            )

            test_runs = {}
            for candidate in validation.rebalance_candidates:
                candidate_settings = replace(settings, rebalance_every=candidate)
                test_run = self.backtester.run(
                    ticker, data=test_data, settings=candidate_settings
                )
                test_runs[candidate] = test_run
                sensitivity_rows.append({
                    "fold": fold_number,
                    "rebalance_every": candidate,
                    "selected": candidate == selected,
                    "total_return": float(test_run.summary["total_return"]),
                    "benchmark_return": float(test_run.summary["benchmark_return"]),
                    "excess_return": float(test_run.summary["excess_return"]),
                    "sharpe_ratio": float(test_run.summary["sharpe_ratio"]),
                    "max_drawdown": float(test_run.summary["max_drawdown"]),
                })

            selected_run = test_runs[selected]
            fold_rows.append({
                "fold": fold_number,
                "train_start": train_data["date"].iloc[settings.warmup_period].date().isoformat(),
                "train_end": train_data["date"].iloc[-1].date().isoformat(),
                "test_start": frame["date"].iloc[test_start].date().isoformat(),
                "test_end": frame["date"].iloc[test_end - 1].date().isoformat(),
                "selected_rebalance_every": selected,
                "training_excess_return": training_scores[selected][0],
                "total_return": float(selected_run.summary["total_return"]),
                "benchmark_return": float(selected_run.summary["benchmark_return"]),
                "excess_return": float(selected_run.summary["excess_return"]),
                "sharpe_ratio": float(selected_run.summary["sharpe_ratio"]),
                "max_drawdown": float(selected_run.summary["max_drawdown"]),
                "trade_count": int(selected_run.summary["trade_count"]),
            })
            active_equity = selected_run.equity_curve.iloc[
                max(settings.warmup_period - 1, 0):
            ]
            selected_returns.append(active_equity.pct_change().dropna())
            if not selected_run.trades.empty:
                pnl_column = "net_pnl" if "net_pnl" in selected_run.trades else "pnl"
                selected_trade_pnls.extend(
                    selected_run.trades[pnl_column].astype(float).tolist()
                )

        folds_frame = pd.DataFrame(fold_rows)
        sensitivity_frame = self._aggregate_sensitivity(
            pd.DataFrame(sensitivity_rows), validation.rebalance_candidates
        )
        summary = self._summarize(
            folds_frame,
            selected_returns,
            selected_trade_pnls,
        )
        summary.update({
            "lookahead_safe": True,
            "selection_rule": "highest training excess return, then Sharpe ratio",
            "start_date": folds_frame["test_start"].iloc[0],
            "end_date": folds_frame["test_end"].iloc[-1],
        })
        return WalkForwardRun(
            ticker=ticker,
            config=validation,
            summary=summary,
            folds=folds_frame,
            sensitivity=sensitivity_frame,
        )

    @staticmethod
    def _fold_boundaries(
        size: int,
        warmup: int,
        config: WalkForwardConfig,
    ) -> list[tuple[int, int]]:
        first_test = warmup + config.train_bars
        return [
            (start, start + config.test_bars)
            for start in range(first_test, size - config.test_bars + 1, config.step_bars)
        ]

    @staticmethod
    def _aggregate_sensitivity(
        rows: pd.DataFrame,
        candidates: Sequence[int],
    ) -> pd.DataFrame:
        records = []
        for candidate in candidates:
            group = rows[rows["rebalance_every"] == candidate]
            records.append({
                "rebalance_every": int(candidate),
                "folds": int(len(group)),
                "selected_folds": int(group["selected"].sum()),
                "mean_total_return": float(group["total_return"].mean()),
                "mean_excess_return": float(group["excess_return"].mean()),
                "mean_sharpe_ratio": float(group["sharpe_ratio"].mean()),
                "worst_drawdown": float(group["max_drawdown"].min()),
                "positive_excess_folds": int((group["excess_return"] > 0).sum()),
            })
        return pd.DataFrame(records).sort_values(
            ["mean_excess_return", "mean_sharpe_ratio"], ascending=False
        ).reset_index(drop=True)

    @staticmethod
    def _summarize(
        folds: pd.DataFrame,
        return_parts: list[pd.Series],
        trade_pnls: list[float],
    ) -> Dict[str, Any]:
        returns = pd.concat(return_parts, ignore_index=True) if return_parts else pd.Series(dtype=float)
        equity = (1.0 + returns).cumprod()
        total_return = float(equity.iloc[-1] - 1.0) if not equity.empty else 0.0
        benchmark_return = float(np.prod(1.0 + folds["benchmark_return"]) - 1.0)
        std = float(returns.std(ddof=1)) if len(returns) > 1 else 0.0
        sharpe = float(returns.mean() / std * np.sqrt(252)) if std > 0 else 0.0
        drawdown = equity / equity.cummax() - 1.0
        trade_count = len(trade_pnls)
        return {
            "fold_count": int(len(folds)),
            "out_of_sample_bars": int(sum(len(part) for part in return_parts)),
            "total_return": total_return,
            "benchmark_return": benchmark_return,
            "excess_return": total_return - benchmark_return,
            "sharpe_ratio": sharpe,
            "max_drawdown": float(drawdown.min()) if not drawdown.empty else 0.0,
            "win_rate": (
                sum(value > 0 for value in trade_pnls) / trade_count
                if trade_count else 0.0
            ),
            "trade_count": trade_count,
        }
