# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from pathlib import Path

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv

# Load .env from parent directory
ENV_PATH = Path(__file__).parent.parent / ".env"

"""
Foundry Chat Client with Hosted MCP Tool - Microsoft Learn Example

This sample demonstrates how to use a hosted MCP tool (Microsoft Learn MCP)
with ``FoundryChatClient``. The MCP call happens server-side in Foundry.

Pre-requisites:
- Set FOUNDRY_PROJECT_ENDPOINT (or AZURE_AI_PROJECT_ENDPOINT) and
  AZURE_AI_MODEL_DEPLOYMENT_NAME environment variables before running this sample.
"""


async def main() -> None:
    """Example showing use of a Hosted MCP Tool with FoundryChatClient."""
    print("=== Foundry Chat Client with Microsoft Learn Hosted MCP ===\n")
    load_dotenv(ENV_PATH)

    project_endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT") or os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    model = os.environ.get("FOUNDRY_MODEL") or os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]

    async with AzureCliCredential() as credential:
        client = FoundryChatClient(
            project_endpoint=project_endpoint,
            model=model,
            credential=credential,
        )

        mcp_tool = client.get_mcp_tool(
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
            allowed_tools=["microsoft_docs_search", "microsoft_docs_fetch"],
            approval_mode="never_require",
        )

        agent = Agent(
            client=client,
            name="AF-MCP-Hosted-MicrosoftLearnAgent",
            instructions=(
                "You are a helpful assistant that can help with Microsoft documentation questions. "
                "Always use the available Microsoft Learn MCP tools to answer the user's questions."
            ),
            tools=mcp_tool,
        )

        query = "List available MCP tools?"
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result}")


if __name__ == "__main__":
    asyncio.run(main())