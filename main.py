from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.database import conectar_db, fechar_db

from app.controllers import user_controller, produto_controller, categoria_controller, sacola_controller, pedido_controller, image_controller

@asynccontextmanager
async def lifespan(app: FastAPI):
    await conectar_db()
    yield
    await fechar_db()

app = FastAPI(
    title="Kaiserhaus API",
    version="1.0.0",
    lifespan=lifespan
)


# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth_controller.router, prefix="/auth", tags=["Autenticação"])

app.include_router(user_controller.router, prefix="/usuarios", tags=["Usuários"])
app.include_router(produto_controller.router, prefix="/produtos", tags=["Produtos"])
app.include_router(categoria_controller.router, prefix="/categorias", tags=["Categorias"])
app.include_router(sacola_controller.router, prefix="/sacola", tags=["Sacola"])
app.include_router(pedido_controller.router, prefix="/pedidos", tags=["Pedidos"])

app.include_router(image_controller.router, prefix="/images", tags=["Imagens"])



@app.get("/")
def root():
    return {"message": "🚀 API rodando com MongoDB"}
