#!/usr/bin/env python3
"""
Custom Documentation Search Implementation
Alternative to Port AI Agent when beta access is not available
"""

import os
import json
import re
from typing import List, Dict, Optional, Tuple
import requests
from dataclasses import dataclass
from fuzzywuzzy import fuzz
import openai  # Optional: for enhanced AI responses
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

@dataclass
class SearchResult:
    """Search result with relevance scoring"""
    entity_id: str
    title: str
    content: str
    summary: str
    category: str
    tags: List[str]
    relevance_score: float
    file_path: str

class PortClient:
    def __init__(self):
        self.client_id = os.getenv('PORT_CLIENT_ID')
        self.client_secret = os.getenv('PORT_CLIENT_SECRET')
        self.base_url = os.getenv('PORT_BASE_URL', 'https://api.getport.io')
        self.token = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Port API"""
        auth_url = f"{self.base_url}/v1/auth/access_token"
        auth_data = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        }
        
        try:
            response = requests.post(auth_url, json=auth_data)
            response.raise_for_status()
            self.token = response.json().get('accessToken')
            return True
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    def get_headers(self):
        """Get headers with authentication token"""
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

class DocumentSearcher:
    """Enhanced document search implementation"""
    
    def __init__(self):
        self.port_client = PortClient()
    
    def search_entities(self, search_term, limit=25):
        """Search for documentation entities using Port's API"""
        # Search within the documentation blueprint specifically
        url = f"{self.port_client.base_url}/v1/blueprints/documentation/entities/search"
        
        # Use the correct Port API format for blueprint-specific search
        payload = {
            "query": {
                "combinator": "or",
                "rules": [
                    {
                        "property": "$title",
                        "operator": "contains",
                        "value": search_term
                    },
                    {
                        "property": "content",
                        "operator": "contains", 
                        "value": search_term
                    },
                    {
                        "property": "summary",
                        "operator": "contains",
                        "value": search_term
                    },
                    {
                        "property": "category",
                        "operator": "contains",
                        "value": search_term
                    }
                ]
            },
            "limit": limit
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.port_client.get_headers())
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'ok': True,
                    'entities': data.get('entities', []),
                    'total_results_found': len(data.get('entities', []))
                }
            else:
                return {
                    'ok': False,
                    'error': f"HTTP {response.status_code}",
                    'message': response.text
                }
                
        except Exception as e:
            return {
                'ok': False,
                'error': 'request_failed',
                'message': str(e)
            }
    
    def similarity_search(self, search_term, limit=10):
        """Search using a simpler approach for now"""
        # For now, use regular search as similarity search
        # The API doesn't seem to have a separate similarity endpoint available
        return self.search_entities(search_term, limit)
    
    def multi_strategy_search(self, query, max_results=10):
        """Perform search using multiple strategies"""
        all_results = []
        
        # Strategy 1: Direct search
        print(f"🔍 Searching for: '{query}'...")
        results = self.search_entities(query)
        
        if results['ok']:
            all_results.extend(results['entities'][:max_results//2])
            print(f"✅ Found {len(results['entities'])} results from direct search")
        else:
            print(f"❌ Direct search failed: {results.get('message', 'Unknown error')}")
        
        # Strategy 2: Keyword-based search
        keywords = query.split()
        if len(keywords) > 1:
            for keyword in keywords:
                if len(keyword) > 3:  # Only search for meaningful keywords
                    keyword_results = self.search_entities(keyword)
                    if keyword_results['ok']:
                        all_results.extend(keyword_results['entities'][:max_results//4])
        
        # Remove duplicates based on identifier
        seen_identifiers = set()
        unique_results = []
        for result in all_results:
            identifier = result.get('identifier', '')
            if identifier not in seen_identifiers:
                seen_identifiers.add(identifier)
                unique_results.append(result)
        
        return unique_results[:max_results]

class DocumentationBot:
    """Documentation assistant bot implementation"""
    
    def __init__(self):
        self.searcher = DocumentSearcher()
        self.openai_client = None
        
        if os.getenv('OPENAI_API_KEY'):
            openai.api_key = os.getenv('OPENAI_API_KEY')
            self.openai_client = openai
    
    def search_and_respond(self, query):
        """Search for relevant documentation and provide a response"""
        print(f"\n🤖 Processing query: {query}")
        
        # Perform multi-strategy search
        results = self.searcher.multi_strategy_search(query)
        
        if not results:
            return self._no_results_response(query)
        
        # Build response from results
        response = self._build_response(query, results)
        return response
    
    def _build_response(self, query, results):
        """Build a comprehensive response from search results"""
        response = f"Based on your query about '{query}', here's what I found:\n\n"
        
        for i, result in enumerate(results[:5], 1):
            title = result.get('title', 'Untitled')
            properties = result.get('properties', {})
            summary = properties.get('summary', '')
            category = properties.get('category', 'General')
            
            response += f"{i}. **{title}** ({category})\n"
            if summary:
                response += f"   {summary[:200]}{'...' if len(summary) > 200 else ''}\n"
            response += "\n"
        
        if len(results) > 5:
            response += f"...and {len(results) - 5} more results found.\n\n"
        
        # Add related suggestions
        categories = set()
        tags = set()
        for result in results:
            props = result.get('properties', {})
            if props.get('category'):
                categories.add(props['category'])
            if props.get('tags'):
                tags.update(props['tags'] if isinstance(props['tags'], list) else [])
        
        if categories:
            response += f"**Related categories:** {', '.join(list(categories)[:3])}\n"
        if tags:
            response += f"**Related topics:** {', '.join(list(tags)[:5])}\n"
        
        return response
    
    def _no_results_response(self, query):
        """Generate response when no results are found"""
        return f"""I couldn't find specific documentation for '{query}'. Here are some suggestions:

1. Try using different keywords or synonyms
2. Check if you're using the correct terminology
3. Browse the main documentation categories:
   - Getting Started
   - Build Your Software Catalog
   - Actions and Automations
   - AI Agents
   - Search and Query

Would you like me to search for something else?"""

def main():
    """Interactive command-line interface"""
    print("🚀 Port Documentation Assistant")
    print("Type 'quit' or 'exit' to stop\n")
    
    bot = DocumentationBot()
    
    while True:
        try:
            query = input("❓ Ask me about Port documentation: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not query:
                print("Please enter a question or search term.\n")
                continue
            
            response = bot.search_and_respond(query)
            print(f"\n{response}\n")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 