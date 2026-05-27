# Copyright (c) Microsoft. All rights reserved.
"""
MCP Simple Hosted Agent — uses Microsoft Learn MCP as a hosted MCP tool.
"""

import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

MCP_TOOL_NAME = os.getenv("MCP_TOOL_NAME", "Microsoft Learn MCP")
MCP_TOOL_URL = os.getenv("MCP_TOOL_URL", "https://learn.microsoft.com/api/mcp")


def main() -> None:
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=DefaultAzureCredential(),
    )

    mcp_tool = client.get_mcp_tool(
        name=MCP_TOOL_NAME,
        url=MCP_TOOL_URL,
        approval_mode="never_require",
    )

    agent = Agent(
        client=client,
        instructions=(
            "You are a helpful assistant that answers Microsoft documentation questions. "
            "Always use the provided tool to look up answers from the Microsoft Learn MCP API."
        ),
        tools=mcp_tool,
        default_options={"store": False},
    )

    ResponsesHostServer(agent).run()


if __name__ == "__main__":
    main()
