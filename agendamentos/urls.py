# agendamentos/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Mapeia a URL 'home' para a função 'home' na views.py
    path('', views.home, name='home'),
]
