# 🖼️ Sistema de Imagens Base64

## Como funciona

Agora as imagens são salvas diretamente no banco de dados como strings base64, ao invés de arquivos estáticos.

## Endpoints disponíveis

### 1. Upload e validação de imagem
```
POST /images/upload-image
```

**Body:**
```json
{
  "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD...",
  "filename": "produto.jpg" // opcional
}
```

**Resposta:**
```json
{
  "success": true,
  "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD...",
  "message": "Imagem processada com sucesso"
}
```

### 2. Apenas validar imagem
```
POST /images/validate-image
```

**Body:**
```json
{
  "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD..."
}
```

## Como criar um produto com imagem

### 1. Converter imagem para base64 (no frontend)
```javascript
// JavaScript exemplo
const fileInput = document.getElementById('image-input');
const file = fileInput.files[0];

const reader = new FileReader();
reader.onload = function(e) {
    const base64Image = e.target.result; // data:image/jpeg;base64,/9j/4AAQ...
    
    // Agora usar no produto
    createProduct({
        titulo: "Prato Especial",
        descricao: "Descrição do prato",
        preco: 29.90,
        imagem: base64Image, // <- Imagem base64
        categoria_id: "categoria_id_aqui",
        quantidade: 10
    });
};
reader.readAsDataURL(file);
```

### 2. Criar produto via API
```
POST /produtos/
```

**Body:**
```json
{
  "titulo": "Filé à Parmegiana",
  "descricao": "Delicioso filé empanado com molho de tomate e queijo",
  "preco": 32.90,
  "imagem": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD...",
  "categoria_id": "60f7b3b3b3b3b3b3b3b3b3b3",
  "quantidade": 15
}
```

## Vantagens do sistema base64

✅ **Simplicidade**: Não precisa gerenciar arquivos no servidor  
✅ **Portabilidade**: Imagem fica junto com os dados do produto  
✅ **Backup**: Imagens são incluídas automaticamente no backup do banco  
✅ **Deploy**: Não precisa configurar servidor de arquivos estáticos  

## Limitações

⚠️ **Tamanho**: Imagens grandes aumentam o tamanho do banco  
⚠️ **Performance**: Imagens grandes podem tornar as consultas mais lentas  
⚠️ **Cache**: Não há cache automático como arquivos estáticos  

## Recomendações

- **Tamanho máximo**: 5MB por imagem
- **Formato recomendado**: JPEG ou WebP para melhor compressão
- **Redimensionar**: Redimensione imagens para no máximo 800x600px antes de converter para base64

## Exemplo completo (Frontend)

```javascript
// Função para converter e enviar produto
async function createProductWithImage() {
    const fileInput = document.getElementById('image-input');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Selecione uma imagem');
        return;
    }
    
    // Converter para base64
    const base64Image = await new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.readAsDataURL(file);
    });
    
    // Criar produto
    const productData = {
        titulo: document.getElementById('titulo').value,
        descricao: document.getElementById('descricao').value,
        preco: parseFloat(document.getElementById('preco').value),
        imagem: base64Image,
        categoria_id: document.getElementById('categoria').value,
        quantidade: parseInt(document.getElementById('quantidade').value)
    };
    
    // Enviar para API
    try {
        const response = await fetch('/produtos/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(productData)
        });
        
        if (response.ok) {
            alert('Produto criado com sucesso!');
        } else {
            alert('Erro ao criar produto');
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao criar produto');
    }
}
```

