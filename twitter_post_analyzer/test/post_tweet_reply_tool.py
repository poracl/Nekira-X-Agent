# test_post_reply.py
import asyncio
import logging
from pathlib import Path

# Import the post_tweet_reply function and constants
# Make sure the import path matches your structure
# This import assumes test_post_reply.py is in the root,
# and twitter_post_analyzer is a package in that root.
from twitter_post_analyzer.sub_agents.post_reply_agent.tool.post_tweet_reply_tool import post_tweet_reply
from twitter_post_analyzer.constants import (
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET
)

# Configure logging to see tool outputs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s")
logger = logging.getLogger()

async def main():
    logger.info("Starting direct test of post_tweet_reply tool...")

    # 1. Check if keys are loaded from constants
    if not all([TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
        logger.error("CRITICAL: Twitter API credentials are not fully loaded from constants.py. Check your .env file and constants.py.")
        return
    logger.info("Twitter API credentials seem to be loaded.")

    # 2. Prepare test data
    # ---- REPLACE THIS ID WITH A REAL TWEET ID YOU CAN REPLY TO ----
    # Important: this should be an ID of a tweet that exists and you can reply to.
    # To avoid spam, you can use your own tweet's ID.
    test_tweet_id_to_reply_to = "1928348469648830604"
    test_reply_text = f"test1"

    # Optional: path to a test image if you want to test media upload.
    # Make sure the file exists at this path.
    # test_image_path = r"C:\path\to\your\test\image.jpg"  # Use r"" for Windows paths
    test_image_path = None  # Default: no image for simplicity

    if "YOUR_TEST_TWEET_ID" in test_tweet_id_to_reply_to:
        logger.error("PLEASE REPLACE test_tweet_id_to_reply_to WITH A REAL Tweet ID!")
        return

    logger.info(f"Attempting to reply to tweet ID: {test_tweet_id_to_reply_to}")
    logger.info(f"Reply text: \"{test_reply_text}\"")
    if test_image_path:
        logger.info(f"With image: {test_image_path}")
    else:
        logger.info("Without image.")

    # 3. Call the posting function directly
    try:
        result = await post_tweet_reply(
            tweet_id_to_reply_to=test_tweet_id_to_reply_to,
            reply_text=test_reply_text,
            image_path=test_image_path
        )

        logger.info(f"Tool call result: {result}")

        if result and result.get("status") == "success":
            logger.info(f"SUCCESS! Tweet posted. ID: {result.get('tweet_id')}, Text: {result.get('text')}")
            if result.get("posted_image_url"):
                logger.info(f"Image posted: {result.get('posted_image_url')}")
        else:
            logger.error(f"FAILURE: Tool returned an error or unexpected status. Message: {result.get('message') if result else 'No result'}")

    except Exception as e:
        logger.error(f"An unexpected error occurred during the direct tool call: {e}", exc_info=True)

if __name__ == "__main__":
    # Load .env if using dotenv in constants.py and it hasn't loaded automatically
    from dotenv import load_dotenv
    load_dotenv()  # Assuming .env is in root or constants.py will find it

    # Ensure constants.py initializes environment variables for GOOGLE_APPLICATION_CREDENTIALS if needed
    # This is usually done on import, but just in case.
    import twitter_post_analyzer.constants  # Just to ensure constants.py has executed

    asyncio.run(main())