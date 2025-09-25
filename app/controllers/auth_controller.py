from fastapi import APIRouter, HTTPException, Depends, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas import LoginIn, LoginOut, LogoutOut, UsuarioOut
from app.services import auth_service
from app.dependencies import get_current_user_from_cookie

router = APIRouter()
security = HTTPBearer()

@router.post("/login", response_model=LoginOut)
async def login_route(login_data: LoginIn, response: Response):
    """
    Realiza login do usuário e define cookie de autenticação
    """
    login_result, access_token = await auth_service.login_user(login_data)
    
    # Definir cookie com o token
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=1800,  # 30 minutos
        httponly=True,  # Não acessível via JavaScript
        secure=False,   # Para desenvolvimento (use True em produção com HTTPS)
        samesite="lax"
    )
    
    return login_result

@router.post("/logout", response_model=LogoutOut)
async def logout_route(response: Response):
    """
    Realiza logout do usuário removendo o cookie
    """
    response.delete_cookie(key="access_token")
    return LogoutOut(message="Logout realizado com sucesso")

@router.get("/me", response_model=UsuarioOut)
async def get_current_user_route(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Retorna informações do usuário logado via Authorization header
    """
    user = await auth_service.get_current_user(credentials.credentials)
    return auth_service.user_helper(user)

@router.get("/me-cookie", response_model=UsuarioOut)
async def get_current_user_cookie_route(current_user: UsuarioOut = Depends(get_current_user_from_cookie)):
    """
    Retorna informações do usuário logado via cookie
    """
    return current_user
