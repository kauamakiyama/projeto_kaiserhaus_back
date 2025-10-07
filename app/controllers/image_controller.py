from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
from typing import Optional

router = APIRouter()

class ImageUploadRequest(BaseModel):
    image_base64: str
    filename: Optional[str] = None

class ImageUploadResponse(BaseModel):
    success: bool
    image_data: str
    message: str

@router.post("/upload-image", response_model=ImageUploadResponse)
async def upload_image(request: ImageUploadRequest):
    """
    Converte e valida imagem base64 para ser salva no banco de dados
    """
    try:
        # Remove o prefixo data:image/...;base64, se existir
        if request.image_base64.startswith("data:image"):
            # Extrai apenas a parte base64
            image_data = request.image_base64.split(",")[1]
        else:
            image_data = request.image_base64
        
        # Valida se é base64 válido
        try:
            decoded = base64.b64decode(image_data)
            # Testa se consegue decodificar (validação básica)
            if len(decoded) == 0:
                raise HTTPException(status_code=400, detail="Imagem base64 inválida")
        except Exception:
            raise HTTPException(status_code=400, detail="Formato base64 inválido")
        
        # Verifica tamanho da imagem (máximo 5MB)
        if len(decoded) > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(status_code=400, detail="Imagem muito grande. Máximo 5MB")
        
        return ImageUploadResponse(
            success=True,
            image_data=request.image_base64,
            message="Imagem processada com sucesso"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}")

@router.post("/validate-image")
async def validate_image(request: ImageUploadRequest):
    """
    Apenas valida se a imagem base64 é válida, sem retornar os dados
    """
    try:
        # Remove o prefixo data:image/...;base64, se existir
        if request.image_base64.startswith("data:image"):
            image_data = request.image_base64.split(",")[1]
        else:
            image_data = request.image_base64
        
        # Valida base64
        try:
            decoded = base64.b64decode(image_data)
            if len(decoded) == 0:
                raise HTTPException(status_code=400, detail="Imagem base64 inválida")
        except Exception:
            raise HTTPException(status_code=400, detail="Formato base64 inválido")
        
        # Verifica tamanho
        if len(decoded) > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(status_code=400, detail="Imagem muito grande. Máximo 5MB")
        
        return {"success": True, "message": "Imagem válida", "size_bytes": len(decoded)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao validar imagem: {str(e)}")

