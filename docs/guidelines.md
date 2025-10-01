# 🚀 Guidelines, Testes e Contribuições

## 1. Guidelines e Padrões de Código

### 1.1. Padrões de Commit (Conventional Commits)

Os commits devem seguir o padrão **`type(scope): message`** para manter um histórico claro e automatizável.

* `feat`: Adiciona um novo recurso (ex: `feat(api): Adiciona endpoint de usuários`).
* `fix`: Corrige um bug (ex: `fix(auth): Corrige falha no redirecionamento pós-login`).
* `chore`: Mudanças em builds, dependências, configs (ex: `chore(deps): Atualiza Django para 5.0.5`).
* `docs`: Mudanças na documentação.
* `refactor`: Refatoração que não corrige bug nem adiciona funcionalidade.

### 1.2. Padrão de Arquitetura

* Lógica de negócio complexa deve ser isolada em **`services.py`**.
* Views devem ser leves, focadas em I/O e renderização.

## 2. Desenvolvimento e Testes

### 2.1. Testes de Unidade

A cobertura de testes é focada na **Camada de Serviços (`services.py`)**.

Para rodar os testes:
```bash
python manage.py test agendamentos
```
Foco: Garantir que as regras de negócio críticas (conflito de horário, duração, horários de almoço) funcionem 100% do tempo.

### 2.2. Docker para Desenvolvimento
Utilize o docker-compose.yml para rodar o ambiente com PostgreSQL localmente, replicando o ambiente de produção.
```bash
docker-compose up --build
```

## 3. Contribuições
Contribuições são bem-vindas! Siga o processo de Pull Request (PR):

Crie um fork do projeto.

Crie uma branch com o nome descritivo (ex: feat/adicionar-relatorio ou fix/corrigir-bug-cep).

Implemente suas alterações, seguindo os Guidelines acima.

Crie um Pull Request para a branch main.

## 4. Release Notes
Detalhes sobre as versões e as principais mudanças.

v1.1.0 - Refatoração e Qualidade (Próxima Versão)
feat: Implementação da Camada de Serviços para Agendamento.

fix: Correção de erro de digitação no test suite que impedia a execução.

chore: Mapeamento de tags de mensagem Django para classes Bootstrap.

feat: Dockerização completa do projeto para portabilidade.

v1.0.0 - Lançamento Inicial
Lançamento da funcionalidade básica de CRUD de Agendamentos e Pets.

Integração com Bootstrap 5 e Jazzmin Admin.

Funcionalidade de preenchimento automático de endereço ViaCEP.