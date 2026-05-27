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
Foundry Chat Client with Hosted MCP Tool - Bearer Token Authentication Example

This sample demonstrates how to use Bearer Token authentication with a hosted MCP
tool when using ``FoundryChatClient``. The headers are forwarded by the Foundry
service to the MCP server during the hosted MCP invocation.

If you would rather not pass the token directly, create a Custom Key connection
in your Foundry project and reference it via the ``additional_properties``
argument with ``project_connection_id``.

Pre-requisites:
- Set FOUNDRY_PROJECT_ENDPOINT (or AZURE_AI_PROJECT_ENDPOINT) and
  AZURE_AI_MODEL_DEPLOYMENT_NAME environment variables.
- Provide MCP_BEARER_TOKEN, or set MCP_CUSTOM_PROJECT_CONNECTION_ID to a
  Custom Key connection in your Azure AI Foundry project that stores the token.
"""


async def main() -> None:
    """Example showing use of a Hosted MCP Tool with bearer authentication."""
    print("=== Foundry Chat Client with Hosted MCP - Bearer Auth ===\n")
    load_dotenv(ENV_PATH)

    project_endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT") or os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    model = os.environ.get("FOUNDRY_MODEL") or os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]

    bearer_token = os.getenv("MCP_BEARER_TOKEN")
    project_connection_id = os.getenv("MCP_CUSTOM_PROJECT_CONNECTION_ID")

    headers: dict[str, str] | None = None
    if bearer_token:
        token = bearer_token if bearer_token.startswith("Bearer ") else f"Bearer {bearer_token}"
        headers = {"Authorization": token}

    additional_properties: dict[str, str] | None = None
    if project_connection_id:
        additional_properties = {"project_connection_id": project_connection_id}

    async with AzureCliCredential() as credential:
        client = FoundryChatClient(
            project_endpoint=project_endpoint,
            model=model,
            credential=credential,
        )

        mcp_tool = client.get_mcp_tool(
            name="Custom_MCP",
            url="https://app-ext-eus2-mcp-profx-01.azurewebsites.net/mcp",
            allowed_tools=["multiply", "validate_user"],
            approval_mode="never_require",
            headers=headers,
            additional_properties=additional_properties,
        )

        agent = Agent(
            client=client,
            name="AF-MCP-Hosted-BearerAuth-Agent",
            instructions=(
                "You are a helpful assistant that can help with user questions. "
                "Always use the available tools to answer the user's questions."
            ),
            tools=mcp_tool,
        )

        query = "Multiply 10 and 20"
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result}")


if __name__ == "__main__":
    asyncio.run(main())