Backend — KaizerHaus (FastAPI + Uvicorn + MongoDB)

API do restaurante KaizerHaus, construída com FastAPI e MongoDB.
A documentação interativa da API pode ser acessada em /docs (Swagger) e /redoc.

✅ Pré-requisitos

Python 3.10 ou superior

Windows: baixe em https://www.python.org/downloads/
 e marque “Add Python to PATH” durante a instalação.

macOS: use o comando brew install python ou baixe diretamente do site.

Linux (Debian/Ubuntu): use sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip.

Git

Baixe e instale pelo site oficial https://git-scm.com/downloads
.

MongoDB Atlas

Banco de dados na nuvem gratuito. Será usado para armazenar os dados da aplicação.

📦 Clonar o projeto

Abra o terminal e digite:
git clone https://github.com/<seu-usuario>/<seu-repo-backend>.git
Substitua <seu-usuario> e <seu-repo-backend> pelo nome do seu repositório.

Acesse a pasta do projeto:
cd <seu-repo-backend>

🧪 Criar e ativar o ambiente virtual

No Windows (PowerShell):

Crie o ambiente: python -m venv .venv

Ative o ambiente: .\.venv\Scripts\Activate.ps1

Se aparecer erro de permissão, abra o PowerShell como administrador e execute:
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

No macOS ou Linux:

Crie o ambiente: python3 -m venv .venv

Ative o ambiente: source .venv/bin/activate

📥 Instalar as dependências

Atualize o pip com pip install --upgrade pip.

Instale os pacotes do projeto com pip install -r requirements.txt.

Caso algum pacote falte, instale manualmente com:
pip install uvicorn[standard] fastapi python-dotenv pymongo

🗄️ Criar conta e cluster no MongoDB Atlas

Acesse https://www.mongodb.com/cloud/atlas
 e crie uma conta (ou entre com Google/GitHub).

Crie um projeto novo (Project) chamado, por exemplo, “kaizerhaus”.

Clique em “Build a Database” e escolha a opção gratuita “Free (M0)”.

Selecione a região mais próxima (por exemplo, AWS sa-east-1) e crie o cluster.

Vá em “Database Access” e clique em “Add New Database User”.

Escolha autenticação por senha.

Defina um nome de usuário (exemplo: appuser) e uma senha forte.

Nas permissões, selecione “Read and write to any database”.

Vá em “Network Access” e adicione o IP 0.0.0.0/0 para permitir acesso de qualquer lugar durante o desenvolvimento.

Em “Database”, clique em “Connect” e depois em “Connect your application”.

Copie a connection string que se parece com:
mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority

Substitua <username> pelo nome de usuário que você criou.

Substitua <password> pela sua senha.

O campo <cluster> já virá preenchido automaticamente pelo Atlas (exemplo: cluster0.xxxxxxx).

🧭 Testar a conexão no MongoDB Compass (opcional)

Baixe o MongoDB Compass em https://www.mongodb.com/products/compass
.

Abra o Compass e clique em “New Connection”.

Cole a connection string copiada do Atlas.

Substitua <username> e <password> pelos seus dados reais e clique em “Connect”.

O banco “kaizerhaus” pode ser criado manualmente ou será criado automaticamente ao rodar a API.

🔐 Configurar o arquivo .env

Crie um arquivo chamado .env na raiz do projeto.

Adicione as variáveis a seguir (trocando os valores entre <> pelos seus dados reais):

MONGODB_URI=mongodb+srv://appuser:SUA_SENHA@cluster0.xxxxxx.mongodb.net/?retryWrites=true&w=majority

MONGODB_DB=kaizerhaus

JWT_SECRET=troque-por-um-segredo-bem-grande-e-aleatorio

ACCESS_TOKEN_EXPIRE_MINUTES=60

CORS_ORIGINS=http://localhost:5173,https://seu-dominio.com

Para gerar um segredo JWT seguro, você pode usar o comando Python:

Abra o terminal Python e digite:
import secrets; print(secrets.token_urlsafe(64))

▶️ Rodar o servidor localmente

Certifique-se de que o ambiente virtual está ativado e o .env configurado.

Execute o comando:
python -m uvicorn main:app --reload --port 8001

Acesse a API pelo navegador em http://localhost:8001
.

Acesse a documentação Swagger em http://localhost:8001/docs
 e Redoc em http://localhost:8001/redoc
.

Se o arquivo principal estiver em outra pasta (por exemplo, app/main.py), use:
python -m uvicorn app.main:app --reload --port 8001

🧪 Teste rápido

Para testar rapidamente, acesse no navegador o endereço http://localhost:8001/docs
.
Se o projeto tiver um endpoint de saúde (health check), você também pode testar em http://localhost:8001/health
.

⚙️ Dicas e solução de problemas

Se aparecer o erro “No module named uvicorn”, instale com pip install uvicorn[standard].

Se o MongoDB não conectar, verifique:

Se a variável MONGODB_URI está correta no .env.

Se o IP 0.0.0.0/0 está liberado em Network Access.

Se o usuário e senha estão certos em Database Access.

Se o frontend der erro de CORS, adicione o domínio correto em CORS_ORIGINS.

Se o ambiente virtual não ativar no Windows, abra o PowerShell como administrador e rode:
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser.

🗂️ Arquivos recomendados no .gitignore

Adicione estas linhas no seu arquivo .gitignore:

.venv/

pycache/

*.pyc

.env

.idea/

.vscode/

📚 Stack utilizada

FastAPI

Uvicorn (ASGI server)

MongoDB Atlas (banco na nuvem)

python-dotenv (para carregar o .env)

pydantic (validação de dados)

🔒 Boas práticas

Nunca envie o arquivo .env para o GitHub.

Use senhas fortes e altere o JWT_SECRET regularmente.

Sempre rode a API com o ambiente virtual ativo.

Mantenha as dependências atualizadas com pip install -U -r requirements.txt.