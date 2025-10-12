from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt, ExpiredSignatureError
from app.services.auth_service import get_user_by_email
from app.schemas import UsuarioOut
import os
import logging
from typing import Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do JWT - DEVE SER IGUAL AO auth_service.py
SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta-super-segura-aqui")
ALGORITHM = "HS256"

# Esquema de autenticação Bearer
security = HTTPBearer()

async def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UsuarioOut:
    """
    Extrai e valida o token JWT do header Authorization Bearer
    """
    try:
        # Extrai o token do header Authorization: Bearer <token>
        token = credentials.credentials
        logger.info(f"Validando token JWT: {token[:50]}...")
        
        # Decodifica o token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            logger.error("Token JWT não contém campo 'sub' (email)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: campo 'sub' não encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        logger.info(f"Token JWT válido para usuário: {email}")
        
    except ExpiredSignatureError as e:
        logger.error(f"Token JWT expirado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        # Verifica o tipo específico do erro
        error_msg = str(e).lower()
        if "signature" in error_msg:
            logger.error(f"Assinatura JWT inválida: {str(e)}")
            detail = "Token com assinatura inválida"
        elif "audience" in error_msg:
            logger.error(f"Audience JWT inválido: {str(e)}")
            detail = "Token com audience inválido"
        elif "issuer" in error_msg:
            logger.error(f"Issuer JWT inválido: {str(e)}")
            detail = "Token com issuer inválido"
        else:
            logger.error(f"Erro JWT genérico: {str(e)}")
            detail = f"Token inválido: {str(e)}"
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Busca o usuário no banco de dados
    user = await get_user_by_email(email)
    if user is None:
        logger.error(f"Usuário não encontrado no banco: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    logger.info(f"Usuário autenticado com sucesso: {email}")
    return user

async def get_current_user_id_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extrai apenas o ID do usuário do token JWT
    """
    user = await get_current_user_from_token(credentials)
    return user.id  # Retorna como string (ObjectId do MongoDB)

async def get_current_user_optional_from_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[UsuarioOut]:
    """
    Versão opcional da autenticação - retorna None se não autenticado
    """
    if credentials is None:
        return None
        
    try:
        return await get_current_user_from_token(credentials)
    except HTTPException:
        return None

async def verify_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UsuarioOut:
    """
    Verifica se o usuário é admin
    """
    user = await get_current_user_from_token(credentials)
    
    if user.hierarquia != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem acessar este recurso."
        )
    
    return user

async def verify_funcionario_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UsuarioOut:
    user = await get_current_user_from_token(credentials)
    
    if user.hierarquia not in ["funcionario", "admin", "colaborador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas funcionários, administradores e colaboradores podem acessar este recurso."
        )
    
    return user

