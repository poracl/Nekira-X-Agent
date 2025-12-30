from typing import Dict, Any
import os
import logging
from vertexai.generative_models import Image # Only Image is needed here
from .common_llm_utils import get_vision_model # MODIFIED: Relative import

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(module)s - %(message)s")

async def analyze_image_content(local_path: str, tweet_text_context: str) -> Dict[str, Any]:
    """
    Analyzes image content using Google Gemini Vision Pro.
    """
    vision_model = get_vision_model()
    if not vision_model:
        return {"description": None, "source": "gemini-pro-vision", "error": "Gemini Vision model not initialized."}
    
    if not os.path.exists(local_path):
        return {"description": None, "source": "gemini-pro-vision", "error": f"Image file not found: {local_path}"}

    try:
        image = Image.load_from_file(local_path)
        prompt = f"Analyze this image in the context of the following tweet text: '{tweet_text_context}'. Describe the image content, any objects, scenes, or text present, and its relevance to the tweet. Be concise and informative."
        
        responses = await vision_model.generate_content_async([prompt, image])
        description = responses.text.strip()
        return {"description": description, "source": "gemini-pro-vision", "error": None}
    except Exception as e:
        logging.error(f"Error analyzing image {local_path}: {e}")
        return {"description": None, "source": "gemini-pro-vision", "error": str(e)}