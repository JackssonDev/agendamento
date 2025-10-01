from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, datetime, time, timedelta
import json
import urllib.request

# Importa a nova camada de serviços
from .services import (
    calcular_duracao_total, 
    gerar_horarios_possiveis, 
    checar_conflito_agendamento
)

from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, PetForm, 
    DadosPessoaisForm, AgendamentoForm
)
from .models import Pet, PerfilUsuario, Servico, Agendamento

# ==============================================================================
# Views de Autenticação e Informação (sem alterações na lógica)
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
    if not request.user.is_superuser and not request.user.is_staff:
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
    
    messages.info(request, 'Usuários administradores não possuem perfil personalizado.')
    return redirect('home')

# ==============================================================================
# Views de Agendamento e Utilitários
# ==============================================================================

def agendar_servico(request):
    if request.method == 'POST':
        form = AgendamentoForm(request.POST, user=request.user if request.user.is_authenticated else None)
        
        servicos_ids = request.POST.getlist('servicos')
        horario_inicio_str = request.POST.get('horario_inicio')
        data_str = request.POST.get('data')

        if form.is_valid():
            
            # 1. CÁLCULO DA DURAÇÃO (USANDO SERVICE)
            duracao_total = calcular_duracao_total(servicos_ids)
            
            try:
                data_agendamento = date.fromisoformat(data_str)
            except ValueError:
                messages.error(request, "Data inválida.")
                return redirect('agendar_servico')
            
            # 2. VALIDAÇÃO DE CONFLITO (USANDO SERVICE)
            if not checar_conflito_agendamento(data_agendamento, horario_inicio_str, duracao_total):
                messages.error(request, f"O horário selecionado ({horario_inicio_str}) está ocupado pelo período de {duracao_total} minutos. Escolha outro horário.")
                return redirect('agendar_servico')
            
            # 3. SALVAR O AGENDAMENTO (com novos campos)
            agendamento = form.save(commit=False)
            
            agendamento.duracao_total_minutos = duracao_total
            agendamento.horario_inicio = datetime.strptime(horario_inicio_str, '%H:%M').time()
            
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

def verificar_horarios_disponiveis(request):
    data = request.GET.get('data')
    servicos_ids_str = request.GET.get('servicos_ids') 
    
    if not data or not servicos_ids_str:
        return JsonResponse({'error': 'Data e serviços são obrigatórios para verificar a disponibilidade'}, status=400)
    
    try:
        # 1. Preparação de Data
        data_obj = date.fromisoformat(data)
        
        agora_local = timezone.localtime(timezone.now())
        hoje = agora_local.date()
        hora_minima_para_agendar = agora_local + timedelta(minutes=15)
        
        # 2. Obter Duração e Horários Base (USANDO SERVICE)
        servicos_ids = [int(sid) for sid in servicos_ids_str.split(',') if sid]
        if not servicos_ids:
            return JsonResponse({'error': 'Serviço(s) inválido(s) selecionado(s).'}, status=400)
            
        duracao_novo_agendamento = calcular_duracao_total(servicos_ids)
        horarios_possiveis = gerar_horarios_possiveis(intervalo_minutos=15)
        
        horarios_disponiveis = []
        
        # 3. Iterar e Checar a disponibilidade
        for horario_str in horarios_possiveis:
            
            slot_time = datetime.strptime(horario_str, '%H:%M').time()
            
            # --- FILTRO DE TEMPO PASSADO (MANTIDO NA VIEW) ---
            if data_obj == hoje:
                slot_dt_naive = datetime.combine(data_obj, slot_time)
                slot_dt_completo = timezone.make_aware(slot_dt_naive, timezone.get_current_timezone()) 
                
                if slot_dt_completo < hora_minima_para_agendar.replace(second=0, microsecond=0):
                    continue
            # ------------------------------------
            
            # Checa o conflito usando a função de serviço
            if checar_conflito_agendamento(data_obj, horario_str, duracao_novo_agendamento):
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
            data = json.loads(data)
        
        if data.get('erro'):
            return JsonResponse({'error': 'CEP não encontrado'}, status=404)
        
        return JsonResponse({
            'rua': data.get('logradouro', ''),
            'bairro': data.get('bairro', ''),
            'cidade': data.get('localidade', ''),
            'estado': data.get('uf', '')
        })
        
    except Exception as e:
        return JsonResponse({'error': 'Erro ao consultar CEP: ' + str(e)}, status=500)

@login_required
def editar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id, usuario=request.user)

    if request.method == 'POST':
        form = AgendamentoForm(request.POST, instance=agendamento, user=request.user)
        
        servicos_ids = request.POST.getlist('servicos') 
        horario_inicio_str = request.POST.get('horario_inicio')
        data_str = request.POST.get('data')

        if form.is_valid():
            
            # 1. CÁLCULO DA DURAÇÃO (USANDO SERVICE)
            duracao_total = calcular_duracao_total(servicos_ids)
            
            try:
                data_agendamento = date.fromisoformat(data_str)
            except ValueError:
                messages.error(request, "Data inválida.")
                return redirect('meus_agendamentos')
                
            # 2. VALIDAÇÃO DE CONFLITO (USANDO SERVICE)
            if not checar_conflito_agendamento(data_agendamento, horario_inicio_str, duracao_total, agendamento_id=agendamento.id):
                messages.error(request, f"O horário selecionado ({horario_inicio_str}) está ocupado pelo período de {duracao_total} minutos. Escolha outro horário.")
                return redirect('meus_agendamentos')

            # 3. SALVAR
            agendamento = form.save(commit=False)
            agendamento.duracao_total_minutos = duracao_total
            agendamento.horario_inicio = datetime.strptime(horario_inicio_str, '%H:%M').time()
            agendamento.save()
            form.save_m2m()

            messages.success(request, 'Agendamento atualizado com sucesso!')
            return redirect('meus_agendamentos')
    else:
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