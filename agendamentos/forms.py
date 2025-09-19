# agendamentos/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Pet, PerfilUsuario, Servico, Agendamento
from django.core.exceptions import ValidationError
from datetime import date
import re
import json

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="E-mail",
        widget=forms.EmailInput(attrs={
            'autocomplete': 'email',
            'placeholder': 'Seu e-mail'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adiciona placeholders
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Seu nome de usuário'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Crie uma senha'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Repita a senha'
        })
        
        # REMOVE os help_texts
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adiciona placeholders
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Nome de usuário ou e-mail',
            'autocomplete': 'username'
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Sua senha',
            'autocomplete': 'current-password'
        })
        
        # REMOVE os help_texts
        self.fields['username'].help_text = ''
        self.fields['password'].help_text = ''

class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['nome', 'tipo', 'raca', 'idade', 'observacao']
        widgets = {
            'nome': forms.TextInput(attrs={
                'placeholder': 'Ex: Rex, Luna, Thor...',
                'class': 'form-control'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'raca': forms.TextInput(attrs={
                'placeholder': 'Ex: Labrador, Siames, SRD...',
                'class': 'form-control'
            }),
            'idade': forms.NumberInput(attrs={
                'placeholder': 'Idade em anos',
                'class': 'form-control',
                'min': '0',
                'max': '30'
            }),
            'observacao': forms.Textarea(attrs={
                'placeholder': 'Alguma observação importante sobre seu pet...',
                'class': 'form-control',
                'rows': 3
            }),
        }
        labels = {
            'nome': 'Nome do Pet',
            'tipo': 'Tipo de Animal',
            'raca': 'Raça',
            'idade': 'Idade (anos)',
            'observacao': 'Observações'
        }

class DadosPessoaisForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='Nome',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label='Sobrenome',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu sobrenome'
        })
    )
    email = forms.EmailField(
        required=True,
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu.email@exemplo.com'
        })
    )
    
    class Meta:
        model = PerfilUsuario
        fields = ['first_name', 'last_name', 'email', 'cpf', 'genero', 'data_nascimento', 'telefone']
        widgets = {
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00'
            }),
            'genero': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000'
            }),
        }
        labels = {
            'cpf': 'CPF',
            'genero': 'Gênero',
            'data_nascimento': 'Data de Nascimento',
            'telefone': 'Telefone'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.usuario:
            self.fields['first_name'].initial = self.instance.usuario.first_name
            self.fields['last_name'].initial = self.instance.usuario.last_name
            self.fields['email'].initial = self.instance.usuario.email
    
    def save(self, commit=True):
        perfil = super().save(commit=False)
        if perfil.usuario:
            perfil.usuario.first_name = self.cleaned_data['first_name']
            perfil.usuario.last_name = self.cleaned_data['last_name']
            perfil.usuario.email = self.cleaned_data['email']
            if commit:
                perfil.usuario.save()
                perfil.save()
        return perfil
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '')
        cpf = re.sub(r'[^0-9]', '', cpf)
        
        if cpf and len(cpf) != 11:
            raise ValidationError('CPF deve ter 11 dígitos.')
        
        return cpf
    
    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone', '')
        telefone = re.sub(r'[^0-9]', '', telefone)
        
        if telefone and len(telefone) not in [10, 11]:
            raise ValidationError('Telefone deve ter 10 ou 11 dígitos.')
        
        return telefone

class AgendamentoForm(forms.ModelForm):
    servicos = forms.ModelMultipleChoiceField(
        queryset=Servico.objects.filter(ativo=True),
        widget=forms.CheckboxSelectMultiple(),
        label='Serviços *'
    )
    
    class Meta:
        model = Agendamento
        fields = [
            'servicos', 'pet', 'nome_tutor', 'nome_pet', 'tipo_pet',
            'data', 'horario', 'cep', 'rua', 'numero', 'bairro', 'cidade', 'estado', 
            'complemento', 'forma_pagamento', 'observacoes'
        ]
        widgets = {
            'pet': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nome_tutor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do tutor'
            }),
            'nome_pet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do pet'
            }),
            'tipo_pet': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().isoformat()
            }),
            'horario': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000',
                'id': 'cep'
            }),
            'rua': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da rua',
                'id': 'rua'
            }),
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número',
                'id': 'numero'
            }),
            'bairro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bairro',
                'id': 'bairro'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade',
                'id': 'cidade'
            }),
            'estado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'UF',
                'id': 'estado',
                'maxlength': '2'
            }),
            'complemento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Complemento (opcional)',
                'id': 'complemento'
            }),
            'forma_pagamento': forms.Select(attrs={
                'class': 'form-select',
                'id': 'forma_pagamento'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Observações adicionais (opcional)',
                'rows': 3
            }),
        }
        labels = {
            'servicos': 'Serviços *',
            'pet': 'Pet (se já cadastrado)',
            'nome_tutor': 'Nome do Tutor *',
            'nome_pet': 'Nome do Pet *',
            'tipo_pet': 'Tipo do Pet *',
            'data': 'Data *',
            'horario': 'Horário *',
            'cep': 'CEP *',
            'rua': 'Rua *',
            'numero': 'Número *',
            'bairro': 'Bairro *',
            'cidade': 'Cidade *',
            'estado': 'Estado *',
            'complemento': 'Complemento',
            'forma_pagamento': 'Forma de Pagamento *',
            'observacoes': 'Observações'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtra pets do usuário se estiver logado
        if self.user and self.user.is_authenticated:
            self.fields['pet'].queryset = Pet.objects.filter(dono=self.user)
            
            # Preenche automaticamente os dados do usuário se existirem
            try:
                perfil = self.user.perfil
                self.fields['nome_tutor'].initial = f"{self.user.first_name} {self.user.last_name}".strip()
            except PerfilUsuario.DoesNotExist:
                pass
        else:
            self.fields['pet'].queryset = Pet.objects.none()
        
        # Opções para tipo de pet
        self.fields['tipo_pet'].widget.choices = [
            ('', 'Selecione o tipo...'),
            ('cachorro', 'Cachorro'),
            ('gato', 'Gato'),
            ('passaro', 'Pássaro'),
            ('roedor', 'Roedor'),
            ('outro', 'Outro'),
        ]
        
        # Opções para forma de pagamento
        self.fields['forma_pagamento'].widget.choices = [
            ('', 'Selecione a forma de pagamento...'),
        ] + Agendamento.FORMA_PAGAMENTO_CHOICES

    def clean_data(self):
        data = self.cleaned_data.get('data')
        if data and data < date.today():
            raise ValidationError('Não é possível agendar para datas passadas.')
        return data

    def clean_cep(self):
        cep = self.cleaned_data.get('cep', '')
        cep = re.sub(r'[^0-9]', '', cep)
        if len(cep) != 8:
            raise ValidationError('CEP deve ter 8 dígitos.')
        return f"{cep[:5]}-{cep[5:]}"
    
    def clean_estado(self):
        estado = self.cleaned_data.get('estado', '')
        if estado and len(estado) != 2:
            raise ValidationError('Estado deve ter 2 caracteres (ex: SP, RJ).')
        return estado.upper()
    
    def save(self, commit=True):
        agendamento = super().save(commit=False)
        
        # Calcula o valor total baseado nos serviços selecionados
        servicos = self.cleaned_data['servicos']
        agendamento.valor_total = sum(servico.preco for servico in servicos)
        
        if commit:
            agendamento.save()
            agendamento.servicos.set(servicos)  # Salva os serviços ManyToMany
        
        return agendamento