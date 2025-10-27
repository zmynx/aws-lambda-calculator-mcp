from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
import yaml
import json
import boto3

## Convert YAML OpenAPI spec to JSON format ##
# Define the file paths
yaml_file_path = 'openapi.yaml'
json_file_path = 'openapi.json'

# Step 1: Load the YAML file into a Python object
with open(yaml_file_path, 'r') as yaml_in:
    # Use yaml.safe_load() for untrusted sources to prevent security risks
    python_object = yaml.safe_load(yaml_in)

# Step 2: Dump the Python object to a JSON file
with open(json_file_path, 'w') as json_out:
    # `indent=4` makes the JSON output human-readable
    json.dump(python_object, json_out, indent=4)

print(f"Successfully converted '{yaml_file_path}' to '{json_file_path}'")

with open(json_file_path, "r") as f:
    spec = json.load(f)

### Gateway Client Setup ###
with open("gateway_config.json", "r") as f:
    config = json.load(f)

# Create a session with the zMynx profile
session = boto3.Session(profile_name="zMynx")

# Create GatewayClient with the session (note: GatewayClient needs modification to accept session)
# Since GatewayClient doesn't accept session directly, we need to set the default session
boto3.setup_default_session(profile_name="zMynx")

client = GatewayClient(region_name=config["region"])
gateway = client.client.get_gateway(gatewayIdentifier=config["gateway_id"])

### Create the openApi Target ###
open_api_target = client.create_mcp_gateway_target(
    gateway=gateway,
    name=None,
    target_type="openApiSchema",
    # the API spec to use (note don't forget to )
    target_payload={
        "inlinePayload": json.dumps(spec)
    },
    # the credentials to use when interacting with this API
    credentials={
        "api_key": "<INSERT KEY>",
        "credential_location": "QUERY_PARAMETER",
        "credential_parameter_name": "api_key"
    }
)

print(f"✓ Custom openApi API added! Try: ")
print("Run 'python run_agent.py' and try: ")
