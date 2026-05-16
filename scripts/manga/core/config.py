from pathlib import Path

# --- Project Root ---
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# --- Directory Paths ---
RAW_MANGA_DIR = DATA_DIR / "raw" / "manga" / "panels"
SEGMENTED_DIR = DATA_DIR / "raw" / "manga" / "segmented"
MOBILE_DIR = DATA_DIR / "manga" / "mobile"

# --- Panel Paths (Volume specific) ---
def get_panel_dir(volume: str = "buddha_v01") -> Path:
    # Returns the path to image panels for a given volume
    return RAW_MANGA_DIR / volume / "panels" / "image panels"

def get_text_dir(volume: str = "buddha_v01") -> Path:
    # Returns the path to text panels for a given volume
    return RAW_MANGA_DIR / volume / "panels" / "text panels"

# --- Available Volumes ---
VOLUMES = [f"buddha_v{i:02d}" for i in range(1, 9)]

# --- Ollama Configuration ---
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
VISION_MODEL = "llava"
TEXT_MODEL = "qwen2.5:14b"
EMBEDDING_MODEL = "nomic-embed-text"

# --- Pipeline Settings ---
PANEL_MIN_WIDTH = 200
PANEL_MIN_HEIGHT = 200
OCR_TEXT_THRESHOLD = 2

# --- Mobile Optimization ---
MOBILE_MAX_DIMENSION = 1200
MOBILE_WEBP_QUALITY = 80
