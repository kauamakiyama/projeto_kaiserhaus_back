from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.database import conectar_db, fechar_db
from app.controllers import user_controller, produto_controller, categoria_controller, sacola_controller, pedido_controller, auth_controller, images_controller

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

# Middleware de compressão para melhorar performance
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configurar CORS para permitir comunicação com o frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Porta do seu frontend
    allow_credentials=True,  # Permitir cookies
    allow_methods=["*"],     # Permitir todos os métodos HTTP
    allow_headers=["*"],     # Permitir todos os headers
)

# Servir arquivos estáticos (imagens) - otimizado para performance
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth_controller.router, prefix="/auth", tags=["Autenticação"])
app.include_router(user_controller.router, prefix="/usuarios", tags=["Usuários"])
app.include_router(produto_controller.router, prefix="/produtos", tags=["Produtos"])
app.include_router(categoria_controller.router, prefix="/categorias", tags=["Categorias"])
app.include_router(sacola_controller.router, prefix="/sacola", tags=["Sacola"])
app.include_router(pedido_controller.router, prefix="/pedidos", tags=["Pedidos"])
app.include_router(images_controller.router, tags=["Imagens"])

@app.get("/")
def root():
    return {"message": "🚀 API rodando com MongoDB"}
