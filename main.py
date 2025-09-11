from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import conectar_db, fechar_db
from app.controllers import user_controller, produto_controller

@asynccontextmanager
async def lifespan(app: FastAPI):
    # antes de iniciar o servidor
    await conectar_db()
    yield
    # quando o servidor for encerrado
    await fechar_db()

app = FastAPI(
    title="Kaiserhaus API",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(user_controller.router, prefix="/usuarios", tags=["Usuários"])
app.include_router(produto_controller.router, prefix="/produtos", tags=["Produtos"])

@app.get("/")
def root():
    return {"message": "🚀 API rodando com MongoDB"}
