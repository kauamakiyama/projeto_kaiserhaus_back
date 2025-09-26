import app.database as database
from app.schemas import UsuarioIn, UsuarioOut, UsuarioUpdate
from bson import ObjectId
from passlib.hash import bcrypt
from datetime import datetime

def user_helper(user) -> UsuarioOut:
    # Converter string de data_nascimento de volta para date
    data_nascimento = user["data_nascimento"]
    if isinstance(data_nascimento, str):
        data_nascimento = datetime.strptime(data_nascimento, "%Y-%m-%d").date()
    
    return UsuarioOut(
        id=str(user["_id"]),
        nome=user["nome"],
        email=user["email"],
        data_nascimento=data_nascimento,
        telefone=user["telefone"],
        endereco=user["endereco"],
        complemento=user["complemento"],
        hierarquia=user.get("hierarquia", "usuario")   
    )


async def create_user(user: UsuarioIn) -> UsuarioOut:
    user_dict = user.dict()

    # Converter data_nascimento para string
    user_dict["data_nascimento"] = str(user_dict["data_nascimento"])
    
    # Criptografar senha
    user_dict["senha_hash"] = bcrypt.hash(user_dict["senha"])
    del user_dict["senha"]
    user_dict["hierarquia"] = "usuario"

    result = await database.db["usuarios"].insert_one(user_dict)
    user_dict["_id"] = result.inserted_id
    return user_helper(user_dict)


async def get_users() -> list[UsuarioOut]:
    usuarios = []
    async for user in database.db["usuarios"].find():
        usuarios.append(user_helper(user))
    return usuarios

async def get_user_by_id(user_id: str) -> UsuarioOut | None:
    user = await database.db["usuarios"].find_one({"_id": ObjectId(user_id)})
    if user:
        return user_helper(user)

async def update_user(user_id: str, user: UsuarioUpdate) -> UsuarioOut | None:
    update_data = {k: v for k, v in user.dict().items() if v is not None}
    
    # Converter data_nascimento para string se existir
    if "data_nascimento" in update_data:
        update_data["data_nascimento"] = str(update_data["data_nascimento"])
    
    if "senha" in update_data:
        update_data["senha_hash"] = bcrypt.hash(update_data["senha"])
        del update_data["senha"]  # Remove a senha em texto plano

    result = await database.db["usuarios"].update_one(
        {"_id": ObjectId(user_id)}, {"$set": update_data}
    )

    if result.modified_count == 1:
        return await get_user_by_id(user_id)

async def delete_user(user_id: str) -> bool:
    result = await database.db["usuarios"].delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count == 1
