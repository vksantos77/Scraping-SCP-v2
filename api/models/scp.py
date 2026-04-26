from .scpEnumClass import SCPClassEnum
from pydantic import BaseModel
class SCP(BaseModel):
    itemNumber: str
    objectClass: SCPClassEnum
    containmentProcedures: str
    description: str

