# Dockerfile

# 1. Imagem Base: Usamos uma imagem Python mais recente e estável
FROM python:3.10-slim

# 2. Configurações de Ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE agendamento.settings # Garante que as configurações corretas sejam usadas

# 3. Defina o diretório de trabalho dentro do container
WORKDIR /app

# 4. Instale dependências do sistema necessárias para pacotes Python (ex: psycopg2)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    # Limpa o cache após a instalação
    && rm -rf /var/lib/apt/lists/*

# 5. Copie e instale dependências do Python
# Copiar o requirements.txt primeiro aproveita o cache do Docker
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 6. Copie todo o código do projeto para o container
COPY . /app/

# 7. Coleta de arquivos estáticos (para produção, usando WhiteNoise)
# Este comando é executado durante o build para preparar os estáticos
RUN python manage.py collectstatic --noinput

# 8. Comando de Início (Define o que rodar quando o container iniciar)
# Este comando deve ser o mesmo usado no seu Procfile para produção
CMD gunicorn agendamento.wsgi:application --bind 0.0.0.0:$PORT