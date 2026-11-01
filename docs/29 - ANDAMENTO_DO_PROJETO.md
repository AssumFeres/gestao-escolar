# Andamento do Projeto — 29

**Data:** 03/09/2026
**Branch:** `dev` (sessão sem commit — dedicada inteiramente a design/decisão de arquitetura, sem nenhuma linha de código escrita)
**Sessão dedicada a: desenhar o próximo item do Kanban ("Editar/Encerrar Atribuição de Função"), o que evoluiu para uma discussão mais ampla sobre onde moram Ata/Turma/Módulo no sistema, e a separação de responsabilidades entre `cadastros` e o futuro módulo Atribuição.**

---

## Contexto

Continuação direta do diário 28. Próximo item confirmado no fim daquela sessão: Editar Atribuição de Função. Ao levantar o escopo, ficou claro que a pergunta "o que dá pra editar numa AtribuicaoFuncao" não tinha resposta simples sem antes decidir onde vivem Ata e Turma — que a pessoa responsável queria adicionar como campos do fluxo de Discente. Isso puxou uma discussão de várias rodadas, sem código, só desenho.

---

## Rodada 1 — Primeira tentativa: Ata/Turma dentro de `DadosDiscente`

Proposta inicial (rejeitada nas rodadas seguintes): adicionar `ata_inicio_vinculo`/`ata_termino_vinculo` (texto livre) e um campo `turma` (texto livre, placeholder) direto em `DadosDiscente`, e dois botões em `detalhe.html` ("Adicionar Vínculo" / "Encerrar Vínculo") controlando isso junto com a criação de `AtribuicaoFuncao`.

**Motivo da revisão:** a pessoa responsável apontou que "Adicionar Vínculo" já existe de fato (busca por CPF + reenvio do formulário de cadastro com Função diferente, ver diário 28) — não precisa de botão novo. Isso simplificou a v1 para só "Encerrar", mas a dúvida sobre onde os campos deveriam morar continuou.

---

## Rodada 2 — Regra de negócio real do "Ata de Início/Término": não é por turma

A pessoa responsável explicou 3 cenários reais de trajetória de um Discente:
1. Progressão normal (Básico → Especializado): troca de turma, **sem** Ata de Término.
2. Realocação dentro do mesmo módulo: troca de turma, **sem** Ata nenhuma.
3. Reprovação/transferência para fora da escola: **com** Ata de Término.

**Conclusão:** Ata de Início/Término marca a entrada/saída **da escola**, não de uma turma específica — pertence à trajetória de `AtribuicaoFuncao`/`DadosDiscente` (nível "vínculo com a escola"), não à trajetória de turma (nível "vínculo com uma sala de aula naquele ano"). Isso já separava conceitualmente Ata de Turma, mas ainda não resolvia estrutura de dado.

---

## Rodada 3 — Escala do problema: 300 registros manuais é inviável

A pessoa responsável revelou o motivo prático de repensar a estrutura de Turma: ao criar uma turma, a secretaria precisa popular Data de Início e Ata de Início para ~300 alunos de uma vez. Fazer isso um a um, por texto livre repetido, é lento e propenso a erro de digitação — o mesmo problema que já motivou `Funcao` e `VinculoFormal` a virarem catálogos abertos em vez de texto solto repetido.

**Decisão:** `Ata` vira um catálogo próprio (`numero` único + `tipo` Ordinária/Extraordinária + `data`), não mais texto livre — uma Ata é cadastrada uma vez e referenciada por N alunos.

---

## Rodada 4 — A virada principal: separar "catálogo" (prateleira) de "trilha" (receita)

A pessoa responsável trouxe a visão-chave da sessão, usando a metáfora de supermercado: `cadastros` é a **prateleira** — só guarda os produtos (catálogos de referência: `Funcao`, `Disciplina`, `VinculoFormal`, e agora `Ata`, `Módulo`, `SubModulo`, `Turma`). O **uso** desses produtos para registrar uma trajetória real (quem passou por qual turma, quando, com qual Ata) é responsabilidade de um módulo futuro, à parte — **Atribuição** —, que ainda não existe.

**Regra explícita, para não repetir o erro de misturar responsabilidades:**
- `cadastros` (o que já existe) cadastra só a "vida" da Pessoa na escola: Discente/Docente/Gestão, `AtribuicaoFuncao` = Pessoa + Função + Situação + período. Nada de Turma/Ata ali.
- A trilha completa (turmas por que um Discente passou, disciplinas que um Docente ministrou, treinamentos feitos) é dado de **outros módulos** (Atribuição, Treinamento), e é só **exibida** na tela de detalhe de `cadastros` — não é dado próprio do cadastro. No futuro, essa exibição pode até migrar para um módulo de Relatório/Dashboard/Consulta separado.

Isso reverteu a Rodada 1 por completo: nenhum campo de Ata/Turma entra em `DadosDiscente`/`AtribuicaoFuncao`.

---

## Rodada 5 — Ata/Módulo/Turma SÃO catálogos de `cadastros`, mas o vínculo (quem passou por onde) não é

Ajuste fino sobre a Rodada 4: os catálogos em si (`Ata`, `Módulo`, `SubModulo`, `Turma`) **entram em `cadastros`**, porque são "produtos" reutilizáveis por qualquer módulo — inclusive o futuro Atribuição. O que não entra em `cadastros` é o **evento de vínculo** (`TurmaAluno`, ligando um Discente a uma Turma específica, com Status/Data/Ata daquele evento específico) — isso é receita, do módulo Atribuição.

---

## Rodada 6 — Hierarquia curricular real: Módulo → SubModulo → Disciplina

A pessoa responsável descreveu uma estrutura vinda de uma atualização real da ANAC: um Módulo (ex: Básico) se divide em SubModulos (ex: "Performance Humana e Limitações", 50h; "Conhecimentos Aplicados", 200h), cada um com suas próprias Disciplinas.

**Correção de direção de FK identificada durante o desenho:** a primeira formulação tinha a FK invertida (Módulo → SubModulo → Disciplina, como se o "pai" apontasse pro "filho"). Corrigido para o padrão Django correto: FK sempre do lado "muitos" para o lado "um" — `SubModulo.modulo` (FK → Módulo) e `Disciplina.submodulo` (FK → SubModulo, opcional por enquanto, já que as 23 disciplinas identificadas na auditoria de 03/09 — diário 28 — ainda não têm submódulo atribuído).

**Campo `conteudo_programatico`** (texto livre) também identificado como lacuna de `Disciplina` durante essa discussão, incluído no desenho.

---

## Rodada 7 — `Módulo`: uma tabela só, sem campo `habilitação` redundante

Dúvida levantada: `Módulo` deveria ter `nome` (livre) e `habilitação` (Básico/Aviônica/Célula/GMP/Extra) como campos separados? A pessoa responsável decidiu que não — `nome` sozinho já carrega o valor distintivo completo ("Básico", "Especializado em Aviônica", "Especializado em Célula", "Especializado em GMP", "Extra"), evitando uma coluna redundante. Modelo final: `Modulo.nome` (único), ponto.

---

## Rodada 8 — Prévia do futuro módulo Atribuição: `ModuloAno`

Fora do escopo de implementação de hoje, mas registrado para o plano futuro: a pessoa responsável descreveu que o módulo Atribuição vai "montar a receita" — pegar o `Módulo` genérico (produto processado, atemporal) e uni-lo a um ano letivo específico + Docentes específicos (de `cadastros`) responsáveis por cada Disciplina naquele ano, gerando uma nova entidade (provisoriamente chamada `ModuloAno`). Só depois disso, `TurmaAluno` conectaria o Discente a uma Turma dentro desse `ModuloAno`. Esse desenho fica registrado aqui como ponto de partida para um plano de migração dedicado (`docs/PLANO_MODULO_ATRIBUICAO.md`, ainda não escrito) — comparável em escala à migração `Vinculo→Funcao`.

---

## Rodada 9 — Simplificação de `situacao`/`ativo` em `AtribuicaoFuncao`

Separado da discussão de Ata/Turma: `AtribuicaoFuncao` hoje tem dois campos que se sobrepõem — `situacao` (texto livre, sempre `"ATIVO"` na prática, nunca editável por nenhuma tela) e `ativo` (booleano, `default=True`, também nunca alterado por nenhuma tela). **Decisão:** consolidar em um campo só — `situacao`, `CharField` com `choices` de duas opções (`ATIVO`/`INATIVO`) — removendo o booleano `ativo` por completo. O botão único "Encerrar Função" (item que estava em aberto desde o início da sessão) mexe só nesse campo: `ATIVO` → `INATIVO`, mais `data_fim` (opcional, sem exigir Ata nem Turma, já que isso não é mais responsabilidade de `cadastros`).

---

## Decisão final de escopo para a próxima sessão de código

1. **Catálogos novos em `cadastros`** (Admin-only, sem CRUD dedicado ainda, mesmo padrão de `Funcao`/`VinculoFormal`): `Ata`, `Modulo`, `SubModulo`, `Turma`.
2. **`Disciplina`**: novo campo `conteudo_programatico` (texto livre) e `submodulo` (FK opcional para `SubModulo`).
3. **`AtribuicaoFuncao`**: campo `situacao` vira `choices` (`ATIVO`/`INATIVO`), campo `ativo` (booleano) é removido — precisa de migration com passo de dado (normalizar `situacao` a partir do `ativo` existente antes de remover).
4. **Botão único "Encerrar Função"** em `detalhe.html`, na tabela de Funções — visível só quando `situacao == ATIVO`; popup só com `data_fim` (opcional); ao confirmar, `situacao` vira `INATIVO`.
5. **Nada de Ata/Turma/Módulo entra em `DadosDiscente`/`AtribuicaoFuncao`** — são só catálogo, consumidos futuramente pelo módulo Atribuição.
6. **Coluna "Turma"** na tabela de Funções continua placeholder ("-----") — permanece assim até o módulo Atribuição existir de verdade.

Nenhuma dessas mudanças foi implementada nesta sessão — fica para a próxima, já com o desenho fechado.

---

## Itens novos de Backlog/Planejamento identificados nesta sessão

- [ ] **Implementar os catálogos `Ata`, `Modulo`, `SubModulo`, `Turma`** em `cadastros` (Admin-only por enquanto) + `Disciplina.conteudo_programatico`/`Disciplina.submodulo` — ver desenho completo acima.
- [ ] **Consolidar `AtribuicaoFuncao.situacao`/`ativo`** em um único campo `choices` (ATIVO/INATIVO), com migration de dado preservando o estado atual (derivar de `ativo`, já que `situacao` livre nunca foi editado de verdade).
- [ ] **Botão único "Encerrar Função"** em `detalhe.html` — ver desenho completo acima.
- [ ] **Escrever `docs/PLANO_MODULO_ATRIBUICAO.md`** — plano de migração dedicado para o futuro módulo Atribuição (`ModuloAno`, `TurmaAluno`, fluxo de atribuição em lote de ~300 alunos por turma, tela de criar/encerrar turma, tela de editar status individual do aluno). Escala comparável à migração `Vinculo→Funcao` — não deve ser implementado "de passagem" dentro de uma sessão do Kanban de `cadastros`.
- [ ] **Popular `Disciplina.submodulo`** para as 23 disciplinas já cadastradas (achado de brinde da auditoria, diário 28), quando `SubModulo` existir.
- [ ] Reformular itens 3 e 4 do Kanban ("Editar Atribuição de Função" / "Encerrar Atribuição de Função") — viram um item só ("Encerrar Função"), já que não haverá edição livre de `situacao` fora do botão de encerramento.
- [ ] Confirmar item 5 do Kanban ("Adicionar Nova Função a Pessoa existente") como **já resolvido** desde o diário 28 — a busca por CPF + reenvio do cadastro com Função diferente já cobre esse caso, sem necessidade de tela nova.

---

## Próximos passos

Na próxima sessão de código: implementar os 4 pontos de escopo fechados acima (catálogos, `Disciplina`, consolidação de `situacao`/`ativo`, botão "Encerrar Função"), com migrations aditivas/de-dado, seguindo o mesmo cuidado de preservar dado já usado nas 3 máquinas (casa/quartel/escola). Depois, decidir quando dedicar uma sessão só para desenhar `docs/PLANO_MODULO_ATRIBUICAO.md` em detalhe.
