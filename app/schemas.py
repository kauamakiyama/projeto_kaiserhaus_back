from pydantic import BaseModel, EmailStr
from datetime import date
from typing import List, Optional


class UsuarioIn(BaseModel):   # Cadastro
    nome: str
    email: EmailStr
    cpf: str  # Obrigatório
    data_nascimento: str  # Aceita string para conversão posterior
    telefone: str
    endereco: str
    complemento: str
    senha: str   

class UsuarioOut(BaseModel): 
    id: str
    nome: str
    email: EmailStr
    cpf: str
    data_nascimento: date
    telefone: str
    endereco: str
    complemento: str
    hierarquia: str  

class UsuarioUpdate(BaseModel):  
    nome: str | None = None
    email: EmailStr | None = None
    cpf: str | None = None
    data_nascimento: str | None = None  # Aceita string para conversão posterior
    telefone: str | None = None
    endereco: str | None = None
    complemento: str | None = None
    senha: str | None = None

# SCHEMAS DE AUTENTICAÇÃO
class LoginIn(BaseModel):
    email: EmailStr
    senha: str

class LoginOut(BaseModel):
    message: str
    usuario: UsuarioOut

class LogoutOut(BaseModel):
    message: str

class TokenData(BaseModel):
    email: str | None = None


class CategoriaIn(BaseModel):
    nome: str
    descricao: str

class CategoriaOut(BaseModel):
    id: str
    nome: str
    descricao: str

class CategoriaUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None


class ProdutoIn(BaseModel):
    titulo: str
    descricao: str
    preco: float
    imagem: str
    categoria_id: str
    quantidade: int = 0

class ProdutoOut(BaseModel):
    id: str
    titulo: str
    descricao: str
    preco: float
    imagem: str
    categoria_id: str
    quantidade: int

class ProdutoUpdate(BaseModel):
    titulo: str | None = None
    descricao: str | None = None
    preco: float | None = None
    imagem: str | None = None
    categoria_id: str | None = None
    quantidade: int | None = None


class ItemSacolaIn(BaseModel):
    produto_id: str
    quantidade: int

class ItemSacolaOut(BaseModel):
    id: str
    produto_id: str
    quantidade: int
    preco_unitario: float
    preco_total: float

class ItemSacolaUpdate(BaseModel):
    quantidade: int | None = None


class SacolaIn(BaseModel):
    usuario_id: str
    itens: List[ItemSacolaIn]

class SacolaOut(BaseModel):
    id: str
    usuario_id: str
    itens: List[ItemSacolaOut]
    total: float

class SacolaUpdate(BaseModel):
    itens: List[ItemSacolaIn] | None = None


class PedidoIn(BaseModel):
    usuario_id: str
    itens: List[ItemSacolaIn]
    endereco_entrega: str
    forma_pagamento: str

class PedidoOut(BaseModel):
    id: str
    usuario_id: str
    itens: List[ItemSacolaOut]
    endereco_entrega: str
    forma_pagamento: str
    status: str
    data_pedido: date
    total: float

class PedidoUpdate(BaseModel):
    status: str | None = None
    endereco_entrega: str | None = None
    forma_pagamento: str | None = None
