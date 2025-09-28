#!/usr/bin/env bash
# Cria o superusuário (se ainda não existir) usando as variáveis de ambiente
python manage.py createsuperuser --noinput || true

# Inicia o servidor Gunicorn (o que antes estava no Procfile)
exec gunicorn agendamento.wsgi:application --log-file -