from app.database import get_database
from app.schemas import (
    PedidoCheckoutIn, PedidoCheckoutOut, PedidoDetalhadoOut, 
    ItemPedidoOut, StatusPedido, TipoEntrega, MetodoPagamento
)
from bson import ObjectId
from datetime import datetime
from typing import List, Optional, Union
import math


def resolver_produto_id(produto_id: Union[str, int]) -> dict:
    """
    Resolve o ID do produto para a query do MongoDB
    - Se for string: trata como ObjectId
    - Se for int: usa produtoId numérico
    """
    if isinstance(produto_id, str):
        try:
            object_id = ObjectId(produto_id)
            return {"_id": object_id, "ativo": True}
        except Exception:
            return {"produtoId": produto_id, "ativo": True}
    else:
        return {"produtoId": produto_id, "ativo": True}

def pedido_helper(pedido) -> dict:
    if pedido:
        return {
            "id": pedido.get("_id"),
            "pedidoId": pedido.get("pedidoId"),
            "usuarioId": pedido.get("usuarioId"),
            "status": pedido.get("status"),
            "total": pedido.get("total"),
            "taxaEntrega": pedido.get("taxaEntrega"),
            "metodoPagamento": pedido.get("metodoPagamento"),
            "criadoEm": pedido.get("criadoEm"),
            "atualizadoEm": pedido.get("atualizadoEm")
        }
    return None

def item_pedido_helper(item) -> dict:
    if item:
        return {
            "id": str(item.get("_id")),
            "produtoId": item.get("produtoId"),
            "quantidade": item.get("quantidade"),
            "observacoes": item.get("observacoes"),
            "precoUnitario": item.get("precoUnitario"),
            "precoTotal": item.get("precoTotal"),
            "nomeProduto": item.get("nomeProduto")
        }
    return None

def endereco_helper(endereco) -> dict:
    if endereco:
        return {
            "logradouro": endereco.get("logradouro"),
            "numero": endereco.get("numero"),
            "bairro": endereco.get("bairro"),
            "cidade": endereco.get("cidade"),
            "uf": endereco.get("uf"),
            "cep": endereco.get("cep"),
            "complemento": endereco.get("complemento")
        }
    return None

def pagamento_helper(pagamento) -> dict:
    if pagamento:
        return {
            "id": str(pagamento.get("_id")),
            "pedidoId": pagamento.get("pedidoId"),
            "metodo": pagamento.get("metodo"),
            "valor": pagamento.get("valor"),
            "status": pagamento.get("status"),
            "qrcode": pagamento.get("qrcode"),
            "copiaECola": pagamento.get("copiaECola"),
            "transacaoId": pagamento.get("transacaoId"),
            "criadoEm": pagamento.get("criadoEm")
        }
    return None


async def validar_produtos_existentes(produto_ids: List[Union[str, int]]) -> bool:
    """Valida se todos os produtos existem e estão ativos"""
    db = await get_database()
    produtos = db.produtos
    
    for produto_id in produto_ids:
        query = resolver_produto_id(produto_id)
        produto = await produtos.find_one(query)
        if not produto:
            return False
    return True

async def calcular_totais(itens: List[dict], tipo_entrega: str) -> dict:
    """Calcula total de produtos, taxa de entrega e total final"""
    db = await get_database()
    produtos = db.produtos
    
    total_produtos = 0.0
    
    for item in itens:
        query = resolver_produto_id(item["produtoId"])
        produto = await produtos.find_one(query)
        
        if not produto:
            raise ValueError(f"Produto {item['produtoId']} não encontrado ou inativo")
        
        preco_unitario = float(produto["preco"])
        quantidade = item["quantidade"]
        total_item = preco_unitario * quantidade
        
        total_produtos += total_item
        
        item["precoUnitario"] = preco_unitario
        item["precoTotal"] = total_item
        item["nomeProduto"] = produto["titulo"]
        item["imagemProduto"] = produto.get("imagem")
    
    taxa_entrega = 17.99 if tipo_entrega == TipoEntrega.TURBO else 0.0
    total_final = total_produtos + taxa_entrega
    
    return {
        "totalProdutos": total_produtos,
        "taxaEntrega": taxa_entrega,
        "total": total_final,
        "itens": itens
    }


async def criar_pedido(pedido_data: PedidoCheckoutIn, usuario_id: str) -> PedidoCheckoutOut:
    """Cria um novo pedido com validações"""
    db = await get_database()
    pedidos = db.pedidos
    itens_pedido = db.itens_pedido
    enderecos = db.enderecos
    
    if not pedido_data.itens:
        raise ValueError("Pedido deve conter pelo menos um item")
    
    for item in pedido_data.itens:
        if item.quantidade < 1:
            raise ValueError("Quantidade deve ser maior que 0")
    
    produto_ids = [item.produtoId for item in pedido_data.itens]
    if not await validar_produtos_existentes(produto_ids):
        raise ValueError("Um ou mais produtos não existem ou estão inativos")
    
    itens_dict = [item.dict() for item in pedido_data.itens]
    totais = await calcular_totais(itens_dict, pedido_data.entrega.tipo)
    
    ultimo_pedido = await pedidos.find_one(sort=[("pedidoId", -1)])
    proximo_id = (ultimo_pedido["pedidoId"] + 1) if ultimo_pedido else 1
    
    agora = datetime.utcnow()
    
    itens_com_id = []
    for i, item in enumerate(totais["itens"]):
        produto = await db.produtos.find_one(resolver_produto_id(item["produtoId"]))
        
        item_com_id = {
            "id": f"item_{proximo_id}_{i}",
            "produtoId": item["produtoId"],
            "quantidade": item["quantidade"],
            "observacoes": item.get("observacoes"),
            "precoUnitario": item["precoUnitario"],
            "precoTotal": item["precoTotal"],
            "nomeProduto": item["nomeProduto"],
            "imagemProduto": item.get("imagemProduto"),
            "produto": {
                "nome": produto["titulo"] if produto else "Produto não encontrado",
                "preco": produto["preco"] if produto else 0.0,
                "imagem": produto.get("imagem") if produto else None,
                "categoria": produto.get("categoria_id") if produto else None
            }
        }
        itens_com_id.append(item_com_id)
    
    pedido_doc = {
        "pedidoId": proximo_id,
        "usuarioId": usuario_id,
        "status": StatusPedido.PENDENTE,
        "total": totais["total"],
        "taxaEntrega": totais["taxaEntrega"],
        "metodoPagamento": pedido_data.pagamento.metodo,
        "itens": itens_com_id,
        "criadoEm": agora,
        "atualizadoEm": agora
    }
    
    resultado_pedido = await pedidos.insert_one(pedido_doc)
    pedido_id = resultado_pedido.inserted_id
    
    endereco_doc = {
        "pedidoId": proximo_id,
        "logradouro": pedido_data.entrega.endereco.logradouro,
        "numero": pedido_data.entrega.endereco.numero,
        "bairro": pedido_data.entrega.endereco.bairro,
        "cidade": pedido_data.entrega.endereco.cidade,
        "uf": pedido_data.entrega.endereco.uf,
        "cep": pedido_data.entrega.endereco.cep,
        "complemento": pedido_data.entrega.endereco.complemento
    }
    await enderecos.insert_one(endereco_doc)
    itens_response = [ItemPedidoOut(**item) for item in itens_com_id]
    
    return PedidoCheckoutOut(
        pedidoId=proximo_id,
        status=StatusPedido.PENDENTE,
        total=totais["total"],
        taxaEntrega=totais["taxaEntrega"],
        itens=itens_response,
        pagamento=pedido_data.pagamento,
        criadoEm=agora,
        atualizadoEm=agora
    )

async def obter_pedido_por_id(pedido_id: int, usuario_id: str) -> Optional[PedidoDetalhadoOut]:
    """Obtém um pedido específico (apenas o dono ou admin pode ver)"""
    db = await get_database()
    pedidos = db.pedidos
    enderecos = db.enderecos
    pagamentos = db.pagamentos
    
    pedido = await pedidos.find_one({"pedidoId": pedido_id})
    if not pedido:
        return None
    
    if pedido["usuarioId"] != usuario_id:
        raise PermissionError("Você não tem permissão para ver este pedido")
    
    itens = [ItemPedidoOut(**item) for item in pedido.get("itens", [])]
    
    endereco_doc = await enderecos.find_one({"pedidoId": pedido_id})
    endereco = endereco_helper(endereco_doc) if endereco_doc else None
    
    pagamento_doc = await pagamentos.find_one({"pedidoId": pedido_id})
    pagamento = pagamento_helper(pagamento_doc) if pagamento_doc else None
    
    return PedidoDetalhadoOut(
        id=pedido["pedidoId"],
        usuarioId=pedido["usuarioId"],
        status=StatusPedido(pedido["status"]),
        total=pedido["total"],
        taxaEntrega=pedido["taxaEntrega"],
        metodoPagamento=MetodoPagamento(pedido["metodoPagamento"]),
        criadoEm=pedido["criadoEm"],
        atualizadoEm=pedido["atualizadoEm"],
        itens=itens,
        endereco=endereco,
        pagamento=pagamento
    )

async def listar_pedidos_usuario(usuario_id: str, page: int = 1, page_size: int = 10) -> dict:
    """Lista pedidos de um usuário com paginação"""
    db = await get_database()
    pedidos = db.pedidos
    
    skip = (page - 1) * page_size
    
    pedidos_cursor = pedidos.find(
        {"usuarioId": usuario_id}
    ).sort("criadoEm", -1).skip(skip).limit(page_size)
    
    pedidos_lista = []
    total_pedidos = await pedidos.count_documents({"usuarioId": usuario_id})
    
    async for pedido in pedidos_cursor:
        itens = [ItemPedidoOut(**item) for item in pedido.get("itens", [])]
        
        pedidos_lista.append({
            "id": pedido["pedidoId"],
            "status": StatusPedido(pedido["status"]),
            "total": pedido["total"],
            "metodoPagamento": MetodoPagamento(pedido["metodoPagamento"]),
            "criadoEm": pedido["criadoEm"],
            "itens": itens
        })
    
    total_pages = math.ceil(total_pedidos / page_size)
    
    return {
        "pedidos": pedidos_lista,
        "total": total_pedidos,
        "page": page,
        "pageSize": page_size,
        "totalPages": total_pages
    }

async def atualizar_status_pedido(pedido_id: int, novo_status: StatusPedido) -> bool:
    """Atualiza o status de um pedido"""
    db = await get_database()
    pedidos = db.pedidos
    
    resultado = await pedidos.update_one(
        {"pedidoId": pedido_id},
        {
            "$set": {
                "status": novo_status,
                "atualizadoEm": datetime.utcnow()
            }
        }
    )
    
    return resultado.modified_count > 0

async def verificar_se_pedido_existe(pedido_id: int) -> bool:
    """Verifica se um pedido existe"""
    db = await get_database()
    pedidos = db.pedidos
    
    pedido = await pedidos.find_one({"pedidoId": pedido_id})
    return pedido is not None

async def obter_total_pedido(pedido_id: int) -> Optional[float]:
    """Obtém o total de um pedido"""
    db = await get_database()
    pedidos = db.pedidos
    
    pedido = await pedidos.find_one({"pedidoId": pedido_id})
    return pedido["total"] if pedido else None

async def listar_todos_pedidos_admin(page: int = 1, page_size: int = 10) -> list[dict]:
    """Lista todos os pedidos do sistema (apenas para admin)"""
    db = await get_database()
    pedidos = db.pedidos
    
    offset = (page - 1) * page_size
    
    pedidos_cursor = pedidos.find().sort("criadoEm", -1).skip(offset).limit(page_size)
    
    pedidos_lista = []
    async for pedido in pedidos_cursor:
        itens = [ItemPedidoOut(**item) for item in pedido.get("itens", [])]

        pedidos_lista.append({
            "id": pedido["pedidoId"],
            "usuarioId": pedido["usuarioId"],
            "status": StatusPedido(pedido["status"]),
            "total": pedido["total"],
            "metodoPagamento": MetodoPagamento(pedido["metodoPagamento"]),
            "criadoEm": pedido["criadoEm"],
            "atualizadoEm": pedido.get("atualizadoEm"),
            "itens": itens
        })
    
    return pedidos_lista

async def obter_contadores_pedidos() -> dict:
    """Retorna contadores de pedidos por status"""
    db = await get_database()
    pedidos = db.pedidos
    
    # Contar pedidos por status
    pendentes = await pedidos.count_documents({"status": "pendente"})
    em_preparacao = await pedidos.count_documents({"status": "em_preparacao"})
    saiu_para_entrega = await pedidos.count_documents({"status": "saiu_para_entrega"})
    concluidos = await pedidos.count_documents({"status": "concluido"})
    total = await pedidos.count_documents({})
    
    return {
        "pendentes": pendentes,
        "em_preparacao": em_preparacao,
        "saiu_para_entrega": saiu_para_entrega,
        "concluidos": concluidos,
        "total": total
    }