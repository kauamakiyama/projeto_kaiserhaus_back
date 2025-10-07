const fs = require('fs');
const path = require('path');

// Configurações
const IMAGES_DIR = './imagens-temporarias'; // Pasta temporária para conversão
const OUTPUT_FILE = './converted_images.json';

function convertImageToBase64(imagePath) {
    try {
        const imageBuffer = fs.readFileSync(imagePath);
        const base64String = imageBuffer.toString('base64');
        const mimeType = getMimeType(imagePath);
        return `data:${mimeType};base64,${base64String}`;
    } catch (error) {
        console.error(`Erro ao converter ${imagePath}:`, error.message);
        return null;
    }
}

function getMimeType(filePath) {
    const ext = path.extname(filePath).toLowerCase();
    const mimeTypes = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml'
    };
    return mimeTypes[ext] || 'image/jpeg';
}

function getAllImages(dir, baseDir = '') {
    let images = [];
    const items = fs.readdirSync(dir);
    
    for (const item of items) {
        const fullPath = path.join(dir, item);
        const relativePath = path.join(baseDir, item);
        
        if (fs.statSync(fullPath).isDirectory()) {
            images = images.concat(getAllImages(fullPath, relativePath));
        } else if (/\.(jpg|jpeg|png|gif|webp|svg)$/i.test(item)) {
            images.push({
                filename: item,
                path: fullPath,
                relativePath: relativePath,
                category: path.basename(dir) // Pasta pai como categoria
            });
        }
    }
    
    return images;
}

async function convertAllImages() {
    console.log('🖼️ Iniciando conversão de imagens para base64...\n');
    
    if (!fs.existsSync(IMAGES_DIR)) {
        console.error(`❌ Diretório não encontrado: ${IMAGES_DIR}`);
        console.log('📝 Ajuste a variável IMAGES_DIR no script para o caminho correto das suas imagens');
        return;
    }
    
    const images = getAllImages(IMAGES_DIR);
    const convertedImages = {};
    
    console.log(`📁 Encontradas ${images.length} imagens:`);
    images.forEach(img => console.log(`   - ${img.relativePath}`));
    console.log('');
    
    for (const image of images) {
        console.log(`🔄 Convertendo: ${image.relativePath}`);
        
        const base64 = convertImageToBase64(image.path);
        if (base64) {
            // Organizar por categoria
            if (!convertedImages[image.category]) {
                convertedImages[image.category] = {};
            }
            
            convertedImages[image.category][image.filename] = {
                base64: base64,
                filename: image.filename,
                path: image.relativePath,
                size: fs.statSync(image.path).size,
                mimeType: getMimeType(image.path)
            };
            
            console.log(`   ✅ Convertida (${Math.round(fs.statSync(image.path).size / 1024)}KB)`);
        } else {
            console.log(`   ❌ Falha na conversão`);
        }
    }
    
    // Salvar resultado
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(convertedImages, null, 2));
    
    console.log(`\n🎉 Conversão concluída!`);
    console.log(`📄 Resultado salvo em: ${OUTPUT_FILE}`);
    console.log(`📊 Total de imagens convertidas: ${Object.values(convertedImages).flat().length}`);
    
    // Mostrar estatísticas
    console.log('\n📈 Estatísticas por categoria:');
    Object.entries(convertedImages).forEach(([category, images]) => {
        const totalSize = Object.values(images).reduce((sum, img) => sum + img.size, 0);
        console.log(`   ${category}: ${Object.keys(images).length} imagens (${Math.round(totalSize / 1024)}KB)`);
    });
}

// Executar conversão
convertAllImages().catch(console.error);
