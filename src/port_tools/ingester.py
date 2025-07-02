import json
import logging
from typing import Dict

from port_tools.clients.port_client import PortClient
from port_tools.parsers.doc_parser import DocMetadata

logger = logging.getLogger(__name__)

class DocumentIngester:
    """Handles the ingestion of processed documents into Port."""

    BLUEPRINT_ID = "documentation"

    def __init__(self, port_client: PortClient):
        self.port_client = port_client

    def _construct_entity_payload(self, doc_metadata: DocMetadata) -> Dict:
        """Constructs the Port entity payload from document metadata."""
        # The identifier is a combination of the source and the file path
        identifier = f"{doc_metadata.source}/{doc_metadata.file_path}".lower().replace(" ", "-")
        
        properties = {
            "source": doc_metadata.source,
            "filePath": doc_metadata.file_path,
            "content": doc_metadata.content,
            "summary": doc_metadata.summary,
            "category": doc_metadata.category,
            "tags": doc_metadata.tags,
            "lastUpdated": doc_metadata.last_updated,
            "wordCount": doc_metadata.word_count,
            "readingTime": doc_metadata.reading_time,
            "repositoryUrl": doc_metadata.repository_url,
            "fileUrl": doc_metadata.file_url,
        }

        # Filter out None values from properties
        valid_properties = {k: v for k, v in properties.items() if v is not None}

        entity_data = {
            "identifier": identifier,
            "title": doc_metadata.title,
            "properties": valid_properties
        }
        return entity_data

    def ingest_document(self, doc_metadata: DocMetadata) -> bool:
        """
        Ingests a single document into Port by constructing and sending
        the entity payload.
        """
        if not isinstance(doc_metadata, DocMetadata):
            logger.error("Invalid metadata object provided to ingest_document.")
            return False
            
        try:
            entity_payload = self._construct_entity_payload(doc_metadata)
            return self.port_client.create_entity(self.BLUEPRINT_ID, entity_payload)
        except Exception as e:
            logger.error(f"Failed to ingest document {doc_metadata.file_path}: {e}", exc_info=True)
            return False

    def setup_blueprint(self, blueprint_file: str = "port-docs-blueprint.json") -> bool:
        """
        Creates or updates the documentation blueprint in Port using a
        local JSON file definition.
        """
        logger.info(f"Setting up '{self.BLUEPRINT_ID}' blueprint from {blueprint_file}...")
        try:
            with open(blueprint_file, 'r', encoding='utf-8') as f:
                blueprint_data = json.load(f)
            
            # Ensure the identifier in the file matches our standard
            if blueprint_data.get("identifier") != self.BLUEPRINT_ID:
                logger.warning(
                    f"Blueprint identifier in {blueprint_file} is not '{self.BLUEPRINT_ID}'. Adjusting..."
                )
                blueprint_data["identifier"] = self.BLUEPRINT_ID

            return self.port_client.create_blueprint(blueprint_data)
        except FileNotFoundError:
            logger.error(f"Blueprint definition file not found: {blueprint_file}")
            return False
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from {blueprint_file}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during blueprint setup: {e}", exc_info=True)
            return False 