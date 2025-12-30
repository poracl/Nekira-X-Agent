"""
Post Reply Agent
=================
Posts replies to Twitter using the Twitter API v2.
Handles media upload and tweet posting.
"""

import logging
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.function_tool import FunctionTool
from .tool.post_tweet_reply_tool import post_tweet_reply
from ...constants import MODEL

logger = logging.getLogger(__name__)

# Create the tweet posting tool
post_tweet_reply_function_tool = FunctionTool(
    func=post_tweet_reply,
)

post_reply_agent = LlmAgent(
    name="PostReplyAgent",
    model="gemini-2.5-flash-preview-05-20",
    description="Posts replies. Retrieves ALL necessary data (target tweet ID, reply text, image path) from 'image_generation_results' in session.state. MUST call its tool.",
    tools=[post_tweet_reply_function_tool],
    instruction="""## Role
You are the *PostReplyAgent*. Your task is to post a reply using data fully bundled by `ImageGeneratorAgent` and stored in `session.state.image_generation_results`.
Immediately call the `post_tweet_reply` tool with this data.

**State Logging:** You MUST log your current state and key decisions using "Agent State:" prefix.

## Process

**Step 1: Retrieve and Parse Bundled Data**
    a. Agent State: Reading bundled data from `session.state.image_generation_results`.
    b. Let `results_json_str = session.state.get('image_generation_results', '{}')`.
    c. Parse `results_json_str` into a dictionary `parsed_results`.
       If parsing fails OR `parsed_results` is empty OR not isinstance(parsed_results, dict):
           Agent State: Critical error parsing `image_generation_results`.
           Return JSON error: `{"status": "error", "message": "Failed to get bundled data for posting from image_generation_results."}`. STOP.

    d. Let `tweet_id_val = parsed_results.get('main_post_id_to_reply_to')`.
    e. Let `text_to_post_val = parsed_results.get('final_reply_text')`.
    f. Let `image_file_path_val = parsed_results.get('final_generated_image_path')`. // Can be null
    g. Let `image_outcome_msg = parsed_results.get('image_generation_outcome_message', '')`. // For logging

**Step 2: Validate Essential Data for Posting**
    a. IF `tweet_id_val` is null OR (isinstance(tweet_id_val, str) and tweet_id_val.strip() == ""):
        Agent State: Critical error - `main_post_id_to_reply_to` is missing or empty in the bundled data.
        Return JSON error: `{"status": "error", "message": "Missing target tweet ID in data from ImageGeneratorAgent."}`. STOP.
    b. IF `text_to_post_val` is null OR (isinstance(text_to_post_val, str) and text_to_post_val.strip() == ""):
        Agent State: Critical error - `final_reply_text` is missing or empty in the bundled data.
        Return JSON error: `{"status": "error", "message": "Missing text content for reply in data from ImageGeneratorAgent."}`. STOP.
    c. Agent State: All required data available.
       `tweet_id`: "[`tweet_id_val`]"
       `text_to_post` (first 50 chars): "[`text_to_post_val[:50]`]..."
       `image_file_path`: "[`image_file_path_val`]"
       `image_generation_status_from_prev_agent`: "[`image_outcome_msg`]"

**Step 3: Call the `post_tweet_reply` Tool**
    a. **You MUST now call the `post_tweet_reply` tool** with the gathered arguments:
        *   `tweet_id_to_reply_to`: `tweet_id_val`
        *   `reply_text`: `text_to_post_val`
        *   `image_path`: `image_file_path_val`
    b. Let `tool_output_dict = tool_call_result`.
       Agent State: `post_tweet_reply` tool completed. Output: `tool_output_dict`.

**Step 4: Return Tool's Output**
    a. Your final output MUST be the exact `tool_output_dict`.
    b. STOP.
"""
)