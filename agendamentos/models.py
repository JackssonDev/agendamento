from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Pet(models.Model):
    TIPO_CHOICES = [
        ('cachorro', 'Cachorro'),
        ('gato', 'Gato'),
        ('passaro', 'Pássaro'),
        ('roedor', 'Roedor'),
        ('outro', 'Outro'),
    ]
    
    dono = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')
    nome = models.CharField(max_length=100, verbose_name='Nome do Pet')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo')
    raca = models.CharField(max_length=100, verbose_name='Raça', blank=True)
    idade = models.PositiveIntegerField(verbose_name='Idade (anos)', null=True, blank=True)
    observacao = models.TextField(verbose_name='Observações', blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['nome']
        verbose_name = 'Pet'
        verbose_name_plural = 'Pets'
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()}) - {self.dono.username}"

class PerfilUsuario(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
        ('N', 'Prefiro não informar'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    cpf = models.CharField(max_length=14, verbose_name='CPF', blank=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, blank=True, verbose_name='Gênero')
    data_nascimento = models.DateField(null=True, blank=True, verbose_name='Data de Nascimento')
    telefone = models.CharField(max_length=15, blank=True, verbose_name='Telefone')
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"

class Servico(models.Model):
    nome = models.CharField(max_length=100, verbose_name='Nome do Serviço')
    preco = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        verbose_name='Preço',
        validators=[MinValueValidator(0)]
    )
    descricao = models.TextField(verbose_name='Descrição', blank=True)
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    
    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - R$ {self.preco}"

class Agendamento(models.Model):
    HORARIOS_DISPONIVEIS = [
        ('08:00', '08:00'),
        ('09:00', '09:00'),
        ('10:00', '10:00'),
        ('11:00', '11:00'),
        ('14:00', '14:00'),
        ('15:00', '15:00'),
        ('16:00', '16:00'),
        ('17:00', '17:00'),
    ]
    
    STATUS_CHOICES = [
        ('agendado', 'Agendado'),
        ('confirmado', 'Confirmado'),
        ('realizado', 'Realizado'),
        ('cancelado', 'Cancelado'),
    ]
    
    FORMA_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('transferencia', 'Transferência Bancária'),
    ]
    
    # Relacionamentos
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='agendamentos')
    servicos = models.ManyToManyField(Servico, verbose_name='Serviços')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Pet')
    
    # Informações do agendamento
    nome_tutor = models.CharField(max_length=100, verbose_name='Nome do Tutor')
    nome_pet = models.CharField(max_length=100, verbose_name='Nome do Pet')
    tipo_pet = models.CharField(max_length=20, verbose_name='Tipo do Pet')
    data = models.DateField(verbose_name='Data do Agendamento')
    horario = models.CharField(max_length=5, choices=HORARIOS_DISPONIVEIS, verbose_name='Horário')
    
    # Endereço
    cep = models.CharField(max_length=9, verbose_name='CEP')
    rua = models.CharField(max_length=200, verbose_name='Rua')
    numero = models.CharField(max_length=10, verbose_name='Número')
    bairro = models.CharField(max_length=100, verbose_name='Bairro')
    cidade = models.CharField(max_length=100, default='', verbose_name='Cidade')
    estado = models.CharField(max_length=2, default='', verbose_name='Estado')
    complemento = models.CharField(max_length=100, blank=True, verbose_name='Complemento')
    
    # Pagamento e valor
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES, verbose_name='Forma de Pagamento')
    valor_total = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='Valor Total')
    
    # Status e informações adicionais
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='agendado', verbose_name='Status')
    motivo_cancelamento = models.TextField(blank=True, verbose_name='Motivo do Cancelamento')  # NOVO CAMPO
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        ordering = ['-data', 'horario']
    
    def __str__(self):
        return f"{self.nome_pet} - {self.data} {self.horario}"
    
    def calcular_valor_total(self):
        return sum(servico.preco for servico in self.servicos.all())
