from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import shutil
from datetime import datetime

router = APIRouter()

# Diretório onde as imagens serão salvas
UPLOAD_DIR = "static/images"

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    Faz upload de uma imagem
    """
    # Verificar se é uma imagem
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Apenas imagens são permitidas")
    
    # Criar diretório se não existir
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Gerar nome único para o arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Salvar arquivo
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Retornar URL da imagem
    image_url = f"/static/images/{filename}"
    return {
        "message": "Imagem enviada com sucesso!",
        "filename": filename,
        "url": image_url
    }

@router.get("/images/{filename}")
async def get_image(filename: str):
    """
    Retorna uma imagem específica
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    
    return FileResponse(file_path)

@router.get("/images")
async def list_images():
    """
    Lista todas as imagens disponíveis
    """
    if not os.path.exists(UPLOAD_DIR):
        return {"images": []}
    
    images = []
    for filename in os.listdir(UPLOAD_DIR):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            images.append({
                "filename": filename,
                "url": f"/static/images/{filename}"
            })
    
    return {"images": images}
