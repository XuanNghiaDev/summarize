from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import init_db, Base, engine
from routes import auth, users, quiz, summary, analytics, leaderboard, bookmarks

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Quiz and Article Summarization System with Advanced Analytics",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# API routes
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(quiz.router)
app.include_router(summary.router)
app.include_router(analytics.router)
app.include_router(leaderboard.router)
app.include_router(bookmarks.router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "endpoints": {
            "auth": "/auth",
            "user": "/user",
            "quiz": "/quiz",
            "summary": "/summary",
            "analytics": "/analytics",
            "leaderboard": "/leaderboard",
            "bookmarks": "/bookmarks"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
