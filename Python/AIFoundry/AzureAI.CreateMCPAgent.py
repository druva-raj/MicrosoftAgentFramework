# Copyright (c) Microsoft. All rights reserved.

import asyncio
from dotenv import load_dotenv

from agent_framework import MCPStreamableHTTPTool
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
        headers={"Authorization": "Bearer <YOUR_BEARER_TOKEN>"},
    )

    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential,should_cleanup_agent=False).create_agent(
            name="AgentFramework-MCPAgent",
            instructions="You are a utility agent, answer questions based on the utilities available to you!",
            tools=[mcpTools]
        ) as agent,
    ):
        result = await agent.run("Multiply 456 and 457.")
        print(result.text)

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())