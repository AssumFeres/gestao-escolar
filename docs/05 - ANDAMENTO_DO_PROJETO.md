# Andamento do Projeto — 05

**Data:** 23-24/08/2026
**Branch:** `dev`
**Commits desta etapa:** `9b9a2cd`, `3a64172`

---

## O que foi feito

### 1. Especificação de Formação do Docente (FE 008)

Analisado o formulário institucional **FE 008 — Formulário de Cadastro de Instrutor e Atribuição de Disciplina** (Rev. 01, 24/06/2026). Mapeadas as seções relevantes ao domínio `pessoas` e discutidas três decisões de modelagem:

- **Tabela única `FormacaoDocente`** (com campo `tipo_formacao` enum) para Graduação, Formação Profissional e Aperfeiçoamento Profissional — as três seções do formulário têm estrutura idêntica, então uma tabela + enum evita duplicação (DRY), diferente do caso `Vinculo` (onde os subtipos têm campos genuinamente diferentes).
- **Requisitos de Contratação como campos diretos em `VinculoDocente`**, não como catálogo genérico — decisão explicitamente guiada pelo princípio **YAGNI**: são apenas 2 critérios fixos hoje, sem sinal de crescimento; um catálogo (`RequisitoContratacao` + tabela associativa) seria over-engineering nesse momento.
- **`Capacidade` ganha campo `formacao_comprobatoria`** (FK para `FormacaoDocente`), fechando o mapeamento da Seção 7 do formulário ("Disciplina Habilitado a Ministrar"), que já correspondia ao Model existente.

Especificação completa (com esboços de código) registrada num capítulo próprio no final do `docs/00 - KANBAN.md` ("📐 Especificações Detalhadas"), separado da entrada sucinta no Backlog — para não implementar agora, mas não perder o raciocínio quando chegar a hora.

### 2. Sincronização de um quinto ambiente (notebook)

Clone completo do zero num notebook novo. Dois obstáculos encontrados e resolvidos:
- `git status` inicial retornou `fatal: not a git repository` — o comando estava sendo rodado na pasta **pai** do clone, não na pasta do repositório em si.
- `python manage.py migrate` nunca tinha sido rodado nesse notebook — resultando em `OperationalError: no such table: pessoas_pessoa` na primeira tentativa de uso real do formulário. Resolvido rodando `migrate` antes de continuar.

### 3. Formulário de cadastro de Pessoa (Template View com POST)

- `pessoas/forms.py`: `CadastrarPessoaForm`, espelhando os campos do `CadastrarPessoaInputSerializer` já existente na API.
- `NovoCadastroPessoaView`: `GET` renderiza o formulário vazio; `POST` valida, chama `CadastrarPessoaComVinculoService` (o mesmo Service já usado pela API — nenhuma regra de negócio duplicada) e redireciona para o detalhe da Pessoa criada.
- `pessoas/templates/pessoas/form_pessoa.html`: template do formulário.
- Rota `pessoas/novo/` adicionada, com atenção à ordem (precisa vir antes de `<int:pk>/`, senão o Django tentaria interpretar "novo" como ID).

### 4. JavaScript — busca automática de CEP no formulário

`pessoas/static/pessoas/js/buscar-cep.js`: ao sair do campo CEP (evento `blur`), dispara `fetch()` contra o endpoint `GET /api/pessoas/cep/<cep>/` já existente e testado, preenchendo Logradouro, Bairro, Cidade e UF automaticamente. Primeiro JavaScript funcional do projeto, cobrindo o requisito "script web" do tema do PI com propósito de negócio real, não decorativo.

---

## Erros e correções desta etapa

| O que aconteceu | Causa | Como foi resolvido |
|---|---|---|
| `fatal: not a git repository` no notebook | Comando rodado na pasta pai do clone, não na raiz do repositório | Navegado para dentro de `gestao-escolar/` |
| `OperationalError: no such table: pessoas_pessoa` | `migrate` nunca executado nesse notebook | `python manage.py migrate` |
| Imports duplicados em `views.py` (`django.shortcuts`, `.models`, `rest_framework` repetidos) | Edições sucessivas colando blocos de import sem checar o que já existia | Consolidado num único bloco por origem (Django → DRF → módulos locais) |
| `{% load static %}` e a tag `<script>` "sumiam" do `form_pessoa.html` mesmo após edição no VSCode | Edições não persistindo corretamente (causa exata não confirmada — possível cache do editor ou salvamento incompleto) | Arquivo apagado (`Remove-Item`) e recriado do zero via `Set-Content` com array de linhas, eliminando qualquer resquício |
| `TemplateSyntaxError: {% extends %} must be the first tag` | `{% load static %}` foi colocado *antes* de `{% extends %}` — regra do Django é `extends` sempre ser a primeira tag do arquivo, sem exceção | Invertida a ordem: `extends` na linha 1, `load static` na linha 2 |
| Conteúdo duplicado (`<form>` repetido duas vezes) após um `Set-Content` | Possível problema de buffer/cache do PowerShell nesse notebook específico ao sobrescrever arquivo existente | Arquivo removido fisicamente antes de recriar, em vez de sobrescrever diretamente |

---

## Decisão de processo: revisão honesta do escopo "concluído"

Ao final da sessão, foi identificado que classificar o módulo `pessoas` como "pronto" seria impreciso. Levantamento feito:

- **Pessoa:** Create (parcial) e Read prontos; Update e Delete ainda não implementados via interface.
- **Vínculo:** só é possível criar o primeiro vínculo (junto com a Pessoa); não há tela para adicionar segundo vínculo, editar ou encerrar um vínculo existente.
- **FuncaoGestao, Habilitacao, Disciplina:** nenhuma tela própria — só acessíveis via Django Admin.
- **Associar Habilitação a Coordenador:** funciona via API (testado e validado dias atrás), mas não existe tela HTML para uso real por um usuário do sistema.

O Kanban foi reestruturado para refletir isso com precisão: a seção "A Fazer" ganhou um checklist numerado e ordenado por prioridade (9 itens, do menor/mais simples ao mais dependente), deixando claro que configurar PostgreSQL/deploy é prematuro antes de fechar esse CRUD.

---

## Decisão de continuidade da conversa

Dado o tamanho acumulado desta conversa (~5 dias de sessões, desde a modelagem inicial até aqui), foi decidido encerrar este contexto e iniciar um novo, usando os arquivos versionados em `docs/` (arquitetura, diários numerados, Kanban) como fonte de continuidade — não o histórico de chat. Um prompt de abertura para o próximo contexto foi preparado separadamente (`PROMPT_PROXIMO_CONTEXTO.md`).

---

## Estado geral ao final desta etapa

| Camada | Status |
|---|---|
| Models | 9 entidades, completos para o escopo atual |
| Services | 3 de 3, testados (7 testes) |
| API (DRF) | 3 de 3 endpoints funcionando |
| Template Views | 3 (lista, detalhe, cadastro de Pessoa) |
| JavaScript | 1 script funcional (busca de CEP) |
| CRUD do módulo Pessoas | Parcial — checklist detalhado no Kanban |
| Ambientes validados | 5 máquinas |

---

## Próximos passos

Seguir o checklist numerado da seção "A Fazer — CRUD completo do módulo Pessoas" no `docs/00 - KANBAN.md`, começando pelo item 1 (Editar Pessoa).
