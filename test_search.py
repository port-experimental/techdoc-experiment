#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv
from custom_search import DocumentSearcher, DocumentationBot

def main():
    # Load environment
    load_dotenv()
    
    print("🔍 Testing Port Documentation Search")
    print("=" * 40)
    
    try:
        # Test search
        searcher = DocumentSearcher()
        print("✅ DocumentSearcher initialized")
        
        # Test simple search
        print("\n🔍 Testing search for 'getting started'...")
        results = searcher.search_entities("getting started")
        print(f"Results: {results}")
        
        # Test bot
        print("\n🤖 Testing DocumentationBot...")
        bot = DocumentationBot()
        response = bot.search_and_respond("getting started guide")
        print(f"Bot response: {response}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 