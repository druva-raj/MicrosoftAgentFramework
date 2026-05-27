# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from pathlib import Path

from agent_framework.foundry import FoundryAgent
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv

# Load .env from parent directory
ENV_PATH = Path(__file__).parent.parent / ".env"

"""
Connect to a pre-configured Foundry Agent via the Foundry Agent SDK

This sample uses ``FoundryAgent`` to connect to an existing PromptAgent or
HostedAgent in Azure AI Foundry. The agent's instructions, model, and hosted
tools are all configured on the service — this code just connects and runs.

Pre-requisites:
- Set FOUNDRY_PROJECT_ENDPOINT (or AZURE_AI_PROJECT_ENDPOINT) environment variable.
- The agent named below must already exist in the Foundry project.
"""

AGENT_NAME = os.getenv("FOUNDRY_AGENT_NAME", "FoundryNew-MCP-MSLearnAgent")


async def main() -> None:
    """Example showing how to connect to an existing Foundry agent."""
    print("=== Connect to existing Foundry Agent ===\n")
    load_dotenv(ENV_PATH)

    project_endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT") or os.environ["AZURE_AI_PROJECT_ENDPOINT"]

    async with AzureCliCredential() as credential:
        agent = FoundryAgent(
            project_endpoint=project_endpoint,
            agent_name=AGENT_NAME,
            credential=credential,
        )

        query = "List available MCP tools?"
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result}")


if __name__ == "__main__":
    asyncio.run(main())