from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify if the API is running.
    Returns a simple message indicating the API is healthy.
    """
    return {"status": "healthy"}