#!/usr/bin/env python3
"""
Port Credentials Setup Script
Helps you configure your Port API credentials
"""

import os
import sys
from pathlib import Path

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
6. Give it a name (e.g., 'Documentation AI Agent')
7. Copy the Client ID and Client Secret

⚠️  IMPORTANT: Save the Client Secret immediately - you won't be able to see it again!

""")

def setup_environment_file():
    """Create .env file with user input"""
    print("📝 Setting up your environment configuration...")
    
    # Get credentials from user
    client_id = input("Enter your Port Client ID: ").strip()
    client_secret = input("Enter your Port Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Both Client ID and Client Secret are required!")
        return False
    
    # Ask for optional OpenAI key
    openai_key = input("Enter your OpenAI API key (optional, press Enter to skip): ").strip()
    
    # Ask for docs path
    docs_path = input("Enter path to your documentation (default: ./docs): ").strip()
    if not docs_path:
        docs_path = "./docs"
    
    # Create .env file content
    env_content = f"""# Port API Credentials
PORT_CLIENT_ID={client_id}
PORT_CLIENT_SECRET={client_secret}

# Documentation source path
DOCS_PATH={docs_path}
"""
    
    if openai_key:
        env_content += f"\n# OpenAI API Key for enhanced AI responses\nOPENAI_API_KEY={openai_key}\n"
    
    # Write to .env file
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"✅ Created .env file successfully!")
        print(f"📁 Docs path set to: {docs_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def setup_environment_variables():
    """Alternative: Set environment variables for current session"""
    print("🔧 Setting environment variables for current session...")
    
    client_id = input("Enter your Port Client ID: ").strip()
    client_secret = input("Enter your Port Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Both Client ID and Client Secret are required!")
        return False
    
    os.environ['PORT_CLIENT_ID'] = client_id
    os.environ['PORT_CLIENT_SECRET'] = client_secret
    os.environ['DOCS_PATH'] = './docs'
    
    print("✅ Environment variables set for current session!")
    print("⚠️  Note: These will be lost when you close the terminal.")
    print("💡 Consider creating a .env file for permanent storage.")
    return True

def test_credentials():
    """Test the configured credentials"""
    print("🧪 Testing your Port API credentials...")
    
    try:
        # Try to import and test
        sys.path.append('.')
        from ingest_docs import PortClient
        
        client_id = os.getenv('PORT_CLIENT_ID')
        client_secret = os.getenv('PORT_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            print("❌ Credentials not found in environment")
            return False
        
        client = PortClient(client_id, client_secret)
        
        if client.access_token:
            print("✅ Credentials are valid! Successfully authenticated with Port API")
            return True
        else:
            print("❌ Authentication failed - please check your credentials")
            return False
            
    except Exception as e:
        print(f"❌ Credential test failed: {e}")
        return False

def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    if env_file.exists():
        print("📄 Loading existing .env file...")
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        return True
    return False

def main():
    """Main setup function"""
    print("🚀 Port API Credentials Setup")
    print("=" * 40)
    
    # Check if .env file exists
    if Path('.env').exists():
        print("📄 Found existing .env file")
        load_env_file()
        
        if test_credentials():
            print("🎉 Your credentials are already configured and working!")
            return
        else:
            print("⚠️  Existing credentials seem invalid. Let's reconfigure...")
    
    # Show guide
    get_port_credentials_guide()
    
    # Ask user preference
    while True:
        choice = input("""
Choose setup method:
1. Create .env file (recommended)
2. Set environment variables for current session
3. Show credential guide again
4. Test existing credentials
5. Exit

Enter choice (1-5): """).strip()
        
        if choice == '1':
            if setup_environment_file():
                load_env_file()
                if test_credentials():
                    print("\n🎉 Setup completed successfully!")
                    print("You can now run: python quick_start.py")
                    break
        
        elif choice == '2':
            if setup_environment_variables():
                if test_credentials():
                    print("\n🎉 Setup completed successfully!")
                    print("You can now run: python quick_start.py")
                    break
        
        elif choice == '3':
            get_port_credentials_guide()
        
        elif choice == '4':
            load_env_file()
            test_credentials()
        
        elif choice == '5':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main() 