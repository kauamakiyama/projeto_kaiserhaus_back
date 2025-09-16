import app.database as database
from app.schemas import SacolaIn, SacolaOut, SacolaUpdate, ItemSacolaIn, ItemSacolaOut, ItemSacolaUpdate
from bson import ObjectId
from typing import List

def item_sacola_helper(item, produto_preco: float) -> ItemSacolaOut:
    return ItemSacolaOut(
        id=str(item["_id"]),
        produto_id=item["produto_id"],
        quantidade=item["quantidade"],
        preco_unitario=produto_preco,
        preco_total=item["quantidade"] * produto_preco
    )

def sacola_helper(sacola) -> SacolaOut:
    # Calcular total da sacola
    total = sum(item["quantidade"] * item.get("preco_unitario", 0) for item in sacola.get("itens", []))
    
    return SacolaOut(
        id=str(sacola["_id"]),
        usuario_id=sacola["usuario_id"],
        itens=[],  # Será preenchido com os itens completos
        total=total
    )

# CREATE
async def create_sacola(sacola: SacolaIn) -> SacolaOut:
    # Buscar preços dos produtos
    itens_com_preco = []
    for item in sacola.itens:
        produto = await database.db["produtos"].find_one({"_id": ObjectId(item.produto_id)})
        if produto:
            item_dict = item.dict()
            item_dict["preco_unitario"] = produto["preco"]
            itens_com_preco.append(item_dict)
    
    sacola_dict = {
        "usuario_id": sacola.usuario_id,
        "itens": itens_com_preco
    }
    
    result = await database.db["sacola"].insert_one(sacola_dict)
    sacola_dict["_id"] = result.inserted_id
    return await get_sacola_by_id(str(result.inserted_id))

# READ ALL
async def get_sacolas() -> list[SacolaOut]:
    sacolas = []
    async for sacola in database.db["sacola"].find():
        sacola_completa = await get_sacola_by_id(str(sacola["_id"]))
        if sacola_completa:
            sacolas.append(sacola_completa)
    return sacolas

# READ BY ID
async def get_sacola_by_id(sacola_id: str) -> SacolaOut | None:
    sacola = await database.db["sacola"].find_one({"_id": ObjectId(sacola_id)})
    if not sacola:
        return None
    
    # Buscar informações completas dos produtos
    itens_completos = []
    for item in sacola.get("itens", []):
        produto = await database.db["produtos"].find_one({"_id": ObjectId(item["produto_id"])})
        if produto:
            itens_completos.append(item_sacola_helper(item, produto["preco"]))
    
    return SacolaOut(
        id=str(sacola["_id"]),
        usuario_id=sacola["usuario_id"],
        itens=itens_completos,
        total=sum(item.preco_total for item in itens_completos)
    )

# READ BY USER ID
async def get_sacola_by_user_id(usuario_id: str) -> SacolaOut | None:
    sacola = await database.db["sacola"].find_one({"usuario_id": usuario_id})
    if sacola:
        return await get_sacola_by_id(str(sacola["_id"]))
    return None

# UPDATE
async def update_sacola(sacola_id: str, sacola: SacolaUpdate) -> SacolaOut | None:
    if sacola.itens:
        # Buscar preços dos produtos
        itens_com_preco = []
        for item in sacola.itens:
            produto = await database.db["produtos"].find_one({"_id": ObjectId(item.produto_id)})
            if produto:
                item_dict = item.dict()
                item_dict["preco_unitario"] = produto["preco"]
                itens_com_preco.append(item_dict)
        
        update_data = {"itens": itens_com_preco}
        result = await database.db["sacola"].update_one(
            {"_id": ObjectId(sacola_id)}, {"$set": update_data}
        )
        
        if result.modified_count == 1:
            return await get_sacola_by_id(sacola_id)
    return None

# ADD ITEM TO SACOLA
async def add_item_to_sacola(sacola_id: str, item: ItemSacolaIn) -> SacolaOut | None:
    produto = await database.db["produtos"].find_one({"_id": ObjectId(item.produto_id)})
    if not produto:
        return None
    
    item_dict = item.dict()
    item_dict["preco_unitario"] = produto["preco"]
    
    result = await database.db["sacola"].update_one(
        {"_id": ObjectId(sacola_id)},
        {"$push": {"itens": item_dict}}
    )
    
    if result.modified_count == 1:
        return await get_sacola_by_id(sacola_id)
    return None

# REMOVE ITEM FROM SACOLA
async def remove_item_from_sacola(sacola_id: str, item_id: str) -> SacolaOut | None:
    result = await database.db["sacola"].update_one(
        {"_id": ObjectId(sacola_id)},
        {"$pull": {"itens": {"_id": ObjectId(item_id)}}}
    )
    
    if result.modified_count == 1:
        return await get_sacola_by_id(sacola_id)
    return None

# DELETE
async def delete_sacola(sacola_id: str) -> bool:
    result = await database.db["sacola"].delete_one({"_id": ObjectId(sacola_id)})
    return result.deleted_count == 1

# CLEAR SACOLA
async def clear_sacola(sacola_id: str) -> SacolaOut | None:
    result = await database.db["sacola"].update_one(
        {"_id": ObjectId(sacola_id)},
        {"$set": {"itens": []}}
    )
    
    if result.modified_count == 1:
        return await get_sacola_by_id(sacola_id)
    return None
