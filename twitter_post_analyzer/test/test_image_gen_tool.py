# test_image_gen_tool.py
import asyncio
import logging
from pathlib import Path

# Make sure PYTHONPATH is configured to import your modules,
# or add the project path if not running from the root.
# import sys
# sys.path.append(str(Path(__file__).resolve().parent))  # Add current directory to PYTHONPATH

# Import required modules from your project
from twitter_post_analyzer.sub_agents.image_generator_agent.tool.image_generator_tool import generate_image_via_replicate_sdk
from twitter_post_analyzer.constants import REPLICATE_GENERATED_IMAGES_DIR, ensure_dir_exists

# Configure logging to see tool outputs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s")
logger = logging.getLogger()  # Get root logger

async def main():
    logger.info("Starting direct test of generate_image_via_replicate_sdk tool...")

    # 1. Ensure the save directory exists
    ensure_dir_exists(REPLICATE_GENERATED_IMAGES_DIR)
    logger.info(f"Ensured Replicate generated images directory exists: {REPLICATE_GENERATED_IMAGES_DIR.resolve()}")

    # 2. Prepare test data
    test_prompt = "Nekira, a cyberpunk anime girl and digital avatar from a parallel multiverse, inspired by 80s-90s manga and anime (cyberpunk-girl-v2, ghost-in-the-shell-style, Akira, Ghost in the Shell, Bubblegum Crisis). She has short neon-pink hair with black streaks, large expressive eyes with sharp lashes. Her outfit includes a cropped neon-yellow jacket with glowing blue circuit patterns, a black asymmetrical top, tight tactical pants with neon straps, and high combat boots with glowing soles. She has subtle cybernetic implants on her cheek and neck with metallic textures, and faint pixelated glitches around her body, hinting at her digital nature. She wears futuristic AR-glasses with neon-blue displays and holographic fabric inserts on her jacket that shimmer with changing colors. Extreme close-up on Nekara's face, focusing on her cybernetic implants around her cheek and neck. The implants are heavily glitched, revealing raw data streams in neon green and electric blue, and distorting the surrounding skin with pixelated artifacts. She has a playful, slightly menacing smirk, her eyes sparkling with digital mischief. The AR-glasses show fragmented code. Background: Abstract, swirling patterns of binary code and distorted neon colors, suggesting a chaotic data stream. Art Style: hand-drawn manga style, cel-shaded, flat shading, retro anime aesthetic with crisp outlines, slight VHS grain texture, vibrant neon colors (pink, blue, purple) contrasting deep shadows, detailed mechanical elements, cinematic lighting with neon glow. Keywords: glitch art, data stream, cybernetic malfunction, menacing smirk, abstract background."
    # test_prompt = "A beautiful landscape painting of a serene valley at sunset, digital art."  # You can try different prompts
    test_image_name_prefix = "test_direct_gen"
    test_aspect_ratio = "1:1"
    test_output_format = "jpg"

    logger.info(f"Test prompt: \"{test_prompt}\"")
    logger.info(f"Image name prefix: {test_image_name_prefix}")

    # 3. Call the tool directly
    try:
        generated_file_path_str = await generate_image_via_replicate_sdk(
            prompt=test_prompt,
            image_name_prefix=test_image_name_prefix,
            aspect_ratio=test_aspect_ratio,
            output_format=test_output_format
        )

        if generated_file_path_str:
            logger.info(f"SUCCESS! Tool returned image path: {generated_file_path_str}")
            # Check if the file exists
            if Path(generated_file_path_str).is_file():
                logger.info(f"VERIFIED: File exists at {Path(generated_file_path_str).resolve()}")
                logger.info(f"File size: {Path(generated_file_path_str).stat().st_size / 1024:.2f} KB")
            else:
                logger.error(f"ERROR: Tool returned a path, but the file does NOT exist at {generated_file_path_str}")
        else:
            logger.error("FAILURE: Tool returned None, indicating an error during image generation or saving.")

    except Exception as e:
        logger.error(f"An unexpected error occurred during the test: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())