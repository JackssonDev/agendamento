from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm, PetForm, DadosPessoaisForm, AgendamentoForm
from .models import Pet, PerfilUsuario, Servico, Agendamento
from django.http import JsonResponse
from datetime import date, datetime, time, timedelta
import json
import urllib.request
import json as json_lib
from django.utils import timezone # <--- Importado

# ==============================================================================
# Funções de Auxílio para Agendamento por Duração
# ==============================================================================

def calcular_duracao_total(servicos_ids):
    """Calcula a duração total em minutos somando a duração de todos os serviços."""
    
    # 1. Converte as IDs (strings) para inteiros
    servicos_ids = [int(sid) for sid in servicos_ids if sid]
    
    # 2. Busca e soma a duração_minutos dos serviços
    duracao_soma = sum(
        Servico.objects.filter(id=sid).values_list('duracao_minutos', flat=True).first() or 0 
        for sid in servicos_ids
    )
    
    # 3. Retorna a duração mínima de 15 minutos, caso a soma seja menor
    return max(15, duracao_soma)

def gerar_horarios_possiveis(intervalo_minutos=15):
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

def is_slot_livre(data_agendamento, horario_inicio_str, duracao_minutos, agendamento_id=None):
    """
    Verifica se o intervalo completo (inicio + duração) está livre,
    considerando agendamentos existentes.
    """
    
    # Converte horário de início (string 'HH:MM') para objeto datetime completo
    horario_inicio_dt = datetime.strptime(horario_inicio_str, '%H:%M')
    horario_inicio_completo = datetime.combine(data_agendamento, horario_inicio_dt.time())
    
    # Calcular o horário de fim do novo agendamento
    horario_fim_agendamento = horario_inicio_completo + timedelta(minutes=duracao_minutos)
    
    # 1. Buscar agendamentos existentes no mesmo dia (excluindo o que está sendo editado, se for o caso)
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

        # Lógica de Conflito: O novo agendamento se sobrepõe ao existente
        conflito = (
            (horario_inicio_completo < agendamento_fim) and 
            (horario_fim_agendamento > agendamento_inicio)
        )

        if conflito:
            return False  # Slot OCUPADO
            
    return True # Slot LIVRE

# ==============================================================================
# Views Existentes (com alterações na lógica de agendamento)
# ==============================================================================

def home(request):
    servicos = Servico.objects.filter(ativo=True)[:5]
    return render(request, 'agendamentos/home.html', {'servicos': servicos})

def cadastro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso! Bem-vindo(a)!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'agendamentos/cadastro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'agendamentos/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('home')

@login_required
def meus_agendamentos(request):
    # Alterado 'horario' para 'horario_inicio' na ordenação
    agendamentos = Agendamento.objects.filter(usuario=request.user).order_by('-data', 'horario_inicio') 
    return render(request, 'agendamentos/meus_agendamentos.html', {'agendamentos': agendamentos})

@login_required
def meus_pets(request):
    pets = Pet.objects.filter(dono=request.user)
    return render(request, 'agendamentos/meus_pets.html', {'pets': pets})

@login_required
def cadastrar_pet(request):
    if request.method == 'POST':
        form = PetForm(request.POST)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.dono = request.user
            pet.save()
            messages.success(request, f'Pet {pet.nome} cadastrado com sucesso!')
            return redirect('meus_pets')
    else:
        form = PetForm()
    
    return render(request, 'agendamentos/cadastrar_pet.html', {'form': form})

@login_required
def editar_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, dono=request.user)
    
    if request.method == 'POST':
        form = PetForm(request.POST, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, f'Pet {pet.nome} atualizado com sucesso!')
            return redirect('meus_pets')
    else:
        form = PetForm(instance=pet)
    
    return render(request, 'agendamentos/cadastrar_pet.html', {'form': form, 'pet': pet})

@login_required
def excluir_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, dono=request.user)
    if request.method == 'POST':
        pet.delete()
        messages.success(request, f'Pet {pet.nome} excluído com sucesso!')
        return redirect('meus_pets')
    return render(request, 'agendamentos/excluir_pet.html', {'pet': pet})

@login_required
def dados_pessoais(request):
    if request.user.is_superuser or request.user.is_staff:
        messages.info(request, 'Usuários administradores não possuem perfil personalizado.')
        return redirect('home')
    
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    
    if created:
        messages.info(request, 'Perfil criado com sucesso! Complete seus dados.')
    
    if request.method == 'POST':
        form = DadosPessoaisForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados pessoais atualizados com sucesso!')
            return redirect('dados_pessoais')
    else:
        form = DadosPessoaisForm(instance=perfil)
    
    return render(request, 'agendamentos/dados_pessoais.html', {'form': form})

# ==============================================================================
# View de Agendamento (ALTERADA)
# ==============================================================================

def agendar_servico(request):
    if request.method == 'POST':
        # Instanciar o formulário para validação inicial de dados
        form = AgendamentoForm(request.POST, user=request.user if request.user.is_authenticated else None)
        
        # Capturar os dados brutos antes de validar o formulário
        servicos_ids = request.POST.getlist('servicos') # IDs dos serviços
        horario_inicio_str = request.POST.get('horario_inicio')
        data_str = request.POST.get('data')

        if form.is_valid():
            
            # 1. CÁLCULO DA DURAÇÃO
            duracao_total = calcular_duracao_total(servicos_ids)
            
            try:
                data_agendamento = date.fromisoformat(data_str)
            except ValueError:
                messages.error(request, "Data inválida.")
                return redirect('agendar_servico')
            
            # 2. VALIDAÇÃO DE CONFLITO
            if not is_slot_livre(data_agendamento, horario_inicio_str, duracao_total):
                messages.error(request, f"O horário selecionado ({horario_inicio_str}) está ocupado pelo período de {duracao_total} minutos. Escolha outro horário.")
                return redirect('agendar_servico')
            
            # 3. SALVAR O AGENDAMENTO (com novos campos)
            agendamento = form.save(commit=False)
            
            # Preenche os campos de duração e horário de início
            agendamento.duracao_total_minutos = duracao_total
            agendamento.horario_inicio = datetime.strptime(horario_inicio_str, '%H:%M').time()
            
            # Código original de autenticação do usuário
            if request.user.is_authenticated:
                agendamento.usuario = request.user
                pet = form.cleaned_data.get('pet')
                if pet:
                    agendamento.pet = pet
            
            agendamento.save()
            form.save_m2m()
            
            messages.success(request, f'Agendamento realizado com sucesso para {agendamento.data} das {horario_inicio_str} até {agendamento.horario_fim().strftime("%H:%M")}!')
            return redirect('home')
        
    else:
        form = AgendamentoForm(user=request.user if request.user.is_authenticated else None)
    
    servicos = Servico.objects.filter(ativo=True)
    
    pets_json = []
    if request.user.is_authenticated:
        pets = Pet.objects.filter(dono=request.user)
        pets_json = [{'id': pet.id, 'nome': pet.nome, 'tipo': pet.tipo} for pet in pets]
    
    return render(request, 'agendamentos/agendar_servico.html', {
        'form': form,
        'servicos': servicos,
        'pets_json': json.dumps(pets_json)
    })

# ==============================================================================
# View de Disponibilidade (CORRIGIDA)
# ==============================================================================

def verificar_horarios_disponiveis(request):
    data = request.GET.get('data')
    # O frontend precisa enviar uma string de IDs separados por vírgula (ex: "1,3,4")
    # REMOVIDO: default='', pois o frontend DEVE enviar
    servicos_ids_str = request.GET.get('servicos_ids') 
    
    if not data or not servicos_ids_str:
        # Se os serviços não foram selecionados, não podemos calcular a duração
        return JsonResponse({'error': 'Data e serviços são obrigatórios para verificar a disponibilidade'}, status=400)
    
    try:
        # 1. Preparação de Data e Hora
        data_obj = date.fromisoformat(data)
        
        # Obtém o horário atual do servidor no fuso horário configurado no settings.py
        agora_local = timezone.localtime(timezone.now())
        hoje = agora_local.date()
        
        # Define a hora limite para agendamento (hora atual arredondada para baixo, mais 15 minutos)
        hora_minima_para_agendar = agora_local + timedelta(minutes=15)
        
        # 2. Calcular a duração potencial do NOVO agendamento
        # Garante que IDs vazios não quebrem
        servicos_ids = [int(sid) for sid in servicos_ids_str.split(',') if sid]
        
        # Garante que pelo menos um serviço foi selecionado (já que servicos_ids_str não é nulo/vazio)
        if not servicos_ids:
            return JsonResponse({'error': 'Serviço(s) inválido(s) selecionado(s).'}, status=400)
            
        duracao_novo_agendamento = calcular_duracao_total(servicos_ids)
        
        horarios_possiveis = gerar_horarios_possiveis(intervalo_minutos=15)
        horarios_disponiveis = []
        
        # 3. Buscar agendamentos existentes no dia
        agendamentos_dia = Agendamento.objects.filter(
            data=data_obj,
            status__in=['agendado', 'confirmado']
        )
        
        # 4. Iterar por cada horário possível (slots de 15 minutos)
        for horario_str in horarios_possiveis:
            
            slot_time = datetime.strptime(horario_str, '%H:%M').time()
            
            # --- NOVO FILTRO DE TEMPO PASSADO (CORRIGIDO PARA O ERRO 500) ---
            if data_obj == hoje:
                # Cria o datetime NAIVE (sem fuso)
                slot_dt_naive = datetime.combine(data_obj, slot_time)
                
                # Converte o slot para AWARE para que a comparação funcione
                slot_dt_completo = timezone.make_aware(slot_dt_naive, timezone.get_current_timezone()) 
                
                # O horário do slot deve ser maior ou igual à hora mínima de agendamento de hoje
                if slot_dt_completo < hora_minima_para_agendar.replace(second=0, microsecond=0):
                    continue # Pula o slot se ele já passou
            # ------------------------------------
            
            # Slot que o usuário está tentando reservar (início e fim)
            slot_inicio_dt = datetime.combine(data_obj, slot_time)
            slot_fim_dt = slot_inicio_dt + timedelta(minutes=duracao_novo_agendamento)
            
            is_livre = True
            
            # Verifica se o NOVO slot completo se sobrepõe a qualquer agendamento existente
            for agendamento in agendamentos_dia:
                agendamento_inicio = datetime.combine(data_obj, agendamento.horario_inicio)
                agendamento_fim = agendamento_inicio + timedelta(minutes=agendamento.duracao_total_minutos)

                conflito = (
                    (slot_inicio_dt < agendamento_fim) and 
                    (slot_fim_dt > agendamento_inicio)
                )

                if conflito:
                    is_livre = False
                    break 
                    
            if is_livre:
                horarios_disponiveis.append(horario_str)
        
        return JsonResponse({'horarios_disponiveis': horarios_disponiveis})
    
    except ValueError:
        return JsonResponse({'error': 'Data ou formato de serviço inválido'}, status=400)

def consultar_cep(request):
    cep = request.GET.get('cep', '').replace('-', '')
    
    if len(cep) != 8:
        return JsonResponse({'error': 'CEP deve ter 8 dígitos'}, status=400)
    
    try:
        url = f'https://viacep.com.br/ws/{cep}/json/'
        
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            data = json_lib.loads(data)
        
        if 'erro' in data:
            return JsonResponse({'error': 'CEP não encontrado'}, status=404)
        
        return JsonResponse({
            'rua': data.get('logradouro', ''),
            'bairro': data.get('bairro', ''),
            'cidade': data.get('localidade', ''),
            'estado': data.get('uf', '')
        })
        
    except Exception as e:
        return JsonResponse({'error': 'Erro ao consultar CEP: ' + str(e)}, status=500)

# ===========================
# NOVAS FUNÇÕES: Editar e Cancelar Agendamento (MUDANÇAS MÍNIMAS)
# ===========================

@login_required
def editar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id, usuario=request.user)

    if request.method == 'POST':
        form = AgendamentoForm(request.POST, instance=agendamento, user=request.user)
        
        # Capturar os dados brutos
        servicos_ids = request.POST.getlist('servicos') 
        horario_inicio_str = request.POST.get('horario_inicio')
        data_str = request.POST.get('data')

        if form.is_valid():
            # 1. CÁLCULO DA DURAÇÃO
            duracao_total = calcular_duracao_total(servicos_ids)
            
            try:
                data_agendamento = date.fromisoformat(data_str)
            except ValueError:
                messages.error(request, "Data inválida.")
                return redirect('meus_agendamentos')
                
            # 2. VALIDAÇÃO DE CONFLITO (incluindo a ID para ignorar o próprio agendamento)
            if not is_slot_livre(data_agendamento, horario_inicio_str, duracao_total, agendamento_id=agendamento.id):
                messages.error(request, f"O horário selecionado ({horario_inicio_str}) está ocupado pelo período de {duracao_total} minutos. Escolha outro horário.")
                return redirect('meus_agendamentos')

            # 3. SALVAR (com novos campos)
            agendamento = form.save(commit=False)
            agendamento.duracao_total_minutos = duracao_total
            agendamento.horario_inicio = datetime.strptime(horario_inicio_str, '%H:%M').time()
            agendamento.save()
            form.save_m2m() # Salva a relação de serviços

            messages.success(request, 'Agendamento atualizado com sucesso!')
            return redirect('meus_agendamentos')
    else:
        # Se for GET, o horário no form deve ser o TimeField
        # O campo 'horario' no form deve ser preenchido corretamente pelo Django
        form = AgendamentoForm(instance=agendamento, user=request.user)

    # Monta os pets em JSON para o JS do template
    pets_json = []
    if request.user.is_authenticated:
        pets = Pet.objects.filter(dono=request.user)
        pets_json = [{'id': pet.id, 'nome': pet.nome, 'tipo': pet.tipo} for pet in pets]

    servicos = Servico.objects.filter(ativo=True)

    return render(request, 'agendamentos/agendar_servico.html', {
        'form': form,
        'servicos': servicos,
        'pets_json': json.dumps(pets_json),
        'editar': True,
        'agendamento': agendamento
    })


@login_required
def cancelar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id, usuario=request.user)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '')
        agendamento.status = 'cancelado'
        if motivo:
            agendamento.motivo_cancelamento = motivo
        agendamento.save()
        messages.warning(request, 'Agendamento cancelado com sucesso!')
        return redirect('meus_agendamentos')
    
    return redirect('meus_agendamentos')