# Copyright (c) Microsoft. All rights reserved.

import asyncio
from dotenv import load_dotenv

from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

"""
Azure AI Agent Basic Example
"""

async def main():
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIAgentClient(
                async_credential=credential,
                ## Existing Agent - either use agent_id or agent_name
                ## agent_id="asst_Zl9a0pnLuqL43DMYMhAh6vYo"
                agent_name="AgentFramework-BasicAgent",
            ),
            instructions="You are a helpful assistant."
        ) as agent,
    ):
        result = await agent.run("What do you know about agents?")
        print(result.text)

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())