"""Rule berdasarkan ekstensi file."""

from rules.rule_engine import RuleEngine


class RuleEkstensi(RuleEngine):
    CATEGORY_MAP = {
        ".pdf": "PDF",
        ".doc": "Word",
        ".docx": "Word",
        ".odt": "Word",
        ".rtf": "Word",
        ".txt": "Teks",
        ".md": "Teks",
        ".epub": "EBook",
        ".mobi": "EBook",
        ".xls": "Spreadsheet",
        ".xlsx": "Spreadsheet",
        ".csv": "Spreadsheet",
        ".ppt": "Presentasi",
        ".pptx": "Presentasi",
        ".jpg": "Gambar",
        ".jpeg": "Gambar",
        ".png": "Gambar",
        ".gif": "Gambar",
        ".bmp": "Gambar",
        ".webp": "Gambar",
        ".svg": "Vector",
        ".ico": "Icon",
        ".icns": "Icon",
        ".mp4": "Video",
        ".mkv": "Video",
        ".mov": "Video",
        ".avi": "Video",
        ".webm": "Video",
        ".mp3": "Audio",
        ".wav": "Audio",
        ".flac": "Audio",
        ".m4a": "Audio",
        ".aac": "Audio",
        ".ogg": "Audio",
        ".zip": "Arsip",
        ".rar": "Arsip",
        ".7z": "Arsip",
        ".tar": "Arsip",
        ".gz": "Arsip",
        ".exe": "Program",
        ".msi": "Program",
        ".dmg": "Installer",
        ".pkg": "Installer",
        ".bat": "Program",
        ".cmd": "Program",
        ".sh": "Program",
        ".ps1": "Program",
        ".py": "Kode",
        ".js": "Kode",
        ".java": "Kode",
        ".cpp": "Kode",
        ".c": "Kode",
        ".html": "Kode",
        ".css": "Kode",
        ".php": "Kode",
        ".json": "Kode",
        ".xml": "Kode",
        ".yaml": "Config",
        ".yml": "Config",
        ".ini": "Config",
        ".cfg": "Config",
        ".toml": "Config",
        ".env": "Config",
        ".lock": "Config",
        ".iso": "DiskImage",
        ".img": "DiskImage",
    }

    def determine_category(self, file):
        ext = file.ext.lower()
        if ext in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"}:
            if self._looks_like_screenshot(file.name):
                return "Screenshot"
            if self._looks_like_logo(file.name):
                return "Logo"
            return "Gambar"

        if ext in {".ico", ".icns"}:
            return "Icon"

        if ext in {".exe", ".msi", ".dmg", ".pkg"}:
            if self._looks_like_installer(file.name):
                return "Installer"
            return "Program"

        if ext in {".zip", ".rar", ".7z", ".tar", ".gz", ".xz"}:
            return "Arsip"

        if ext in {".yaml", ".yml", ".ini", ".cfg", ".toml", ".env", ".lock"}:
            return "Config"

        return self.CATEGORY_MAP.get(ext, "Lainnya")

    @staticmethod
    def _looks_like_screenshot(name: str) -> bool:
        lowered = name.lower()
        return any(keyword in lowered for keyword in ("screenshot", "screen shot", "capture", "ss", "snip"))

    @staticmethod
    def _looks_like_logo(name: str) -> bool:
        lowered = name.lower()
        return any(keyword in lowered for keyword in ("logo", "brand", "icon", "mark"))

    @staticmethod
    def _looks_like_installer(name: str) -> bool:
        lowered = name.lower()
        return any(keyword in lowered for keyword in ("setup", "install", "installer", "update", "driver"))

    def generate_new_name(self, file, category: str) -> str:
        tanggal = file.mod_time.strftime("%Y-%m-%d")
        nama_asli = file.sanitize_name(file.name)
        kategori = file.sanitize_name(category)
        return f"{tanggal}_{nama_asli}_{kategori}"
