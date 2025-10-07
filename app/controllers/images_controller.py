from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
import os
import mimetypes
from datetime import datetime, timedelta

router = APIRouter()

# Diretório das imagens
IMAGES_DIR = "app/static"

@router.get("/images/{category}/{filename}")
async def get_optimized_image(category: str, filename: str, response: Response):
    """
    Serve imagens com headers otimizados para cache e performance
    """
    # Remove @ do início do filename se existir
    if filename.startswith("@"):
        filename = filename[1:]
    
    file_path = os.path.join(IMAGES_DIR, "produtos", category, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    
    # Configurar headers de cache (cache por 30 dias)
    response.headers["Cache-Control"] = "public, max-age=2592000"  # 30 dias
    response.headers["Expires"] = (datetime.utcnow() + timedelta(days=30)).strftime("%a, %d %b %Y %H:%M:%S GMT")
    response.headers["Last-Modified"] = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    # Configurar content type baseado na extensão
    content_type, _ = mimetypes.guess_type(file_path)
    if content_type:
        response.headers["Content-Type"] = content_type
    
    # Configurar headers de performance
    response.headers["ETag"] = f'"{os.path.getmtime(file_path)}"'
    
    return FileResponse(file_path)

@router.get("/images/{category}/@{filename}")
async def get_image_with_at(category: str, filename: str, response: Response):
    """
    Serve imagens com @ no início do nome (formato especial)
    """
    file_path = os.path.join(IMAGES_DIR, "produtos", category, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    
    # Configurar headers de cache (cache por 30 dias)
    response.headers["Cache-Control"] = "public, max-age=2592000"  # 30 dias
    response.headers["Expires"] = (datetime.utcnow() + timedelta(days=30)).strftime("%a, %d %b %Y %H:%M:%S GMT")
    response.headers["Last-Modified"] = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    # Configurar content type baseado na extensão
    content_type, _ = mimetypes.guess_type(file_path)
    if content_type:
        response.headers["Content-Type"] = content_type
    
    # Configurar headers de performance
    response.headers["ETag"] = f'"{os.path.getmtime(file_path)}"'
    
    return FileResponse(file_path)

@router.get("/images/{category}")
async def list_category_images(category: str):
    """
    Lista todas as imagens de uma categoria específica
    """
    category_path = os.path.join(IMAGES_DIR, "produtos", category)
    
    if not os.path.exists(category_path):
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    images = []
    for filename in os.listdir(category_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif')):
            images.append({
                "filename": filename,
                "url": f"/images/{category}/{filename}",
                "size": os.path.getsize(os.path.join(category_path, filename))
            })
    
    return {"category": category, "images": images}

@router.get("/images")
async def list_all_images():
    """
    Lista todas as imagens organizadas por categoria
    """
    produtos_path = os.path.join(IMAGES_DIR, "produtos")
    
    if not os.path.exists(produtos_path):
        return {"categories": []}
    
    categories = {}
    
    for category in os.listdir(produtos_path):
        category_path = os.path.join(produtos_path, category)
        if os.path.isdir(category_path):
            images = []
            for filename in os.listdir(category_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif')):
                    images.append({
                        "filename": filename,
                        "url": f"/images/{category}/{filename}",
                        "size": os.path.getsize(os.path.join(category_path, filename))
                    })
            categories[category] = images
    
    return {"categories": categories}

@router.get("/images/preload/{category}")
async def preload_category_images(category: str):
    """
    Retorna URLs de todas as imagens de uma categoria para preload no frontend
    """
    category_path = os.path.join(IMAGES_DIR, "produtos", category)
    
    if not os.path.exists(category_path):
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    images = []
    for filename in os.listdir(category_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif')):
            images.append(f"/images/{category}/{filename}")
    
    return {
        "category": category,
        "preload_urls": images,
        "count": len(images)
    }
