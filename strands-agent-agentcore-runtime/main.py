"""
Strands Agent with AWS Bedrock AgentCore Runtime Integration
Uses deployed MCP server for tools and AgentCore managed memory
"""

import os
import boto3
from datetime import datetime

# Strands Agents imports
from strands_agents import Agent

# AWS Bedrock AgentCore client
bedrock_agentcore = boto3.client('bedrock-agentcore-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))


def invoke_mcp_server(mcp_runtime_id: str, session_id: str, user_input: str) -> str:
    """
    Invoke the deployed MCP server via AgentCore runtime

    Args:
        mcp_runtime_id: The AgentCore runtime ID of the MCP server
        session_id: Session identifier for continuity
        user_input: User's query to send to the MCP server

    Returns:
        Response from the MCP server
    """
    try:
        response = bedrock_agentcore.invoke_runtime(
            runtimeId=mcp_runtime_id,
            sessionId=session_id,
            inputText=user_input
        )

        # Collect streaming response
        result = ""
        if 'output' in response:
            for event in response['output']:
                if 'chunk' in event and 'bytes' in event['chunk']:
                    result += event['chunk']['bytes'].decode('utf-8')

        return result

    except Exception as e:
        return f"Error invoking MCP server: {str(e)}"


def create_lambda_cost_advisor_agent(mcp_runtime_id: str) -> Agent:
    """
    Create a Strands Agent that uses the deployed MCP server

    Args:
        mcp_runtime_id: AgentCore runtime ID of the deployed MCP server

    Returns:
        Configured Strands Agent instance
    """
    # System prompt that guides the agent to use the MCP server
    system_prompt = f"""You are an expert AWS Lambda cost optimization advisor.

You have access to an MCP (Model Context Protocol) server for AWS Lambda cost calculations.
MCP Runtime ID: {mcp_runtime_id}

When users ask about Lambda costs:
1. Understand their requirements (region, memory, duration, requests, etc.)
2. Use the MCP server to get accurate cost calculations
3. Interpret results and provide clear recommendations
4. Suggest optimizations (ARM64 vs x86, memory sizing, etc.)

Available MCP tools:
- calculate_lambda_cost: Detailed cost calculations
- compare_lambda_architectures: x86 vs ARM64 comparison
- get_lambda_pricing_info: General pricing information

AgentCore will automatically manage your memory across sessions.

Provide clear, actionable cost optimization advice."""

    # Create Strands Agent
    agent = Agent(
        name="Lambda Cost Advisor",
        instructions=system_prompt,
        model="bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0"
    )

    return agent


def main():
    """
    Main entry point for the Strands Agent with AgentCore integration
    Memory is automatically managed by AgentCore when deployed
    """
    print("🚀 Strands Agent with AgentCore - AWS Lambda Cost Advisor")
    print("=" * 70)

    # Get configuration from environment
    mcp_runtime_id = os.getenv('MCP_AGENT_ID', 'aws_lambda_calculator_fastmcp_runtime-qjjkEwHUCs')

    print(f"\n📋 Configuration:")
    print(f"  • MCP Runtime ID: {mcp_runtime_id}")
    print(f"  • Region: {os.getenv('AWS_REGION', 'us-east-1')}")
    print(f"  • Memory: Managed by AgentCore\n")

    # Create agent
    print("🔧 Initializing Strands Agent...")
    agent = create_lambda_cost_advisor_agent(mcp_runtime_id=mcp_runtime_id)

    # Generate session ID for MCP continuity
    session_id = f"lambda-advisor-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    print(f"✓ Agent '{agent.name}' ready!")
    print(f"✓ Session ID: {session_id}\n")

    # Interactive chat loop
    print("💬 Chat with the agent. Type 'exit' to quit.")
    print("💡 Tip: Ask about Lambda costs, comparisons, or pricing info.\n")

    conversation_count = 0

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                print("\n👋 Goodbye!")
                print(f"\n📊 Session Summary:")
                print(f"  • Session ID: {session_id}")
                print(f"  • Messages exchanged: {conversation_count}")
                print(f"  • MCP Runtime: {mcp_runtime_id}")
                break

            if not user_input:
                continue

            conversation_count += 1

            # Check if query is Lambda-related
            is_lambda_query = any(keyword in user_input.lower() for keyword in
                                 ['cost', 'calculate', 'price', 'lambda', 'compare', 'architecture'])

            print("\n🤖 Agent: ", end="", flush=True)

            if is_lambda_query:
                # Use MCP server for Lambda calculations
                print("[Querying MCP server...] ", end="", flush=True)
                mcp_response = invoke_mcp_server(mcp_runtime_id, session_id, user_input)

                # Agent interprets the MCP response
                agent_prompt = f"""User asked: {user_input}

MCP Server Response:
{mcp_response}

Please interpret these results and provide clear, actionable advice to the user."""

                response = agent.run(agent_prompt)
                print(response.text)
            else:
                # General conversation
                response = agent.run(user_input)
                print(response.text)

            print()

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
