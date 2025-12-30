import os
import logging
from typing import Dict, Any
from vertexai.generative_models import Part, GenerativeModel
from .common_llm_utils import get_vision_model, initialize_vertex_ai # MODIFIED: Relative import

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(module)s - %(message)s")

# Max file size in MB for inlineData (slightly less than the actual API limit)
MAX_INLINE_VIDEO_SIZE_MB = 19.0

async def analyze_video_content(local_path: str, tweet_text_context: str) -> Dict[str, Any]:
    """
    Analyzes video content using Google Gemini API.
    Prioritizes inlineData for smaller videos, or suggests GCS upload for larger ones.
    """
    logging.info(f"Starting video analysis: {local_path}")

    vision_model = get_vision_model()
    if not vision_model:
        error_msg = "Gemini Vision model not initialized."
        logging.error(error_msg)
        return {"description": None, "source": "gemini_video", "error": error_msg}

    if not os.path.exists(local_path):
        error_msg = f"Video file not found: {local_path}"
        logging.error(error_msg)
        return {"description": None, "source": "gemini_video", "error": error_msg}

    try:
        file_size_bytes = os.path.getsize(local_path)
        file_size_mb = file_size_bytes / (1024 * 1024)

        if file_size_mb > MAX_INLINE_VIDEO_SIZE_MB:
            error_msg = (f"Video file {os.path.basename(local_path)} ({file_size_mb:.2f}MB) "
                         f"is too large for inlineData (limit ~{MAX_INLINE_VIDEO_SIZE_MB}MB). "
                         f"Skipping this file or use GCS upload method.")
            logging.warning(error_msg)
            return {"description": None, "source": "gemini_video", "error": error_msg}

        logging.info(f"Video file size: {file_size_mb:.2f}MB. Suitable for inlineData.")

        with open(local_path, "rb") as video_file:
            video_bytes = video_file.read()

        file_extension = os.path.splitext(local_path)[1].lower()
        mime_map = {
            ".mp4": "video/mp4",
            ".mov": "video/quicktime",
            ".webm": "video/webm",
            ".avi": "video/avi",
            ".mpeg": "video/mpeg",
            ".mpg": "video/mpeg",
        }
        mime_type = mime_map.get(file_extension, "video/mp4")
        logging.info(f"Determined MIME type: {mime_type} for file {local_path}")

        video_part = Part.from_data(data=video_bytes, mime_type=mime_type)

        # The prompt provided by the user for video analysis
        prompt_text = (
            "Please describe this video in detail. "
            "Indicate key scenes, objects, actions, and any visible text. "
            "What is the overall theme or message of the video? "
            "If there are people in the video, describe their appearance and actions. "
            "If there are animals, specify their species. "
            "If it's an animation, describe the animation style."
        )
        
        contents = [video_part, prompt_text]

        logging.info(f"Sending video {os.path.basename(local_path)} for analysis to model {vision_model._model_name}...")
        
        response = await vision_model.generate_content_async(contents)
        
        description = response.text.strip()
        logging.info(f"Video analysis for {os.path.basename(local_path)} successful.")
        
        return {"description": description, "source": f"{vision_model._model_name}_inline", "error": None}

    except Exception as e:
        error_msg = f"Error during video analysis {local_path}: {e}"
        logging.exception(error_msg)
        return {"description": None, "source": "gemini_video", "error": error_msg}