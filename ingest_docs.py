#!/usr/bin/env python3
"""
Port Documentation Ingestion Script
Ingests markdown files into Port as documentation entities
"""

import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import requests
from dataclasses import dataclass
import markdown
from bs4 import BeautifulSoup
import frontmatter
from dotenv import load_dotenv

@dataclass
class DocMetadata:
    """Metadata extracted from documentation"""
    title: str
    content: str
    summary: str
    category: str
    tags: List[str]
    file_path: str
    word_count: int
    reading_time: int
    last_updated: str

class PortClient:
    """Client for interacting with Port API"""
    
    def __init__(self, client_id: str, client_secret: str, base_url: str = "https://api.getport.io/v1"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
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
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def create_blueprint(self, blueprint_data: Dict) -> bool:
        """Create or update documentation blueprint"""
        url = f"{self.base_url}/blueprints"
        
        # Check if blueprint exists
        get_response = requests.get(
            f"{url}/{blueprint_data['identifier']}", 
            headers=self._get_headers()
        )
        
        if get_response.status_code == 200:
            # Update existing blueprint
            response = requests.put(
                f"{url}/{blueprint_data['identifier']}", 
                json=blueprint_data,
                headers=self._get_headers()
            )
        else:
            # Create new blueprint
            response = requests.post(url, json=blueprint_data, headers=self._get_headers())
        
        if response.status_code in [200, 201]:
            print(f"✅ Blueprint '{blueprint_data['identifier']}' created/updated successfully")
            return True
        else:
            print(f"❌ Failed to create blueprint: {response.text}")
            return False
    
    def create_entity(self, blueprint_id: str, entity_data: Dict) -> bool:
        """Create or update documentation entity"""
        url = f"{self.base_url}/blueprints/{blueprint_id}/entities"
        
        # Use upsert to handle existing entities
        params = {"upsert": "true", "merge": "true"}
        
        response = requests.post(
            url, 
            json=entity_data, 
            headers=self._get_headers(),
            params=params
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Entity '{entity_data.get('identifier', 'unknown')}' created/updated")
            return True
        else:
            print(f"❌ Failed to create entity: {response.text}")
            return False

class DocumentProcessor:
    """Process markdown documents and extract metadata"""
    
    @staticmethod
    def extract_frontmatter(content: str) -> Tuple[Dict, str]:
        """Extract frontmatter from markdown content"""
        try:
            post = frontmatter.loads(content)
            return post.metadata, post.content
        except:
            return {}, content
    
    @staticmethod
    def extract_title(content: str, file_path: str) -> str:
        """Extract title from content or filename"""
        # Try to find H1 header
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()
        
        # Fall back to filename
        return Path(file_path).stem.replace('-', ' ').replace('_', ' ').title()
    
    @staticmethod
    def generate_summary(content: str, max_length: int = 200) -> str:
        """Generate summary from content"""
        # Convert markdown to text
        html = markdown.markdown(content)
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        # Get first paragraph or sentences up to max_length
        sentences = text.split('.')
        summary = ""
        for sentence in sentences:
            if len(summary + sentence) < max_length:
                summary += sentence + "."
            else:
                break
        
        return summary.strip() or text[:max_length] + "..."
    
    @staticmethod
    def categorize_document(file_path: str, content: str) -> str:
        """Categorize document based on path and content"""
        path_lower = file_path.lower()
        content_lower = content.lower()
        
        # Path-based categorization
        if 'api' in path_lower:
            return 'API Reference'
        elif 'guide' in path_lower or 'tutorial' in path_lower:
            return 'Guide'
        elif 'example' in path_lower:
            return 'Example'
        elif 'concept' in path_lower:
            return 'Concept'
        
        # Content-based categorization
        if 'endpoint' in content_lower or 'request' in content_lower:
            return 'API Reference'
        elif 'step' in content_lower and ('1.' in content or '2.' in content):
            return 'Tutorial'
        elif 'example' in content_lower:
            return 'Example'
        
        return 'Documentation'
    
    @staticmethod
    def extract_tags(content: str, file_path: str) -> List[str]:
        """Extract tags from content and file path"""
        tags = set()
        
        # Extract from file path
        path_parts = Path(file_path).parts
        for part in path_parts:
            if part not in ['.', '..', 'docs', 'documentation']:
                tags.add(part.lower())
        
        # Extract from content (look for common tech terms)
        tech_terms = [
            'api', 'rest', 'graphql', 'webhook', 'authentication', 'authorization',
            'database', 'blueprint', 'entity', 'property', 'relation', 'scorecard',
            'python', 'javascript', 'typescript', 'json', 'yaml', 'docker',
            'kubernetes', 'aws', 'azure', 'gcp', 'integration'
        ]
        
        content_lower = content.lower()
        for term in tech_terms:
            if term in content_lower:
                tags.add(term)
        
        return list(tags)
    
    @classmethod
    def process_file(cls, file_path: str) -> Optional[DocMetadata]:
        """Process a single markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract frontmatter
            frontmatter_data, main_content = cls.extract_frontmatter(content)
            
            # Extract metadata
            title = frontmatter_data.get('title') or cls.extract_title(main_content, file_path)
            summary = frontmatter_data.get('description') or cls.generate_summary(main_content)
            category = frontmatter_data.get('category') or cls.categorize_document(file_path, main_content)
            tags = frontmatter_data.get('tags', []) + cls.extract_tags(main_content, file_path)
            
            # Calculate metrics
            word_count = len(main_content.split())
            reading_time = max(1, word_count // 200)  # Assume 200 words per minute
            
            # Get file modification time (RFC 3339 format)
            last_updated = datetime.fromtimestamp(os.path.getmtime(file_path), tz=timezone.utc).isoformat()
            
            return DocMetadata(
                title=title,
                content=main_content,
                summary=summary,
                category=category,
                tags=list(set(tags)),  # Remove duplicates
                file_path=file_path,
                word_count=word_count,
                reading_time=reading_time,
                last_updated=last_updated
            )
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return None

class DocumentIngester:
    """Main class for ingesting documentation into Port"""
    
    def __init__(self, port_client: PortClient):
        self.port_client = port_client
        self.processor = DocumentProcessor()
    
    def setup_blueprint(self, blueprint_file: str = "port-docs-blueprint.json") -> bool:
        """Setup the documentation blueprint in Port"""
        try:
            with open(blueprint_file, 'r') as f:
                blueprint_data = json.load(f)
            
            return self.port_client.create_blueprint(blueprint_data)
        except Exception as e:
            print(f"❌ Error setting up blueprint: {e}")
            return False
    
    def ingest_directory(self, docs_path: str, file_extensions: List[str] = ['.md', '.markdown']) -> int:
        """Ingest all markdown files from a directory"""
        docs_path = Path(docs_path)
        ingested_count = 0
        
        print(f"🔍 Scanning {docs_path} for documentation files...")
        
        for file_path in docs_path.rglob('*'):
            if file_path.suffix.lower() in file_extensions and file_path.is_file():
                print(f"📄 Processing {file_path}")
                
                doc_metadata = self.processor.process_file(str(file_path))
                if doc_metadata:
                    if self.create_doc_entity(doc_metadata):
                        ingested_count += 1
        
        return ingested_count
    
    def create_doc_entity(self, doc_metadata: DocMetadata) -> bool:
        """Create a documentation entity in Port"""
        # Generate unique identifier from file path
        identifier = hashlib.md5(doc_metadata.file_path.encode()).hexdigest()[:16]
        
        entity_data = {
            "identifier": identifier,
            "title": doc_metadata.title,
            "properties": {
                "content": doc_metadata.content,
                "summary": doc_metadata.summary,
                "category": doc_metadata.category,
                "tags": doc_metadata.tags,
                "lastUpdated": doc_metadata.last_updated,
                "filePath": doc_metadata.file_path,
                "wordCount": doc_metadata.word_count,
                "readingTime": doc_metadata.reading_time
            }
        }
        
        return self.port_client.create_entity("documentation", entity_data)

def main():
    """Main function to run the ingestion process"""
    # Load environment variables
    load_dotenv()
    
    # Configuration
    CLIENT_ID = os.getenv('PORT_CLIENT_ID', '')
    CLIENT_SECRET = os.getenv('PORT_CLIENT_SECRET', '')
    DOCS_PATH = os.getenv('DOCS_PATH', './docs')
    
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ Please set PORT_CLIENT_ID and PORT_CLIENT_SECRET environment variables")
        return
    
    try:
        # Initialize Port client
        print("🔗 Connecting to Port API...")
        port_client = PortClient(CLIENT_ID, CLIENT_SECRET)
        
        # Initialize ingester
        ingester = DocumentIngester(port_client)
        
        # Setup blueprint
        print("🏗️ Setting up documentation blueprint...")
        if not ingester.setup_blueprint():
            print("❌ Failed to setup blueprint. Exiting.")
            return
        
        # Ingest documentation
        print("📚 Starting documentation ingestion...")
        ingested_count = ingester.ingest_directory(DOCS_PATH)
        
        print(f"✅ Successfully ingested {ingested_count} documentation files!")
        
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")

if __name__ == "__main__":
    main() 