"""
Lambda handler for chatbot API Gateway endpoint
Proxies requests to AWS Bedrock AgentCore Runtime
"""

import json
import os
import boto3
from datetime import datetime

# Initialize Bedrock AgentCore Runtime client
bedrock_agentcore = boto3.client('bedrock-agentcore-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))

# Your AgentCore runtime ID from deployment
AGENT_RUNTIME_ID = os.getenv('AGENT_RUNTIME_ID', 'strands_agent_agentcore_runtime-H37svwDSIJ')


def lambda_handler(event, context):
    """
    Handle POST /chat requests from the frontend chatbot

    Expected request body:
    {
        "message": "user's message",
        "sessionId": "session-12345"
    }

    Response:
    {
        "response": "agent's response"
    }
    """

    # Enable CORS
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',  # Configure this to your GitHub Pages domain in production
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
    }

    # Handle OPTIONS preflight request
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'OK'})
        }

    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        user_message = body.get('message', '')
        session_id = body.get('sessionId', f'session-{int(datetime.now().timestamp())}')

        if not user_message:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Message is required'})
            }

        print(f"Processing message for session {session_id}: {user_message}")

        # Invoke AgentCore runtime
        response = bedrock_agentcore.invoke_runtime(
            runtimeId=AGENT_RUNTIME_ID,
            sessionId=session_id,
            inputText=user_message
        )

        # Collect streaming response
        agent_response = ""
        if 'output' in response:
            for event_chunk in response['output']:
                if 'chunk' in event_chunk and 'bytes' in event_chunk['chunk']:
                    agent_response += event_chunk['chunk']['bytes'].decode('utf-8')

        print(f"Agent response: {agent_response[:100]}...")

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'response': agent_response,
                'sessionId': session_id
            })
        }

    except bedrock_agentcore.exceptions.ValidationException as e:
        print(f"Validation error: {str(e)}")
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': f'Validation error: {str(e)}'})
        }

    except bedrock_agentcore.exceptions.ResourceNotFoundException as e:
        print(f"Resource not found: {str(e)}")
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': f'Agent runtime not found: {str(e)}'})
        }

    except Exception as e:
        print(f"Error invoking agent: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
