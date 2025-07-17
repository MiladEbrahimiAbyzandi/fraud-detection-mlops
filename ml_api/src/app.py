from fastapi import Body, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Fraud Detection ML API", description="Fraud Detection ML API", version="1.0.0")

# Include routers
# app.include_router(data_router)


# Add middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "running", "service": "Fraud Detection ML API", "version": "1.0.0"}


@app.get("/")
async def root():
    return {"message": "Fraud Detection ML API"}
