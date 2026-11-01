# Fechamento — Estrutura Curricular (9 tabelas, versão final)

**Origem:** sessão de validação campo-a-campo em 04-05/09/2026 (continuação de `docs/29`/`docs/30`/`docs/31`/`docs/32`). Cada tabela foi discutida individualmente antes de qualquer código — este documento é a **versão final e definitiva** do desenho, pronta para virar `models.py`/migration/`admin.py`. Em caso de divergência com qualquer versão anterior (`docs/31`, o `.txt` original da pessoa responsável), **este documento prevalece**.

**Status:** desenho fechado, código ainda não escrito.

---

## 1. `Disciplina` (ajustada — já existe, campos mudam)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | BigAutoField | PK |
| `nome` | CharField(100) | `unique=True` — sem mudança |
| `sigla` | CharField(3) | `unique=True`, `RegexValidator` (3 letras maiúsculas) — sem mudança |
| `ativo` | BooleanField | `default=True` — **novo** |
| `carga_horaria_programa_de_instrucao` | DecimalField(6,2) | obrigatório — valor fixo do PI aprovado pela ANAC — **novo** |
| `carga_horaria_teorica` | DecimalField(6,2) | obrigatório, digitado — **novo** |
| `carga_horaria_pratica` | DecimalField(6,2) | obrigatório, digitado — **novo** |

**Removidos:** `carga_horaria` (`IntegerField` antigo — confirmado sem uso fora de `models.py`/`migrations/0001_initial.py`; `RemoveField` direto, sem preservação de dado) e `conteudo_programatico` (nunca chegou a existir como campo — vira tabela própria, item 2).

**Calculados (property Python, não gravados):**
```python
carga_horaria_total = carga_horaria_teorica + carga_horaria_pratica
hora_aula_total = carga_horaria_total / 0.75
hora_aula_pratica = carga_horaria_pratica / 0.75
hora_aula_teorica = carga_horaria_teorica / 0.75
```

**Validação bloqueante, em `Model.clean()`:**
```python
if carga_horaria_total != carga_horaria_programa_de_instrucao:
    raise ValidationError("... não bate com o Programa de Instrução aprovado ...")
```
Motivo do peso dessa regra: descumprimento do PI aprovado pode gerar notificação da ANAC à escola (risco real, não só validação de dado).

**⚠️ Risco identificado, registrado no Backlog:** `Model.clean()` só dispara automaticamente no Admin/`ModelForm` — **não** dispara num `Model.objects.create()` direto (Service, script, importação em lote). Quando a população de `Disciplina` vier por planilha Excel (decisão já tomada pela pessoa responsável), o script de importação precisa chamar `full_clean()` explicitamente por linha, ou a trava de conformidade simplesmente não roda nesse caminho.

---

## 2. `ConteudoProgramatico` (nova)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | BigAutoField | PK |
| `disciplina` | FK → `Disciplina` | obrigatório, **`on_delete=PROTECT`** |
| `ordem` | PositiveSmallIntegerField | obrigatório |
| `descricao` | TextField | obrigatório |
| `observacao` | TextField | `blank=True` |
| `ativo` | BooleanField | `default=True` |

`UNIQUE(disciplina, ordem)`.

**`ordem` — esclarecido explicitamente pela pessoa responsável:** o Conteúdo Programático é uma **trilha para o professor, não um trilho** — o instrutor decide a sequência real de ensino com base nos conhecimentos prévios e lacunas cognitivas daquela turma específica. `ordem` serve só para **organizar a exibição no cadastro** (evitar ordem alfabética arbitrária), sem nenhuma regra de negócio associada, sem obrigar o instrutor a seguir aquela sequência. Mesmo princípio aplicado a `SubModuloDisciplina.ordem` e `ModuloSubModulo.ordem` (itens 4 e 6).

**`PROTECT`, não `CASCADE`:** decisão motivada por uma preocupação real da pessoa responsável — perder rastreabilidade do que foi ministrado se uma Disciplina for excluída. Com `PROTECT`, não é possível excluir uma `Disciplina` que já tenha Conteúdo Programático, forçando `ativo=False` em vez de exclusão física.

### Nota de arquitetura para o futuro Registro de Instrução (importante, evita erro de granularidade)

Durante a discussão, uma conta inicial da pessoa responsável estimava ~40 mil registros/ano (400 mil em 10 anos) multiplicando "linhas de CP × alunos da turma" — number that seemed high enough to shape the design. Duas correções:

1. **Volume não é problema real:** 400 mil linhas em 10 anos é irrelevante para qualquer banco relacional (SQLite incluso) — não deveria influenciar a arquitetura.
2. **A premissa do cálculo estava errada, e essa correção sim importa:** "o que foi ministrado" não deveria multiplicar por aluno — um professor ministra um assunto **uma vez pra turma inteira**, não uma vez por aluno. O futuro Registro de Instrução provavelmente precisa de **3 tabelas com granularidades diferentes**, nenhuma delas cruzando CP×Aluno:
   - `ExecucaoConteudoProgramatico` (FK → `ConteudoProgramatico`, FK → `Turma`, `data`, `tipo_aula`) — "isso foi dado, nesse dia, pra essa turma".
   - `Frequencia` (FK → `TurmaAluno`, `data_aula`, `presente`) — por aluno, mas por **sessão de aula**, não por linha de CP.
   - `Avaliacao`/`NotaAvaliacao` (FK → `TurmaAluno`, nota) — por aluno, só nos momentos de avaliação.

   Registrado aqui para não ser esquecido quando o módulo Registro de Instrução for desenhado de verdade (ver `docs/32`).

---

## 3. `SubModulo` (nova)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | BigAutoField | PK |
| `nome` | CharField(150) | obrigatório |
| `sigla` | CharField(3) | obrigatório, `unique=True`, `RegexValidator` (3 letras maiúsculas — mesmo validador de `Disciplina.sigla`) |
| `carga_horaria` | — | **calculado** (soma via `SubModuloDisciplina`, não editável, não pode divergir do Programa de Instrução aprovado) |
| `ativo` | BooleanField | `default=True` |

**Padrão identificado:** `Disciplina`, `SubModulo` e `Modulo` (item 5) compartilham exatamente a mesma "forma" — `nome` + `sigla` (3 letras, regex, única) + `ativo`. Vale extrair uma classe abstrata comum (`AbstractCatalogoComSigla` ou nome equivalente) na hora de codar, para não repetir o validador e os campos em 3 lugares.

---

## 4. `SubModuloDisciplina` (tabela intermediária, nova)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | BigAutoField | PK |
| `submodulo` | FK → `SubModulo` | obrigatório, `on_delete=PROTECT` |
| `disciplina` | FK → `Disciplina` | obrigatório, `on_delete=PROTECT` |
| `ordem` | PositiveSmallIntegerField | obrigatório — mesmo espírito "sem regra de negócio" do item 2 |

`UNIQUE(submodulo, disciplina)` + `UNIQUE(submodulo, ordem)`.

---

## 5. `Modulo` (nova)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | BigAutoField | PK |
| `nome` | CharField(150) | `unique=True`, texto livre (não `choices`) — "Básico", "Especializado em Aviônica", etc. |
| `sigla` | CharField(3) | obrigatório, `unique=True`, `RegexValidator` (3 letras maiúsculas) |
| `descricao` | TextField | `blank=True` |
| `ativo` | BooleanField | `default=True` |

**Motivo prático da sigla, além de padronização:** hábito da escola de usar siglas na geração de PDFs (relatórios, certificados) — ver nota de composição de nome no item 8.

---

## 6. `ModuloSubModulo` (tabela intermediária, nova)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | BigAutoField | PK |
| `modulo` | FK → `Modulo` | obrigatório, `on_delete=PROTECT` |
| `submodulo` | FK → `SubModulo` | obrigatório, `on_delete=PROTECT` |
| `ordem` | PositiveSmallIntegerField | obrigatório — mesmo espírito "sem regra de negócio" |

`UNIQUE(modulo, submodulo)` + `UNIQUE(modulo, ordem)`.

---

## 7. `OfertaModulo` (nova)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | BigAutoField | PK |
| `modulo` | FK → `Modulo` | obrigatório, `on_delete=PROTECT` |
| `ano_letivo` | PositiveSmallIntegerField | obrigatório |
| `data_inicio` | DateField | **obrigatório no cadastro** |
| `data_fim` | DateField | `null=True, blank=True` — só obrigatório na tela/popup futura de "Encerrar" |
| `ativo` | BooleanField | `default=True` |
| `observacao` | TextField | `blank=True` |

**Removidos da proposta original:** `periodo` (migrou para `Turma` — uma mesma Oferta pode ter turmas em turnos diferentes, ex: Básico 2026 no vespertino e no noturno ao mesmo tempo) e `situacao` (substituído por `ativo`, mesmo padrão simples de `AtribuicaoFuncao`).

**Padrão consciente, replicado de `AtribuicaoFuncao`:** cadastro pede só `data_inicio`; `data_fim` só é exigida no momento de encerrar (botão/popup dedicado, quando essa tela existir) — evita pedir uma data que ninguém tem no momento do cadastro.

---

## 8. `Turma` (nova)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | BigAutoField | PK |
| `oferta_modulo` | FK → `OfertaModulo` | obrigatório, `on_delete=PROTECT` |
| `nome` | CharField(100) | obrigatório |
| `sigla` | CharField(10) | obrigatório — **texto livre, sem regex** (diferente dos catálogos de item 1/3/5), pode ter espaço (ex: "CEL NOT II", "BAS NOT") |
| `periodo` | CharField + `choices` | MATUTINO / VESPERTINO / NOTURNO |
| `capacidade_maxima` | PositiveSmallIntegerField | opcional |
| `situacao` | CharField + `choices` | PLANEJADA / EM_ANDAMENTO / ENCERRADA — editado manualmente pelo Admin por enquanto |
| `observacao` | TextField | `blank=True` |

`UNIQUE(oferta_modulo, sigla)`.

**Sem `data_inicio`/`data_fim` própria** — `Turma` herda as datas de `OfertaModulo` (confirmado pela pessoa responsável).

**Nota para o futuro módulo Relatórios (`docs/32`), não implementar agora:** a convenção de nome usada em documentos oficiais (ex: "2026 BAS NOT R3 MAT") é uma **composição calculada na hora de gerar o PDF**, não um campo gravado: `oferta_modulo.ano_letivo` + `oferta_modulo.modulo.sigla` + `turma.sigla` + `disciplina.sigla`. Se a sigla de um Módulo mudar no futuro, qualquer PDF novo já reflete a mudança automaticamente, sem precisar re-gravar nada.

---

## 9. `Ata` (nova)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | BigAutoField | PK |
| `numero` | CharField(20) | `unique=True` |
| `tipo` | CharField + `choices` | ORDINARIA / EXTRAORDINARIA |
| `finalidade` | CharField + `choices` | INICIO_VINCULO / TERMINO_VINCULO / ORIENTACAO / CONSELHO_ENSINO / OUTRO |
| `data` | DateField | obrigatório |
| `assunto` | CharField(255) | opcional |
| `observacao` | TextField | `blank=True` |

**`tipo` e `finalidade` são eixos independentes**, um não determina o outro — ex: uma Ata de finalidade Término de Vínculo pode ser tipo Ordinária (reunião de calendário normal) ou Extraordinária (reunião de emergência). `finalidade` é `choices` de escolha única (não múltipla) — confirmado pela pessoa responsável.

**Cardinalidade de uso, esclarecida (não afeta o desenho da própria tabela, só como ela será referenciada por outras tabelas futuras):**
- Ata Ordinária de Início/Término de Vínculo → referenciada por **muitos** alunos de uma vez (motivo original de `Ata` ser catálogo — evita repetir texto pra ~300 registros).
- Ata Extraordinária de Término → referenciada por **poucos** alunos (1 a ~10), tratado manualmente.
- Ata de Conselho de Ensino → referenciada por **1** aluno só (individual).

Sem `ativo` — uma Ata é, por natureza, um registro histórico fechado; não faz sentido "desativar" uma Ata.

---

## Itens de Backlog gerados ao longo desta sessão de validação

- [ ] **Importação de `Disciplina` via planilha Excel** — colunas correspondentes aos campos do Model; o script precisa chamar `full_clean()` explicitamente por linha (`Model.clean()` não dispara sozinho fora do Admin/`ModelForm`) para não pular a validação de conformidade com o Programa de Instrução aprovado pela ANAC.
- [ ] **3 tabelas futuras do Registro de Instrução** (`ExecucaoConteudoProgramatico`, `Frequencia`, `Avaliacao`/`NotaAvaliacao`) — granularidades diferentes, nenhuma cruza CP×Aluno. Ver nota completa no item 2 acima.
- [ ] **Classe abstrata compartilhada** para `Disciplina`/`SubModulo`/`Modulo` (mesma forma: `nome` + `sigla` regex única + `ativo`) — decisão de implementação, não de modelagem de dado.
- [ ] **Registro de Ata de Conselho de Ensino na vida do Discente** — mostrar, no futuro (`detalhe.html` ou módulo Relatório/Dashboard), quais Atas de Conselho de Ensino um Discente específico passou. Depende de uma relação própria Pessoa↔Ata para essa finalidade (diferente de `TurmaAluno.ata_inicio`/`ata_termino`, que é sempre em lote/pouco, não individual).
- [ ] **Composição de nome para PDFs/Relatórios** (ano + sigla Módulo + sigla Turma + sigla Disciplina) — calculada na hora de gerar o documento, não gravada. Ver nota completa no item 8.
- [ ] **Cadeia de `PROTECT`** aplicada consistentemente do topo (`Disciplina`/`Modulo`) até a ponta (`ConteudoProgramatico`, `SubModuloDisciplina`, `ModuloSubModulo`, `OfertaModulo`, `Turma`) — nenhuma exclusão física possível em nenhum nível, só `ativo=False`. Confirmar que essa cadeia se mantém íntegra na implementação (nenhum `CASCADE` escapou por engano).

---

## Próximos passos (confirmados pela pessoa responsável em 05/09/2026)

1. Implementar as 9 tabelas: `models.py`, migrations, `admin.py` (Admin-only por enquanto, sem CRUD dedicado ainda, seguindo o padrão já usado por `Funcao`/`VinculoFormal`).
2. **Depois** de implementadas: telas de CRUD dedicadas, "onde for aplicado" (escopo de quais catálogos precisam de tela própria vs. continuam só Admin ainda não definido — precisa de discussão de escopo antes de codar, seguindo o mesmo processo desta sessão).
3. Construir uma **tela de navegação inicial** (escopo ainda não definido — precisa de discussão antes de codar).
4. Motivação explícita da pessoa responsável para essa sequência: **operar o sistema de ponta a ponta** para identificar pontos pequenos de melhoria na prática, não só no desenho.
