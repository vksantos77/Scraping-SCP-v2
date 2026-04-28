from fastapi import FastAPI
from routes.scp import router as scp_router

app = FastAPI(title="SCP API", version="1.0.0")

app.include_router(scp_router)

@app.get("/")
async def root():
    return {"status": "online"}