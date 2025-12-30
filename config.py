"""
Nekira Agent - Configuration Module
====================================
Centralized configuration for character loading and project settings.
"""

import os
import logging
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ============================================
# Directory Configuration
# ============================================
PROJECT_ROOT = Path(__file__).parent
CHARACTERS_DIR = PROJECT_ROOT / "characters"

# ============================================
# Active Character
# ============================================
ACTIVE_CHARACTER = os.getenv("ACTIVE_CHARACTER", "nekira")


def get_character_path(character_name: Optional[str] = None) -> Path:
    """
    Get the path to a character's directory.
    
    Args:
        character_name: Name of the character (folder name). 
                       Defaults to ACTIVE_CHARACTER.
    
    Returns:
        Path to the character directory.
    
    Raises:
        ValueError: If character directory doesn't exist.
    """
    name = character_name or ACTIVE_CHARACTER
    path = CHARACTERS_DIR / name
    
    if not path.exists():
        available = [d.name for d in CHARACTERS_DIR.iterdir() 
                    if d.is_dir() and not d.name.startswith('_')]
        raise ValueError(
            f"Character '{name}' not found in {CHARACTERS_DIR}. "
            f"Available characters: {available}"
        )
    
    return path


def load_character_profile(character_name: Optional[str] = None) -> str:
    """
    Load character profile markdown content.
    
    Args:
        character_name: Name of the character to load.
    
    Returns:
        Content of the profile.md file.
    """
    char_path = get_character_path(character_name)
    profile_path = char_path / "profile.md"
    
    if not profile_path.exists():
        raise FileNotFoundError(
            f"Profile not found at {profile_path}. "
            f"Please create a profile.md file for your character."
        )
    
    content = profile_path.read_text(encoding="utf-8")
    logger.info(f"Loaded character profile: {character_name or ACTIVE_CHARACTER}")
    return content


def load_visual_config(character_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Load character visual configuration for image generation.
    
    Args:
        character_name: Name of the character to load.
    
    Returns:
        Dictionary with visual configuration:
        - base_description: Character's physical appearance
        - background_style: Default background and art style
        - personality_context: How personality affects visuals
    """
    char_path = get_character_path(character_name)
    config_path = char_path / "visual_config.py"
    
    if not config_path.exists():
        logger.warning(
            f"Visual config not found at {config_path}. "
            f"Using empty defaults."
        )
        return {
            "base_description": "",
            "background_style": "",
            "personality_context": "",
        }
    
    # Dynamically import the visual_config module
    spec = importlib.util.spec_from_file_location("visual_config", config_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    config = {
        "base_description": getattr(module, "BASE_DESCRIPTION", ""),
        "background_style": getattr(module, "BACKGROUND_STYLE", ""),
        "personality_context": getattr(module, "PERSONALITY_CONTEXT", ""),
    }
    
    logger.info(f"Loaded visual config: {character_name or ACTIVE_CHARACTER}")
    return config


def list_available_characters() -> list:
    """
    List all available character profiles.
    
    Returns:
        List of character names (folder names).
    """
    if not CHARACTERS_DIR.exists():
        return []
    
    return [
        d.name for d in CHARACTERS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith('_')
    ]
