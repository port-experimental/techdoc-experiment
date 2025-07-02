import logging
import os
import sys
from dotenv import load_dotenv

# Add src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from port_tools.clients.port_client import PortClient
from port_tools.parsers.doc_parser import DocParser
from port_tools.fetchers.local_fetcher import LocalFetcher
from port_tools.ingester import DocumentIngester

# Basic logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    """Main function to run the local documentation ingestion process."""
    load_dotenv()
    
    # Configuration from environment variables
    CLIENT_ID = os.getenv('PORT_CLIENT_ID')
    CLIENT_SECRET = os.getenv('PORT_CLIENT_SECRET')
    DOCS_PATH = os.getenv('DOCS_PATH', './docs')
    
    if not CLIENT_ID or not CLIENT_SECRET:
        logging.error("PORT_CLIENT_ID and PORT_CLIENT_SECRET must be set.")
        sys.exit(1)

    try:
        # Initialize components
        logging.info("Initializing Port client and services...")
        port_client = PortClient(CLIENT_ID, CLIENT_SECRET)
        doc_parser = DocParser()
        local_fetcher = LocalFetcher(parser=doc_parser)
        ingester = DocumentIngester(port_client=port_client)

        # Setup the blueprint in Port
        logging.info("Setting up documentation blueprint...")
        if not ingester.setup_blueprint():
            logging.error("Failed to set up blueprint. Aborting.")
            sys.exit(1)

        # Fetch and ingest documents
        logging.info(f"Starting ingestion from local directory: {DOCS_PATH}")
        ingested_count = 0
        failed_count = 0

        for doc_metadata in local_fetcher.fetch_documents(docs_path=DOCS_PATH):
            if ingester.ingest_document(doc_metadata):
                ingested_count += 1
            else:
                failed_count += 1
        
        logging.info("--- Ingestion Summary ---")
        logging.info(f"Successfully ingested: {ingested_count} documents")
        logging.info(f"Failed to ingest: {failed_count} documents")
        logging.info("-------------------------")

    except Exception as e:
        logging.error(f"An unexpected error occurred during the ingestion process: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 