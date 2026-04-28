from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from .scpEnumClass import SCPClassEnum

class ConteudoAdjacente(BaseModel):
    titulo: str
    conteudo: str

class Metadados(BaseModel):
    url_origem: str
    data_scraping: datetime = Field(default_factory=datetime.utcnow)

class SCP(BaseModel):
    itemNumber: str
    objectClass: SCPClassEnum
    containmentProcedures: str
    description: str
    conteudos_adjacentes: Optional[list[ConteudoAdjacente]] = []
    metadados: Optional[Metadados] = None