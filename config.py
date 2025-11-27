"""
HyprContext - Merkezi Konfigürasyon
Tüm ayarlar burada tanımlı. .env dosyasından okunur.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# === .env YÜKLE ===
BASE_DIR = Path(__file__).parent.resolve()
load_dotenv(BASE_DIR / ".env")


def get_env(key: str, default: str = "") -> str:
    """Environment variable okur, yoksa default döner."""
    return os.getenv(key, default)


def get_env_int(key: str, default: int = 0) -> int:
    """Environment variable'ı int olarak okur."""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


def get_env_list(key: str, default: list = None) -> list:
    """Environment variable'ı virgülle ayrılmış liste olarak okur."""
    if default is None:
        default = []
    value = os.getenv(key)
    if value:
        return [item.strip() for item in value.split(",")]
    return default


def get_env_path(key: str, default: str = "") -> Path:
    """Environment variable'ı Path olarak okur, ~ işaretini genişletir."""
    value = os.getenv(key, default)
    return Path(value).expanduser() if value else Path(default)


# === TEMEL YOLLAR ===
HISTORY_FILE = BASE_DIR / "history.jsonl"
DB_PATH = BASE_DIR / "hafiza_db"
REPORTS_DIR = BASE_DIR / "raporlar"

# === OBSIDIAN ENTEGRASYONU ===
OBSIDIAN_VAULT = get_env_path("OBSIDIAN_VAULT", "~/SecondBrain")
OBSIDIAN_DAILY_DIR = get_env_path("OBSIDIAN_DAILY_DIR", "~/SecondBrain/Gunlukler")

# === OLLAMA MODELLERİ ===
MODEL_VISION = get_env("MODEL_VISION", "gemma3")
MODEL_EMBED = get_env("MODEL_EMBED", "mxbai-embed-large")
MODEL_CHAT = get_env("MODEL_CHAT", "gemma3")
MODEL_PLAN = get_env("MODEL_PLAN", MODEL_VISION)  # Vision ile aynı
MODEL_REPORT = get_env("MODEL_REPORT", MODEL_VISION)  # Vision ile aynı

# === ZAMANLAMA ===
CAPTURE_INTERVAL = get_env_int("CAPTURE_INTERVAL", 20)
MIN_COOLDOWN = get_env_int("MIN_COOLDOWN", 5)

# === HAFIZA ===
RAM_SIZE = get_env_int("RAM_SIZE", 5)
MEMORY_DAYS = get_env_int("MEMORY_DAYS", 7)

# === ODAK BEKÇİSİ ===
YASAKLI_KELIMELER = get_env_list(
    "YASAKLI_KELIMELER",
    ["youtube", "instagram", "twitter", "reddit", "oyun", "netflix", "video", "tiktok"]
)
DISTRACTION_THRESHOLD = get_env_int("DISTRACTION_THRESHOLD", 3)

# === DASHBOARD ===
MAX_DASHBOARD_ROWS = get_env_int("MAX_DASHBOARD_ROWS", 50)

# === CHROMADB ===
COLLECTION_NAME = "hypr_logs"

# === HAVA DURUMU ===
WEATHER_CITY = get_env("WEATHER_CITY", "Mersin")
WEATHER_URL = f"wttr.in/{WEATHER_CITY}?format=%c+%t"

# === PROFİL ===
PROFILE_PATH = BASE_DIR / "profile.yaml"


def ensure_dirs():
    """Gerekli klasörlerin var olduğundan emin ol."""
    REPORTS_DIR.mkdir(exist_ok=True)
    OBSIDIAN_DAILY_DIR.mkdir(parents=True, exist_ok=True)


def print_config():
    """Mevcut konfigürasyonu yazdırır (debug için)."""
    print("=== HyprContext Konfigürasyonu ===")
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"OBSIDIAN_VAULT: {OBSIDIAN_VAULT}")
    print(f"MODEL_VISION: {MODEL_VISION}")
    print(f"MODEL_EMBED: {MODEL_EMBED}")
    print(f"CAPTURE_INTERVAL: {CAPTURE_INTERVAL}s")
    print(f"YASAKLI_KELIMELER: {YASAKLI_KELIMELER}")
    print(f"WEATHER_CITY: {WEATHER_CITY}")
    print("=" * 35)


if __name__ == "__main__":
    print_config()
