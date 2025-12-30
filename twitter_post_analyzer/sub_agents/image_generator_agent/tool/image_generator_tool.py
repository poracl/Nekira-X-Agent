"""
Image Generator Tool
=====================
Generates images using Replicate API (Flux 1.1 Pro Ultra model).
"""

import httpx
import logging
import time
from pathlib import Path
from typing import Optional, Any
import asyncio
import replicate

from ....constants import REPLICATE_API_TOKEN, REPLICATE_GENERATED_IMAGES_DIR, ensure_dir_exists

logger = logging.getLogger(__name__)

REPLICATE_MODEL_FOR_GENERATION = "black-forest-labs/flux-1.1-pro-ultra"

if not REPLICATE_API_TOKEN:
    logger.warning("REPLICATE_SDK_TOOL: REPLICATE_API_TOKEN not found. Image generation unavailable.")


async def _save_image_from_url(image_url: str, output_path: Path) -> bool:
    """Download and save image from URL to local path."""
    if not image_url:
        logger.error("IMAGE_SAVE_TOOL: Cannot save image: image_url is None or empty.")
        return False
    
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            logger.info(f"IMAGE_SAVE_TOOL: Downloading image from: {image_url}")
            response = await client.get(image_url)
            logger.info(f"IMAGE_SAVE_TOOL: Response status: {response.status_code}")
            response.raise_for_status()
            
            ensure_dir_exists(output_path.parent)
            
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            logger.info(f"IMAGE_SAVE_TOOL: Image saved: {output_path} ({output_path.stat().st_size / 1024:.2f} KB)")
            return True
    
    except httpx.HTTPStatusError as e:
        logger.error(f"IMAGE_SAVE_TOOL: HTTP error downloading {image_url}: {e.response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"IMAGE_SAVE_TOOL: Request error downloading {image_url}: {e}")
    except Exception as e:
        logger.error(f"IMAGE_SAVE_TOOL: Failed to save {image_url}: {e}", exc_info=True)
    
    return False


async def generate_image_via_replicate_sdk(
    prompt: str,
    image_name_prefix: str,
    aspect_ratio: str = "1:1",
    output_format: str = "jpg",
    raw_output: Optional[bool] = None,
    seed: Optional[int] = None,
    safety_tolerance: Optional[int] = None,
    image_prompt_url: Optional[str] = None,
    image_prompt_strength: Optional[float] = None,
) -> Any:
    """
    Generate an image using Replicate's Flux model.
    
    Args:
        prompt: Text prompt for image generation
        image_name_prefix: Prefix for the output filename
        aspect_ratio: Image aspect ratio (default: "1:1")
        output_format: Output format (default: "jpg")
        raw_output: Whether to use raw output mode
        seed: Random seed for reproducibility
        safety_tolerance: Safety filter tolerance level
        image_prompt_url: Reference image URL for img2img
        image_prompt_strength: Strength of image prompt influence
    
    Returns:
        Path to the generated image file, or None on failure
    """
    final_result: Any = {"debug_status": "function_started_but_did_not_complete_normally"}

    try:
        logger.info(f"REPLICATE_SDK_TOOL: Starting. Prompt: {prompt[:100]}..., Prefix: {image_name_prefix}")

        if not REPLICATE_API_TOKEN:
            logger.error("REPLICATE_SDK_TOOL: REPLICATE_API_TOKEN is not configured.")
            return None

        # Build input payload
        input_payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "output_format": output_format,
        }
        
        if raw_output is not None:
            input_payload["raw"] = raw_output
        if seed is not None:
            input_payload["seed"] = seed
        if safety_tolerance is not None:
            input_payload["safety_tolerance"] = safety_tolerance
        if image_prompt_url:
            input_payload["image_prompt"] = image_prompt_url
            if image_prompt_strength is not None:
                input_payload["image_prompt_strength"] = image_prompt_strength

        logger.info(f"REPLICATE_SDK_TOOL: Calling model: {REPLICATE_MODEL_FOR_GENERATION}")
        logger.debug(f"REPLICATE_SDK_TOOL: Payload: {input_payload}")

        # Run Replicate API call in executor (blocking call)
        api_output = None
        try:
            loop = asyncio.get_event_loop()
            
            def sync_replicate_run():
                logger.info("REPLICATE_SDK_TOOL: Executing Replicate API call...")
                output = replicate.run(REPLICATE_MODEL_FOR_GENERATION, input=input_payload)
                logger.info(f"REPLICATE_SDK_TOOL: API call completed. Output type: {type(output)}")
                return output

            api_output = await loop.run_in_executor(None, sync_replicate_run)

        except Exception as e:
            logger.error(f"REPLICATE_SDK_TOOL: Error during replicate.run: {e}", exc_info=True)
            return None

        logger.info(f"REPLICATE_SDK_TOOL: Raw API output type: {type(api_output)}")
        logger.info(f"REPLICATE_SDK_TOOL: Raw API output: {api_output}")

        if not api_output:
            logger.error("REPLICATE_SDK_TOOL: Replicate API returned no output.")
            return None

        # Extract image URL from API output
        output_image_url = None
        
        if isinstance(api_output, str):
            output_image_url = api_output
        elif hasattr(api_output, 'url') and isinstance(getattr(api_output, 'url', None), str):
            output_image_url = api_output.url
        elif isinstance(api_output, (list, tuple)) and len(api_output) > 0:
            first_item = api_output[0]
            if isinstance(first_item, str):
                output_image_url = first_item
            elif hasattr(first_item, 'url') and isinstance(getattr(first_item, 'url', None), str):
                output_image_url = first_item.url

        logger.info(f"REPLICATE_SDK_TOOL: Extracted image URL: {output_image_url}")

        if not output_image_url:
            logger.error("REPLICATE_SDK_TOOL: Could not determine valid image URL from output.")
            return None

        # Save the image locally
        file_extension = f".{output_format.lower()}"
        safe_prefix = "".join(c if c.isalnum() or c in ['_', '-'] else '_' for c in image_name_prefix)
        image_filename = f"{safe_prefix}_{int(time.time())}{file_extension}"

        if not isinstance(REPLICATE_GENERATED_IMAGES_DIR, Path):
            logger.error(f"REPLICATE_SDK_TOOL: Invalid images directory: {REPLICATE_GENERATED_IMAGES_DIR}")
            return None

        output_file_path = REPLICATE_GENERATED_IMAGES_DIR / image_filename
        logger.info(f"REPLICATE_SDK_TOOL: Saving to: {output_file_path.resolve()}")

        if await _save_image_from_url(output_image_url, output_file_path):
            logger.info("REPLICATE_SDK_TOOL: Image saved successfully.")
            return str(output_file_path)
        else:
            logger.error("REPLICATE_SDK_TOOL: Failed to save image from URL.")
            return None

    except replicate.exceptions.ReplicateError as e:
        logger.error(f"REPLICATE_SDK_TOOL: Replicate API error: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.exception(f"REPLICATE_SDK_TOOL: Unexpected error: {e}")
        return None
    finally:
        logger.info(f"REPLICATE_SDK_TOOL: Exiting. Final result: {final_result} (type: {type(final_result)})")