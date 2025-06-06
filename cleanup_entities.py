#!/usr/bin/env python3
"""
Cleanup Script for Port Documentation Entities
Removes existing entities and recreates blueprint to fix schema issues
"""

import os
import sys
import requests
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

class PortCleanup:
    """Port API cleanup utilities"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.getport.io/v1"
        self.access_token = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Port API"""
        auth_url = f"{self.base_url}/auth/access_token"
        data = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        }
        
        response = requests.post(auth_url, json=data)
        response.raise_for_status()
        self.access_token = response.json()["accessToken"]
    
    def _get_headers(self):
        """Get authenticated headers"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def get_all_entities(self, blueprint_id: str):
        """Get all entities for a blueprint"""
        url = f"{self.base_url}/blueprints/{blueprint_id}/entities"
        response = requests.get(url, headers=self._get_headers())
        
        if response.status_code == 200:
            return response.json().get("entities", [])
        else:
            print(f"Failed to get entities: {response.text}")
            return []
    
    def delete_entity(self, blueprint_id: str, entity_id: str):
        """Delete a specific entity"""
        url = f"{self.base_url}/blueprints/{blueprint_id}/entities/{entity_id}"
        response = requests.delete(url, headers=self._get_headers())
        
        return response.status_code in [200, 204, 404]  # 404 means already deleted
    
    def delete_all_entities(self, blueprint_id: str):
        """Delete all entities for a blueprint"""
        entities = self.get_all_entities(blueprint_id)
        deleted_count = 0
        
        for entity in entities:
            entity_id = entity.get("identifier")
            if entity_id and self.delete_entity(blueprint_id, entity_id):
                deleted_count += 1
                print(f"✅ Deleted entity: {entity_id}")
            else:
                print(f"❌ Failed to delete entity: {entity_id}")
        
        return deleted_count
    
    def delete_blueprint(self, blueprint_id: str):
        """Delete a blueprint"""
        url = f"{self.base_url}/blueprints/{blueprint_id}"
        response = requests.delete(url, headers=self._get_headers())
        
        if response.status_code in [200, 204]:
            print(f"✅ Deleted blueprint: {blueprint_id}")
            return True
        elif response.status_code == 404:
            print(f"ℹ️ Blueprint {blueprint_id} doesn't exist")
            return True
        else:
            print(f"❌ Failed to delete blueprint: {response.text}")
            return False

def main():
    """Main cleanup function"""
    print("🧹 Port Documentation Cleanup")
    print("=" * 40)
    
    # Load environment
    load_env_file()
    
    client_id = os.getenv('PORT_CLIENT_ID')
    client_secret = os.getenv('PORT_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Port credentials not found. Run setup_credentials.py first.")
        return
    
    try:
        cleanup = PortCleanup(client_id, client_secret)
        
        # Delete all documentation entities
        print("🗑️ Deleting existing documentation entities...")
        deleted_count = cleanup.delete_all_entities("documentation")
        print(f"✅ Deleted {deleted_count} entities")
        
        # Optionally delete and recreate blueprint
        recreate = input("Do you want to recreate the blueprint? (y/N): ").strip().lower()
        if recreate == 'y':
            print("🗑️ Deleting documentation blueprint...")
            cleanup.delete_blueprint("documentation")
            
            print("🏗️ Recreating blueprint...")
            # Import and run blueprint creation
            from ingest_docs import PortClient, DocumentIngester
            port_client = PortClient(client_id, client_secret)
            ingester = DocumentIngester(port_client)
            
            if ingester.setup_blueprint():
                print("✅ Blueprint recreated successfully!")
            else:
                print("❌ Failed to recreate blueprint")
        
        print("\n🎉 Cleanup completed!")
        print("You can now run: python quick_start.py")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

if __name__ == "__main__":
    main() 