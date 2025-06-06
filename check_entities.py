#!/usr/bin/env python3

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def main():
    # Get credentials
    client_id = os.getenv('PORT_CLIENT_ID')
    client_secret = os.getenv('PORT_CLIENT_SECRET')
    base_url = os.getenv('PORT_BASE_URL', 'https://api.getport.io')
    
    # Authenticate
    auth_url = f"{base_url}/v1/auth/access_token"
    auth_data = {"clientId": client_id, "clientSecret": client_secret}
    auth_response = requests.post(auth_url, json=auth_data)
    token = auth_response.json()['accessToken']
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get entities
    print("📋 Fetching entities from documentation blueprint...")
    url = f"{base_url}/v1/blueprints/documentation/entities"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        entities = data.get('entities', [])
        print(f"✅ Found {len(entities)} entities")
        
        if entities:
            print("\n📄 First entity structure:")
            first_entity = entities[0]
            print(f"Identifier: {first_entity.get('identifier')}")
            print(f"Title: {first_entity.get('title')}")
            print(f"Properties: {list(first_entity.get('properties', {}).keys())}")
            print(f"Full entity: {first_entity}")
        else:
            print("❌ No entities found")
    else:
        print(f"❌ Error fetching entities: {response.status_code} - {response.text}")

if __name__ == "__main__":
    main() 