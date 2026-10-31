# Andamento do Projeto — 14

**Data:** 25-29/08/2026 (sessão iniciada com testes manuais da Etapa 7.4, retomada em outra máquina)
**Branches:** `feature/refatoracao-funcao`
**Sessão dedicada a corrigir os problemas encontrados no teste manual da Etapa 7.4, sincronizar uma segunda máquina, e fechar documentação pendente.**

---

## Contexto: teste manual revelou 3 problemas em cascata

Ao testar o formulário de cadastro completo pela primeira vez (Etapa 7.4a/b), surgiram, em sequência, três problemas distintos — cada um com causa e correção próprias.

### Problema 1 — Formsets sem management_form (bloqueava todo POST)

`form_pessoa.html` ainda usava só `{{ form.as_p }}`, sem nunca mencionar os 3 Formsets criados na Etapa 7.3. Isso significava que os campos ocultos de controle (`TOTAL_FORMS`, `INITIAL_FORMS`) nunca eram enviados ao servidor — o Django recusa qualquer POST de Formset sem esses campos, com o erro "ManagementForm data is missing or has been tampered with".

**Diagnóstico:** feito com `print()` temporário no `views.py`, inspecionando `form.is_valid()`, `formset.errors` e `formset.non_form_errors()` separadamente — os `.errors` normais vinham vazios, mas `.non_form_errors()` continha a mensagem real.

**Correção:** `form_pessoa.html` passou a incluir `{{ formset.management_form }}` e iterar cada Formset renderizando `{{ subform.as_p }}` — versão mínima, sem nenhuma organização visual ainda (isso fica para a 7.4c/d, quando o CSS/JavaScript de fato organizarem a tela por categoria).

### Problema 2 — `IntegrityError`: RM/RA/CANAC duplicados como string vazia

Depois de resolver o Formset, o cadastro avançou até tentar salvar no banco, e falhou com `UNIQUE constraint failed: pessoas_pessoa.registro_matricula` — mesmo sem o usuário ter preenchido o campo.

**Causa raiz:** `registro_matricula`/`registro_aluno`/`codigo_anac` tinham `unique=True` e `blank=True`, mas **não** `null=True`. Quando o campo fica vazio no formulário, o Django salva string vazia (`""`), não `NULL` — e o SQLite trata múltiplas strings vazias como duplicatas entre si na constraint `unique`, diferente de múltiplos `NULL`, que não conflitam.

**Correção em duas partes**, e a segunda só foi descoberta ao testar de novo:
1. Adicionado `null=True` aos 3 campos em `Pessoa` (migration `0017`).
2. **Isso sozinho não resolveu** — a View continuava montando `dados.get("registro_matricula", "")`, sempre entregando string vazia mesmo com o Model já aceitando `NULL`. Corrigido para `dados.get("registro_matricula") or None`, garantindo que campo vazio vire `None` de verdade antes de chegar ao banco.

**Lição prática:** corrigir só o Model não bastou — a View também precisava ser ajustada para efetivamente produzir `None` em vez de string vazia. Um ajuste de Model sem o ajuste correspondente na camada que monta os dados não resolve o problema por completo.

### Discussão de modelagem: duplicação aparente entre `codigo_anac` e `codigo_matricula_anac`

Ao revisar o código em busca do problema, foi levantada a suspeita de que `Pessoa.codigo_anac` e `DadosDiscente.codigo_matricula_anac` seriam o mesmo dado duplicado. **Esclarecido que não são** — `codigo_anac` (CANAC) identifica a *pessoa* perante a ANAC, permanente; `codigo_matricula_anac` (CMA) identifica a *matrícula específica* daquele curso (formato Ciac.Habilitação.Ano.Sequencial, ex: `239.MCELT.25.00115`), mudando a cada novo curso. A modelagem já estava correta desde a Etapa 4; documentado com mais destaque no docstring de `DadosDiscente` para evitar a mesma confusão no futuro.

**Decisão sobre obrigatoriedade do CANAC:** confirmado que, na prática, o Discente pode ser cadastrado no sistema antes de ter o CANAC processado pela ANAC — por isso o campo continua opcional (`blank=True`), tratado como pendência a resolver, não como bloqueio ao cadastro.

---

## Nova funcionalidade: `PendenciaCadastro`

Discussão iniciada a partir da pergunta "e se o Discente não tiver CANAC ainda?" evoluiu para uma necessidade de negócio mais ampla: rastrear documentação física pendente do cadastro (Certidão de Nascimento, CPF físico, RG, comprovante de endereço, cartão de vacina para menores, e os próprios CANAC/RM/RA/Código de Matrícula ANAC quando vazios) — não apenas para saber "está faltando", mas para **gerar um relatório operacional** (Turma → Aluno → Pendências) entregue ao Coordenador de Curso para cobrança.

**Decisão de design, revisada durante a conversa:** a primeira proposta (calcular pendências dinamicamente via `property`, sem tabela nova) foi descartada depois que a pessoa responsável explicou o requisito do relatório — uma pendência "calculada na hora" não é naturalmente agrupável/filtrável do jeito que um relatório por Turma exige. Voltou-se à ideia original: uma tabela de verdade, `PendenciaCadastro`.

**Modelo implementado:**
- Enum `TipoPendencia` com os tipos comuns identificados (CANAC, RM, RA, Código de Matrícula ANAC, Certidão de Nascimento, CPF físico, RG, Passaporte/Autorização de Permanência, Comprovante de Endereço, Cartão de Vacina) + `OUTRO` com campo `descricao` livre, para casos incomuns (ex: pendência específica de Docente, ou "assinatura" mencionada pela Secretaria) sem precisar prever cada tipo possível de antemão.
- `PendenciaCadastro` ligada a `AtribuicaoFuncao` (não a `Pessoa`), pensando no relatório futuro por Turma — Turma vai se relacionar com a atribuição de Discente específica, não com a Pessoa em geral.
- **Universal entre categorias:** diferente de Formação/Experiência/Histórico de Vínculo Formal (condicionais por categoria), `PendenciaCadastro` se aplica a Discente, Docente ou Gestão sem distinção — confirmado que pendências em Docente são raras, mas cabem perfeitamente na mesma tabela via `OUTRO`, sem necessidade de estrutura separada.
- Campos `resolvida` (booleano) e `resolvida_em` (timestamp), para o futuro fluxo de "marcar como resolvido".

Migration `0017` (junto da correção de RM/RA/CANAC). Registrada no Admin.

---

## Sincronização de uma segunda máquina ("casa")

Ao retomar o trabalho em outra máquina, `git status` mostrou branch correta e árvore limpa, mas o `git log` revelou que o **trabalho da sessão anterior nunca tinha sido commitado** — ficou só na máquina de origem. Nada foi perdido (a máquina de origem ainda tinha o código), mas exigiu:

1. Commitar o trabalho pendente na máquina de origem primeiro (`git commit -m "wip: ..."`, seguido de `push`) — usando o prefixo `wip:` para sinalizar trabalho reconhecidamente incompleto, distinto dos prefixos formais já documentados (`feat`/`fix`/`docs`/`chore`).
2. `git pull` na máquina de casa, trazendo os 5 arquivos pendentes.
3. `python manage.py migrate` — aplicou as 14 migrations que essa máquina nunca tinha visto, confirmando que era a primeira vez rodando essa migração ali.
4. `pytest` — `5 passed`.

**Observação registrada:** a máquina de casa roda Python 3.13.0, enquanto a outra roda 3.14.5 — divergência de versão entre máquinas do grupo, sem problema prático até agora, mas registrada no Backlog para padronização futura.

**Nota de segurança à parte:** durante a sincronização, um hash de senha de superusuário (`pbkdf2_sha256$...`) foi colado nesta conversa. Embora hashes bem formados não sejam diretamente reversíveis, foi recomendado não deixar esse tipo de dado circulando fora do ambiente do banco, e sugerida a troca da senha por precaução. Não registrado em nenhum documento do projeto.

### Fixture do catálogo `Funcao`/`VinculoFormal`

Para evitar repetir o cadastro manual das 9 Funções + Vínculos Formais em cada máquina nova (item já pendente no Backlog desde a Etapa 2), foi criada `pessoas/fixtures/catalogo_inicial.json`, carregável com `python manage.py loaddata catalogo_inicial`. Resolve de forma definitiva a necessidade de popular manualmente cada uma das 5 máquinas validadas.

---

## Estado geral ao final desta sessão

| Item | Status |
|---|---|
| Formsets renderizando corretamente (management_form) | ✅ Corrigido |
| `IntegrityError` de RM/RA/CANAC | ✅ Corrigido (Model + View) |
| `PendenciaCadastro` | ✅ Implementada e no Admin |
| Fixture do catálogo `Funcao`/`VinculoFormal` | ✅ Criada, item de Backlog resolvido |
| Máquina de casa sincronizada | ✅ |
| Fluxo de cadastro (Discente/Docente/Gestão) testado manualmente | ✅ Funcional, ainda sem organização visual |

Commits desta sessão: `3f73c3b` (Formsets + correção inicial), `4e6b547` (null=True em RM/RA/CANAC, PendenciaCadastro, fixture).

---

## Próximos passos

Etapa 7.4c/d — organização visual do formulário (CSS mínimo, blocos por categoria) e o JavaScript que mostra/esconde esses blocos conforme a Função escolhida no dropdown, além do botão "Adicionar linha" nos Formsets. Também incluir `PendenciaCadastro` como um bloco a mais no formulário — sempre visível, sem condicional de categoria, com um sexto parâmetro `pendencias: list` no `CadastrarPessoaComFuncaoService`.
