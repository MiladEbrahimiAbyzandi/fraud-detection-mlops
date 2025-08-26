from fastapi import APIRouter

router = APIRouter()


@router.get("/load-data/health", tags=["Data Loader"])
async def health_check():
    return {"status": "ok"}
