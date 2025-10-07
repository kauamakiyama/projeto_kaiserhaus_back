from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# Carrega variáveis do arquivo .env
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "back-jr")

client: AsyncIOMotorClient = None
db = None

async def conectar_db():
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[MONGO_DB]
    print(f"Conectado ao MongoDB: {MONGO_DB}")

async def fechar_db():
    global client
    if client:
        client.close()
        print("Conexao com MongoDB encerrada")
