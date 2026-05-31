from fastapi import FastAPI
from routes.scp import router as scp_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SCP API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scp_router)

@app.get("/")
async def root():
    return {"status": "online"}