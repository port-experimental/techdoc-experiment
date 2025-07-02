#!/usr/bin/env python3
"""
Create Port AI Agent Script
This script creates or updates the Port AI agent based on the `ai-agent-config.json` file.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from port_tools.clients.port_client import PortClient
from port_tools.ai_agent.manager import AIAgentManager

def main():
    """Main function to create the AI agent."""
    print("🚀 Port AI Agent Creator")
    print("=" * 40)
    
    load_dotenv()
    
    client_id = os.getenv("PORT_CLIENT_ID")
    client_secret = os.getenv("PORT_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ Missing PORT_CLIENT_ID or PORT_CLIENT_SECRET in .env file.")
        print("   Please run 'python scripts/setup_credentials.py' first.")
        sys.exit(1)
        
    try:
        # Initialize the Port client
        port_client = PortClient(client_id, client_secret)
        
        # Initialize the AI Agent Manager
        agent_manager = AIAgentManager(port_client)
        
        # Attempt to create the agent
        success = agent_manager.create_agent()
        
        if success:
            print("\n🎉 Agent creation process finished.")
            print("   You can now test the agent using 'python scripts/test_ai_agent.py'.")
        else:
            print("\n⚠️ Agent creation process encountered an error.")
            
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 