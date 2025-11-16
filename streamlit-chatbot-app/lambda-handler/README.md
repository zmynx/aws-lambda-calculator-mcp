# Lambda Handler for Chatbot API

This Lambda function serves as a proxy between your GitHub Pages frontend and your AWS Bedrock AgentCore runtime.

## Setup Instructions

### 1. Add to Your Existing Lambda (Option A)

If you want to add this to an existing Lambda function:

1. Copy the handler code from `index.py` into your existing Lambda
2. Add a new route in API Gateway: `POST /chat`
3. Point the route to your Lambda function
4. Set environment variables (see below)

### 2. Create New Lambda Function (Option B)

If you prefer a dedicated Lambda:

```bash
# Create deployment package
cd lambda-handler
pip install -r requirements.txt -t .
zip -r chatbot-lambda.zip .

# Upload to AWS Lambda via CLI
aws lambda create-function \
  --function-name chatbot-agentcore-proxy \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/YOUR_LAMBDA_ROLE \
  --handler index.lambda_handler \
  --zip-file fileb://chatbot-lambda.zip \
  --timeout 30 \
  --environment Variables="{AGENT_RUNTIME_ID=strands_agent_agentcore_runtime-H37svwDSIJ,AWS_REGION=us-east-1}"
```

### 3. Environment Variables

Set these in your Lambda configuration:

| Variable | Value | Description |
|----------|-------|-------------|
| `AGENT_RUNTIME_ID` | `strands_agent_agentcore_runtime-H37svwDSIJ` | Your AgentCore runtime ID |
| `AWS_REGION` | `us-east-1` | AWS region where agent is deployed |

### 4. IAM Permissions

Your Lambda execution role needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock-agentcore-runtime:InvokeRuntime"
      ],
      "Resource": "arn:aws:bedrock-agentcore:us-east-1:006262944085:runtime/strands_agent_agentcore_runtime-H37svwDSIJ"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

### 5. API Gateway Configuration

#### Add Route to Existing API Gateway:

1. Go to API Gateway console
2. Select your existing API
3. Create new resource: `/chat`
4. Add method: `POST`
5. Integration type: Lambda Function
6. Select your Lambda function
7. Enable CORS
8. Deploy to your stage

#### CORS Configuration:

Make sure CORS is enabled with these headers:
- `Access-Control-Allow-Origin: *` (or your specific GitHub Pages domain)
- `Access-Control-Allow-Headers: Content-Type`
- `Access-Control-Allow-Methods: POST, OPTIONS`

### 6. Update Frontend Configuration

Create `.env.local` in your React app:

```bash
VITE_API_ENDPOINT=https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/prod/chat
```

Or update `VITE_API_ENDPOINT` in your GitHub Pages deployment settings.

## Testing

### Test Locally with curl:

```bash
curl -X POST https://your-api-gateway-url/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Calculate Lambda costs for 1M requests with 512MB memory",
    "sessionId": "test-session-123"
  }'
```

Expected response:
```json
{
  "response": "I'll help you calculate AWS Lambda costs...",
  "sessionId": "test-session-123"
}
```

### Test with Frontend:

1. Update `.env.local` with your API endpoint
2. Run `npm run dev`
3. Click the chat bubble
4. Send a test message

## Request/Response Format

### Request:
```json
{
  "message": "user's question here",
  "sessionId": "unique-session-id"
}
```

### Response (Success):
```json
{
  "response": "agent's response text",
  "sessionId": "session-id"
}
```

### Response (Error):
```json
{
  "error": "error message"
}
```

## Troubleshooting

### CORS Errors
- Verify CORS is enabled in API Gateway
- Check `Access-Control-Allow-Origin` matches your domain
- Ensure OPTIONS method is configured

### 403 Forbidden
- Check Lambda IAM role has `bedrock-agentcore-runtime:InvokeRuntime` permission
- Verify API Gateway has permission to invoke Lambda

### 500 Internal Server Error
- Check CloudWatch Logs for Lambda errors
- Verify `AGENT_RUNTIME_ID` environment variable is correct
- Ensure AgentCore runtime is deployed and accessible

### Timeout
- Increase Lambda timeout (default is 3s, recommend 30s)
- Check if AgentCore runtime is responding

## Cost Optimization

- Lambda execution: ~$0.20 per 1M requests (128MB memory)
- API Gateway: $3.50 per 1M requests
- AgentCore runtime: Based on usage
- Total estimated cost: ~$4-5 per 1M chatbot interactions

## Security Best Practices

1. **CORS**: Configure specific origin instead of `*` in production
2. **Rate Limiting**: Add throttling in API Gateway
3. **Authentication**: Consider adding API key or Cognito auth
4. **Input Validation**: Sanitize user input
5. **Secrets**: Use AWS Secrets Manager for sensitive config

## Monitoring

CloudWatch metrics to monitor:
- Lambda invocations
- Lambda errors
- Lambda duration
- API Gateway 4XX/5XX errors
- AgentCore runtime calls
