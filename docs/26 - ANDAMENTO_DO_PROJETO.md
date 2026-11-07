# Andamento do Projeto — 26

**Data:** 02/09/2026 (máquina do quartel)
**Branch:** `dev` (commits diretos)
**Sessão dedicada a: implementar Editar Pessoa (Update) e executar a Etapa B da consolidação de telas — eliminação de `preencher_requisitos_docente.html`, com o CRUD de Formação movido para `detalhe.html`.**

---

## Contexto

Continuação direta do diário 25. Antes de começar, a pessoa responsável reforçou uma sequência de trabalho a seguir (registrada aqui para referência):

1. **Editar Pessoa** (esta sessão)
2. Ajustar `form_pessoa.html` para incluir Requisitos de Contratação no cadastro inicial (todos exceto Discente)
3. Busca por CPF com reaproveitamento/edição de dados (reformulação do antigo item "FE 007 — Discente" do Kanban, generalizado para qualquer categoria — só faz sentido **depois** de Editar Pessoa estar pronto)
4. Auditoria dos campos nas 3 situações (Discente/Docente/Gestão), comparando contra as fichas oficiais (FE 007, FE 008, FOP 402)

Também foi confirmada explicitamente uma regra de negócio importante: **Pessoa nunca é excluída, só Create/Read/Update** — o item de Backlog "Excluir/inativar Pessoa" precisa ser corrigido para refletir isso (só inativar via o campo `ativo` já existente, nunca Delete de verdade).

---

## 1. Editar Pessoa (Update)

### Definição de escopo, antes de codar

O item original do Kanban dizia "reaproveita o Form já existente" (`CadastrarPessoaForm`) — mas esse Form mistura Pessoa + Funcao/AtribuicaoFuncao + campos de `DadosDiscente`. Pergunta de esclarecimento feita antes de implementar: Editar Pessoa deveria incluir os campos de `DadosDiscente` (Código de Matrícula ANAC, Passaporte, Contato de Emergência, Responsável legal)?

**Resposta e decisão de escopo:** não. Editar Pessoa cobre só os campos **comuns** da `Pessoa` em si (identificação + endereço). Ficam de fora, deliberadamente:
- **CPF** — imutável, é a chave da busca-ou-criar do cadastro inicial
- **Função/`AtribuicaoFuncao`** — item futuro próprio ("Edição de Funções")
- **Campos de `DadosDiscente`** — Discente ainda não tem nenhum CRUD próprio para isso; a pessoa responsável quer organizar isso visualmente numa etapa futura, com `fieldset`s aninhados por sub-grupo (Passaporte, Responsável legal, Contato de Emergência) — hoje "visualmente confuso" — **depois** da auditoria de campos (item 4 da sequência).

### Implementação

`EditarPessoaForm` (`ModelForm` novo, 26 campos comuns) + `EditarPessoaView` (mesmo padrão de `EditarRequisitoContratacaoView` — não é lista repetível, só Editar direto no objeto, sem `dispatch()` resolvendo "pai"). Botão "Editar" adicionado ao lado do nome, no topo de `detalhe.html`.

`pytest` — `29 passed`. Testado manualmente: edição funcionando, CPF corretamente não editável (só exibido como texto no popup).

---

## 2. Etapa B: eliminação de `preencher_requisitos_docente.html`

Durante o teste de regressão da sessão, a pessoa responsável notou que a seção "Formação" tinha sumido de `detalhe.html` — não era uma regressão: Formação nunca teve botões em `detalhe.html`, o CRUD sempre viveu só na tela de Requisitos (decisão documentada no diário 25 como "Etapa B, não executada ainda"). A pessoa responsável perguntou se valia a pena fazer esse ajuste agora, e confirmou que a tela antiga **não era referenciada em nenhum outro lugar do sistema** — condição necessária para remover com segurança.

### Execução

- **`detalhe.html`**: seção "Formação" reestruturada no mesmo padrão das outras entidades (`fieldset` por `AtribuicaoFuncao` de categoria Docente, com botões Adicionar/Editar/Excluir).
- **3 Views de Formação** (`Adicionar`/`Editar`/`ExcluirFormacaoDocenteView`): `get_success_url()` trocado de `preencher-requisitos-docente` para `detalhe-pessoa`.
- **`NovoCadastroPessoaView.post()`**: simplificado — sempre redireciona para `detalhe-pessoa`, independente da categoria (o ramo especial para Docente foi removido).
- **Removidos por completo**: `PreencherRequisitosDocenteView`, a rota `docente/<pk>/requisitos/`, e o arquivo `preencher_requisitos_docente.html`.

**Nota sobre o padrão da sessão:** essa foi a primeira mudança da série que é predominantemente **remoção**, não adição — diferente de tudo que vínhamos fazendo até aqui. Risco reconhecido e aceito: depois de apagar, não há mais como acessar a URL antiga por engano; isso é o comportamento correto e esperado, confirmado no Teste 4 (acessar a URL antiga retorna `404`).

`pytest` — `29 passed`. Testado manualmente com sucesso, em 5 frentes:
1. Formação completa (Adicionar/Editar/Excluir) funcionando em `detalhe.html`, para Docente
2. Seção ausente corretamente para Discente/Gestão
3. Fluxo de cadastro de Docente cai direto em `detalhe-pessoa` (não mais numa tela de Requisitos)
4. URL antiga (`/cadastros/docente/<pk>/requisitos/`) retorna `404`, confirmando a remoção de verdade
5. Regressão geral: Editar Pessoa, Requisitos de Contratação, Pendências, Experiência, Vínculo Formal — tudo continua funcionando

**Commit:** `267ba49` — `feat: Editar Pessoa (Update) + Etapa B - elimina preencher_requisitos_docente.html`.

---

## `detalhe.html` — estado final como "centro de comando" único

Com a Etapa B fechada, `detalhe.html` passa a concentrar **tudo** sobre uma Pessoa, para qualquer categoria: dados básicos (com Editar), Requisitos de Contratação (Docente/Gestão), Pendências (universal), Formação (Docente), Experiência (Gestão), Histórico de Vínculo Formal (Docente/Gestão) — todos via popup, mesmo `ModalCrudMixin`/`modal-crud.js`. Não existe mais nenhuma tela satélite fora dessa.

---

## Estado geral ao final desta sessão

| Item | Status |
|---|---|
| Editar Pessoa (Update) | ✅ Implementado e testado |
| Etapa B (eliminação de `preencher_requisitos_docente.html`) | ✅ Executada e testada |
| `detalhe.html` como centro de comando único da Pessoa | ✅ Consolidado |
| Item 2 da sequência (Requisitos de Contratação no `form_pessoa.html`) | ⏳ Próximo passo |
| Item 3 (busca por CPF, generalizada) | ⏳ Depois do item 2 |
| Item 4 (auditoria de campos FE 007/FE 008/FOP 402) | ⏳ Depois do item 3 |
| Testes automatizados | 29 passed (sem alteração) |

---

## Itens novos/corrigidos de Backlog identificados nesta sessão

- [ ] **Corrigir item "Excluir/inativar Pessoa" no Kanban** — Pessoa nunca é excluída de verdade, regra de negócio confirmada em 02/09/2026; o item deve ser reformulado para "Inativar Pessoa" (via campo `ativo` já existente no Model).
- [ ] **Reformular o item "Tela de cadastro (FE 007) — Discente"** no Kanban — não é mais uma tela separada de Discente; é a capacidade geral de "buscar Pessoa por CPF e reaproveitar/editar dados", válida para qualquer categoria. Depende de Editar Pessoa estar pronto (✅, feito nesta sessão) antes de poder ser implementada de verdade.
- [ ] **Auditar os campos de "Tela de cadastro (FE 008) — Docente" e "Tela de cadastro (FOP 402) — Gestão"** contra o formulário único atual (`form_pessoa.html`) antes de marcá-los como concluídos — a arquitetura evoluiu de "3 telas separadas" para "1 tela única com JS controlando visibilidade por categoria", e pode ter havido perda silenciosa de algum campo nessa evolução. Adiado deliberadamente para depois dos itens 2 e 3 da sequência.
- [ ] **Reorganização visual de `detalhe.html`** com `fieldset`s aninhados para os sub-grupos de `DadosDiscente` (Passaporte, Responsável legal, Contato de Emergência) — adiada para depois da auditoria de campos, junto de uma "organização da visualização de Pessoas" mais ampla, mencionada pela pessoa responsável.
- [ ] Testes automatizados para `EditarPessoaView` — nenhum ainda.

---

## Próximos passos

Seguir a sequência já definida: ajustar `form_pessoa.html` para incluir os Requisitos de Contratação no cadastro inicial (todos exceto Discente); depois, implementar a busca por CPF com reaproveitamento/edição de dados, generalizada para qualquer categoria; por fim, a auditoria de campos nas 3 situações antes de fechar os itens de Backlog correspondentes.
