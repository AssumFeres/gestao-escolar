# Andamento do Projeto — 22

**Data:** 01/09/2026 (sessão curta, ~30 minutos, máquina do quartel)
**Branch:** `dev` (commit direto)
**Sessão dedicada a: discutir reuso de CRUD entre entidades, e implementar o primeiro CRUD independente real (Create de FormacaoDocente), como piloto da arquitetura descrita em `docs/21`.**

---

## Contexto

Sessão curta, deliberadamente pausável a qualquer momento (a pessoa responsável avisou de início que tinha só 30 minutos, mas que poderia continuar depois em outra máquina). Antes de programar, uma discussão conceitual sobre reuso de CRUD entre os cadastros do sistema (Pessoa, Disciplina, Turma, Módulo, e as entidades filhas como Formação).

---

## Discussão: dois tipos de reuso de CRUD, não um só

A pergunta inicial era se o CRUD é "uma coisa que se reaproveita entre Disciplina, Turma, Módulo". A resposta se dividiu em dois casos bem diferentes:

### Entidades "soltas" (Disciplina, Turma, Módulo)

Sem relação de dependência com outra entidade — reuso "de graça" via `CreateView`/`UpdateView`/`DeleteView`/`ListView` genéricas do Django. Poucas linhas por entidade (Model já existe, `ModelForm` simples, URLs, templates reaproveitando `base.html`). Não precisa de nenhuma abstração nova — o padrão genérico do próprio framework já resolve.

### Entidades "filhas de um pai" (Formação, Experiência, Histórico, Pendência, Capacidade)

Caso mais complexo, coberto pela especificação `docs/21`: essas entidades só existem presas a uma `Pessoa`/`AtribuicaoFuncao`/`DadosDocente`. O Django não resolve isso sozinho — é preciso garantir, no servidor, que o "pai" é resolvido pela URL (nunca por um campo enviado pelo navegador), e que o registro editado/excluído realmente pertence a esse pai. **Decisão explícita, para evitar abstração prematura:** não generalizar essa camada agora — implementar o piloto concreto (Formação) primeiro, e só depois de ter 2-3 casos reais extrair o que for genuinamente comum. Mesmo raciocínio de YAGNI já aplicado em outras decisões do projeto (`RequisitoContratacao`, `PendenciaCadastro`).

---

## Implementação: piloto do CRUD independente (só Create)

Primeira implementação concreta da arquitetura de `docs/21`, escopada para caber no tempo disponível: **só o "C" de CRUD**, para `FormacaoDocente`.

- **`FormacaoDocenteModelForm`** (novo, em `forms.py`) — `ModelForm` de verdade (diferente do `FormacaoDocenteForm` já existente, usado só no Formset do cadastro inicial). `dados_docente` fica de fora de `fields`, de propósito — não pode ser manipulado pelo POST.
- **`AdicionarFormacaoDocenteView`** (nova, em `views.py`) — `CreateView` genérica do Django. `dispatch()` resolve o `DadosDocente` "pai" a partir do `<int:pk>` da URL (nunca de um campo do formulário), `form_valid()` associa esse pai antes de salvar, `get_success_url()` volta para a tela de Requisitos do Docente.
- **URL nova:** `docente/<int:pk>/formacoes/nova/`, seguindo o mesmo padrão já usado para `requisitos/`.
- **Template novo:** `form_formacao.html` — simples, sem Formset, sem JavaScript nenhum de "+ Adicionar"/clone.

`python manage.py check` limpo, `pytest` — `29 passed` (nenhum teste existente afetado; a View nova ainda não tem cobertura automatizada própria).

**Testado manualmente com sucesso:** acessando a URL diretamente (`/cadastros/docente/<pk>/formacoes/nova/`), preenchendo o formulário e salvando — a Formação persistiu de verdade no banco (confirmado no Admin) e apareceu corretamente na tela de detalhe/Requisitos do Docente.

**Commit:** `b2e3cbb` — `feat: CRUD independente de FormacaoDocente (piloto docs/21), so Create por enquanto`.

---

## O que ficou faltando (para continuar em outra máquina)

- **Update e Delete** de `FormacaoDocente` — ainda não implementados, só o Create.
- **Link visível** na tela `preencher_requisitos_docente.html` apontando para a URL de adicionar Formação — hoje só é acessível digitando a URL manualmente. Precisa de uma pequena edição no template (fora do escopo desta sessão curta).
- **Listagem de Formações já cadastradas** na própria tela de Requisitos, para o usuário ver o que já existe antes de adicionar mais.
- **Testes automatizados** para a nova View/Form — nenhum ainda.
- **Replicar o padrão** para Experiência, Histórico, Pendência, Capacidade — só depois de fechar Update/Delete de Formação primeiro, validando o piloto por completo.

---

## Estado geral ao final desta sessão

| Item | Status |
|---|---|
| Discussão sobre reuso de CRUD (entidades soltas vs. filhas de um pai) | ✅ Esclarecida, decisão de não abstrair prematuramente registrada |
| CRUD independente de FormacaoDocente — Create | ✅ Implementado e testado manualmente |
| CRUD independente de FormacaoDocente — Update/Delete | ⏳ Não iniciado |
| Link/listagem na tela de Requisitos do Docente | ⏳ Não iniciado |
| Testes automatizados da View/Form nova | ⏳ Não iniciado |
| Testes automatizados | 29 passed (sem alteração) |

---

## Próximos passos

Continuar o piloto de Formação: Update (editar uma Formação já cadastrada) e Delete (excluir), depois adicionar o link e a listagem na tela de Requisitos. Só depois disso, considerar extrair a camada comum (resolução do pai pela URL + checagem de propriedade) para reaproveitar nas outras 4 entidades filhas.
