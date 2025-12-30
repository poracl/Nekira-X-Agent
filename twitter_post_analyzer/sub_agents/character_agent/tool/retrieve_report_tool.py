# twitter_post_analyzer/sub_agents/character_agent/tool/retrieve_report_tool.py
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def retrieve_report_content_from_file(report_file_path: str) -> Dict[str, Any]:
    """
    ADK Tool: Reads the content of the analysis report file.

    Args:
        report_file_path (str): The path to the markdown report file.

    Returns:
        Dict[str, Any]: A dictionary containing the status and content of the file,
                        or an error message.
    """
    logger.info(f"CharacterAgent - TOOL: Attempting to read report from: {report_file_path}")
    if not report_file_path:
        logger.warning("CharacterAgent - TOOL: No report file path provided.")
        return {"status": "error", "message": "No report file path provided to tool."}

    try:
        path = Path(report_file_path)
        if not path.is_file():
            logger.error(f"CharacterAgent - TOOL: Report file not found at {report_file_path}")
            return {"status": "error", "message": f"Report file not found: {report_file_path}"}

        content = path.read_text(encoding='utf-8')
        logger.info(f"CharacterAgent - TOOL: Successfully read report file {report_file_path}, length {len(content)} chars.")
        return {"status": "success", "report_markdown_content": content}
    except Exception as e:
        logger.exception(f"CharacterAgent - TOOL: Error reading report file {report_file_path}: {e}")
        return {"status": "error", "message": f"Failed to read report: {str(e)}"}