# Andamento do Projeto — 38

**Data:** 07/09/2026 (sessão longa, contínua — implementação completa do `docs/37`)
**Branch:** `dev`
**Sessão dedicada a: implementar o módulo Atribuição/Turma do zero até o fim — Etapa 0, `MatriculaTurma`, as 3 fases da Turma (Planejamento/Em Andamento/Encerrada), e o "Sumário Histórico de Vínculos" em `detalhe.html`.**

---

## 1. Etapa 0 — pré-requisitos em `cadastros`

- **Consolidação `AtribuicaoFuncao.situacao`/`ativo`**: os dois campos redundantes viraram um só, `situacao` com `choices` (`ATIVO`/`INATIVO`) — migrations `0012`-`0014`, com passo de normalização de dado a partir do `ativo` existente antes de remover o campo.
- **Bug corrigido**: `CadastrarPessoaComFuncaoService` bloqueava um ex-aluno de voltar como Discente, porque checava só a *existência* de uma `AtribuicaoFuncao` Discente, não se ela estava `ATIVO`. Corrigido para filtrar por `situacao='ATIVO'` — cada passagem pela EMCA como Discente agora é sua própria `AtribuicaoFuncao`, e um retorno depois de formado/reprovado cria uma nova, sem reabrir a antiga.
- **`Modulo.categoria`** (novo campo estruturado: `BASICO`/`ESPECIALIZADO`/`EXTRACURRICULAR`) — usado depois pela regra de fechamento de vínculo no "Encerrar Turma".
- **2 Services novos em `cadastros/services.py`**: `EncerrarVinculoService` (fecha qualquer `AtribuicaoFuncao`, sem Ata — a Ata mora em `MatriculaTurma`) e `ObterOuCriarAtribuicaoDiscenteService` (reaproveita vínculo ativo existente, ou cria um novo mínimo — usado tanto no cadastro quanto na matrícula em Turma).

**Princípio arquitetural fixado nesta sessão, seguido à risca do início ao fim:** `atribuicao` nunca escreve direto nos Models de `cadastros` — toda escrita passa por um Service exposto lá. `atribuicao` só *lê* de `cadastros` (inclusive via relações reversas, sem import — usado depois no Sumário Histórico).

---

## 2. App novo `atribuicao` — `MatriculaTurma`

Model novo, com as duas `UniqueConstraint` que a modelagem exigia (`atribuicao_funcao`+`turma`; `turma`+`numero_na_turma` — permitindo múltiplos `NULL` coexistindo durante o Planejamento). `numero_na_turma` nunca muda depois de atribuído (referência formal usada por professor/secretaria).

---

## 3. Fase Planejamento

Telas: lista de composição da Turma (`GerenciarTurmaView`), **+ Adicionar Aluno** (dropdown filtrado por elegibilidade — Discente `ATIVO` "aguardando", ou qualquer Pessoa se a Turma for Extracurricular), **Editar/Excluir** (CANAC / remoção física, só enquanto `PLANEJADA`), e **Finalizar Planejamento** (popup pede `data_inicio`+`ata_inicio`, grava em massa + atribui `numero_na_turma` em ordem alfabética + avança `Turma.situacao` via `IniciarTurmaService`, novo em `cadastros`).

**Decisão de UX confirmada:** "Nr" (posição do aluno na turma) nunca é recalculado — uma vez atribuído, é fixo, porque professores/secretaria referenciam "aluno nº 22" em registros formais.

---

## 4. Fechamento das 2 perguntas em aberto do `docs/37`

- **8-A (revisão pré-aprovação em massa):** confirmado o popup com checkbox "Aprovar" por aluno, marcado por padrão, desmarcável — quem for desmarcado fica de fora, resolvido individualmente depois.
- **8-B (encerramento individual em Turma Básico):** confirmado que `REPROVADO`/`TRANSFERIDO`/`MATRICULA_EXCLUIDA` é **sempre** fim de ciclo na EMCA — independente do Módulo (Básico ou Especializado) — sempre exige Ata de Término e sempre fecha o vínculo. Isso restringiu a distinção Básico/Especializado a um único lugar: a promoção `APROVADO` em massa no fim de ano.

---

## 5. Fase Em Andamento

**Relocação**: 2 operações atômicas — fecha a linha de origem (`RELOCADO`+`data_fim`, sem tocar em `AtribuicaoFuncao`), cria uma linha nova na Turma destino (`CURSANDO`, `numero_na_turma=MAX+1` de lá). Vínculo institucional nunca é afetado por relocação.

**Status terminais** (Reprovado/Transferido/Matrícula Excluída): sempre pedem `data_fim`+`ata_encerramento`, sempre chamam `EncerrarVinculoService`. `motivo_saida` (Abandonou/Solicitou) só existe pra Transferido — Matrícula Excluída já é abandono por definição.

**Gap real encontrado durante o teste funcional, registrado no Backlog:** uma Turma que só vai receber alunos por relocação (nunca teve planejamento inicial com CANAC) precisa, mesmo assim, passar pelo botão "Finalizar Planejamento" (mesmo vazia, 0 alunos) pra sair de `PLANEJADA` — senão a Relocação funciona, mas a Turma nunca avança de estado, e trava o "Encerrar Turma" mais tarde. Não corrigido nesta sessão.

---

## 6. Fase Encerrar Turma (2 cliques) — e a pendência da seção 7 do `docs/37` resolvida

- **1º clique**: lista de revisão (8-A) → promove os marcados a `APROVADO` em massa.
- **2º clique** (só disponível sem ninguém `CURSANDO`): pede `data_encerramento` sempre; `ata_encerramento` só exigida se o Módulo não for Básico.
- **Regra por categoria, testada nos 3 cenários reais:**
  - `BASICO`: nunca fecha vínculo — só grava `data_fim`.
  - `ESPECIALIZADO`: sempre fecha vínculo (Ata em massa).
  - `EXTRACURRICULAR`: fecha vínculo **exceto** se a mesma `AtribuicaoFuncao` ainda tiver outra `MatriculaTurma` `CURSANDO` numa Turma não-Extracurricular (acumulação) — resolve de vez a pendência que tinha ficado em aberto na seção 7 do `docs/37`, com a checagem que já estava esboçada lá.

**Gap de schema encontrado e corrigido:** `Turma` nunca teve nenhum campo de data de encerramento, apesar da especificação da secretaria pedir isso explicitamente — adicionado `Turma.data_encerramento` (migration `0015`), com `ConcluirTurmaService` novo em `cadastros` pra fazer a transição `EM_ANDAMENTO→ENCERRADA`.

---

## 7. "Sumário Histórico de Vínculos" (renomeado de "Funções")

Substituída a tabela antiga (`detalhe.html`) por uma consulta consolidada, montada em `DetalhePessoaView`:
- **Docente/Gestão**: 1-2 linhas direto de `AtribuicaoFuncao` (Ativo + Inativo, se houver `data_fim`).
- **Discente**: 1 linha por `MatriculaTurma`, na ordem em que aconteceram — código de matrícula ANAC aparece junto do nome da Função. **Toda linha mostra "Ativo", exceto a última**, que reflete o valor atual de `AtribuicaoFuncao.situacao` — funciona porque `situacao` só muda uma vez por vínculo (nunca reabre a mesma `AtribuicaoFuncao`), então a última linha sempre coincide com o evento que fechou (ou não).

**Testado com o cenário real completo** (Relocação → Aprovação Básico → Reprovação Especializado) e bateu exatamente com o exemplo que a pessoa responsável tinha desenhado à mão dias atrás.

Essa consulta lê `atribuicao_funcao.matriculas_turma` (o `related_name` do módulo `atribuicao`) **sem nenhum import de `atribuicao` em `cadastros`** — a leitura funciona pela relação reversa que o Django já registra sozinho, preservando a fronteira entre os dois apps mesmo nessa ponta.

---

## 8. Correção de cabeçalho (sem relação com Atribuição)

`cadastros/models.py` ainda tinha, no topo, `"""pessoas/models.py"""` — sobra do rename `pessoas`→`cadastros` (diário 17, 31/08/2026) que nunca tinha sido corrigida no próprio arquivo. Corrigido nesta sessão.

**Convenção nova, a partir de agora:** todo arquivo com nome comum entre apps (`urls.py`, `views.py`, `forms.py`, etc.) leva o caminho completo no cabeçalho (ex: `"""atribuicao/urls.py"""`), pra facilitar saber onde aplicar cada entrega — sem retroagir nos arquivos já existentes.

---

## Estado geral ao final desta sessão

| Item | Status |
|---|---|
| Etapa 0 (situacao/ativo, bug, Modulo.categoria, Services) | ✅ |
| App `atribuicao` + `MatriculaTurma` | ✅ |
| Fase Planejamento (Adicionar/Editar/Excluir/Finalizar) | ✅ |
| Fase Em Andamento (Relocação, status terminais) | ✅ |
| Fase Encerrar Turma (2 cliques, revisão, regra por categoria) | ✅ |
| Regra de acumulação do Extracurricular (seção 7 do `docs/37`) | ✅ |
| "Sumário Histórico de Vínculos" em `detalhe.html` | ✅ |
| **`docs/37` — módulo Atribuição/Turma completo** | ✅ |

---

## Itens novos de Backlog

- [ ] **Turma que só recebe relocados nunca sai de `PLANEJADA`** sem passar manualmente por "Finalizar Planejamento" vazia — considerar avançar automaticamente o estado da Turma destino na primeira Relocação recebida, se ainda `PLANEJADA`.
- [ ] **Menu lateral, item "Atribuição"** (grupo Coordenação) ainda aponta para "Em Construção" — decidir entre criar uma lista de Turmas em `atribuicao` pra apontar pra lá, ou manter como está por mais um tempo.
- [ ] **Links do `base.html`** pendentes de revisão geral — pessoa responsável sinalizou para revisar amanhã.
- [ ] Testes automatizados para todo o módulo `atribuicao` (nenhum ainda — mesma lacuna já registrada para o resto do projeto).
- [ ] Limpeza de código morto em `models.py`/`services.py` antes de produção — ainda não feita (registrada desde `docs/37`).

---

## Próximos passos

Revisar/atualizar `base.html` (links pendentes) e decidir o destino do item "Atribuição" no menu. Depois, considerar a próxima frente grande: Instrutor↔Turma↔Disciplina (Capacidade + Treinamento), ou finalizar `detalhe.html` com outros ajustes pendentes, ou Relatórios (Ficha de Matrícula) — ordem ainda não definida.
