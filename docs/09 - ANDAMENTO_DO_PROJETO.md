# Andamento do Projeto — 09

**Data:** 25/08/2026
**Branch:** `feature/refatoracao-funcao`
**Sessão dedicada a finalizar a Etapa 4 do plano de migração** (`docs/07 - PLANO_DE_MIGRACAO.md`), decisão explícita de não parar no meio.

---

## O que foi feito

### 1. Correção de escopo: RM, RA e CANAC pertencem a `Pessoa`, não a `DadosDiscente`

Antes de criar `DadosDiscente`, foi levantada a pergunta de quais dos 4 campos de matrícula da FE 007 (RM, RA, Código ANAC, Código de Matrícula ANAC) precisavam de `unique=True`. A resposta revelou um problema de modelagem que teria passado despercebido: **RM, RA e Código ANAC nunca mudam** — são identificadores permanentes da pessoa perante a instituição/órgão regulador — enquanto **Código de Matrícula ANAC muda a cada novo vínculo** que a pessoa estabelece com a EMCA (ex: segundo curso).

Como `DadosDiscente` nasce como um registro novo por `AtribuicaoFuncao` (um por vínculo), manter RM/RA/CANAC ali forçaria o usuário a redigitar os mesmos valores a cada novo curso da mesma pessoa — com risco real de inconsistência (o mesmo RM digitado diferente da segunda vez) e sem trava de unicidade funcionando direito nesse cenário.

**Decisão:** RM (`registro_matricula`), RA (`registro_aluno`) e CANAC (`codigo_anac`) migraram para `Pessoa`, todos com `unique=True, blank=True`. Só `codigo_matricula_anac` — que de fato muda por vínculo — permaneceu em `DadosDiscente`.

**Trabalho técnico decorrente**, tratado como extensão da Etapa 1:
- Migration `0007` criou os 3 campos em `Pessoa` (inicialmente sem `unique=True`, para confirmar quais campos precisavam da trava)
- Confirmado com a pessoa responsável pelo projeto: os três precisam de `unique=True`
- Os nomes de campo foram revisados de `rm`/`ra` (pouco descritivos) para `registro_matricula`/`registro_aluno`, com `verbose_name="RM"`/`"RA"` para manter a sigla como rótulo de exibição
- Migration `0008` aplicou a renomeação — o Django não detectou automaticamente como "rename" (por mudar nome + `unique` + `verbose_name` ao mesmo tempo), tratando como remove+add; inofensivo, pois o banco local não tinha nenhuma Pessoa com esses campos preenchidos ainda
- Commit `9ddf529`: `feat: adiciona RM, RA e CANAC em Pessoa`

### 2. Etapa 4.1 — `DadosDiscente`

Model criado com escopo já ajustado (sem RM/RA/CANAC): `atribuicao` (`OneToOneField` → `AtribuicaoFuncao`), `codigo_matricula_anac`, documentação de estrangeiro (passaporte, autorização de permanência), contato de emergência (nome, parentesco, telefone, endereço — campos de texto simples, sem entidade própria, conforme decidido em sessão anterior), responsável legal (nome, endereço, identidade, órgão expedidor, data de emissão, qualificação — mesma lógica de campos simples).

Sem incidentes técnicos nesta sub-etapa — posicionamento no arquivo e imports já corretos de primeira, sinal de que os erros de sessões anteriores foram internalizados. Migration `0009_dadosdiscente`. `pytest` — `7 passed`. Commit `6550d94`: `feat: extensao DadosDiscente`.

### 3. Etapa 4.2 — `DadosDocente`

Alinhamento de escopo feito antes de codar: `DadosDocente` ficou **minimalista** por decisão consciente — só `atribuicao` (`OneToOneField`) e o método `possui_treinamento_valido()` migrado de `VinculoDocente`. Os campos de requisitos de contratação e formação (FE 008) permanecem no Backlog, não implementados nesta etapa — a especificação detalhada já existe no Kanban, será retomada quando aquele item específico for priorizado.

**Ajuste em `Capacidade`:** a FK que apontava para `VinculoDocente` foi trocada para `DadosDocente`, incluindo a `UniqueConstraint` dentro de `class Meta` (fácil de esquecer — o nome do campo também precisa mudar ali, não só na declaração da FK).

**Dois erros de sintaxe/organização, ambos resolvidos:**
1. `IndentationError: unexpected indent` — ao editar a FK de `Capacidade`, a linha `class Meta:` ficou com 8 espaços de indentação em vez de 4, desalinhada do resto do corpo da classe.
2. `NameError: name 'DadosDocente' is not defined` — mesmo padrão de erro já visto na Etapa 3 (classe referenciando outra definida mais abaixo no arquivo). `Capacidade` estava na posição original (no meio do arquivo, entre as classes antigas), mas passou a referenciar `DadosDocente`, que só existe no final. Resolvido movendo `Capacidade` inteira para o final do arquivo, junto de `DadosDiscente`/`DadosDocente`.

Django pediu um valor default one-off durante o `makemigrations` (situação normal ao adicionar campo obrigatório numa tabela existente) — sem risco, pois o banco local não tinha nenhuma linha em `Capacidade`. Migration `0010_dadosdocente_and_more`. `pytest` — `7 passed`. Commit `4ed57e4`: `feat: extensao DadosDocente, ajusta FK de Capacidade`.

### 4. Etapa 4.3 — `ExperienciaProfissional`

Confirmado com a pessoa responsável pelo projeto: a FK para `AtribuicaoFuncao` é uma `ForeignKey` normal, não `OneToOneField` — uma mesma `AtribuicaoFuncao` pode ter várias `ExperienciaProfissional` associadas, refletindo fielmente a tabela repetível (Organização/Cargo/Período) do FOP 402.

**Decisão sobre o formato do período:** entre texto livre (mais fiel ao formulário físico) e datas estruturadas (`data_inicio`/`data_fim`), optou-se por datas estruturadas — decisão explícita para permitir cálculos futuros sobre tempo de experiência (ex: somar tempo total, validar consistência cronológica), algo que texto livre não permitiria sem reprocessamento manual.

Sem incidentes técnicos — posicionamento e imports corretos de primeira. Migration `0011_experienciaprofissional`. `pytest` — `7 passed`. Commit `1b7046a`: `feat: model ExperienciaProfissional`.

---

## Padrão de erro identificado ao longo da sessão (útil para o relatório do PI)

Os quatro erros enfrentados nesta sessão (dois na Etapa 4.2, mais os dois já vistos na Etapa 3 de uma sessão anterior) pertencem todos à mesma categoria: **erros de ordem de definição ou de indentação**, nunca de lógica de negócio. Em Python, uma classe só pode referenciar outra classe já definida **acima dela** no arquivo — diferente de outras linguagens que resolvem isso em tempo de compilação, independente da ordem física do código. Essa é uma boa observação didática para a fundamentação teórica do PI: ilustra uma diferença real de comportamento entre linguagens interpretadas linha a linha e linguagens compiladas, e reforça por que a ordem das classes dentro de um arquivo `models.py` que cresce organicamente precisa de atenção deliberada.

---

## Estado geral ao final desta sessão

| Etapa do plano de migração | Status |
|---|---|
| Etapas 1, 2, 3 | ✅ Concluídas em sessões anteriores |
| Etapa 4 — Criar as extensões | ✅ Concluída nesta sessão, incluindo a correção de escopo de RM/RA/CANAC |
| Etapas 5 a 9 | Não iniciadas |

**Models do modelo novo, todos implementados:** `Pessoa` (ampliada), `Funcao`, `AtribuicaoFuncao`, `DadosDiscente`, `DadosDocente`, `ExperienciaProfissional`.

---

## Próximos passos

Etapa 5 do plano de migração — remover o que ficou obsoleto (`Vinculo` e subtipos, `FuncaoGestao`, `Habilitacao`, `FuncaoGestaoHabilitacao`, `AssociarHabilitacaoService` e seus testes, o endpoint de API correspondente). O plano recomenda explicitamente fazer isso só depois da Etapa 4 estar completa e testada — condição agora satisfeita. Atenção especial ao remover `VinculoDocente`: confirmar que `possui_treinamento_valido()` já foi levado para `DadosDocente` (já foi, nesta sessão) antes de apagar o original.
