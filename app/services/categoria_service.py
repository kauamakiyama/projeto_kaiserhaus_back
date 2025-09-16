import app.database as database
from app.schemas import CategoriaIn, CategoriaOut, CategoriaUpdate
from bson import ObjectId

def categoria_helper(cat) -> CategoriaOut:
    return CategoriaOut(
        id=str(cat["_id"]),
        nome=cat["nome"],
        descricao=cat["descricao"]
    )


async def create_categoria(cat: CategoriaIn) -> CategoriaOut:
    cat_dict = cat.dict()
    result = await database.db["categorias"].insert_one(cat_dict)
    cat_dict["_id"] = result.inserted_id
    return categoria_helper(cat_dict)


async def get_categorias() -> list[CategoriaOut]:
    categorias = []
    async for cat in database.db["categorias"].find():
        categorias.append(categoria_helper(cat))
    return categorias


async def get_categoria_by_id(cat_id: str) -> CategoriaOut | None:
    cat = await database.db["categorias"].find_one({"_id": ObjectId(cat_id)})
    if cat:
        return categoria_helper(cat)


async def update_categoria(cat_id: str, cat: CategoriaUpdate) -> CategoriaOut | None:
    update_data = {k: v for k, v in cat.dict().items() if v is not None}
    result = await database.db["categorias"].update_one(
        {"_id": ObjectId(cat_id)}, {"$set": update_data}
    )

    if result.modified_count == 1:
        return await get_categoria_by_id(cat_id)


async def delete_categoria(cat_id: str) -> bool:
    result = await database.db["categorias"].delete_one({"_id": ObjectId(cat_id)})
    return result.deleted_count == 1
