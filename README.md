# 🐾 PetCare Agendamento

[![Licença MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Feito com Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Feito com Django](https://img.shields.io/badge/Django-5.0.x-092E20.svg)](https://www.djangoproject.com/)

## 📄 Sobre o Projeto

O **PetCare Agendamento** é uma plataforma robusta desenvolvida em Django para facilitar a vida de tutores de animais de estimação que precisam agendar serviços como banho, tosa, curativos ou consultas veterinárias de rotina.

O diferencial do sistema está na lógica de agendamento: ele calcula a **duração total** baseada nos serviços selecionados e verifica a **disponibilidade de *slots*** em tempo real, garantindo que não haja conflitos de horário.

### 🔑 Principais Funcionalidades

* **Agendamento Dinâmico por Duração:** Calcula o tempo total do serviço e exibe apenas horários disponíveis que acomodem essa duração.
* **Gestão de Pets:** Usuários podem cadastrar e gerenciar seus múltiplos pets.
* **Integração ViaCEP:** Preenchimento automático de endereço (Rua, Bairro, Cidade) ao informar o CEP, agilizando o cadastro.
* **Perfis de Usuário:** Gestão completa de dados pessoais (CPF, telefone, data de nascimento) vinculados à conta Django.
* **Autenticação Segura:** Login, Logout e Cadastro com validações customizadas.

---

## 💻 Tecnologias Utilizadas

O projeto foi construído sobre uma arquitetura moderna e escalável:

| Categoria | Tecnologia |
| :--- | :--- |
| **Backend** | Python 3.10+, Django 5.x |
| **Banco de Dados** | PostgreSQL (Padrão de produção), SQLite3 (Desenvolvimento) |
| **Frontend** | HTML5, CSS3 (Bootstrap 5), JavaScript (jQuery e Vanilla JS) |
| **Deployment** | Render (PaaS), Gunicorn, WhiteNoise |
| **Ambiente** | Virtualenv, `python-decouple` |

---

## ⚙️ Como Rodar Localmente

Siga os passos abaixo para configurar o projeto em sua máquina local.

### 1. Pré-requisitos

Certifique-se de ter instalado:
* [Python 3.10+](https://www.python.org/downloads/)
* [Git](https://git-scm.com/downloads)

### 2. Clonagem e Configuração do Ambiente

```bash
# 1. Clone o repositório
git clone [https://github.com/jacksonpr74-sketch/agendamento]
cd agendamento

# 2. Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate  # No Windows, use: venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt