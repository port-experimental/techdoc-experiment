import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator, List, Optional

from port_tools.parsers.doc_parser import DocParser, DocMetadata

logger = logging.getLogger(__name__)

class LocalFetcher:
    """Fetches documentation from the local file system."""

    def __init__(self, parser: DocParser):
        self.parser = parser

    def fetch_documents(
        self,
        docs_path: str,
        file_extensions: List[str] = ['.md', '.markdown']
    ) -> Generator[DocMetadata, None, None]:
        """
        Scans a directory for documentation files and yields metadata for each.

        :param docs_path: The root directory to scan for documentation.
        :param file_extensions: A list of file extensions to consider.
        :return: A generator of DocMetadata objects.
        """
        base_path = Path(docs_path)
        if not base_path.is_dir():
            logger.error(f"Provided documentation path is not a valid directory: {docs_path}")
            return

        logger.info(f"Scanning for documents in '{base_path}' with extensions {file_extensions}...")
        
        for file_path in base_path.rglob('*'):
            if file_path.suffix.lower() in file_extensions and file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Use relative path for a cleaner file_path in the entity
                    relative_path = file_path.relative_to(base_path)
                    
                    last_updated_ts = os.path.getmtime(file_path)
                    last_updated_dt = datetime.fromtimestamp(last_updated_ts, tz=timezone.utc)
                    
                    doc_metadata = self.parser.parse(
                        content=content,
                        source='local',
                        file_path=str(relative_path),
                        last_updated=last_updated_dt.isoformat()
                    )
                    yield doc_metadata

                except Exception as e:
                    logger.error(f"Failed to process local file {file_path}: {e}", exc_info=True)
