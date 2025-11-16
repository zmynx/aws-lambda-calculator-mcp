/**
 * Development proxy server for testing chatbot with live AgentCore runtime
 * Uses AWS SDK to call bedrock-agentcore-runtime API
 */

import express from 'express';
import cors from 'cors';
import { fromNodeProviderChain } from '@aws-sdk/credential-providers';
import { SignatureV4 } from '@smithy/signature-v4';
import { HttpRequest } from '@smithy/protocol-http';
import { Sha256 } from '@aws-crypto/sha256-js';

const app = express();
const PORT = 3001;

// Your AgentCore runtime configuration
const AGENT_RUNTIME_ARN = process.env.AGENT_RUNTIME_ARN || 'arn:aws:bedrock-agentcore:us-east-1:006262944085:runtime/strands_agent_agentcore_runtime-H37svwDSIJ';
const AWS_REGION = process.env.AWS_REGION || 'us-east-1';

// Enable CORS for local development
app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', agentArn: AGENT_RUNTIME_ARN, region: AWS_REGION });
});

// Chat endpoint
app.post('/chat', async (req, res) => {
  try {
    const { message, sessionId } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    console.log(`\n📩 Received message: "${message}"`);
    console.log(`🔑 Session ID: ${sessionId}`);
    console.log(`🤖 Agent Runtime ARN: ${AGENT_RUNTIME_ARN}`);

    // Get AWS credentials
    const credentialsProvider = fromNodeProviderChain();
    const credentials = await credentialsProvider();

    // Prepare request - using bedrock-agentcore service
    const endpoint = `https://bedrock-agentcore.${AWS_REGION}.amazonaws.com`;
    const path = `/invoke-agent-runtime`;

    const requestBody = JSON.stringify({
      runtimeArn: AGENT_RUNTIME_ARN,
      runtimeSessionId: sessionId || `dev-session-${Date.now()}`,
      inputText: message,
    });

    // Create HTTP request
    const request = new HttpRequest({
      method: 'POST',
      protocol: 'https:',
      hostname: `bedrock-agentcore.${AWS_REGION}.amazonaws.com`,
      path: path,
      headers: {
        'Content-Type': 'application/json',
        'Host': `bedrock-agentcore.${AWS_REGION}.amazonaws.com`,
      },
      body: requestBody,
    });

    // Sign request with SigV4
    const signer = new SignatureV4({
      credentials: credentials,
      region: AWS_REGION,
      service: 'bedrock-agentcore',
      sha256: Sha256,
    });

    const signedRequest = await signer.sign(request);

    console.log(`⏳ Invoking agent at ${endpoint}${path}...`);

    // Make the request
    const response = await fetch(`${endpoint}${path}`, {
      method: signedRequest.method,
      headers: signedRequest.headers,
      body: signedRequest.body,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ API Error (${response.status}):`, errorText);
      throw new Error(`AgentCore API error: ${response.status} - ${errorText}`);
    }

    // Read response body
    const responseData = await response.json();
    console.log(`✅ Response:`, responseData);

    // Extract agent response
    const agentResponse = responseData.output || responseData.completion || 'No response from agent';

    res.json({
      response: agentResponse,
      sessionId: sessionId,
    });

  } catch (error) {
    console.error('❌ Error:', error);

    res.status(500).json({
      error: 'Internal server error',
      details: error.message,
      name: error.name,
    });
  }
});

app.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║  🚀 Development Proxy Server Running                       ║
╟────────────────────────────────────────────────────────────╢
║  URL:        http://localhost:${PORT}                         ║
║  Endpoint:   http://localhost:${PORT}/chat                    ║
║  Health:     http://localhost:${PORT}/health                  ║
║                                                            ║
║  Agent ARN:  ${AGENT_RUNTIME_ARN.substring(0, 60)}... ║
║  Region:     ${AWS_REGION}                                      ║
╟────────────────────────────────────────────────────────────╢
║  Using AWS credentials from your local profile             ║
╚════════════════════════════════════════════════════════════╝
  `);
});
