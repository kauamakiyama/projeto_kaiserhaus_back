from fastapi import APIRouter, HTTPException
from app.schemas import ProdutoIn, ProdutoOut, ProdutoUpdate
from app.services.produto_service import (
    create_product, get_products, get_product_by_id,
    update_product, delete_product
)

router = APIRouter()

@router.post("/", response_model=ProdutoOut)
async def create_product_route(prod: ProdutoIn):
    return await create_product(prod)

@router.get("/", response_model=list[ProdutoOut])
async def list_products_route():
    return await get_products()

@router.get("/{prod_id}", response_model=ProdutoOut)
async def get_product_route(prod_id: str):
    prod = await get_product_by_id(prod_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return prod

@router.put("/{prod_id}", response_model=ProdutoOut)
async def update_product_route(prod_id: str, prod: ProdutoUpdate):
    updated = await update_product(prod_id, prod)
    if not updated:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return updated

@router.delete("/{prod_id}")
async def delete_product_route(prod_id: str):
    deleted = await delete_product(prod_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return {"message": "Produto deletado com sucesso"}
