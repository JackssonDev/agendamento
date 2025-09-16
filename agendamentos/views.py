# agendamentos/views.py

from django.shortcuts import render

def home(request):
    """
    Esta função renderiza a página inicial do site.
    Ela não precisa de passar nenhum contexto por enquanto,
    apenas retorna o template 'agendamentos/home.html'.
    """
    return render(request, 'agendamentos/home.html')
