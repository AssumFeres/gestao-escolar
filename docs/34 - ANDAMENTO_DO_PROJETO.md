# Andamento do Projeto — 34

**Data:** 05/09/2026 (continuação direta de `docs/33`)
**Branch:** `dev`
**Sessão dedicada a: implementar de verdade a estrutura curricular fechada em `docs/33` — `models.py`/`admin.py`/migration das 9 tabelas, e depois as telas de CRUD (Disciplina, SubModulo, Modulo, OfertaModulo/Turma, Ata/AtaPessoa).**

---

## 1. `models.py` + migration `0008` + `admin.py`

Implementadas as 9 tabelas fechadas em `docs/33`: `Disciplina` (ajustada — `carga_horaria` antiga removida, `carga_horaria_programa_de_instrucao`/`teorica`/`pratica` novas, `clean()` bloqueando divergência do PI aprovado), `ConteudoProgramatico`, `SubModulo`, `SubModuloDisciplina`, `Modulo`, `ModuloSubModulo`, `OfertaModulo`, `Turma`, `Ata`. Classe abstrata `CatalogoComSigla` extraída para `Disciplina`/`SubModulo`/`Modulo` (mesmo validador de sigla, mesmo campo `ativo`).

Todos os catálogos registrados no Admin (`admin.site.register()` puro, sem customização — mesmo padrão de `Funcao`/`VinculoFormal`).

**Validação testada manualmente pelo Admin:** cadastrar uma `Disciplina` com carga teórica+prática divergente da carga do Programa de Instrução — bloqueou com a mensagem de erro esperada. Depois corrigido e salvo com sucesso. Confirma a trava mais importante desta entrega (risco de não-conformidade com a ANAC).

**Incidente à parte, resolvido no meio da sessão:** `Turma.capacidade_maxima` foi removido por decisão da pessoa responsável (sem necessidade real de dado) — gerou a migration `0009_remove_turma_capacidade_maxima`, aplicada antes da migration de `AtaPessoa` (que por isso nasceu como `0010`, não `0009`).

---

## 2. Telas de CRUD — Disciplina (+ ConteudoProgramatico)

Primeira tela construída, piloto do padrão a replicar nas seguintes. `Disciplina` é **CRU** (Criar/Ler/Atualizar — nunca Delete, confirmado pela pessoa responsável): toggle Ativo/Inativo substitui a exclusão, com popup de confirmação simples. `ConteudoProgramatico` mora dentro do detalhe da Disciplina, mesmo padrão CRU (sem Delete), com `ordem` sem nenhuma regra de negócio — é só organização de exibição, não uma trilha obrigatória pro instrutor (esclarecido explicitamente pela pessoa responsável).

Todas as Views novas reaproveitam `ModalCrudMixin`/`modal-crud.js` já existentes — nenhuma linha de JavaScript nova precisou ser escrita.

**Novo padrão adotado a partir daqui, por pedido da pessoa responsável:** rodapé discreto em cada template mostrando o caminho do próprio arquivo (ex: "📄 cadastros/templates/cadastros/detalhe_disciplina.html") — ajuda a não se perder com a quantidade crescente de templates. Vale só pra templates novos, não retroativo aos de Pessoa.

**Também adotado a partir daqui:** título de página centralizado, maiúsculo, dentro de `<h2><p align="center">...</p></h2>` — padrão definido pela pessoa responsável olhando o resultado da primeira tela.

---

## 3. Telas de CRUD — SubModulo (+ SubModuloDisciplina)

Primeira tela com uma interação nova: não é "criar uma linha filha do zero", é **selecionar uma Disciplina já cadastrada** e vinculá-la (com `ordem`) via `SubModuloDisciplina`. Decisões fechadas:
- Dropdown simples (não autocomplete) — catálogo pequeno hoje, não justifica componente novo.
- Mensagens de erro amigáveis pra duplicidade (Disciplina repetida no mesmo SubModulo, ou `ordem` repetida) — validação customizada no Form, não a mensagem genérica do Django.
- **Desvincular é Delete real** do vínculo (`SubModuloDisciplina`), não da Disciplina. Discussão importante antes de fechar essa decisão: a pessoa responsável tinha uma preocupação legítima de perder rastreabilidade — esclarecido que `ConteudoProgramatico.disciplina` aponta direto pra `Disciplina` (nunca passa pelo vínculo com SubModulo), então desvincular não afeta em nada o histórico de rastreabilidade real.

Templates de confirmação de exclusão **reaproveitados** dos já existentes (`confirmar_exclusao.html`/`_confirmar_exclusao_fragment.html`, usados desde Formação/Experiência/Pendência) — nenhum arquivo novo precisou ser criado pra isso.

---

## 4. Telas de CRUD — Modulo (+ ModuloSubModulo)

Réplica direta do padrão de SubModulo, uma camada acima (Módulo↔SubModulo em vez de SubModulo↔Disciplina). Adicionada, de bônus, uma `@property carga_horaria` em `Modulo` (soma recursiva dos SubModulos vinculados, que por sua vez somam as Disciplinas) — não fazia parte do pedido original, sugerida por simetria com `SubModulo.carga_horaria`, aprovada. Não gerou nenhuma migration (propriedade Python, não campo de banco).

---

## 5. Telas de CRUD — OfertaModulo + Turma

Padrão de "Encerrar" assimétrico, igual `AtribuicaoFuncao`/`HistoricoVinculoFormal` já usam: cadastro pede só `data_inicio`; `data_fim` só é exigida no popup de Encerrar. Decisão nova confirmada pela pessoa responsável: **Reativar uma Oferta encerrada só é possível pelo Django Admin** — a tela nunca mostra botão de Reativar, só um aviso visual quando a Oferta está encerrada.

`Turma` é filha de `OfertaModulo` (criada só de dentro do detalhe da Oferta, nunca com dropdown próprio) — decisão consciente da pessoa responsável, mesmo reconhecendo que isso deixa a criação "meio escondida": mantida assim por ora.

---

## 6. Telas de CRUD — Ata + AtaPessoa

`Ata` é CRU — Delete só pelo Admin. `AtaPessoa` é uma **exceção provisória e documentada** ao princípio "Pessoa amarrada = módulo Atribuição" (`docs/29`): a pessoa responsável pediu a possibilidade de vincular um Discente a uma Ata (Conselho de Ensino, Orientação, Outro) antes do módulo Atribuição existir de verdade. Decisão explícita: **este vínculo migra para o módulo Atribuição quando ele for construído** — registrado tanto no código (docstring de `AtaPessoa` em `models.py`) quanto aqui.

Botão "+ Vincular Pessoa" aparece só pra `finalidade` Orientação/Conselho de Ensino/Outro — nunca pra Início/Término de Vínculo (que são em lote, não individuais).

Dropdown de Pessoa filtrado a Discentes com `AtribuicaoFuncao` **ativa** (matriculados agora, não ex-alunos).

---

## 7. Bug real encontrado em `Ata`, correção ainda não implementada

A pessoa responsável percebeu que `Ata.numero` como `unique=True` sozinho está errado: o mesmo número (ex: "001/2026") pode existir como Ordinária **e** Extraordinária ao mesmo tempo (séries de numeração independentes). A constraint certa é composta: `UNIQUE(numero, tipo)`.

Também foi levantada a ideia de **numeração automática** (sequencial/ano, por tipo) em vez de digitação manual — proposta técnica esboçada (`save()` sobrescrito, contando Atas existentes do mesmo tipo/ano), com 3 perguntas em aberto (reinício de contagem por ano da `data` ou do sistema; tirar `numero` do formulário de vez; formato com zero à esquerda). **Nenhuma das duas correções foi implementada ainda** — a conversa foi interrompida pela decisão de documentar antes de continuar.

---

## Estado geral ao final desta sessão

| Item | Status |
|---|---|
| `models.py`/`admin.py`/migrations das 9 tabelas | ✅ Implementado e testado |
| Telas de CRUD: Disciplina, SubModulo, Modulo, OfertaModulo/Turma, Ata/AtaPessoa | ✅ Implementadas e testadas manualmente |
| `Turma.capacidade_maxima` removido | ✅ Aplicado (migration `0009`) |
| Bug de `Ata.numero` (`unique` deveria ser composto com `tipo`) | 🔴 Identificado, **não corrigido ainda** |
| Numeração automática de Ata | 📝 Proposta esboçada, não implementada, 3 perguntas em aberto |
| Testes automatizados para as novas Views/Forms | ⏳ Nenhum ainda (mesma lacuna já registrada para o CRUD de Pessoa) |

---

## Itens novos de Backlog

- [ ] **Corrigir `Ata`: `UNIQUE(numero, tipo)`** em vez de `numero` sozinho único — bug real, mesmo número pode ser Ordinária e Extraordinária.
- [ ] **Numeração automática de Ata** (sequencial/ano, série própria por tipo) — proposta esboçada, 3 perguntas em aberto (ver seção 7 acima).
- [ ] Testes automatizados para todas as Views/Forms novas desta sessão (Disciplina, ConteudoProgramatico, SubModulo, SubModuloDisciplina, Modulo, ModuloSubModulo, OfertaModulo, Turma, Ata, AtaPessoa) — nenhum ainda.
- [ ] `Módulo Atribuição`: quando existir, migrar `AtaPessoa` pra lá (já documentado no código, reforçado aqui).

---

## Próximos passos

Fechar o bug/numeração automática de `Ata`. Depois, seguir pra tela de navegação inicial (ver `docs/35`, sessão seguinte, já concluída em paralelo a este diário).
