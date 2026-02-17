"""
Service Contract Management System - FastAPI Backend
Refactored modular architecture.
"""
from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app
app = FastAPI(title="Service Contract Management System", version="2.0.0")

# Create the main API router
api_router = APIRouter(prefix="/api")

# Import route modules
from routes.auth import router as auth_router
from routes.notifications import router as notifications_router
from routes.auditors import router as auditors_router
from routes.certificates import router as certificates_router
from routes.public_verify import router as public_verify_router
from routes.templates import router as templates_router, seed_default_templates
from routes.documents import router as documents_router
from routes.sites import router as sites_router
from routes.contacts import router as contacts_router

# Include all routers
api_router.include_router(auth_router)
api_router.include_router(notifications_router)
api_router.include_router(auditors_router)
api_router.include_router(certificates_router)
api_router.include_router(public_verify_router)
api_router.include_router(templates_router)
api_router.include_router(documents_router)
api_router.include_router(sites_router)
api_router.include_router(contacts_router)

# Root endpoint
@api_router.get("/")
async def root():
    return {"message": "Service Contract Management System API", "version": "2.0.0"}

# Include the main router
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run startup tasks"""
    await seed_default_templates()
    logger.info("Server started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    from database import client
    client.close()
    logger.info("Server shutdown complete")
