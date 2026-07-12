"""Service utama untuk memproses file secara otomatis."""

from __future__ import annotations

import json
import hashlib
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

import config
from models.file_item import FileItem


@dataclass
class ProcessResult:
    total: int = 0
    processed: int = 0
    duplicates: int = 0
    errors: int = 0
    logs: list[str] = field(default_factory=list)
    actions: list[dict] = field(default_factory=list)
    manifest_path: str = ""


class FileOrganizer:
    def __init__(self, rules, dry_run: bool = True, output_root_name: str = "BeresFile"):
        self.rules = list(rules)
        self.dry_run = dry_run
        self.output_root_name = output_root_name
        self.result = ProcessResult()

    def process_directory(self, scan_dir):
        scan_path = Path(scan_dir)
        if not scan_path.exists():
            raise FileNotFoundError(f"Folder tidak ditemukan: {scan_path}")

        self.result = ProcessResult()
        files = [item for item in scan_path.iterdir() if item.is_file()]
        self.result.total = len(files)
        seen_signatures: dict[str, Path] = {}

        output_root = scan_path / self.output_root_name
        output_root.mkdir(exist_ok=True)

        for file_path in files:
            try:
                file_item = FileItem(file_path)

                signature = self._file_signature(file_item.path)
                if signature in seen_signatures:
                    self.result.duplicates += 1
                    original = seen_signatures[signature]
                    self.result.logs.append(
                        f"[DUPLICATE] {file_item.path.name} sama dengan {original.name}, dilewati"
                    )
                    continue

                seen_signatures[signature] = file_item.path

                rule = self._select_rule(file_item)
                category = rule.determine_category(file_item)
                new_name = rule.generate_new_name(file_item, category)

                target_dir = output_root / category
                target_dir.mkdir(parents=True, exist_ok=True)

                target_path = self._get_unique_target(target_dir / f"{new_name}{file_item.ext}")
                preview = f"{file_item.path.name} -> {target_path.relative_to(scan_path)}"
                action = {
                    "source": str(file_item.path),
                    "target": str(target_path),
                    "category": category,
                    "original_name": file_item.path.name,
                    "new_name": target_path.name,
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                }

                if self.dry_run:
                    self.result.logs.append(f"[DRY-RUN] {preview}")
                else:
                    shutil.move(str(file_item.path), str(target_path))
                    self.result.logs.append(f"[OK] {preview}")

                self.result.actions.append(action)

                self.result.processed += 1
            except Exception as exc:
                self.result.errors += 1
                self.result.logs.append(f"[ERROR] {file_path.name}: {exc}")

        self._save_manifest(scan_path)
        return self.result

    def _select_rule(self, file_item: FileItem):
        if not self.rules:
            raise ValueError("Tidak ada rule yang tersedia.")

        for rule in self.rules:
            try:
                category = rule.determine_category(file_item)
                if category:
                    return rule
            except Exception:
                continue

        return self.rules[0]

    def _get_unique_target(self, target_path: Path) -> Path:
        if not target_path.exists():
            return target_path

        base = target_path.stem
        suffix = target_path.suffix
        parent = target_path.parent
        index = 1
        while True:
            candidate = parent / f"{base}_{index}{suffix}"
            if not candidate.exists():
                return candidate
            index += 1

    def _file_signature(self, file_path: Path) -> str:
        hasher = hashlib.sha256()
        with file_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _save_manifest(self, scan_path: Path):
        manifest_dir = scan_path / config.LOG_DIR_NAME
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = manifest_dir / "beresfile_manifest.json"
        payload = {
            "dry_run": self.dry_run,
            "output_root_name": self.output_root_name,
            "total": self.result.total,
            "processed": self.result.processed,
            "duplicates": self.result.duplicates,
            "errors": self.result.errors,
            "actions": self.result.actions,
            "logs": self.result.logs,
        }
        manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        self.result.manifest_path = str(manifest_path)

    def undo_last_run(self, scan_dir):
        scan_path = Path(scan_dir)
        manifest_path = scan_path / config.LOG_DIR_NAME / "beresfile_manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError("Manifest undo tidak ditemukan. Jalankan proses nyata terlebih dahulu.")

        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        actions = list(reversed(payload.get("actions", [])))
        undo_logs = []

        for action in actions:
            source = Path(action["source"])
            target = Path(action["target"])
            if target.exists():
                source.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(target), str(source))
                undo_logs.append(f"[UNDO] {target.name} -> {source.name}")
            else:
                undo_logs.append(f"[SKIP] File tidak ditemukan: {target.name}")

        payload["undone_at"] = datetime.now().isoformat(timespec="seconds")
        manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return undo_logs, manifest_path
