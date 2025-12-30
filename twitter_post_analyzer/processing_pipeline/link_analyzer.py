import os
import asyncio
import logging
from googleapiclient.discovery import build
from typing import Dict, Any, List
from .common_llm_utils import get_text_model  # Relative import

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(module)s - %(message)s")

GOOGLE_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

async def analyze_link_content(url: str, tweet_text_context: str) -> Dict[str, Any]:
    """
    Analyzes link content using Google Custom Search API.
    """
    print(f"CUSTOM_SEARCH: Analyzing URL: {url} (context: {tweet_text_context[:50]}...)")
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        error_msg = "Configuration error: GOOGLE_SEARCH_API_KEY or GOOGLE_CSE_ID not set."
        print(f"CUSTOM_SEARCH: {error_msg}")
        return {"summary": None, "search_results": [], "error": error_msg}

    search_results_list = []
    summary = None

    try:
        loop = asyncio.get_running_loop()
        service = await loop.run_in_executor(None, lambda: build("customsearch", "v1", developerKey=GOOGLE_API_KEY))
        
        query = f"{url}" 
        print(f"CUSTOM_SEARCH: Google query: {query}")

        response = await loop.run_in_executor(None, lambda: service.cse().list(q=query, cx=GOOGLE_CSE_ID, num=3).execute())

        if 'items' in response:
            for item in response['items']:
                search_results_list.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet")
                })
            
            text_model = get_text_model()
            if search_results_list and text_model:
                summary_snippets = [res.get('snippet', '') for res in search_results_list if res.get('snippet')]
                summary_prompt = f"Summarize the following search results about '{url}' in the context of '{tweet_text_context}':\n\n" + "\n\n".join(summary_snippets)
                summary_responses = await text_model.generate_content_async([summary_prompt])
                summary = summary_responses.text.strip()
            elif search_results_list:
                summary_parts = [res.get('snippet', '') for res in search_results_list if res.get('snippet')]
                summary = " ".join(summary_parts)[:500]
                if not summary:
                    summary = f"Found {len(search_results_list)} results for the link."
        else:
            print(f"CUSTOM_SEARCH: No results found for query '{query}'.")
            summary = f"Search for link {url} returned no results."

        print(f"CUSTOM_SEARCH: Results found: {len(search_results_list)}")
        return {"summary": summary, "search_results": search_results_list, "error": None}

    except Exception as e:
        error_msg = f"Error calling Google Custom Search API: {e}"
        print(f"CUSTOM_SEARCH: {error_msg}")
        return {"summary": None, "search_results": [], "error": error_msg}