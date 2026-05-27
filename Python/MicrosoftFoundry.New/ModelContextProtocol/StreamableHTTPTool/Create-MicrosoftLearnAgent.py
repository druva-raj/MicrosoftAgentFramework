# Copyright (c) Microsoft. All rights reserved.

import asyncio
import logging
import os
import warnings
from pathlib import Path

# Suppress asyncio cleanup errors (known MCP client issue during shutdown)
logging.getLogger("asyncio").setLevel(logging.WARNING)
warnings.filterwarnings("ignore", message=".*cancel scope.*")

# Enable detailed HTTP tracing (set to INFO for less verbose output)
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

# Azure SDK HTTP logging (shows requests/responses)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.INFO)

# httpx logging (used by MCP clients)
logging.getLogger("httpx").setLevel(logging.INFO)

# MCP client logging (set to INFO to see tool calls without noise)
logging.getLogger("mcp").setLevel(logging.INFO)

# Agent Framework internal logging
logging.getLogger("agent_framework").setLevel(logging.INFO)

from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.foundry import FoundryChatClient
from agent_framework.observability import configure_otel_providers
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv

"""
Foundry Chat Client with Streamable HTTP MCP Tool - Microsoft Learn Example

This sample demonstrates integration of ``FoundryChatClient`` with a remote
Model Context Protocol (MCP) server using ``MCPStreamableHTTPTool``. The MCP
connection is created locally; the agent passes the tool definitions to the
Foundry model and invokes tools on this side.

Pre-requisites:
- Set FOUNDRY_PROJECT_ENDPOINT (or AZURE_AI_PROJECT_ENDPOINT) and
  AZURE_AI_MODEL_DEPLOYMENT_NAME environment variables.
"""

# Load .env from parent directory
ENV_PATH = Path(__file__).parent.parent / ".env"

# ========== TRACING SETUP ==========
# Option 1: Local AI Toolkit trace viewer
configure_otel_providers(
    vs_code_extension_port=4317,  # AI Toolkit gRPC port
    enable_sensitive_data=True,   # Capture prompts, completions, and tool results
)

# Option 2: Send traces to Azure AI Foundry (uncomment to enable)
# This enables tracing in the Foundry portal under "Tracing" tab
from azure.core.settings import settings
settings.tracing_implementation = "opentelemetry"
os.environ["AZURE_TRACING_GEN_AI_INCLUDE_BINARY_DATA"] = "true"

from azure.ai.projects.telemetry import AIProjectInstrumentor
AIProjectInstrumentor().instrument(enable_content_recording=True)
# ========== END TRACING SETUP ==========


async def main() -> None:
    """Example showing MCPStreamableHTTPTool with a Foundry Chat Client agent."""
    print("=== Foundry Chat Client with Microsoft Learn MCP (Streamable HTTP) ===\n")
    load_dotenv(ENV_PATH)

    project_endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT") or os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    model = os.environ.get("FOUNDRY_MODEL") or os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]

    async with AzureCliCredential() as credential:
        client = FoundryChatClient(
            project_endpoint=project_endpoint,
            model=model,
            credential=credential,
        )

        async with MCPStreamableHTTPTool(
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
        ) as mcp_tool:
            agent = Agent(
                client=client,
                name="StreamableDocsAgent",
                instructions=(
                    "You are a helpful assistant that can help with Microsoft documentation questions. "
                    "Always use the provided tool to look up answers from the Microsoft Learn MCP server. "
                    "Provide references in your answers."
                ),
                tools=mcp_tool,
            )

            first_query = "What is Azure Sphere?"
            print(f"User: {first_query}")
            first_result = await agent.run(first_query)
            print(f"Agent: {first_result}")
            print("\n=======================================\n")


if __name__ == "__main__":
    asyncio.run(main())