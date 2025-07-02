#!/usr/bin/env python3
"""
Test Port AI Agent Script
This script invokes the AI agent with a series of test prompts to ensure it's responding correctly.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from port_tools.clients.port_client import PortClient
from port_tools.ai_agent.manager import AIAgentManager

def run_test_queries(agent_manager: AIAgentManager):
    """Runs a predefined set of test queries against the AI agent."""
    test_queries = [
        "What is this documentation about?",
        "How do I get started?",
        "Explain API authentication.",
        "Show me how to create a new blueprint.",
        "Find examples of using webhooks.",
        "How do I set up RBAC?"
    ]

    print("🧪 Running a series of test queries against the AI agent...")
    print("=" * 60)

    results = []
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Query: '{query}'")
        result = agent_manager.invoke(query, wait_for_completion=True)
        results.append({
            "query": query,
            "result": result,
            "success": result is not None and result.get('status') == 'completed'
        })
        time.sleep(1)  # Avoid hitting rate limits

    successful_queries = sum(1 for r in results if r['success'])
    print("\n📊 Test Summary:")
    print(f"   - Total queries tested: {len(test_queries)}")
    print(f"   - Successful responses: {successful_queries}")
    print(f"   - Success rate: {successful_queries / len(test_queries) * 100:.1f}%")
    
    if successful_queries > 0:
        print("\n🎉 AI Agent is responding to queries!")
    else:
        print("\n⚠️ AI Agent did not respond successfully to any queries.")
        print("   - Check if the agent was created successfully.")
        print("   - Ensure your Port account has the AI Agents feature enabled.")


def main():
    """Main function to test the AI agent."""
    print("🚀 Port AI Agent Tester")
    print("=" * 40)
    
    load_dotenv()
    
    client_id = os.getenv("PORT_CLIENT_ID")
    client_secret = os.getenv("PORT_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ Missing PORT_CLIENT_ID or PORT_CLIENT_SECRET in .env file.")
        print("   Please run 'python scripts/setup_credentials.py' first.")
        sys.exit(1)
        
    try:
        # Initialize the Port client and AI Agent Manager
        port_client = PortClient(client_id, client_secret)
        agent_manager = AIAgentManager(port_client)
        
        # Run a single, simple invocation first
        print("1. Running a simple health-check invocation...")
        initial_result = agent_manager.invoke("Hello, are you there?", wait_for_completion=False)
        
        if not initial_result:
            print("\n❌ The initial health-check invocation failed. Aborting further tests.")
            print("   Please check your credentials and ensure the AI agent feature is enabled for your account.")
            sys.exit(1)
        
        print("   ✅ Initial invocation was successful.")
        
        # Run the full suite of test queries
        print("\n2. Proceeding with the full test suite...")
        run_test_queries(agent_manager)

    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 