
### 3. `docs/architecture.md` (Arquitetura, Modelagem e Endpoints)

Este arquivo detalha a **Estrutura**, **Modelagem de Dados**, **Arquitetura** e **Endpoints API**.

```markdown
# 📐 Arquitetura do Sistema e Modelagem

## 1. Estrutura do Projeto (Diretórios e Arquivos)

A estrutura segue o padrão Django, com a aplicação principal (`agendamentos`) isolada e focada em Domain-Driven Design (DDD), separando a lógica de negócio na camada de serviços.

```text
agendamento/
├── agendamento/        # Configuração do Projeto Django (settings, urls)
│   ├── settings.py     # Configurações com python-decouple e settings de produção/Docker.
│   └── urls.py         # URLs principais
├── agendamentos/       # Aplicação Principal (Domain)
│   ├── models.py       # Definição dos modelos de dados.
│   ├── forms.py        # Customização de formulários (Autenticação, Agendamento).
│   ├── services.py     # 🚨 Camada de Serviços: Lógica de negócio crítica (conflito, duração).
│   ├── views.py        # Camada de Apresentação e requisições.
│   ├── tests.py        # Testes de Unidade para a camada de serviços.
│   └── templates/      # Templates HTML.
├── docs/               # Documentação Técnica do Projeto (este diretório).
├── venv/
├── Dockerfile          # Instruções de Build do Container.
├── docker-compose.yml  # Configuração local (Django + PostgreSQL).
└── requirements.txt
```

## 2. Modelos de Dados (ERD Simplificado)

O diagrama abaixo representa as relações críticas para o sistema de agendamento.

```mermaid
erDiagram
    USUARIO ||--o{ PERFIL_USUARIO : "tem um"
    USUARIO ||--o{ PET : "é dono de"
    PET ||--o{ AGENDAMENTO : "pertence a"
    AGENDAMENTO ||--o{ PERFIL_USUARIO : "criado por"
    AGENDAMENTO }o--o{ SERVICO : "contém"

    USUARIO {
        int id PK
        varchar username
        varchar email
    }
    PERFIL_USUARIO {
        int id PK
        int usuario_id FK
        varchar cpf
        date data_nascimento
    }
    PET {
        int id PK
        int dono_id FK
        varchar nome
        varchar tipo
     }
    SERVICO {
        int id PK
        varchar nome
        int duracao_minutos
        decimal preco
    }
    AGENDAMENTO {
        int id PK
        int tutor_id FK
        int pet_id FK
        date data
        time horario_inicio
        decimal valor_total
        varchar endereco
    }
    ```
    
## 3. Arquitetura do Sistema (Fluxo de Dados)
O diagrama ilustra a separação de responsabilidades (SoC) com a Camada de Serviços isolada.
```mermaid
graph TD
    A[Usuário/Cliente] --> B(Requisição HTTP);
    B --> C{Django: URLs};
    C --> D[Views.py];
    D -- Dados/Regras --> E[Services.py: Lógica de Negócio];
    E -- Validação/Consultas --> F[Models.py / Banco de Dados];
    F --> E;
    E -- Resultado --> D;
    D -- Renderização --> G[Templates/Mensagens];
    G --> A;

    subgraph Backend
        C
        D
        E
        F
    end
    ```
    
## 4. Fluxos Críticos do Sistema

### 4.1. Fluxo de Agendamento (CRUD)
```mermaid
flowchart TD
    A[Início: Formulário de Agendamento] --> B{POST: views.agendar_servico};
    B --> C[Forms.py: Validação de Dados];
    C -- Dados Válidos --> D[Services.py: Checar Conflito e Duração];
    D -- Conflito Encontrado --> E[Views: messages.error('Conflito')]
    D -- Slot Livre --> F[Services.py: Criar Agendamento]
    F --> G[Models.py: Salvar no DB]
    G --> H[Views: messages.success('Agendado')]
    H --> I[Redirecionar para Meus Agendamentos]
    E --> B;
    ```
    
### 4.2. Fluxo de Autenticação (Login)
```mermaid
flowchart TD
    A[Tela de Login] --> B{POST: forms.CustomAuthenticationForm};
    B -- Credenciais --> C[Django Auth Backend];
    C -- Falha na Autenticação --> D[Forms: erro 'Usuário/Senha inválido'];
    D --> A;
    C -- Sucesso --> E[Views: login(user)];
    E --> F[Redirecionamento Pós-Login];
    ```
    