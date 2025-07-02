#!/usr/bin/env python3
"""
Cleanup Script for Port Documentation Entities
Removes entities from the 'documentation' blueprint.
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

class PortEntityCleaner:
    """A utility to clean up entities from a Port blueprint."""
    
    def __init__(self, port_client: PortClient):
        self.port_client = port_client

    def get_all_entities(self, blueprint_id: str) -> list:
        """Get all entities for a specific blueprint."""
        url = f"{self.port_client.base_url}/v1/blueprints/{blueprint_id}/entities"
        try:
            response = requests.get(url, headers=self.port_client._get_headers())
            response.raise_for_status()
            return response.json().get("entities", [])
        except requests.HTTPError as e:
            logging.error(f"Failed to get entities for blueprint '{blueprint_id}': {e.response.text}")
            return []

    def delete_entity(self, blueprint_id: str, entity_id: str) -> bool:
        """Deletes a single entity from a blueprint."""
        url = f"{self.port_client.base_url}/v1/blueprints/{blueprint_id}/entities/{entity_id}"
        try:
            response = requests.delete(url, headers=self.port_client._get_headers())
            # 404 means it's already gone, which is a success for our purposes
            if response.status_code == 404:
                return True
            response.raise_for_status()
            return True
        except requests.HTTPError as e:
            logging.error(f"Failed to delete entity '{entity_id}': {e.response.text}")
            return False

    def delete_all_entities(self, blueprint_id: str) -> int:
        """Deletes all entities for a given blueprint and returns the count."""
        logging.info(f"Fetching all entities for blueprint '{blueprint_id}' to begin cleanup...")
        entities = self.get_all_entities(blueprint_id)
        if not entities:
            logging.info(f"No entities found for blueprint '{blueprint_id}'. Nothing to delete.")
            return 0
        
        logging.info(f"Found {len(entities)} entities. Proceeding with deletion...")
        deleted_count = 0
        for entity in entities:
            entity_id = entity.get("identifier")
            if entity_id:
                if self.delete_entity(blueprint_id, entity_id):
                    logging.info(f"  - Deleted entity: {entity_id}")
                    deleted_count += 1
                else:
                    logging.warning(f"  - Failed to delete entity: {entity_id}")
        return deleted_count

def main():
    """Main cleanup function."""
    print("🧹 Port Documentation Cleanup Utility")
    print("=" * 40)
    
    load_dotenv()
    
    CLIENT_ID = os.getenv('PORT_CLIENT_ID')
    CLIENT_SECRET = os.getenv('PORT_CLIENT_SECRET')
    
    if not CLIENT_ID or not CLIENT_SECRET:
        logging.error("Port credentials (PORT_CLIENT_ID, PORT_CLIENT_SECRET) not found in .env file.")
        sys.exit(1)
        
    try:
        port_client = PortClient(CLIENT_ID, CLIENT_SECRET)
        cleaner = PortEntityCleaner(port_client)
        
        blueprint_to_clean = "documentation"
        
        # Confirmation step
        confirm = input(f"This will delete ALL entities in the '{blueprint_to_clean}' blueprint.\n"
                        "This action cannot be undone.\n"
                        "Are you sure you want to continue? (y/N): ").strip().lower()

        if confirm != 'y':
            print("Cleanup aborted by user.")
            sys.exit(0)
            
        deleted_count = cleaner.delete_all_entities(blueprint_to_clean)
        
        print("\n🎉 Cleanup Summary 🎉")
        print(f"Successfully deleted {deleted_count} entities from the '{blueprint_to_clean}' blueprint.")
        
    except Exception as e:
        logging.error(f"An unexpected error occurred during cleanup: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 