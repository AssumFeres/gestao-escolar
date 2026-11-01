# Andamento do Projeto — 17

**Data:** 31/08/2026
**Branch:** `feature/rename-pessoas-cadastros`
**Sessão dedicada a executar as Etapas 1 a 5 do plano de migração `docs/16 - PLANO_DE_MIGRACAO_APP_CADASTROS.md` — renomear o app Django `pessoas` para `cadastros`.**

---

## Contexto

Com a migração `Vinculo`→`Funcao` fechada e mesclada em `dev` (histórico completo em `docs/06` a `docs/15`), esta sessão iniciou a próxima frente já registrada no Kanban: renomear o app `pessoas` para `cadastros`, reconhecendo que o módulo sempre misturou catálogo (`Funcao`, `Disciplina`, `VinculoFormal`) com cadastro de pessoa de fato. Sessão realizada no quartel, passo a passo, com o ambiente já preparado antes de começar (branch criada a partir de `dev`, banco local resetado e testado, `pytest` verde com 18 testes).

---

## Etapa 1 — Renomear a pasta e os caminhos internos

Executada com `git mv` (em vez de mover pelo Explorer/`Rename-Item`), garantindo que o Git registrasse cada arquivo como `renamed` desde o início — importante para a legibilidade do diff no PR final.

- `pessoas/` → `cadastros/` (todos os 33 arquivos internos)
- `pessoas/static/pessoas/` → `cadastros/static/cadastros/`
- `pessoas/templates/pessoas/` → `cadastros/templates/cadastros/`
- `apps.py`: `name = 'pessoas'` → `name = 'cadastros'`, e a classe `PessoasConfig` renomeada para `CadastrosConfig` (não obrigatório para o Django, mas evita inconsistência interna)
- 4 `template_name` corrigidos em `views.py` (`ListaPessoasView`, `DetalhePessoaView`, `NovoCadastroPessoaView`, `PreencherRequisitosDocenteView`), via substituição em massa (`'pessoas/` → `'cadastros/`), segura porque o padrão só aparecia nesses 4 pontos
- Templates corrigidos: `/pessoas/` → `/cadastros/` nas URLs hardcoded (`detalhe.html`, `form_pessoa.html`, `lista.html`, `preencher_requisitos_docente.html`), e `{% static 'pessoas/js/...' %}` → `'cadastros/js/...'` em `form_pessoa.html`. **Não alterado, por ser rótulo de tela/variável, não nome de app:** títulos "Pessoas cadastradas" e a variável de contexto `pessoas`/`pessoa` em `lista.html`.

**Efeito colateral notado, sem risco real:** o Git parou de reconhecer `preencher_requisitos_docente.html` como "mesmo arquivo renomeado" depois da edição de conteúdo (mostrou como `deleted` + `new file` em vez de `renamed`) — o limiar de similaridade do Git foi ultrapassado pela quantidade de linhas alteradas. Conteúdo final correto, só o diff ficou menos elegante para revisão.

`python manage.py check` confirmou, ao final da etapa, um único erro esperado (`ModuleNotFoundError: No module named 'pessoas'`, porque `INSTALLED_APPS` ainda apontava para o nome antigo) — validando que a Etapa 1 não introduziu nenhum problema além do previsto.

**Commit:** `79882c9` — `refactor: renomeia app pessoas para cadastros (Etapa 1)`.

---

## Etapa 3 executada antes da Etapa 2 (ordem invertida, deliberadamente)

Depois da Etapa 1, o plano original previa a Etapa 2 (busca de imports Python) antes da Etapa 3 (configuração). Na prática, invertemos: sem o app registrado em `INSTALLED_APPS`, o Django nem carrega os models para permitir validar imports — então resolvemos `config/settings.py` e `config/urls.py` primeiro.

### Decisão nova, não prevista no plano original: prefixo da API também muda

O plano só especificava a mudança da URL pública (`/pessoas/` → `/cadastros/`), sem mencionar o prefixo da API (`/api/pessoas/`). Levantada a dúvida, a pessoa responsável esclareceu o propósito maior do app: `cadastros` vai ser o módulo "escritor" de todo o catálogo compartilhado do sistema (Pessoa, Disciplina, e futuramente Módulo/Turma), consumido por outros apps como Treinamento e Turmas. Isso reforçou a mesma lógica que já motivava a mudança da URL pública — um prefixo `api/pessoas/` sugeriria escopo só de pessoas, quando na verdade é mais amplo.

**Decisão confirmada:** `path('api/pessoas/', include('pessoas.api_urls'))` → `path('api/cadastros/', include('cadastros.api_urls'))`.

- `config/settings.py`: `'pessoas'` → `'cadastros'` em `INSTALLED_APPS`
- `config/urls.py`: `path('cadastros/', include('cadastros.urls'))` e `path('api/cadastros/', include('cadastros.api_urls'))`

---

## Etapa 2 — Buscar e corrigir todos os imports Python

Busca exaustiva com `Get-ChildItem -Recurse -Filter *.py | Where-Object { $_.FullName -notmatch '\venv\' } | Select-String -Pattern "from pessoas|import pessoas"` em todo o projeto (não só dentro de `cadastros/`).

### Descoberta que contradiz uma suposição do plano

O plano registrava, na seção "Atenção especial": *"`infraestrutura/` não referencia `pessoas`, então não precisa de mudança ali"*. Na prática, `python manage.py check` revelou que **`infraestrutura/cep/adapters.py` e `infraestrutura/cep/ports.py` importavam `from pessoas.models import Endereco`** — um import esquecido pelo próprio plano, exatamente o tipo de risco que o documento já alertava ("Import esquecido... gera `ModuleNotFoundError` só na hora de rodar"). Corrigido junto dos 3 arquivos de teste que também apareceram na busca (`test_buscar_cep.py`, `test_cadastrar_pessoa.py`, `test_views_api.py`).

`python manage.py check` retornou limpo (`System check identified no issues`) ao final.

**Commit (Etapas 2 e 3 juntas):** `10b3e8e` — `refactor: atualiza imports e configuracao para app cadastros (Etapas 2 e 3)`.

---

## Etapa 4 — Resetar o banco local e o histórico de migrations

- Pasta `cadastros/migrations/` apagada e recriada vazia (só `__init__.py`)
- `db.sqlite3` apagado
- `python manage.py makemigrations cadastros` gerou uma única `0001_initial.py`, consolidando as 18 migrations antigas
- `python manage.py migrate` aplicou limpo
- Superusuário recriado
- `python manage.py loaddata catalogo_inicial` — falhou na primeira tentativa

### Incidente 1 — fixture guarda o app_label dentro do próprio JSON

`loaddata` falhou com `Invalid model identifier: pessoas.funcao`. Descoberta: o fixture `catalogo_inicial.json` guarda o nome do app **dentro do conteúdo**, no campo `"model": "pessoas.funcao"` de cada um dos 11 objetos — uma referência textual que nenhuma das buscas de código (Etapas 1 e 2) conseguiria pegar, por não ser `.py` nem template. Corrigido com substituição em massa (`"pessoas.` → `"cadastros.`).

### Incidente 2 — BOM quebrando o parser JSON

Corrigido o app_label, o `loaddata` falhou de novo, agora com `Unexpected UTF-8 BOM`. Causa: `Set-Content -Encoding utf8` do PowerShell grava um BOM (Byte Order Mark) por padrão, que o parser `json.loads()` do Python não tolera (diferente de `.py`/`.html`, que toleram BOM sem problema). Corrigido regravando o arquivo com `[System.IO.File]::WriteAllText(..., New-Object System.Text.UTF8Encoding $false)`, que grava UTF-8 sem BOM.

**Lição prática, relevante para o relatório do PI:** qualquer edição de `.json` (ou outro formato com parser estrito) via `Set-Content -Encoding utf8` no PowerShell precisa desse passo extra de remoção de BOM — não é um problema geral de "encoding errado", é especificamente sobre quais parsers toleram ou não o marcador BOM.

Confirmado com `pytest` — `18 passed`.

**Commit:** `98d9173` — `chore: reseta migrations e banco local para app cadastros (Etapa 4)`.

---

## Etapa 5 — Testes manuais pelo navegador

### Incidente 3 — corrupção de acentuação (mojibake) espalhada por 8 arquivos

Ao testar manualmente, dois problemas de superfície apareceram: a API de busca de CEP não funcionava, e várias telas mostravam texto com acentuação quebrada (`Ã§`, `Ã£`, etc. em vez de `ç`, `ã`) em rótulos como "Matrícula e Documentação de Estrangeiro".

**Diagnóstico:** o comando usado para os replaces em massa da Etapa 2 (`(Get-Content $arquivo -Raw) -replace ... | Set-Content -Encoding utf8`) **lia** o arquivo sem especificar `-Encoding utf8` no `Get-Content` — o PowerShell assumiu uma codificação diferente da real (UTF-8 com acentuação), interpretou mal os bytes acentuados na memória, e gravou esse texto já corrompido de volta como "UTF-8 válido" (mas com o conteúdo errado). Isso atingiu 8 arquivos ao todo: os 3 testes já commitados na Etapa 2 (com falhas reais de `match=` em 3 `pytest.raises`, texto do teste corrompido embora a mensagem real do código estivesse certa), mais `views.py`, os 4 templates e o fixture — que já tinham sido corrompidos silenciosamente desde a Etapa 1/4, sem gerar nenhum erro visível até o teste manual olhar as telas.

**Correção, em duas fases:**
1. Os 3 arquivos de teste: restaurados do commit `79882c9` (ainda com acentuação correta, só com o import antigo `from pessoas`) e reaplicado o replace com `-Encoding utf8` explícito na leitura.
2. `views.py`, os 4 templates e o fixture: como esses já estavam corrompidos **desde antes** do commit `79882c9`, restaurar dali não ajudaria. Restaurados do commit-base da branch (`b2ffa1c`, antes de qualquer mudança da sessão) sob os caminhos antigos (`pessoas/...`), copiados com `Copy-Item` (cópia de bytes, sem reinterpretação de texto) para os caminhos novos (`cadastros/...`), e só então reaplicadas as substituições de caminho necessárias, com leitura `-Encoding utf8` correta.

`pytest` confirmou `18 passed` após a correção completa.

### Incidente 4 — URL da API de CEP com prefixo antigo

`cadastros/static/cadastros/js/buscar-cep.js` tinha a URL hardcoded `/api/pessoas/cep/${cep}/`, não capturada por nenhuma busca anterior (JS não estava no escopo de nenhuma das Etapas 1-4). Corrigido para `/api/cadastros/cep/${cep}/`, coerente com a decisão da Etapa 3.

**Commit (correções da Etapa 5):** `ec9a75c` — `fix: corrige URL de API de CEP e mojibake introduzido durante a renomeacao (Etapa 5)`.

### Teste funcional dos 3 fluxos (Discente/Docente/Gestão)

Telas de lista, detalhe, formulário completo e Admin testadas e funcionando. Dois bugs reais encontrados, **ambos pré-existentes, sem relação com a renomeação do app** — registrados no Kanban em vez de corrigidos nesta sessão, para manter o escopo da renomeação limpo:

- **`codigo_matricula_anac` salvo como string vazia:** `NovoCadastroPessoaView` monta `dados_extensao["codigo_matricula_anac"]` com `dados.get("codigo_matricula_anac", "")` em vez de `or None` — o mesmo padrão de `IntegrityError` já corrigido para `registro_matricula`/`registro_aluno`/`codigo_anac` na migração anterior, mas nunca replicado para este campo específico dentro do bloco de extensão do Discente.
- **Formset de Formação não valida `ano_conclusao` obrigatório:** o filtro `_linhas_preenchidas` considera uma linha "preenchida" checando só o campo `curso`; se `ano_conclusao` (também obrigatório no Model) ficar em branco, a linha passa pelo filtro e só falha no banco, gerando tela de erro genérica.

Também notado, sem necessidade de item novo no Backlog (já coberto pelo item existente sobre CRUD de edição): depois de um erro de submissão, não há como editar o cadastro que falhou — mas, como todo o fluxo roda em `transaction.atomic()`, não há risco real de dado salvo pela metade, só experiência de tela ruim.

---

## Estado geral ao final desta sessão

| Etapa do plano de migração (`docs/16`) | Status |
|---|---|
| Antes de começar (branch, banco resetado, `pytest` verde) | ✅ Já feito antes da sessão |
| Etapa 1 — Renomear pasta e caminhos internos | ✅ Concluída (`79882c9`) |
| Etapa 3 — Configuração (`settings.py`/`urls.py`) | ✅ Concluída, executada antes da Etapa 2 |
| Etapa 2 — Buscar e corrigir imports Python | ✅ Concluída (`10b3e8e`, junto da Etapa 3) — incluiu 2 arquivos de `infraestrutura/` não previstos no plano |
| Etapa 4 — Resetar migrations e banco local | ✅ Concluída (`98d9173`) — 2 incidentes de encoding resolvidos |
| Etapa 5 — Testar (automatizado + manual) | ✅ Concluída (`ec9a75c`) — 1 incidente de mojibake em 8 arquivos, 1 bug de URL, 2 bugs pré-existentes registrados no Backlog |
| Etapa 6 — Documentação e commit | 🔨 Em andamento (este diário) |
| Etapa 7 — Sincronizar as demais máquinas | ⏳ Não iniciada |

`pytest` — `18 passed` (mesma cobertura de antes da renomeação, sem alteração de conteúdo de teste).

---

## Itens novos de Backlog identificados nesta sessão

- [ ] `infraestrutura/cep/{adapters,ports}.py` importava de `pessoas` — corrigido nesta sessão, mas vale registrar como lição: a suposição "`infraestrutura/` é isento" no plano `docs/16` estava incorreta e não deve ser repetida em futuras reestruturações de app.
- [ ] `codigo_matricula_anac` salvo como string vazia em vez de `None` na `NovoCadastroPessoaView` (bloco Discente de `dados_extensao`) — mesmo padrão já conhecido, correção de uma linha (`or None`), não aplicada ainda.
- [ ] Formset de Formação (`FormacaoDocenteFormSet`) não valida `ano_conclusao` obrigatório antes de enviar ao Service — linha passa pelo filtro `_linhas_preenchidas` só checando `curso`.
- [ ] **Padrão a lembrar em qualquer edição de arquivo `.json` (ou outro parser estrito) via PowerShell:** `Set-Content -Encoding utf8` grava BOM, que quebra `json.loads()`; usar `[System.IO.File]::WriteAllText(..., New-Object System.Text.UTF8Encoding $false)` para gravar sem BOM.
- [ ] **Padrão a lembrar em qualquer substituição de texto via PowerShell:** sempre especificar `-Encoding utf8` explicitamente no `Get-Content -Raw`, não só no `Set-Content` — ler sem especificar a codificação corrompeu acentuação em 8 arquivos nesta sessão.

---

## Próximos passos

Fechar a Etapa 6: revisar `docs/00 - KANBAN.md` por completo (remover o item de Backlog que descrevia esta renomeação como "a executar", já que está em andamento/concluída), commitar este diário, e então avançar para a Etapa 7 — sincronizar as demais máquinas validadas (`git pull`, apagar `db.sqlite3` local, `migrate`, `createsuperuser`, `loaddata catalogo_inicial` em cada uma). Depois, abrir o Pull Request de `feature/rename-pessoas-cadastros` para `dev`.
