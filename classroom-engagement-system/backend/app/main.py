from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes.meetings import router as meetings_router

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Analyze classroom engagement through speaker diarization and participation metrics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(meetings_router, prefix="/api", tags=["meetings"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Classroom Engagement System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Classroom Engagement System"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
