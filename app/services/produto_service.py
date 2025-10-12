import app.database as database
from app.schemas import ProdutoIn, ProdutoOut, ProdutoUpdate
from bson import ObjectId

def product_helper(prod) -> ProdutoOut:
    return ProdutoOut(
        id=str(prod["_id"]),
        titulo=prod["titulo"],
        descricao=prod["descricao"],
        preco=prod["preco"],
        imagem=prod["imagem"],
        categoria_id=prod["categoria_id"],
        quantidade=prod.get("quantidade", 0),
        ativo=prod.get("ativo", True)
    )


async def create_product(prod: ProdutoIn) -> ProdutoOut:
    prod_dict = prod.dict()
    result = await database.db["produtos"].insert_one(prod_dict)
    prod_dict["_id"] = result.inserted_id
    return product_helper(prod_dict)


async def get_products() -> list[ProdutoOut]:
    produtos = []
    async for prod in database.db["produtos"].find():
        produtos.append(product_helper(prod))
    return produtos


async def get_product_by_id(prod_id: str) -> ProdutoOut | None:
    prod = await database.db["produtos"].find_one({"_id": ObjectId(prod_id)})
    if prod:
        return product_helper(prod)


async def update_product(prod_id: str, prod: ProdutoUpdate) -> ProdutoOut | None:
    update_data = {k: v for k, v in prod.dict().items() if v is not None}
    result = await database.db["produtos"].update_one(
        {"_id": ObjectId(prod_id)}, {"$set": update_data}
    )

    if result.modified_count == 1:
        return await get_product_by_id(prod_id)


async def delete_product(prod_id: str) -> bool:
    result = await database.db["produtos"].delete_one({"_id": ObjectId(prod_id)})
    return result.deleted_count == 1


async def alterar_quantidade_produto(produto_id: str, quantidade_alteracao: int) -> ProdutoOut | None:

    produto = await database.db["produtos"].find_one({"_id": ObjectId(produto_id)})
    if not produto:
        return None
    

    nova_quantidade = produto["quantidade"] + quantidade_alteracao
    if nova_quantidade < 0:
        return None
    
    result = await database.db["produtos"].update_one(
        {"_id": ObjectId(produto_id)},
        {"$inc": {"quantidade": quantidade_alteracao}}
    )
    
    if result.modified_count == 1:
        return await get_product_by_id(produto_id)
    return None

async def verificar_estoque_disponivel(produto_id: str, quantidade_desejada: int) -> bool:

    produto = await database.db["produtos"].find_one({"_id": ObjectId(produto_id)})
    if not produto:
        return False
    return produto["quantidade"] >= quantidade_desejada


async def alterar_status_produto(produto_id: str, ativo: bool) -> ProdutoOut | None:
    """
    Altera o status ativo/inativo de um produto
    """
    result = await database.db["produtos"].update_one(
        {"_id": ObjectId(produto_id)},
        {"$set": {"ativo": ativo}}
    )
    
    if result.modified_count == 1:
        return await get_product_by_id(produto_id)
    return None

async def migrar_produtos_existentes():

    result = await database.db["produtos"].update_many(
        {"quantidade": {"$exists": False}},
        {"$set": {"quantidade": 0}}
    )
    return result.modified_count
