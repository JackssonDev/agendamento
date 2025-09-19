# agendamentos/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('meus-agendamentos/', views.meus_agendamentos, name='meus_agendamentos'),
    path('meus-pets/', views.meus_pets, name='meus_pets'),
    path('cadastrar-pet/', views.cadastrar_pet, name='cadastrar_pet'),
    path('editar-pet/<int:pet_id>/', views.editar_pet, name='editar_pet'),
    path('excluir-pet/<int:pet_id>/', views.excluir_pet, name='excluir_pet'),
    path('dados-pessoais/', views.dados_pessoais, name='dados_pessoais'),
    path('agendar-servico/', views.agendar_servico, name='agendar_servico'),
    path('verificar-horarios/', views.verificar_horarios_disponiveis, name='verificar_horarios'),
    path('consultar-cep/', views.consultar_cep, name='consultar_cep'),
]