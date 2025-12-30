"""
Image Generator Agent
======================
Generates AI images using Replicate API when the character decides an image is needed.
Bundles all data for the PostReplyAgent.
"""

import logging
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.function_tool import FunctionTool
from ...constants import MODEL
from .tool.image_generator_tool import generate_image_via_replicate_sdk

logger = logging.getLogger(__name__)

# Create the image generation tool
replicate_image_generation_tool = FunctionTool(
    func=generate_image_via_replicate_sdk,
)

image_generator_agent = LlmAgent(
    name="ImageGeneratorAgent",
    model="gemini-2.5-flash-preview-05-20",
    description="Receives image gen params. If needed, calls tool. Bundles ALL data for PostReplyAgent: reply text, image path, AND target tweet ID.",
    tools=[
        replicate_image_generation_tool
    ],
    output_key="image_generation_results",
    instruction="""## Your Role: Image Generation Executor & Final Data Bundler for Posting

Your only job is to look at the `"generate_this_image"` flag from the `ImagePromptFormatterAgent` output in the context and follow one of two exact scenarios.

**SCENARIOS (Follow one and only one):**

---
**SCENARIO A: If the context contains the JSON from `ImagePromptFormatterAgent` with `"generate_this_image": true`**

1.  **You MUST immediately call the `generate_image_via_replicate_sdk` tool.**
2.  Use the following arguments for the tool, finding their values in the `ImagePromptFormatterAgent`'s JSON from the context:
    - `prompt`: the value of `actual_image_prompt_for_generation`.
    - `image_name_prefix`: the value of `image_name_prefix`.
    - `aspect_ratio`: "1:1"
    - `output_format`: "jpg"
3.  The tool will return a dictionary. Let's call it `tool_result`.
4.  Your final response MUST be a single JSON object constructed exactly like this, filling in the values:
    ```json
    {
      "main_post_id_to_reply_to": "Find this value in the [TweetDataPreparationAgent] output in the context.",
      "final_reply_text": "Find this value in the [ImagePromptFormatterAgent] output in the context.",
      "final_generated_image_path": "Use the 'path' value from the tool_result.",
      "image_generation_outcome_message": "Use the 'message' value from the tool_result."
    }
    ```

---
**SCENARIO B: If the context contains the JSON from `ImagePromptFormatterAgent` with `"generate_this_image": false`**

1.  **DO NOT call any tool.**
2.  Your final response MUST be a single JSON object constructed exactly like this, filling in the values from the context:
    ```json
    {
      "main_post_id_to_reply_to": "Find this value in the [TweetDataPreparationAgent] output in the context.",
      "final_reply_text": "Find this value in the [ImagePromptFormatterAgent] output in the context.",
      "final_generated_image_path": null,
      "image_generation_outcome_message": "Find the 'formatter_status_message' value in the [ImagePromptFormatterAgent] output in the context."
    }
    ```
---

**Your entire response must be ONLY the final JSON object from the scenario you followed.**
"""
)