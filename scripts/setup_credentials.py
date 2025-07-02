#!/usr/bin/env python3
"""
Port Credentials Setup Script
Helps you configure your Port API credentials for all scripts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Conditional import for testing
try:
    from port_tools.clients.port_client import PortClient
except ImportError:
    PortClient = None

def get_port_credentials_guide():
    """Display guide for getting Port credentials"""
    print("""
🔑 How to Get Your Port API Credentials
========================================

1. Log into your Port organization at https://app.getport.io
2. Navigate to Settings (⚙️ icon in the bottom left)
3. Go to 'Developers' section
4. Click on 'API Keys' 
5. Click 'Create API Key'
6. Give it a name (e.g., 'Documentation Ingestion')
7. Copy the Client ID and Client Secret

⚠️  IMPORTANT: Save the Client Secret immediately - you won't be able to see it again!

""")

def setup_environment_file():
    """Create or update the .env file with user input."""
    print("📝 Setting up your .env configuration file...")
    
    # Get Port credentials
    port_client_id = input("Enter your Port Client ID: ").strip()
    port_client_secret = input("Enter your Port Client Secret: ").strip()
    
    if not port_client_id or not port_client_secret:
        print("❌ Port Client ID and Client Secret are required.")
        return False
    
    # Get optional credentials for remote ingestion
    print("\n(Optional) For fetching READMEs from remote Git providers, provide the following credentials.")
    print("You can leave any of these blank and add them to the .env file later.")
    
    github_token = input("Enter your GitHub PAT: ").strip()
    gitlab_url = input("Enter your GitLab URL (e.g., https://gitlab.com): ").strip()
    gitlab_token = input("Enter your GitLab PAT: ").strip()
    azure_url = input("Enter your Azure DevOps Org URL (e.g., https://dev.azure.com/my-org): ").strip()
    azure_token = input("Enter your Azure DevOps PAT: ").strip()

    # Create .env file content
    env_lines = [
        "# Port API Credentials",
        f"PORT_CLIENT_ID={port_client_id}",
        f"PORT_CLIENT_SECRET={port_client_secret}",
        "\n# --- Credentials for Remote README Ingestion (Optional) ---",
        f"GITHUB_TOKEN={github_token}",
        f"GITLAB_URL={gitlab_url}",
        f"GITLAB_TOKEN={gitlab_token}",
        f"AZURE_DEVOPS_URL={azure_url}",
        f"AZURE_DEVOPS_TOKEN={azure_token}"
    ]
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write("\n".join(env_lines))
        
        print("\n✅ Successfully created/updated .env file!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def test_credentials():
    """Test the configured Port credentials by attempting to authenticate."""
    print("🧪 Testing your Port API credentials...")
    
    if PortClient is None:
        print("❌ Could not import PortClient. Cannot test credentials.")
        return False
        
    load_dotenv()
    client_id = os.getenv('PORT_CLIENT_ID')
    client_secret = os.getenv('PORT_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Credentials not found in environment. Please run setup first.")
        return False
    
    try:
        # Attempt to initialize the client, which triggers authentication
        PortClient(client_id, client_secret)
        print("✅ Credentials are valid! Successfully authenticated with Port API.")
        return True
    except Exception as e:
        print(f"❌ Authentication failed. Please check your credentials. Error: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Port Ingestion Framework - Credentials Setup")
    print("=" * 50)
    
    # Check if .env file exists and if credentials work
    if Path('.env').exists():
        print("📄 Found existing .env file.")
        if test_credentials():
            reconfigure = input("Your credentials are valid. Do you want to re-configure them anyway? (y/N): ").strip().lower()
            if reconfigure != 'y':
                print("👋 Exiting setup.")
                return
        else:
            print("⚠️ Existing credentials seem invalid. Let's reconfigure...")
    
    get_port_credentials_guide()
    
    if setup_environment_file():
        print("\nNow testing the new credentials...")
        if test_credentials():
            print("\n🎉 Setup completed successfully!")
            print("You can now run the ingestion and utility scripts.")
        else:
            print("\n⚠️ Setup finished, but the new credentials failed the test.")
            print("Please double-check the values in your .env file.")

if __name__ == "__main__":
    main() 