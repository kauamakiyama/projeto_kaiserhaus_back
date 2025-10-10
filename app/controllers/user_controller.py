from fastapi import APIRouter, HTTPException, Depends, Query
from app.schemas import UsuarioIn, UsuarioOut, UsuarioUpdate, PaginacaoPedidosOut
from app.services.user_service import (
    create_user, get_users, get_user_by_id,
    update_user, delete_user
)
from app.services import pedido_service
from app.dependencies_jwt import get_current_user_id_from_token
# from app.dependencies import get_current_user_from_cookie

router = APIRouter()

@router.post("/", response_model=UsuarioOut)
async def create_user_route(user: UsuarioIn):
    return await create_user(user)


@router.get("/", response_model=list[UsuarioOut])
async def list_users_route():
    return await get_users()

@router.get("/{user_id}", response_model=UsuarioOut)
async def get_user_route(user_id: str):
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.put("/{user_id}", response_model=UsuarioOut)
async def update_user_route(user_id: str, user: UsuarioUpdate):
    updated = await update_user(user_id, user)
    if not updated:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return updated

@router.delete("/{user_id}")
async def delete_user_route(user_id: str):
    deleted = await delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"message": "Usuário deletado com sucesso"}

@router.get("/me/pedidos", response_model=PaginacaoPedidosOut)
async def listar_meus_pedidos(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=50, description="Itens por página"),
    usuario_id: str = Depends(get_current_user_id_from_token)
):
    """
    Lista pedidos do usuário autenticado
    
    - Endpoint específico para /usuarios/me/pedidos
    - Retorna pedidos ordenados por data de criação (mais recentes primeiro)
    - Suporte a paginação
    """
    try:
        resultado = await pedido_service.listar_pedidos_usuario(usuario_id, page, page_size)
        return PaginacaoPedidosOut(**resultado)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno do servidor: {str(e)}"
        )
