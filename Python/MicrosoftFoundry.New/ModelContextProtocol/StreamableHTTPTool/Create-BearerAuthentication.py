# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from pathlib import Path

from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv

# Load .env from parent directory
ENV_PATH = Path(__file__).parent.parent / ".env"

"""
Foundry Chat Client with Streamable HTTP MCP Tool - Bearer Authentication Example

This sample demonstrates how to use Bearer Token authentication with a locally
connected MCP server via ``MCPStreamableHTTPTool`` and ``FoundryChatClient``.

Unlike a hosted MCP tool, the MCP connection here is made from the client
process, so the bearer token never has to leave the local environment.

Pre-requisites:
- Set FOUNDRY_PROJECT_ENDPOINT (or AZURE_AI_PROJECT_ENDPOINT) and
  AZURE_AI_MODEL_DEPLOYMENT_NAME environment variables.
- Set the MCP_BEARER_TOKEN environment variable with the bearer token for the
  upstream MCP server.
"""


async def main() -> None:
    """Example showing use of MCPStreamableHTTPTool with Bearer Authentication."""
    print("=== Foundry Chat Client with Streamable HTTP MCP - Bearer Auth ===\n")
    load_dotenv(ENV_PATH)

    project_endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT") or os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    model = os.environ.get("FOUNDRY_MODEL") or os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]

    bearer_token = os.environ["MCP_BEARER_TOKEN"]
    token = bearer_token if bearer_token.startswith("Bearer ") else f"Bearer {bearer_token}"

    async with AzureCliCredential() as credential:
        client = FoundryChatClient(
            project_endpoint=project_endpoint,
            model=model,
            credential=credential,
        )

        async with MCPStreamableHTTPTool(
            name="Custom_MCP",
            url="https://app-ext-eus2-mcp-profx-01.azurewebsites.net/mcp",
            allowed_tools=["multiply", "validate_user"],
            approval_mode="never_require",
            headers={"Authorization": token},
            load_prompts=False,  # Disable prompt loading if server doesn't support it
        ) as mcp_tool:
            agent = Agent(
                client=client,
                name="AF-MCP-Streamable-BearerAuth-Agent",
                instructions="Only use the available tools to answer the user's questions.",
                tools=mcp_tool,
            )

            query = "Validate user druvan"
            print(f"User: {query}")
            result = await agent.run(query)
            print(f"Agent: {result}")


if __name__ == "__main__":
    asyncio.run(main())