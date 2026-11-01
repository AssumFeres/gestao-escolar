# Plano de Migração — Renomear app `pessoas` para `cadastros`

**Origem da decisão:** registrado no Backlog desde a sessão de redesenho arquitetural (`docs/06 - ANDAMENTO_DO_PROJETO.md`) — o app sempre misturou catálogo (`Funcao`, `Disciplina`, `VinculoFormal`) com cadastro de fato (`Pessoa`, `AtribuicaoFuncao`), e o nome `cadastros` reflete isso com mais precisão. O conceito de "pré-cadastro" como app/camada separada morre — tudo continua junto num módulo só, só com o nome corrigido.

**Status:** não iniciado.

**Pré-requisito já cumprido:** a migração `Vinculo`→`Funcao` foi concluída e mesclada em `dev` antes de começar esta — evita empilhar dois refactors grandes ao mesmo tempo (risco já observado nas Etapas 5a/6 da migração anterior).

---

## Decisão de abordagem: reset do banco local, não preservação de histórico

Renomear um app Django amarra várias coisas ao nome, não só a pasta: `INSTALLED_APPS`, o `AppConfig` interno, o prefixo das tabelas no banco (`pessoas_pessoa` → precisaria virar `cadastros_pessoa`), o histórico de migrations (a tabela `django_migrations` registra cada migration sob o nome do app antigo), todos os imports Python, e os caminhos de template/estático.

**Decisão confirmada (30/08/2026):** apagar o banco atual e as migrations antigas, recriar do zero sob o nome `cadastros`.

**Como ainda não existe dado real de produção** (só testes, banco local SQLite por máquina, nenhum aluno/professor real cadastrado) — a abordagem escolhida é a mais simples e menos arriscada: **apagar as migrations antigas e o banco local de cada máquina, recriar do zero já sob o nome `cadastros`**, em vez de tentar preservar/renomear o histórico de migrations entre apps (tecnicamente possível, mas trabalhoso e arriscado, sem necessidade real aqui).

**⚠️ Esta abordagem deixa de ser válida no dia em que houver dado real cadastrado** — a partir daí, qualquer renomeação de app precisaria de uma estratégia que preserve dados (fora do escopo deste plano).

---

## Antes de começar

- [ ] Confirmar com o grupo (se houver mais gente ativa no projeto) que não há dado real a perder em nenhuma das 5 máquinas validadas
- [ ] Criar uma branch nova a partir de `dev`: `git checkout -b feature/rename-pessoas-cadastros`
- [ ] Confirmar que `pytest` passa antes de qualquer mudança (ponto de partida limpo)

---

## Etapa 1 — Renomear a pasta e os caminhos internos

- [ ] Renomear a pasta `pessoas/` para `cadastros/`
- [ ] Dentro de `cadastros/`, renomear `pessoas/templates/pessoas/` para `cadastros/templates/cadastros/`
- [ ] Renomear `pessoas/static/pessoas/` para `cadastros/static/cadastros/`
- [ ] Em `cadastros/apps.py`, atualizar `name = 'pessoas'` para `name = 'cadastros'` (e o `verbose_name`, se houver)
- [ ] Em cada Template View (`ListaPessoasView`, `DetalhePessoaView`, `NovoCadastroPessoaView`, `PreencherRequisitosDocenteView`), atualizar `template_name = 'pessoas/...'` para `'cadastros/...'`
- [ ] Em `form_pessoa.html` e demais templates, atualizar `{% static 'pessoas/js/...' %}` para `{% static 'cadastros/js/...' %}`

## Etapa 2 — Atualizar todos os imports Python

- [ ] Buscar (Ctrl+Shift+F no VS Code, ou `grep -r "from pessoas" .`) todas as ocorrências de `from pessoas.` e `import pessoas` no projeto inteiro — não só dentro da própria pasta, mas em `config/urls.py`, `config/settings.py`, e nos próprios arquivos internos do app (`views.py` importando de `.models`, isso não muda, mas imports absolutos tipo `from pessoas.models import X` dentro de `tests/`, sim)
- [ ] Atualizar cada ocorrência para `from cadastros.` / `import cadastros`
- [ ] Atenção especial: `infraestrutura/` não referencia `pessoas`, então não precisa de mudança ali

## Etapa 3 — Atualizar configuração do projeto

- [x] `config/settings.py`: em `INSTALLED_APPS`, trocar `'pessoas'` por `'cadastros'`
- [x] `config/urls.py`: trocar `include('pessoas.urls')` e `include('pessoas.api_urls')` por `include('cadastros.urls')`/`include('cadastros.api_urls')`; **decisão confirmada (30/08/2026): a URL pública também muda**, de `path('pessoas/', ...)` para `path('cadastros/', ...)` — coerente com o fato de "Pessoa" ser só uma das entidades cadastradas ali (Função, Disciplina, VinculoFormal também), não faria sentido a URL continuar amarrada só a "pessoas"

## Etapa 4 — Resetar o banco local e o histórico de migrations

- [ ] Apagar a pasta `cadastros/migrations/` inteira (as 18 migrations antigas, sob o nome `pessoas`, não fazem mais sentido)
- [ ] Recriar `cadastros/migrations/__init__.py` (pasta vazia, só com o `__init__.py`, pronta para gerar migrations novas)
- [ ] Apagar `db.sqlite3` local
- [ ] Gerar a migration inicial do zero: `python manage.py makemigrations cadastros`
- [ ] Aplicar: `python manage.py migrate`
- [ ] Recriar o superusuário: `python manage.py createsuperuser`
- [ ] Recarregar o catálogo: `python manage.py loaddata catalogo_inicial` (confirmar que o caminho da fixture, `cadastros/fixtures/catalogo_inicial.json`, foi movido junto na Etapa 1)

## Etapa 5 — Testar

- [ ] `pytest` — todos os testes devem passar sem nenhuma alteração de conteúdo (só os imports foram ajustados na Etapa 2); se algum teste falhar, é sinal de um import ou caminho esquecido
- [ ] Testar manualmente pelo navegador: lista, detalhe, cadastro completo (Discente/Docente/Gestão), Admin
- [ ] Conferir o Admin: os nomes das seções continuam corretos (não deveriam mudar, já que `verbose_name` dos Models não foi alterado, só o app)

## Etapa 6 — Documentação e commit

- [ ] Atualizar `docs/00 - KANBAN.md`: remover o item de Backlog sobre essa renomeação (concluído), atualizar qualquer menção a `pessoas/` na documentação viva
- [ ] Escrever diário da sessão (`docs/17 - ANDAMENTO_DO_PROJETO.md` ou próximo número disponível)
- [ ] Commit único ou poucos commits pequenos (ex: `refactor: renomeia app pessoas para cadastros`, depois `chore: reseta migrations e banco local`)
- [ ] Push, abrir Pull Request para `dev`

## Etapa 7 — Sincronizar as demais máquinas

Como o banco local de cada máquina será resetado, isso precisa ser comunicado e replicado manualmente:

- [ ] Em cada uma das 5 máquinas validadas, depois do merge: `git pull`, apagar `db.sqlite3` local, `python manage.py migrate`, `python manage.py createsuperuser`, `python manage.py loaddata catalogo_inicial`
- [ ] Atualizar `docs/00 - GUIA_GIT_E_DJANGO.md` se o roteiro de sincronização entre máquinas mudar de alguma forma permanente por causa disso

---

## Riscos e pontos de atenção

- **Import esquecido:** a busca por `from pessoas` na Etapa 2 precisa ser exaustiva — um import esquecido gera `ModuleNotFoundError` só na hora de rodar, não em tempo de "escrita". Rodar `python manage.py check` logo após a Etapa 2/3, antes mesmo de mexer no banco, ajuda a pegar isso cedo.
- **Caminho de template/estático esquecido:** diferente de import Python (que quebra alto e claro), um `{% static %}` ou `template_name` apontando para o caminho antigo falha silenciosamente ou com erro 404 mais discreto — checar visualmente cada tela.
- **Nome de tabela no Admin:** por padrão, o Django deriva o nome de exibição no Admin do nome do Model, não do app — não deveria mudar nada visualmente ali, mas vale conferir.
- **Coordenação com o grupo:** se alguém mais estiver com uma branch aberta em cima da `pessoas` antiga no momento do merge desta renomeação, vai ter conflito significativo — bom avisar antes de mesclar.
