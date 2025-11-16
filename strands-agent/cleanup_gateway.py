from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
import json
import boto3

with open("gateway_config.json", "r") as f:
    config = json.load(f)

# Set up boto3 to use the zMynx profile
boto3.setup_default_session(profile_name="zMynx")

client = GatewayClient(region_name=config["region"])
client.cleanup_gateway(config["gateway_id"], config["client_info"])
print("✅ Cleanup complete!")
