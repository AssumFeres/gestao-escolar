# Plano — Módulo Atribuição (Vínculo Aluno↔Turma)

**Origem da decisão:** sessão de arquitetura de 03/09/2026 (`docs/29`), revisada em 04/09/2026 (`docs/31`) depois que `OfertaModulo`/`Turma` migraram para `cadastros`. Este documento é o ponto de partida para quando essa frente for de fato iniciada; não é um plano de execução fechado.

**Status:** não iniciado — depende de toda a estrutura curricular (`Disciplina`/`SubModulo`/`Modulo`/`OfertaModulo`/`Turma`/`Ata`, ver `docs/31`) já existir implementada em `cadastros`.

**Escala esperada:** bem mais enxuta do que a estimativa original de 03/09/2026 — como `OfertaModulo`/`Turma` deixaram de ser responsabilidade deste módulo, o que resta aqui é essencialmente **uma entidade** (`TurmaAluno`) e o fluxo de tela em torno dela. Ainda assim, merece sessão própria antes de codar, pela regra fina de negócio envolvida (ver abaixo).

---

## Princípio arquitetural (atualizado em 04/09/2026)

`cadastros` deixou de ser só "prateleira atemporal" — passou a incluir também a **estrutura anual** (`OfertaModulo`, `Turma`), desde que ela não referencie `Pessoa`. A régua que decide o que é `cadastros` e o que é módulo Atribuição não é mais "tem ano/data" — é **"tem Pessoa amarrada"**:

- `cadastros`: Disciplina, ConteudoProgramatico, SubModulo, SubModuloDisciplina, Modulo, ModuloSubModulo, OfertaModulo, Turma, Ata — estrutura curricular completa, incluindo a oferta anual, sem nenhuma Pessoa vinculada.
- Módulo Atribuição: só o que conecta essa estrutura a uma `Pessoa` de verdade — hoje, isso é só `TurmaAluno`.

---

## `TurmaAluno` — desenho preliminar (a refinar quando esta frente for iniciada)

```
TurmaAluno
├── turma            (FK → Turma, de cadastros)
├── pessoa            (FK → Pessoa, de cadastros — o Discente)
├── atribuicao_funcao (FK → AtribuicaoFuncao, de cadastros — liga ao vínculo
│                      geral do Discente com a escola)
├── data_inicio
├── ata_inicio        (FK → Ata, de cadastros)
├── status            (choices: Ativo / Transferido / Aprovado / Reprovado /
│                      Desistente / Matrícula Excluída)
├── data_fim
└── ata_termino       (FK → Ata, de cadastros — só preenchida quando o status
                       significa saída DEFINITIVA da escola, não troca de turma)
```

**Regra fina, confirmada em `docs/29` (Rodada 2), ainda o ponto mais delicado desta frente:** trocar de turma dentro da mesma jornada (Básico → Especializado, ou realocação dentro do mesmo módulo) NÃO gera `ata_termino` — só sair de vez da escola gera. Isso provavelmente exige que `TurmaAluno.status` decida, em alguns casos, fechar também a `AtribuicaoFuncao` correspondente (`situacao` → `INATIVO`) em `cadastros` — um cruzamento entre os dois módulos que precisa ser desenhado com cuidado antes de codar.

---

## Perguntas em aberto para quando esta frente for iniciada de verdade

- [ ] `TurmaAluno` fica num app Django novo (`atribuicao`) ou dentro de `cadastros`? Como agora é uma peça só (não um módulo inteiro de várias entidades), talvez nem justifique um app novo — avaliar quando chegar a hora.
- [ ] Fluxo de atribuição em lote: a secretaria cria uma Turma e adiciona ~300 alunos de uma vez, populando `data_inicio`/`ata_inicio` compartilhados — motivo original de `Ata` ser catálogo (`docs/29`, Rodada 3). Tela ainda não desenhada.
- [ ] Como fica a tela de "editar status do aluno" quando ele sai antes do fim da turma — a pessoa responsável descreveu um fluxo de dois passos (altera status na turma, depois volta em `detalhe.html` da Pessoa pra fechar `AtribuicaoFuncao`). Vale automatizar esse segundo passo quando o status implica saída definitiva?
- [ ] Desenho equivalente para Docente (`TurmaDocente`? — quais turmas ministrou, quais disciplinas) — ainda não desenhado.
- [ ] Relação com "Módulo Atribuição de Instrutor" (já registrado em Fora de Escopo do Kanban antes de `docs/29` existir) — mesma frente, precisa conciliar nomenclatura.
- [ ] Relação com o módulo "Registro de Instrução" (identificado em `docs/31`) e com "Módulo Diário de Classe" (já em Fora de Escopo) — parecem sobrepostos, precisa mapear a fronteira entre os dois antes de decidir se são a mesma coisa.

---

## Próximos passos

1. Implementar primeiro toda a estrutura curricular em `cadastros` (`docs/31`) — item já no Backlog do Kanban.
2. Só depois de `OfertaModulo`/`Turma` existirem e estarem em uso real, dedicar uma sessão específica para desenhar `TurmaAluno` em detalhe — respondendo as perguntas em aberto acima, especialmente a regra de quando fechar `AtribuicaoFuncao` automaticamente.
