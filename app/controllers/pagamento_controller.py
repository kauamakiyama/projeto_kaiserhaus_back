from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import (
    PagamentoPixIn, PagamentoPixOut, PagamentoCartaoIn, PagamentoCartaoOut,
    PagamentoWebhookIn, PagamentoOut
)
from app.services import pagamento_service
from app.dependencies_jwt import get_current_user_id_from_token
from typing import Optional

router = APIRouter()

@router.post("/pix", response_model=PagamentoPixOut)
async def criar_pagamento_pix(
    pagamento_data: PagamentoPixIn,
    usuario_id: str = Depends(get_current_user_id_from_token)
):
    """
    Cria um pagamento PIX
    
    - Gera QR Code em base64
    - Gera código copia e cola
    - Define expiração em 30 minutos
    - Valida se o valor confere com o total do pedido
    """
    try:
        return await pagamento_service.criar_pagamento_pix(pagamento_data, usuario_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.post("/pix/webhook")
async def webhook_pagamento_pix(webhook_data: PagamentoWebhookIn):
    """
    Webhook para receber notificações de pagamento PIX
    
    - Endpoint público (não requer autenticação)
    - Recebe status: "pago" ou "expirado"
    - Atualiza automaticamente o status do pedido quando pago
    """
    try:
        sucesso = await pagamento_service.processar_webhook_pix(webhook_data)
        if not sucesso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pagamento não encontrado"
            )
        
        return {"message": f"Webhook processado com sucesso. Status: {webhook_data.status}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.post("/cartao", response_model=PagamentoCartaoOut)
async def criar_pagamento_cartao(
    pagamento_data: PagamentoCartaoIn,
    usuario_id: str = Depends(get_current_user_id_from_token)
):
    """
    Cria um pagamento via cartão (simulado)
    
    - Simula autorização do cartão (90% de aprovação)
    - Retorna status: "pago" se aprovado, "expirado" se negado
    - Atualiza automaticamente o status do pedido quando aprovado
    """
    try:
        return await pagamento_service.criar_pagamento_cartao(pagamento_data, usuario_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.get("/pedido/{pedido_id}", response_model=Optional[PagamentoOut])
async def obter_pagamento_pedido(
    pedido_id: int,
    usuario_id: str = Depends(get_current_user_id_from_token)
):
    """
    Obtém informações de pagamento de um pedido
    
    - Retorna dados do pagamento (PIX, cartão, etc.)
    - Inclui QR Code, códigos de transação, status
    """
    try:
        pagamento = await pagamento_service.obter_pagamento_por_pedido(pedido_id)
        if not pagamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pagamento não encontrado para este pedido"
            )
        return pagamento
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.post("/pix/simular-pagamento")
async def simular_pagamento_pix(
    pedido_id: int,
    status_pagamento: str,
    usuario_id: str = Depends(get_current_user_id_from_token)
):
    """
    Endpoint para simular pagamento PIX (apenas para testes)
    
    - Simula o webhook do PIX
    - Útil para testes de desenvolvimento
    """
    try:
        from app.schemas import StatusPagamento
        
        if status_pagamento not in ["pago", "expirado"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status deve ser 'pago' ou 'expirado'"
            )
        
        webhook_data = PagamentoWebhookIn(
            pedidoId=pedido_id,
            status=StatusPagamento(status_pagamento)
        )
        
        sucesso = await pagamento_service.processar_webhook_pix(webhook_data)
        if not sucesso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pagamento não encontrado"
            )
        
        return {"message": f"Pagamento simulado com sucesso. Status: {status_pagamento}"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

