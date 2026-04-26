from fastapi import FastAPI
from routes.scp import router as scp_router

app = FastAPI()
app.include_router(scp_router)
