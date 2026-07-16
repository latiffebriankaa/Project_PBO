"""Konfigurasi utama aplikasi BeresFile."""

from pathlib import Path


SCAN_DIR = str(Path.home() / "Downloads")
DRY_RUN = True
ENABLE_AI = True

# gemini vision masukan api key
GEMINI_API_KEY = ""
GEMINI_MODEL = "gemini-1.5-flash"

# Folder hasil pengelompokan akan dibuat di dalam folder target.
OUTPUT_ROOT_NAME = "BeresFile"

# Nama folder backup log dan folder undo yang dibuat di dalam folder target.
LOG_DIR_NAME = "BeresFile_Logs"
