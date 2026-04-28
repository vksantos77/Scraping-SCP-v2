from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "scp_db"

client = AsyncIOMotorClient(MONGO_URL)
database = client[DB_NAME]

def get_collection(name: str):
    return database[name]
