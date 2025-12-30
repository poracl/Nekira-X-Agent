import asyncio
import os
from google.adk.runners import InMemoryRunner
from google.adk.agents import LlmAgent
from .sub_agents.extract_twitter_data.agent import extract_twitter_data_agent

async def test_extractor_agent():
    print("Starting test for extract_twitter_data_agent...")

    # Create an InMemoryRunner for the extractor_agent
    runner = InMemoryRunner(agent=extract_twitter_data_agent)

    # Create a session for the agent
    session = runner.session_service.create_session(
        app_name=extract_twitter_data_agent.name, user_id="test_user"
    )

    # Provide a sample Twitter URL for testing
    # IMPORTANT: Replace this with a real Twitter URL for actual testing
    # Make sure the URL is accessible and not rate-limited by Twitter API.
    test_tweet_url = "https://x.com/TwitterDev/status/1460323737035677698" # Example URL, replace with a valid one

    print(f"Sending test tweet URL: {test_tweet_url}")

    # Run the agent with the test URL
    # The agent's instruction will guide it to use the tool
    for event in runner.run(
        user_id=session.user_id, session_id=session.id, new_message=test_tweet_url
    ):
        # Process events from the agent
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"Agent Response: {part.text}")
                if part.tool_code:
                    print(f"Agent used tool: {part.tool_code}")
                if part.tool_response:
                    print(f"Tool Response: {part.tool_response}")
        else:
            print(f"Received event: {event}")

    print("Test for extract_twitter_data_agent completed.")

if __name__ == "__main__":
    asyncio.run(test_extractor_agent())