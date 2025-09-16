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
        quantidade=prod.get("quantidade", 0)  # Usa 0 como padrão se não existir
    )

# CREATE
async def create_product(prod: ProdutoIn) -> ProdutoOut:
    prod_dict = prod.dict()
    result = await database.db["produtos"].insert_one(prod_dict)
    prod_dict["_id"] = result.inserted_id
    return product_helper(prod_dict)

# READ ALL
async def get_products() -> list[ProdutoOut]:
    produtos = []
    async for prod in database.db["produtos"].find():
        produtos.append(product_helper(prod))
    return produtos

# READ BY ID
async def get_product_by_id(prod_id: str) -> ProdutoOut | None:
    prod = await database.db["produtos"].find_one({"_id": ObjectId(prod_id)})
    if prod:
        return product_helper(prod)

# UPDATE
async def update_product(prod_id: str, prod: ProdutoUpdate) -> ProdutoOut | None:
    update_data = {k: v for k, v in prod.dict().items() if v is not None}
    result = await database.db["produtos"].update_one(
        {"_id": ObjectId(prod_id)}, {"$set": update_data}
    )

    if result.modified_count == 1:
        return await get_product_by_id(prod_id)

# DELETE
async def delete_product(prod_id: str) -> bool:
    result = await database.db["produtos"].delete_one({"_id": ObjectId(prod_id)})
    return result.deleted_count == 1

# FUNÇÕES DE ESTOQUE INTEGRADAS
async def alterar_quantidade_produto(produto_id: str, quantidade_alteracao: int) -> ProdutoOut | None:
    """
    Altera a quantidade do produto (aumentar ou diminuir)
    quantidade_alteracao: positivo para aumentar, negativo para diminuir
    """
    produto = await database.db["produtos"].find_one({"_id": ObjectId(produto_id)})
    if not produto:
        return None
    
    # Verificar se não vai ficar negativo
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
    """
    Verifica se tem estoque suficiente para a quantidade desejada
    """
    produto = await database.db["produtos"].find_one({"_id": ObjectId(produto_id)})
    if not produto:
        return False
    return produto["quantidade"] >= quantidade_desejada

# FUNÇÃO SIMPLES PARA MIGRAR PRODUTOS EXISTENTES
async def migrar_produtos_existentes():
    """
    Adiciona o campo quantidade com valor 0 para produtos que não têm esse campo
    """
    result = await database.db["produtos"].update_many(
        {"quantidade": {"$exists": False}},
        {"$set": {"quantidade": 0}}
    )
    return result.modified_count
