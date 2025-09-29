#!/usr/bin/env python3
"""Debug script to test Azure service connections separately."""

import asyncio
from mapper_api.config.settings import Settings
from mapper_api.infrastructure.azure.blob_definitions_repo import BlobDefinitionsRepository
from mapper_api.infrastructure.azure.openai_client import AzureOpenAILLMClient

async def test_blob_storage():
    """Test Azure Blob Storage connection."""
    print("🧪 Testing Azure Blob Storage connection...")
    try:
        settings = Settings()
        repo = BlobDefinitionsRepository(
            account_name=settings.STORAGE_ACCOUNT_NAME,
            container_name=settings.STORAGE_CONTAINER_NAME,
            tenant_id=settings.AZURE_TENANT_ID,
            client_id=settings.AZURE_CLIENT_ID,
            client_secret=settings.AZURE_CLIENT_SECRET,
        )
        
        # Try to load definitions
        risk_themes = repo.get_risk_themes()
        fivews = repo.get_fivews_rows()
        
        print(f"✅ Blob Storage connected successfully!")
        print(f"   - Loaded {len(themes)} theme rows")
        print(f"   - Loaded {len(fivews)} 5Ws definitions")
        return True
        
    except Exception as e:
        print(f"❌ Blob Storage connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def test_openai():
    """Test Azure OpenAI connection."""
    print("🧪 Testing Azure OpenAI connection...")
    try:
        settings = Settings()
        client = AzureOpenAILLMClient(
            endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
        )
        
        # Simple test call
        response = client.json_schema_chat(
            system="You are a helpful assistant.",
            user="Say 'connection test successful'",
            schema_name="TestResponse",
            schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                },
                "required": ["message"],
                "additionalProperties": False
            },
            max_tokens=50,
            deployment=settings.AZURE_OPENAI_DEPLOYMENT
        )
        
        print(f"✅ Azure OpenAI connected successfully!")
        print(f"   Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Azure OpenAI connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

async def main():
    """Test all Azure connections."""
    print("🔍 Azure Connection Diagnostic")
    print("=" * 50)
    
    # Test environment first
    try:
        settings = Settings()
        print("✅ Environment variables loaded")
    except Exception as e:
        print(f"❌ Environment error: {e}")
        return
    
    # Test connections
    blob_ok = await test_blob_storage()
    openai_ok = test_openai()
    
    print("\n📊 Connection Summary:")
    print(f"   Blob Storage: {'✅ OK' if blob_ok else '❌ FAILED'}")
    print(f"   Azure OpenAI: {'✅ OK' if openai_ok else '❌ FAILED'}")
    
    if not (blob_ok and openai_ok):
        print("\n💡 Next Steps:")
        if not blob_ok:
            print("   - Check Azure Storage credentials and network access")
            print("   - Verify storage account name and container exist")
        if not openai_ok:
            print("   - Check Azure OpenAI credentials and deployment name")
            print("   - Verify network access to Azure OpenAI endpoint")

if __name__ == "__main__":
    asyncio.run(main())
