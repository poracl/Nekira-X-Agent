# twitter_post_analyzer/agent.py
"""
Main Agent Orchestrator
========================
Sequential pipeline that coordinates all sub-agents to process
tweets and generate responses.
"""

from google.adk.agents import SequentialAgent

# Import sub-agents
from .sub_agents.tweet_data_preparation_agent.agent import tweet_data_preparation_agent
from .sub_agents.character_agent.agent import character_agent
from .sub_agents.image_generator_agent.agent import image_generator_agent
from .sub_agents.post_reply_agent.agent import post_reply_agent
from .sub_agents.prompt_formatter_agent.agent import prompt_formatter_agent

# Create the main orchestrator using SequentialAgent
twitter_post_analyzer = SequentialAgent(
    name="twitter_post_analyzer_workflow",
    description="Sequentially processes a tweet: data preparation, character response, image generation (optional), and posting the reply.",
    sub_agents=[
        tweet_data_preparation_agent,
        character_agent,
        prompt_formatter_agent,
        image_generator_agent,
        post_reply_agent
    ],
    # The flow of data and conditional logic is handled within the sub-agents
    # by reading from and writing to session.state.
    # The final output will be the output of the last agent (post_reply_agent).
)

# Root agent for ADK Runner
root_agent = twitter_post_analyzer