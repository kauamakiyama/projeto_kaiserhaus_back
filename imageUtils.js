// Utilitário para usar imagens base64 no frontend
import convertedImages from './converted_images.json';

class ImageManager {
    constructor() {
        this.images = convertedImages;
    }
    
    /**
     * Busca uma imagem por categoria e nome do arquivo
     * @param {string} category - Categoria (ex: 'pratos', 'entradas', 'bebidas')
     * @param {string} filename - Nome do arquivo (ex: 'file-parmegiana.jpg')
     * @returns {string|null} - Base64 da imagem ou null se não encontrada
     */
    getImage(category, filename) {
        try {
            if (this.images[category] && this.images[category][filename]) {
                return this.images[category][filename].base64;
            }
            console.warn(`Imagem não encontrada: ${category}/${filename}`);
            return null;
        } catch (error) {
            console.error('Erro ao buscar imagem:', error);
            return null;
        }
    }
    
    /**
     * Lista todas as imagens de uma categoria
     * @param {string} category - Categoria
     * @returns {Array} - Array com informações das imagens
     */
    getImagesByCategory(category) {
        if (this.images[category]) {
            return Object.values(this.images[category]);
        }
        return [];
    }
    
    /**
     * Busca uma imagem por nome (em qualquer categoria)
     * @param {string} filename - Nome do arquivo
     * @returns {Object|null} - Objeto com categoria e base64 ou null
     */
    findImage(filename) {
        for (const [category, images] of Object.entries(this.images)) {
            if (images[filename]) {
                return {
                    category,
                    filename,
                    ...images[filename]
                };
            }
        }
        return null;
    }
    
    /**
     * Retorna todas as categorias disponíveis
     * @returns {Array} - Array com nomes das categorias
     */
    getCategories() {
        return Object.keys(this.images);
    }
    
    /**
     * Converte arquivo de imagem para base64 (para uploads dinâmicos)
     * @param {File} file - Arquivo de imagem
     * @returns {Promise<string>} - Promise com base64 da imagem
     */
    static async fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }
    
    /**
     * Redimensiona e comprime uma imagem base64
     * @param {string} base64 - Base64 da imagem
     * @param {number} maxWidth - Largura máxima
     * @param {number} maxHeight - Altura máxima
     * @param {number} quality - Qualidade (0-1)
     * @returns {Promise<string>} - Promise com base64 otimizado
     */
    static async optimizeBase64Image(base64, maxWidth = 800, maxHeight = 600, quality = 0.8) {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                
                // Calcular novas dimensões mantendo proporção
                let { width, height } = img;
                if (width > maxWidth || height > maxHeight) {
                    const ratio = Math.min(maxWidth / width, maxHeight / height);
                    width *= ratio;
                    height *= ratio;
                }
                
                canvas.width = width;
                canvas.height = height;
                
                // Desenhar imagem redimensionada
                ctx.drawImage(img, 0, 0, width, height);
                
                // Converter para base64 otimizado
                const optimizedBase64 = canvas.toDataURL('image/jpeg', quality);
                resolve(optimizedBase64);
            };
            img.src = base64;
        });
    }
}

// Instância global
export const imageManager = new ImageManager();

// Exemplos de uso:
export const examples = {
    // Buscar imagem específica
    getParmegianaImage: () => imageManager.getImage('pratos', 'file-parmegiana.jpg'),
    
    // Listar todas as imagens de pratos
    getAllPratosImages: () => imageManager.getImagesByCategory('pratos'),
    
    // Buscar imagem por nome
    findSaladImage: () => imageManager.findImage('salada-de-batata-alema.png'),
    
    // Converter arquivo para base64
    convertFile: async (file) => await ImageManager.fileToBase64(file),
    
    // Otimizar imagem
    optimizeImage: async (base64) => await ImageManager.optimizeBase64Image(base64, 800, 600, 0.8)
};

export default imageManager;

