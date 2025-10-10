from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.database import conectar_db, fechar_db

from app.controllers import user_controller, produto_controller, categoria_controller, sacola_controller, pedido_controller, image_controller, auth_controller, profile_controller, pagamento_controller, cartao_controller


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

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_controller.router, tags=["Autenticação"])
app.include_router(profile_controller.router, prefix="/usuarios", tags=["Perfil"])
app.include_router(user_controller.router, prefix="/usuarios", tags=["Usuários"])
app.include_router(produto_controller.router, prefix="/produtos", tags=["Produtos"])
app.include_router(categoria_controller.router, prefix="/categorias", tags=["Categorias"])
app.include_router(sacola_controller.router, prefix="/sacola", tags=["Sacola"])
app.include_router(pedido_controller.router, prefix="/pedidos", tags=["Pedidos"])
app.include_router(pagamento_controller.router, prefix="/pagamentos", tags=["Pagamentos"])
app.include_router(cartao_controller.router, prefix="/cartoes", tags=["Cartões"])
app.include_router(image_controller.router, prefix="/images", tags=["Imagens"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/usuarios", tags=["users"])

@app.get("/")
def root():
    return {"message": "🚀 API rodando com MongoDB"}