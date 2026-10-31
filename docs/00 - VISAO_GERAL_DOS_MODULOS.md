# Visão Geral dos Módulos — Sistema de Gestão Escolar (EMCA)

Mapa de alto nível dos módulos (Bounded Contexts) do sistema. Cada módulo tem um resumo breve e seu status atual. **Este documento não substitui os planos detalhados** (`docs/PLANO_MODULO_ATRIBUICAO.md`, futuros planos equivalentes para os demais) — é só o "índice" de onde cada responsabilidade mora, pra não redesenhar a mesma fronteira duas vezes.

Se já existir um `documentacao_arquitetura.md` cobrindo Bounded Contexts (referenciado no Kanban, seção 5), este documento deve ser conciliado com ele — não foi verificado ainda se há sobreposição ou conflito de conteúdo.

---

## CADASTRO ✅ *em desenvolvimento ativo*

A "prateleira" do sistema — catálogos de referência, atemporais, e o cadastro da vida da Pessoa na escola.

- **Pessoa** (Discente/Docente/Gestão), `Funcao`/`AtribuicaoFuncao` (vínculo Pessoa↔Função, situação Ativo/Inativo).
- **Estrutura curricular completa** (desenho fechado em 04/09/2026, `docs/31`): `Disciplina`, `ConteudoProgramatico`, `SubModulo`, `Modulo`, `OfertaModulo`, `Turma`, `Ata`.
- **Não guarda evento de vínculo** entre Pessoa e a estrutura curricular — isso é do módulo Atribuição.
- App Django: `cadastros`.

## TREINAMENTO — *a ser desenvolvido*

Controla o treinamento inicial e recorrente dos Instrutores. Dá a condição formal para um Instrutor ministrar uma Disciplina — a Disciplina precisa já estar na `Capacidade` dele (Cadastro), e o Treinamento é o que valida/renova essa condição ao longo do tempo.

- Consome: `DadosDocente`/`Capacidade`/`Disciplina` (Cadastro).
- Ainda não desenhado em detalhe.

## ATRIBUIÇÃO — *a ser desenvolvido*

"Extensão do Cadastro" (nas palavras da pessoa responsável) — conecta uma `Pessoa` de verdade à estrutura curricular. Reduzido, em 04/09/2026, a essencialmente uma entidade: **`TurmaAluno`** (vínculo Discente↔Turma, com Ata de início/término e status ao longo da trajetória — Ativo/Transferido/Aprovado/Reprovado/Desistente/Matrícula Excluída).

- Consome: `Pessoa`, `AtribuicaoFuncao`, `Turma`, `Ata` (Cadastro).
- Plano em `docs/PLANO_MODULO_ATRIBUICAO.md` (`docs/30`).
- Inclui, no futuro, o equivalente para Docente (quais turmas/disciplinas ministrou por ano) — ainda não desenhado.

## REGISTRO DE INSTRUÇÃO — *a ser desenvolvido*

Unifica 4 frentes que a pessoa responsável identificou como a mesma responsabilidade: **Diário de Classe**, **Controle de Frequência**, **Registro de Avaliações**, e o **consumo do Conteúdo Programático**. É onde o Instrutor efetivamente registra o que aconteceu em cada aula: o que foi ministrado (a partir do `ConteudoProgramatico` definido em Cadastro), quando, tipo de aula (prática/teórica/mista), presença dos alunos, e lançamento de notas/avaliações.

- Consome: `ConteudoProgramatico`, `Disciplina`, `Turma` (Cadastro); `TurmaAluno` (Atribuição).
- Resolve a dúvida em aberto de `docs/31` — "Registro de Instrução" e "Diário de Classe" são o mesmo módulo, não dois módulos sobrepostos.
- Ainda não desenhado em detalhe.

## HORÁRIOS — *a ser desenvolvido*

Carga de horários de aula a partir de planilhas Excel enviadas pelos Coordenadores de Curso, processadas via Python/pandas para popular o banco. Inclui controle de conflitos (ex: mesmo Instrutor ou mesma sala escalados em dois lugares ao mesmo tempo).

- Consome: `Disciplina`, `Turma`, `OfertaModulo` (Cadastro); Docente (via `AtribuicaoFuncao`/`TurmaDocente`, quando existir).
- Ainda não desenhado — inclusive o formato exato das planilhas de entrada.

## CONTRATOS — *a ser desenvolvido*

Controle dos contratos de Instrutores e Gestores — hoje, só com a entidade FAPETI.

- **Ponto de atenção, não resolvido:** `cadastros` já tem `VinculoFormal`/`HistoricoVinculoFormal`, que registra o histórico de vínculo contratual (qual entidade, de quando a quando) para Docente/Gestão. Não está claro ainda se "Contratos" é uma **extensão** disso (ex: valores, cláusulas, renovação, documento do contrato em si) ou uma **duplicação conceitual** que precisa ser conciliada com o que já existe. Avaliar antes de desenhar, para não recriar o que `HistoricoVinculoFormal` já cobre.

## RELATÓRIOS — *a ser desenvolvido*

Geração de documentos formais a partir dos dados do sistema: Relatório Final da Disciplina, Ficha de Frequência e Avaliações (por Aluno), Histórico Escolar, Certificados. Também é onde a geração da Ficha de Matrícula FE 007/FE 008/FOP 402 (já registrada no Backlog de Cadastro) provavelmente deveria morar, em vez de dentro de `cadastros`.

- Consome: praticamente todos os outros módulos (Cadastro, Atribuição, Registro de Instrução).
- Provável uso do fluxo de geração de `.docx`/PDF já usado no projeto.
- Ainda não desenhado em detalhe.

## DASHBOARD — *a ser desenvolvido*

Visualização/consulta consolidada — indicadores, provavelmente a evolução futura da tela de detalhe de Pessoa mencionada em `docs/29` ("no futuro, a tela detalhe pode até migrar pra um módulo de Relatório ou Dashboard/Consulta").

- Consome: todos os módulos, só leitura.
- Ainda não desenhado — inclusive se é o mesmo módulo que Relatórios ou um módulo à parte.

---

## Mapa de dependências (visão simplificada)

```
CADASTRO (prateleira: Pessoa, estrutura curricular)
   │
   ├─→ TREINAMENTO (consome DadosDocente/Capacidade)
   │
   ├─→ ATRIBUIÇÃO (TurmaAluno — conecta Pessoa à estrutura curricular)
   │      │
   │      └─→ REGISTRO DE INSTRUÇÃO (Diário/Frequência/Avaliações/Conteúdo)
   │
   ├─→ HORÁRIOS (carga via Excel/pandas, controle de conflito)
   │
   └─→ CONTRATOS (ponto de atenção: sobreposição com HistoricoVinculoFormal?)

RELATÓRIOS ←── consome CADASTRO + ATRIBUIÇÃO + REGISTRO DE INSTRUÇÃO
DASHBOARD  ←── consome tudo, só leitura
```

---

## Perguntas em aberto

- [ ] Conciliar este documento com `documentacao_arquitetura.md` (já existente, referenciado no Kanban) — verificar sobreposição.
- [ ] **Contratos vs. `HistoricoVinculoFormal`** — mesma responsabilidade ou complementares? Avaliar antes de desenhar Contratos.
- [ ] **Relatórios vs. Dashboard** — módulos distintos ou um só, com duas formas de apresentação (documento gerado vs. tela de consulta)?
- [ ] Cada módulo "a ser desenvolvido" precisa, na hora certa, de um plano próprio no padrão já estabelecido (`docs/16`, `docs/30`) antes de qualquer código.

---

## Próximos passos

Nenhuma implementação prevista para os módulos além de Cadastro neste momento. Este documento serve de referência para quando cada frente for iniciada — a ordem de prioridade entre Treinamento/Atribuição/Registro de Instrução/Horários/Contratos/Relatórios/Dashboard ainda não foi definida pela pessoa responsável.
