import logging
import json
import io
from PIL import Image
from typing import List, Dict, Any, Union, Optional

import vertexai
from vertexai.generative_models import GenerativeModel, Part, HarmCategory, HarmBlockThreshold
from twitter_post_analyzer.constants import (
    GOOGLE_CLOUD_PROJECT_ID,
    VERTEX_AI_LOCATION,
    VERTEX_AI_MODEL_ID,
)

logger = logging.getLogger(__name__)

# --- Helper functions ---
def compress_image_to_bytes(image: Image.Image, max_size=(800, 800), quality=85, format_str="PNG") -> bytes:
    """Compresses PIL Image and returns bytes."""
    try:
        original_mode = image.mode
        if original_mode == 'P' or original_mode == 'RGBA':
             image = image.convert("RGB")

        img_copy = image.copy()
        img_copy.thumbnail(max_size)
        
        byte_io = io.BytesIO()
        save_format = format_str if format_str in ["JPEG", "PNG"] else "PNG"
        if save_format == "JPEG" and img_copy.mode == "RGBA":
            img_copy = img_copy.convert("RGB")

        img_copy.save(byte_io, format=save_format, optimize=True, quality=quality)
        return byte_io.getvalue()
    except Exception as e:
        logger.error(f"Error compressing image: {e}", exc_info=True)
        byte_io = io.BytesIO()
        try:
            original_format = image.format or "PNG"
            if original_format == "JPEG" and image.mode == "RGBA":
                image.convert("RGB").save(byte_io, format="JPEG")
            else:
                image.save(byte_io, format=original_format)
        except Exception:
            image.convert("RGB").save(byte_io, format="PNG")
        return byte_io.getvalue()

class VertexAILLMInterface:
    def __init__(self,
                 project_id: str = GOOGLE_CLOUD_PROJECT_ID,
                 location: str = VERTEX_AI_LOCATION,
                 model_id: str = VERTEX_AI_MODEL_ID):
        if not project_id:
            logger.critical("Project ID for Vertex AI not provided. Check twitter_post_analyzer/constants.py and .env file.")
            raise ValueError("Project ID for Vertex AI not provided.")
        try:
            vertexai.init(project=project_id, location=location)
            self.model = GenerativeModel(model_id)
            self.model_id = model_id
            logger.info(f"Vertex AI LLM interface initialized: project='{project_id}', location='{location}', model='{model_id}'")
        except Exception as e:
            logger.critical(f"Critical error initializing Vertex AI SDK: {e}", exc_info=True)
            raise

    def analyze_content_with_gemini(
        self,
        contents: List[Union[str, Part]],
        generation_config_override: Optional[Dict] = None,
        safety_settings_override: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Analyzes content (text and/or image/video parts) using Vertex AI Gemini API.
        Returns the parsed JSON response or an error dictionary.
        """
        default_generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 2048,
        }
        current_generation_config = {**default_generation_config, **(generation_config_override or {})}
        
        default_safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        current_safety_settings = safety_settings_override if safety_settings_override is not None else default_safety_settings
        
        raw_response_text = ""
        try:
            response = self.model.generate_content(
                contents=contents,
                generation_config=current_generation_config,
                safety_settings=current_safety_settings,
            )
            
            if not response.candidates:
                block_reason_msg = "Unknown reason for no candidates."
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    block_reason_msg = response.prompt_feedback.block_reason_message or str(response.prompt_feedback.block_reason)
                logger.error(f"Vertex AI response blocked or empty. Reason: {block_reason_msg}")
                return {"error": "VERTEX_AI_BLOCKED_OR_EMPTY", "details": block_reason_msg, "status_code": 400}

            if not response.text:
                 logger.error(f"Vertex AI response.text is empty. Candidates: {len(response.candidates)}")
                 if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                     response_text_from_parts = "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text'))
                     if not response_text_from_parts:
                        logger.error("Vertex AI response.text and combined parts are empty.")
                        return {"error": "VERTEX_AI_EMPTY_RESPONSE_TEXT_AND_PARTS", "details": "Response text and parts are empty.", "status_code": 500}
                     raw_response_text = response_text_from_parts
                 else:
                    logger.error("Vertex AI response.text is empty and no parts found.")
                    return {"error": "VERTEX_AI_EMPTY_RESPONSE_TEXT", "details": "Response text is empty and no parts.", "status_code": 500}
            else:
                raw_response_text = response.text

            # Strip Markdown code fences if present
            cleaned_response_text = raw_response_text.strip()
            if cleaned_response_text.startswith("```json"):
                cleaned_response_text = cleaned_response_text[7:]
            if cleaned_response_text.startswith("```"):
                cleaned_response_text = cleaned_response_text[3:]
            if cleaned_response_text.endswith("```"):
                cleaned_response_text = cleaned_response_text[:-3]
            cleaned_response_text = cleaned_response_text.strip()
            
            response_dict = json.loads(cleaned_response_text)
            logger.info("Successfully received and parsed response from Vertex AI.")
            return response_dict

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Vertex AI response as JSON. Raw response: '{raw_response_text}'", exc_info=True)
            return {"error": "VERTEX_AI_RESPONSE_PARSE_ERROR", "details": str(e), "raw_response": raw_response_text, "status_code": 500}
        except Exception as e:
            logger.exception(f"Error in VertexAILLMInterface during Vertex AI call: {e}")
            error_details = str(e)
            if hasattr(e, 'message'): 
                error_details = e.message
            elif hasattr(e, '_message'):
                 error_details = e._message
            return {"error": "VERTEX_AI_ERROR", "details": error_details, "status_code": 500}

    def analyze_image(self, image: Image.Image, text_prompt: str = "Describe this image.") -> str:
        try:
            image_format = image.format if image.format and image.format in ["JPEG", "PNG"] else "PNG"
            mime_type = f"image/{image_format.lower()}"
            
            compressed_bytes = compress_image_to_bytes(image, format_str=image_format)
            
            image_part = Part.from_data(data=compressed_bytes, mime_type=mime_type)
            text_part = Part.from_text(text_prompt)
            
            response = self.model.generate_content(
                contents=[text_part, image_part],
                generation_config={"temperature": 0.1, "max_output_tokens": 500} # Low temp for factual description
            )
            
            if not response.candidates:
                return "Error: No candidates from image analysis."
            return response.text
        except Exception as e:
            logger.error(f"Error during image analysis with Vertex AI: {e}", exc_info=True)
            return f"Error: {str(e)}"