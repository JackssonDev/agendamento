# ⚙️ Setup e Configuração do Ambiente

Este guia detalha como configurar e rodar o projeto localmente.

## 1. Pré-requisitos

Certifique-se de ter instalado em seu ambiente:
* **Python 3.10+**
* **Git**
* **Docker** e **Docker Compose** (Opcional, mas altamente recomendado para desenvolvimento com PostgreSQL).

## 2. Instalação Local

Siga estes passos para configurar e iniciar o projeto:

### 2.1. Clonagem e Ambiente Virtual

```bash
# Clone o repositório
git clone [https://github.com/JackssonDev/agendamento](https://github.com/JackssonDev/agendamento)
cd agendamento

# Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate # Use 'venv\Scripts\activate' no Windows

# Instale as dependências
pip install -r requirements.txt
```

### 2.2. Configuração de Variáveis de Ambiente
Crie um arquivo chamado .env na raiz do projeto. Utilize a biblioteca python-decouple para gerenciar as configurações.
```bash
# .env (Ambiente de Desenvolvimento)

# Segurança
SECRET_KEY='chave_local_de_desenvolvimento'
DEBUG=True
ALLOWED_HOSTS='127.0.0.1,localhost'

# Banco de Dados (SQLite)
# DATABASE_URL é opcional, pois o settings.py usa SQLite por padrão se vazio.
# DATABASE_URL=

# Configurações do Email (se aplicável)
EMAIL_HOST=
EMAIL_PORT=
```
### 2.3. Inicialização e Migrações
```bash
# Aplique as migrações (cria o banco de dados SQLite)
python manage.py migrate

# Coleta de arquivos estáticos (útil para desenvolvimento)
python manage.py collectstatic --noinput

# Crie um superusuário para acessar a área administrativa (Jazzmin)
python manage.py createsuperuser
```
### 2.4. Iniciando o Servidor
```bash
python manage.py runserver
```
Acesse o projeto em http://127.0.0.1:8000/
