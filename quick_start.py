#!/usr/bin/env python3
"""
Quick Start Script for Port Documentation AI Agent Project
Tests connection and demonstrates basic functionality
"""

import os
import sys
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

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment configuration...")
    
    required_vars = ['PORT_CLIENT_ID', 'PORT_CLIENT_SECRET']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file or environment")
        return False
    
    print("✅ Environment variables configured")
    return True

def check_dependencies():
    """Check if required Python packages are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'requests', 'frontmatter', 'markdown', 
        'bs4', 'fuzzywuzzy', 'Levenshtein'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed")
    return True

def test_port_connection():
    """Test connection to Port API"""
    print("🔍 Testing Port API connection...")
    
    try:
        from ingest_docs import PortClient
        
        client_id = os.getenv('PORT_CLIENT_ID')
        client_secret = os.getenv('PORT_CLIENT_SECRET')
        
        client = PortClient(client_id, client_secret)
        
        if client.access_token:
            print("✅ Successfully connected to Port API")
            return True
        else:
            print("❌ Failed to authenticate with Port API")
            return False
            
    except Exception as e:
        print(f"❌ Port API connection failed: {e}")
        return False

def setup_sample_docs():
    """Create sample documentation for testing"""
    print("🔍 Setting up sample documentation...")
    
    docs_dir = Path("./sample_docs")
    docs_dir.mkdir(exist_ok=True)
    
    sample_files = {
        "getting-started.md": """# Getting Started

This is a sample getting started guide for testing the Port documentation AI agent.

## Prerequisites
- Port account
- API credentials
- Python environment

## Quick Setup
1. Install dependencies
2. Configure environment
3. Run ingestion script

Tags: guide, setup, beginner
""",
        "api-reference.md": """# API Reference

Sample API documentation for testing.

## Authentication
Use Bearer token authentication with your API key.

## Endpoints

### GET /entities
Retrieve entities from your catalog.

### POST /entities
Create new entities.

Tags: api, reference, endpoints
""",
        "troubleshooting.md": """# Troubleshooting

Common issues and solutions.

## Connection Issues
- Check your API credentials
- Verify network connectivity
- Review error logs

## Authentication Errors
- Ensure correct client ID and secret
- Check token expiration

Tags: troubleshooting, help, support
"""
    }
    
    for filename, content in sample_files.items():
        file_path = docs_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"✅ Created sample docs in {docs_dir}")
    return str(docs_dir)

def run_ingestion_test(docs_path):
    """Test documentation ingestion"""
    print("🔍 Testing documentation ingestion...")
    
    try:
        from ingest_docs import PortClient, DocumentIngester
        
        client_id = os.getenv('PORT_CLIENT_ID')
        client_secret = os.getenv('PORT_CLIENT_SECRET')
        
        port_client = PortClient(client_id, client_secret)
        ingester = DocumentIngester(port_client)
        
        # Setup blueprint
        if ingester.setup_blueprint():
            print("✅ Blueprint setup successful")
        else:
            print("❌ Blueprint setup failed")
            return False
        
        # Test ingestion
        count = ingester.ingest_directory(docs_path)
        print(f"✅ Successfully ingested {count} documents")
        return True
        
    except Exception as e:
        print(f"❌ Ingestion test failed: {e}")
        return False

def test_search():
    """Test documentation search functionality"""
    print("🔍 Testing search functionality...")
    
    try:
        from custom_search import DocumentSearcher, DocumentationBot
        
        # Use the updated classes (no parameters needed)
        searcher = DocumentSearcher()
        bot = DocumentationBot()
        
        # Test search
        test_query = "getting started"
        results = searcher.search_entities(test_query)
        
        if results['ok'] and results['total_results_found'] > 0:
            print(f"✅ Search test successful - found {results['total_results_found']} results")
            return True
        else:
            print(f"⚠️ Search test completed but found {results.get('total_results_found', 0)} results")
            if not results['ok']:
                print(f"Error: {results.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

def main():
    """Main quick start function"""
    print("🚀 Port Documentation AI Agent - Quick Start")
    print("=" * 60)
    
    # Load .env file if it exists
    load_env_file()
    
    # Environment check
    if not check_environment():
        print("\n❌ Environment check failed. Please configure your environment first.")
        sys.exit(1)
    
    # Dependencies check
    if not check_dependencies():
        print("\n❌ Dependencies check failed. Please install required packages.")
        sys.exit(1)
    
    # Port connection test
    if not test_port_connection():
        print("\n❌ Port connection failed. Please check your credentials.")
        sys.exit(1)
    
    # Setup sample docs
    docs_path = setup_sample_docs()
    
    # Test ingestion
    if not run_ingestion_test(docs_path):
        print("\n❌ Ingestion test failed.")
        sys.exit(1)
    
    # Test search
    if not test_search():
        print("\n⚠️ Search test had issues, but ingestion worked.")
    
    print("\n🎉 Quick start completed successfully!")
    print("\nNext steps:")
    print("1. Add your real documentation to the docs folder")
    print("2. Run: python ingest_docs.py")
    print("3. Test with: python custom_search.py")
    print("4. If you have AI agent beta access, configure it in Port UI")
    print("\nSee IMPLEMENTATION_GUIDE.md for detailed instructions.")

if __name__ == "__main__":
    main() 