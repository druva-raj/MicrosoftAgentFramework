# Copyright (c) Microsoft. All rights reserved.
"""
MCP Custom Hosted Agent — uses a custom remote MCP server with bearer authentication.

The bearer token is sent to the MCP server by the Foundry-side hosted MCP tool.
Set the ``MCP_BEARER_TOKEN`` environment variable (or a Foundry connection) to
authenticate to the upstream MCP server.

Note:
    Per-request bearer token rotation (previously implemented by mutating the
    MCP tool headers inside ``agent_run``) is no longer wired up — the new
    hosted Responses server does not expose request metadata to the tool layer
    the same way. Use a single static token here, or expose a Foundry project
    connection on the agent if you need managed credentials.
"""

import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

MCP_TOOL_NAME = os.getenv("MCP_TOOL_NAME", "Custom MCP Server")
MCP_TOOL_URL = os.getenv("MCP_TOOL_URL", "https://app-ext-eus2-mcp-profx-01.azurewebsites.net/mcp")
MCP_BEARER_TOKEN = os.getenv("MCP_BEARER_TOKEN")


def _build_headers() -> dict[str, str] | None:
    if not MCP_BEARER_TOKEN:
        return None
    token = MCP_BEARER_TOKEN if MCP_BEARER_TOKEN.startswith("Bearer ") else f"Bearer {MCP_BEARER_TOKEN}"
    return {"Authorization": token}


def main() -> None:
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=DefaultAzureCredential(),
    )

    mcp_tool = client.get_mcp_tool(
        name=MCP_TOOL_NAME,
        url=MCP_TOOL_URL,
        headers=_build_headers(),
        approval_mode="never_require",
    )

    agent = Agent(
        client=client,
        instructions=(
            "You are a helpful assistant that answers questions. "
            "Always use the provided tool to look up answers from the available MCP tools."
        ),
        tools=mcp_tool,
        default_options={"store": False},
    )

    ResponsesHostServer(agent).run()


if __name__ == "__main__":
    main()