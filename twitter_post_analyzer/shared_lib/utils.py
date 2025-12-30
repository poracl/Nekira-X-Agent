# shared_lib/utils.py
import os
import json
import logging
import aiofiles

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        filename="twitter_post_analyzer.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def get_data_dir(analysis_id):
    """Get the directory for storing data for a given analysis_id."""
    data_dir = os.path.join("data", analysis_id)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

def get_media_dir(analysis_id):
    """Get the directory for storing media for a given analysis_id."""
    media_dir = os.path.join(get_data_dir(analysis_id), "media")
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
    return media_dir

async def save_json(data, filename, analysis_id):
    """Save data to a JSON file in the data directory."""
    data_dir = get_data_dir(analysis_id)
    filepath = os.path.join(data_dir, filename)
    async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, indent=2, ensure_ascii=False))
    logging.info(f"Saved data to {filepath}")
    return filepath

async def load_json(filename, analysis_id):
    """Load data from a JSON file in the data directory."""
    data_dir = get_data_dir(analysis_id)
    filepath = os.path.join(data_dir, filename)
    if not os.path.exists(filepath):
        logging.error(f"File {filepath} does not exist")
        return None
    async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
        data = json.loads(await f.read())
    logging.info(f"Loaded data from {filepath}")
    return data