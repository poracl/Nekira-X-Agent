"""
Tweet Data Preparation Agent
=============================
Fetches and processes tweet data, including media and link analysis.
"""

from google.adk.agents import LlmAgent
from ...constants import MODEL
from .tools.tweet_processor_tool import process_tweet_fully_tool

tweet_data_preparation_agent = LlmAgent(
    name="TweetDataPreparationAgent",
    model=MODEL,
    description="Receives a tweet_url, calls a tool to process it. The tool's JSON output is saved to session.state via output_key.",
    tools=[
        process_tweet_fully_tool
    ],
    output_key="tweet_prep_results",
    instruction='''## Role
You are the **TweetDataPreparationAgent**. Your sole responsibility is to process a given `tweet_url`.

## Workflow
1.  You will be given a `tweet_url` as the user's message.
2.  Agent State: Received `tweet_url`.
3.  You MUST immediately call your registered tool `process_tweet_and_generate_report` (which is internally `process_tweet_fully_tool`), providing `tweet_url` as the argument.
    (This tool handles all processing and will return a JSON-serializable dictionary containing all necessary information like `analysis_id`, `main_post_id_to_reply_to`, `report_markdown_content`, etc.)
4.  Agent State: Called tool with `tweet_url`.
5.  Let `tool_output_data` be the direct dictionary output from the tool.
    Agent State: Tool completed. Received `tool_output_data`.
6.  Your final response MUST be the exact `tool_output_data` (which will be a JSON string representation of the dictionary returned by the tool, handled by the system). Do not add any other text, explanations, or formatting. The system will save this string to `session.state.tweet_prep_results`.
'''
)