"""Rule opsional yang memakai Gemini Vision untuk file gambar."""

from __future__ import annotations

import base64
from pathlib import Path

from rules.rule_engine import RuleEngine

try:
    import requests
except Exception:  # pragma: no cover - fallback bila requests tidak ada
    requests = None


class RuleAI(RuleEngine):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key.strip()
        self.model = model

    @staticmethod
    def _is_image(file) -> bool:
        return file.ext.lower() in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

    def is_available(self) -> bool:
        return bool(self.api_key) and requests is not None

    def determine_category(self, file):
        if not self.is_available() or not self._is_image(file):
            return ""

        return "Gambar"

    def generate_new_name(self, file, category: str) -> str:
        if not self.is_available() or not self._is_image(file):
            return file.sanitize_name(file.name)

        try:
            desc = self._analyze_image(file.path)
            if not desc:
                return file.sanitize_name(file.name)
            return file.sanitize_name(desc)
        except Exception:
            return file.sanitize_name(file.name)

    def _analyze_image(self, image_path: Path) -> str:
        if requests is None:
            return ""

        mime = "image/png"
        suffix = image_path.suffix.lower()
        if suffix in {".jpg", ".jpeg"}:
            mime = "image/jpeg"
        elif suffix == ".webp":
            mime = "image/webp"
        elif suffix == ".gif":
            mime = "image/gif"

        with open(image_path, "rb") as handle:
            encoded = base64.b64encode(handle.read()).decode("utf-8")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": "Beri nama singkat dan deskriptif dalam bahasa Indonesia untuk file gambar ini. Hanya keluarkan satu judul singkat."},
                        {"inline_data": {"mime_type": mime, "data": encoded}},
                    ]
                }
            ]
        }

        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        texts = [part.get("text", "") for part in parts if part.get("text")]
        return " ".join(texts).strip()
