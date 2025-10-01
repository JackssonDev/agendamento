from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, time, timedelta

# Importa os modelos e a camada de serviços
from .models import Servico, Agendamento
from .services import (
    calcular_duracao_total, 
    gerar_horarios_possiveis, 
    checar_conflito_agendamento
)

# Define uma data de teste fixa
DATA_TESTE = date(2025, 10, 10)
DATA_FUTURA = date(2025, 10, 11)

# ==============================================================================
# 1. Testes da Lógica de Serviços
# ==============================================================================

class AgendamentoServiceTest(TestCase):
    """Testa as funções auxiliares de cálculo e geração de horários."""
    
    def setUp(self):
        # Cria serviços de teste que serão usados para calcular a duração
        self.servico_30 = Servico.objects.create(nome="Banho", duracao_minutos=30, preco=50.00)
        self.servico_60 = Servico.objects.create(nome="Tosa Completa", duracao_minutos=60, preco=120.00)
        self.servico_15 = Servico.objects.create(nome="Curativo", duracao_minutos=15, preco=30.00)

    def test_calcular_duracao_total_simples(self):
        """Deve calcular a duração de um único serviço."""
        servicos_ids = [str(self.servico_30.id)]
        duracao = calcular_duracao_total(servicos_ids)
        self.assertEqual(duracao, 30)

    def test_calcular_duracao_total_multiplo(self):
        """Deve somar a duração de múltiplos serviços."""
        servicos_ids = [str(self.servico_30.id), str(self.servico_60.id), str(self.servico_15.id)]
        # 30 + 60 + 15 = 105
        duracao = calcular_duracao_total(servicos_ids)
        self.assertEqual(duracao, 105)

    def test_calcular_duracao_minima(self):
        """Deve retornar a duração mínima de 15 minutos, mesmo que a soma seja 0."""
        # Supondo uma lista vazia ou serviços inexistentes
        duracao = calcular_duracao_total([])
        self.assertEqual(duracao, 15)

    def test_gerar_horarios_possiveis_limites(self):
        """Deve gerar horários corretamente, começando em 08:00 e terminando antes de 18:00."""
        horarios = gerar_horarios_possiveis(intervalo_minutos=30)
        
        # O primeiro horário deve ser 08:00
        self.assertEqual(horarios[0], "08:00")
        
        # O último horário deve ser 17:30 (pois 18:00 é o final)
        self.assertEqual(horarios[-1], "17:30")

    def test_gerar_horarios_possiveis_pular_almoco(self):
        """Deve pular o intervalo de almoço (12:00 a 14:00)."""
        horarios = gerar_horarios_possiveis(intervalo_minutos=30)
        
        # 11:30 deve estar presente
        self.assertIn("11:30", horarios)
        
        # 12:00, 12:30, 13:00, 13:30 NÃO devem estar presentes
        self.assertNotIn("12:00", horarios)
        self.assertNotIn("12:30", horarios)
        self.assertNotIn("13:00", horarios)
        self.assertNotIn("13:30", horarios)
        
        # 14:00 deve ser o próximo horário
        self.assertIn("14:00", horarios)

# ==============================================================================
# 2. Testes da Lógica de Conflito de Agendamento
# ==============================================================================

class ConflitoAgendamentoTest(TestCase):
    """Testa a função checar_conflito_agendamento para garantir que detecta sobreposições."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='tutor', password='password')
        self.servico_60 = Servico.objects.create(id=10, nome="Tosa 1h", duracao_minutos=60, preco=100.00)
        self.servico_30 = Servico.objects.create(id=20, nome="Banho 30m", duracao_minutos=30, preco=50.00)
        
        # Cria um agendamento fixo de 10:00 (60 minutos) que vai até 11:00
        Agendamento.objects.create(
            usuario=self.user,
            nome_tutor="Tutor Teste",
            nome_pet="Buddy",
            tipo_pet="cachorro",
            data=DATA_TESTE,
            horario_inicio=time(10, 0),
            duracao_total_minutos=60,
            cep='00000-000', rua='Rua', numero='1', bairro='Bairro', cidade='Cidade', estado='RS',
            forma_pagamento='pix', valor_total=100.00,
            status='agendado',
        ).servicos.add(self.servico_60)
        
        # Este é o agendamento de referência: [10:00 -> 11:00]
        self.agendamento_referencia = Agendamento.objects.get(horario_inicio=time(10, 0))

    # --- Testes de Conflito Total ---

    def test_conflito_total_sobreposicao_cheio(self):
        """Teste 1: Novo agendamento [10:15 -> 10:45] deve CONFLITAR com [10:00 -> 11:00]."""
        # Tentativa de Agendar: [10:15 - 30 minutos]
        livre = checar_conflito_agendamento(
            DATA_TESTE, 
            "10:15", # Início
            30       # Duração
        )
        self.assertFalse(livre, "Deve falhar: conflito total dentro do horário existente.")

    # --- Testes de Conflito nos Limites (Edge Cases) ---

    def test_conflito_total_borda_inicio(self):
        """Teste 2: Novo agendamento [09:30 -> 10:30] deve CONFLITAR."""
        # Início antes, fim invadindo
        livre = checar_conflito_agendamento(DATA_TESTE, "09:30", 60)
        self.assertFalse(livre, "Deve falhar: o agendamento inicia antes e invade o horário.")

    def test_conflito_total_borda_fim(self):
        """Teste 3: Novo agendamento [10:30 -> 11:30] deve CONFLITAR."""
        # Início invadindo, fim depois
        livre = checar_conflito_agendamento(DATA_TESTE, "10:30", 60)
        self.assertFalse(livre, "Deve falhar: o agendamento inicia invadindo e termina depois.")

    # --- Testes de Slots Livres ---

    def test_nao_conflito_imediatamente_antes(self):
        """Teste 4: Novo agendamento [09:00 -> 10:00] DEVE ser LIVRE."""
        # Horário: [09:00 -> 10:00] - Toca na borda de início, mas não sobrepõe
        livre = checar_conflito_agendamento(DATA_TESTE, "09:00", 60)
        self.assertTrue(livre, "Deve ser livre: agendamento termina exatamente quando o outro começa.")

    def test_nao_conflito_imediatamente_depois(self):
        """Teste 5: Novo agendamento [11:00 -> 12:00] DEVE ser LIVRE."""
        # Horário: [11:00 -> 12:00] - Toca na borda de fim, mas não sobrepõe
        livre = checar_conflito_agendamento(DATA_TESTE, "11:00", 60)
        self.assertTrue(livre, "Deve ser livre: agendamento começa exatamente quando o outro termina.")
        
    def test_nao_conflito_outro_dia(self):
        """Teste 6: Novo agendamento em outro dia DEVE ser LIVRE."""
        # Horário: [10:30 -> 11:30] em outra data
        livre = checar_conflito_agendamento(DATA_FUTURA, "10:30", 60)
        self.assertTrue(livre, "Deve ser livre: a data é diferente.")

    # --- Teste de Edição (Excluindo a si mesmo) ---
    
    def test_conflito_edicao_com_si_mesmo(self):
        """Teste 7: Editar o próprio agendamento não deve causar conflito."""
        # Tenta checar o agendamento [10:00 -> 11:00] passando seu próprio ID
        livre = checar_conflito_agendamento(
            DATA_TESTE, 
            "10:00", # Horário inicial do próprio agendamento
            60,      # Duração do próprio agendamento
            agendamento_id=self.agendamento_referencia.id
        )
        self.assertTrue(livre, "Deve ser livre: o agendamento está excluindo a si mesmo da checagem.")