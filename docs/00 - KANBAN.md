# Kanban do Projeto — Sistema de Gestão Escolar

Quadro de acompanhamento vivo. Diferente dos arquivos `NN - ANDAMENTO_DO_PROJETO.md` (que são um diário, fechados por data), este arquivo é **atualizado continuamente** — mova os itens entre colunas conforme o status muda.

**Como atualizar:** corte o item de uma coluna e cole na outra, mantendo o formato de checklist. Ao mover para "Concluído", adicione a data e o commit relacionado entre parênteses.

> **Nota de contexto (24/08/2026):** o módulo Pessoas está em plena refatoração — o modelo `Vinculo`/`FuncaoGestao`/`Habilitacao` foi substituído, em nível de design, pelo modelo `Funcao`/`AtribuicaoFuncao`. Raciocínio completo em `docs/06 - ANDAMENTO_DO_PROJETO.md`; execução passo a passo em `docs/07 - PLANO_DE_MIGRACAO.md`. Itens deste Kanban que mencionam `Vinculo`/`Habilitacao` estão sendo substituídos pelos itens da nova seção abaixo.

> **Nota de contexto (31/08/2026):** o app antigo `pessoas` foi renomeado para `cadastros` e ambos os PRs grandes do projeto (migração `Funcao` e renomeação `cadastros`) estão mesclados em `dev`. O fluxo de trabalho deste projeto passa a ser **commits diretos em `dev`**, sem branch nova para mudanças pequenas (decisão da pessoa responsável, registrada em `docs/18 - ANDAMENTO_DO_PROJETO.md`). Branches de feature já mescladas (`feature/refatoracao-funcao`, `feature/rename-pessoas-cadastros`) são mantidas no remoto de propósito, como evidência de processo para avaliação do PI — não devem ser apagadas.

> **✅ Nota de contexto (01/09/2026):** o bug "Docente não cadastra" (registrado em 31/08/2026) está **resolvido** — a causa real não era uma regressão do fix de `<select>`, e sim uma lacuna de validação no JavaScript do botão "+ Adicionar" (permitia linha incompleta passar, só rejeitada tarde demais no back-end). Ver `docs/20 - ANDAMENTO_DO_PROJETO.md`. **O CRUD completo do módulo Cadastros está liberado para retomar.** Em 01/09/2026, o piloto da migração de arquitetura `docs/21` começou de fato — ver "Em Andamento".

---

## 🔨 Em Andamento

_Sendo trabalhado agora_

- [ ] **Piloto do CRUD independente de `FormacaoDocente` (docs/21)** — só o "C" implementado (`AdicionarFormacaoDocenteView`, `FormacaoDocenteModelForm`, URL `docente/<pk>/formacoes/nova/`), testado manualmente e commitado (`b2e3cbb`, 01/09/2026, ver `docs/22`). **Faltando:** Update e Delete da Formação; link e listagem visível na tela `preencher_requisitos_docente.html` (hoje só acessível digitando a URL); testes automatizados. Continuar antes de replicar o padrão para Experiência/Histórico/Pendência/Capacidade.

---

## 🧊 Backlog

_Product Backlog único, ordenado por prioridade — etiquetado por `[Cadastro]` (módulo em desenvolvimento ativo, prioridade maior) ou `[Projeto]` (infraestrutura/arquitetura geral, sem módulo específico). Reorganizado em 25/08/2026 para reduzir a mistura que dificultava a leitura; nenhum item foi removido ou repriorizado além da ordenação por etiqueta._

**`[Cadastro]`**

- [ ] **Cadastro de Formação do Docente (Graduação/Formação Profissional/Aperfeiçoamento) + vínculo com Requisitos de Contratação e Disciplina Habilitada, baseado no FE 008** — especificação completa no capítulo "📐 Especificações Detalhadas" no final deste documento, já atualizada para referenciar `DadosDocente` (implementado em 25/08/2026).
- [ ] Definir quais campos de `Pessoa` são editáveis no fluxo de "segundo preenchimento" (CPF já existente) — hipótese registrada em `06 - ANDAMENTO_DO_PROJETO.md`: tudo exceto CPF, mas ainda não confirmado a fundo
- [ ] **Curso Inicial (Aviônica/Célula/GMP) + PI Inicial/Final + Ata de Vínculo, da FE 007** — depende do conceito de Módulo, que segue fora de escopo. Fica em branco no FE 007 gerado até então.
- [ ] **Motivo de encerramento de `AtribuicaoFuncao` para Discente** (Transferido / Reprovado / Aprovado / Matrícula Excluída) — capturar junto quando o item "Encerrar Atribuição de Função" (ver lista "A Fazer") for implementado; não é só desativar, é registrar o motivo.
- [ ] Geração da Ficha de Matrícula FE 007 (e, no futuro, FE 008/FOP 402) preenchida a partir dos dados do sistema — requisito de output confirmado, não modelagem; provável uso futuro do fluxo de geração de `.docx`/PDF
- [ ] **Alerta de FE 008 desatualizada** — ao gerar a FE 008 (item acima), comparar `atualizado_em` das `FormacaoDocente`/`Capacidade` daquele Docente contra a data da última geração do documento; se houver alteração posterior, bloquear a geração/download com alerta imperativo ("os dados mudaram desde a última impressão, gere novamente antes de usar"). Motivo: a numeração exibida no papel (ex: "4.1") é calculada e pode mudar silenciosamente com edições, mesmo sem perda de dado real — o papel físico assinado pelo CC ficaria desatualizado sem ninguém perceber. Campos `atualizado_em` já adicionados em `FormacaoDocente`/`Capacidade` (25/08/2026) preparando o terreno; a lógica do alerta em si depende da geração de documento existir primeiro.
- [ ] Validação de erros de negócio no formulário HTML mais amigável (hoje aparece como mensagem genérica no topo, sem destacar o campo) — **parcialmente resolvido**: `clean()` nos Formsets (31/08) e mensagens do popup customizado indicando os campos faltando ao clicar "+ Adicionar" (01/09/2026) já cobrem os casos mais comuns; segue válido para erros de negócio do `Service` (duplicidade de RM/RA/CANAC, "Discente não acumula"), que ainda aparecem como mensagem genérica no topo.
- [ ] Máscaras de formato nos campos do formulário (CPF, CEP, telefone)
- [ ] **Django Admin não aplica a regra "Discente não acumula outra Função"** — mesmo raciocínio pragmático já documentado para o caso antigo do `AssociarHabilitacaoService` (ver `03 - ANDAMENTO_DO_PROJETO.md`): o Admin conversa direto com `AtribuicaoFuncao.objects.create()`, sem passar pelo Service que vai aplicar essa regra. Registrado preventivamente desta vez, antes de alguém encontrar o bug na prática.
- [ ] Melhorar Django Admin com Inlines (editar `AtribuicaoFuncao`/extensões na mesma tela de Pessoa) — paliativo até as Template Views customizadas cobrirem cadastro completo
- [ ] Ajustar `verbose_name_plural` de `Funcao` no Admin (hoje exibido como "Funcaos")
- [ ] **Teste manual a validar quando a Etapa 4/5 estiver pronta:** confirmar que o Admin realmente bloqueia a exclusão de uma `Funcao` que já tem `AtribuicaoFuncao` vinculada (`on_delete=PROTECT`), validando na prática a proteção contra perda de rastreabilidade
- [ ] Testes automatizados para as Template Views (`ListaPessoasView`, `DetalhePessoaView`, `NovoCadastroPessoaView`) — `NovoCadastroPessoaView` já tem 1 teste via `Client` (`test_views_novo_cadastro.py`); `ListaPessoasView` e `DetalhePessoaView` seguem sem teste próprio. **Reforçado em 01/09/2026:** também sem cobertura automatizada a regra "Vínculo Formal obrigatório para Docente/Gestão" e a validação de linha completa do JS antes de "+ Adicionar" — nenhum runner de teste JS configurado no projeto.
- [ ] **Transformar as tabelas de Formação, Capacidades, Experiência Profissional e Histórico de Vínculo Formal, na tela de DETALHE, em um botão que abre pop-up** — hoje ocupam espaço fixo na tela, mesmo quando vazias (30/08/2026). **Distinto do item abaixo**, que é sobre o formulário de CADASTRO, não a tela de leitura.
- [ ] **Popup para os blocos repetíveis no FORMULÁRIO DE CADASTRO** (Formação, Experiência Profissional, Histórico de Vínculo Formal, Pendências) — ideia levantada em 31/08/2026: um único botão por bloco abre um popup para o preenchimento, em vez de ocupar espaço fixo na ficha de cadastro. **Convergiu, em 01/09/2026, com uma especificação de arquitetura maior** (ver item novo abaixo, "Migração para CRUDs independentes") — quando essa migração for implementada, este item é resolvido de quebra, já que a nova arquitetura já prevê modais por entidade.
- [ ] **Migração da arquitetura de cadastro para CRUDs independentes por entidade relacionada** (Formação, Experiência, Histórico, Pendência, Capacidade) — elimina `cloneNode()`/Formsets/`TOTAL_FORMS` como mecanismo de persistência, substituindo por `ModelForm`+View+URL+modal próprios por entidade, com FK real assim que a Pessoa existir. Especificação completa em `docs/21 - POPUP - ESPECIFICACAO_DE_ARQUITETURA_CADASTRO_DE_PESSOA_E_REGISTROS_RELACIONADOS.md`, recebida e avaliada em 01/09/2026 (ver também `docs/20 - ANDAMENTO_DO_PROJETO.md` para a análise) — **precisa de ajuste antes de implementar**: a especificação assume FK direta para `Pessoa`, mas no código real `FormacaoDocente` aponta para `DadosDocente` e `ExperienciaProfissional`/`HistoricoVinculoFormal`/`PendenciaCadastro` apontam para `AtribuicaoFuncao`; também não contempla que o primeiro salvamento de um Docente precisa criar 3 entidades juntas (`Pessoa`+`AtribuicaoFuncao`+`DadosDocente`), não só `Pessoa`. Escala comparável à migração `Funcao` (múltiplas sessões). **Planejado para branch separada, quando houver tempo dedicado — não misturar com o CRUD incremental em andamento.**
- [ ] **Extrair a montagem do contexto de template repetido** nos pontos de `return render(...)` de `NovoCadastroPessoaView.post()` para um método auxiliar único — reduz o risco de esquecer um contexto (como aconteceu com `funcao_categorias`, corrigido em 30/08/2026) em futuras alterações. **Reforçado em 01/09/2026:** o novo bloco de validação de Histórico obrigatório adicionou mais um ponto de `return render(...)` repetindo o mesmo contexto — mais um candidato a esquecimento futuro.
- [ ] Avaliar dividir `cadastros/models.py` em uma pasta `models/` com um arquivo por classe/grupo de classes relacionadas, à medida que o arquivo cresce — refatoração puramente organizacional, sem mudança de comportamento
- [ ] Manter o docstring de índice no topo de `cadastros/models.py` sincronizado conforme classes são adicionadas/removidas
- [ ] **Relatório de Pendências por Turma** (Turma → Aluno → Pendências) usando `PendenciaCadastro`, para entrega ao Coordenador de Curso — depende do módulo de Turmas existir (fora de escopo deste PI); Model já implementado (25/08/2026), pronto para quando Turma existir
- [ ] Tela/fluxo para marcar uma `PendenciaCadastro` como resolvida (`resolvida=True`, `resolvida_em`) — hoje só existe o Model, sem interface
- [ ] **Padrão a lembrar em qualquer novo campo `unique=True, blank=True` futuro:** usar `null=True` também, e garantir que a View converta campo vazio para `None` (não `""`) antes de montar o dict para o Service — o Model sozinho não basta; já causou `IntegrityError` real em RM/RA/CANAC (25/08/2026) e em `codigo_matricula_anac` (31/08/2026), corrigido nos dois casos.
- [ ] **Padrão a lembrar em qualquer Formset com linha opcional (`extra=1`, campos `required=False`):** todos os campos `required=False` permitem a linha vazia passar, mas também deixam preenchimento *parcial* passar sem erro — sempre adicionar `clean()` no Form da linha (backend) **e** validação equivalente no JavaScript antes de "+ Adicionar" (frontend) — as duas camadas são necessárias: só o `clean()` deixa o usuário adicionar uma linha incompleta na tabela visual, sem saber que vai falhar só na hora de Salvar (foi exatamente o que causou a confusão do "Docente não cadastra" em 31/08-01/09/2026). Resolvido para Formação/Experiência/Histórico de Vínculo Formal em 01/09/2026; aplicar o mesmo raciocínio (as duas camadas) a qualquer Formset novo.
- [ ] **Padrão a lembrar em qualquer bloco de Formset dinâmico com campo `<select>` (JavaScript de "Adicionar linha" via `cloneNode()`):** `cloneNode()` não preserva a opção atualmente selecionada de um `<select>` — sempre copiar manualmente o `.value` de cada `<select>` do original para o clone antes de guardá-lo como o formulário "oculto" a ser enviado. Corrigido em `form-dinamico.js` em 31/08/2026. **Nota de fragilidade estrutural reconhecida (01/09/2026):** essa correção é um "padrão a lembrar", não uma eliminação do risco — qualquer `<select>` novo adicionado a um Formset no futuro reintroduz a mesma armadilha. A eliminação de raiz está registrada como decisão de arquitetura futura (ver item "Migração para CRUDs independentes" acima).
- [ ] Padronizar versão do Python entre as máquinas do grupo (hoje: 3.14.5/3.14.3 em uma, 3.13.0 em outra, 3.10.11 na da escola/outra máquina) — atualizar Python + recriar `venv` quando for conveniente, não durante sessão de teste ativo
- [ ] **`infraestrutura/cep/{adapters,ports}.py` importava de `pessoas.models`** — corrigido durante a Etapa 2 da renomeação (31/08/2026), mas registrado como lição: a suposição de que `infraestrutura/` seria isenta de referências ao app de cadastro (documentada no plano `docs/16`) estava incorreta e não deve ser repetida em futuras reestruturações de app.
- [ ] **Padrões de PowerShell a lembrar para futuras edições em massa de arquivo (renomeações, refactors):** (1) `Get-Content -Raw` sem `-Encoding utf8` explícito corrompe acentuação ao reler o conteúdo antes de gravar — sempre especificar o encoding também na leitura, não só na gravação; (2) `Set-Content -Encoding utf8` grava BOM, que quebra parsers estritos como `json.loads()` — usar `[System.IO.File]::WriteAllText(..., New-Object System.Text.UTF8Encoding $false)` para arquivos `.json`; (3) `.Replace()`/`-replace` por correspondência de texto exato pode falhar silenciosamente se o texto não bater byte a byte — conferir sempre com `Select-String` depois, e considerar reescrever o arquivo inteiro via `create_file` quando a edição cirúrgica falhar mais de uma vez.

**`[Projeto]`**

- [ ] Recuperação de senha para usuários administradores (Django já oferece nativo via `django.contrib.auth` — falta configurar backend de e-mail e templates)
- [ ] **Tela de login + estratégia de autenticação** — decidir se usuários do sistema (além do superusuário Admin) serão o `User` padrão do Django, vinculado a `Pessoa`, ou solução customizada.
- [ ] **Reestruturação em múltiplos apps Django (arquitetura "módulo por módulo")** — decisão de arquitetura registrada em 25/08/2026, **para implementar depois** que o CRUD completo do módulo Cadastros estiver fechado. Motivo de adiar: reestruturar em cima de trabalho de CRUD ainda em andamento arrisca empilhar dois refatores simultâneos, com risco de dependências escondidas se manifestando em cascata (mesmo padrão de risco já visto nas migrações anteriores).

  **Decisões já fechadas:**
  - **App `pessoas` renomeado para `cadastros`** — ✅ **concluído e mesclado em `dev` (31/08/2026, PR #2)**. Motivo do nome: o app sempre misturou catálogo (`Funcao`, `Disciplina`) com cadastro de fato (`Pessoa`, `AtribuicaoFuncao`). **O conceito de "pré-cadastro" como app/camada separada morre** — não haverá separação futura entre `pre_cadastros` e `cadastros`; tudo fica junto num único módulo `cadastros`, só com o nome corrigido.
  - Estrutura de app Django por Bounded Context, replicando o padrão de `cadastros` (ex-`pessoas`) hoje (`models.py`, `views.py`, `forms.py`, `services.py`, `urls.py`, `tests/`, `static/<app>/`, `templates/<app>/`) para cada módulo futuro: `cadastros`, `treinamentos`, `instrucao`, e outros Bounded Contexts já mapeados em `documentacao_arquitetura.md` seção 5. Ainda não iniciada (depende da reestruturação maior, que segue adiada).
  - **App novo `core`** — página inicial, login, e estrutura/templates comuns entre os módulos (distinto de `infraestrutura/`, que fica na raiz do projeto por ser capacidade técnica genérica sem UI, como já decidido para o cliente ViaCEP). Ainda não iniciado.
  - **Site público/institucional** (ideia nova, ainda não detalhada) — como porta de entrada de acesso público, servindo de landing antes da área restrita (que abriga `cadastros`/`treinamentos`/`instrucao` etc., atrás de login). Conecta diretamente com o item de login acima, que só foi possível retomar depois que `Funcao`/`AtribuicaoFuncao` passou a existir de fato no código. Ainda não iniciado.

  **Ainda em aberto, decidir quando a reestruturação maior começar:** onde exatamente o site público/institucional mora na estrutura de apps (dentro de `core`, ou app próprio); se `cadastros` continua sendo um único app amplo (catálogo + cadastro de pessoa junto) para sempre, ou se algum dia é dividido — por ora a resposta é "não divide", mas vale reconfirmar quando a reestruturação for iniciada, com mais contexto de como o sistema cresceu até lá. **Levantado em 25/08/2026:** `Disciplina` pode não pertencer a `cadastros` a longo prazo — ela é dado de currículo, não de cadastro de pessoa, e quando os módulos `treinamentos`/`instrucao` existirem (Turma precisa de `Disciplina` também), importar de dentro de `cadastros` criaria acoplamento estranho entre módulos que deveriam ser independentes. Possível solução futura: um app `curriculo` próprio, compartilhado. Decidir junto da reestruturação, não antes.

- [ ] Avaliar GitHub Student Developer Pack (PyCharm Professional gratuito, entre outros benefícios)
- [ ] **Estratégia de Git para trabalho em grupo por módulo** — ideia original: uma branch por módulo (`cadastros`, `treinamentos`, `instrucao`), cada integrante do grupo dono de um módulo, unindo tudo só no final. Avaliado e ajustado (25/08/2026): separar o **trabalho** por módulo está certo (evita gente mexendo nos mesmos arquivos), mas manter branches **vivas até o fim** arrisca "merge hell" — divergência longa, conflitos difíceis de revisar, arquivos compartilhados (`config/settings.py`, `config/urls.py` ao registrar cada app novo) mudando sem coordenação. **Recomendação registrada:** manter o padrão que já está em uso (`main`/`dev`/`feature/*`), mas aplicado por módulo — cada pessoa foca predominantemente no seu módulo, com branches de **tarefa curta** (não uma por módulo inteiro), integrando a `dev` com frequência. **Atualizado em 31/08/2026:** para o trabalho solo atual, a pessoa responsável optou por commitar direto em `dev`, sem branch, mesmo para tarefas curtas — a recomendação de branch por tarefa acima vale para quando o trabalho em grupo por módulo realmente começar, não necessariamente antes disso. **Exceção confirmada em 01/09/2026:** a migração de arquitetura CRUD independente (ver Backlog `[Cadastro]`) será feita numa branch separada, por ser um trabalho grande e isolado — a preferência por commits diretos em `dev` continua valendo para o trabalho incremental do dia a dia.

---

## 📋 A Fazer — CRUD completo do módulo Cadastros (ex-Pessoas)

_Desbloqueado (25/08/2026): a base do modelo novo (`Funcao`/`AtribuicaoFuncao` + extensões) está implementada, testada e commitada, mesclada em `dev` (31/08/2026). Um formulário de cadastro **simplificado de transição** já existe e funciona (Pessoa + `Funcao` genérica do catálogo, sem os campos específicos por categoria) — os itens 2-4 abaixo evoluem esse formulário para a experiência completa por categoria. **Retomado em 01/09/2026** — o bug do Docente que pausou esta lista está resolvido (ver "Concluído")._

**Ordem sugerida, revisada em 25/08/2026:**

1. [ ] **Editar Pessoa** (Update) — reaproveita o Form já existente, nova View de edição.
2. [ ] **Tela de cadastro (FE 007) — Discente**: Pessoa + extensão `DadosDiscente`, com fluxo de buscar-ou-criar por CPF (Service já pronto — falta a criação da extensão e os campos específicos no Form)
3. [ ] **Tela de cadastro (FE 008) — Docente**: Pessoa + extensão `DadosDocente`
4. [ ] **Tela de cadastro (FOP 402) — Gestão**: Pessoa + `ExperienciaProfissional`, com seleção da `Funcao` específica do catálogo
5. [ ] **Adicionar nova Função a uma Pessoa já existente** (acúmulo de cargo, ou segundo curso para Discente) — via busca por CPF (Service já suporta isso; falta a tela)
6. [ ] **Editar Atribuição de Função** (situação, datas)
7. [ ] **Encerrar Atribuição de Função** (`data_fim` + `ativo=False` + motivo, ver item correspondente no Backlog para o caso Discente)
8. [ ] **Excluir/inativar Pessoa**
9. [ ] **Tela de cadastro de Disciplina** (Create/Read/Update/Delete) — hoje só existe via Admin, não depende da migração

**Outras pendências antes do deploy:**

- [ ] Configurar PostgreSQL (atualmente em SQLite) via variável de ambiente
- [ ] Ajustes de `settings.py` para produção (`DEBUG=False`, `ALLOWED_HOSTS`, `SECRET_KEY` via `.env`)
- [ ] Configurar arquivos estáticos para produção (`whitenoise` ou equivalente)
- [ ] Escolher e configurar provedor de nuvem (Render ou Railway)
- [ ] Revisão de acessibilidade nos templates HTML
- [ ] Testes de Views/API (além dos testes de Service já existentes) — inclui o endpoint `CadastrarPessoaView`, já reescrito mas ainda sem teste próprio
- [ ] Convidar colegas de grupo como collaborators no GitHub
- [ ] Sincronizar `dev` nas demais máquinas do grupo (Etapa 7 do plano `docs/16`) — escola já sincronizada (confirmado em 31/08/2026); casa e notebook pendentes, a fazer quando estiver fisicamente em cada uma

---

## ✅ Concluído

_Feito, testado e versionado_

- [x] Repositório Git criado e configurado (branches `main`/`dev`) — 19/08/2026
- [x] `.gitignore` configurado — 19/08/2026 (`f27cb9f`)
- [x] Documentação de arquitetura (DDD/SOLID pragmático, camadas, decisões de modelagem) — 19/08/2026
- [x] Estrutura inicial do projeto Django — 20/08/2026 (`513ca35`)
- [x] Ambiente validado em 5 máquinas (casa, quartel, escola, notebook) — 20-24/08/2026
- [x] README de setup para o grupo — 20/08/2026
- [x] `BuscarEnderecoPorCepService` (Porta/Adaptador ViaCEP) + 1 teste — 20/08/2026 (`662f87f`)
- [x] Endpoint de API `GET /api/pessoas/cep/<cep>/` (`BuscarCepView`) — 21/08/2026 (`b244774`) — **URL atualizada para `/api/cadastros/cep/<cep>/` em 31/08/2026 (`ec9a75c`), ver renomeação de app**
- [x] Layout base compartilhado (`templates/base.html` + `static/global/css/base.css`) — 23/08/2026 (`f337e0d`)
- [x] Bug de tooling corrigido: auto-format do VSCode quebrando templates Django — `.vscode/settings.json` versionado — 23/08/2026 (`78cf27f`)
- [x] JavaScript — busca automática de endereço por CEP no formulário — 24/08/2026 (`3a64172`)
- [x] **Redesenho arquitetural do módulo Pessoas** (`Vinculo`/`FuncaoGestao`/`Habilitacao` → `Funcao`/`AtribuicaoFuncao`), baseado em 3 formulários institucionais reais (FOP 402, FE 007, FE 008) — decisão de design fechada em 24/08/2026, ver `docs/06 - ANDAMENTO_DO_PROJETO.md`. Execução completa em 25/08/2026 (Etapas 1 a 9, ver `docs/07` a `15`). **PR #1 mesclado em `dev`** (confirmado em 31/08/2026).
- [x] **Renomeação do app `pessoas` para `cadastros`, Etapas 1 a 6** (pasta, imports, configuração, migrations/banco, testes, documentação) — 31/08/2026 (`79882c9`, `10b3e8e`, `98d9173`, `ec9a75c`, `419c9ad`), ver `docs/17 - ANDAMENTO_DO_PROJETO.md`. **PR #2 mesclado em `dev` em 31/08/2026.** Etapa 7 (sincronizar as demais máquinas) segue em andamento oportunista — escola já sincronizada.
- [x] **Bugfix: `codigo_matricula_anac` salvo como string vazia em vez de `None`** em `NovoCadastroPessoaView`, causando `IntegrityError` ao cadastrar 2º Discente com o campo em branco — 31/08/2026 (`dba6fa4`), com teste novo (`test_views_novo_cadastro.py`, primeiro teste via `Client` para uma Template View do projeto). Ver `docs/18 - ANDAMENTO_DO_PROJETO.md`.
- [x] **Bugfix: Formsets de Formação/Experiência Profissional/Histórico de Vínculo Formal aceitavam linha parcialmente preenchida sem validar campos obrigatórios do Model** no backend (ex: Curso preenchido, Ano de conclusão vazio) — 31/08/2026 (`b3c1e89`), com `clean()` customizado nos 3 Forms e 10 testes novos (`test_forms_formsets_parciais.py`). `PendenciaCadastroForm` não precisou de correção (único outro campo já `blank=True` no Model). Ver `docs/18 - ANDAMENTO_DO_PROJETO.md`.
- [x] **`choices` para `sexo`, `estado_civil` e `raca_cor`** — 3 `TextChoices` novos no `models.py` (`Sexo`, `EstadoCivil`, `RacaCor`), `ChoiceField` nos 3 campos do `CadastrarPessoaForm`, exibição via `get_<campo>_display` em `detalhe.html`. Migration `0002`. Testado (`pytest` 29 passed + manual Diretor/Coordenador) — 31/08/2026 (`dca5ab5`). Ver `docs/19 - ANDAMENTO_DO_PROJETO.md`.
- [x] **Diagnóstico e correção: dados de Pendência/Formação/Histórico descartados silenciosamente ao salvar** — causa raiz nº1: `cloneNode()` não preserva a opção selecionada de um `<select>`, corrigido copiando `.value` manualmente (31/08/2026, `dca5ab5`). Causa raiz nº2, descoberta em 01/09/2026: o botão "+ Adicionar" só validava o campo-sinal da linha, não os demais campos obrigatórios do Model, deixando linha incompleta passar visualmente e falhar só no Salvar — corrigido com validação completa no JS (`5735c5b`). Ver `docs/19` e `docs/20 - ANDAMENTO_DO_PROJETO.md`.
- [x] **Popup customizado substituindo `alert()` nativo** — overlay centralizado, botão OK, sem texto de origem da página (não removível/estilizável no `alert()` nativo) — 01/09/2026 (`5735c5b`). Ver `docs/20`.
- [x] **Nova regra de negócio: Histórico de Vínculo Formal obrigatório para Docente/Gestão** — implementada só em `NovoCadastroPessoaView` (formulário HTML), deliberadamente não no `Service`, para não quebrar a API mínima (`CadastrarPessoaView`) nem os testes existentes que cadastram Docente/Gestão sem Histórico de propósito — 01/09/2026 (`5735c5b`). Ver `docs/20`.
- [x] **Especificação de arquitetura para eliminar `cloneNode()` de vez (CRUDs independentes por entidade)** — recebida, avaliada tecnicamente e considerada boa, mas de grande escala; adiada para branch futura dedicada — 01/09/2026. Documento completo em `docs/21 - POPUP - ESPECIFICACAO_DE_ARQUITETURA_CADASTRO_DE_PESSOA_E_REGISTROS_RELACIONADOS.md`. Ver `docs/20 - ANDAMENTO_DO_PROJETO.md` (análise) e o item correspondente no Backlog `[Cadastro]`.

### Itens historicamente concluídos, agora em revisão pela migração

_Estes itens foram concluídos sob o modelo antigo (`Vinculo`/`FuncaoGestao`/`Habilitacao`) — mantidos aqui como registro histórico do que já existiu. A maioria já foi removida ou reescrita de fato (25/08/2026); os que restam "em revisão" aguardam a Etapa 7 completa (os 3 formulários especializados por categoria):_

- [x] ~~Models: `Vinculo`, `VinculoDiscente`, `VinculoDocente`, `VinculoGestao`, `FuncaoGestao`, `Habilitacao`, `FuncaoGestaoHabilitacao`~~ — 20/08/2026 (`524e6e0`) — **todos removidos de fato (25/08/2026, `49142fa` e `cf7846f`)**
- [x] ~~Django Admin registrado para essas 9 entidades~~ — 20/08/2026 (`524e6e0`) — **registro das 7 entidades antigas removido por completo (25/08/2026)**
- [x] ~~`AssociarHabilitacaoService` + 2 testes~~ — 20/08/2026 (`89ed300`) — **removido de fato em 25/08/2026 (`49142fa`)**, conceito absorvido pelo catálogo aberto `Funcao`
- [x] ~~`CadastrarPessoaComVinculoService` + 4 testes~~ — 20/08/2026 (`b347ae3`) — **reescrito por completo em 25/08/2026 (`cf7846f`)**, renomeado para `CadastrarPessoaComFuncaoService`, com fluxo buscar-ou-criar por CPF e a regra "Discente não acumula" implementada
- [x] ~~Endpoint de API `POST /api/pessoas/funcoes-gestao/habilitacoes/`~~ — 21/08/2026 (`bb01f2e`) — **removido de fato em 25/08/2026 (`49142fa`)**
- [x] ~~Endpoint de API `POST /api/pessoas/pessoas/`~~ — 23/08/2026 (`97e2915`) — **atualizado para o modelo novo em 25/08/2026 (`cf7846f`)**; falta só teste próprio (ver "A Fazer")
- [x] ~~Campo `sigla` em `Disciplina`~~ — 23/08/2026 (`fbfc3b1`) — não afetado pela migração, mantido válido
- [x] ~~Template View — lista de Pessoas~~ — 23/08/2026 (`f337e0d`) — confirmado que não dependia de `Vinculo`, mantida sem alteração
- [x] ~~Template View — detalhe de Pessoa com histórico de vínculos~~ — 23/08/2026 (`78cf27f`) — **atualizada em 25/08/2026 (`cf7846f`)** para exibir Funções em vez de Vínculos
- [x] ~~Property `tipo_legivel` em `Vinculo`~~ — 23/08/2026 (`78cf27f`) — **removida junto com `Vinculo`**; não fez falta, `funcao.nome` já é legível por si só
- [x] ~~Template View — formulário de cadastro de Pessoa (`NovoCadastroPessoaView`)~~ — 24/08/2026 (`3a64172`) — **versão de transição implementada em 25/08/2026** (Pessoa + Função genérica via dropdown); a evolução para 3 fluxos distintos por categoria (FE 007/008/402) é a Etapa 7, ainda pendente

---

## 🔭 Fora de Escopo (PI futuro)

_Não entra neste PI — mapeado como Bounded Context futuro, ver `documentacao_arquitetura.md` seção 5_

- [ ] Módulo Gestão de Turmas (`Turma`, `Modulo`, relação `Disciplina`↔`Modulo`) — confirmado fora de escopo em 24/08/2026, mesmo após a descoberta de que a FE 007 depende parcialmente disso (curso inicial, PI Inicial/Final)
- [ ] Módulo Atribuição de Instrutor
- [ ] Módulo Gestão de Treinamentos
- [ ] Módulo Diário de Classe (frequência, conteúdo, notas)

---

## Status Geral

| Métrica                           | Valor atual                                                                                                                                                    |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Services implementados            | 2 (`CadastrarPessoaComFuncaoService` reescrito, `BuscarEnderecoPorCepService` inalterado) — modelo antigo totalmente removido                                  |
| Endpoints de API implementados    | 2 (`CadastrarPessoaView` atualizado para o modelo novo, `BuscarCepView` inalterado) — prefixo `/api/cadastros/` (desde 31/08/2026)                              |
| Template Views implementadas      | 3 (lista inalterada, detalhe atualizada para Funções + choices, cadastro em versão de transição — evolução completa é o CRUD, liberado para retomar)           |
| Testes automatizados              | 29 (sem alteração nesta sessão — correções de JS e regra específica de View, sem cobertura de teste JS no projeto)                                              |
| Models do modelo antigo restantes | 0 — `Vinculo` e subtipos removidos em 25/08/2026 (`cf7846f`)                                                                                                   |
| Models do modelo novo             | 9 implementados (`Pessoa` ampliada, `Funcao`, `AtribuicaoFuncao`, `DadosDiscente`, `DadosDocente`, `ExperienciaProfissional`, `FormacaoDocente`, `VinculoFormal`/`HistoricoVinculoFormal`, `PendenciaCadastro`) |
| Catálogo `Funcao`/`VinculoFormal` populado | 11 objetos via fixture `catalogo_inicial.json` (9 Funções + 2 VinculoFormal)                                                                          |
| Validação end-to-end              | Testada manualmente pelo navegador em várias sessões; **bug do Docente (31/08) confirmado resolvido em 01/09/2026, todos os cenários testados**                 |
| Nome do app de cadastro           | `cadastros` (renomeado de `pessoas` em 31/08/2026)                                                                                                               |
| PRs no GitHub                     | 2 abertos historicamente, ambos mesclados (#1 migração Funcao, #2 renomeação cadastros) — 0 Open, 2 Closed                                                      |
| Fluxo de trabalho Git             | Commits diretos em `dev`; branches de feature mescladas preservadas no remoto como evidência de processo; exceção planejada para a migração de arquitetura CRUD (branch dedicada) |
| Última branch ativa               | `dev`                                                                                                                                                            |
| Último commit                     | `b2e3cbb` — `feat: CRUD independente de FormacaoDocente (piloto docs/21), so Create por enquanto`                                                              |

---

---

# 📐 Especificações Detalhadas de Itens do Backlog

_Este capítulo guarda o raciocínio completo e esboços de código para itens do Backlog que já foram discutidos em profundidade, mas ainda não entraram em desenvolvimento. Quando um item daqui for iniciado, mova a entrada correspondente do Backlog para "Em Andamento" e use esta seção como ponto de partida — não como código final, como referência de decisão já tomada._

## Cadastro de Formação do Docente (baseado no FE 008)

**Origem:** Formulário FE 008 — Formulário de Cadastro de Instrutor e Atribuição de Disciplina (Rev. 01, 24/06/2026). Discutido em 23/08/2026.

> **✅ Nota de atualização (25/08/2026):** `VinculoDocente` foi removido do design e `DadosDocente` já está implementado (ver `docs/08 - ANDAMENTO_DO_PROJETO.md`, Etapa 4.2). Os esboços de código abaixo já referenciam `DadosDocente` corretamente. O raciocínio de modelagem (tabela única com enum, requisitos como campos diretos por YAGNI, FK de comprovação) continua válido e ainda não foi implementado — segue no Backlog.

### Contexto do formulário

O FE 008 tem, entre outras, estas seções relevantes para `cadastros` (ex-`pessoas`):

- **Seção 3 — Graduação:** tabela com colunas Curso, Entidade, Cidade, UF, Ano de Conclusão.
- **Seção 4 — Formação Profissional:** mesmas colunas da seção 3.
- **Seção 5 — Aperfeiçoamento Profissional:** mesmas colunas da seção 3.
- **Seção 6 — Requisitos de Contratação:** dois critérios fixos, baseados na norma RBAC 141:
  - 2.3.1 — experiência docente comprovada (6 meses geral + 6 meses na área específica) — evidência em **texto livre** (análise de CV/declarações).
  - 2.3.2 — formação específica na área de atuação — evidência é uma **referência direta** a um dos cursos cadastrados nas seções 3/4/5 (identificados por numeração tipo "3.2", "4.1").
- **Seção 7 — Disciplina Habilitado(a) a Ministrar:** já corresponde ao Model `Capacidade` existente; falta o campo de documento comprobatório, que também é uma referência a um curso cadastrado (mesmo padrão do item 2.3.2).

### Decisão 1 — Tabela única para Graduação/Formação/Aperfeiçoamento

As três seções têm exatamente a mesma estrutura de colunas — só a categoria muda. Criar 3 Models seria duplicação (viola DRY) sem ganho de expressividade. Aqui, o padrão correto é **uma tabela + campo enum**.

```python
class TipoFormacaoDocente(models.TextChoices):
    GRADUACAO = 'GRADUACAO', 'Graduação'
    FORMACAO_PROFISSIONAL = 'FORMACAO_PROFISSIONAL', 'Formação Profissional'
    APERFEICOAMENTO_PROFISSIONAL = 'APERFEICOAMENTO_PROFISSIONAL', 'Aperfeiçoamento Profissional'


class FormacaoDocente(models.Model):
    dados_docente = models.ForeignKey('DadosDocente', on_delete=models.CASCADE, related_name='formacoes')
    tipo_formacao = models.CharField(max_length=30, choices=TipoFormacaoDocente.choices)
    curso = models.CharField(max_length=200)
    entidade = models.CharField(max_length=200)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    ano_conclusao = models.IntegerField()

    def __str__(self):
        return f"{self.curso} ({self.get_tipo_formacao_display()})"
```

**Nota sobre a numeração "3.1", "4.2", "5.3" do formulário físico:** é a posição do registro dentro do seu próprio tipo, usada como referência cruzada com a pasta física/digital do docente. Não precisa virar campo salvo no banco — pode ser calculada dinamicamente (property que conta a posição entre os registros do mesmo tipo e mesma pessoa) quando for implementado.

### Decisão 2 — Requisitos de Contratação: campos diretos em `DadosDocente`, não catálogo

Primeira proposta considerada foi um catálogo (`RequisitoContratacao` + tabela associativa) — descartada por ser over-engineering (**YAGNI**) para exatamente 2 critérios fixos, sem sinal de que vão crescer em variedade tão cedo.

```python
class DadosDocente(models.Model):
    atribuicao = models.OneToOneField('AtribuicaoFuncao', on_delete=models.CASCADE, related_name='dados_docente')

    # Requisito 2.3.1 — texto livre, análise de CV/declarações de serviço
    experiencia_docente_comprovada = models.TextField(
        blank=True,
        help_text="Análise de declarações de serviço, CV, etc. — comprovação de experiência docente (RBAC 141)."
    )

    # Requisito 2.3.2 — referência única a um curso já cadastrado
    formacao_especifica_comprobatoria = models.ForeignKey(
        'FormacaoDocente', on_delete=models.PROTECT, null=True, blank=True,
        related_name='comprova_requisito_para',
        help_text="Curso que comprova formação específica na área de atuação (RBAC 141)."
    )

    def possui_treinamento_valido(self) -> bool:
        return True
```

Se a EMCA um dia ampliar os critérios de contratação, a refatoração para um catálogo genérico deve ser feita **naquele momento**, com informação real sobre o novo formato — não especulativamente hoje.

### Decisão 3 — `Capacidade` ganha referência ao documento comprobatório

```python
class Capacidade(models.Model):
    dados_docente = models.ForeignKey('DadosDocente', on_delete=models.CASCADE, related_name='capacidades')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT, related_name='capacidades')
    formacao_comprobatoria = models.ForeignKey(
        'FormacaoDocente', on_delete=models.PROTECT, null=True, blank=True,
        help_text="Curso que comprova a capacidade de ministrar esta disciplina."
    )
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    # ... resto das constraints existentes inalteradas
```

### Resumo do impacto quando for implementado

| Model             | Mudança                                                                                 |
| ----------------- | ---------------------------------------------------------------------------------------- |
| `FormacaoDocente` | **Novo** — Graduação/Formação Profissional/Aperfeiçoamento numa tabela só               |
| `DadosDocente`    | +2 campos (`experiencia_docente_comprovada`, `formacao_especifica_comprobatoria`)       |
| `Capacidade`      | FK trocada de `VinculoDocente` para `DadosDocente`, +1 campo (`formacao_comprobatoria`) |

### Campos de identificação vistos no FE 008, já resolvidos

~~O formulário também tem uma seção de identificação/documentos pessoais mais completa do que o `Pessoa` atual.~~ **Resolvido em 24/08/2026** — ver `docs/06 - ANDAMENTO_DO_PROJETO.md`, item 6: os campos de identificação ampliada (RG/identidade, naturalidade, nacionalidade, filiação, nível de instrução, estado civil, etc.) entraram em `Pessoa` como parte da migração.
