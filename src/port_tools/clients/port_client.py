import logging
from typing import Dict, Optional

import requests

logger = logging.getLogger(__name__)


class PortClient:
    """A client for interacting with the Port API."""

    def __init__(self, client_id: str, client_secret: str, base_url: str = "https://api.getport.io"):
        self.base_url = base_url
        self.session = self._authenticate(client_id, client_secret)

    def _authenticate(self, client_id: str, client_secret: str) -> requests.Session:
        """Authenticate with the Port API and return an authenticated session."""
        logger.info("Authenticating with Port API...")
        auth_url = f"{self.base_url}/v1/auth/access_token"
        auth_data = {"clientId": client_id, "clientSecret": client_secret}
        
        try:
            response = requests.post(auth_url, json=auth_data)
            response.raise_for_status()
            access_token = response.json().get("accessToken")
            
            session = requests.Session()
            session.headers.update({
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            })
            logger.info("Authentication successful.")
            return session
        except requests.RequestException as e:
            logger.error(f"Failed to authenticate with Port API: {e}", exc_info=True)
            raise

    def create_blueprint(self, blueprint_data: Dict) -> bool:
        """Creates or updates a blueprint in Port."""
        identifier = blueprint_data.get("identifier")
        if not identifier:
            logger.error("Blueprint data must contain an 'identifier'.")
            return False
            
        url = f"{self.base_url}/v1/blueprints/{identifier}"
        
        try:
            # Check if the blueprint exists
            get_response = self.session.get(url)

            if get_response.status_code == 200:
                # Update existing blueprint
                logger.info(f"Blueprint '{identifier}' already exists. Updating...")
                response = self.session.put(url, json=blueprint_data)
            else:
                # Create new blueprint
                logger.info(f"Blueprint '{identifier}' not found. Creating...")
                # The base URL for creation is different
                create_url = f"{self.base_url}/v1/blueprints"
                response = self.session.post(create_url, json=blueprint_data)

            response.raise_for_status()
            logger.info(f"Blueprint '{identifier}' created/updated successfully.")
            return True

        except requests.RequestException as e:
            logger.error(f"Failed to create or update blueprint '{identifier}': {e}", exc_info=True)
            return False

    def create_entity(self, blueprint_id: str, entity_data: Dict) -> bool:
        """Creates or updates an entity in a blueprint."""
        identifier = entity_data.get("identifier")
        url = f"{self.base_url}/v1/blueprints/{blueprint_id}/entities"
        params = {"upsert": "true", "merge": "true"}
        
        logger.info(f"Creating/updating entity '{identifier}' in blueprint '{blueprint_id}'...")
        
        try:
            response = self.session.post(url, json=entity_data, params=params)
            response.raise_for_status()
            logger.info(f"Entity '{identifier}' created/updated successfully in blueprint '{blueprint_id}'.")
            return True
        except requests.HTTPError as e:
            # Log the detailed error response from Port for better debugging
            error_details = response.text
            logger.error(
                f"Failed to create/update entity '{identifier}' in blueprint '{blueprint_id}': {e}\\n"
                f"Response Body: {error_details}"
            )
            return False

    def search_entities(self, blueprint_id: str, query: Optional[Dict] = None, limit: int = 5) -> Dict:
        """Searches for entities within a given blueprint."""
        url = f"{self.base_url}/v1/blueprints/{blueprint_id}/entities/search"
        payload = {
            "query": query if query else {"combinator": "and", "rules": []},
            "limit": limit
        }
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to search entities in blueprint '{blueprint_id}': {e}", exc_info=True)
            raise
