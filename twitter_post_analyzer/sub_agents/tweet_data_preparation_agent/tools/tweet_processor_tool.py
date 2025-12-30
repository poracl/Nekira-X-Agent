# --- Start of file: twitter_post_analyzer/sub_agents/tweet_data_preparation_agent/tools/tweet_processor_tool.py ---

import asyncio
import json
import os
from typing import Dict, Any
from pathlib import Path
from google.adk.tools import FunctionTool  # Import FunctionTool

# Relative imports for processing_pipeline modules
from ....processing_pipeline.data_extractor import fetch_and_prepare_tweet_data
from ....processing_pipeline.image_analyzer import analyze_image_content
from ....processing_pipeline.video_analyzer import analyze_video_content
from ....processing_pipeline.link_analyzer import analyze_link_content
from ....processing_pipeline.report_compiler import compile_tweet_report_markdown

# Function remains unchanged (no ToolContext in arguments, returns dictionary)
async def process_tweet_and_generate_report(tweet_url: str) -> Dict[str, Any]:
    """
    Python function (ADK Tool Logic): Extracts tweet data, analyzes content, generates a Markdown report,
    saves all collected data to JSON and Markdown files.
    Returns a dictionary with paths, key information, AND the Markdown report content.
    """
    print(f"PROCESS_TWEET_TOOL_LOGIC: Starting processing URL: {tweet_url}")

    extracted_data_result = await fetch_and_prepare_tweet_data(tweet_url)
    if extracted_data_result.get("status") == "error":
        print(f"PROCESS_TWEET_TOOL_LOGIC: Extraction error - {extracted_data_result.get('message')}")
        return {
            "status": "error",
            "message": f"Data extraction failed: {extracted_data_result.get('message')}",
            "analysis_id": extracted_data_result.get("analysis_id"),
            "main_post_id_to_reply_to": extracted_data_result.get("main_post_id_to_reply_to"),
            "final_markdown_report_path": None,
            "analysis_data_json_path": None,
            "report_markdown_content": None
        }

    analysis_id = extracted_data_result.get("analysis_id", "unknown_id")
    main_post_id_to_reply_to = extracted_data_result.get("main_post_id_to_reply_to", analysis_id)

    print(f"PROCESS_TWEET_TOOL_LOGIC: Data extracted for ID: {analysis_id}. Main Post ID: {main_post_id_to_reply_to}")

    all_image_analysis_results = []
    all_video_analysis_results = []
    all_link_analysis_results = []

    for post_data in extracted_data_result.get("all_posts_structured", []):
        post_id = post_data["post_id"]
        tweet_text_for_context = post_data["text"]
        for media_item in post_data.get("media_to_analyze", []):
            if media_item["type"] == "photo":
                img_res = await analyze_image_content(media_item['local_path'], tweet_text_for_context)
                all_image_analysis_results.append({"post_id": post_id, **media_item, "analysis": img_res})
            elif media_item["type"] == "video":
                vid_res = await analyze_video_content(media_item['local_path'], tweet_text_for_context)
                all_video_analysis_results.append({"post_id": post_id, **media_item, "analysis": vid_res})
        for link_item in post_data.get("links_to_analyze", []):
            link_res = await analyze_link_content(link_item['url'], link_item['tweet_text_context'])
            all_link_analysis_results.append({"post_id": post_id, **link_item, "analysis": link_res})

    comprehensive_data = {
        "analysis_id": analysis_id,
        "tweet_url": tweet_url,
        "full_extracted_data": extracted_data_result,
        "all_image_analyses_conducted": all_image_analysis_results,
        "all_video_analyses_conducted": all_video_analysis_results,
        "all_link_analyses_conducted": all_link_analysis_results,
    }

    base_dir_path = Path("twitter_post_analyzer/media/analysis_media_cache")
    analysis_data_dir_path = base_dir_path / str(analysis_id)
    analysis_data_dir_path.mkdir(parents=True, exist_ok=True)
    
    data_file_path_obj = analysis_data_dir_path / "analysis_data.json"
    markdown_file_path_obj = analysis_data_dir_path / f"report_{analysis_id}.md"
    data_file_path_str = str(data_file_path_obj)
    markdown_file_path_str = str(markdown_file_path_obj)

    try:
        with open(data_file_path_obj, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_data, f, ensure_ascii=False, indent=4)
        print(f"PROCESS_TWEET_TOOL_LOGIC: JSON data saved: {data_file_path_str}")
    except IOError as e:
        print(f"PROCESS_TWEET_TOOL_LOGIC: Error saving JSON: {e}")
        return {
            "status": "error", "message": f"Error saving JSON: {e}",
            "analysis_id": analysis_id, "main_post_id_to_reply_to": main_post_id_to_reply_to,
            "data_file_path": None, "final_markdown_report_path": None, "report_markdown_content": None
        }

    markdown_report_content_str = None
    try:
        markdown_report_content_str = await compile_tweet_report_markdown(
            extracted_data_result, all_image_analysis_results,
            all_video_analysis_results, all_link_analysis_results
        )
        with open(markdown_file_path_obj, 'w', encoding='utf-8') as f:
            f.write(markdown_report_content_str)
        print(f"PROCESS_TWEET_TOOL_LOGIC: Markdown report saved: {markdown_file_path_str}")
    except Exception as e:
        print(f"PROCESS_TWEET_TOOL_LOGIC: Error generating/saving Markdown: {e}")
        return {
            "status": "partial_success", "message": f"JSON saved, Markdown error: {e}",
            "analysis_id": analysis_id, "main_post_id_to_reply_to": main_post_id_to_reply_to,
            "data_file_path": data_file_path_str, "final_markdown_report_path": None,
            "report_markdown_content": None
        }

    return {
        "status": "success",
        "message": f"Data saved to JSON ({data_file_path_str}) and Markdown ({markdown_file_path_str}). Report content included.",
        "analysis_id": analysis_id,
        "main_post_id_to_reply_to": main_post_id_to_reply_to,
        "data_file_path": data_file_path_str,
        "final_markdown_report_path": markdown_file_path_str,
        "report_markdown_content": markdown_report_content_str
    }

# Create FunctionTool instance
# Using the name process_tweet_fully_tool as expected by the agent
process_tweet_fully_tool = FunctionTool(
    func=process_tweet_and_generate_report
)
# --- End of file: twitter_post_analyzer/sub_agents/tweet_data_preparation_agent/tools/tweet_processor_tool.py ---