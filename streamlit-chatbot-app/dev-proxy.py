#!/usr/bin/env python3
"""
Development proxy server for testing chatbot with live AgentCore runtime
Uses boto3 to call bedrock-agentcore API directly
"""

import json
import os
import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for local development

# Your AgentCore runtime configuration
AGENT_RUNTIME_ARN = os.getenv(
    'AGENT_RUNTIME_ARN',
    'arn:aws:bedrock-agentcore:us-east-1:006262944085:runtime/strands_agent_agentcore_runtime-H37svwDSIJ'
)
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# Initialize Bedrock AgentCore client
bedrock_agentcore = boto3.client('bedrock-agentcore', region_name=AWS_REGION)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'agentArn': AGENT_RUNTIME_ARN,
        'region': AWS_REGION
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint that invokes AgentCore runtime"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        session_id = data.get('sessionId', f'dev-session-{int(__import__("time").time())}')

        if not message:
            return jsonify({'error': 'Message is required'}), 400

        print(f"\n📩 Received message: \"{message}\"")
        print(f"🔑 Session ID: {session_id}")
        print(f"🤖 Agent Runtime ARN: {AGENT_RUNTIME_ARN}")
        print(f"⏳ Invoking agent...")

        # Generate a proper session ID (min 33 chars)
        if not session_id or len(session_id) < 33:
            import uuid
            session_id = f"session-{uuid.uuid4()}"

        # Invoke AgentCore runtime with correct parameters
        # Payload must be JSON bytes with 'prompt' key
        payload_dict = {'prompt': message}
        payload_bytes = json.dumps(payload_dict).encode('utf-8')

        response = bedrock_agentcore.invoke_agent_runtime(
            agentRuntimeArn=AGENT_RUNTIME_ARN,
            runtimeSessionId=session_id,
            payload=payload_bytes,
            contentType='application/json',
            accept='application/json'
        )

        print(f"✅ Response received")
        print(f"Response keys: {response.keys()}")

        # Extract response from the streaming response body
        agent_response = ""

        if 'response' in response:
            # Read the streaming body
            streaming_body = response['response']
            agent_response = streaming_body.read().decode('utf-8')
            print(f"📄 Agent response: {agent_response}")
        elif 'completion' in response:
            # Handle streaming response (alternative format)
            for event in response['completion']:
                print(f"Event: {event}")
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        chunk_text = chunk['bytes'].decode('utf-8')
                        agent_response += chunk_text
                        print(chunk_text, end='', flush=True)

        print(f"\n✅ Agent response complete ({len(agent_response)} chars)\n")

        return jsonify({
            'response': agent_response or 'No response from agent',
            'sessionId': session_id
        })

    except Exception as e:
        import traceback
        print(f"❌ Error: {e}", flush=True)
        print(f"Error type: {type(e).__name__}", flush=True)
        print(f"Traceback:", flush=True)
        traceback.print_exc()

        return jsonify({
            'error': 'Internal server error',
            'details': str(e),
            'type': type(e).__name__
        }), 500

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════╗
║  🚀 Development Proxy Server Running (Python)              ║
╟────────────────────────────────────────────────────────────╢
║  URL:        http://localhost:3001                         ║
║  Endpoint:   http://localhost:3001/chat                    ║
║  Health:     http://localhost:3001/health                  ║
║                                                            ║
║  Agent ARN:  {}... ║
║  Region:     {}                                      ║
╟────────────────────────────────────────────────────────────╢
║  Using AWS credentials from your local profile             ║
╚════════════════════════════════════════════════════════════╝
    """.format(AGENT_RUNTIME_ARN[:60], AWS_REGION))

    app.run(host='localhost', port=3001, debug=True)
