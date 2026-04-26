from fastapi import APIRouter
from models.scp import SCP

router = APIRouter(prefix="/scp", tags=["SCP"])

@router.post("/")
async def criar_scp(scp: SCP):
    return SCP # por enquanto vai devolver o que recebeu

