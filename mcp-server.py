import os
from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.auth import OAuthProxy
from pydantic import AnyHttpUrl
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
KEYCLOAK_BASE_URL = os.getenv("KEYCLOAK_BASE_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "master")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")
MCP_SERVER_BASE_URL = os.getenv("MCP_SERVER_BASE_URL", "http://localhost:8000")

# Validate required environment variables
if not KEYCLOAK_CLIENT_ID:
    raise ValueError("KEYCLOAK_CLIENT_ID environment variable is required")
if not KEYCLOAK_CLIENT_SECRET:
    raise ValueError("KEYCLOAK_CLIENT_SECRET environment variable is required")

# Build Keycloak URLs
KEYCLOAK_JWKS_URI = f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
KEYCLOAK_ISSUER = f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}"
KEYCLOAK_AUTH_ENDPOINT = f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth"
KEYCLOAK_TOKEN_ENDPOINT = f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"

# Configure token validation for your identity provider
token_verifier = JWTVerifier(
    jwks_uri=KEYCLOAK_JWKS_URI,
    issuer=KEYCLOAK_ISSUER
)

# Create the OAuth Proxy
auth = OAuthProxy(
    upstream_authorization_endpoint=KEYCLOAK_AUTH_ENDPOINT,
    upstream_token_endpoint=KEYCLOAK_TOKEN_ENDPOINT,

    # Your registered app credentials (from environment variables)
    upstream_client_id=KEYCLOAK_CLIENT_ID,
    upstream_client_secret=KEYCLOAK_CLIENT_SECRET,

    # Token validation (see Token Verification guide)
    token_verifier=token_verifier,

    # Your FastMCP server's public URL
    base_url=MCP_SERVER_BASE_URL,

    # Optional: customize the callback path (default is "/auth/callback")
    # redirect_path="/custom/callback",
)

mcp = FastMCP(
        name="mcp_server",
        instructions="""This server greets and provides information about me""",
        auth=auth
    )

print(mcp.settings)

@mcp.tool()
def greet(name: str) -> str:
    """Returns the greeting message from me, to the name passed in greet"""
    return f"Hello! {name}"

@mcp.resource(uri="resource://profile", mime_type="application/json")
def get_my_profile() -> dict:
    """Provides information about Vikrant"""
    return dict(first_name="Vikrant", last_name="Jain", address="Rohini, Delhi, India")

@mcp.prompt(name="ask_about_topic", description="Creates a prompt for asking a question about a topic")
def ask_about_topic(topic: str) -> str:
    return f"Please provide detailed information on ```{topic}```"


if __name__ == "__main__":
    mcp.run()
