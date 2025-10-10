from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import CartaoIn, CartaoOut
from app.services import cartao_service
from app.dependencies_jwt import get_current_user_id_from_token
from typing import List

router = APIRouter()

@router.post("/", response_model=CartaoOut, status_code=status.HTTP_201_CREATED)
async def criar_cartao(
    cartao_data: CartaoIn,
    usuario_id: str = Depends(get_current_user_id_from_token)
):
    """
    Cria um novo cartão de crédito para o usuário
    
    - Valida dados do cartão (número, CVV, validade)
    - Criptografa dados sensíveis (número, CVV)
    - Detecta automaticamente a bandeira do cartão
    - Retorna apenas dados seguros (sem número completo)
    """
    try:
        return await cartao_service.criar_cartao(cartao_data, usuario_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.get("/", response_model=List[CartaoOut])
async def listar_cartoes(
    usuario_id: str = Depends(get_current_user_id_from_token)
):
    """
    Lista todos os cartões do usuário
    
    - Retorna apenas dados seguros (sem números completos)
    - Ordenado por data de criação (mais recente primeiro)
    """
    try:
        return await cartao_service.listar_cartoes_usuario(usuario_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.get("/{cartao_id}", response_model=CartaoOut)
async def obter_cartao(
    cartao_id: str,
    usuario_id: str = Depends(get_current_user_id_from_token)
):
    """
    Obtém um cartão específico
    
    - Apenas o dono pode ver o cartão
    - Retorna apenas dados seguros
    """
    try:
        cartao = await cartao_service.obter_cartao_por_id(cartao_id, usuario_id)
        if not cartao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cartão não encontrado"
            )
        return cartao
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )

@router.delete("/{cartao_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_cartao(
    cartao_id: str,
    usuario_id: str = Depends(get_current_user_id_from_token)
):
    """
    Deleta um cartão
    
    - Apenas o dono pode deletar o cartão
    - Remove permanentemente do banco de dados
    """
    try:
        sucesso = await cartao_service.deletar_cartao(cartao_id, usuario_id)
        if not sucesso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cartão não encontrado"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )
