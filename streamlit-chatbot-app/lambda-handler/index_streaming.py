"""
Lambda handler with streaming response support for chatbot API
Uses Lambda Response Streaming for real-time agent responses
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
    Handle POST /chat requests with streaming support

    For Lambda Response Streaming, the function URL must be configured with InvokeMode: RESPONSE_STREAM
    """

    # Enable CORS headers
    headers = {
        'Content-Type': 'text/event-stream',  # Server-Sent Events
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    }

    # Handle OPTIONS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'OK'})
        }

    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        user_message = body.get('message', '')
        session_id = body.get('sessionId', f'session-{int(datetime.now().timestamp())}')

        if not user_message:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', **headers},
                'body': json.dumps({'error': 'Message is required'})
            }

        print(f"Processing streaming message for session {session_id}")

        # For standard Lambda (non-streaming function URL)
        # We'll collect chunks and send back complete response
        # If you configure Lambda Function URL with RESPONSE_STREAM,
        # you can use awslambdaric.streaming for true streaming

        response = bedrock_agentcore.invoke_runtime(
            runtimeId=AGENT_RUNTIME_ID,
            sessionId=session_id,
            inputText=user_message
        )

        # Collect all chunks
        chunks = []
        if 'output' in response:
            for event_chunk in response['output']:
                if 'chunk' in event_chunk and 'bytes' in event_chunk['chunk']:
                    chunk_text = event_chunk['chunk']['bytes'].decode('utf-8')
                    chunks.append(chunk_text)

        full_response = ''.join(chunks)

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', **headers},
            'body': json.dumps({
                'response': full_response,
                'sessionId': session_id,
                'streaming': False  # Indicates this is not true streaming
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', **headers},
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }


# Alternative: True streaming handler for Lambda Function URLs with RESPONSE_STREAM mode
# Requires Lambda Function URL with InvokeMode set to RESPONSE_STREAM
def streaming_lambda_handler(event, response_stream, context):
    """
    True streaming handler using Lambda Response Streaming
    Configure your Lambda Function URL with InvokeMode: RESPONSE_STREAM
    """
    import awslambdaric

    try:
        body = json.loads(event.get('body', '{}'))
        user_message = body.get('message', '')
        session_id = body.get('sessionId', f'session-{int(datetime.now().timestamp())}')

        # Send headers
        response_stream.write(
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: text/event-stream\r\n"
            f"Access-Control-Allow-Origin: *\r\n"
            f"Cache-Control: no-cache\r\n"
            f"Connection: keep-alive\r\n\r\n"
        )

        # Send initial thinking event
        response_stream.write(f"data: {json.dumps({'type': 'thinking', 'content': 'Thinking...'})}\n\n")
        response_stream.flush()

        # Invoke AgentCore runtime
        response = bedrock_agentcore.invoke_runtime(
            runtimeId=AGENT_RUNTIME_ID,
            sessionId=session_id,
            inputText=user_message
        )

        # Stream chunks as they arrive
        if 'output' in response:
            for event_chunk in response['output']:
                if 'chunk' in event_chunk and 'bytes' in event_chunk['chunk']:
                    chunk_text = event_chunk['chunk']['bytes'].decode('utf-8')

                    # Send chunk via Server-Sent Events
                    response_stream.write(
                        f"data: {json.dumps({'type': 'chunk', 'content': chunk_text})}\n\n"
                    )
                    response_stream.flush()

        # Send completion event
        response_stream.write(f"data: {json.dumps({'type': 'done'})}\n\n")
        response_stream.flush()

    except Exception as e:
        print(f"Streaming error: {str(e)}")
        response_stream.write(
            f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        )
        response_stream.flush()
