# 🔒 Autenticação e Segurança

O projeto prioriza a segurança, seguindo as melhores práticas do Django para proteção de dados e deploy em produção.

## 1. Autenticação

### 1.1. Formulários Customizados

* A autenticação utiliza **`CustomAuthenticationForm`** (`agendamentos/forms.py`).
* **Segurança de Login (UX):** A mensagem de erro de falha de login é genérica e customizada ("Usuário ou senha inválido"), mitigando ataques de enumeração de usuários.

### 1.2. Gerenciamento de Senhas
O Django utiliza o padrão **PBKDF2** (Password-Based Key Derivation Function 2) com **salting** para o hash de senhas.

## 2. Padrões de Segurança no Deploy

### 2.1. Gerenciamento de Segredos (`python-decouple`)

Todos os segredos críticos (`SECRET_KEY`, `DATABASE_URL`) são lidos de variáveis de ambiente.

### 2.2. Configurações de HTTPS e HSTS

As seguintes configurações no `settings.py` são ativas em ambiente de produção (`DEBUG=False`):

* **Forçar HTTPS:** `SECURE_SSL_REDIRECT = True`
* **Cookies Seguros:** `CSRF_COOKIE_SECURE = True` e `SESSION_COOKIE_SECURE = True`
* **HSTS:** Configurado com `SECURE_HSTS_SECONDS = 31536000` (1 ano) para forçar o navegador a usar HTTPS em acessos futuros.

### 2.3. Host Header Protection

A lista **`ALLOWED_HOSTS`** é estritamente configurada (via variáveis de ambiente) para aceitar apenas os domínios de produção, prevenindo ataques de *Host Header Spoofing*.

## 3. Fluxo de Segurança (Exemplo de Proteção de Dados)

O diagrama ilustra como os segredos são lidos no ambiente de produção (Render).

```mermaid
flowchart LR
    A[Variáveis de Ambiente (Render)] --> B(settings.py);
    subgraph Código Django
        B --> C{python-decouple};
        C --> D[Chaves como SECRET_KEY];
    end
    D --> E[Execução da Aplicação];