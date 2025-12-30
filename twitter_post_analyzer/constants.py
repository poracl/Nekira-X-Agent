"""
Nekira Agent - Constants and Configuration
============================================
Environment variables, API keys, and directory configuration.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load .env file
load_dotenv()

# ============================================
# Model Configuration
# ============================================
MODEL = "gemini-2.0-flash"

# ============================================
# Vertex AI Settings
# ============================================
GOOGLE_CLOUD_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
GOOGLE_APPLICATION_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
VERTEX_AI_LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")
VERTEX_AI_MODEL_ID = os.getenv("VERTEX_AI_MODEL_ID", MODEL)

# ============================================
# API Key Settings
# ============================================
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Twitter API v2 (OAuth 1.0a User Context)
TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# ============================================
# Media Directories
# ============================================
PROJECT_ROOT_DIR = Path(__file__).resolve().parent
MEDIA_ROOT_DIR = PROJECT_ROOT_DIR / "media"

DOWNLOADED_TWEET_MEDIA_DIR_NAME = "downloaded_tweet_media"
DOWNLOAD_DIR = MEDIA_ROOT_DIR / DOWNLOADED_TWEET_MEDIA_DIR_NAME

GENERATED_TOKEN_IMAGES_DIR_NAME = "generated_token_images_replicate"
REPLICATE_GENERATED_IMAGES_DIR = MEDIA_ROOT_DIR / GENERATED_TOKEN_IMAGES_DIR_NAME

# ============================================
# Utility Functions
# ============================================
def ensure_dir_exists(dir_path: Path):
    """Create directory if it doesn't exist."""
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {dir_path}")


# Create directories upon configuration load
ensure_dir_exists(MEDIA_ROOT_DIR)
ensure_dir_exists(DOWNLOAD_DIR)
ensure_dir_exists(REPLICATE_GENERATED_IMAGES_DIR)

# ============================================
# Environment Validation
# ============================================
if not GOOGLE_CLOUD_PROJECT_ID:
    logger.error("CRITICAL: GOOGLE_CLOUD_PROJECT_ID not found. Check your .env file.")

if GOOGLE_APPLICATION_CREDENTIALS_PATH:
    if os.path.exists(GOOGLE_APPLICATION_CREDENTIALS_PATH):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS_PATH
        logger.info(f"GOOGLE_APPLICATION_CREDENTIALS set to: {GOOGLE_APPLICATION_CREDENTIALS_PATH}")
    else:
        logger.warning(f"Credentials file not found: {GOOGLE_APPLICATION_CREDENTIALS_PATH}. Using ADC.")
else:
    logger.info("GOOGLE_APPLICATION_CREDENTIALS not specified. Using ADC (Application Default Credentials).")

if not REPLICATE_API_TOKEN:
    logger.warning("REPLICATE_API_TOKEN not found. Image generation will be unavailable.")

if not all([TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
    logger.warning("Twitter API credentials incomplete. Tweet posting will be unavailable.")

logger.info(f"Configuration loaded. Project: {GOOGLE_CLOUD_PROJECT_ID}, Model: {VERTEX_AI_MODEL_ID}, Location: {VERTEX_AI_LOCATION}")
logger.info(f"Replicate API Token: {'Present' if REPLICATE_API_TOKEN else 'Missing'}")