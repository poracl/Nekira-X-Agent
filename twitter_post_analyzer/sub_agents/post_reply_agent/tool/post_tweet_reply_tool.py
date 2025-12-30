"""
Post Tweet Reply Tool
======================
Posts replies to Twitter using the Twitter API v2.
Handles media upload via v1.1 API.
"""

import logging
import os
import httpx
import asyncio
from requests_oauthlib import OAuth1Session
from typing import Dict, Any, Optional

from twitter_post_analyzer.constants import (
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET
)

logger = logging.getLogger(__name__)


async def _upload_media_to_twitter(image_path: str, oauth: OAuth1Session) -> Optional[str]:
    """
    Upload media to Twitter and return the media_id_string.
    Uses Twitter API v1.1 for media upload.
    """
    logger.info(f"POST_REPLY_TOOL: Uploading media: {image_path}")
    media_upload_url = "https://upload.twitter.com/1.1/media/upload.json"

    try:
        with open(image_path, 'rb') as image_file:
            loop = asyncio.get_running_loop()

            # Simple upload for images
            files_for_upload = {'media': image_file}
            upload_response = await loop.run_in_executor(
                None,
                lambda: oauth.post(media_upload_url, files=files_for_upload)
            )
            upload_response.raise_for_status()

            uploaded_media_data = upload_response.json()
            media_id_string = uploaded_media_data.get('media_id_string')

            if media_id_string:
                logger.info(f"POST_REPLY_TOOL: Media uploaded successfully. Media ID: {media_id_string}")
                return media_id_string
            else:
                logger.error(f"POST_REPLY_TOOL: Media upload failed. Response: {upload_response.text}")
                return None

    except FileNotFoundError:
        logger.error(f"POST_REPLY_TOOL: Image file not found: {image_path}")
        return None
    except httpx.HTTPStatusError as e:
        logger.error(f"POST_REPLY_TOOL: HTTP error during media upload: {e.response.status_code}")
        return None
    except Exception as e:
        logger.exception(f"POST_REPLY_TOOL: Unexpected error during media upload: {e}")
        return None


async def post_tweet_reply(
    tweet_id_to_reply_to: str,
    reply_text: str,
    image_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Post a reply to a specific tweet using Twitter API v2.
    Optionally attach an image to the reply.
    
    Args:
        tweet_id_to_reply_to: ID of the tweet to reply to
        reply_text: Text content of the reply
        image_path: Optional local path to an image to attach
    
    Returns:
        Dictionary with status and tweet details or error message
    """
    logger.info(f"POST_REPLY_TOOL: Posting reply to tweet ID: {tweet_id_to_reply_to}")
    logger.info(f"POST_REPLY_TOOL: Image path: {image_path}")

    # Validate credentials
    if not all([TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, 
                TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
        logger.error("POST_REPLY_TOOL: Twitter API credentials are incomplete.")
        return {"status": "error", "message": "Twitter API credentials missing."}

    # Create OAuth session
    oauth = OAuth1Session(
        TWITTER_CONSUMER_KEY,
        client_secret=TWITTER_CONSUMER_SECRET,
        resource_owner_key=TWITTER_ACCESS_TOKEN,
        resource_owner_secret=TWITTER_ACCESS_TOKEN_SECRET
    )

    # Build payload
    payload = {
        "text": reply_text,
        "reply": {
            "in_reply_to_tweet_id": tweet_id_to_reply_to
        }
    }

    media_id_string: Optional[str] = None
    posted_image_url: Optional[str] = None

    # Upload media if provided
    if image_path:
        media_id_string = await _upload_media_to_twitter(image_path, oauth)
        if media_id_string:
            payload["media"] = {"media_ids": [media_id_string]}
            posted_image_url = f"media_id_{media_id_string}_posted"
        else:
            logger.warning(f"POST_REPLY_TOOL: Failed to upload media. Posting without image.")

    # Post the tweet
    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: oauth.post("https://api.twitter.com/2/tweets", json=payload)
        )

        response.raise_for_status()
        response_data = response.json()

        if "data" in response_data and "id" in response_data["data"]:
            logger.info(f"POST_REPLY_TOOL: Successfully posted reply: {response_data['data']['id']}")
            return {
                "status": "success",
                "tweet_id": response_data["data"]["id"],
                "text": response_data["data"]["text"],
                "posted_image_url": posted_image_url
            }
        else:
            logger.error(f"POST_REPLY_TOOL: Failed to post reply. Response: {response_data}")
            return {
                "status": "error",
                "message": response_data.get("detail", "Unknown error from Twitter API.")
            }

    except httpx.HTTPStatusError as e:
        logger.error(f"POST_REPLY_TOOL: HTTP error: {e.response.status_code} - {e.response.text}")
        return {"status": "error", "message": f"HTTP error: {e.response.status_code}"}
    except httpx.RequestError as e:
        logger.error(f"POST_REPLY_TOOL: Request error: {e}")
        return {"status": "error", "message": f"Request error: {str(e)}"}
    except Exception as e:
        logger.exception(f"POST_REPLY_TOOL: Unexpected error: {e}")
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}