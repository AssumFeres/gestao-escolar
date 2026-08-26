# Plano de Migração — De `Vinculo`/`FuncaoGestao`/`Habilitacao` para `Funcao`/`AtribuicaoFuncao`

**Origem da decisão:** ver `docs/06 - ANDAMENTO_DO_PROJETO.md` para o raciocínio completo por trás de cada escolha registrada aqui. Este documento é só o **como executar**, não o porquê.

**Status:** em execução, branch `feature/refatoracao-funcao`. Etapas 1, 2, 3 e 4 concluídas e commitadas (25/08/2026) — ver `docs/08 - ANDAMENTO_DO_PROJETO.md` para o relato da sessão. Faltam as Etapas 5 a 9 (remoção do modelo antigo, reescrita do Service, ajuste de Views/Templates, endpoint de API, fechamento).

**Como usar este documento:** cada etapa é pequena e termina em um estado que roda e testa (mesmo que incompleto). Marque `[x]` ao concluir cada passo, e não pule etapas — a ordem importa, porque cada uma depende da anterior não quebrar o projeto.

---

## Antes de começar

- [x] Criar uma branch nova a partir de `dev`: `git checkout -b feature/refatoracao-funcao` — 25/08/2026
- [x] Confirmar que a suíte de testes atual passa antes de qualquer mudança (`pytest`) — 25/08/2026, `7 passed`
- [ ] Fazer backup do `db.sqlite3` local antes de começar a mexer em migrations — não confirmado como feito; sem incidente até agora, mas o passo em si não foi formalmente executado

---

## Etapa 1 — Ampliar `Pessoa` ✅ Concluída (25/08/2026)

A menor mudança, sem dependência de nada mais, e não quebra nada existente (só adiciona campos).

- [x] Adicionar em `Pessoa`: `sexo`, `identidade` (nº), `data_emissao_identidade`, `orgao_expedidor_identidade`, `naturalidade`, `uf_naturalidade`, `nacionalidade`, `filiacao_1`, `filiacao_2`, `nivel_instrucao`, `estado_civil`, `raca_cor` (`data_nascimento` já existia em `Pessoa` antes desta etapa — não precisou ser criado)
- [x] Todos os campos novos `blank=True`
- [x] `cpf` já tinha `unique=True` desde antes — nada a alterar
- [x] Migration `0004_pessoa_data_emissao_identidade_pessoa_estado_civil_and_more` gerada e aplicada. Uma migration pendente de sessão anterior (`0003_alter_disciplina_sigla` — só adicionava a mensagem de erro do `RegexValidator` de `Disciplina.sigla`, sem efeito sobre dados) foi identificada e aplicada junto, por ser inofensiva.
- [x] `pytest` — `7 passed`
- [x] Commit: `feat: amplia Pessoa com campos de identificacao (FE 007/FE 008)`
- [ ] **Registrado no Backlog do Kanban, não executado nesta etapa:** configurar `choices` para `sexo`, `estado_civil`, `raca_cor` (e reavaliar os demais campos de identificação quanto à necessidade de `choices`) — decisão adiada deliberadamente

---

## Etapa 2 — Criar `Funcao` (catálogo) e popular dados iniciais ✅ Concluída (25/08/2026)

- [x] Criar Model `Funcao`: `id`, `nome` (`CharField`, `unique=True`) — mantido `unique=True` após esclarecer que isso trava duplicata de *nome no catálogo*, não a quantidade de pessoas que podem ocupar aquela Função (ver nota de design abaixo)
- [x] `__str__` retornando `nome`, já incluído desde o início — evita repetir o problema já visto com `Habilitacao`/`Vinculo` antes de terem `__str__` (ver `03 - ANDAMENTO_DO_PROJETO.md`)
- [x] Registrar `Funcao` no Django Admin
- [x] Migration `0005_funcao` gerada e aplicada
- [x] `pytest` — `7 passed`
- [x] Popular dados iniciais — via Admin, sem fixture versionada (decisão tomada na hora): 9 Funções cadastradas (Auxiliar Administrativo, Secretária, Coordenador de Curso GMP, Coordenador de Curso Célula, Coordenador de Curso Aviônicos, Gerente de Qualidade, Diretor, Discente - Aluno, Docente - Instrutor). **GSO não entra** (não se aplica à organização); **Diretor = Gestor Responsável** (mesmo cargo, nomenclatura EMCA vs. ANAC/FOP 402) — uma linha só, não duas. Cada ambiente (das 5 máquinas já validadas) vai precisar popular seu próprio catálogo manualmente, já que não foi versionada fixture.
- [x] Commit: `feat: catalogo aberto Funcao` (`44c142c`)

### ⚠️ Nota de design importante, registrada durante esta etapa

**`Funcao.nome` é editável a qualquer momento sem risco de perda de histórico** — uma `AtribuicaoFuncao` referencia uma `Funcao` pelo `id` interno, não pelo texto do nome. Renomear "Discente" para "Aluno", por exemplo, não quebra nem apaga nenhuma atribuição existente; todo o histórico permanece ligado à mesma linha do catálogo, só exibindo o rótulo atualizado.

**Isso tem uma implicação direta e obrigatória para a Etapa 3/6 (regra "Discente não acumula outra Função"):** essa regra de negócio **nunca deve ser implementada comparando `Funcao.nome`** (ex: `if funcao.nome == "Discente"`). Se o catálogo for renomeado no futuro, uma regra baseada em texto pararia de funcionar silenciosamente, sem erro nenhum — uma falha de segurança de dados sutil e perigosa. A regra deve ser implementada verificando a **estrutura**: se a `AtribuicaoFuncao` em questão possui (ou vai possuir) um `DadosDiscente` associado, não se o nome da Função bate com uma string específica. Isso ancora a regra em algo que só muda deliberadamente (a extensão de dados), não em um rótulo editável livremente por qualquer pessoa com acesso ao Admin.

**Ação obrigatória para quem for implementar a Etapa 3/6:** ao escrever a validação de acúmulo de Função, checar a presença de `DadosDiscente`, nunca o texto do nome da Função.

---

## Etapa 3 — Criar `AtribuicaoFuncao` ✅ Concluída (25/08/2026)

- [x] Criar Model `AtribuicaoFuncao`: `pessoa` (FK → `Pessoa`, `CASCADE`, `related_name='atribuicoes'`), `funcao` (FK → `Funcao`, `PROTECT`, `related_name='atribuicoes'`), `situacao`, `data_inicio`, `data_fim` (nullable), `ativo`
- [x] Registrado no Admin. Item de Backlog já anotado (Etapa 2) sobre a regra "Discente não acumula" não ser aplicada pelo Admin — mesmo raciocínio pragmático de `03 - ANDAMENTO_DO_PROJETO.md`.
- [x] Migration `0006_atribuicaofuncao` gerada e aplicada
- [x] `pytest` — `7 passed`
- [x] Commit: `feat: model AtribuicaoFuncao` (`193fd99`)

**Dois erros de ordem de definição/import encontrados e resolvidos** (ver `docs/08 - ANDAMENTO_DO_PROJETO.md` para o relato completo): (1) `AtribuicaoFuncao` colada antes de `Funcao` no `models.py` — Python exige que uma classe referenciada já esteja definida acima no arquivo; (2) `AtribuicaoFuncao` registrada no `admin.py` sem estar no bloco de `import`. Nenhum dos dois teve relação com lógica de negócio — categoria de erro puramente sintática/organizacional.

---

## Etapa 4 — Criar as extensões (`DadosDiscente`, `DadosDocente`, `ExperienciaProfissional`) ✅ Concluída (25/08/2026)

Fazer uma de cada vez, cada uma com seu próprio commit — são independentes entre si.

### Correção de escopo, feita antes de 4.1: RM, RA e CANAC movidos para `Pessoa`

Ao desenhar `DadosDiscente`, ficou claro que RM, RA e Código ANAC (CANAC) **não mudam nunca** e são identificadores da **pessoa**, não do vínculo — diferente de "Código de Matrícula ANAC", que muda a cada novo vínculo com a EMCA. Como `DadosDiscente` nasce um registro novo por `AtribuicaoFuncao`, manter RM/RA/CANAC ali forçaria redigitação (com risco de inconsistência) a cada novo curso da mesma pessoa. Decisão: os 3 campos migraram para `Pessoa` (`registro_matricula`/RM, `registro_aluno`/RA, `codigo_anac`/CANAC — os três com `unique=True`, `blank=True`), fora do escopo original desta etapa mas tecnicamente uma continuação da Etapa 1. Só `codigo_matricula_anac` (o que de fato muda por vínculo) ficou em `DadosDiscente`. Duas migrations (`0007` criando os campos, `0008` renomeando `rm`/`ra` para os nomes finais com `verbose_name`) geradas, aplicadas e commitadas (`9ddf529`) antes de seguir para 4.1.

### 4.1 — `DadosDiscente` ✅

- [x] Criar Model: `atribuicao` (`OneToOneField` → `AtribuicaoFuncao`), `codigo_matricula_anac`, documentação de estrangeiro (passaporte, autorização de permanência), contato de emergência (texto simples), responsável legal (texto simples)
- [x] Migration `0009_dadosdiscente` + commit: `feat: extensao DadosDiscente` (`6550d94`)

### 4.2 — `DadosDocente` ✅

- [x] Criar Model minimalista: só `atribuicao` (`OneToOneField` → `AtribuicaoFuncao`) + `possui_treinamento_valido()` migrado de `VinculoDocente`. Os campos de requisitos de contratação/formação do FE 008 permanecem no Backlog, não implementados agora — decisão consciente de manter escopo mínimo nesta etapa.
- [x] `Capacidade` ajustada: FK trocada de `vinculo_docente`/`VinculoDocente` para `dados_docente`/`DadosDocente`, incluindo a `UniqueConstraint` em `Meta` (fácil de esquecer, não é óbvia à primeira vista)
- [x] Migration `0010_dadosdocente_and_more` (Django pediu um valor default one-off para popular linhas existentes — sem risco, banco local vazio) + commit: `feat: extensao DadosDocente, ajusta FK de Capacidade` (`4ed57e4`)
- [x] **Especificação de `FormacaoDocente` no Kanban já atualizada** para referenciar `DadosDocente` (havia sido corrigida numa atualização de documentação anterior a esta sessão de código)

**Dois erros de indentação/ordem de definição encontrados e resolvidos** (ver `docs/08 - ANDAMENTO_DO_PROJETO.md`): (1) `class Meta:` de `Capacidade` com indentação incorreta (8 espaços em vez de 4) após a edição da FK — `IndentationError`; (2) `Capacidade` posicionada antes de `DadosDocente` no arquivo, mas referenciando-a — resolvido movendo `Capacidade` para depois de `DadosDocente`.

### 4.3 — `ExperienciaProfissional` ✅

- [x] Criar Model: `atribuicao` (`ForeignKey` normal, não 1:1 — uma `AtribuicaoFuncao` pode ter várias experiências, refletindo a tabela repetível do FOP 402), `organizacao`, `cargo`, **`data_inicio`/`data_fim` estruturados** (decisão tomada: não texto livre, para permitir cálculo futuro sobre tempo de experiência)
- [x] Migration `0011_experienciaprofissional` + commit: `feat: model ExperienciaProfissional` (`1b7046a`)

---

## Etapa 5 — Remover o que ficou obsoleto

**Fazer só depois que a Etapa 4 estiver completa e testada** — remover cedo demais deixa o projeto num estado quebrado por mais tempo do que necessário.

- [ ] Remover testes que dependem do que vai sumir: `test_services.py` (testes de `AssociarHabilitacaoService`)
- [ ] Remover `AssociarHabilitacaoService` de `services.py`
- [ ] Remover endpoint `POST /api/pessoas/funcoes-gestao/habilitacoes/`: view, serializers (`FuncaoGestaoHabilitacaoInputSerializer`/`OutputSerializer`), rota em `api_urls.py`
- [ ] Remover Models: `FuncaoGestaoHabilitacao`, `Habilitacao`, `FuncaoGestao`, `VinculoGestao`, `VinculoDocente` (⚠️ só depois de confirmar que `DadosDocente` já assumiu tudo que era necessário), `VinculoDiscente`, `Vinculo`
- [ ] Remover do Admin o registro desses Models
- [ ] Gerar migration de remoção (`makemigrations` vai detectar as remoções automaticamente)
- [ ] Rodar `pytest` — checar o que quebrou e corrigir (Template Views de lista/detalhe de Pessoa provavelmente referenciam `pessoa.vinculos.all()` — precisam ser reescritas para `pessoa.atribuicoes.all()` ou nome equivalente)
- [ ] Commit: `refactor: remove Vinculo, FuncaoGestao, Habilitacao e AssociarHabilitacaoService`

---

## Etapa 6 — Reescrever o Service de cadastro (buscar-ou-criar por CPF)

- [ ] Revisar `CadastrarPessoaComVinculoService`: hoje sempre cria `Pessoa` nova; passa a **buscar por CPF primeiro** e só criar se não existir
- [ ] Decidir nome do Service atualizado — manter o nome atual (o comportamento mudou, mas o propósito geral — "cadastrar pessoa com uma função" — continua parecido) ou renomear para refletir melhor o novo comportamento (ex: `CadastrarOuAtribuirFuncaoService`) — **decisão de nomenclatura a tomar na hora, não antecipar aqui**
- [ ] Escrever teste novo: cadastro com CPF já existente não deve criar segunda `Pessoa`, deve criar só a nova `AtribuicaoFuncao`
- [ ] Escrever/ajustar teste da regra de negócio única: Pessoa com Função de Discente não pode acumular outra Função — decidir onde essa validação mora (no Service, seguindo o mesmo padrão do antigo `AssociarHabilitacaoService`)
- [ ] Commit: `feat: fluxo buscar-ou-criar Pessoa por CPF`

---

## Etapa 7 — Ajustar Views e Templates existentes

- [ ] `ListaPessoasView` / `lista.html`: revisar se depende de algo específico de `Vinculo`
- [ ] `DetalhePessoaView` / `detalhe.html`: troca `pessoa.vinculos.all()` (ou equivalente) para o novo relacionamento via `AtribuicaoFuncao`; a property `tipo_legivel` criada para `Vinculo` provavelmente não é mais necessária do mesmo jeito, já que não há mais subtipo por herança — reavaliar
- [ ] `NovoCadastroPessoaView` / `form_pessoa.html` / `CadastrarPessoaForm`: repensar como três fluxos distintos (FE 007/FE 008/FOP 402), conforme desenhado em `06 - ANDAMENTO_DO_PROJETO.md`, seção 10 — isso provavelmente é trabalho suficiente para ser tratado como uma etapa própria, não um ajuste rápido dentro desta
- [ ] JS de busca de CEP (`buscar-cep.js`): não deveria ser afetado, mas confirmar que o formulário reestruturado ainda tem os mesmos `id`s de campo que o script espera

---

## Etapa 8 — Endpoint de API para `CadastrarPessoaComVinculoService`

- [ ] Revisar `CadastrarPessoaInputSerializer`/`OutputSerializer`/`CadastrarPessoaView` para refletir o novo formato de entrada (Função em vez de tipo de vínculo fixo, campos condicionais por categoria)

---

## Etapa 9 — Fechar a etapa

- [ ] Rodar `pytest` completo, confirmar tudo passando
- [ ] Testar manualmente pelo navegador: Admin com os novos Models, fluxo de cadastro (se já reescrito), endpoints de API restantes
- [ ] Atualizar `docs/00 - KANBAN.md`: mover itens concluídos, ajustar a especificação de `FormacaoDocente` (referência a `VinculoDocente` → `DadosDocente`), remover o item de Backlog sobre o bug do Admin/Habilitação (deixou de existir), adicionar os novos itens de "A Fazer" que ficaram claros nesta migração (telas por formulário, regra de "Discente não acumula", constraint de CPF único, etc.)
- [ ] Escrever diário `docs/08 - ANDAMENTO_DO_PROJETO.md` com o que foi de fato executado (distinto deste plano, que é o *previsto* — o diário registra o que *aconteceu*, incluindo qualquer desvio deste plano)
- [ ] Abrir Pull Request de `feature/refatoracao-funcao` → `dev`
- [ ] Sincronizar as demais máquinas (múltiplos ambientes já validados) após o merge

---

## Riscos e pontos de atenção já identificados

- **Migrations de remoção de Model em SQLite local:** se o banco local tiver dados de teste nas tabelas antigas, o Django geralmente lida bem com a remoção (dropa a tabela), mas vale confirmar que não há nada crítico a preservar antes de aplicar
- **`DadosDocente` herdando responsabilidade de `VinculoDocente`:** conferir com atenção se algum campo ou método (`possui_treinamento_valido()`, por exemplo) precisa ser trazido junto, não só os campos óbvios
- **Ordem de execução das Etapas 4 e 5:** resistir à tentação de remover o antigo antes do novo estar pronto — deixa o projeto sem rodar por mais tempo que o necessário
- **Fixture de `Funcao`:** se não for versionada, cada ambiente (casa, quartel, escola, notebook — já são 5 máquinas validadas) precisa popular manualmente o catálogo, o que é chato mas não bloqueante
