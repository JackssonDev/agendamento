from django.contrib import admin
from .models import Pet, PerfilUsuario, Servico, Agendamento

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'dono', 'idade']
    list_filter = ['tipo', 'data_cadastro']
    search_fields = ['nome', 'raca', 'dono__username']

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'cpf', 'telefone', 'data_nascimento']
    search_fields = ['usuario__username', 'usuario__email', 'cpf']

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome']
    list_editable = ['preco', 'ativo']

@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ['nome_pet', 'data', 'horario_inicio', 'status', 'nome_tutor', 'valor_total']
    list_filter = ['status', 'data', 'servicos', 'tipo_pet', 'forma_pagamento']
    search_fields = ['nome_pet', 'nome_tutor', 'rua', 'bairro', 'cidade']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    filter_horizontal = ['servicos']