# Plano — Módulo Atribuição (Discente ↔ Turma)

**Origem:** série de conversas em 07/09/2026, entre a pessoa responsável e outra IA (documento "Modelagem — Vínculo do Discente com a Turma"), refinada nesta conversa. Consolida e **substitui** o esboço anterior (`docs/30`) na parte de Discente — `docs/30` continua válido como registro histórico do raciocínio inicial, mas este documento é a referência definitiva para implementação.

**Status:** desenho fechado na maior parte; 2 pontos seguem em aberto (marcados abaixo). Nenhum código escrito ainda.

**Escala:** comparável à migração `Vinculo→Funcao` — app novo, Model com máquina de estado, múltiplos Services, mudança de comportamento em `cadastros` (correção de bug + consolidação de campo). Implementar em etapas, cada uma testável isoladamente.

---

## 1. Princípio arquitetural (fronteira entre `cadastros` e `atribuicao`)

- **`cadastros` continua dono do ciclo de vida de `Pessoa`/`AtribuicaoFuncao`/`Ata`/`Turma`/`Modulo`** — inclusive das regras "o que significa um vínculo estar ativo/inativo".
- **`atribuicao` (app novo) identifica eventos** (matrícula em turma, relocação, reprovação, encerramento de turma) **mas nunca escreve direto nos Models de `cadastros`.**
- **A comunicação entre os dois é por Services expostos por `cadastros`**, não por acesso direto a `AtribuicaoFuncao`/`Ata` a partir de `atribuicao`. Reduz acoplamento, mantém a regra de negócio de "como fechar um vínculo" no dono do dado.
- `MatriculaTurma` (novo, em `atribuicao`) controla exclusivamente a relação Discente↔Turma — não duplica nem substitui `AtribuicaoFuncao`.

---

## 2. Pré-requisitos em `cadastros` (Etapa 0 — sem tela nova, só schema + Services)

### 2.1 — Consolidar `AtribuicaoFuncao.situacao`/`ativo`

Hoje `AtribuicaoFuncao` tem dois campos redundantes (`situacao` texto livre, `ativo` booleano), nenhum editável por tela nenhuma até hoje. Consolidar em um só:

```python
class SituacaoAtribuicao(models.TextChoices):
    ATIVO = 'ATIVO', 'Ativo'
    INATIVO = 'INATIVO', 'Inativo'
```
`situacao` vira `CharField(choices=SituacaoAtribuicao.choices, default=ATIVO)`; `ativo` (booleano) é removido. Migration com passo de dado: normalizar `situacao` a partir do `ativo` existente antes de remover (mesmo padrão já usado antes nesta série de sessões).

**Confirmado:** binário só — `ATIVO`/`INATIVO`. A distinção fina (`Aguardando Atribuição`/`Aguardando Turma`) é só de **exibição**, calculada olhando `MatriculaTurma`, nunca gravada em `situacao` (ver seção 6).

### 2.2 — Corrigir bug: "já é Discente" não filtra por situação

Hoje (`CadastrarPessoaComFuncaoService`):
```python
ja_e_discente = pessoa.atribuicoes.filter(dados_discente__isnull=False).exists()
```
Bloqueia mesmo se a `AtribuicaoFuncao` Discente já estiver `INATIVO` (aluno que já se formou/foi embora). Corrigir para:
```python
ja_e_discente_ativo = pessoa.atribuicoes.filter(dados_discente__isnull=False, situacao='ATIVO').exists()
```
Cada passagem pela EMCA como Discente é sua própria `AtribuicaoFuncao` — a Pessoa pode acumular várias ao longo da vida (fechadas + no máximo uma ativa por vez, exceto Extracurricular, ver seção 7).

### 2.3 — Novo campo: `Modulo.categoria`

```python
class CategoriaModulo(models.TextChoices):
    BASICO = 'BASICO', 'Básico'
    ESPECIALIZADO = 'ESPECIALIZADO', 'Especializado'
    EXTRACURRICULAR = 'EXTRACURRICULAR', 'Extracurricular'
```
`Modulo.nome` continua livre (como já é — "Básico", "Especializado em Aviônica", etc.); `categoria` é o campo estruturado que a regra de negócio usa pra decidir se encerrar uma Turma daquele Módulo fecha o vínculo Discente ou não.

### 2.4 — Novos Services em `cadastros/services.py`

```python
class EncerrarVinculoService:
    """
    Encerra qualquer AtribuicaoFuncao — Discente, Docente ou Gestão. Sem Ata:
    a Ata de encerramento (quando existir) vive em MatriculaTurma, não aqui —
    decisão confirmada em 07/09/2026 (AtribuicaoFuncao não guarda Ata).
    """
    def executar(self, atribuicao_funcao, data_fim):
        atribuicao_funcao.situacao = SituacaoAtribuicao.INATIVO
        atribuicao_funcao.data_fim = data_fim
        atribuicao_funcao.save()


class ObterOuCriarAtribuicaoDiscenteService:
    """
    Usado pelo módulo Atribuição ao matricular alguém numa Turma (regular ou
    extracurricular). Reaproveita a AtribuicaoFuncao Discente ATIVA existente,
    se houver; senão cria uma nova (mínima — sem CANAC, sem nenhum requisito
    de aluno regular, já opcionais em DadosDiscente hoje). Nunca reabre uma
    AtribuicaoFuncao já INATIVA.
    """
    def executar(self, pessoa):
        ativa = pessoa.atribuicoes.filter(dados_discente__isnull=False, situacao='ATIVO').first()
        if ativa:
            return ativa
        funcao_discente = Funcao.objects.get(categoria=CategoriaFuncao.DISCENTE)
        nova = AtribuicaoFuncao.objects.create(
            pessoa=pessoa, funcao=funcao_discente,
            situacao=SituacaoAtribuicao.ATIVO, data_inicio=timezone.now().date(),
        )
        DadosDiscente.objects.create(atribuicao=nova)
        return nova
```

**Nota:** não existe "AtivarVinculoDiscenteService" separado — a ativação já acontece na criação (`situacao=ATIVO` por padrão), seja no cadastro inicial de Pessoa (já existente) ou nesta função acima (matrícula direta em Extracurricular sem cadastro prévio).

---

## 3. App novo `atribuicao` — `MatriculaTurma`

```python
class StatusMatriculaTurma(models.TextChoices):
    CURSANDO = 'CURSANDO', 'Cursando'
    APROVADO = 'APROVADO', 'Aprovado'
    RELOCADO = 'RELOCADO', 'Relocado'
    TRANSFERIDO = 'TRANSFERIDO', 'Transferido'
    REPROVADO = 'REPROVADO', 'Reprovado'
    MATRICULA_EXCLUIDA = 'MATRICULA_EXCLUIDA', 'Matrícula Excluída'


class MotivoSaida(models.TextChoices):
    """Só preenchido quando status=TRANSFERIDO. MATRICULA_EXCLUIDA já é abandono por definição, sem campo extra."""
    ABANDONOU = 'ABANDONOU', 'Desistente - Abandonou'
    SOLICITOU = 'SOLICITOU', 'Desistente - Solicitou'


class MatriculaTurma(models.Model):
    atribuicao_funcao = models.ForeignKey('cadastros.AtribuicaoFuncao', on_delete=models.PROTECT, related_name='matriculas_turma')
    turma = models.ForeignKey('cadastros.Turma', on_delete=models.PROTECT, related_name='matriculas')

    # Atribuído em "Finalizar Planejamento" (ordem alfabética) ou ao entrar
    # numa turma já EM_ANDAMENTO (MAX+1) — nunca muda depois de atribuído
    # (professores/secretaria referenciam "aluno nº 22" em registros formais).
    numero_na_turma = models.PositiveSmallIntegerField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=StatusMatriculaTurma.choices, default=StatusMatriculaTurma.CURSANDO)
    motivo_saida = models.CharField(max_length=20, choices=MotivoSaida.choices, blank=True)

    # Vazios enquanto a Turma está PLANEJADA; preenchidos em massa (ou individualmente,
    # em caso de relocação/saída no meio do ano) quando o status ganha uma data.
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)
    ata_inicio = models.ForeignKey('cadastros.Ata', on_delete=models.PROTECT, null=True, blank=True, related_name='+')
    ata_encerramento = models.ForeignKey('cadastros.Ata', on_delete=models.PROTECT, null=True, blank=True, related_name='+')

    observacao = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['atribuicao_funcao', 'turma'], name='unique_atribuicao_por_turma'),
            models.UniqueConstraint(fields=['turma', 'numero_na_turma'], name='unique_numero_por_turma'),
        ]
```

**Regra confirmada:** nunca há Delete físico de `MatriculaTurma` depois que a Turma sai de `PLANEJADA` — só enquanto `PLANEJADA` (CRUD livre). Depois disso, tudo é mudança de `status`, gerando uma nova "foto" na consulta de histórico (ver seção 6) — mas fisicamente, cada mudança de status **atualiza a mesma linha** de `MatriculaTurma`? Ou cria uma linha nova? **Confirmado: cria uma linha nova em relocação** (2 operações — fecha a antiga com `RELOCADO`+`data_fim`, cria uma nova `CURSANDO` na turma destino). Pra Reprovado/Transferido/Matrícula Excluída, **atualiza a mesma linha** (não é troca de turma, é fim de linha na mesma turma).

---

## 4. Máquina de estado de `Turma.situacao`

`PLANEJADA → EM_ANDAMENTO → ENCERRADA`, **só nesse sentido** — nunca volta, exceto via Django Admin diretamente (nenhuma tela do sistema permite reverter). Toda transição roda dentro de um Service próprio em `atribuicao`, nunca só um `save()` de campo solto.

### 4.1 — Enquanto `PLANEJADA`

- CRUD livre de `MatriculaTurma`: **+ Adicionar Aluno** (popup: seleciona Pessoa com `AtribuicaoFuncao` Discente `ATIVO` "aguardando atribuição" — ou qualquer Pessoa, se a Turma for `Modulo.categoria=EXTRACURRICULAR`, ver seção 7; pede Código de Matrícula ANAC; insere em ordem alfabética — sem `numero_na_turma` ainda), **Editar/Excluir** por linha (popup: corrige CANAC, ou remove a linha — Delete físico permitido só aqui).

### 4.2 — Botão "Finalizar Planejamento"

1. Aviso: ação não pode ser desfeita.
2. Popup: pede `data_inicio` + `ata_inicio` (finalidade `INICIO_VINCULO`).
3. Em massa, para cada `MatriculaTurma` da Turma: atribui `numero_na_turma` (ordem alfabética por nome da Pessoa, sequencial a partir de 1), grava `data_inicio`/`ata_inicio`.
4. `Turma.situacao → EM_ANDAMENTO`.
5. A partir daqui, essas linhas passam a aparecer no "Sumário Histórico de Vínculos" de cada Pessoa (antes de ter `data_inicio`, a linha existe no banco mas não aparece no histórico).

### 4.3 — Enquanto `EM_ANDAMENTO`

- **+ Adicionar Aluno** continua disponível (só para Relocados de outra turma, ou entrada nova em Extracurricular) — entra no fim da lista (`numero_na_turma = MAX+1` daquela Turma), sem popup de CANAC (Discente relocado já tem).
- **Editar/CRU** por linha: **sem Excluir físico** (botão de excluir some) — só edição de `status` (choice: `RELOCADO`/`REPROVADO`/`TRANSFERIDO` com `motivo_saida`/`MATRICULA_EXCLUIDA`).
  - `RELOCADO`: fecha a linha atual (`data_fim`=hoje), abre uma `MatriculaTurma` nova na Turma destino (`CURSANDO`, sem `data_fim`). Não mexe em `AtribuicaoFuncao` (vínculo institucional continua `ATIVO`, sem Ata).
  - `REPROVADO`/`TRANSFERIDO`/`MATRICULA_EXCLUIDA`: **sempre** fim de ciclo do aluno na EMCA, independente do `Modulo.categoria` (seção 8-B, fechada em 07/09/2026) — pede `data_fim` + `ata_encerramento`; chama `EncerrarVinculoService` sobre a `AtribuicaoFuncao` correspondente.

### 4.4 — Botão "Encerrar Turma" (2 cliques)

**1º clique:**
- Popup de aviso com **lista de revisão pré-aprovação** (seção 8-A — checkbox "Aprovar" por aluno, marcado por padrão, desmarcável) → confirma → todo `CURSANDO` ainda marcado vira `APROVADO` em massa; quem foi desmarcado continua `CURSANDO`, bloqueando o 2º clique até ser resolvido individualmente. `Turma.situacao` continua `EM_ANDAMENTO`.

**2º clique** (só disponível quando não sobra ninguém `CURSANDO`):
- Se `Modulo.categoria = BASICO` (ou `EXTRACURRICULAR`, conforme fechamento da seção 7): popup pede só `data_fim` da Turma; todo `APROVADO` fica "Aguardando Turma" (`AtribuicaoFuncao` continua `ATIVO`, sem Ata).
- Se `Modulo.categoria = ESPECIALIZADO`: popup pede `data_fim` + `ata_encerramento` (preenchimento em massa); todo `APROVADO` recebe essa Ata em `MatriculaTurma.ata_encerramento`, e `EncerrarVinculoService` fecha a `AtribuicaoFuncao` de cada um (`INATIVO`).
- `Turma.situacao → ENCERRADA`.

---

## 5. Interface visual — pontos já combinados (sem impacto de schema)

- **Sequência das 3 fases é uma "workflow"** (Planejada → Em Andamento → Encerrada, com a atual destacada), não 3 telas separadas.
- **Formatação condicional por `status`** na tabela de composição da Turma: Reprovado = vermelho `#FF0000`/texto branco; Aprovado = azul `#002060`/texto branco; Cursando = verde `#92D050`/texto branco; outros estados = laranja `#FFC000`/texto preto.
- **"Nr" (numero_na_turma) nunca é recalculado na exibição** — é o campo gravado (seção 3), não uma numeração de linha da tabela.

---

## 6. "Sumário Histórico de Vínculos" (renomeado de "Funções")

Rótulo único pra qualquer categoria (Discente/Docente/Gestão) — decisão confirmada, porque uma Pessoa pode acumular papéis ao longo da vida (ex: foi Discente, depois Instrutor), e um rótulo condicional por categoria criaria inconsistência.

**Não é uma tabela nova no banco.** É uma consulta que junta, por `AtribuicaoFuncao`:
- **Docente/Gestão:** 1 ou 2 linhas por `AtribuicaoFuncao` — uma linha "Ativo" (`data_inicio`), e se `data_fim` estiver preenchida, uma segunda linha "Inativo" (`data_fim`). Sem Turma, sem Ata.
- **Discente:** uma linha por `MatriculaTurma` daquela `AtribuicaoFuncao`, na ordem em que aconteceram — `situacao` mostrada é sempre o valor atual de `AtribuicaoFuncao.situacao` (não muda por linha; é o "estado do vínculo institucional" enquanto aquele evento acontecia), colunas Ata/Data/Turma/Status vêm de `MatriculaTurma`.

### "Situação calculada" exibida para Discente (não gravada em nenhum campo)

| Condição (última `MatriculaTurma` da `AtribuicaoFuncao`) | Situação exibida |
|---|---|
| Nenhuma `MatriculaTurma` ainda | **Aguardando Atribuição** |
| `RELOCADO`, ou `APROVADO` numa Turma de `Modulo.categoria=BASICO` (ou `EXTRACURRICULAR`, ❓ ver seção 7) | **Aguardando Turma** |
| `CURSANDO` | **Ativo** |
| `REPROVADO`/`TRANSFERIDO`/`MATRICULA_EXCLUIDA`, ou `APROVADO` numa Turma `ESPECIALIZADO` | **Inativo** |

**Motivo confirmado pela pessoa responsável:** essa régua serve de ferramenta de auditoria — "todo Discente `ATIVO` que está em Aguardando Atribuição/Aguardando Turma há muito tempo" é literalmente o relatório de "quem está perdido no sistema, sem turma".

---

## 7. Regra de Turma Extracurricular

- **Quem pode entrar:** qualquer Pessoa — já foi aluna, é aluna ativa agora, ou nunca foi aluna da EMCA.
- **`MatriculaTurma` sempre aponta pra `AtribuicaoFuncao`** (nunca FK direta pra `Pessoa`) — mantém uniformidade estrutural e garante que Extracurricular apareça no Sumário Histórico de Vínculos.
- **Ao matricular:** usa `ObterOuCriarAtribuicaoDiscenteService` (seção 2.4) — reaproveita a `AtribuicaoFuncao` Discente `ATIVO` existente (se a Pessoa já é aluna regular agora, acumula sem criar nada novo); senão, cria uma nova `AtribuicaoFuncao` mínima (nunca reabre uma já `INATIVO`).
- **Pode acumular várias Turmas Extracurriculares ao mesmo tempo** (`UNIQUE(atribuicao_funcao, turma)` impede duplicidade na mesma Turma, mas não entre Turmas diferentes).
- ❓ **Em aberto:** quando um Extracurricular termina, ele fecha o vínculo (`INATIVO`) só se essa `AtribuicaoFuncao` **não estiver também associada a uma Turma regular ativa** (Básico/Especializado) ao mesmo tempo — ou seja, "quem acumula" não pode ter o vínculo fechado por causa do Extra terminando, já que o vínculo pertence, na prática, ao curso regular. Confirmado o princípio; a regra de implementação exata (como o Service de encerramento sabe "não fechar, porque tem outra Turma regular ativa pendurada na mesma `AtribuicaoFuncao`") ainda precisa ser desenhada — provável checagem antes de chamar `EncerrarVinculoService`: existe alguma outra `MatriculaTurma` `CURSANDO` na mesma `AtribuicaoFuncao`, numa Turma não-Extracurricular? Se sim, não fecha.

---

## 8. Perguntas em aberto (não bloqueiam o início da implementação, mas precisam ser fechadas antes das Etapas correspondentes)

### 8-A — Revisão pré-aprovação em massa (seção 4.4, 1º clique) — ✅ FECHADA em 07/09/2026

**Decisão confirmada:** o 1º clique em "Encerrar Turma" abre uma lista de revisão com todos os alunos ainda `CURSANDO`, cada um com uma caixa "Aprovar" marcada por padrão — editável individualmente antes de confirmar. Quem for desmarcado fica de fora da promoção em massa (permanece `CURSANDO`, precisa ser resolvido individualmente via Editar/CRU antes de a Turma poder ser encerrada de vez, ver seção 4.4 e regra da seção 12 do documento original).

### 8-B — Encerramento individual em Turma Básico — ✅ FECHADA em 07/09/2026

**Decisão:** `REPROVADO`/`TRANSFERIDO`/`MATRICULA_EXCLUIDA` é sempre fim de ciclo do aluno na EMCA — **independente do `Modulo.categoria`** (Básico ou Especializado) e independente de ser resolvido individualmente no meio do ano ou antes do fechamento em massa da Turma. Sempre exige `ata_encerramento` em `MatriculaTurma` e sempre chama `EncerrarVinculoService` (`AtribuicaoFuncao → INATIVO`).

Isso restringe a distinção Básico/Especializado a **um único lugar**: a promoção `APROVADO` em massa no "Encerrar Turma" (seção 4.4) — Básico aprovado vira "Aguardando Turma" (não fecha vínculo, é continuação natural pro Especializado); Especializado aprovado fecha vínculo (concluiu a habilitação). Fora desse caso específico de aprovação normal, qualquer término é término — não importa o Módulo.

---

## 9. Ordem de implementação sugerida

1. **Etapa 0** (seção 2): consolidar `situacao`/`ativo`, corrigir bug do Service, adicionar `Modulo.categoria`, criar os 2 Services novos em `cadastros`. Baixo risco, testável isoladamente, sem tela nova.
2. **App `atribuicao`**: `MatriculaTurma` + migration + Admin (Admin-only primeiro, mesmo padrão já usado nos outros catálogos).
3. ~~Fechar 8-A e 8-B antes de codar a tela de "Encerrar Turma"~~ — ✅ **as duas fechadas em 07/09/2026.** Nenhum bloqueio restante para codar a fase "Em Andamento" (Relocação, mudança de status) nem "Encerrar Turma".
4. **Telas**: gestão de composição da Turma (Planejamento → Finalizar → Em Andamento → Encerrar), reaproveitando `ModalCrudMixin`/`modal-crud.js` como sempre.
5. **`detalhe.html` de Pessoa**: renomear seção pra "Sumário Histórico de Vínculos", implementar a consulta consolidada (seção 6).
6. **Extracurricular** (seção 7): fechar a regra de "não fechar vínculo se houver Turma regular ativa acumulada" antes de liberar matrícula extracurricular de verdade.
7. Só depois: Instrutor↔Turma↔Disciplina com validação de Capacidade+Treinamento (frente separada, ver Kanban), Relatórios (Ficha de Matrícula).

---

## Itens de Backlog gerados por este documento

- [ ] Limpeza de código morto em `models.py`/`services.py` — mencionada pela pessoa responsável como necessária **antes de produção**, ainda não feita. Fazer uma leitura completa do código existente antes do primeiro deploy real.
- [ ] Discussão futura (**não agora**, após Relatórios/Ficha de Matrícula): local para armazenar documentação digitalizada de Discente/Docente/Gestão.
- [ ] Recorte mínimo do módulo Treinamento (só o suficiente para responder "Instrutor tem Treinamento válido para esta Disciplina, sim/não") — pré-requisito da atribuição de Instrutor↔Turma↔Disciplina.
