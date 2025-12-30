"""
Tweet Data Extractor
=====================
Fetches tweet data from Twitter API, downloads media files,
and structures the data for analysis.
"""

import re
import os
import json
import aiohttp
import asyncio
import logging
from urllib.parse import urlparse
import aiofiles
from typing import Dict, Any, List
from pathlib import Path

# Configuration
API_KEY = os.getenv("TWITTERAPI_KEY")
MAX_VIDEO_DURATION_SECONDS = 120

if not API_KEY:
    logging.error("TWITTERAPI_KEY is missing")

# Define project root and media cache directory
PROJECT_ROOT_DIR = Path(__file__).resolve().parent.parent
MEDIA_CACHE_BASE_DIR = PROJECT_ROOT_DIR / "media" / "analysis_media_cache"


def get_tweet_id_from_url(url: str) -> str | None:
    """Extract tweet ID from a Twitter/X URL."""
    url = url.strip()
    parsed = urlparse(url)
    
    if parsed.netloc not in ["x.com", "twitter.com"]:
        logging.error(f"Unsupported domain in URL: {parsed.netloc}")
        return None
    
    path_parts = parsed.path.split('/')
    if len(path_parts) >= 4 and path_parts[2] == "status":
        return path_parts[3]
    
    logging.error(f"Invalid URL format: {url}")
    return None


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text content."""
    url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»""'']))"
    return [match[0] for match in re.findall(url_regex, text)]


async def download_media_internal(
    session: aiohttp.ClientSession,
    media_list: List[Dict],
    tweet_id: str,
    media_type_prefix: str,
    analysis_id: str
) -> List[Dict]:
    """Download media files from a tweet and save locally."""
    saved_files = []
    media_cache_dir = MEDIA_CACHE_BASE_DIR / analysis_id
    os.makedirs(media_cache_dir, exist_ok=True)

    for index, media in enumerate(media_list):
        media_url = None
        file_ext = ".jpg"
        
        # Handle video media
        if media.get("type") == "video" and "video_info" in media:
            duration_millis = media["video_info"].get("duration_millis", 0)
            duration_seconds = duration_millis / 1000
            
            if duration_seconds > MAX_VIDEO_DURATION_SECONDS:
                logging.info(
                    f"Skipping video in tweet {tweet_id}: duration {duration_seconds:.2f}s exceeds limit {MAX_VIDEO_DURATION_SECONDS}s"
                )
                continue
            
            variants = media["video_info"].get("variants", [])
            mp4_variants = sorted(
                [v for v in variants if v.get("content_type") == "video/mp4"],
                key=lambda x: x.get("bitrate", 0),
                reverse=True
            )
            
            if mp4_variants:
                media_url = mp4_variants[0]["url"]
                file_ext = ".mp4"
            else:
                logging.warning(f"No mp4 variant found for video in tweet {tweet_id}")
                continue
        else:
            # Handle image media
            media_url = media.get("media_url_https") or media.get("media_url")
            if media_url:
                parsed_url = urlparse(media_url)
                file_ext = os.path.splitext(parsed_url.path)[1] or ".jpg"

        if not media_url:
            continue

        file_name = f"{media_type_prefix}_{tweet_id}_{index}{file_ext}"
        file_path = media_cache_dir / file_name

        try:
            async with session.get(media_url) as response:
                response.raise_for_status()
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(await response.read())
                
                saved_files.append({
                    "url": media_url,
                    "local_path": str(file_path),
                    "type": media.get("type", "unknown")
                })
                logging.info(f"Downloaded media: {media_url} -> {file_path}")
        
        except Exception as e:
            logging.error(f"Error downloading media {media_url}: {e}")

    return saved_files


async def get_tweet_details_internal(
    session: aiohttp.ClientSession,
    tweet_id: str
) -> Dict | None:
    """Fetch tweet details from the Twitter API."""
    url = "https://api.twitterapi.io/twitter/tweets"
    headers = {"X-API-Key": API_KEY}
    params = {"tweet_ids": tweet_id}

    try:
        async with session.get(url, headers=headers, params=params) as response:
            status_code = response.status
            response_text = await response.text()

            if status_code != 200:
                logging.error(f"HTTP {status_code} error fetching tweet {tweet_id}: {response_text}")
                return None

            data = await response.json()
            if data.get("status") != "success" or not data.get("tweets"):
                logging.error(f"Error fetching tweet {tweet_id}: {data.get('message', 'Unknown error')}")
                return None
            
            return data["tweets"][0]
    
    except aiohttp.ClientError as e:
        if "429" in str(e):
            logging.warning("Rate limit reached (429). Waiting 60 seconds before retry...")
            await asyncio.sleep(60)
            return await get_tweet_details_internal(session, tweet_id)
        
        logging.error(f"Request error for tweet {tweet_id}: {e}")
        return None


async def process_single_tweet(
    session: aiohttp.ClientSession,
    tweet_id: str,
    media_prefix: str,
    analysis_id: str,
    parent_post_id: str = None
) -> Dict | None:
    """Process a single tweet: fetch data and download media."""
    tweet = await get_tweet_details_internal(session, tweet_id)
    
    if not tweet:
        logging.error(f"Failed to fetch tweet data for {tweet_id}")
        return None

    # Get media list from both entities and extendedEntities
    media_list = (
        tweet.get("entities", {}).get("media", []) +
        tweet.get("extendedEntities", {}).get("media", [])
    )
    
    # Deduplicate media by URL
    media_list = list({
        media.get("media_url_https") or media.get("media_url"): media
        for media in media_list
    }.values())
    
    downloaded_media = await download_media_internal(
        session, media_list, tweet_id, media_prefix, analysis_id
    )

    extracted_urls = extract_urls(tweet.get("text", ""))

    # Get quoted post ID if exists
    quoted_post_id = None
    if tweet.get("quoted_tweet") and isinstance(tweet["quoted_tweet"], dict):
        quoted_post_id = tweet["quoted_tweet"].get("id")

    tweet_data = {
        "post_id": tweet_id,
        "parent_post_id": parent_post_id,
        "quoted_post_id": quoted_post_id,
        "replied_to_post_id": tweet.get("inReplyToId") if tweet.get("isReply") else None,
        "text": tweet.get("text", ""),
        "author": tweet.get("author", {}).get("userName", "Unknown"),
        "created_at": tweet.get("createdAt", ""),
        "extracted_urls": extracted_urls,
        "downloaded_media": downloaded_media,
        "raw_data": tweet
    }

    return tweet_data


async def fetch_and_prepare_tweet_data(tweet_url: str) -> Dict[str, Any]:
    """
    Main function to fetch tweet data, including quoted/replied tweets,
    download media, and extract URLs for further analysis.
    """
    if not API_KEY:
        return {
            "status": "error",
            "message": "TWITTERAPI_KEY is not set in environment variables.",
            "analysis_id": None
        }

    try:
        tweet_id = get_tweet_id_from_url(tweet_url)
        if not tweet_id:
            return {
                "status": "error",
                "message": "Invalid tweet URL provided.",
                "analysis_id": None
            }

        analysis_id = tweet_id
        all_posts_data = []
        all_posts_structured = []

        async with aiohttp.ClientSession() as session:
            # Fetch main post
            main_post_data = await process_single_tweet(
                session, tweet_id,
                media_prefix="post",
                analysis_id=analysis_id,
                parent_post_id=None
            )
            
            if not main_post_data:
                return {
                    "status": "error",
                    "message": "Failed to retrieve main tweet data.",
                    "analysis_id": analysis_id
                }
            
            all_posts_data.append(main_post_data)

            # Fetch quoted post if exists
            if main_post_data["quoted_post_id"]:
                quoted_data = await process_single_tweet(
                    session, main_post_data["quoted_post_id"],
                    media_prefix="quoted",
                    analysis_id=analysis_id,
                    parent_post_id=tweet_id
                )
                if quoted_data:
                    all_posts_data.append(quoted_data)

            # Fetch replied-to post if exists
            if main_post_data["replied_to_post_id"]:
                replied_to_data = await process_single_tweet(
                    session, main_post_data["replied_to_post_id"],
                    media_prefix="replied_to",
                    analysis_id=analysis_id,
                    parent_post_id=tweet_id
                )
                
                if replied_to_data:
                    all_posts_data.append(replied_to_data)
                    
                    # Also fetch quoted post in the reply
                    if replied_to_data["quoted_post_id"]:
                        quoted_in_reply_data = await process_single_tweet(
                            session, replied_to_data["quoted_post_id"],
                            media_prefix="quoted_in_reply",
                            analysis_id=analysis_id,
                            parent_post_id=replied_to_data["post_id"]
                        )
                        if quoted_in_reply_data:
                            all_posts_data.append(quoted_in_reply_data)

        # Structure the data for analysis
        for post in all_posts_data:
            media_to_analyze = []
            for media_item in post["downloaded_media"]:
                media_to_analyze.append({
                    "type": media_item["type"],
                    "local_path": media_item["local_path"],
                    "original_url": media_item["url"],
                    "tweet_text_context": post["text"]
                })

            links_to_analyze = []
            for url_item in post["extracted_urls"]:
                parsed_url = urlparse(url_item)
                # Exclude Twitter/X links
                if (parsed_url.netloc not in ["x.com", "twitter.com", "www.x.com", "www.twitter.com"]
                    and "t.co" not in parsed_url.netloc):
                    links_to_analyze.append({
                        "url": url_item,
                        "tweet_text_context": post["text"]
                    })

            all_posts_structured.append({
                "post_id": post["post_id"],
                "parent_post_id": post["parent_post_id"],
                "quoted_post_id": post["quoted_post_id"],
                "text": post["text"],
                "author": post["author"],
                "created_at": post["created_at"],
                "media_to_analyze": media_to_analyze,
                "links_to_analyze": links_to_analyze
            })

        return {
            "status": "success",
            "message": "Tweet data extracted and structured successfully.",
            "analysis_id": analysis_id,
            "all_posts_structured": all_posts_structured
        }

    except aiohttp.ClientError as e:
        return {
            "status": "error",
            "message": f"Network error fetching tweet data: {e}",
            "analysis_id": None
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"An unexpected error occurred: {e}",
            "analysis_id": None
        }