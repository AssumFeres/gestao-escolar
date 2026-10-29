# Andamento do Projeto — 18

**Data:** 31/08/2026
**Branch:** `dev` (commits diretos, sem branch de feature — decisão de fluxo de trabalho confirmada nesta sessão, ver abaixo)
**Sessão dedicada a: mesclar o PR da renomeação `pessoas`→`cadastros`, investigar uma divergência inesperada no `dev` remoto, e corrigir 2 bugs pré-existentes descobertos em teste manual antes de iniciar o CRUD completo.**

---

## Contexto

Sessão de continuação direta da renomeação `pessoas`→`cadastros` (Etapas 1-6 fechadas em `docs/17 - ANDAMENTO_DO_PROJETO.md`). Objetivo inicial era só mesclar o PR e seguir para o CRUD do módulo Cadastros — mas o merge revelou uma surpresa que precisou de investigação antes de prosseguir.

---

## Merge do PR #2 e descoberta: `dev` remoto estava mais atrasado do que o esperado

PR **#2 — "Renomeia app pessoas para cadastros"** aberto e mesclado no GitHub. Ao rodar `git pull origin dev` localmente depois do merge, o resultado veio muito maior do que o esperado para uma renomeação de app: **44 commits, 57 arquivos alterados**, incluindo criação de `base.css`, `base.html`, `logo-emca.png`, e um `pessoas/models.py` de só 169 linhas sendo apagado (bem menor que as ~368 linhas do `models.py` real, já com toda a migração `Funcao`).

**Diagnóstico:** o PR **#1 — "Migração Vinculo/FuncaoGestao/Habilitacao para Funcao/AtribuicaoFuncao"** nunca tinha sido de fato mesclado no `origin/dev` até então — apesar dos diários 06 a 15 registrarem a migração como "completa" e o Kanban como "falta só abrir o PR", o `dev` remoto ainda estava no estado *anterior* a toda essa migração. O trabalho existia e estava correto localmente (testado, `pytest` verde), só não tinha chegado ao GitHub. Como a branch `feature/rename-pessoas-cadastros` foi criada a partir do `dev` **local** (já à frente do remoto), ela carregou consigo, sem intenção, todo o conteúdo da migração anterior — e o merge do PR #2 trouxe as duas migrações de uma vez para `origin/dev`.

**Verificação de segurança, antes de prosseguir:**
- `python manage.py check` → limpo
- `pytest` → `18 passed`
- `https://github.com/AssumFeres/gestao-escolar/pulls?q=is%3Apr` → **0 Open, 2 Closed**, ambos os PRs (#1 e #2) mesclados, nenhum pendente ou duplicado

Nenhuma inconsistência real encontrada — só um histórico de merge mais "gordo" do que o normal, sem conflito nem duplicação de dado.

**Decisão registrada:** as branches `feature/refatoracao-funcao` e `feature/rename-pessoas-cadastros` **não serão apagadas do remoto**, mesmo já mescladas — decisão deliberada da pessoa responsável, para preservar evidência verificável da evolução real do projeto (histórico de commits e branches), complementar aos diários escritos, útil para avaliação do professor no PI.

---

## Decisão de fluxo de trabalho: commits diretos em `dev`, sem branch para mudanças pequenas

Depois de discutir o que `git checkout -b` faz e por que a sugestão de branch curta tinha sido feita, a pessoa responsável decidiu que, daqui em diante, prefere commitar e versionar **direto na `dev`** para este projeto, em vez de abrir uma branch nova a cada correção pequena — julgando o overhead de gerenciar múltiplas branches desnecessário para o ritmo de trabalho solo. Rede de segurança considerada suficiente: commits pequenos e frequentes permitem reverter (`git revert`/`git reset`) sem precisar de branch. Esta preferência foi registrada para aplicação nas próximas sessões.

---

## Bug 1 — `codigo_matricula_anac` salvo como string vazia em vez de `None`

Já registrado no Backlog desde a sessão anterior (descoberto em teste manual, não corrigido de propósito para manter o escopo da renomeação limpo). Reproduzido de novo nesta sessão, agora na máquina da escola, com o erro real de tela (`IntegrityError` em `/cadastros/novo/`).

**Causa:** `NovoCadastroPessoaView` montava `dados_extensao["codigo_matricula_anac"]` com `dados.get("codigo_matricula_anac", "")` — mesmo padrão de bug já corrigido para `registro_matricula`/`registro_aluno`/`codigo_anac` nas Etapas 7.4/9 da migração anterior, mas nunca replicado para este campo específico do bloco Discente.

**Correção:** trocado por `dados.get("codigo_matricula_anac") or None`.

**Teste novo:** `cadastros/tests/test_views_novo_cadastro.py` — primeiro teste automatizado do projeto para uma Template View via `Client` de teste do Django (não só `Service`), simulando o POST real do formulário HTML com dois Discentes cadastrados em sequência, ambos com o campo em branco. Payload do teste construído a partir do payload real capturado no erro de tela, garantindo fidelidade ao formulário de verdade.

**Commit:** `dba6fa4` — `fix: corrige codigo_matricula_anac vazio salvo como string em vez de None`.

---

## Bug 2 — Formsets aceitavam linha parcialmente preenchida sem validar campos obrigatórios

Também já registrado no Backlog (Formset de Formação, `ano_conclusao` não validado). Ao investigar `forms.py`, ficou claro que o problema é mais amplo do que só esse campo: **todos** os campos de `FormacaoDocenteForm` são `required=False` (necessário para a linha `extra=1` vazia do Formset passar sem erro), o que também permite qualquer combinação **parcial** passar — não só "Curso preenchido, Ano vazio", mas qualquer subconjunto.

**Decisão de escopo:** em vez de corrigir só o campo relatado, a pessoa responsável optou por aplicar o mesmo padrão de validação aos 3 Formsets afetados de uma vez (`FormacaoDocenteForm`, `ExperienciaProfissionalForm`, `HistoricoVinculoFormalForm`), evitando retrabalho de descobrir o mesmo bug de novo em cada um separadamente. `PendenciaCadastroForm` não precisou de correção: seu único outro campo (`descricao`) já é `blank=True` de verdade no Model, sem combinação parcial inválida possível.

**Correção:** adicionado `clean()` em cada um dos 3 Forms, usando o mesmo campo "sinal" que `views.py::_CAMPO_PREENCHIDO` já usa para decidir se uma linha foi preenchida de verdade (`curso`, `organizacao`, `vinculo_formal`, respectivamente) — se o sinal estiver preenchido, os demais campos obrigatórios do Model correspondente (verificados um a um contra os `models.py` reais antes de escrever o código) passam a ser exigidos também, com mensagem de erro no campo certo.

**Teste novo:** `cadastros/tests/test_forms_formsets_parciais.py` — 10 testes cobrindo, para cada um dos 3 Forms: linha totalmente vazia (válida, não pode quebrar o caso `extra=1`), linha parcial (inválida, erro no campo certo), linha completa (válida). Testado no nível de `Form`, mais direto e rápido que simular o POST completo da View.

**Commit:** `b3c1e89` — `fix: valida campos obrigatorios de linha parcialmente preenchida nos Formsets`.

---

## Ideia nova registrada, não implementada: popup para os campos-tabela no formulário de cadastro

A pessoa responsável levantou a ideia de que os blocos repetíveis do formulário de cadastro (Formação, Experiência Profissional, Histórico de Vínculo Formal, Pendências) apareçam como um único botão que abre um popup para o cadastro, em vez de ocupar espaço fixo na tela — deixando a ficha de cadastro mais leve. **Decisão: não implementar agora** — é trabalho de frontend (JavaScript + modal) desacoplado dos bugfixes desta sessão e do CRUD que vem a seguir; registrado no Backlog para quando fizer sentido encaixar. Distinto do item de Backlog já existente sobre a **tela de detalhe** (que trata de exibição/leitura, não de cadastro).

---

## Estado geral ao final desta sessão

| Item | Status |
|---|---|
| PR #1 (migração Funcao) | ✅ Mesclado em `dev` (confirmado nesta sessão, já estava fechado antes) |
| PR #2 (renomeação pessoas→cadastros) | ✅ Mesclado em `dev` nesta sessão |
| `dev` local e remoto sincronizados, `check`/`pytest` limpos | ✅ |
| Branches de feature preservadas no remoto (decisão deliberada) | ✅ |
| Bug 1 — `codigo_matricula_anac` vazio | ✅ Corrigido e testado (`dba6fa4`) |
| Bug 2 — Formsets sem validação de linha parcial (3 Forms) | ✅ Corrigido e testado (`b3c1e89`) |
| Ideia de popup para campos-tabela no cadastro | 📝 Registrada no Backlog, não implementada |
| Testes automatizados | 29 passed |
| Limpeza geral do Kanban (reorganização, não só atualização pontual) | ⏳ Adiada para quando fizer sentido — decisão explícita da pessoa responsável |

---

## Próximos passos

Retomar a lista "A Fazer — CRUD completo do módulo Cadastros" (editar Pessoa, telas de cadastro por categoria FE 007/008/FOP 402, encerrar/editar Atribuição de Função, etc.), agora com a base de app renomeada e os 2 bugs de formulário resolvidos. Etapa 7 do plano `docs/16` (sincronizar as demais máquinas) segue sendo aplicada oportunisticamente — a máquina da escola já está sincronizada, como evidenciado pelo próprio teste manual desta sessão.
