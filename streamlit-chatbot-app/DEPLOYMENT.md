# Deployment Guide - AWS Lambda Cost Advisor Chatbot

This guide covers deploying both the frontend (GitHub Pages) and backend (AWS Lambda + API Gateway).

## Architecture Overview

```
┌─────────────────┐
│  GitHub Pages   │
│  (React App)    │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  API Gateway    │
│   /chat route   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐       ┌──────────────────────┐
│  Lambda Proxy   │──────>│ Bedrock AgentCore    │
│   Function      │       │ strands_agent_...    │
└─────────────────┘       └──────────────────────┘
```

## Part 1: Deploy Backend (Lambda + API Gateway)

### Step 1: Deploy Lambda Function

You have two options:

#### Option A: Add to Existing Lambda

If you already have a Lambda function with API Gateway:

1. Add the handler code to your existing Lambda function
2. Add environment variables
3. Update IAM permissions
4. Add new route to API Gateway

#### Option B: Create New Lambda Function

```bash
cd lambda-handler

# Install dependencies
pip install -r requirements.txt -t .

# Create deployment package
zip -r chatbot-lambda.zip .

# Create Lambda function
aws lambda create-function \
  --function-name chatbot-agentcore-proxy \
  --runtime python3.11 \
  --role arn:aws:iam::006262944085:role/YOUR_LAMBDA_ROLE \
  --handler index.lambda_handler \
  --zip-file fileb://chatbot-lambda.zip \
  --timeout 30 \
  --memory-size 256 \
  --environment Variables="{AGENT_RUNTIME_ID=strands_agent_agentcore_runtime-H37svwDSIJ,AWS_REGION=us-east-1}" \
  --region us-east-1
```

### Step 2: Configure IAM Permissions

Your Lambda execution role needs:

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

Apply permissions:

```bash
# Create policy
aws iam create-policy \
  --policy-name ChatbotAgentCorePolicy \
  --policy-document file://iam-policy.json

# Attach to Lambda role
aws iam attach-role-policy \
  --role-name YOUR_LAMBDA_ROLE \
  --policy-arn arn:aws:iam::006262944085:policy/ChatbotAgentCorePolicy
```

### Step 3: Configure API Gateway

#### Create or Update API Gateway:

1. Go to API Gateway Console
2. Select your API (or create new REST API)
3. Create resource: `/chat`
4. Add method: `POST`
   - Integration type: Lambda Function
   - Lambda Function: `chatbot-agentcore-proxy`
   - Use Lambda Proxy integration: Yes
5. Add method: `OPTIONS` (for CORS)
   - Integration type: Mock
6. Deploy to stage (e.g., `prod`)

#### Enable CORS:

Select the `/chat` resource and enable CORS with:
- Access-Control-Allow-Origin: `*` (or your specific GitHub Pages URL)
- Access-Control-Allow-Headers: `Content-Type,X-Amz-Date,Authorization,X-Api-Key`
- Access-Control-Allow-Methods: `POST,OPTIONS`

#### Get API Endpoint:

After deployment, your endpoint will be:
```
https://{api-id}.execute-api.us-east-1.amazonaws.com/{stage}/chat
```

Example:
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/chat
```

### Step 4: Test Backend

```bash
curl -X POST https://YOUR_API_ENDPOINT/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Calculate Lambda costs for 1M requests with 512MB memory and 200ms duration",
    "sessionId": "test-123"
  }'
```

Expected response:
```json
{
  "response": "I'll help you calculate AWS Lambda costs...",
  "sessionId": "test-123"
}
```

## Part 2: Deploy Frontend (GitHub Pages)

### Step 1: Configure Environment

Create `.env.production`:

```bash
VITE_API_ENDPOINT=https://YOUR_API_ENDPOINT/chat
```

Example:
```bash
VITE_API_ENDPOINT=https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/chat
```

### Step 2: Update vite.config.js

If deploying to a project page (not user/org page):

```javascript
export default defineConfig({
  plugins: [react()],
  base: '/your-repo-name/', // e.g., '/lambda-chatbot/'
})
```

If deploying to user/org page (username.github.io):

```javascript
export default defineConfig({
  plugins: [react()],
  base: '/', // Keep as is
})
```

### Step 3: Initialize Git Repository

```bash
# If not already a git repo
git init
git add .
git commit -m "Initial commit: AWS Lambda Cost Advisor chatbot"

# Create GitHub repository and link
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 4: Deploy to GitHub Pages

#### Option A: Automated with gh-pages

```bash
# Build and deploy
npm run deploy
```

This will:
1. Build the production bundle
2. Push to `gh-pages` branch
3. Deploy automatically

#### Option B: Manual Deployment

```bash
# Build
npm run build

# The dist folder contains your static files
# Upload to gh-pages branch or use GitHub Actions
```

#### Option C: GitHub Actions (Recommended for CI/CD)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout
      uses: actions/checkout@v4

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'

    - name: Install dependencies
      run: npm ci

    - name: Build
      env:
        VITE_API_ENDPOINT: ${{ secrets.VITE_API_ENDPOINT }}
      run: npm run build

    - name: Setup Pages
      uses: actions/configure-pages@v4

    - name: Upload artifact
      uses: actions/upload-pages-artifact@v3
      with:
        path: './dist'

    - name: Deploy to GitHub Pages
      uses: actions/deploy-pages@v4
```

Add your API endpoint as a secret:
1. Go to repository Settings > Secrets and variables > Actions
2. Add `VITE_API_ENDPOINT` with your API Gateway URL

### Step 5: Configure GitHub Pages

1. Go to repository Settings
2. Navigate to Pages
3. Source: Deploy from a branch
4. Branch: `gh-pages` (if using gh-pages package) or `main` + `/dist` (if manual)
5. Save

Your site will be available at:
- User/Org page: `https://USERNAME.github.io/`
- Project page: `https://USERNAME.github.io/REPO_NAME/`

## Part 3: Embedding in Existing Website

### Option 1: Floating Widget (Recommended)

The app is already configured as a floating widget. Just deploy and it works!

### Option 2: Embed as Component

If you have an existing React site:

```javascript
import ChatWidget from './components/ChatWidget'

function YourPage() {
  return (
    <div>
      <h1>Your Content</h1>
      {/* ... */}
      <ChatWidget />
    </div>
  )
}
```

### Option 3: Embed in Static HTML Site

Add to your HTML pages:

```html
<!-- In <head> -->
<link rel="stylesheet" href="https://USERNAME.github.io/REPO_NAME/assets/index.css">

<!-- Before </body> -->
<div id="chatbot-root"></div>
<script type="module" src="https://USERNAME.github.io/REPO_NAME/assets/index.js"></script>
```

## Testing

### Test Locally

```bash
# Start dev server
npm run dev

# Visit http://localhost:5173
# Click chat bubble, send a message
```

### Test Production Build

```bash
# Build
npm run build

# Preview
npm run preview

# Visit http://localhost:4173
```

### Test Deployed Version

1. Visit your GitHub Pages URL
2. Click the chat bubble in bottom-right
3. Send test message: "Calculate costs for 1M Lambda requests"
4. Should see "Thinking..." then response from agent

## Troubleshooting

### CORS Errors

**Error**: `Access to fetch blocked by CORS policy`

**Fix**:
1. Verify API Gateway CORS is enabled for `/chat`
2. Check `Access-Control-Allow-Origin` includes your GitHub Pages domain
3. Ensure `OPTIONS` method exists and returns 200

### 403 Forbidden / Permission Denied

**Error**: `User: ... is not authorized to perform: bedrock-agentcore-runtime:InvokeRuntime`

**Fix**:
1. Verify Lambda IAM role has bedrock-agentcore-runtime permissions
2. Check resource ARN matches your agent runtime ID
3. Verify agent is deployed and accessible

### API Endpoint Not Found

**Error**: `Failed to fetch` or `404 Not Found`

**Fix**:
1. Check `.env.production` has correct `VITE_API_ENDPOINT`
2. Rebuild after changing env variables: `npm run build`
3. Verify API Gateway endpoint URL is correct
4. Check API Gateway stage is deployed

### Widget Not Appearing

**Fix**:
1. Check browser console for errors
2. Verify CSS is loaded
3. Check if JavaScript is blocked
4. Try hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

### Agent Not Responding

**Error**: Timeout or empty response

**Fix**:
1. Check Lambda CloudWatch Logs for errors
2. Verify `AGENT_RUNTIME_ID` environment variable is correct
3. Test AgentCore runtime directly:
```bash
aws bedrock-agentcore-runtime invoke-runtime \
  --runtime-id strands_agent_agentcore_runtime-H37svwDSIJ \
  --session-id test-123 \
  --input-text "Hello"
```

## Monitoring

### CloudWatch Metrics

Monitor these metrics:
- Lambda Invocations
- Lambda Errors
- Lambda Duration
- API Gateway 4XX/5XX Errors
- API Gateway Latency

### Cost Tracking

Expected costs:
- Lambda: ~$0.20 per 1M requests (128MB, 3s avg)
- API Gateway: ~$3.50 per 1M requests
- AgentCore Runtime: Based on usage
- GitHub Pages: Free
- **Total**: ~$4-5 per 1M chatbot interactions

## Security Best Practices

1. **CORS**: Set specific origin instead of `*` in production
2. **Rate Limiting**: Add API Gateway throttling
3. **API Keys**: Consider requiring API keys
4. **Input Validation**: Sanitize all user inputs
5. **HTTPS**: Always use HTTPS (GitHub Pages + API Gateway both support this)
6. **Secrets**: Never commit .env files

## Updating the Chatbot

### Update Frontend Only

```bash
# Make changes to React code
npm run build
npm run deploy
# Or push to trigger GitHub Actions
```

### Update Backend Only

```bash
cd lambda-handler

# Make changes to index.py
zip -r chatbot-lambda.zip .

aws lambda update-function-code \
  --function-name chatbot-agentcore-proxy \
  --zip-file fileb://chatbot-lambda.zip
```

### Update Environment Variables

```bash
aws lambda update-function-configuration \
  --function-name chatbot-agentcore-proxy \
  --environment Variables="{AGENT_RUNTIME_ID=new-value,AWS_REGION=us-east-1}"
```

## Custom Domain (Optional)

To use a custom domain like `chat.yourdomain.com`:

1. Set up custom domain in API Gateway
2. Configure DNS (CNAME or A record)
3. Update `.env.production` with new endpoint
4. Rebuild and redeploy frontend

## Need Help?

Check:
- [Vite Documentation](https://vitejs.dev/)
- [GitHub Pages Documentation](https://docs.github.com/pages)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [Bedrock AgentCore Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
