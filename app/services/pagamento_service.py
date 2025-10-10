from app.database import get_database
from app.schemas import (
    PagamentoPixIn, PagamentoPixOut, PagamentoCartaoIn, PagamentoCartaoOut,
    PagamentoWebhookIn, PagamentoOut, StatusPagamento, MetodoPagamento
)
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Optional
import uuid
import base64
import os


# HELPERS PARA MONGODB
def pagamento_helper(pagamento) -> dict:
    if pagamento:
        return {
            "id": pagamento.get("_id"),
            "pagamentoId": pagamento.get("pagamentoId"),
            "pedidoId": pagamento.get("pedidoId"),
            "metodo": pagamento.get("metodo"),
            "valor": pagamento.get("valor"),
            "status": pagamento.get("status"),
            "qrcode": pagamento.get("qrcode"),
            "copiaECola": pagamento.get("copiaECola"),
            "transacaoId": pagamento.get("transacaoId"),
            "criadoEm": pagamento.get("criadoEm")
        }
    return None


# OPERAÇÕES DE PAGAMENTO PIX
async def criar_pagamento_pix(pagamento_data: PagamentoPixIn, usuario_id: str) -> PagamentoPixOut:
    """Cria um pagamento PIX com QR Code e código copia e cola"""
    from app.services.pedido_service import verificar_se_pedido_existe, obter_total_pedido
    
    db = await get_database()
    pagamentos = db.pagamentos
    
    # Valida se o pedido existe
    if not await verificar_se_pedido_existe(pagamento_data.pedidoId):
        raise ValueError("Pedido não encontrado")
    
    # Valida se o valor bate com o total do pedido
    total_pedido = await obter_total_pedido(pagamento_data.pedidoId)
    if total_pedido is None:
        raise ValueError("Não foi possível obter o total do pedido")
    
    if abs(pagamento_data.valor - total_pedido) > 0.01:  # Tolerância de 1 centavo
        raise ValueError(f"Valor do pagamento ({pagamento_data.valor}) não confere com o total do pedido ({total_pedido})")
    
    # Gera próximo ID do pagamento
    ultimo_pagamento = await pagamentos.find_one(sort=[("pagamentoId", -1)])
    proximo_id = (ultimo_pagamento["pagamentoId"] + 1) if ultimo_pagamento else 1
    
    agora = datetime.utcnow()
    expira_em = int((agora + timedelta(minutes=30)).timestamp())  # Expira em 30 minutos
    
    # Gera dados do PIX (mock)
    copia_e_cola = gerar_copia_e_cola(pagamento_data.pedidoId, pagamento_data.valor)
    qrcode_base64 = gerar_qrcode_mock(copia_e_cola)
    
    # Cria o pagamento
    pagamento_doc = {
        "pagamentoId": proximo_id,
        "pedidoId": pagamento_data.pedidoId,
        "metodo": MetodoPagamento.PIX,
        "valor": pagamento_data.valor,
        "status": StatusPagamento.PENDENTE,
        "qrcode": qrcode_base64,
        "copiaECola": copia_e_cola,
        "criadoEm": agora
    }
    
    await pagamentos.insert_one(pagamento_doc)
    
    return PagamentoPixOut(
        pedidoId=pagamento_data.pedidoId,
        qrcode=qrcode_base64,
        copiaECola=copia_e_cola,
        expiraEm=expira_em
    )

async def processar_webhook_pix(webhook_data: PagamentoWebhookIn) -> bool:
    """Processa webhook do PIX e atualiza status do pedido"""
    from app.services.pedido_service import atualizar_status_pedido
    
    db = await get_database()
    pagamentos = db.pagamentos
    
    # Atualiza status do pagamento
    resultado = await pagamentos.update_one(
        {"pedidoId": webhook_data.pedidoId, "metodo": MetodoPagamento.PIX},
        {
            "$set": {
                "status": webhook_data.status,
                "atualizadoEm": datetime.utcnow()
            }
        }
    )
    
    if resultado.modified_count == 0:
        return False
    
    # Se o pagamento foi aprovado, atualiza o status do pedido
    if webhook_data.status == StatusPagamento.PAGO:
        from app.schemas import StatusPedido
        await atualizar_status_pedido(webhook_data.pedidoId, StatusPedido.EM_PREPARACAO)
    
    return True

async def criar_pagamento_cartao(pagamento_data: PagamentoCartaoIn, usuario_id: str) -> PagamentoCartaoOut:
    """Cria um pagamento via cartão (simulado)"""
    from app.services.pedido_service import verificar_se_pedido_existe, obter_total_pedido
    
    db = await get_database()
    pagamentos = db.pagamentos
    
    # Valida se o pedido existe
    if not await verificar_se_pedido_existe(pagamento_data.pedidoId):
        raise ValueError("Pedido não encontrado")
    
    # Obtém o total do pedido
    total_pedido = await obter_total_pedido(pagamento_data.pedidoId)
    if total_pedido is None:
        raise ValueError("Não foi possível obter o total do pedido")
    
    # Gera próximo ID do pagamento
    ultimo_pagamento = await pagamentos.find_one(sort=[("pagamentoId", -1)])
    proximo_id = (ultimo_pagamento["pagamentoId"] + 1) if ultimo_pagamento else 1
    
    agora = datetime.utcnow()
    
    # Simula processamento do cartão (90% de aprovação)
    import random
    aprovado = random.random() < 0.9
    status = StatusPagamento.PAGO if aprovado else StatusPagamento.EXPIRADO
    transacao_id = str(uuid.uuid4())
    
    # Cria o pagamento
    pagamento_doc = {
        "pagamentoId": proximo_id,
        "pedidoId": pagamento_data.pedidoId,
        "metodo": MetodoPagamento.CARTAO,
        "valor": total_pedido,
        "status": status,
        "transacaoId": transacao_id,
        "criadoEm": agora
    }
    
    await pagamentos.insert_one(pagamento_doc)
    
    # Se aprovado, atualiza status do pedido
    if aprovado:
        from app.services.pedido_service import atualizar_status_pedido
        from app.schemas import StatusPedido
        await atualizar_status_pedido(pagamento_data.pedidoId, StatusPedido.EM_PREPARACAO)
    
    return PagamentoCartaoOut(
        pedidoId=pagamento_data.pedidoId,
        status=status,
        transacaoId=transacao_id
    )

async def obter_pagamento_por_pedido(pedido_id: int) -> Optional[PagamentoOut]:
    """Obtém informações de pagamento de um pedido"""
    db = await get_database()
    pagamentos = db.pagamentos
    
    pagamento = await pagamentos.find_one({"pedidoId": pedido_id})
    if not pagamento:
        return None
    
    return PagamentoOut(**pagamento_helper(pagamento))


# FUNÇÕES AUXILIARES
def gerar_copia_e_cola(pedido_id: int, valor: float) -> str:
    """Gera um código PIX copia e cola (mock)"""
    # Em uma implementação real, isso seria feito por um provedor PIX
    # Aqui estamos simulando o formato básico
    timestamp = int(datetime.utcnow().timestamp())
    
    # Simula um código PIX básico (formato simplificado)
    copia_e_cola = f"00020126580014br.gov.bcb.pix0136{pedido_id}520400005303986540{valor:.2f}5802BR5913Kaiserhaus6009SAO PAULO62070503***6304"
    
    # Adiciona checksum (simulado)
    checksum = str(hash(copia_e_cola) % 10000).zfill(4)
    copia_e_cola += checksum
    
    return copia_e_cola

def gerar_qrcode_mock(copia_e_cola: str) -> str:
    """Gera um QR Code mock em base64"""
    # Em uma implementação real, isso seria feito por uma biblioteca como qrcode
    # Aqui estamos simulando um QR Code simples
    
    # Cria um QR Code mock (imagem 200x200 pixels simples)
    # Em produção, usar: qrcode.make(copia_e_cola)
    
    # Simula uma imagem PNG simples (1x1 pixel branco)
    # Em produção, usar a biblioteca qrcode para gerar o QR Code real
    qr_mock = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
    
    return f"data:image/png;base64,{base64.b64encode(qr_mock).decode()}"

async def verificar_pagamento_pendente(pedido_id: int) -> bool:
    """Verifica se existe um pagamento pendente para o pedido"""
    db = await get_database()
    pagamentos = db.pagamentos
    
    pagamento = await pagamentos.find_one({
        "pedidoId": pedido_id,
        "status": StatusPagamento.PENDENTE
    })
    
    return pagamento is not None

async def cancelar_pagamentos_pendentes(pedido_id: int) -> bool:
    """Cancela pagamentos pendentes de um pedido"""
    db = await get_database()
    pagamentos = db.pagamentos
    
    resultado = await pagamentos.update_many(
        {
            "pedidoId": pedido_id,
            "status": StatusPagamento.PENDENTE
        },
        {
            "$set": {
                "status": StatusPagamento.EXPIRADO,
                "atualizadoEm": datetime.utcnow()
            }
        }
    )
    
    return resultado.modified_count > 0
