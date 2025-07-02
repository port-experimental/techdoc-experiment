#!/usr/bin/env python3
"""
Port Status Check Script
Connects to Port and verifies that the documentation blueprint contains entities.
"""

import logging
import os
import sys
import requests
from dotenv import load_dotenv

# Add src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from port_tools.clients.port_client import PortClient

# Basic logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_status_check(port_client: PortClient, blueprint_id: str = "documentation"):
    """
    Connects to Port, fetches a sample of entities from a blueprint,
    and prints a status report.
    """
    logging.info(f"Attempting to fetch entities from blueprint: '{blueprint_id}'...")
    
    try:
        # Use the client's search method
        data = port_client.search_entities(blueprint_id, limit=5)
        
        entities = data.get('entities', [])
        total_count = data.get('meta', {}).get('totalCount', len(entities))

        print("\n✅ --- Port Status Report --- ✅")
        print(f"Successfully connected to Port API at {port_client.base_url}")
        
        if total_count > 0:
            print(f"Found {total_count} total entities in the '{blueprint_id}' blueprint.")
            print("\nSample of entities found:")
            for i, entity in enumerate(entities):
                title = entity.get('title', 'Untitled')
                identifier = entity.get('identifier', 'No Identifier')
                print(f"  {i+1}. {title} (Identifier: {identifier})")
        else:
            print(f"Blueprint '{blueprint_id}' exists but contains no entities.")
            
        print("\nStatus check complete. System appears to be operational.")
        print("------------------------------")

    except requests.HTTPError as e:
        print("\n❌ --- Port Status Report --- ❌")
        if e.response.status_code == 404:
            print(f"Error: The blueprint '{blueprint_id}' was not found.")
            print("Please run an ingestion script first to create it.")
        else:
            print(f"An HTTP error occurred: {e.response.status_code} - {e.response.text}")
        print("------------------------------")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)

def main():
    """Main function to run the status check."""
    load_dotenv()
    
    CLIENT_ID = os.getenv('PORT_CLIENT_ID')
    CLIENT_SECRET = os.getenv('PORT_CLIENT_SECRET')
    
    if not CLIENT_ID or not CLIENT_SECRET:
        logging.error("Port credentials (PORT_CLIENT_ID, PORT_CLIENT_SECRET) not found in .env file.")
        sys.exit(1)
        
    try:
        port_client = PortClient(CLIENT_ID, CLIENT_SECRET)
        run_status_check(port_client)
        
    except Exception as e:
        logging.error(f"Failed to initialize Port Client: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 