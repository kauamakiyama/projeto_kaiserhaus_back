import app.database as database
from app.schemas import ProdutoIn, ProdutoOut, ProdutoUpdate
from bson import ObjectId

def product_helper(prod) -> ProdutoOut:
    return ProdutoOut(
        id=str(prod["_id"]),
        imagem=prod["imagem"],
        titulo=prod["titulo"],
        descricao=prod["descricao"],
        preco=prod["preco"]
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
