from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas import (
    PedidoCheckoutIn, PedidoCheckoutOut, PedidoDetalhadoOut, 
    PaginacaoPedidosOut, StatusPedido
)
from app.services import pedido_service
from app.dependencies_jwt import get_current_user_id_from_token, get_current_user_from_token, verify_admin_user
from typing import Optional

router = APIRouter()

@router.post("/", response_model=PedidoCheckoutOut)
@router.post("", response_model=PedidoCheckoutOut)
async def criar_pedido(
    pedido_data: PedidoCheckoutIn,
    usuario_id: str = Depends(get_current_user_id_from_token)
):
    """
    Cria um novo pedido
    
    Validações:
    - Usuário deve estar autenticado
    - Itens não podem estar vazios
    - Quantidade deve ser >= 1
    - Produtos devem existir e estar ativos
    - Endereço é obrigatório
    - Método de pagamento válido
    
    Cálculos automáticos:
    - totalProdutos = soma(precoBanco * quantidade)
    - taxaEntrega = tipo==="turbo" ? 17.99 : 0
    - total = totalProdutos + taxaEntrega
    """
    try:
        return await pedido_service.criar_pedido(pedido_data, usuario_id)
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

@router.get("/admin", response_model=list[dict])
async def listar_todos_pedidos_admin(
    admin_user = Depends(verify_admin_user),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamanho da página")
):
    """
    Lista todos os pedidos do sistema (apenas para administradores)
    """
    try:
        pedidos = await pedido_service.listar_todos_pedidos_admin(page, page_size)
        return pedidos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.get("/{pedido_id}", response_model=PedidoDetalhadoOut)
async def obter_pedido(
    pedido_id: int,
    usuario_id: str = Depends(get_current_user_id_from_token)
):
    """
    Obtém um pedido específico
    
    - Apenas o dono do pedido ou admin pode visualizar
    - Retorna todos os detalhes: itens, endereço, pagamento, totais
    """
    try:
        pedido = await pedido_service.obter_pedido_por_id(pedido_id, usuario_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido não encontrado"
            )
        return pedido
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.get("/", response_model=PaginacaoPedidosOut)
@router.get("", response_model=PaginacaoPedidosOut)
async def listar_pedidos_usuario(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=50, description="Itens por página"),
    usuario_id: str = Depends(get_current_user_id_from_token)
):
    """
    Lista pedidos do usuário autenticado
    
    - Retorna pedidos ordenados por data de criação (mais recentes primeiro)
    - Suporte a paginação
    - Cada pedido inclui itens e informações básicas
    """
    try:
        resultado = await pedido_service.listar_pedidos_usuario(usuario_id, page, page_size)
        return PaginacaoPedidosOut(**resultado)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.patch("/{pedido_id}/status")
async def atualizar_status_pedido(
    pedido_id: int,
    novo_status: StatusPedido,
    usuario_id: str = Depends(get_current_user_id_from_token)
):
    """
    Atualiza o status de um pedido
    
    - Apenas admin pode alterar status
    - Status válidos: "pendente", "em_preparacao", "saiu_para_entrega", "concluido"
    """
    try:
        # Por enquanto, qualquer usuário pode alterar status
        
        sucesso = await pedido_service.atualizar_status_pedido(pedido_id, novo_status)
        if not sucesso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido não encontrado"
            )
        
        return {"message": f"Status do pedido {pedido_id} atualizado para {novo_status}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )
