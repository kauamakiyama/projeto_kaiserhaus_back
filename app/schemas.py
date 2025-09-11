from pydantic import BaseModel, EmailStr
from datetime import date


class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    data_nascimento: date
    telefone: str
    endereco: str
    complemento: str

class UsuarioIn(UsuarioBase):  
    senha: str

class UsuarioUpdate(BaseModel): 
    nome: str | None = None
    email: EmailStr | None = None
    data_nascimento: date | None = None
    telefone: str | None = None
    endereco: str | None = None
    complemento: str | None = None
    senha: str | None = None

class UsuarioOut(UsuarioBase):  
    id: str



class ProdutoBase(BaseModel):
    imagem: str
    titulo: str
    descricao: str
    preco: float

class ProdutoIn(ProdutoBase):  
    pass

class ProdutoUpdate(BaseModel): 
    imagem: str | None = None
    titulo: str | None = None
    descricao: str | None = None
    preco: float | None = None

class ProdutoOut(ProdutoBase):  
    id: str
