"""Small, dependency-free persistent cache for market DataFrames."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import tempfile
import time
from io import StringIO
from pathlib import Path
from typing import Optional, Sequence

import pandas as pd


class DataFrameTTLCache:
    """Store pandas frames as compressed JSON with atomic replacement."""

    SCHEMA_VERSION = 1

    def __init__(self, directory: str) -> None:
        self.directory = Path(directory).expanduser().resolve()

    def get(
        self,
        namespace: str,
        key: Sequence[str],
        ttl_seconds: float,
    ) -> Optional[pd.DataFrame]:
        path = self._path(namespace, key)
        if not path.exists():
            return None
        try:
            with gzip.open(path, "rt", encoding="utf-8") as handle:
                envelope = json.load(handle)
            created_at = float(envelope["created_at"])
            if ttl_seconds >= 0 and time.time() - created_at > ttl_seconds:
                path.unlink(missing_ok=True)
                return None
            if envelope.get("schema_version") != self.SCHEMA_VERSION:
                path.unlink(missing_ok=True)
                return None
            frame = pd.read_json(
                StringIO(envelope["frame"]),
                orient="table",
            )
            for column, dtype in envelope.get("dtypes", {}).items():
                if column in frame.columns:
                    frame[column] = frame[column].astype(dtype)
            return frame
        except (OSError, ValueError, KeyError, TypeError):
            path.unlink(missing_ok=True)
            return None

    def set(self, namespace: str, key: Sequence[str], frame: pd.DataFrame) -> None:
        target = self._path(namespace, key)
        target.parent.mkdir(parents=True, exist_ok=True)
        envelope = {
            "schema_version": self.SCHEMA_VERSION,
            "created_at": time.time(),
            "dtypes": {column: str(dtype) for column, dtype in frame.dtypes.items()},
            "frame": frame.to_json(orient="table", date_format="iso"),
        }
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{target.stem}-",
            suffix=".tmp",
            dir=target.parent,
        )
        try:
            with os.fdopen(descriptor, "wb") as raw:
                with gzip.GzipFile(fileobj=raw, mode="wb") as compressed:
                    compressed.write(json.dumps(envelope).encode("utf-8"))
            os.replace(temporary_name, target)
        finally:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)

    def clear_expired(self, ttl_seconds: float) -> int:
        if not self.directory.exists():
            return 0
        removed = 0
        now = time.time()
        for path in self.directory.glob("*/*.json.gz"):
            try:
                if now - path.stat().st_mtime > ttl_seconds:
                    path.unlink()
                    removed += 1
            except OSError:
                continue
        return removed

    def _path(self, namespace: str, key: Sequence[str]) -> Path:
        safe_namespace = "".join(
            character for character in namespace if character.isalnum() or character in "-_"
        ) or "default"
        digest_input = json.dumps(
            [self.SCHEMA_VERSION, *[str(value) for value in key]],
            ensure_ascii=True,
            separators=(",", ":"),
        )
        digest = hashlib.sha256(digest_input.encode("utf-8")).hexdigest()
        return self.directory / safe_namespace / f"{digest}.json.gz"
