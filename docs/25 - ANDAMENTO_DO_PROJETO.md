# Andamento do Projeto — 25

**Data:** 02/09/2026 (máquina do quartel)
**Branch:** `dev` (commits diretos)
**Sessão dedicada a: fechar o CRUD via popup de `PendenciaCadastro` (última das 4 entidades repetíveis do cadastro inicial), refinar a aparência visual da tela de detalhe, e implementar os "Requisitos de Contratação" (RBAC 141) para Docente e Gestão.**

---

## Contexto

Continuação direta do diário 24. Retomando na máquina do quartel: `git pull`, `migrate` (aplicando a `0003` do dia anterior), `check`/`pytest` confirmados saudáveis antes de começar.

---

## 1. CRUD completo de `PendenciaCadastro` (última das 4 entidades)

Seguindo exatamente o padrão já validado 3 vezes (Formação, Vínculo, Experiência): `PendenciaCadastroModelForm` (Create — `tipo`+`descricao`) e `EditarPendenciaCadastroForm` (Update — inclui `resolvida`), `AtribuicaoFuncao` como pai.

**Detalhe de design, aproveitando um item já existente no Backlog** ("Tela/fluxo para marcar uma `PendenciaCadastro` como resolvida"): ao marcar `resolvida=True` na edição, a `View` (`EditarPendenciaCadastroView.form_valid()`) preenche `resolvida_em` automaticamente com `timezone.now()` — e limpa de volta para `None` se `resolvida` voltar a `False`. Esse campo nunca aparece no formulário, evitando o usuário digitar uma data manual incoerente com o clique real.

**Decisão de negócio confirmada:** Pendência permite Delete real (como Formação/Experiência), não a restrição de "nunca excluir" do Vínculo Formal.

`pytest` — `29 passed`. Testado manualmente com sucesso: Adicionar, Editar (com o teste específico de marcar/desmarcar `resolvida` e confirmar `resolvida_em` no Admin), e Excluir.

Com isso, **as 4 entidades repetíveis do cadastro inicial (Formação, Vínculo Formal, Experiência Profissional, Pendência) têm CRUD completo via popup**, todas reaproveitando o mesmo `ModalCrudMixin`/`modal-crud.js` sem nenhuma linha de JavaScript nova desde o segundo piloto (diário 23). Fecha a migração de arquitetura `docs/21` para essa camada — só `Capacidade` (ligada à tela de Requisitos do Docente, ainda placeholder) fica de fora por enquanto.

---

## 2. Refinamento visual: `fieldset` + `.btn-crud`

A pessoa responsável pediu 3 mudanças de aparência:
1. Mover os botões "+ Adicionar" para o final de cada seção (não logo depois do título)
2. Envolver cada seção num "card" visual, para separação clara
3. Trocar a cor dos botões do CRUD de `#002060` (cor primária do sistema) para `#1F4E79`

**Decisão de escopo, confirmada explicitamente:** a nova cor `#1F4E79` é aplicada só nos botões do CRUD (classe nova `.btn-crud`), **não** na variável `--cor-primaria` global — evitando mudar a cor de cabeçalho/links/outros botões do sistema inteiro sem essa intenção.

Para o "card", nenhum CSS novo foi necessário: o projeto já tinha `fieldset`/`legend` estilizados como card desde a Etapa 7.3 (`base.css`, seção "FORMULÁRIOS DE CADASTRO") — só reaproveitamos a tag certa no HTML de `detalhe.html` e `preencher_requisitos_docente.html`, envolvendo Pendências/Experiência/Histórico/Formação/Capacidade cada uma no seu `fieldset`.

### Incidente: `TemplateSyntaxError` ao tentar editar manualmente

A pessoa responsável tentou adicionar o `fieldset` em Formação/Capacidade por conta própria e introduziu um erro de sintaxe de template (`Invalid block tag: 'endwith', expected 'endfor'`) — a causa exata não foi identificada com certeza (possível caractere invisível ou desalinhamento de tags durante a edição manual). Resolvido reescrevendo o arquivo `detalhe.html` inteiro do zero, em vez de tentar uma correção cirúrgica — mais seguro quando a causa não está clara.

---

## 3. Decisão de arquitetura: eliminar `preencher_requisitos_docente.html` (Etapa B, ainda não executada)

Ao notar que o botão "+ Adicionar Formação" nunca existiu em `detalhe.html` (o CRUD de Formação sempre viveu só na tela de Requisitos), a pessoa responsável propôs consolidar tudo em `detalhe.html`, eliminando a tela separada. **Decisão tomada, mas dividida em 2 etapas para não misturar escopos:**

- **Etapa A (executada nesta sessão):** implementar os Requisitos de Contratação primeiro, sem mexer na tela antiga ainda.
- **Etapa B (não executada, próxima sessão):** mover o CRUD de Formação para `detalhe.html`, trocar os redirecionamentos, apagar a tela antiga.

O `views.py` desta sessão já documenta essa decisão numa nota na `PreencherRequisitosDocenteView`, para não ser esquecida.

---

## 4. Requisitos de Contratação (RBAC 141) — Docente e Gestão

### Discussão de design, com um conflito real identificado a tempo

A pessoa responsável pediu um campo de "Requisitos de Contratação" com 3 opções (escolha única): experiência docente comprovada, formação específica, ou outro — mais um campo "Documento comprobatório". Antes de implementar, duas perguntas de esclarecimento evitaram um design errado:

1. **Aplica-se a Gestão também, não só Docente?** Confirmado que sim — isso mudou onde os campos deveriam morar: em `AtribuicaoFuncao` (comum às duas categorias), não em `DadosDocente` (só existe para Docente).
2. **"Documento comprobatório" como FK para `FormacaoDocente`?** A pessoa responsável queria inicialmente uma referência a uma Formação já cadastrada — mas isso não funciona para Gestão, que nunca tem `FormacaoDocente` (só `ExperienciaProfissional`). Apresentado o conflito, decidido voltar para **texto livre**, que funciona igual para as duas categorias.

### Implementação

- **Migration `0004`**: 2 campos novos em `AtribuicaoFuncao` — `requisito_contratacao` (`CharField` com `choices` de 3 opções, `RequisitoContratacao.TextChoices`) e `documento_comprobatorio` (`CharField` texto livre).
- **`EditarRequisitoContratacaoForm`**: `ModelForm` restrito a esses 2 campos, com `requisito_contratacao` usando `forms.RadioSelect()` (não o `<select>` padrão dos outros campos de `choices` do projeto) — decisão deliberada, já que são só 3 opções com texto longo, mais legível lado a lado.
- **`EditarRequisitoContratacaoView`**: diferente das outras entidades do CRUD independente, não é uma lista repetível — só Editar, sem Adicionar/Excluir, direto na própria `AtribuicaoFuncao` (o objeto editado já é o "pai").
- **`detalhe.html`**: nova seção "Requisitos de Contratação", visível só para Docente/Gestão (`atribuicao.funcao.categoria != 'DISCENTE'`).

`pytest` — `29 passed`. Testado manualmente com sucesso: edição via popup com radio funcionando, seção ausente corretamente na tela de Discente.

---

## Item levantado no fim da sessão, não implementado ainda

A pessoa responsável notou que `documento_comprobatorio` deveria ser **obrigatório**, e levantou a preocupação de isso quebrar dados já cadastrados. **Esclarecido, mas não implementado nesta sessão:** o campo já não aceita `NULL` no banco (`null=True` nunca foi usado) — os registros existentes têm string vazia (`""`), que continua um valor válido no banco independente de `blank=True`/`False`. Trocar para `blank=False` é uma migration trivial, sem risco a dado existente — o efeito é só passar a exigir o preenchimento na próxima vez que alguém editar aquele registro pelo formulário. Registrado no Backlog para a próxima sessão.

---

## Estado geral ao final desta sessão

| Item | Status |
|---|---|
| CRUD completo de `PendenciaCadastro` | ✅ Implementado e testado |
| As 4 entidades repetíveis do cadastro inicial com CRUD via popup | ✅ Completo (Formação, Vínculo, Experiência, Pendência) |
| Refinamento visual (`fieldset` + `.btn-crud`) | ✅ Aplicado em `detalhe.html` e `preencher_requisitos_docente.html` |
| Decisão: eliminar `preencher_requisitos_docente.html` | ✅ Decidido, dividido em Etapa A (feita) e Etapa B (pendente) |
| Requisitos de Contratação (RBAC 141), Docente e Gestão | ✅ Implementado e testado |
| `documento_comprobatorio` obrigatório | 📝 Registrado no Backlog, não implementado |
| Edição de Funções (`AtribuicaoFuncao` — situação/datas) | 📝 Próxima sessão, mencionada mas não iniciada |
| Testes automatizados | 29 passed (sem alteração — nenhuma View/Form novo desta sessão tem cobertura ainda) |

---

## Itens novos de Backlog identificados nesta sessão

- [ ] **Tornar `documento_comprobatorio` obrigatório** (`blank=False`) em `AtribuicaoFuncao` — migration trivial, sem risco a dados existentes (campo já não aceita `NULL`; registros antigos com `""` continuam válidos). Efeito: passa a exigir preenchimento na próxima edição via formulário.
- [ ] **Etapa B da consolidação**: mover o CRUD de Formação (`Adicionar`/`Editar`/`Excluir`) de `preencher_requisitos_docente.html` para `detalhe.html`, trocar os redirecionamentos (`get_success_url` das 3 Views de Formação, e o redirecionamento pós-cadastro de Docente em `NovoCadastroPessoaView`), e então apagar a tela antiga.
- [ ] **Edição de Funções** (`AtribuicaoFuncao` — situação, datas) — mencionada como próximo passo desta sessão, ainda não escopada em detalhe.
- [ ] Testes automatizados para `AdicionarPendenciaCadastroView`, `EditarPendenciaCadastroView`, `ExcluirPendenciaCadastroView`, `EditarRequisitoContratacaoView` — nenhum ainda.
- [ ] Aplicar `fieldset`/`.btn-crud` de forma consistente também nas seções "Funções" e "Dados do Discente" de `detalhe.html`, se fizer sentido visualmente — não solicitado explicitamente nesta sessão, mas coerente com a direção de "deixar mais bonito".

---

## Próximos passos

Editar Funções (`AtribuicaoFuncao`), conforme indicado pela pessoa responsável ao final da sessão — escopo ainda a definir na próxima conversa. Depois, retomar a Etapa B (eliminação de `preencher_requisitos_docente.html`) e tornar `documento_comprobatorio` obrigatório.
