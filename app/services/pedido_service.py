import app.database as database
from app.schemas import PedidoIn, PedidoOut, PedidoUpdate, ItemSacolaIn, ItemSacolaOut
from bson import ObjectId
from datetime import datetime, date

def item_pedido_helper(item, produto_preco: float) -> ItemSacolaOut:
    return ItemSacolaOut(
        id=str(item["_id"]),
        produto_id=item["produto_id"],
        quantidade=item["quantidade"],
        preco_unitario=produto_preco,
        preco_total=item["quantidade"] * produto_preco
    )

def pedido_helper(pedido) -> PedidoOut:
    return PedidoOut(
        id=str(pedido["_id"]),
        usuario_id=pedido["usuario_id"],
        itens=[],  # Será preenchido com os itens completos
        endereco_entrega=pedido["endereco_entrega"],
        forma_pagamento=pedido["forma_pagamento"],
        status=pedido["status"],
        data_pedido=pedido["data_pedido"],
        total=pedido["total"]
    )

async def create_pedido(pedido: PedidoIn) -> PedidoOut:

    from app.services.produto_service import verificar_estoque_disponivel, alterar_quantidade_produto
    

    for item in pedido.itens:
        tem_estoque = await verificar_estoque_disponivel(item.produto_id, item.quantidade)
        if not tem_estoque:
            raise ValueError(f"Estoque insuficiente para o produto {item.produto_id}")
    
    itens_com_preco = []
    total = 0.0
    
    for item in pedido.itens:
        produto = await database.db["produtos"].find_one({"_id": ObjectId(item.produto_id)})
        if produto:
            item_dict = item.dict()
            item_dict["preco_unitario"] = produto["preco"]
            item_dict["preco_total"] = item.quantidade * produto["preco"]
            itens_com_preco.append(item_dict)
            total += item_dict["preco_total"]
    
    pedido_dict = {
        "usuario_id": pedido.usuario_id,
        "itens": itens_com_preco,
        "endereco_entrega": pedido.endereco_entrega,
        "forma_pagamento": pedido.forma_pagamento,
        "status": "pendente",
        "data_pedido": datetime.now().date(),
        "total": total
    }
    
    result = await database.db["pedidos"].insert_one(pedido_dict)
    pedido_dict["_id"] = result.inserted_id
    return await get_pedido_by_id(str(result.inserted_id))


async def get_pedidos() -> list[PedidoOut]:
    pedidos = []
    async for pedido in database.db["pedidos"].find():
        pedido_completo = await get_pedido_by_id(str(pedido["_id"]))
        if pedido_completo:
            pedidos.append(pedido_completo)
    return pedidos


async def get_pedido_by_id(pedido_id: str) -> PedidoOut | None:
    pedido = await database.db["pedidos"].find_one({"_id": ObjectId(pedido_id)})
    if not pedido:
        return None
    

    itens_completos = []
    for item in pedido.get("itens", []):
        produto = await database.db["produtos"].find_one({"_id": ObjectId(item["produto_id"])})
        if produto:
            itens_completos.append(item_pedido_helper(item, produto["preco"]))
    
    return PedidoOut(
        id=str(pedido["_id"]),
        usuario_id=pedido["usuario_id"],
        itens=itens_completos,
        endereco_entrega=pedido["endereco_entrega"],
        forma_pagamento=pedido["forma_pagamento"],
        status=pedido["status"],
        data_pedido=pedido["data_pedido"],
        total=pedido["total"]
    )


async def get_pedidos_by_user_id(usuario_id: str) -> list[PedidoOut]:
    pedidos = []
    async for pedido in database.db["pedidos"].find({"usuario_id": usuario_id}):
        pedido_completo = await get_pedido_by_id(str(pedido["_id"]))
        if pedido_completo:
            pedidos.append(pedido_completo)
    return pedidos


async def get_pedidos_by_status(status: str) -> list[PedidoOut]:
    pedidos = []
    async for pedido in database.db["pedidos"].find({"status": status}):
        pedido_completo = await get_pedido_by_id(str(pedido["_id"]))
        if pedido_completo:
            pedidos.append(pedido_completo)
    return pedidos


async def update_pedido(pedido_id: str, pedido: PedidoUpdate) -> PedidoOut | None:
    update_data = {k: v for k, v in pedido.dict().items() if v is not None}
    result = await database.db["pedidos"].update_one(
        {"_id": ObjectId(pedido_id)}, {"$set": update_data}
    )

    if result.modified_count == 1:
        return await get_pedido_by_id(pedido_id)
    return None


async def update_pedido_status(pedido_id: str, status: str) -> PedidoOut | None:

    from app.services.produto_service import alterar_quantidade_produto
    

    if status == "confirmado":
        pedido = await database.db["pedidos"].find_one({"_id": ObjectId(pedido_id)})
        if pedido:
            # Reduzir estoque para cada item do pedido
            for item in pedido.get("itens", []):
                await alterar_quantidade_produto(item["produto_id"], -item["quantidade"])
    
    result = await database.db["pedidos"].update_one(
        {"_id": ObjectId(pedido_id)}, {"$set": {"status": status}}
    )

    if result.modified_count == 1:
        return await get_pedido_by_id(pedido_id)
    return None


async def delete_pedido(pedido_id: str) -> bool:
    result = await database.db["pedidos"].delete_one({"_id": ObjectId(pedido_id)})
    return result.deleted_count == 1


async def get_pedidos_by_date_range(data_inicio: date, data_fim: date) -> list[PedidoOut]:
    pedidos = []
    async for pedido in database.db["pedidos"].find({
        "data_pedido": {"$gte": data_inicio, "$lte": data_fim}
    }):
        pedido_completo = await get_pedido_by_id(str(pedido["_id"]))
        if pedido_completo:
            pedidos.append(pedido_completo)
    return pedidos
