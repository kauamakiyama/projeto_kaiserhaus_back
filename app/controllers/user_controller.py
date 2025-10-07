from fastapi import APIRouter, HTTPException, Depends
from app.schemas import UsuarioIn, UsuarioOut, UsuarioUpdate
from app.services.user_service import (
    create_user, get_users, get_user_by_id,
    update_user, delete_user
)
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

# @router.get("/perfil", response_model=UsuarioOut)
# async def get_perfil_route(current_user: UsuarioOut = Depends(get_current_user_from_cookie)):
#     """
#     Rota protegida - retorna dados do usuário logado
#     """
#     return current_user
