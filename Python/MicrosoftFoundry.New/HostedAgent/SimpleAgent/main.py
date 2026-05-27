# Copyright (c) Microsoft. All rights reserved.
"""
Simple Hosted Agent Example

This demonstrates the minimal setup for a hosted agent in Microsoft Foundry.
The agent runs locally on localhost:8088 and can be deployed to Foundry Agent Service.
"""

import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


def main():
    """Entry point - create the agent and run the hosted Responses server."""
    load_dotenv()

    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=DefaultAzureCredential(),
    )

    agent = Agent(
        client=client,
        name="SimpleAgent",
        instructions=(
            "You are a helpful, friendly assistant. "
            "Keep your responses concise and helpful. "
            "If you don't know something, say so honestly."
        ),
        # History is managed by the hosting infrastructure, so the service
        # does not need to store it. See:
        # https://developers.openai.com/api/reference/resources/responses/methods/create
        default_options={"store": False},
    )

    # Starts the Foundry Responses host on port 8088 (HTTP, SSE streaming, OTel tracing).
    ResponsesHostServer(agent).run()


if __name__ == "__main__":
    main()
