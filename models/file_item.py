"""Entity untuk merepresentasikan file yang akan diproses."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re


_ILLEGAL_CHARS = r'<>:"/\\|?*'


class FileItem:
    """Menyimpan informasi file dengan encapsulation."""

    def __init__(self, path: str | Path):
        self._path = Path(path)
        self._name = self._path.stem
        self._ext = self._path.suffix.lower()
        self._size = self._path.stat().st_size if self._path.exists() else 0
        self._mod_time = datetime.fromtimestamp(self._path.stat().st_mtime) if self._path.exists() else datetime.now()

    @property
    def path(self) -> Path:
        return self._path

    @property
    def name(self) -> str:
        return self._name

    @property
    def ext(self) -> str:
        return self._ext

    @property
    def size(self) -> int:
        return self._size

    @property
    def mod_time(self) -> datetime:
        return self._mod_time

    @property
    def parent_dir(self) -> Path:
        return self._path.parent

    def is_file(self) -> bool:
        return self._path.is_file()

    def sanitize_name(self, value: str) -> str:
        value = re.sub(f"[{re.escape(_ILLEGAL_CHARS)}]", "_", value)
        value = re.sub(r"\s+", "_", value.strip())
        value = re.sub(r"_+", "_", value)
        return value.strip("._") or "file"

    def rename(self, new_name: str) -> Path:
        if not new_name or not new_name.strip():
            raise ValueError("Nama file baru tidak boleh kosong.")

        safe_name = self.sanitize_name(new_name)
        if not safe_name:
            raise ValueError("Nama file baru tidak valid.")

        new_path = self._path.with_name(f"{safe_name}{self._ext}")
        return new_path

    def move_to(self, target_dir: str | Path) -> Path:
        target_dir = Path(target_dir)
        return target_dir / self._path.name

