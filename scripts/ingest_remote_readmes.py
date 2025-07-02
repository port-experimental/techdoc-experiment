import logging
import os
import sys
import toml
from dotenv import load_dotenv

# Add src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from port_tools.clients.port_client import PortClient
from port_tools.parsers.doc_parser import DocParser
from port_tools.fetchers.git_fetcher import GitFetcher
from port_tools.ingester import DocumentIngester

# Basic logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("urllib3").setLevel(logging.WARNING) # Silence noisy library logs

def load_config(config_file: str = "repositories.toml"):
    """Loads the repository configuration from a TOML file."""
    try:
        return toml.load(config_file)
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_file}")
        sys.exit(1)
    except toml.TomlDecodeError as e:
        logging.error(f"Error decoding {config_file}: {e}")
        sys.exit(1)

def main():
    """Main function to run the remote README ingestion process."""
    load_dotenv()

    # Load credentials from environment
    PORT_CLIENT_ID = os.getenv('PORT_CLIENT_ID')
    PORT_CLIENT_SECRET = os.getenv('PORT_CLIENT_SECRET')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITLAB_URL = os.getenv('GITLAB_URL')
    GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
    AZURE_DEVOPS_URL = os.getenv('AZURE_DEVOPS_URL')
    AZURE_DEVOPS_TOKEN = os.getenv('AZURE_DEVOPS_TOKEN')

    if not PORT_CLIENT_ID or not PORT_CLIENT_SECRET:
        logging.error("PORT_CLIENT_ID and PORT_CLIENT_SECRET must be set.")
        sys.exit(1)

    # Load repository targets from config file
    repo_config = load_config()
    github_orgs = repo_config.get("github", {}).get("orgs", [])
    gitlab_groups = repo_config.get("gitlab", {}).get("groups", [])
    azure_projects = repo_config.get("azure_repos", {}).get("projects", [])

    try:
        # Initialize components
        logging.info("Initializing Port client and services...")
        port_client = PortClient(PORT_CLIENT_ID, PORT_CLIENT_SECRET)
        doc_parser = DocParser()
        git_fetcher = GitFetcher(
            parser=doc_parser,
            github_token=GITHUB_TOKEN,
            gitlab_url=GITLAB_URL,
            gitlab_token=GITLAB_TOKEN,
            azure_devops_url=AZURE_DEVOPS_URL,
            azure_devops_token=AZURE_DEVOPS_TOKEN,
        )
        ingester = DocumentIngester(port_client=port_client)

        # Setup the blueprint in Port
        logging.info("Setting up documentation blueprint...")
        if not ingester.setup_blueprint():
            logging.error("Failed to set up blueprint. Aborting.")
            sys.exit(1)

        # Fetch and ingest documents
        logging.info("Starting ingestion from remote Git repositories...")
        ingested_count = 0
        failed_count = 0

        # Create a single generator for all providers
        all_readmes = git_fetcher.fetch_readmes(
            github_orgs=github_orgs,
            gitlab_groups=gitlab_groups,
            azure_projects=azure_projects,
        )

        for doc_metadata in all_readmes:
            if ingester.ingest_document(doc_metadata):
                ingested_count += 1
            else:
                failed_count += 1

        logging.info("--- Ingestion Summary ---")
        logging.info(f"Successfully ingested: {ingested_count} READMEs")
        logging.info(f"Failed to ingest: {failed_count} READMEs")
        logging.info("-------------------------")

    except Exception as e:
        logging.error(f"An unexpected error occurred during the ingestion process: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 