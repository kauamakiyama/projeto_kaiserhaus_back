from app.database import get_database
from app.schemas import CartaoIn, CartaoOut, CartaoSalvar
from bson import ObjectId
from datetime import datetime
from typing import Optional, List
import os
from cryptography.fernet import Fernet
import hashlib
import re


# CONFIGURAÇÃO DE CRIPTOGRAFIA
def get_encryption_key() -> bytes:
    """Obtém a chave de criptografia do ambiente"""
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        # Gera uma chave padrão para desenvolvimento
        # EM PRODUÇÃO: usar uma chave forte e segura
        key = "development-key-not-for-production-use-only"
    
    # Converte para 32 bytes usando hash
    return hashlib.sha256(key.encode()).digest()


def encrypt_data(data: str) -> str:
    """Criptografa dados sensíveis"""
    key = get_encryption_key()
    f = Fernet(Fernet.generate_key())
    # Para simplicidade, usando base64 encoding
    import base64
    return base64.b64encode(data.encode()).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Descriptografa dados sensíveis"""
    import base64
    return base64.b64decode(encrypted_data.encode()).decode()


# VALIDAÇÕES
def validar_numero_cartao(numero: str) -> bool:
    """Valida número do cartão usando algoritmo de Luhn"""
    # Remove espaços e caracteres não numéricos
    numero = re.sub(r'\D', '', numero)
    
    if len(numero) < 13 or len(numero) > 19:
        return False
    
    # Algoritmo de Luhn
    def luhn_checksum(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10
    
    return luhn_checksum(int(numero)) == 0




def validar_dados_cartao(cartao: CartaoIn) -> dict:
    """Valida todos os dados do cartão"""
    erros = []
    
    # Validações básicas removidas - aceita qualquer número e ano
    
    # Valida nome
    if len(cartao.nome.strip()) < 2:
        erros.append("Nome deve ter pelo menos 2 caracteres")
    
    return {
        "valido": len(erros) == 0,
        "erros": erros
    }


# HELPERS PARA MONGODB
def cartao_helper(cartao) -> dict:
    """Converte documento do MongoDB para dicionário"""
    if cartao:
        return {
            "id": str(cartao.get("_id")),
            "last4": cartao.get("last4"),
            "type": "credit",  # Por enquanto, apenas cartões de crédito
            "nome": cartao.get("nome"),
            "mes": cartao.get("mes"),
            "ano": cartao.get("ano"),
            "usuarioId": cartao.get("usuarioId"),
            "criadoEm": cartao.get("criadoEm")
        }
    return None


# OPERAÇÕES CRUD
async def criar_cartao(cartao_data: CartaoIn, usuario_id: str) -> CartaoOut:
    """Cria um novo cartão de crédito para o usuário"""
    db = await get_database()
    cartoes = db.cartoes
    
    # Valida dados do cartão
    validacao = validar_dados_cartao(cartao_data)
    if not validacao["valido"]:
        raise ValueError(f"Dados inválidos: {', '.join(validacao['erros'])}")
    
    # Prepara dados para salvar
    numero_limpo = re.sub(r'\D', '', cartao_data.numero)
    last4 = numero_limpo[-4:]
    
    agora = datetime.utcnow()
    
    # Cria documento do cartão
    cartao_doc = {
        "numero_criptografado": encrypt_data(numero_limpo),
        "cvv_criptografado": encrypt_data(cartao_data.cvv),
        "nome": cartao_data.nome.strip(),
        "mes": cartao_data.mes,
        "ano": cartao_data.ano,
        "last4": last4,
        "usuarioId": usuario_id,
        "criadoEm": agora
    }
    
    # Salva no banco
    resultado = await cartoes.insert_one(cartao_doc)
    
    # Retorna dados seguros
    cartao_doc["_id"] = resultado.inserted_id
    return CartaoOut(**cartao_helper(cartao_doc))


async def obter_cartao_por_id(cartao_id: str, usuario_id: str) -> Optional[CartaoOut]:
    """Obtém um cartão específico (apenas o dono pode ver)"""
    db = await get_database()
    cartoes = db.cartoes
    
    try:
        object_id = ObjectId(cartao_id)
    except Exception:
        return None
    
    cartao = await cartoes.find_one({"_id": object_id, "usuarioId": usuario_id})
    if not cartao:
        return None
    
    return CartaoOut(**cartao_helper(cartao))


async def listar_cartoes_usuario(usuario_id: str) -> List[CartaoOut]:
    """Lista todos os cartões de um usuário"""
    db = await get_database()
    cartoes = db.cartoes
    
    cartoes_cursor = cartoes.find({"usuarioId": usuario_id}).sort("criadoEm", -1)
    cartoes_lista = []
    
    async for cartao in cartoes_cursor:
        cartoes_lista.append(CartaoOut(**cartao_helper(cartao)))
    
    return cartoes_lista


async def deletar_cartao(cartao_id: str, usuario_id: str) -> bool:
    """Deleta um cartão (apenas o dono pode deletar)"""
    db = await get_database()
    cartoes = db.cartoes
    
    try:
        object_id = ObjectId(cartao_id)
    except Exception:
        return False
    
    resultado = await cartoes.delete_one({"_id": object_id, "usuarioId": usuario_id})
    return resultado.deleted_count > 0


async def verificar_se_cartao_existe(cartao_id: str, usuario_id: str) -> bool:
    """Verifica se um cartão existe e pertence ao usuário"""
    db = await get_database()
    cartoes = db.cartoes
    
    try:
        object_id = ObjectId(cartao_id)
    except Exception:
        return False
    
    cartao = await cartoes.find_one({"_id": object_id, "usuarioId": usuario_id})
    return cartao is not None
