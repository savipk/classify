import uvicorn
from mapper_api.config.settings import Settings

if __name__ == "__main__":
    settings = Settings()
    uvicorn.run(
        "mapper_api.interface.http.api:app", 
        host="0.0.0.0", 
        port=settings.PORT
    )