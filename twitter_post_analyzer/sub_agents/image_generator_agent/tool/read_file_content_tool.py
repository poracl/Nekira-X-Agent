import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def read_text_file_content(file_path: str) -> Dict[str, Any]:
    """
    ADK Tool: Reads the content of a specified text file.
    """
    logger.info(f"READ_FILE_TOOL: Attempting to read file: {file_path}")
    if not file_path:
        logger.warning("READ_FILE_TOOL: No file path provided.")
        return {"status": "error", "message": "No file path provided to tool.", "file_content": None}

    try:
        path = Path(file_path)
        if not path.is_file():
            logger.error(f"READ_FILE_TOOL: File not found at {file_path}")
            return {"status": "error", "message": f"File not found: {file_path}", "file_content": None}

        content = path.read_text(encoding='utf-8')
        logger.info(f"READ_FILE_TOOL: Successfully read file {file_path}, length {len(content)} chars.")
        return {"status": "success", "file_content": content, "message": "File read successfully."}
    except Exception as e:
        logger.exception(f"READ_FILE_TOOL: Error reading file {file_path}: {e}")
        return {"status": "error", "message": f"Failed to read file: {str(e)}", "file_content": None}