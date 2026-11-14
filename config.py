import os

from dotenv import load_dotenv

load_dotenv()


def _env_int(name, default):
    return int(os.getenv(name, str(default)))


def _env_bool(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in ("1", "true", "yes", "on"):
        return True
    if normalized in ("0", "false", "no", "off"):
        return False
    raise ValueError(f"{name} must be true or false")


def _env_list(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]

# --- AI (Groq) ---  needs GROQ_API_KEY environment variable
VISION_MODEL = "qwen/qwen3.8-27b"     # must accept images. CHECK console.groq.com/docs/vision (list changes)
CHAT_MODEL = "openai/gpt-oss-120b"    # text-only 120B model: answers questions and reasons over history
CHAT_REASONING_EFFORT = "low"         # "low" | "medium" | "high"
MAX_TOKENS_DESCRIBE = 400
MAX_TOKENS_SCREEN = 900               # detailed screen reading before the 120B model answers
MAX_TOKENS_CHAT = 1500                # gpt-oss counts its thinking tokens here too

# --- Timing ---
CHECK_INTERVAL = 2                    # seconds between "what window is active?" checks
MIN_SECONDS_BETWEEN_ANALYSES = 5      # throttle so you don't spend money on rapid switching

# --- Screenshot ---
MONITOR = 1                           # 1 = primary monitor, 0 = all monitors combined
IMAGE_MAX_SIZE = 1280                 # longest side in pixels (smaller = cheaper/faster)
JPEG_QUALITY = 70
SAME_SCREEN_THRESHOLD = 5             # perceptual-hash distance; lower = more sensitive

# --- Storage ---
DATA_DIR = "data"
DB_PATH = os.path.join(DATA_DIR, "history.db")
IMAGE_DIR = os.path.join(DATA_DIR, "images")
SAVE_IMAGES = False                   # False = images live in RAM only, never touch disk
IMAGE_KEEP_DAYS = 3                   # only used if SAVE_IMAGES = True

# --- Privacy: anything matching is NEVER captured ---
BLOCKED_KEYWORDS = [
    "password", "bank", "incognito", "private browsing", "inprivate",
    "paypal", "upi", "credit card", "login", "sign in", "otp",
]
BLOCKED_APPS = [
    "1password", "bitwarden", "keepass", "lastpass", "whatsapp", "telegram",
    "signal", "authenticator",
]

# Environment values override defaults above.
VISION_MODEL = os.getenv("VISION_MODEL", VISION_MODEL)
CHAT_MODEL = os.getenv("CHAT_MODEL", CHAT_MODEL)
CHAT_REASONING_EFFORT = os.getenv("CHAT_REASONING_EFFORT", CHAT_REASONING_EFFORT)
MAX_TOKENS_DESCRIBE = _env_int("MAX_TOKENS_DESCRIBE", MAX_TOKENS_DESCRIBE)
MAX_TOKENS_SCREEN = _env_int("MAX_TOKENS_SCREEN", MAX_TOKENS_SCREEN)
MAX_TOKENS_CHAT = _env_int("MAX_TOKENS_CHAT", MAX_TOKENS_CHAT)
CHECK_INTERVAL = _env_int("CHECK_INTERVAL", CHECK_INTERVAL)
MIN_SECONDS_BETWEEN_ANALYSES = _env_int(
    "MIN_SECONDS_BETWEEN_ANALYSES", MIN_SECONDS_BETWEEN_ANALYSES)
MONITOR = _env_int("MONITOR", MONITOR)
IMAGE_MAX_SIZE = _env_int("IMAGE_MAX_SIZE", IMAGE_MAX_SIZE)
JPEG_QUALITY = _env_int("JPEG_QUALITY", JPEG_QUALITY)
SAME_SCREEN_THRESHOLD = _env_int("SAME_SCREEN_THRESHOLD", SAME_SCREEN_THRESHOLD)
DATA_DIR = os.getenv("DATA_DIR", DATA_DIR)
DB_PATH = os.path.join(DATA_DIR, "history.db")
IMAGE_DIR = os.path.join(DATA_DIR, "images")
SAVE_IMAGES = _env_bool("SAVE_IMAGES", SAVE_IMAGES)
IMAGE_KEEP_DAYS = _env_int("IMAGE_KEEP_DAYS", IMAGE_KEEP_DAYS)
BLOCKED_KEYWORDS = _env_list("BLOCKED_KEYWORDS", BLOCKED_KEYWORDS)
BLOCKED_APPS = _env_list("BLOCKED_APPS", BLOCKED_APPS)

# --- Prompts ---
DESCRIBE_PROMPT = (
    "Describe what the user is doing on this screen in under 100 words. "
    "State the active app and its window title. If a video is open, give its exact title from "
    "the page or window title. List the other currently open taskbar apps from the supplied list; "
    "do not mistake pinned icons for open apps. If a detail is not readable, say so. "
    "Include the key visible text or topic. "
    "Do not identify real people by their faces."
)
