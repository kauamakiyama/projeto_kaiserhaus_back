from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import List, Optional, Union
from enum import Enum


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
    token: str
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


# ENUMS PARA CHECKOUT
class TipoEntrega(str, Enum):
    PADRAO = "padrao"
    TURBO = "turbo"

class MetodoPagamento(str, Enum):
    PIX = "pix"
    CARTAO = "cartao"
    DINHEIRO = "dinheiro"

class StatusPedido(str, Enum):
    PENDENTE = "pendente"
    EM_PREPARACAO = "em_preparacao"
    SAIU_PARA_ENTREGA = "saiu_para_entrega"
    CONCLUIDO = "concluido"

class StatusPagamento(str, Enum):
    PAGO = "pago"
    EXPIRADO = "expirado"
    PENDENTE = "pendente"


# SCHEMAS DE ENDEREÇO
class EnderecoEntrega(BaseModel):
    logradouro: str
    numero: str
    bairro: str
    cidade: str
    uf: str
    cep: str
    complemento: Optional[str] = None

class EntregaInfo(BaseModel):
    tipo: TipoEntrega
    endereco: EnderecoEntrega

class PagamentoInfo(BaseModel):
    metodo: MetodoPagamento
    cartaoId: Optional[int] = None
    trocoPara: Optional[float] = None


# SCHEMAS DE ITEM DO PEDIDO
class ItemPedidoIn(BaseModel):
    produtoId: Union[str, int]  # Aceita ObjectId (str) ou id numérico (int)
    quantidade: int
    observacoes: Optional[str] = None

class ProdutoInfo(BaseModel):
    nome: str
    preco: float
    imagem: Optional[str] = None
    categoria: Optional[str] = None

class ItemPedidoOut(BaseModel):
    id: str
    produtoId: Union[str, int]  # Aceita ObjectId (str) ou id numérico (int)
    quantidade: int
    observacoes: Optional[str] = None
    precoUnitario: float
    precoTotal: float
    nomeProduto: str
    imagemProduto: Optional[str] = None
    produto: Optional[ProdutoInfo] = None


# SCHEMAS DE PEDIDO (NOVO FORMATO)
class PedidoCheckoutIn(BaseModel):
    itens: List[ItemPedidoIn]
    entrega: EntregaInfo
    pagamento: PagamentoInfo

class PedidoCheckoutOut(BaseModel):
    pedidoId: int
    status: StatusPedido
    total: float
    taxaEntrega: float
    itens: List[ItemPedidoOut]
    pagamento: PagamentoInfo
    criadoEm: datetime
    atualizadoEm: datetime

class PedidoDetalhadoOut(BaseModel):
    id: int
    usuarioId: str  # Mudado de int para str (ObjectId)
    status: StatusPedido
    total: float
    taxaEntrega: float
    metodoPagamento: MetodoPagamento
    criadoEm: datetime
    atualizadoEm: datetime
    itens: List[ItemPedidoOut]
    endereco: EnderecoEntrega
    pagamento: Optional['PagamentoOut'] = None


# SCHEMAS DE PAGAMENTO
class PagamentoPixIn(BaseModel):
    pedidoId: int
    valor: float

class PagamentoPixOut(BaseModel):
    pedidoId: int
    qrcode: str
    copiaECola: str
    expiraEm: int

class PagamentoCartaoIn(BaseModel):
    pedidoId: int
    cartaoId: int

class PagamentoCartaoOut(BaseModel):
    pedidoId: int
    status: StatusPagamento
    transacaoId: str

class PagamentoWebhookIn(BaseModel):
    pedidoId: int
    status: StatusPagamento

class PagamentoOut(BaseModel):
    id: str  # Mudado de int para str (ObjectId)
    pedidoId: int
    metodo: MetodoPagamento
    valor: float
    status: StatusPagamento
    qrcode: Optional[str] = None
    copiaECola: Optional[str] = None
    transacaoId: Optional[str] = None
    criadoEm: datetime


# SCHEMAS DE LISTAGEM
class PedidoListaOut(BaseModel):
    id: int
    status: StatusPedido
    total: float
    metodoPagamento: MetodoPagamento
    criadoEm: datetime
    itens: List[ItemPedidoOut]

class PaginacaoPedidosOut(BaseModel):
    pedidos: List[PedidoListaOut]
    total: int
    page: int
    pageSize: int
    totalPages: int


# SCHEMAS DE CARTAO
class CartaoIn(BaseModel):
    numero: str
    mes: int
    ano: int
    cvv: str
    nome: str

class CartaoOut(BaseModel):
    id: str
    last4: str
    type: str
    nome: str
    mes: int
    ano: int
    usuarioId: str
    criadoEm: datetime

class CartaoSalvar(BaseModel):
    numero_criptografado: str
    cvv_criptografado: str
    nome: str
    mes: int
    ano: int
    bandeira: str
    last4: str
    usuarioId: str
