from fastapi import APIRouter, HTTPException
from app.schemas import CategoriaIn, CategoriaOut, CategoriaUpdate
from app.services.categoria_service import (
    create_categoria, get_categorias, get_categoria_by_id,
    update_categoria, delete_categoria
)

router = APIRouter()

@router.post("/", response_model=CategoriaOut)
async def create_categoria_route(cat: CategoriaIn):
    return await create_categoria(cat)

@router.get("/", response_model=list[CategoriaOut])
async def list_categorias_route():
    return await get_categorias()

@router.get("/{cat_id}", response_model=CategoriaOut)
async def get_categoria_route(cat_id: str):
    cat = await get_categoria_by_id(cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return cat

@router.put("/{cat_id}", response_model=CategoriaOut)
async def update_categoria_route(cat_id: str, cat: CategoriaUpdate):
    updated = await update_categoria(cat_id, cat)
    if not updated:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return updated

@router.delete("/{cat_id}")
async def delete_categoria_route(cat_id: str):
    deleted = await delete_categoria(cat_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return {"message": "Categoria deletada com sucesso"}
