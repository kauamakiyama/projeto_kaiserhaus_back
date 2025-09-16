from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import conectar_db, fechar_db
from app.controllers import user_controller, produto_controller, categoria_controller, sacola_controller, pedido_controller

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
app.include_router(categoria_controller.router, prefix="/categorias", tags=["Categorias"])
app.include_router(sacola_controller.router, prefix="/sacola", tags=["Sacola"])
app.include_router(pedido_controller.router, prefix="/pedidos", tags=["Pedidos"])

@app.get("/")
def root():
    return {"message": "🚀 API rodando com MongoDB"}
