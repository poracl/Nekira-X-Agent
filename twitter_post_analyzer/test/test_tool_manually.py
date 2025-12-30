import asyncio
import json
import os
from twitter_post_analyzer.sub_agents.tweet_data_preparation_agent.tools.tweet_processor_tool import process_tweet_and_generate_report

async def main():
    tweet_url = "https://x.com/Rainmaker1973/status/1927677430023569419"
    print(f"Attempting to process tweet_url: {tweet_url}")
    tool_result = None
    try:
        tool_result = await process_tweet_and_generate_report(tweet_url)
        print("\nTool Result (Returned Dictionary):")
        print(json.dumps(tool_result, indent=4, ensure_ascii=False))

        if tool_result and tool_result.get("status") == "success" and tool_result.get("data_file_path"):
            file_path = tool_result["data_file_path"]
            print(f"\nAttempting to verify saved JSON file: {file_path}")
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        saved_data = json.load(f)
                    print(f"Successfully read saved JSON file. Analysis ID from file: {saved_data.get('analysis_id')}")
                    # Optionally print more from saved_data if needed for verification
                except Exception as e:
                    print(f"Error reading or parsing saved JSON file: {e}")
            else:
                print(f"Error: Reported data_file_path does not exist: {file_path}")
        elif tool_result and tool_result.get("status") == "error":
            print(f"Tool reported an error: {tool_result.get('message')}")
        else:
            print("Tool did not return a successful status or data_file_path.")

    except Exception as e:
        print(f"\nAn error occurred during manual tool execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())