from fastapi import HTTPException, Depends, Request, status
from app.services import auth_service

async def get_current_user_from_cookie(request: Request):
    """
    Dependência para obter usuário atual via cookie
    """
    access_token = request.cookies.get("access_token")
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso não encontrado",
        )
    
    try:
        user = await auth_service.get_current_user(access_token)
        return auth_service.user_helper(user)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

# Dependência opcional (não obriga login)
async def get_current_user_optional(request: Request):
    """
    Dependência opcional para obter usuário atual via cookie
    Retorna None se não estiver logado
    """
    access_token = request.cookies.get("access_token")
    
    if not access_token:
        return None
    
    try:
        user = await auth_service.get_current_user(access_token)
        return auth_service.user_helper(user)
    except:
        return None

