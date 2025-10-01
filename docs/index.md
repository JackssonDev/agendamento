# 📚 Documentação Técnica do PetCare Agendamento

## Visão Geral

O PetCare Agendamento é uma plataforma web desenvolvida para simplificar o agendamento de serviços veterinários em domicílio (banho, tosa, curativos etc.). O sistema, construído em **Python (Django)**, é focado em segurança, performance e uma excelente experiência de usuário.

O principal diferencial da aplicação é sua **Camada de Serviços testável**, que gerencia a lógica complexa de agendamento, como cálculo dinâmico de duração de serviços e checagem de conflitos de horário em tempo real.

---

## Índice da Documentação

| Seção | Conteúdo Principal |
| :--- | :--- |
| **[Setup e Instalação](setup.md)** | Pré-requisitos, instruções de instalação local e variáveis de ambiente. |
| **[Arquitetura do Sistema](architecture.md)** | Modelos de dados (ERD), diagramas de fluxo (CRUD, Autenticação) e estrutura de diretórios. |
| **[APIs e Endpoints](architecture.md#4-endpoints-e-potencial-de-api)** | Definição de endpoints REST (potenciais) e estrutura de dados. |
| **[Segurança e Autenticação](security.md)** | Guidelines de autenticação, gerenciamento de segredos e práticas de deploy seguro. |
| **[Qualidade e Padrões](guidelines.md)** | Guidelines de código, padrões de commit, processos de desenvolvimento e testes. |

---

## 🛠️ Tecnologias Principais

| Categoria | Tecnologia |
| :--- | :--- |
| **Backend** | Python 3.10+, Django 5.x, Gunicorn |
| **Banco de Dados** | PostgreSQL (Produção), SQLite3 (Desenvolvimento) |
| **Frontend** | HTML5, CSS3 (Bootstrap 5), JavaScript (jQuery e Vanilla JS) |
| **Infraestrutura** | Docker, Render (PaaS), WhiteNoise |