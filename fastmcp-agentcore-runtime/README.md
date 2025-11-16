# AWS Lambda Calculator MCP Server

FastMCP server for AWS Lambda cost calculation, configured for AWS Bedrock AgentCore runtime deployment.

## Overview

This MCP (Model Context Protocol) server exposes AWS Lambda cost calculation tools via the MCP protocol, integrating with AWS Bedrock AgentCore. It provides intelligent cost estimation and comparison capabilities for AWS Lambda functions.

## Features

### Available Tools

1. **calculate_lambda_cost** - Calculate AWS Lambda costs based on detailed parameters
   - Supports all AWS regions
   - Both x86 and ARM64 architectures
   - Configurable memory, storage, and request patterns
   - Optional AWS Free Tier calculations
   - Verbose output with calculation steps

2. **get_lambda_pricing_info** - Get general AWS Lambda pricing information
   - Free tier details
   - Architecture options and pricing differences
   - Memory and storage ranges
   - Supported regions

3. **compare_lambda_architectures** - Compare costs between x86 and ARM64
   - Side-by-side cost comparison
   - Savings calculation and percentage
   - Architecture recommendations

4. **health_check** - Check API health status

## Prerequisites

- Python 3.11+
- Docker or Podman (for containerized deployment)
- AWS Account (for AgentCore deployment)
- AWS CLI configured (for deployment)
- uv (Python package manager) - `pip install uv`

## Local Development

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server locally
python main.py
```

The server will start on `http://0.0.0.0:8000/mcp` (required for AgentCore compatibility).

### Configuration

Copy `.env.example` to `.env` and customize if needed:

```bash
cp .env.example .env
```

The default API endpoint is already configured. Only modify if using a different backend.

## Docker Deployment

### Build for ARM64 (AWS Graviton)

```bash
# Build the Docker image for ARM64
docker build --platform linux/arm64 -t lambda-calculator-mcp:latest .

# Run locally for testing
docker run -p 8000:8000 lambda-calculator-mcp:latest
```

### Build for x86_64

```bash
# Build for x86_64 if needed
docker build --platform linux/amd64 -t lambda-calculator-mcp:latest .
```

## AWS Bedrock AgentCore Deployment

### Step 1: Install AgentCore Toolkit

```bash
uv pip install bedrock-agentcore-starter-toolkit
```

### Step 2: Create AWS Resources

Before configuring AgentCore, you need to create the required AWS resources.

#### Create ECR Repository

```bash
aws ecr create-repository \
  --repository-name aws-lambda-calculator-fastmcp-ecr \
  --region us-east-1 \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=AES256
```

#### Create IAM Role

First, create the trust policy:

```bash
cat > trust-policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock-agentcore.amazonaws.com"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "<YOUR_ACCOUNT_ID>"
        }
      }
    }
  ]
}
EOF
```

**Note**: Replace `<YOUR_ACCOUNT_ID>` with your AWS account ID (e.g., `006262944085`).

Create the IAM role:

```bash
aws iam create-role \
  --role-name aws-lambda-calculator-fastmcp-role \
  --assume-role-policy-document file://trust-policy.json \
  --description "Execution role for AWS Lambda Calculator FastMCP AgentCore runtime"
```

#### Attach Required Policies

```bash
# ECR access
aws iam attach-role-policy \
  --role-name aws-lambda-calculator-fastmcp-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly

# CloudWatch Logs (for observability)
aws iam attach-role-policy \
  --role-name aws-lambda-calculator-fastmcp-role \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess

# Bedrock Agent access
aws iam attach-role-policy \
  --role-name aws-lambda-calculator-fastmcp-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

#### Verify Resource Creation

```bash
# Verify ECR repository
aws ecr describe-repositories \
  --repository-names aws-lambda-calculator-fastmcp-ecr \
  --region us-east-1

# Verify IAM role
aws iam get-role \
  --role-name aws-lambda-calculator-fastmcp-role
```

### Step 3: Configure AgentCore

```bash
uv run agentcore configure --entrypoint main.py --protocol MCP
```

This will prompt you for:
- **IAM execution role ARN**: `arn:aws:iam::006262944085:role/aws-lambda-calculator-fastmcp-role`
- **ECR registry URL**: `006262944085.dkr.ecr.us-east-1.amazonaws.com/aws-lambda-calculator-fastmcp-ecr`
- **Region**: `us-east-1` (optional)
- **Container runtime**: `podman` (or `docker`)
- **Platform**: `linux/arm64`

### Step 4: Deploy to AWS

```bash
uv run agentcore launch
```

This will:
1. Build the Docker container
2. Push to Amazon ECR
3. Deploy to AWS Bedrock AgentCore
4. Return an agent runtime ARN

### Step 5: Invoke the Agent

```python
import boto3
import json

# Initialize Bedrock AgentCore client
client = boto3.client('bedrock-agentcore-runtime', region_name='us-east-1')

# Invoke the agent
response = client.invoke_agent(
    agentId='your-agent-arn',
    inputText='Calculate Lambda costs for 1M requests in us-east-1 with 256MB memory'
)

print(response)
```

## Usage Examples

### Calculate Lambda Cost

```python
# Example request to the MCP server
{
  "tool": "calculate_lambda_cost",
  "arguments": {
    "region": "us-east-1",
    "architecture": "arm64",
    "number_of_requests": 1000000,
    "request_unit": "per month",
    "duration_of_each_request_in_ms": 200,
    "memory": 256,
    "memory_unit": "MB",
    "ephemeral_storage": 512,
    "storage_unit": "MB",
    "include_free_tier": true,
    "verbose": true
  }
}
```

### Compare Architectures

```python
{
  "tool": "compare_lambda_architectures",
  "arguments": {
    "region": "us-east-1",
    "number_of_requests": 5000000,
    "memory": 1024,
    "duration_of_each_request_in_ms": 500
  }
}
```

## Architecture

- **main.py** - FastMCP server implementation with tool definitions
- **models.py** - Pydantic models for request/response validation
- **Dockerfile** - Multi-stage Docker build optimized for ARM64
- **requirements.txt** - Python dependencies

## Technical Details

### AgentCore Requirements

This server is configured specifically for AWS Bedrock AgentCore:

- **Host**: `0.0.0.0` (required)
- **Port**: `8000` (required)
- **Path**: `/mcp` (required)
- **Stateless HTTP**: `True` (required)

AgentCore automatically injects `Mcp-Session-Id` headers for session management.

### Supported Parameters

- **Regions**: All AWS regions (35+ regions)
- **Architectures**: x86, arm64
- **Memory Range**: 128 MB - 10,240 MB
- **Storage Range**: 512 MB - 10,240 MB
- **Duration**: 1 ms - 900,000 ms (15 minutes)
- **Request Units**: per second/minute/hour/day/month

## API Backend

This MCP server connects to the AWS Lambda Calculator API:
- **Endpoint**: https://kdhtgb2u9d.execute-api.us-east-1.amazonaws.com/prod
- **OpenAPI Spec**: Available at `../openapi.json`
- **No Authentication Required**

## Troubleshooting

### Health Check Failing

```bash
# Test the health endpoint
curl http://localhost:8000/health
```

### Docker Build Issues

```bash
# Ensure Docker supports ARM64
docker buildx ls

# Create a new builder if needed
docker buildx create --use
```

### Import Errors

Ensure `models.py` is in the same directory as `main.py`.

## Contributing

This project is part of the AWS Lambda Calculator MCP integration. For issues or enhancements, please refer to the main project repository.

## License

Apache 2.0 - See LICENSE file for details.

## Contact

- **Author**: Lior Dux
- **Email**: lior.dux@develeap.com
