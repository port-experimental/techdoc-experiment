import logging
import os
from typing import List, Dict

import openai
import requests

from port_tools.clients.port_client import PortClient

logger = logging.getLogger(__name__)

class DocumentSearcher:
    """Enhanced document search implementation."""
    
    def __init__(self, port_client: PortClient):
        self.port_client = port_client
    
    def search_entities(self, search_term: str, limit: int = 25) -> Dict:
        """Search for documentation entities using Port's API."""
        url = f"{self.port_client.base_url}/v1/blueprints/documentation/entities/search"
        
        payload = {
            "query": {
                "combinator": "or",
                "rules": [
                    {"property": "$title", "operator": "contains", "value": search_term},
                    {"property": "content", "operator": "contains", "value": search_term},
                    {"property": "summary", "operator": "contains", "value": search_term},
                    {"property": "category", "operator": "contains", "value": search_term}
                ]
            },
            "limit": limit
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.port_client._get_headers())
            response.raise_for_status()
            data = response.json()
            return {
                'ok': True,
                'entities': data.get('entities', []),
            }
        except requests.HTTPError as e:
            logger.error(f"HTTP error during Port search for '{search_term}': {e.response.status_code} - {e.response.text}")
            return {'ok': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"An unexpected error occurred during Port search: {e}", exc_info=True)
            return {'ok': False, 'error': str(e)}

    def multi_strategy_search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Perform search using multiple strategies to find the best results."""
        all_results = []
        
        logger.info(f"Searching for: '{query}'...")
        results = self.search_entities(query)
        
        if results['ok']:
            all_results.extend(results['entities'][:max_results // 2])
        
        keywords = query.split()
        if len(keywords) > 1:
            for keyword in keywords:
                if len(keyword) > 3:
                    keyword_results = self.search_entities(keyword)
                    if keyword_results['ok']:
                        all_results.extend(keyword_results['entities'][:max_results // 4])
        
        seen_identifiers = set()
        unique_results = []
        for result in all_results:
            identifier = result.get('identifier', '')
            if identifier not in seen_identifiers:
                seen_identifiers.add(identifier)
                unique_results.append(result)
        
        logger.info(f"Found {len(unique_results)} unique results after multi-strategy search.")
        return unique_results[:max_results]


class DocumentationBot:
    """Documentation assistant bot."""
    
    def __init__(self, port_client: PortClient):
        self.searcher = DocumentSearcher(port_client)
        self.openai_client = None
        if os.getenv('OPENAI_API_KEY'):
            try:
                self.openai_client = openai.OpenAI()
                logger.info("OpenAI client initialized.")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")

    def search_and_respond(self, query: str) -> str:
        """Search for relevant documentation and formulate a response."""
        results = self.searcher.multi_strategy_search(query)
        
        if not results:
            return self._no_results_response(query)
        
        # For now, we build a simple text response.
        # OpenAI integration can be used here to generate a more conversational response.
        return self._build_response_from_results(query, results)

    def _build_response_from_results(self, query: str, results: List[Dict]) -> str:
        """Build a comprehensive text response from search results."""
        response = f"Based on your query '{query}', here are the most relevant documents I found:\n\n"
        
        for i, result in enumerate(results[:5], 1):
            title = result.get('title', 'Untitled')
            properties = result.get('properties', {})
            summary = properties.get('summary', 'No summary available.')
            category = properties.get('category', 'General')
            
            response += f"{i}. **{title}** (Category: {category})\n"
            response += f"   *Summary:* {summary[:250]}{'...' if len(summary) > 250 else ''}\n\n"
        
        if len(results) > 5:
            response += f"...and {len(results) - 5} more results were found.\n"
        
        return response

    def _no_results_response(self, query: str) -> str:
        """Generate a helpful response when no results are found."""
        return f"I couldn't find any specific documentation for '{query}'.\n\n"\
               "You could try:\n"\
               "- Using different or more general keywords.\n"\
               "- Checking for typos in your query.\n" 