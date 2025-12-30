#!/usr/bin/env python3
"""
Nekira Agent - Main Entry Point
================================
An autonomous AI agent that analyzes tweets and generates intelligent responses.

Usage:
    python main.py <tweet_url>
    python main.py <tweet_url> --character nekira
    python main.py <tweet_url> --dry-run
    python main.py --list-characters
"""

import argparse
import asyncio
import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("nekira-agent")


def print_banner():
    """Print the Nekira Agent banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ███╗   ██╗███████╗██╗  ██╗██╗██████╗  █████╗                ║
║   ████╗  ██║██╔════╝██║ ██╔╝██║██╔══██╗██╔══██╗               ║
║   ██╔██╗ ██║█████╗  █████╔╝ ██║██████╔╝███████║               ║
║   ██║╚██╗██║██╔══╝  ██╔═██╗ ██║██╔══██╗██╔══██║               ║
║   ██║ ╚████║███████╗██║  ██╗██║██║  ██║██║  ██║               ║
║   ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝               ║
║                        AGENT                                  ║
║                                                               ║
║   Autonomous AI Agent powered by Google Agent SDK             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def list_characters():
    """List all available character profiles."""
    from config import list_available_characters, CHARACTERS_DIR
    
    characters = list_available_characters()
    
    print("\n📁 Available Characters:")
    print(f"   Location: {CHARACTERS_DIR}\n")
    
    if not characters:
        print("   No characters found. Create one using the template!")
        print(f"   Copy: {CHARACTERS_DIR}/_template -> {CHARACTERS_DIR}/your_character")
        return
    
    for char in characters:
        profile_path = CHARACTERS_DIR / char / "profile.md"
        status = "✅" if profile_path.exists() else "⚠️"
        print(f"   {status} {char}")
    
    print(f"\n💡 Use: python main.py <tweet_url> --character <name>")


def main():
    """Main entry point for Nekira Agent."""
    parser = argparse.ArgumentParser(
        description="Nekira Agent - Autonomous AI Twitter Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py https://x.com/user/status/123456789
  python main.py https://x.com/user/status/123456789 --character nekira
  python main.py https://x.com/user/status/123456789 --dry-run
  python main.py --list-characters
        """
    )
    
    parser.add_argument(
        "tweet_url",
        nargs="?",
        help="URL of the tweet to analyze and respond to"
    )
    
    parser.add_argument(
        "--character", "-c",
        default=os.getenv("ACTIVE_CHARACTER", "nekira"),
        help="Character profile to use (default: nekira)"
    )
    
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Analyze and generate response without posting to Twitter"
    )
    
    parser.add_argument(
        "--no-image",
        action="store_true",
        help="Skip image generation even if the agent decides to create one"
    )
    
    parser.add_argument(
        "--list-characters", "-l",
        action="store_true",
        help="List all available character profiles"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Handle --list-characters
    if args.list_characters:
        print_banner()
        list_characters()
        return 0
    
    # Require tweet_url for main operation
    if not args.tweet_url:
        parser.error("tweet_url is required unless using --list-characters")
    
    # Set verbose logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print banner and info
    print_banner()
    
    print(f"🤖 Character: {args.character}")
    print(f"🔗 Tweet: {args.tweet_url}")
    print(f"{'🧪 DRY RUN MODE - Will NOT post to Twitter' if args.dry_run else '✅ LIVE MODE - Will post to Twitter'}")
    print(f"{'🖼️  Image generation: DISABLED' if args.no_image else '🖼️  Image generation: AUTO'}")
    print("-" * 60)
    
    # Set environment variables for the agent
    os.environ["ACTIVE_CHARACTER"] = args.character
    
    if args.dry_run:
        os.environ["DRY_RUN_MODE"] = "true"
    
    if args.no_image:
        os.environ["SKIP_IMAGE_GENERATION"] = "true"
    
    try:
        # Import agent after setting environment
        from twitter_post_analyzer.agent import root_agent
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        
        print("\n🚀 Starting agent pipeline...")
        
        # Create session service and runner
        session_service = InMemorySessionService()
        runner = Runner(
            agent=root_agent,
            session_service=session_service,
            app_name="nekira-agent"
        )
        
        # Run the agent
        async def run_agent():
            session = await session_service.create_session(
                app_name="nekira-agent",
                user_id="user"
            )
            
            async for event in runner.run_async(
                session_id=session.id,
                user_id="user",
                new_message=args.tweet_url
            ):
                if hasattr(event, 'content'):
                    logger.info(f"Agent output: {event.content}")
            
            return session
        
        result = asyncio.run(run_agent())
        
        print("\n" + "=" * 60)
        print("✅ Agent pipeline completed!")
        
        if args.dry_run:
            print("📝 Note: This was a dry run. No tweet was posted.")
        
        return 0
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure all dependencies are installed: pip install -r requirements.txt")
        return 1
    except Exception as e:
        logger.exception(f"Error running agent: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
