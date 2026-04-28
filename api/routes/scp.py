from fastapi import APIRouter, HTTPException
from models.scp import SCP
from database.connection import get_collection

router = APIRouter(prefix="/scp", tags=["SCP"])

@router.post("/")
async def criar_scp(scp: SCP):
    try:
        collection = get_collection("scps")
        resultado = await collection.insert_one(scp.model_dump())
        return {"mensagem": "SCP inserido com sucesso", "id": str(resultado.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{numberSCP}")
async def pegar_scp(numberSCP: str):
    try:
        collection = get_collection("scps")
        scp = await collection.find_one({"itemNumber": numberSCP})
        if scp is None:
            raise HTTPException(status_code=404, detail="SCP não encontrado")
        scp["_id"] = str(scp["_id"])
        return {"SCP": scp}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))