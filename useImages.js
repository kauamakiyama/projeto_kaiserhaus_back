import { useState, useEffect } from 'react';
import { imageManager } from './imageUtils';

/**
 * Hook personalizado para gerenciar imagens base64
 */
export const useImages = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    /**
     * Busca uma imagem específica
     */
    const getImage = (category, filename) => {
        try {
            setError(null);
            const base64 = imageManager.getImage(category, filename);
            return base64;
        } catch (err) {
            setError(err.message);
            return null;
        }
    };
    
    /**
     * Lista imagens de uma categoria
     */
    const getImagesByCategory = (category) => {
        try {
            setError(null);
            return imageManager.getImagesByCategory(category);
        } catch (err) {
            setError(err.message);
            return [];
        }
    };
    
    /**
     * Converte arquivo para base64
     */
    const convertFileToBase64 = async (file) => {
        setLoading(true);
        setError(null);
        
        try {
            const base64 = await imageManager.fileToBase64(file);
            setLoading(false);
            return base64;
        } catch (err) {
            setError(err.message);
            setLoading(false);
            return null;
        }
    };
    
    /**
     * Otimiza uma imagem base64
     */
    const optimizeImage = async (base64, maxWidth = 800, maxHeight = 600, quality = 0.8) => {
        setLoading(true);
        setError(null);
        
        try {
            const optimized = await imageManager.optimizeBase64Image(base64, maxWidth, maxHeight, quality);
            setLoading(false);
            return optimized;
        } catch (err) {
            setError(err.message);
            setLoading(false);
            return base64; // Retorna original em caso de erro
        }
    };
    
    return {
        getImage,
        getImagesByCategory,
        convertFileToBase64,
        optimizeImage,
        loading,
        error,
        categories: imageManager.getCategories()
    };
};

/**
 * Componente para exibir imagem base64
 */
export const Base64Image = ({ 
    category, 
    filename, 
    alt = '', 
    className = '', 
    style = {},
    fallback = null 
}) => {
    const { getImage, error } = useImages();
    const [imageSrc, setImageSrc] = useState(null);
    
    useEffect(() => {
        if (category && filename) {
            const base64 = getImage(category, filename);
            setImageSrc(base64);
        }
    }, [category, filename, getImage]);
    
    if (error) {
        return fallback || <div className="image-error">Erro ao carregar imagem</div>;
    }
    
    if (!imageSrc) {
        return fallback || <div className="image-loading">Carregando...</div>;
    }
    
    return (
        <img 
            src={imageSrc} 
            alt={alt} 
            className={className}
            style={style}
            onError={() => setImageSrc(fallback)}
        />
    );
};

/**
 * Componente para upload e preview de imagem
 */
export const ImageUploader = ({ 
    onImageSelect, 
    maxSize = 5 * 1024 * 1024, // 5MB
    acceptedTypes = ['image/jpeg', 'image/png', 'image/webp'],
    className = ''
}) => {
    const { convertFileToBase64, optimizeImage, loading, error } = useImages();
    const [preview, setPreview] = useState(null);
    
    const handleFileChange = async (event) => {
        const file = event.target.files[0];
        
        if (!file) return;
        
        // Validar tipo
        if (!acceptedTypes.includes(file.type)) {
            alert('Tipo de arquivo não suportado');
            return;
        }
        
        // Validar tamanho
        if (file.size > maxSize) {
            alert('Arquivo muito grande');
            return;
        }
        
        try {
            // Converter para base64
            const base64 = await convertFileToBase64(file);
            
            // Otimizar imagem
            const optimized = await optimizeImage(base64);
            
            setPreview(optimized);
            onImageSelect?.(optimized);
            
        } catch (err) {
            console.error('Erro ao processar imagem:', err);
        }
    };
    
    return (
        <div className={`image-uploader ${className}`}>
            <input 
                type="file" 
                accept={acceptedTypes.join(',')}
                onChange={handleFileChange}
                disabled={loading}
                className="file-input"
            />
            
            {loading && <div>Processando imagem...</div>}
            {error && <div className="error">Erro: {error}</div>}
            {preview && (
                <div className="preview">
                    <img src={preview} alt="Preview" style={{ maxWidth: '200px', maxHeight: '200px' }} />
                </div>
            )}
        </div>
    );
};

export default useImages;

