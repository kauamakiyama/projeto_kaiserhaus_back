from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.schemas import UsuarioOut
from app.dependencies_jwt import get_current_user_from_token

router = APIRouter()

@router.get("/perfil", response_model=UsuarioOut)
async def get_user_profile(current_user: UsuarioOut = Depends(get_current_user_from_token)):
    """
    Retorna os dados do usuário logado
    """
    return current_user

@router.get("/me", response_model=UsuarioOut)
async def get_current_user_info(current_user: UsuarioOut = Depends(get_current_user_from_token)):
    """
    Endpoint alternativo para pegar dados do usuário atual
    """
    return current_user
