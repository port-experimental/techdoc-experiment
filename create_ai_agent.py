#!/usr/bin/env python3

import os
import json
import requests
from dotenv import load_dotenv

class PortAIAgentManager:
    def __init__(self):
        load_dotenv()
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
        
        response = requests.post(auth_url, json=auth_data)
        if response.status_code == 200:
            self.token = response.json()['accessToken']
            print("✅ Successfully authenticated with Port API")
        else:
            raise Exception(f"Authentication failed: {response.text}")
    
    def get_headers(self):
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_ai_agent_access(self):
        """Test if AI agent features are available"""
        try:
            url = f"{self.base_url}/v1/agent/invoke"
            test_payload = {
                "prompt": "Hello, testing AI agent access",
                "context": {},
                "labels": {"test": "access_check"}
            }
            
            response = requests.post(url, json=test_payload, headers=self.get_headers())
            
            if response.status_code == 401:
                print("❌ AI Agents feature is not enabled for your account")
                print("   This feature is currently in closed beta.")
                print("   Please contact Port support to request access.")
                return False
            elif response.status_code in [200, 202]:
                print("✅ AI Agents feature is available!")
                print(f"   Test invocation created: {response.json()}")
                return True
            else:
                print(f"⚠️ Unexpected response: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing AI agent access: {e}")
            return False
    
    def create_documentation_agent(self):
        """Create a documentation AI agent (when access is available)"""
        print("🤖 Creating Documentation Assistant AI Agent...")
        
        # Load agent configuration
        with open('ai-agent-config.json', 'r') as f:
            config = json.load(f)
        
        agent_config = config['agentConfig']
        
        # Note: This is a conceptual implementation
        # The actual API endpoint for creating agents is not documented
        # This would need to be updated once the API is available
        
        agent_payload = {
            "name": agent_config["name"],
            "description": agent_config["description"],
            "purpose": agent_config["purpose"],
            "systemPrompt": agent_config["prompt"]["systemPrompt"],
            "conversationStarters": agent_config["prompt"]["conversationStarters"],
            "blueprints": agent_config["dataAccess"]["blueprints"],
            "properties": agent_config["dataAccess"]["properties"],
            "relations": agent_config["dataAccess"]["relations"],
            "settings": agent_config["settings"]
        }
        
        print("📋 Agent configuration prepared:")
        print(f"   Name: {agent_config['name']}")
        print(f"   Purpose: {agent_config['purpose']}")
        print(f"   Blueprints: {agent_config['dataAccess']['blueprints']}")
        print(f"   Properties: {agent_config['dataAccess']['properties']}")
        
        print("\n⚠️ Note: Agent creation API endpoint is not yet available.")
        print("   Once Port provides access to AI agents beta, this can be implemented.")
        
        return agent_payload
    
    def test_agent_invocation(self, prompt="What documentation do you have about API authentication?"):
        """Test invoking an AI agent with a sample prompt"""
        print(f"🔍 Testing AI agent with prompt: '{prompt}'")
        
        try:
            url = f"{self.base_url}/v1/agent/invoke"
            payload = {
                "prompt": prompt,
                "context": {
                    "user": "documentation_user",
                    "source": "api_test"
                },
                "labels": {
                    "type": "documentation_query",
                    "test": "true"
                }
            }
            
            response = requests.post(url, json=payload, headers=self.get_headers())
            
            if response.status_code == 200:
                result = response.json()
                print("✅ AI agent responded successfully!")
                print(f"   Response: {result}")
                return result
            else:
                print(f"❌ Agent invocation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error invoking AI agent: {e}")
            return None

def main():
    print("🤖 Port AI Agent Manager")
    print("=" * 40)
    
    try:
        manager = PortAIAgentManager()
        
        # Test AI agent access
        print("\n1. Testing AI Agent Access...")
        has_access = manager.test_ai_agent_access()
        
        if has_access:
            print("\n2. Creating Documentation Agent...")
            agent_config = manager.create_documentation_agent()
            
            print("\n3. Testing Agent Invocation...")
            result = manager.test_agent_invocation()
            
            if result:
                print("\n🎉 AI Agent setup completed successfully!")
        else:
            print("\n📝 Alternative Options:")
            print("   1. Use the custom search implementation in 'custom_search.py'")
            print("   2. Request access to AI agents beta from Port support")
            print("   3. Use the documentation bot with: python -c \"from custom_search import DocumentationBot; bot = DocumentationBot(); print(bot.search_and_respond('getting started'))\"")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure PORT_CLIENT_ID and PORT_CLIENT_SECRET are set")
        print("2. Run 'python setup_credentials.py' if needed")
        print("3. Check that your Port account has API access")

if __name__ == "__main__":
    main() 