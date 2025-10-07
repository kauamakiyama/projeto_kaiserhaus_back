const fs = require('fs');
const path = require('path');

console.log('🧹 Limpando arquivos temporários de conversão...\n');

// Arquivos/pastas para remover
const itemsToRemove = [
    './imagens-temporarias',
    './converted_images.json',
    './convert_images_to_base64.js',
    './cleanup_conversion.js',
    './imageUtils.js',
    './useImages.js',
    './IMAGENS_BASE64.md'
];

let removedCount = 0;

itemsToRemove.forEach(item => {
    try {
        if (fs.existsSync(item)) {
            const stats = fs.statSync(item);
            
            if (stats.isDirectory()) {
                // Remover diretório e todo conteúdo
                fs.rmSync(item, { recursive: true, force: true });
                console.log(`🗂️  Pasta removida: ${item}`);
            } else {
                // Remover arquivo
                fs.unlinkSync(item);
                console.log(`📄 Arquivo removido: ${item}`);
            }
            removedCount++;
        } else {
            console.log(`⚠️  Não encontrado: ${item}`);
        }
    } catch (error) {
        console.error(`❌ Erro ao remover ${item}:`, error.message);
    }
});

console.log(`\n✅ Limpeza concluída! ${removedCount} itens removidos.`);
console.log('🎉 Seu projeto está limpo e pronto para produção!');

