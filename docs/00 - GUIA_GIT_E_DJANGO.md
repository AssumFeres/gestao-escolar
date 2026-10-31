# Guia de Comandos — Git e Django (`manage.py`)

Referência rápida para o dia a dia do projeto. Não substitui o `GUIA_DE_SETUP.md` (que cobre instalação e configuração inicial) — este documento é sobre **o que rodar, e quando**, uma vez que o ambiente já está funcionando.

---

## 1. Git — rotina do dia a dia

### Ao começar a trabalhar (sempre, mesmo que tenha trabalhado ontem na mesma máquina)

```powershell
git checkout dev
git pull origin dev
```

Ou, se estiver continuando uma tarefa específica numa branch de feature:

```powershell
git checkout feature/nome-da-tarefa
git pull origin feature/nome-da-tarefa
```

**Por quê:** garante que você está com a versão mais recente, feita por qualquer pessoa do grupo — evita trabalhar em cima de código desatualizado.

### Criar uma branch nova para uma tarefa

```powershell
git checkout dev
git pull origin dev
git checkout -b feature/nome-da-sua-tarefa
```

**Quando usar:** sempre que for começar algo novo e isolável — uma funcionalidade, uma correção, uma etapa de um plano maior. Nomes curtos e descritivos (`feature/refatoracao-funcao`, `feature/editar-pessoa`).

**Atenção:** uma branch criada com `checkout -b` existe **só na sua máquina** até o primeiro `push`. Não aparece no GitHub automaticamente.

### Ver o estado atual antes de qualquer commit

```powershell
git status
```

**Sempre rode isso antes de `git add .`** — confirma exatamente quais arquivos serão incluídos no commit. Nunca deve aparecer `venv/`, `db.sqlite3` ou `.env` na lista (se aparecer, o `.gitignore` tem um problema).

### Adicionar e commitar

```powershell
git add .
git commit -m "prefixo: descrição breve do que foi feito"
```

**Prefixos usados no projeto:**

| Prefixo | Quando usar |
|---|---|
| `feat` | Funcionalidade nova |
| `fix` | Correção de um bug |
| `docs` | Só documentação (`docs/`), sem mudança de código |
| `test` | Só testes, sem funcionalidade nova junto |
| `chore` | Configuração, tooling, manutenção — sem efeito funcional pro usuário |
| `refactor` | Reorganiza/reescreve código existente sem mudar comportamento externo |
| `wip` | Trabalho reconhecidamente incompleto (ex: precisa parar no meio, mas quer salvar o progresso) |

**Regra prática:** cada commit deve representar um pedaço pequeno e testável — não acumule várias mudanças não relacionadas num commit só. Prefira `git status` mostrando poucos arquivos por commit a um commit gigante no fim do dia.

### Enviar para o GitHub

```powershell
git push
```

Primeira vez numa branch nova, use `-u` para associar a branch local com a remota:

```powershell
git push -u origin feature/nome-da-sua-tarefa
```

Depois da primeira vez, `git push` sozinho já basta.

### Ver o histórico de commits

```powershell
git log --oneline -5
```

Mostra os 5 commits mais recentes, um por linha — útil para confirmar em qual commit você está antes de continuar um trabalho, especialmente ao trocar de máquina.

### Ver todas as branches (locais e remotas)

```powershell
git branch -a
```

O `*` marca a branch atual. Branches `remotes/origin/...` já foram enviadas ao GitHub; as sem esse prefixo existem só localmente.

### Trocar de branch

```powershell
git checkout nome-da-branch
```

**Atenção:** sempre commite ou descarte mudanças pendentes antes de trocar de branch — o Git recusa a troca se houver risco de perder trabalho não salvo.

---

## 2. Django (`manage.py`) — rotina do dia a dia

### Ativar o ambiente virtual (sempre, antes de qualquer comando abaixo)

```powershell
.\venv\Scripts\Activate.ps1
```

Confirme que `(venv)` aparece no início da linha do terminal.

### Rodar o servidor local

```powershell
python manage.py runserver
```

Acessa em `http://127.0.0.1:8000/`. `Ctrl+C` (ou `Ctrl+Break` no Windows) para parar.

### Depois de mudar `models.py` — gerar a migration

```powershell
python manage.py makemigrations pessoas
```

**Sempre leia a saída com atenção** — o comando detecta *toda* diferença acumulada entre o código e o histórico de migrations, não só a mudança que você acabou de fazer. Se aparecer algo inesperado, investigue antes de aplicar.

**Se pedir um valor "one-off"** (ao adicionar campo obrigatório numa tabela que já tem dados): confirme se há dado real na tabela antes de escolher um valor arbitrário — se a tabela estiver vazia, qualquer valor serve, sem risco.

### Aplicar a migration ao banco

```powershell
python manage.py migrate
```

**Sempre rode isso logo depois de um `makemigrations`** (ou depois de um `git pull` que trouxe migrations novas de outra pessoa) — gerar a migration não altera o banco por si só, só aplicar de fato muda a estrutura.

### Rodar os testes automatizados

```powershell
pytest
```

**Rode depois de qualquer mudança em `models.py`, `services.py`, `views.py` ou `forms.py`** — mesmo mudanças pequenas. É o jeito mais rápido de confirmar que nada quebrou antes de seguir para o próximo passo.

### Criar um superusuário (uma vez por máquina/banco)

```powershell
python manage.py createsuperuser
```

Pede username, e-mail (pode deixar em branco) e senha. Necessário para acessar `/admin/`.

### Popular dados iniciais de um catálogo (fixture)

```powershell
python manage.py loaddata catalogo_inicial
```

Carrega o arquivo `pessoas/fixtures/catalogo_inicial.json` (Funções e Vínculos Formais padrão) de uma vez, sem precisar cadastrar manualmente pelo Admin. Rode isso em qualquer máquina nova, depois do `migrate`, antes de testar cadastros que dependem do catálogo.

**Cuidado:** fixtures com `pk` fixo sobrescrevem qualquer registro existente com o mesmo `pk`, sem avisar. Seguro em banco vazio ou recém-migrado; arriscado se já houver dados reais cadastrados manualmente com os mesmos números.

### Abrir um terminal Python com o projeto carregado (para testar Models/Forms isoladamente)

```powershell
python manage.py shell
```

Útil para testar um Form ou Model sem precisar montar uma tela inteira — por exemplo, confirmar que um formulário renderiza sem erro (`print(MeuForm())`) antes de integrá-lo numa View. Sai com `exit()`.

### Verificar se o projeto está configurado corretamente, sem rodar nada

```powershell
python manage.py check
```

Útil depois de mexer em `settings.py`, `urls.py`, ou registrar um app novo em `INSTALLED_APPS` — confirma que não há erro de configuração antes de tentar rodar o servidor.

---

## 3. Sequência típica de uma sessão de trabalho

Juntando os dois mundos, esta é a ordem que o projeto tem seguido na prática:

```powershell
# 1. Sincronizar
git checkout feature/nome-da-tarefa
git pull origin feature/nome-da-tarefa
.\venv\Scripts\Activate.ps1

# 2. Confirmar que o ponto de partida está saudável
python manage.py migrate
pytest

# 3. Trabalhar — editar código

# 4. A cada mudança de Model
python manage.py makemigrations pessoas
python manage.py migrate
pytest

# 5. Testar manualmente, se fizer sentido
python manage.py runserver

# 6. Fechar a etapa
git add .
git status
git commit -m "prefixo: descrição"
git push
```

---

## 4. Erros comuns e o que fazem

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| `NameError: name 'X' is not defined` em `models.py` | Uma classe referencia outra definida mais abaixo no arquivo | Mover a classe que falta para cima, ou usar referência por string (`'NomeDaClasse'`) se houver dependência circular |
| `ImportError: cannot import name 'X' from 'pessoas.Y'` | `X` foi removido/renomeado em `Y`, mas outro arquivo ainda tenta importá-lo | Localizar todos os arquivos que importam `X` (busca por texto no projeto) e atualizar |
| `IndentationError` | Espaçamento incorreto após uma edição manual | Conferir se a linha alterada está no mesmo nível de indentação das linhas vizinhas |
| `IntegrityError: UNIQUE constraint failed` | Um campo com `unique=True` recebeu valor duplicado — inclusive string vazia `""`, que conta como valor igual a outra `""` | Se o campo deveria aceitar "vazio" sem conflito, usar `null=True` junto de `blank=True`, e garantir que código Python envie `None`, não `""` |
| `ManagementForm data is missing` | Um Formset foi enviado sem os campos ocultos de controle (`TOTAL_FORMS`, etc.) | Confirmar que o template inclui `{{ meu_formset.management_form }}` |
| `No changes detected in app 'pessoas'` ao rodar `makemigrations` | O arquivo `models.py` não foi salvo antes de rodar o comando | Salvar o arquivo (`Ctrl+S`) e rodar de novo |
| `git push` falha com `Could not resolve host` | Instabilidade momentânea de rede, não relacionado a Git/código | Tentar `git push` de novo depois de alguns segundos |

---

## 5. Sobre trabalhar em mais de uma máquina

O catálogo de dados (`Funcao`, `VinculoFormal`, etc.) **não é versionado pelo Git** — só o *schema* (via migrations) é. Isso significa que, numa máquina nova ou depois de um período sem uso, o roteiro completo é:

```powershell
git pull origin <branch>
python manage.py migrate
python manage.py loaddata catalogo_inicial
pytest
```

Pular o `loaddata` deixa o catálogo vazio, o que impede testar qualquer cadastro que dependa de escolher uma `Funcao`.
