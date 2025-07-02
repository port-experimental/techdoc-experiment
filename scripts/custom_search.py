#!/usr/bin/env python3
"""
Interactive Command-Line Interface for the Port Documentation Assistant
"""

import logging
import os
import sys
from dotenv import load_dotenv

# Add src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from port_tools.clients.port_client import PortClient
from port_tools.search.bot import DocumentationBot

# Basic logging setup, focusing on the script's operations
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """Initializes the bot and starts the interactive command-line loop."""
    print("🚀 Port Documentation Assistant")
    print("Type 'quit' or 'exit' to stop.\n")
    
    load_dotenv()

    # Check for credentials
    CLIENT_ID = os.getenv('PORT_CLIENT_ID')
    CLIENT_SECRET = os.getenv('PORT_CLIENT_SECRET')

    if not CLIENT_ID or not CLIENT_SECRET:
        logging.error("PORT_CLIENT_ID and PORT_CLIENT_SECRET must be set in your .env file.")
        sys.exit(1)

    try:
        # Initialize the main components
        port_client = PortClient(CLIENT_ID, CLIENT_SECRET)
        bot = DocumentationBot(port_client)
        
        while True:
            try:
                query = input("❓ Ask me about Port documentation: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not query:
                    continue
                
                response = bot.search_and_respond(query)
                print(f"\n🤖\n{response}\n")
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
    
    except Exception as e:
        logging.error(f"Failed to initialize the documentation bot: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 