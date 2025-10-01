# agendamentos/services.py

from datetime import datetime, timedelta, date, time
from django.utils import timezone
from .models import Servico, Agendamento

# ==============================================================================
# Funções de Auxílio para Cálculo de Duração e Slot
# ==============================================================================

def calcular_duracao_total(servicos_ids: list) -> int:
    """Calcula a duração total em minutos somando a duração de todos os serviços."""
    
    # Converte as IDs (strings) para inteiros
    servicos_ids = [int(sid) for sid in servicos_ids if sid]
    
    # Busca e soma a duração_minutos dos serviços
    duracao_soma = sum(
        Servico.objects.filter(id=sid).values_list('duracao_minutos', flat=True).first() or 0 
        for sid in servicos_ids
    )
    
    # Retorna a duração mínima de 15 minutos (ou a soma)
    return max(15, duracao_soma)

def gerar_horarios_possiveis(intervalo_minutos=15) -> list:
    """
    Gera uma lista de strings de horário ('HH:MM') em um intervalo de 15 minutos, 
    excluindo o horário de almoço.
    """
    horarios = []
    # Define o horário de início (8:00) e fim (18:00) do dia de trabalho
    inicio = datetime.strptime("08:00", "%H:%M")
    fim = datetime.strptime("18:00", "%H:%M")
    
    # Intervalo de almoço
    almoco_inicio = datetime.strptime("12:00", "%H:%M")
    almoco_fim = datetime.strptime("14:00", "%H:%M")

    current = inicio
    while current < fim:
        # Pula o intervalo de almoço
        if current >= almoco_inicio and current < almoco_fim:
            current += timedelta(minutes=intervalo_minutos)
            continue
            
        horarios.append(current.strftime("%H:%M"))
        current += timedelta(minutes=intervalo_minutos)
        
    return horarios

def checar_conflito_agendamento(
    data_agendamento: date, 
    horario_inicio_str: str, 
    duracao_minutos: int, 
    agendamento_id: int = None
) -> bool:
    """
    Verifica se o intervalo completo (inicio + duração) está livre,
    considerando agendamentos existentes. Retorna True se estiver LIVRE.
    """
    
    # Converte horário de início (string 'HH:MM') para objeto datetime completo
    horario_inicio_dt = datetime.strptime(horario_inicio_str, '%H:%M')
    horario_inicio_completo = datetime.combine(data_agendamento, horario_inicio_dt.time())
    
    # Calcular o horário de fim do novo agendamento
    horario_fim_agendamento = horario_inicio_completo + timedelta(minutes=duracao_minutos)
    
    # 1. Buscar agendamentos existentes no mesmo dia (excluindo o que está sendo editado)
    agendamentos_dia = Agendamento.objects.filter(
        data=data_agendamento,
        status__in=['agendado', 'confirmado']
    )
    if agendamento_id:
        agendamentos_dia = agendamentos_dia.exclude(id=agendamento_id)
    
    # 2. Checar conflito com cada agendamento existente
    for agendamento in agendamentos_dia:
        
        # Início do agendamento existente (TimeField + Data)
        agendamento_inicio = datetime.combine(data_agendamento, agendamento.horario_inicio)
        
        # Fim do agendamento existente (Início + Duração)
        agendamento_fim = agendamento_inicio + timedelta(minutes=agendamento.duracao_total_minutos)

        # Lógica de Conflito
        conflito = (
            (horario_inicio_completo < agendamento_fim) and 
            (horario_fim_agendamento > agendamento_inicio)
        )

        if conflito:
            return False  # Slot OCUPADO
            
    return True # Slot LIVRE