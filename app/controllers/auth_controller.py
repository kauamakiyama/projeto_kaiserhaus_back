from fastapi import APIRouter, HTTPException, Response, status
from app.schemas import LoginIn, LoginOut, UsuarioIn
from app.services import auth_service
from app.services.user_service import create_user
from datetime import timedelta

router = APIRouter()

# Configurações
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/usuarios/login", response_model=LoginOut)
async def login_route(login_data: LoginIn, response: Response):
    """
    Endpoint de login que retorna token e define cookie
    """
    try:
        # Autenticar usuário
        user = await auth_service.authenticate_user(login_data.email, login_data.senha)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        # Criar token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={"sub": user["email"]}, 
            expires_delta=access_token_expires
        )
        
        # Definir cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # em segundos
            httponly=True,
            secure=False,  # True em produção com HTTPS
            samesite="lax"
        )
        
        return LoginOut(
            message="Login realizado com sucesso",
            usuario=auth_service.user_helper(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.post("/usuarios/register", response_model=dict)
async def register_route(user_data: UsuarioIn):
    """
    Endpoint de registro de usuário
    """
    try:
        # Verificar se email já existe
        existing_user = await auth_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso"
            )
        
        # Criar usuário
        new_user = await create_user(user_data)
        
        return {
            "message": "Usuário criado com sucesso",
            "usuario": new_user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.post("/logout")
async def logout_route(response: Response):
    """
    Endpoint de logout que remove o cookie
    """
    response.delete_cookie(key="access_token")
    return {"message": "Logout realizado com sucesso"}