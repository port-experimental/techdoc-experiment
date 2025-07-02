#!/usr/bin/env python3
"""
AI Agent Management Module
Provides a class to manage the lifecycle and testing of Port AI Agents.
"""

import os
import json
import time
from typing import Optional, Dict, Any

from ..clients.port_client import PortClient


class AIAgentManager:
    """
    Manages creation, testing, and interaction with Port AI Agents.
    """

    def __init__(self, client: PortClient, agent_config_path: str = 'ai-agent-config.json'):
        """
        Initializes the AI Agent Manager.

        :param client: An authenticated PortClient instance.
        :param agent_config_path: Path to the JSON file with the agent's configuration.
        """
        self.client = client
        self.agent_config_path = agent_config_path
        self.base_url = self.client.base_url

    def _get_agent_config(self) -> Optional[Dict[str, Any]]:
        """Loads the AI agent configuration from the specified JSON file."""
        try:
            with open(self.agent_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: Agent configuration file not found at '{self.agent_config_path}'")
            return None
        except json.JSONDecodeError:
            print(f"❌ Error: Invalid JSON in agent configuration file at '{self.agent_config_path}'")
            return None

    def create_agent(self) -> bool:
        """
        Creates or updates a Port AI agent based on the configuration file.

        Note: The actual API endpoint for creating agents is not yet public.
        This method is a placeholder for the future implementation.
        """
        print("🤖 Attempting to create or update the AI Documentation Agent...")
        config = self._get_agent_config()
        if not config:
            return False

        agent_config = config.get('agentConfig', {})
        if not agent_config:
            print("❌ Error: 'agentConfig' not found in the configuration file.")
            return False

        # This payload structure is conceptual and based on observed patterns.
        # It will need to be verified once the official API is documented.
        agent_payload = {
            "name": agent_config.get("name"),
            "description": agent_config.get("description"),
            "purpose": agent_config.get("purpose"),
            "systemPrompt": agent_config.get("prompt", {}).get("systemPrompt"),
            "conversationStarters": agent_config.get("prompt", {}).get("conversationStarters"),
            "blueprints": agent_config.get("dataAccess", {}).get("blueprints"),
            "properties": agent_config.get("dataAccess", {}).get("properties"),
            "relations": agent_config.get("dataAccess", {}).get("relations"),
            "settings": agent_config.get("settings")
        }

        print("📋 Agent configuration prepared:")
        print(f"   - Name: {agent_payload['name']}")
        print(f"   - Blueprints: {agent_payload['blueprints']}")

        # Conceptual API call
        # url = f"{self.base_url}/v1/agents"
        # response = self.client.session.post(url, json=agent_payload)
        
        print("\n⚠️ Note: The API endpoint for agent creation is not yet publicly available.")
        print("   This script has prepared the configuration based on the provided JSON file.")
        print("   Once Port enables the API, this function can be fully implemented.")

        # For now, we return True to indicate the process was followed.
        return True

    def invoke(self, prompt: str, wait_for_completion: bool = False, max_wait: int = 30) -> Optional[Dict[str, Any]]:
        """
        Invokes the AI agent with a specific prompt.

        :param prompt: The question or command for the AI agent.
        :param wait_for_completion: If True, waits for the invocation to complete.
        :param max_wait: Maximum seconds to wait for completion.
        :return: The API response dictionary or None on failure.
        """
        print(f"💬 Invoking AI agent with prompt: '{prompt}'")
        url = f"{self.base_url}/v1/agent/invoke"
        payload = {
            "prompt": prompt,
            "context": {
                "user": "cli_user",
                "source": "python_script",
                "timestamp": time.time()
            }
        }

        try:
            response = self.client.session.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            invocation_id = result.get('invocation', {}).get('identifier')
            print(f"✅ Invocation started successfully. ID: {invocation_id}")

            if wait_for_completion and invocation_id:
                return self._wait_for_result(invocation_id, max_wait)
            return result

        except Exception as e:
            print(f"❌ Error invoking AI agent: {e}")
            if "401" in str(e):
                 print("   Hint: This may mean the AI Agents feature is not enabled for your account.")
            return None

    def _wait_for_result(self, invocation_id: str, max_wait: int) -> Optional[Dict[str, Any]]:
        """
        Polls for the result of a specific invocation.

        Note: The actual API endpoint for checking status is not yet public.
        This method is a placeholder for the future implementation.
        """
        print(f"⏳ Waiting up to {max_wait}s for invocation {invocation_id} to complete...")
        
        # This endpoint is conceptual and needs to be verified.
        # url = f"{self.base_url}/v1/agent/invocations/{invocation_id}"

        print("⚠️ Note: The API endpoint for checking invocation status is not yet publicly available.")
        print("   This script cannot currently poll for a final result.")
        
        # Returning a mock success structure for now
        return {"status": "completed", "invocationId": invocation_id, "mock_result": "This is a placeholder result."} 