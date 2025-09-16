from fastapi import APIRouter, HTTPException
from app.schemas import PedidoIn, PedidoOut, PedidoUpdate
from app.services.pedido_service import (
    create_pedido, get_pedidos, get_pedido_by_id, get_pedidos_by_user_id,
    get_pedidos_by_status, update_pedido, update_pedido_status,
    delete_pedido, get_pedidos_by_date_range
)
from datetime import date

router = APIRouter()

@router.post("/", response_model=PedidoOut)
async def create_pedido_route(pedido: PedidoIn):
    return await create_pedido(pedido)

@router.get("/", response_model=list[PedidoOut])
async def list_pedidos_route():
    return await get_pedidos()

@router.get("/{pedido_id}", response_model=PedidoOut)
async def get_pedido_route(pedido_id: str):
    pedido = await get_pedido_by_id(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido

@router.get("/usuario/{usuario_id}", response_model=list[PedidoOut])
async def get_pedidos_by_user_route(usuario_id: str):
    return await get_pedidos_by_user_id(usuario_id)

@router.get("/status/{status}", response_model=list[PedidoOut])
async def get_pedidos_by_status_route(status: str):
    return await get_pedidos_by_status(status)

@router.get("/periodo/{data_inicio}/{data_fim}", response_model=list[PedidoOut])
async def get_pedidos_by_date_range_route(data_inicio: date, data_fim: date):
    if data_inicio > data_fim:
        raise HTTPException(status_code=400, detail="Data de início deve ser anterior à data de fim")
    return await get_pedidos_by_date_range(data_inicio, data_fim)

@router.put("/{pedido_id}", response_model=PedidoOut)
async def update_pedido_route(pedido_id: str, pedido: PedidoUpdate):
    updated = await update_pedido(pedido_id, pedido)
    if not updated:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return updated

@router.patch("/{pedido_id}/status", response_model=PedidoOut)
async def update_pedido_status_route(pedido_id: str, status: str):
    status_validos = ["pendente", "confirmado", "preparando", "enviado", "entregue", "cancelado"]
    if status not in status_validos:
        raise HTTPException(status_code=400, detail=f"Status deve ser um dos seguintes: {', '.join(status_validos)}")
    
    updated = await update_pedido_status(pedido_id, status)
    if not updated:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return updated

@router.delete("/{pedido_id}")
async def delete_pedido_route(pedido_id: str):
    deleted = await delete_pedido(pedido_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return {"message": "Pedido deletado com sucesso"}
