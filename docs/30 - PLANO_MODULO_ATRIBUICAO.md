# Plano — Módulo Atribuição (Turmas, Módulos-Ano, Trajetória de Discente/Docente)

**Origem da decisão:** sessão de arquitetura de 03/09/2026, sem código — ver `docs/29 - ANDAMENTO_DO_PROJETO.md` para o raciocínio completo, rodada a rodada. Este documento é o ponto de partida para quando essa frente for de fato iniciada; não é um plano de execução fechado (diferente de `docs/16`, que já tinha todas as Etapas prontas antes de começar).

**Status:** não iniciado — nem os catálogos de apoio (`Ata`, `Módulo`, `SubModulo`, `Turma`) foram implementados ainda em `cadastros` (isso é o próximo item de código, ver Kanban).

**Escala esperada:** comparável à migração `Vinculo`→`Funcao` (múltiplas sessões, app novo ou pelo menos módulo conceitual próprio) — não deve ser implementado "de passagem" dentro de uma sessão do Kanban de `cadastros`.

---

## Princípio arquitetural central (não negociável, confirmado em 03/09/2026)

`cadastros` é a **prateleira**: guarda catálogos de referência, atemporais, reutilizáveis por qualquer módulo (`Funcao`, `Disciplina`, `VinculoFormal`, e agora `Ata`, `Módulo`, `SubModulo`, `Turma`). `cadastros` NUNCA guarda o **evento de vínculo** de uma trajetória — quem passou por qual Turma, quando, com qual Ata, em qual situação. Isso é responsabilidade do módulo Atribuição.

`AtribuicaoFuncao` (em `cadastros`) continua sendo só "Pessoa tem Função X, de tal data a tal data, ativo ou não" — a vida da pessoa **na escola**, no nível mais alto. A trajetória detalhada (turmas, disciplinas ministradas, treinamentos) é dado de outros módulos, só **exibido** na tela de detalhe de `cadastros`.

---

## Conceitos já desenhados (ver `docs/29`, Rodadas 4-8)

### Catálogos (vivem em `cadastros`, implementação já especificada, ainda não codada)

```
Modulo (nome único: "Básico", "Especializado em Aviônica", "Especializado em Célula",
        "Especializado em GMP", "Extra")
  └─ SubModulo (FK → Modulo; nome — ex: "Performance Humana e Limitações", "Conhecimentos Aplicados")
       └─ Disciplina (FK → SubModulo, opcional por enquanto; conteudo_programatico novo)

Turma (FK → Modulo; nome; ano_letivo) — só cadastro, sem aluno vinculado ainda

Ata (numero único; tipo Ordinária/Extraordinária; data) — catálogo, sem uso ainda
    em nenhum Model de cadastros; existe pronto para o módulo Atribuição consumir
```

### Conceitos do futuro módulo Atribuição (ainda não modelados em detalhe — é o trabalho desta frente)

- **`ModuloAno`** (nome provisório) — une o `Módulo` genérico (produto processado, atemporal) a um ano letivo específico + Docentes específicos (de `cadastros`) responsáveis por cada Disciplina naquele ano. É o "produto pronto pra consumo" daquele ciclo letivo — reaproveita a mesma estrutura curricular todo ano, sem duplicá-la.
- **`TurmaAluno`** — conecta um Discente a uma `Turma`, dentro de um `ModuloAno`, com:
  - `data_inicio`, `ata_inicio_vinculo` (FK → `Ata`)
  - `status` (Ativo / Transferido / Aprovado / Reprovado / Desistente / Matrícula Excluída)
  - `data_fim`, `ata_termino_vinculo` (FK → `Ata`, só preenchida quando o status significa saída **definitiva da escola**, não troca de turma)
- **Regra fina, já confirmada em `docs/29` (Rodada 2):** trocar de turma dentro da mesma jornada (Básico → Especializado, ou realocação dentro do mesmo módulo) NÃO gera Ata de Término — só sair de vez da escola gera. Essa distinção é o ponto mais delicado da implementação futura, porque provavelmente cruza `TurmaAluno.status` com o fechamento de `AtribuicaoFuncao` (`situacao` → `INATIVO`) em `cadastros`.
- **Fluxo de atribuição em lote:** a secretaria cria uma Turma e popula ~300 alunos de uma vez (Data de Início + Ata de Início compartilhada por todos) — motivo original de `Ata` virar catálogo em vez de texto livre repetido (`docs/29`, Rodada 3). A interface para isso (criar turma → adicionar N alunos → popular campos em lote) ainda não foi desenhada.

---

## Perguntas em aberto para quando esta frente for iniciada de verdade

- [ ] `ModuloAno` é o nome certo, ou existe um termo melhor (evitar confusão com "Módulo Atribuição" como nome do app/frente inteira)?
- [ ] `TurmaAluno` fica num app Django novo (`atribuicao`) ou dentro de `cadastros`? (Recomendação preliminar, não decidida: app novo — `cadastros` é "escritor" do catálogo compartilhado, consumido por outros apps, conforme precedente já estabelecido na sessão 17.)
- [ ] Como fica a tela de "editar status do aluno" quando ele sai antes do fim da turma (a pessoa responsável descreveu: altera status na turma primeiro, depois precisa voltar em `detalhe.html` da Pessoa pra fechar `AtribuicaoFuncao` com Data Fim/Ata — dois passos, dois lugares). Vale um mecanismo que sincronize os dois automaticamente quando o status significa saída definitiva?
- [ ] Desenho equivalente para Docente: "quais turmas ministrou, quais disciplinas nessas turmas" — é uma tabela de junção parecida (`TurmaDocente`? `ModuloAnoDocenteDisciplina`?), ainda não desenhada nesta sessão.
- [ ] Relação com o item já registrado em "Fora de Escopo" do Kanban, "Módulo Atribuição de Instrutor" — é a mesma frente, ou uma frente distinta que também precisa ser conciliada aqui?
- [ ] Onde entra o módulo Treinamento (mencionado como consumidor futuro do catálogo de `cadastros`, ver sessão 17) em relação a `ModuloAno`/Capacidade do Docente?

---

## Próximos passos

1. Implementar primeiro os catálogos de apoio em `cadastros` (`Ata`, `Módulo`, `SubModulo`, `Turma`, `Disciplina.submodulo`/`conteudo_programatico`) — item já no Backlog do Kanban, desbloqueado e pronto pra codar.
2. Só depois de os catálogos existirem e estarem em uso (mesmo que só via Admin), dedicar uma sessão específica para detalhar este plano — respondendo as perguntas em aberto acima e escrevendo as Etapas de execução, no mesmo formato de `docs/16`.
