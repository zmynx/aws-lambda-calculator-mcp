# Integration Guide - Add Chatbot to Your Existing Setup

This guide shows how to integrate the AWS Lambda Cost Advisor chatbot into your **existing** GitHub Pages website and API Gateway setup.

## Prerequisites

✅ You already have:
- GitHub Pages website deployed
- API Gateway with Lambda backend
- Lambda execution role with appropriate permissions

## Part 1: Add Lambda Handler to Your Existing Lambda

### Option A: Add to Existing Lambda Function

If you want to add the chatbot handler to your current Lambda:

#### Step 1: Copy the Handler Code

Add this to your existing Lambda function (`lambda_function.py` or similar):

```python
import json
import os
import boto3

# Initialize at module level (reused across invocations)
bedrock_agentcore = boto3.client('bedrock-agentcore-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))
AGENT_RUNTIME_ID = os.getenv('AGENT_RUNTIME_ID', 'strands_agent_agentcore_runtime-H37svwDSIJ')

def handle_chatbot(event, context):
    """
    Chatbot-specific handler
    Call this from your main lambda_handler when path is /chat
    """
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',  # Update to your GitHub Pages domain
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
    }

    # Handle OPTIONS for CORS
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'message': 'OK'})}

    try:
        body = json.loads(event.get('body', '{}'))
        user_message = body.get('message', '')
        session_id = body.get('sessionId', f'session-{int(time.time())}')

        if not user_message:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Message is required'})
            }

        # Invoke AgentCore runtime
        response = bedrock_agentcore.invoke_runtime(
            runtimeId=AGENT_RUNTIME_ID,
            sessionId=session_id,
            inputText=user_message
        )

        # Collect response
        agent_response = ""
        if 'output' in response:
            for event_chunk in response['output']:
                if 'chunk' in event_chunk and 'bytes' in event_chunk['chunk']:
                    agent_response += event_chunk['chunk']['bytes'].decode('utf-8')

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'response': agent_response,
                'sessionId': session_id
            })
        }

    except Exception as e:
        print(f"Chatbot error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
```

#### Step 2: Update Your Main Handler

Modify your existing `lambda_handler` to route chatbot requests:

```python
def lambda_handler(event, context):
    """
    Main Lambda handler - routes to different handlers based on path
    """
    path = event.get('path', '')

    # Route chatbot requests
    if path == '/chat' or path.endswith('/chat'):
        return handle_chatbot(event, context)

    # Your existing routes
    elif path == '/your-existing-route':
        return your_existing_handler(event, context)

    # Default
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Not found'})
        }
```

#### Step 3: Add Environment Variables

Add to your Lambda configuration:

```bash
aws lambda update-function-configuration \
  --function-name YOUR_EXISTING_LAMBDA_NAME \
  --environment Variables="{
    AGENT_RUNTIME_ID=strands_agent_agentcore_runtime-H37svwDSIJ,
    AWS_REGION=us-east-1,
    ...YOUR_EXISTING_ENV_VARS...
  }"
```

Or via AWS Console:
1. Go to Lambda > Functions > YOUR_FUNCTION
2. Configuration > Environment variables
3. Add:
   - `AGENT_RUNTIME_ID`: `strands_agent_agentcore_runtime-H37svwDSIJ`
   - `AWS_REGION`: `us-east-1`

#### Step 4: Update IAM Permissions

Add Bedrock AgentCore permissions to your existing Lambda role:

```bash
# Create policy document
cat > agentcore-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "bedrock-agentcore-runtime:InvokeRuntime",
      "Resource": "arn:aws:bedrock-agentcore:us-east-1:006262944085:runtime/strands_agent_agentcore_runtime-H37svwDSIJ"
    }
  ]
}
EOF

# Create and attach policy
aws iam create-policy \
  --policy-name ChatbotAgentCoreAccess \
  --policy-document file://agentcore-policy.json

aws iam attach-role-policy \
  --role-name YOUR_EXISTING_LAMBDA_ROLE \
  --policy-arn arn:aws:iam::006262944085:policy/ChatbotAgentCoreAccess
```

### Option B: Create Separate Lambda Function

If you prefer isolation, create a dedicated Lambda function:

```bash
cd lambda-handler
pip install -r requirements.txt -t .
zip -r chatbot-lambda.zip .

aws lambda create-function \
  --function-name chatbot-agent-handler \
  --runtime python3.11 \
  --role arn:aws:iam::006262944085:role/YOUR_LAMBDA_ROLE \
  --handler index.lambda_handler \
  --zip-file fileb://chatbot-lambda.zip \
  --timeout 30 \
  --environment Variables="{AGENT_RUNTIME_ID=strands_agent_agentcore_runtime-H37svwDSIJ,AWS_REGION=us-east-1}"
```

## Part 2: Add Route to Your Existing API Gateway

### Step 1: Add /chat Resource

Via AWS Console:
1. Go to API Gateway > Your API
2. Select root `/` resource
3. Actions > Create Resource
4. Resource Name: `chat`
5. Resource Path: `/chat`
6. Create Resource

Via AWS CLI:
```bash
# Get your API ID
API_ID="your-api-id"

# Get root resource ID
ROOT_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query 'items[?path==`/`].id' --output text)

# Create /chat resource
aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part chat
```

### Step 2: Add POST Method

Via AWS Console:
1. Select `/chat` resource
2. Actions > Create Method
3. Select `POST` from dropdown
4. Integration type: Lambda Function
5. Lambda Function: Your function name
6. Use Lambda Proxy integration: ✅ Check this!
7. Save

Via AWS CLI:
```bash
# Get chat resource ID
CHAT_RESOURCE_ID=$(aws apigateway get-resources \
  --rest-api-id $API_ID \
  --query 'items[?path==`/chat`].id' \
  --output text)

# Create POST method
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $CHAT_RESOURCE_ID \
  --http-method POST \
  --authorization-type NONE

# Add Lambda integration
aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $CHAT_RESOURCE_ID \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:006262944085:function:YOUR_FUNCTION_NAME/invocations
```

### Step 3: Enable CORS for /chat

Via AWS Console:
1. Select `/chat` resource
2. Actions > Enable CORS
3. Configure:
   - Access-Control-Allow-Origin: `*` (or your GitHub Pages URL)
   - Access-Control-Allow-Headers: `Content-Type,X-Amz-Date,Authorization`
   - Access-Control-Allow-Methods: POST,OPTIONS
4. Enable CORS

Via AWS CLI:
```bash
# Add OPTIONS method for CORS
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $CHAT_RESOURCE_ID \
  --http-method OPTIONS \
  --authorization-type NONE

# Add OPTIONS integration (Mock)
aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $CHAT_RESOURCE_ID \
  --http-method OPTIONS \
  --type MOCK \
  --request-templates '{"application/json": "{\"statusCode\": 200}"}'

# Add OPTIONS method response
aws apigateway put-method-response \
  --rest-api-id $API_ID \
  --resource-id $CHAT_RESOURCE_ID \
  --http-method OPTIONS \
  --status-code 200 \
  --response-parameters '{
    "method.response.header.Access-Control-Allow-Origin": false,
    "method.response.header.Access-Control-Allow-Methods": false,
    "method.response.header.Access-Control-Allow-Headers": false
  }'

# Add OPTIONS integration response
aws apigateway put-integration-response \
  --rest-api-id $API_ID \
  --resource-id $CHAT_RESOURCE_ID \
  --http-method OPTIONS \
  --status-code 200 \
  --response-parameters '{
    "method.response.header.Access-Control-Allow-Origin": "'"'"'*'"'"'",
    "method.response.header.Access-Control-Allow-Methods": "'"'"'POST,OPTIONS'"'"'",
    "method.response.header.Access-Control-Allow-Headers": "'"'"'Content-Type,X-Amz-Date,Authorization'"'"'"
  }'
```

### Step 4: Deploy API

Via AWS Console:
1. Actions > Deploy API
2. Deployment stage: Select your stage (e.g., `prod`)
3. Deploy

Via AWS CLI:
```bash
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod \
  --description "Added chatbot /chat endpoint"
```

### Step 5: Grant API Gateway Permission to Invoke Lambda

```bash
aws lambda add-permission \
  --function-name YOUR_FUNCTION_NAME \
  --statement-id apigateway-chatbot-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:006262944085:$API_ID/*/POST/chat"
```

### Step 6: Test the Endpoint

```bash
# Your endpoint will be
ENDPOINT="https://$API_ID.execute-api.us-east-1.amazonaws.com/prod/chat"

# Test it
curl -X POST $ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Calculate Lambda costs for 1M requests",
    "sessionId": "test-123"
  }'
```

Expected response:
```json
{
  "response": "I'll help you calculate...",
  "sessionId": "test-123"
}
```

## Part 3: Add Chatbot Widget to Your GitHub Pages Site

### Option A: Add to Existing React/Vite Site

If your GitHub Pages site is already React + Vite:

#### 1. Copy Component Files

Copy these files to your project:

```bash
# Copy chatbot components
cp -r src/components/ChatWidget.jsx your-site/src/components/
cp -r src/components/ChatWidget.css your-site/src/components/
cp -r src/components/ChatMessage.jsx your-site/src/components/
cp -r src/components/ChatMessage.css your-site/src/components/
cp -r src/components/ChatInput.jsx your-site/src/components/
cp -r src/components/ChatInput.css your-site/src/components/
```

#### 2. Add to Your App

```javascript
// your-site/src/App.jsx (or main layout component)
import ChatWidget from './components/ChatWidget'

function App() {
  return (
    <>
      {/* Your existing content */}
      <YourHeader />
      <YourMainContent />
      <YourFooter />

      {/* Add chatbot widget */}
      <ChatWidget />
    </>
  )
}
```

#### 3. Configure API Endpoint

Update your `.env.production`:

```bash
VITE_API_ENDPOINT=https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/chat
```

#### 4. Rebuild and Deploy

```bash
npm run build
npm run deploy  # or your deployment script
```

### Option B: Add to Static HTML Site

If your GitHub Pages site is plain HTML/CSS/JS:

#### 1. Build the Chatbot

```bash
cd streamlit-chatbot-app
npm run build
```

This creates `dist/` folder with:
- `dist/assets/index-HASH.js`
- `dist/assets/index-HASH.css`

#### 2. Copy Build Files

```bash
# Copy to your site's assets folder
cp -r dist/assets/* your-github-pages-site/assets/chatbot/
```

#### 3. Add to Your HTML Pages

Add to every HTML page where you want the chatbot:

```html
<!DOCTYPE html>
<html>
<head>
  <!-- Your existing head content -->

  <!-- Chatbot CSS -->
  <link rel="stylesheet" href="/assets/chatbot/index-HASH.css">
</head>
<body>
  <!-- Your existing content -->

  <!-- Chatbot mount point -->
  <div id="chatbot-root"></div>

  <!-- Chatbot script -->
  <script type="module" src="/assets/chatbot/index-HASH.js"></script>

  <!-- Configure API endpoint -->
  <script>
    window.VITE_API_ENDPOINT = 'https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/chat';
  </script>
</body>
</html>
```

**Note**: Replace `HASH` with actual hash from build output.

#### 4. Update API Endpoint in Build

Before building, update `src/components/ChatWidget.jsx`:

```javascript
const API_ENDPOINT = window.VITE_API_ENDPOINT ||
                     import.meta.env.VITE_API_ENDPOINT ||
                     'https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/chat'
```

### Option C: Include as External Component

Host the chatbot as a separate subdomain or path:

```html
<!-- In your main site -->
<script src="https://yourusername.github.io/chatbot-widget/widget.js"></script>
<script>
  ChatbotWidget.init({
    apiEndpoint: 'https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/chat'
  });
</script>
```

## Part 4: Testing the Integration

### 1. Test Backend

```bash
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "sessionId": "test"}'
```

### 2. Test CORS

```bash
curl -X OPTIONS https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/chat \
  -H "Origin: https://yourusername.github.io" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

Should see:
```
< Access-Control-Allow-Origin: *
< Access-Control-Allow-Methods: POST,OPTIONS
```

### 3. Test Frontend

1. Open your GitHub Pages site
2. Look for chat bubble in bottom-right corner
3. Click to open
4. Send a test message
5. Should see "Thinking..." then response

## Troubleshooting

### Issue: CORS Error

**Symptom**: Browser console shows "blocked by CORS policy"

**Fix**:
1. Verify OPTIONS method exists for `/chat`
2. Check Access-Control-Allow-Origin header
3. Rebuild API Gateway deployment
4. Clear browser cache

### Issue: 403 Forbidden on Lambda

**Symptom**: "User is not authorized to perform: bedrock-agentcore-runtime:InvokeRuntime"

**Fix**:
```bash
# Verify IAM policy is attached
aws iam list-attached-role-policies --role-name YOUR_LAMBDA_ROLE

# Should see ChatbotAgentCoreAccess policy
```

### Issue: Widget Not Appearing

**Fix**:
1. Check browser console for errors
2. Verify JavaScript is loaded
3. Check `<div id="chatbot-root"></div>` exists
4. Verify CSS is loaded

### Issue: Network Error

**Fix**:
1. Check API endpoint URL is correct
2. Test endpoint with curl
3. Verify API Gateway is deployed
4. Check CloudWatch Logs

## Summary Checklist

Backend:
- [ ] Lambda handler code added
- [ ] Environment variables set
- [ ] IAM permissions added
- [ ] API Gateway `/chat` resource created
- [ ] POST method added with Lambda integration
- [ ] CORS enabled
- [ ] API deployed
- [ ] Endpoint tested with curl

Frontend:
- [ ] Chatbot components copied/added
- [ ] API endpoint configured
- [ ] Built and deployed
- [ ] Widget appears on site
- [ ] Messages send successfully
- [ ] Responses received

## Next Steps

After integration:
1. **Update CORS**: Change `*` to your specific GitHub Pages domain
2. **Add Rate Limiting**: Configure API Gateway throttling
3. **Monitor Costs**: Check CloudWatch for usage
4. **Customize UI**: Update colors/branding
5. **Add Analytics**: Track chatbot usage

## Need Help?

- 📖 Full deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- 📝 Lambda setup: [lambda-handler/README.md](lambda-handler/README.md)
- 🐛 Issues: Open a GitHub issue
- 📧 Email: lior.dux@develeap.com
