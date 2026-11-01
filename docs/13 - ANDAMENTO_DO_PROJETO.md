# Andamento do Projeto — 13

**Data:** 25/08/2026
**Branch:** `feature/refatoracao-funcao`
**Sessão dedicada a fechar o inventário de dados de FE 007/FE 008 e a Etapa 7.2 (expandir o Service).**

---

## Contexto: análise de um FE 008 preenchido revelou lacunas reais no modelo

Um formulário FE 008 real, já preenchido (instrutora Fernanda Sanches Graciano), foi analisado em detalhe. Isso revelou que a especificação de `FormacaoDocente`, registrada há dias no Kanban como item de Backlog, nunca tinha sido promovida a código — e que faltavam duas peças inteiras ainda não discutidas: o "Vínculo Formal" (entidade contratante, ex: FAPETI/PMT) e a mecânica exata de como o "documento comprobatório" da seção 7 (Disciplinas) se conecta às seções 3-5 (Formação).

---

## Decisões de modelagem de dados

### `FormacaoDocente` promovida do Backlog para código real

A especificação já existente no Kanban (tabela única + enum `TipoFormacaoDocente`, por DRY) foi implementada sem alterações de fundo — só formalizada como Model de verdade.

### O "documento comprobatório" é uma referência, não um upload

Esclarecido, a partir do exemplo real: "documento comprobatório 4.1" na seção 7 (Disciplinas) do FE 008 significa "o item 4.1 da tabela de Formação Profissional" — não um arquivo anexado. Isso confirma que a FK já especificada (`Capacidade.formacao_comprobatoria → FormacaoDocente`) resolve completamente esse requisito, sem precisar de campo de link/upload adicional.

**Decisão de UI, registrada para a Etapa 7.4:** ao cadastrar uma Capacidade (Disciplina + comprovação), a escolha do "código" (ex: "4.1") deve ser um **dropdown** sobre as `FormacaoDocente` já cadastradas daquele Docente — nunca um campo de texto livre — porque a numeração "4.1" é calculada (posição do registro no seu tipo) e pode mudar silenciosamente se um registro for editado ou reordenado. Um código digitado como texto ficaria referenciando a coisa errada sem nenhum erro visível.

### `VinculoFormal` — catálogo aberto para a entidade contratante

A pessoa responsável identificou a necessidade de registrar formalmente a entidade de vínculo (FAPETI, PMT, etc.), obrigatória para Docente e Gestão (nunca Discente — correção feita durante a conversa, a primeira resposta tinha incluído Discente por engano). Como esse dado se repete e é sujeito a erro de digitação, seguiu o mesmo padrão já usado para `Funcao`: um catálogo aberto (`VinculoFormal`, só `id` + `nome`), evitando duas entradas como "FAPETI" e "Fapeti" coexistindo por acidente.

### `HistoricoVinculoFormal` — não é campo único, é tabela repetível

A primeira proposta (um campo `vinculo_formal` único em `AtribuicaoFuncao`) foi corrigida depois que a pessoa responsável explicou que a entidade contratante pode **mudar no meio** de uma mesma Função na escola (ex: FAPETI de 2025 a 2026, depois FUSSUSS a partir de 2026, em aberto) — exatamente o mesmo padrão de `ExperienciaProfissional` (múltiplos registros ao longo do tempo). Resolvido com uma tabela nova, `HistoricoVinculoFormal`, ligada a `AtribuicaoFuncao` por FK normal (repetível), guardando `vinculo_formal` + `data_inicio`/`data_fim` por período.

### Requisitos de Contratação (seção 6) implementados em `DadosDocente`

Conforme já especificado no Kanban: `experiencia_docente_comprovada` (texto livre) e `formacao_especifica_comprobatoria` (FK para `FormacaoDocente`).

### Referência circular resolvida com FK por string

`DadosDocente.formacao_especifica_comprobatoria` aponta para `FormacaoDocente`, que por sua vez aponta de volta para `DadosDocente` (via `dados_docente`). Resolvido usando a string `'FormacaoDocente'` (entre aspas) na FK de `DadosDocente` — mecanismo do Django que permite referenciar um Model ainda não definido no arquivo, resolvido preguiçosamente quando o app termina de carregar. É uma exceção real e documentada à regra "defina antes de usar" já internalizada em sessões anteriores — só se aplica quando o nome vem como string, não como a classe em si.

### `atualizado_em`, preparando terreno para alerta futuro

A pessoa responsável levantou um cenário de risco real: se um Docente perde um curso que o habilitava a certas disciplinas, ou mesmo sem perder nada, a numeração "4.1" pode mudar com uma edição — e o papel FE 008 já impresso e assinado pelo Coordenador de Curso ficaria, então, desatualizado em relação ao banco, sem ninguém perceber.

Diagnóstico: apagar um `FormacaoDocente` em uso já está protegido (`on_delete=PROTECT`, como toda FK sensível desta migração) — o cenário "perde a capacidade e ninguém percebe" já não pode ocorrer silenciosamente. O problema real é mais sutil: a numeração pode mudar **sem nenhum dado ser perdido**, e não existe hoje mecanismo de gerar/comparar o FE 008 pelo sistema (isso está no Backlog, ainda não construído).

**Decisão:** não implementar o alerta agora (dependeria de uma funcionalidade — geração de documento — que ainda não existe), mas adicionar `atualizado_em = models.DateTimeField(auto_now=True)` em `FormacaoDocente` e `Capacidade` agora, sem custo, para que o dia em que a geração de FE 008 for construída já tenha o dado necessário para comparar "quando foi gerado o último documento" contra "quando os dados mudaram pela última vez". Registrado no Backlog, junto do item já existente de geração de documento.

---

## Incidente: `admin.py` com nomes de Model desatualizados

Ao registrar os 3 Models novos no Admin, foi fornecido por engano um trecho de `admin.py` copiado de uma versão bem mais antiga (anterior à Etapa 5b), ainda citando `VinculoDiscente`/`VinculoDocente`/`VinculoGestao` — Models que já tinham sido removidos há várias sessões. Gerou `ImportError` imediato ao rodar `makemigrations`. Resolvido substituindo pela lista de imports correta, refletindo o estado real do `models.py`.

**Lição prática, self-registrada:** ao fornecer trechos de código para colar, vale conferir contra o estado mais recente conhecido do arquivo, não reaproveitar de memória um padrão "de sempre" — especialmente em um projeto que já passou por várias remoções de Model ao longo da migração.

---

## Etapa 7.2 — Expandir o Service

### Formato de entrada: Opção A confirmada

Parâmetros nomeados e separados por natureza (`dados_extensao: dict`, `formacoes: list`, `experiencias: list`, `historico_vinculo_formal: list`) — não um dict genérico unificado. Decisão mantida com a mesma justificativa de sessões anteriores: cada parâmetro comunica sua própria natureza (1 registro vs. lista) só de olhar a assinatura, sem depender de convenção de nomes de chave dentro de um dict genérico.

### Descoberta: referência circular funcional, não só de sintaxe

Ao tentar desenhar a criação de `DadosDocente` + preenchimento imediato de `formacao_especifica_comprobatoria` na mesma chamada, ficou evidente que isso não é possível na mesma passada: a Formação que comprovaria o requisito só tem `id` **depois** de já ter sido salva — e ela só é salva depois que `DadosDocente` já existe (é `FormacaoDocente` quem aponta para `DadosDocente`, não o contrário). A pessoa responsável perguntou diretamente se o problema era "ter que salvar primeiro, carregar do banco, e depois completar" — confirmado que sim, esse é exatamente o mecanismo.

### Decisão de fluxo em 2 etapas, motivada pela divisão real de trabalho na EMCA

Inicialmente cogitou-se dividir em 2 Services conforme papéis (Secretaria faz uma parte, Coordenador de Curso outra) — corrigido pela pessoa responsável: quem preenche os dados básicos e as Formações (seções 1-5) é Secretaria/Auxiliar Administrativo; quem preenche os Requisitos e Disciplinas (seções 6-7) é a própria pessoa responsável pelo projeto — o Coordenador de Curso **nunca mexe no sistema**, só assina o papel impresso, validando o que já foi lançado.

Isso não muda a divisão técnica (ainda são 2 Services, por causa da dependência de ordem), só corrige quem aciona cada botão. Desenhado como dois botões na mesma tela conceitual: **"Salvar"** (Secretaria/Aux. Adm., fecha a primeira parte) e **"Preencher Requisitos de Contratação"** (quem for completar depois, salva o que tiver e já abre a segunda parte, no mesmo Docente, via `id` na URL — sem precisar buscar de novo).

### Dois Services resultantes

- **`CadastrarPessoaComFuncaoService`** (expandido) — agora cria, além de Pessoa/`AtribuicaoFuncao`: `DadosDiscente` ou `DadosDocente` (extensão 1:1), `FormacaoDocente` (0-N, só Docente), `ExperienciaProfissional` (0-N, só Gestão), `HistoricoVinculoFormal` (1-N, Docente ou Gestão — comum às duas categorias). Retorno mudou de 2 para **3 valores** (`pessoa, atribuicao, dados_docente`), sendo `dados_docente` `None` fora da categoria Docente.
- **`PreencherRequisitosEDisciplinasDocenteService`** (novo) — recebe um `DadosDocente` já existente (via `id`), completa os Requisitos de Contratação e cria as `Capacidade` (1-N), já com as `FormacaoDocente` disponíveis para servir de comprovação.

### Testes reajustados

Os 4 testes de `test_cadastrar_pessoa.py` foram atualizados para desempacotar 3 valores (não 2) e para incluir `categoria` ao criar `Funcao` de teste — campo obrigatório desde a 7.1, que os testes anteriores não tinham. `pytest` — `5 passed`.

### Estado consciente de "quebrado": `views.py`/`serializers.py`

Como o Service passou a retornar 3 valores, `CadastrarPessoaView` (API) e `NovoCadastroPessoaView` (Template) — que ainda desempacotam 2 — vão falhar com `ValueError` se alguém tentar cadastrar pelo formulário HTML ou pela API agora. **Decisão consciente de não corrigir isso ainda**: o ajuste de verdade depende do formulário completo (Etapa 7.4), corrigir isoladamente agora seria retrabalho. Registrado com destaque no plano de migração para não ser confundido com bug esquecido.

Commits desta sessão: `f086f57` (inventário de dados) e `04b461d` (Etapa 7.2).

---

## Estado geral ao final desta sessão

| Etapa/sub-etapa | Status |
|---|---|
| Etapas 1 a 6 | ✅ Concluídas em sessões anteriores |
| Etapa 7.1 — Categoria em Funcao | ✅ Concluída |
| Inventário de dados completo (VinculoFormal, HistoricoVinculoFormal, FormacaoDocente, Requisitos) | ✅ Concluído nesta sessão |
| Etapa 7.2 — Expandir o Service (2 Services) | ✅ Concluída nesta sessão |
| Etapa 7.3 — Form | ⏳ Não iniciada |
| Etapa 7.4 — Template + JS + correção de Views | ⏳ Não iniciada — inclui corrigir o desempacotamento quebrado |
| Etapa 7.5 — Testes | ⏳ Não iniciada |

---

## Próximos passos

Etapa 7.3 — expandir `CadastrarPessoaForm` com todos os campos possíveis das 3 categorias, incluindo os blocos repetíveis (Formação, Capacidade, Experiência Profissional, Histórico de Vínculo Formal). Lembrar, na 7.4, de corrigir `views.py`/`serializers.py` para o retorno de 3 valores do Service, e de implementar o dropdown de `FormacaoDocente` (não campo de texto) na seção de Disciplinas.
