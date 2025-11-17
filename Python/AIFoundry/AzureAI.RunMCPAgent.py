# Copyright (c) Microsoft. All rights reserved.

import asyncio
from dotenv import load_dotenv

from agent_framework import ChatAgent, MCPStreamableHTTPTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential
from pydantic import Field

"""
Azure AI Agent with Microsoft Learn MCP Tool Example
"""

async def main():

    mcpTools = MCPStreamableHTTPTool(
        name="AgentFramework-MCPTool",
        url="https://app-ext-eus2-mcp-profx-01.azurewebsites.net/mcp",
        approval_mode="never_require",
        allowed_tools=["multiply"],
        headers={"Authorization": "Bearer <YOUR_BEARER_TOKEN>"},
    )

    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIAgentClient(async_credential=credential),
            name="AgentFramework-MCPAgent",
            instructions="You are a utility agent, answer questions based on the utilities available to you!",
            tools=[mcpTools],
        ) as agent,
    ):
        result = await agent.run("Multiply 50 and 10.")
        print(result.text)

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())