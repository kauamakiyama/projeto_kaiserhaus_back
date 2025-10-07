import app.database as database
from app.schemas import LoginIn, LoginOut, UsuarioOut, TokenData
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import HTTPException, status
import os

# Configurações
SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta-super-segura-aqui")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuração para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def user_helper(user) -> UsuarioOut:
    # Converter string de data_nascimento de volta para date se necessário
    data_nascimento = user["data_nascimento"]
    if isinstance(data_nascimento, str):
        from datetime import datetime
        data_nascimento = datetime.strptime(data_nascimento, "%Y-%m-%d").date()
    
    return UsuarioOut(
        id=str(user["_id"]),
        nome=user["nome"],
        email=user["email"],
        cpf=user.get("cpf", ""),  # Campo opcional para compatibilidade
        data_nascimento=data_nascimento,
        telefone=user["telefone"],
        endereco=user["endereco"],
        complemento=user["complemento"],
        hierarquia=user.get("hierarquia", "usuario")
    )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Cria hash da senha"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Cria token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def authenticate_user(email: str, password: str):
    """Autentica o usuário"""
    user = await database.db["usuarios"].find_one({"email": email})
    if not user:
        return False
    
    # O campo no banco é 'senha_hash', não 'senha'
    senha_hash = user.get("senha_hash") or user.get("senha")
    if not senha_hash:
        return False
        
    if not verify_password(password, senha_hash):
        return False
    return user

async def get_current_user(token: str):
    """Busca usuário atual pelo token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = await database.db["usuarios"].find_one({"email": token_data.email})
    if user is None:
        raise credentials_exception
    return user

async def login_user(login_data: LoginIn) -> LoginOut:
    """Realiza login do usuário"""
    user = await authenticate_user(login_data.email, login_data.senha)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return LoginOut(
        message="Login realizado com sucesso",
        usuario=user_helper(user)
    ), access_token

async def get_user_by_email(email: str):
    """Busca usuário por email"""
    user = await database.db["usuarios"].find_one({"email": email})
    if user:
        return user_helper(user)
    return None

