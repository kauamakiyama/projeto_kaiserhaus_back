from fastapi import APIRouter, HTTPException
from app.schemas import ProdutoIn, ProdutoOut, ProdutoUpdate
from app.services import produto_service

router = APIRouter()

@router.post("/", response_model=ProdutoOut)
async def create_product_route(prod: ProdutoIn):
    return await produto_service.create_product(prod)

@router.get("/", response_model=list[ProdutoOut])
async def list_products_route():
    return await produto_service.get_products()

@router.get("/{prod_id}", response_model=ProdutoOut)
async def get_product_route(prod_id: str):
    prod = await produto_service.get_product_by_id(prod_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return prod

@router.put("/{prod_id}", response_model=ProdutoOut)
async def update_product_route(prod_id: str, prod: ProdutoUpdate):
    updated = await produto_service.update_product(prod_id, prod)
    if not updated:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return updated

@router.delete("/{prod_id}")
async def delete_product_route(prod_id: str):
    deleted = await produto_service.delete_product(prod_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return {"message": "Produto deletado com sucesso"}


@router.patch("/{produto_id}/adicionar-estoque")
async def adicionar_estoque_route(produto_id: str, quantidade: int):

    if quantidade <= 0:
        raise HTTPException(status_code=400, detail="Quantidade deve ser maior que zero")
    
    produto = await produto_service.alterar_quantidade_produto(produto_id, quantidade)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto

@router.patch("/{produto_id}/remover-estoque")
async def remover_estoque_route(produto_id: str, quantidade: int):

    if quantidade <= 0:
        raise HTTPException(status_code=400, detail="Quantidade deve ser maior que zero")
    
    produto = await produto_service.alterar_quantidade_produto(produto_id, -quantidade)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado ou quantidade insuficiente")
    return produto

@router.get("/{produto_id}/tem-estoque")
async def verificar_estoque_route(produto_id: str, quantidade_desejada: int):

    tem_estoque = await produto_service.verificar_estoque_disponivel(produto_id, quantidade_desejada)
    return {
        "produto_id": produto_id,
        "quantidade_desejada": quantidade_desejada,
        "tem_estoque": tem_estoque
    }

@router.post("/migrar")
async def migrar_produtos_route():

    produtos_migrados = await produto_service.migrar_produtos_existentes()
    return {
        "message": f"Migração concluída! {produtos_migrados} produtos foram atualizados.",
        "produtos_migrados": produtos_migrados
    }
