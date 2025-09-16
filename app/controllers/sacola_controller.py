from fastapi import APIRouter, HTTPException
from app.schemas import SacolaIn, SacolaOut, SacolaUpdate, ItemSacolaIn
from app.services.sacola_service import (
    create_sacola, get_sacolas, get_sacola_by_id, get_sacola_by_user_id,
    update_sacola, add_item_to_sacola, remove_item_from_sacola,
    delete_sacola, clear_sacola
)

router = APIRouter()

@router.post("/", response_model=SacolaOut)
async def create_sacola_route(sacola: SacolaIn):
    return await create_sacola(sacola)

@router.get("/", response_model=list[SacolaOut])
async def list_sacolas_route():
    return await get_sacolas()

@router.get("/{sacola_id}", response_model=SacolaOut)
async def get_sacola_route(sacola_id: str):
    sacola = await get_sacola_by_id(sacola_id)
    if not sacola:
        raise HTTPException(status_code=404, detail="Sacola não encontrada")
    return sacola

@router.get("/usuario/{usuario_id}", response_model=SacolaOut)
async def get_sacola_by_user_route(usuario_id: str):
    sacola = await get_sacola_by_user_id(usuario_id)
    if not sacola:
        raise HTTPException(status_code=404, detail="Sacola não encontrada para este usuário")
    return sacola

@router.put("/{sacola_id}", response_model=SacolaOut)
async def update_sacola_route(sacola_id: str, sacola: SacolaUpdate):
    updated = await update_sacola(sacola_id, sacola)
    if not updated:
        raise HTTPException(status_code=404, detail="Sacola não encontrada")
    return updated

@router.post("/{sacola_id}/itens", response_model=SacolaOut)
async def add_item_to_sacola_route(sacola_id: str, item: ItemSacolaIn):
    if item.quantidade <= 0:
        raise HTTPException(status_code=400, detail="Quantidade deve ser maior que zero")
    
    updated = await add_item_to_sacola(sacola_id, item)
    if not updated:
        raise HTTPException(status_code=404, detail="Sacola não encontrada")
    return updated

@router.delete("/{sacola_id}/itens/{item_id}", response_model=SacolaOut)
async def remove_item_from_sacola_route(sacola_id: str, item_id: str):
    updated = await remove_item_from_sacola(sacola_id, item_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Sacola ou item não encontrado")
    return updated

@router.delete("/{sacola_id}/limpar", response_model=SacolaOut)
async def clear_sacola_route(sacola_id: str):
    cleared = await clear_sacola(sacola_id)
    if not cleared:
        raise HTTPException(status_code=404, detail="Sacola não encontrada")
    return cleared

@router.delete("/{sacola_id}")
async def delete_sacola_route(sacola_id: str):
    deleted = await delete_sacola(sacola_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sacola não encontrada")
    return {"message": "Sacola deletada com sucesso"}
