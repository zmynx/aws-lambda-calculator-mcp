# AWS Lambda Cost Advisor Chatbot

A beautiful, responsive chatbot widget for your website that provides AWS Lambda cost optimization advice. Powered by AWS Bedrock AgentCore and your deployed Strands Agent.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-green)

## ✨ Features

- 🚀 **Floating Widget**: Non-intrusive chat bubble in bottom-right corner
- 💬 **Real-time Responses**: Connects to AWS Bedrock AgentCore runtime
- 🎨 **Beautiful UI**: Modern gradient design with smooth animations
- 📱 **Fully Responsive**: Works great on desktop, tablet, and mobile
- 🔄 **Session Memory**: Maintains conversation context across messages
- ⚡ **Fast & Lightweight**: Built with Vite for optimal performance
- 🌐 **GitHub Pages Ready**: Deploy as static site for free
- 🎯 **"Thinking..." Indicator**: Shows when agent is processing

## 🎬 Quick Demo

```bash
npm install
npm run dev
```

Visit `http://localhost:5173` - click the chat bubble in the bottom-right corner!

## 📋 Table of Contents

- [Integration Options](#integration-options)
- [Quick Start](#quick-start)
- [Integration into Existing Setup](#integration-into-existing-setup)
- [Backend Setup](#backend-setup)
- [Customization](#customization)
- [Deployment](#deployment)
- [FAQ](#faq)

## 🎨 Integration Options

This chatbot supports three integration modes:

### 1. Floating Widget (Recommended ✨)
Best for most websites - appears as a chat bubble that expands into a popup.
- ✅ Non-intrusive
- ✅ Available on all pages
- ✅ Mobile-friendly
- ✅ Easy to integrate

### 2. Full Page
Dedicated chatbot page with full viewport.
- Good for focused interactions
- Can be linked from navigation

### 3. Embedded (iframe)
Integrated into page content.
- Part of page flow
- Customizable placement

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- AWS Account with Bedrock AgentCore access
- Deployed Strands Agent (see [strands-agent-agentcore-runtime](../strands-agent-agentcore-runtime/))

### Installation

```bash
# Clone or download this folder
cd streamlit-chatbot-app

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your API Gateway endpoint

# Start development server
npm run dev
```

Open `http://localhost:5173` to see the chatbot!

## 🔧 Integration into Existing Setup

**Do you already have GitHub Pages and API Gateway?** Great! Follow these guides:

### For Existing GitHub Pages + API Gateway

📖 **See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** for detailed step-by-step instructions on:

1. **Adding the Lambda handler** to your existing Lambda function
2. **Adding `/chat` route** to your existing API Gateway
3. **Embedding the widget** in your existing GitHub Pages site

**Quick Overview:**

```bash
# 1. Add Lambda handler to your existing function
# Copy code from lambda-handler/index.py

# 2. Add /chat route to your API Gateway
# POST /chat → Your Lambda function

# 3. Add widget to your site
# Copy ChatWidget component or include built files
```

### For New Deployment

📖 **See [DEPLOYMENT.md](DEPLOYMENT.md)** for complete deployment guide including:
- Creating new Lambda function
- Setting up new API Gateway
- Deploying to GitHub Pages from scratch

## 🔌 Backend Setup

### Option 1: Add to Existing Lambda (Recommended)

If you already have an API Gateway + Lambda:

1. **Add handler code** to your existing Lambda:

```python
# Add to your existing lambda_function.py
def handle_chatbot(event, context):
    # Copy from lambda-handler/index.py
    ...

def lambda_handler(event, context):
    path = event.get('path', '')

    if path.endswith('/chat'):
        return handle_chatbot(event, context)

    # Your existing handlers...
```

2. **Add environment variables:**
   - `AGENT_RUNTIME_ID`: Your AgentCore runtime ID
   - `AWS_REGION`: `us-east-1`

3. **Update IAM permissions:**
```json
{
  "Effect": "Allow",
  "Action": "bedrock-agentcore-runtime:InvokeRuntime",
  "Resource": "arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:runtime/YOUR_RUNTIME_ID"
}
```

4. **Add `/chat` route** to your API Gateway:
   - Method: POST
   - Integration: Lambda Proxy
   - Enable CORS

### Option 2: Deploy New Lambda

See [lambda-handler/README.md](lambda-handler/README.md)

### API Endpoint Format

Your endpoint will be:
```
https://{api-id}.execute-api.{region}.amazonaws.com/{stage}/chat
```

Example:
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/chat
```

## 🎨 Customization

### Update Colors

Edit `src/App.css` and component CSS files:

```css
/* Change gradient colors */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* To your brand colors */
background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
```

### Change Initial Message

Edit `src/components/ChatWidget.jsx`:

```javascript
const [messages, setMessages] = useState([
  {
    id: 1,
    type: 'assistant',
    content: "Your custom greeting message!",
    timestamp: new Date()
  }
])
```

### Change Widget Position

Edit `src/components/ChatWidget.css`:

```css
.chat-widget {
  position: fixed;
  bottom: 20px;
  right: 20px;  /* Change to left: 20px for left side */
}
```

## 🚀 Deployment

### Deploy to GitHub Pages

```bash
# 1. Configure API endpoint
echo "VITE_API_ENDPOINT=https://YOUR_API.execute-api.us-east-1.amazonaws.com/prod/chat" > .env.production

# 2. Build and deploy
npm run deploy
```

### GitHub Actions (Automated)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run build
        env:
          VITE_API_ENDPOINT: ${{ secrets.VITE_API_ENDPOINT }}
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
```

Add `VITE_API_ENDPOINT` secret in repository settings.

## 📁 Project Structure

```
streamlit-chatbot-app/
├── src/
│   ├── components/
│   │   ├── ChatWidget.jsx      # Floating widget (main component)
│   │   ├── ChatMessage.jsx     # Message bubble
│   │   ├── ChatInput.jsx       # Input field
│   │   └── ChatHeader.jsx      # Header component
│   ├── App.jsx                 # Full-page chatbot
│   ├── AppWidget.jsx           # Widget demo page
│   └── main.jsx                # Entry point
├── lambda-handler/
│   ├── index.py                # Lambda handler code
│   └── README.md               # Lambda setup guide
├── INTEGRATION_GUIDE.md        # Integration into existing setup
├── DEPLOYMENT.md               # Full deployment guide
├── package.json
└── vite.config.js
```

## 🤔 FAQ

### Do I need WebSocket API for streaming?

**No!** The chatbot works with standard REST API Gateway. The "Thinking..." indicator provides great UX without needing WebSocket or real streaming.

The Lambda collects the full response from AgentCore and returns it as JSON. For true streaming (optional), see `lambda-handler/index_streaming.py` which uses Lambda Function URLs with SSE.

### How do I add this to my existing GitHub Pages site?

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - it has step-by-step instructions for:
- Adding to existing React/Vite site
- Adding to static HTML site
- Adding Lambda handler to existing function
- Adding route to existing API Gateway

### Can I customize the colors/branding?

Yes! All colors and styles are in CSS files. See [Customization](#customization) section.

### How much does it cost?

For 10,000 monthly interactions:
- Lambda: ~$0.002
- API Gateway: ~$0.035
- AgentCore: Based on usage
- GitHub Pages: Free
- **Total**: ~$0.04-0.10/month

### Can I use this with my own agent?

Yes! Just update the `AGENT_RUNTIME_ID` environment variable to point to your deployed AgentCore runtime.

### Does it work on mobile?

Yes! The widget is fully responsive and works great on mobile browsers.

## 📚 Additional Resources

- 📖 [Integration Guide](INTEGRATION_GUIDE.md) - Add to existing setup
- 📖 [Deployment Guide](DEPLOYMENT.md) - Deploy from scratch
- 📖 [Lambda Setup](lambda-handler/README.md) - Backend configuration
- 🔗 [Strands Agents](https://strandsagents.com/)
- 🔗 [AWS Bedrock AgentCore](https://aws.amazon.com/bedrock/)

## 🧪 Testing

```bash
# Local development
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Test backend endpoint
curl -X POST https://YOUR_API/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Calculate Lambda costs", "sessionId": "test"}'
```

## 🛠️ Troubleshooting

### CORS Errors
- Enable CORS in API Gateway for `/chat`
- Check `Access-Control-Allow-Origin` header
- Verify OPTIONS method exists

### 403 Forbidden
- Check Lambda IAM role has `bedrock-agentcore-runtime:InvokeRuntime` permission
- Verify `AGENT_RUNTIME_ID` is correct

### Widget Not Appearing
- Check browser console for errors
- Verify JavaScript and CSS files loaded
- Clear browser cache

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting.

## 📜 License

Apache 2.0

## 👤 Author

**Lior Dux**
📧 Email: lior.dux@develeap.com

## 🙏 Acknowledgments

- Built with [Vite](https://vitejs.dev/) and [React](https://react.dev/)
- Powered by [AWS Bedrock AgentCore](https://aws.amazon.com/bedrock/)
- Uses [Strands Agents](https://strandsagents.com/)

---

⭐ **Star this repo** if you find it useful!

📝 **Questions?** Open an issue or email lior.dux@develeap.com
