import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

VIDEO_FORMATS = (".avi", ".mp4", ".m4v", ".mov", ".mkv", ".wmv", ".flv", ".webm", ".mpg", ".mpeg", ".ts", ".3gp", ".ogv", ".asf", ".qt")

DEFAULT_SETTINGS = {}

with open(BASE_DIR / "default-settings.json", "r") as file:
    DEFAULT_SETTINGS = json.load(file)