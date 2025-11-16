"""
FastMCP Server for AWS Lambda Calculator API
Integrates with AWS Bedrock AgentCore to expose Lambda cost calculation tools via MCP protocol.
"""

import os
from fastmcp import FastMCP
import httpx
from typing import Literal
from models import CalculationRequest, CalculationResult
from starlette.responses import JSONResponse

# Initialize FastMCP server configured for AWS Bedrock AgentCore Runtime
# Must use host="0.0.0.0" and stateless_http=True for AgentCore compatibility
mcp = FastMCP("AWS Lambda Calculator")

# API Configuration
API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://kdhtgb2u9d.execute-api.us-east-1.amazonaws.com/prod"
)


@mcp.tool()
async def calculate_lambda_cost(
    region: str = "us-east-1",
    architecture: Literal["x86", "arm64"] = "x86",
    number_of_requests: int = 1000000,
    request_unit: Literal["per second", "per minute", "per hour", "per day", "per month"] = "per month",
    duration_of_each_request_in_ms: int = 200,
    memory: int = 128,
    memory_unit: Literal["MB"] = "MB",
    ephemeral_storage: int = 512,
    storage_unit: Literal["MB", "GB"] = "MB",
    include_free_tier: bool = True,
    verbose: bool = True
) -> dict:
    """
    Calculate AWS Lambda costs based on the provided parameters.

    This tool calculates the estimated cost of running AWS Lambda functions
    based on region, architecture, request volume, duration, memory, and storage.

    Args:
        region: AWS region (e.g., us-east-1, eu-west-1)
        architecture: Lambda architecture (x86 or arm64)
        number_of_requests: Total number of requests
        request_unit: Unit for request count (per second/minute/hour/day/month)
        duration_of_each_request_in_ms: Duration of each request in milliseconds (1-900000)
        memory: Memory allocated in MB (128-10240)
        memory_unit: Memory unit (MB)
        ephemeral_storage: Ephemeral storage in MB (512-10240)
        storage_unit: Storage unit (MB or GB)
        include_free_tier: Include AWS Free Tier benefits
        verbose: Include detailed calculation steps

    Returns:
        Dictionary containing status, cost, and optional calculation steps

    Examples:
        - Basic calculation: calculate_lambda_cost(region="us-east-1", memory=256, duration_of_each_request_in_ms=500)
        - ARM64 calculation: calculate_lambda_cost(architecture="arm64", memory=512)
        - High memory: calculate_lambda_cost(memory=3008, duration_of_each_request_in_ms=5000)
    """
    # Build request payload
    payload = CalculationRequest(
        region=region,
        architecture=architecture,
        number_of_requests=number_of_requests,
        request_unit=request_unit,
        duration_of_each_request_in_ms=duration_of_each_request_in_ms,
        memory=memory,
        memory_unit=memory_unit,
        ephemeral_storage=ephemeral_storage,
        storage_unit=storage_unit,
        include_free_tier=include_free_tier,
        verbose=verbose
    )

    # Make API request
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                API_BASE_URL,
                json=payload.model_dump(),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "status": "error",
                "message": f"API request failed with status {e.response.status_code}: {e.response.text}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to calculate Lambda cost: {str(e)}"
            }


@mcp.tool()
async def get_lambda_pricing_info() -> dict:
    """
    Get general information about AWS Lambda pricing structure.

    Returns:
        Dictionary containing AWS Lambda pricing information and guidelines
    """
    return {
        "status": "success",
        "pricing_info": {
            "free_tier": {
                "requests": "1 million requests per month",
                "compute_time": "400,000 GB-seconds per month"
            },
            "architecture_options": {
                "x86": "Traditional x86_64 architecture",
                "arm64": "ARM-based Graviton2 processors (typically 20% cheaper)"
            },
            "memory_range": {
                "minimum": "128 MB",
                "maximum": "10,240 MB (10 GB)",
                "increment": "1 MB"
            },
            "ephemeral_storage_range": {
                "minimum": "512 MB",
                "maximum": "10,240 MB (10 GB)",
                "note": "Additional storage above 512 MB is charged separately"
            },
            "duration_limits": {
                "minimum": "1 ms",
                "maximum": "900,000 ms (15 minutes)"
            },
            "request_units": [
                "per second",
                "per minute",
                "per hour",
                "per day",
                "per month"
            ],
            "supported_regions": [
                "us-east-1", "us-east-2", "us-west-1", "us-west-2",
                "eu-west-1", "eu-west-2", "eu-west-3", "eu-central-1",
                "ap-southeast-1", "ap-southeast-2", "ap-northeast-1",
                "and many more..."
            ]
        }
    }


@mcp.tool()
async def compare_lambda_architectures(
    region: str = "us-east-1",
    number_of_requests: int = 1000000,
    request_unit: Literal["per second", "per minute", "per hour", "per day", "per month"] = "per month",
    duration_of_each_request_in_ms: int = 200,
    memory: int = 128,
    ephemeral_storage: int = 512,
    include_free_tier: bool = True
) -> dict:
    """
    Compare costs between x86 and arm64 Lambda architectures.

    This tool calculates Lambda costs for both x86 and arm64 architectures
    with identical parameters to help you make informed architecture decisions.

    Args:
        region: AWS region
        number_of_requests: Total number of requests
        request_unit: Unit for request count
        duration_of_each_request_in_ms: Duration per request in ms
        memory: Memory allocated in MB
        ephemeral_storage: Ephemeral storage in MB
        include_free_tier: Include AWS Free Tier benefits

    Returns:
        Dictionary containing cost comparison between x86 and arm64
    """
    # Calculate for x86
    x86_result = await calculate_lambda_cost(
        region=region,
        architecture="x86",
        number_of_requests=number_of_requests,
        request_unit=request_unit,
        duration_of_each_request_in_ms=duration_of_each_request_in_ms,
        memory=memory,
        ephemeral_storage=ephemeral_storage,
        include_free_tier=include_free_tier,
        verbose=False
    )

    # Calculate for arm64
    arm64_result = await calculate_lambda_cost(
        region=region,
        architecture="arm64",
        number_of_requests=number_of_requests,
        request_unit=request_unit,
        duration_of_each_request_in_ms=duration_of_each_request_in_ms,
        memory=memory,
        ephemeral_storage=ephemeral_storage,
        include_free_tier=include_free_tier,
        verbose=False
    )

    # Calculate savings
    if x86_result.get("status") == "success" and arm64_result.get("status") == "success":
        x86_cost = x86_result.get("cost", 0)
        arm64_cost = arm64_result.get("cost", 0)
        savings = x86_cost - arm64_cost
        savings_percentage = (savings / x86_cost * 100) if x86_cost > 0 else 0

        return {
            "status": "success",
            "comparison": {
                "x86": {
                    "cost": x86_cost,
                    "architecture": "x86"
                },
                "arm64": {
                    "cost": arm64_cost,
                    "architecture": "arm64"
                },
                "savings": {
                    "amount": round(savings, 6),
                    "percentage": round(savings_percentage, 2),
                    "recommendation": "arm64" if savings > 0 else "x86"
                }
            },
            "parameters": {
                "region": region,
                "memory": f"{memory} MB",
                "requests": f"{number_of_requests} {request_unit}",
                "duration": f"{duration_of_each_request_in_ms} ms",
                "free_tier": include_free_tier
            }
        }
    else:
        return {
            "status": "error",
            "message": "Failed to compare architectures",
            "x86_result": x86_result,
            "arm64_result": arm64_result
        }


# Health check endpoint
@mcp.tool()
async def health_check() -> dict:
    """
    Check the health status of the AWS Lambda Calculator API.

    Returns:
        Dictionary containing health status information
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Try OPTIONS request for CORS preflight
            response = await client.options(API_BASE_URL)
            return {
                "status": "healthy",
                "api_url": API_BASE_URL,
                "response_code": response.status_code
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "api_url": API_BASE_URL,
                "error": str(e)
            }


if __name__ == "__main__":
    # Run the MCP server for AWS Bedrock AgentCore Runtime
    mcp.run(host="0.0.0.0", stateless_http=True, path="/mcp", transport="streamable-http")
