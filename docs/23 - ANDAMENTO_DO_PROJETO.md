# Andamento do Projeto — 23

**Data:** 01-02/09/2026 (sessão iniciada na máquina da escola, concluída na máquina de casa)
**Branch:** `dev` (commits diretos)
**Sessão dedicada a: implementar o CRUD de `HistoricoVinculoFormal` (Adicionar/Encerrar) via popup, generalizando o mecanismo de modal já criado para Formação — e corrigir um incidente real de commit desatualizado descoberto só no teste manual.**

---

## Contexto

Continuação direta da sessão anterior (diário 22), que fechou o piloto de `FormacaoDocente` (só Create) na máquina do quartel. Esta sessão, iniciada na máquina da escola, tinha como objetivo original continuar a ordem já definida: link + listagem (já feitos), Update, Delete, testes — mas evoluiu para um escopo maior depois de uma conversa sobre o fluxo de edição "final" do sistema.

---

## Discussão de fluxo de navegação, antes de codar

A pessoa responsável levantou a pergunta de como o usuário chegaria à tela de gerenciar Formação, já que hoje só existem dois caminhos (redirecionamento automático pós-cadastro de Docente, ou saber a URL de cor) — nenhum partindo do fluxo natural `/cadastros/` → detalhe da Pessoa. Isso evoluiu para uma reflexão mais ampla sobre onde cada CRUD relacionado deveria "morar" na navegação.

**Decisão tomada:** em vez de criar uma tela "hub" nova de edição, reaproveitar as tabelas de leitura **já existentes** na tela de detalhe da Pessoa (Formação, Capacidades, Experiência, Histórico de Vínculo Formal — adicionadas desde o diário 15), plugando botões de Adicionar/Editar/Encerrar diretamente nelas via o mesmo mecanismo de popup. Isso converge com um item de Backlog já registrado ("Transformar as tabelas... em botão que abre popup").

### Pivot descartado: encerramento de `AtribuicaoFuncao` para Discente

A conversa também levantou a possibilidade de implementar, na mesma sessão, o encerramento de `AtribuicaoFuncao` para Discente (motivo: Transferido/Reprovado/Aprovado/Matrícula Excluída) e dois campos novos ("Ata de Início/Término de Vínculo"). Depois de esclarecer que são conceitos de dados **diferentes e não relacionados no código** (`AtribuicaoFuncao` é o vínculo com a escola; `HistoricoVinculoFormal` é o vínculo contratual, filho de uma `AtribuicaoFuncao` de Docente/Gestão — nunca de Discente), a pessoa responsável decidiu manter o foco no Histórico de Vínculo Formal e deixar o encerramento de Discente para a próxima etapa, evitando misturar dois pivots na mesma sessão.

---

## Implementação: CRUD de `HistoricoVinculoFormal` (Adicionar + Encerrar)

### Regra de negócio confirmada: nunca há Delete, só Encerramento

A pessoa responsável esclareceu que um período de Vínculo Formal nunca é excluído — só encerrado (preenchendo `data_fim`), com um campo `observacao` novo para registrar contexto ou correção de erro de cadastro.

- **Migration `0003`**: campo `observacao` (`TextField`, `blank=True`) adicionado a `HistoricoVinculoFormal`.

  **Incidente durante a edição manual:** ao colar o trecho no `models.py`, a linha `data_inicio` ficou com indentação incorreta (8 espaços em vez de 4), causando `IndentationError` ao rodar `makemigrations`. Diagnosticado mostrando as linhas exatas com números, corrigido substituindo só a linha afetada via array de linhas do PowerShell (mais preciso que um `-replace` textual nesse caso).

- **2 Forms novos**: `HistoricoVinculoFormalModelForm` (Adicionar — todos os campos) e `EncerrarHistoricoVinculoFormalForm` (Encerrar — só `data_fim` + `observacao`, nunca reabre `vinculo_formal`/`data_inicio`).
- **2 Views novas**: `AdicionarHistoricoVinculoFormalView` (`CreateView`, `AtribuicaoFuncao` pai resolvido pela URL) e `EncerrarHistoricoVinculoFormalView` (`UpdateView` restrita ao Form de encerramento).
- **`ModalCrudMixin` generalizado**: `template_fragmento` deixou de ser fixo em Formação e passou a ser obrigatório por subclasse — permitindo reaproveitar o mesmo mecanismo de popup para qualquer entidade nova.
- **JS generalizado**: `modal-formacao.js` renomeado para `modal-crud.js`, com IDs/classes genéricos (`modal-crud-overlay`, `form-modal-crud`) em vez de específicos de Formação.
- **`detalhe.html`**: botões "+ Adicionar Vínculo" e "Encerrar" (só quando `data_fim` ainda está vazio) plugados na tabela de Histórico de Vínculo Formal já existente, visíveis só para Docente/Gestão (`atribuicao.funcao.categoria != 'DISCENTE'`).

**Commit inicial:** `614f9c3` — marcado deliberadamente com prefixo `wip:`, sinalizando "não testado ainda", seguindo o mesmo cuidado do diário 14.

---

## Retomada em outra máquina: 3 bugs reais encontrados no teste manual

### Bug 1 — "+ Adicionar Formação" parou de funcionar

**Sintoma:** nada acontecia ao clicar (popup nem abria). **Causa raiz, descoberta com `git show HEAD:...`:** o arquivo `preencher_requisitos_docente.html` commitado em `614f9c3` continha a versão **antiga**, ainda referenciando `modal-formacao.js` — um arquivo que já tinha sido apagado do repositório na mesma sessão. O erro no Console do navegador (`404 modal-formacao.js`) confirmou exatamente isso.

**Lição prática:** o arquivo foi editado corretamente durante a sessão (confirmado visualmente antes do commit), mas por algum motivo a versão que efetivamente foi staged/commitada não refletia a edição mais recente — provavelmente um arquivo salvo em duplicidade ou um `git add` executado antes da última substituição de conteúdo. Reforça a importância de sempre confirmar com `Select-String`/`git diff` logo antes do commit, não só logo depois de editar.

### Bug 2 — Campo de data sem calendário

`HistoricoVinculoFormalModelForm` e `EncerrarHistoricoVinculoFormalForm` não especificavam `widget=forms.DateInput(attrs={'type': 'date'})` para os campos de data — diferente de todos os outros Forms do projeto, que sempre usam esse padrão. Sem isso, o Django usa um `<input type="text">` simples, sem o seletor de calendário do navegador.

### Bug 3 — Popup menor que o campo de Observação

O `<textarea>` de `observacao` usava o tamanho padrão do navegador (baseado no atributo `cols`), maior que a largura da caixa do popup (`max-width: 600px`), fazendo o conteúdo vazar visualmente para fora da caixa.

**Correção dos bugs 2 e 3:** widgets explícitos nos dois Forms — `forms.DateInput(attrs={'type': 'date'})` para as datas, e `forms.Textarea(attrs={'rows': 3, 'style': 'width:100%; box-sizing:border-box;'})` para a observação.

**Commit da correção:** `a91685d` — `fix: corrige arquivo desatualizado e widgets de data/textarea do Historico de Vinculo`.

---

## Testes finais — todos os 4 fluxos confirmados

Depois da correção, testado manualmente com sucesso, na máquina de casa:

1. **Adicionar Formação** (popup) — funcionando
2. **Editar Formação** (popup) — funcionando
3. **Adicionar Vínculo Formal** (popup, com calendário e largura corretos) — funcionando
4. **Encerrar Vínculo Formal** (popup restrito a `data_fim`/`observacao`, botão "Encerrar" some da linha depois de preenchida) — funcionando

`pytest` — `29 passed` durante toda a sessão (nenhuma das mudanças, incluindo a correção dos 3 bugs, tinha cobertura automatizada — item já registrado no Backlog).

---

## Item pendente, não resolvido: `docs/PROMPT_PROXIMO_CONTEXTO_RENOMEACAO.md`

Durante a limpeza do `git status` antes do commit final, apareceu um arquivo não rastreado (`docs/PROMPT_PROXIMO_CONTEXTO_RENOMEACAO.md`) — aparenta ser o prompt usado no início desta série de sessões, para retomar o contexto da renomeação `pessoas`→`cadastros`. Retirado do stage (`git restore --staged`) para não misturar com o commit de correção, mas a decisão de mantê-lo versionado (como registro histórico) ou descartá-lo ainda não foi tomada.

---

## Estado geral ao final desta sessão

| Item | Status |
|---|---|
| CRUD de `HistoricoVinculoFormal` (Adicionar + Encerrar) | ✅ Implementado, testado, confirmado funcionando |
| `ModalCrudMixin` e JS generalizados (reutilizáveis por qualquer entidade) | ✅ Concluído |
| Bug 1 — arquivo desatualizado commitado | ✅ Corrigido |
| Bug 2 — calendário ausente nos campos de data | ✅ Corrigido |
| Bug 3 — popup menor que o Textarea | ✅ Corrigido |
| Encerramento de `AtribuicaoFuncao` para Discente (motivo + Atas) | ⏳ Adiado para a próxima etapa, deliberadamente |
| `docs/PROMPT_PROXIMO_CONTEXTO_RENOMEACAO.md` | ⏳ Decisão pendente (manter ou descartar) |
| Testes automatizados para as Views/Forms do CRUD | ⏳ Não iniciado |
| Testes automatizados | 29 passed (sem alteração) |

---

## Itens novos de Backlog identificados nesta sessão

- [ ] **Padrão a lembrar em todo ModelForm de data futuro:** sempre especificar `widget=forms.DateInput(attrs={'type': 'date'})` explicitamente — o Django não usa esse widget por padrão, mesmo com `DateField` no Model.
- [ ] **Padrão a lembrar em todo campo de texto longo (`Textarea`) usado dentro do popup/modal:** sempre especificar `attrs={'style': 'width:100%; box-sizing:border-box;'}` — o tamanho padrão do navegador (`cols`) pode ultrapassar a largura de um contêiner com `max-width` fixo.
- [ ] **Confirmar sempre com `Select-String`/`git diff` imediatamente antes do commit**, não só logo depois de editar um arquivo — o incidente do `preencher_requisitos_docente.html` desatualizado só foi descoberto no teste manual em outra máquina, um dia depois do commit.
- [ ] Testes automatizados para `AdicionarHistoricoVinculoFormalView`, `EncerrarHistoricoVinculoFormalView`, e os respectivos Forms — nenhum ainda.
- [ ] Decidir o destino de `docs/PROMPT_PROXIMO_CONTEXTO_RENOMEACAO.md` (manter versionado como registro histórico, ou remover).
- [ ] Encerramento de `AtribuicaoFuncao` para Discente (motivo: Transferido/Reprovado/Aprovado/Matrícula Excluída) + campos "Ata de Início de Vínculo"/"Ata de Término de Vínculo" — adiado nesta sessão, tipo de campo das Atas ainda não definido (código/texto, data, ou os dois).

---

## Próximos passos

Replicar o padrão de CRUD via popup (`ModalCrudMixin` + `modal-crud.js`) para Pendências e Experiência Profissional, seguindo a mesma estrutura já validada duas vezes (Formação, Histórico de Vínculo). Depois, retomar o encerramento de `AtribuicaoFuncao` para Discente como uma frente própria, definindo primeiro o tipo de campo das "Atas de Vínculo".
