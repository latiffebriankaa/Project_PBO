"""Utilitas logging sederhana."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any

import config


def save_log(logs: list[str], base_dir: str | Path, filename: str = "beresfile_log.txt") -> Path:
    base_path = Path(base_dir)
    log_dir = base_path / config.LOG_DIR_NAME
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / filename
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = [f"# BeresFile Log", f"# Generated: {timestamp}", ""] + logs
    log_path.write_text("\n".join(content), encoding="utf-8")
    return log_path


def save_json_log(payload: dict[str, Any], base_dir: str | Path, filename: str = "beresfile_manifest.json") -> Path:
    base_path = Path(base_dir)
    log_dir = base_path / config.LOG_DIR_NAME
    log_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = log_dir / filename
    manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest_path
