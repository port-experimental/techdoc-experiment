import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import frontmatter
import markdown
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

@dataclass
class DocMetadata:
    """Standardized metadata extracted from a documentation file."""
    title: str
    content: str
    source: str
    file_path: str
    last_updated: str
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    repository_url: Optional[str] = None
    file_url: Optional[str] = None
    word_count: int = 0
    reading_time: int = 0


class DocParser:
    """Process markdown document content and extract metadata."""

    @staticmethod
    def extract_frontmatter(content: str) -> Tuple[Dict, str]:
        """Extract frontmatter from markdown content."""
        try:
            post = frontmatter.loads(content)
            return post.metadata, post.content
        except Exception:
            logger.debug("No frontmatter found or failed to parse.")
            return {}, content

    @staticmethod
    def extract_title(content: str, source_path: str) -> str:
        """Extract title from content or filename."""
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()
        return Path(source_path).stem.replace('-', ' ').replace('_', ' ').title()

    @staticmethod
    def generate_summary(content: str, max_length: int = 250) -> str:
        """Generate summary from markdown content."""
        html = markdown.markdown(content)
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text().strip()
        
        summary = ' '.join(text.split()[:50]) # First 50 words
        if len(summary) > max_length:
            summary = summary[:max_length].rsplit(' ', 1)[0] + '...'
        return summary

    @staticmethod
    def categorize_document(source_path: str, content: str) -> str:
        """Categorize document based on path and content."""
        path_lower = source_path.lower()
        if 'api' in path_lower or 'reference' in path_lower:
            return 'API Reference'
        if 'guide' in path_lower or 'tutorial' in path_lower:
            return 'Guide'
        if 'example' in path_lower:
            return 'Example'
        if 'concept' in path_lower:
            return 'Concept'
        return 'Documentation'

    @staticmethod
    def extract_tags(source_path: str, content: str) -> List[str]:
        """Extract tags from content and file path."""
        tags = set()
        try:
            path_parts = Path(source_path).parts
            if len(path_parts) > 1:
                # Use parent directory as a tag
                tags.add(path_parts[-2].lower().replace('_', '-'))
        except Exception:
            pass

        tech_terms = [
            'api', 'rest', 'graphql', 'webhook', 'python', 'javascript', 
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'integration'
        ]
        content_lower = content.lower()
        for term in tech_terms:
            if term in content_lower:
                tags.add(term)
        
        return sorted(list(tags))

    @classmethod
    def parse(cls, content: str, source: str, file_path: str, last_updated: str, 
              repo_url: Optional[str] = None, file_url: Optional[str] = None) -> DocMetadata:
        """
        Process markdown content and return structured metadata.
        
        :param content: The markdown content of the file.
        :param source: The origin of the doc (e.g., 'local', 'github').
        :param file_path: The path to the file within its source.
        :param last_updated: ISO 8601 string of the last update time.
        :param repo_url: Optional URL to the source repository.
        :param file_url: Optional URL to the file in its source.
        :return: A DocMetadata object.
        """
        try:
            fm, main_content = cls.extract_frontmatter(content)
            
            title = fm.get('title') or cls.extract_title(main_content, file_path)
            summary = fm.get('description') or cls.generate_summary(main_content)
            category = fm.get('category') or cls.categorize_document(file_path, main_content)
            
            # Combine tags from frontmatter and content analysis
            tags = set(fm.get('tags', []))
            tags.update(cls.extract_tags(file_path, main_content))

            word_count = len(main_content.split())
            reading_time = max(1, round(word_count / 200))

            return DocMetadata(
                title=title,
                content=main_content,
                summary=summary,
                category=category,
                tags=sorted(list(tags)),
                source=source,
                file_path=file_path,
                last_updated=last_updated,
                repository_url=repo_url,
                file_url=file_url,
                word_count=word_count,
                reading_time=reading_time,
            )
        except Exception as e:
            logger.error(f"Error parsing document content for {file_path}: {e}", exc_info=True)
            raise
