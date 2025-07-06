from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from mangum import Mangum
from starlette.middleware.authentication import AuthenticationMiddleware
from pyngrok import ngrok

from app.api.api import api_router
from app.core.models.models import __all__
from app.utils.authentication import ApiAuthBackend
from app.config import settings

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.VERSION}/{settings.OPEN_API_JSON_FILENAME}",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Authentication middleware
app.add_middleware(AuthenticationMiddleware, backend=ApiAuthBackend())

@app.on_event("startup")
async def startup_event():
    # Initialize MongoDB connection
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    # Initialize Beanie with the MongoDB client
    await init_beanie(
        database=client[settings.DB_NAME],
        document_models=__all__
    )

# Include API router
app.include_router(api_router, prefix="/v1")
public_url = ngrok.connect(8000).public_url
print("your public endpoint :", public_url)
# handler = Mangum(app)