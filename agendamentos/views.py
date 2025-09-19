# agendamentos/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm, PetForm, DadosPessoaisForm, AgendamentoForm
from .models import Pet, PerfilUsuario, Servico, Agendamento
from django.http import JsonResponse
from datetime import date
import json
import urllib.request
import json as json_lib

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
    agendamentos = Agendamento.objects.filter(usuario=request.user).order_by('-data', 'horario')
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

def agendar_servico(request):
    if request.method == 'POST':
        form = AgendamentoForm(request.POST, user=request.user if request.user.is_authenticated else None)
        if form.is_valid():
            agendamento = form.save(commit=False)
            
            if request.user.is_authenticated:
                agendamento.usuario = request.user
                pet = form.cleaned_data.get('pet')
                if pet:
                    agendamento.pet = pet
            
            agendamento.save()
            form.save_m2m()
            
            messages.success(request, f'Agendamento realizado com sucesso para {agendamento.data} às {agendamento.horario}!')
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
    
    if not data:
        return JsonResponse({'error': 'Data é obrigatória'}, status=400)
    
    try:
        data_obj = date.fromisoformat(data)
        horarios_disponiveis = [h[0] for h in Agendamento.HORARIOS_DISPONIVEIS]
        
        horarios_ocupados = Agendamento.objects.filter(
            data=data_obj,
            status__in=['agendado', 'confirmado']
        ).values_list('horario', flat=True)
        
        horarios_disponiveis = [h for h in horarios_disponiveis if h not in horarios_ocupados]
        
        return JsonResponse({'horarios_disponiveis': horarios_disponiveis})
    
    except ValueError:
        return JsonResponse({'error': 'Data inválida'}, status=400)

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