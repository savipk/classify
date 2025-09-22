#!/usr/bin/env python3
"""Debug script to check environment configuration on the server."""

from mapper_api.config.settings import Settings
from pydantic import ValidationError

def check_environment():
    """Check if all required environment variables are properly set."""
    try:
        settings = Settings()
        print("✅ Environment variables loaded successfully!")
        
        # Check Azure OpenAI settings
        print(f"🤖 Azure OpenAI Endpoint: {settings.AZURE_OPENAI_ENDPOINT}")
        print(f"🤖 Azure OpenAI API Version: {settings.AZURE_OPENAI_API_VERSION}")
        print(f"🤖 Azure OpenAI Deployment: {settings.AZURE_OPENAI_DEPLOYMENT}")
        print(f"🤖 Azure OpenAI API Key: {'***' + settings.AZURE_OPENAI_API_KEY[-4:] if len(settings.AZURE_OPENAI_API_KEY) > 4 else 'NOT SET'}")
        
        # Check Azure Storage settings
        print(f"💾 Storage Account: {settings.STORAGE_ACCOUNT_NAME}")
        print(f"💾 Storage Container: {settings.STORAGE_CONTAINER_NAME}")
        print(f"💾 Azure Tenant ID: {settings.AZURE_TENANT_ID}")
        print(f"💾 Azure Client ID: {settings.AZURE_CLIENT_ID}")
        print(f"💾 Azure Client Secret: {'***' + settings.AZURE_CLIENT_SECRET[-4:] if len(settings.AZURE_CLIENT_SECRET) > 4 else 'NOT SET'}")
        
        return settings
        
    except ValidationError as e:
        print("❌ Environment configuration error:")
        for error in e.errors():
            field_name = error['loc'][0] if error['loc'] else 'unknown'
            print(f"   - {field_name}: {error['msg']}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

if __name__ == "__main__":
    check_environment()
