# Plano de Migração — De `Vinculo`/`FuncaoGestao`/`Habilitacao` para `Funcao`/`AtribuicaoFuncao`

**Origem da decisão:** ver `docs/06 - ANDAMENTO_DO_PROJETO.md` para o raciocínio completo por trás de cada escolha registrada aqui. Este documento é só o **como executar**, não o porquê.

**Status:** não iniciado. Nenhum passo abaixo foi executado ainda.

**Como usar este documento:** cada etapa é pequena e termina em um estado que roda e testa (mesmo que incompleto). Marque `[x]` ao concluir cada passo, e não pule etapas — a ordem importa, porque cada uma depende da anterior não quebrar o projeto.

---

## Antes de começar

- [x] Criar uma branch nova a partir de `dev`: `git checkout -b feature/refatoracao-funcao`
- [x] Confirmar que a suíte de testes atual passa antes de qualquer mudança (`pytest`) — ponto de partida limpo, para isolar qualquer erro novo como consequência da migração, não de algo pré-existente
- [ ] Fazer backup do `db.sqlite3` local antes de começar a mexer em migrations (cópia simples do arquivo, fora do Git) — o banco de desenvolvimento local não é crítico, mas evita ter que recriar dados de teste do zero se algo sair errado no meio do caminho

---

## Etapa 1 — Ampliar `Pessoa`

A menor mudança, sem dependência de nada mais, e não quebra nada existente (só adiciona campos).

- [ ] Adicionar em `Pessoa`: `sexo`, `identidade` (nº), `data_emissao_identidade`, `orgao_expedidor_identidade`, `naturalidade`, `uf_naturalidade`, `nacionalidade`, `filiacao_1`, `filiacao_2`, `nivel_instrucao`, `data_nascimento`, `estado_civil`, `raca_cor`
- [ ] Decidir e aplicar: todos esses campos devem ser `blank=True` (opcionais) nesta etapa, já que cadastros existentes não vão ter esses dados preenchidos, e forçar obrigatoriedade quebraria dados já no banco
- [ ] Adicionar `unique=True` ao campo `cpf` (confirmar primeiro se já não existe — checar `models.py` atual). **Atenção:** se já houver dados de teste no banco local com CPF duplicado ou vazio, a migration vai falhar — limpar esses registros antes, ou popular CPFs distintos
- [ ] Gerar e aplicar migration: `python manage.py makemigrations pessoas`, `python manage.py migrate`
- [ ] Rodar `pytest` — deve continuar tudo passando (nenhum teste existente depende desses campos novos)
- [ ] Commit: `feat: amplia Pessoa com campos de identificacao (FE 007/FE 008)`

---

## Etapa 2 — Criar `Funcao` (catálogo) e popular dados iniciais

- [ ] Criar Model `Funcao`: `id`, `nome` (`CharField`, provavelmente `unique=True` para evitar duplicata de cadastro por engano)
- [ ] Registrar `Funcao` no Django Admin (cadastro simples, sem regra de negócio — Admin é apropriado aqui)
- [ ] Gerar e aplicar migration
- [ ] Popular manualmente (via Admin, ou via `data migration`/fixture, a critério de quem for aplicar) as Funções já conhecidas: Diretor, Gerente da Qualidade, Secretaria, Auxiliar Administrativo, Gestor Responsável, Gerente de Segurança Operacional, Docente, Discente, e quaisquer "Coordenador de Curso de X" já em uso — **decisão a tomar na hora:** popular via fixture versionada no Git (reprodutível em qualquer máquina) ou deixar cada ambiente popular manualmente pelo Admin
- [ ] Commit: `feat: catalogo aberto Funcao`

---

## Etapa 3 — Criar `AtribuicaoFuncao`

- [ ] Criar Model `AtribuicaoFuncao`: `pessoa` (FK → `Pessoa`), `funcao` (FK → `Funcao`, `on_delete=PROTECT` — não faz sentido apagar uma Função do catálogo que já tem gente atribuída), `situacao`, `data_inicio`, `data_fim` (nullable), `ativo`
- [ ] Registrar no Admin (mesmo sabendo que, assim como o antigo `FuncaoGestaoHabilitacao`, o Admin não vai aplicar a regra de negócio de "Discente não acumula" — isso é aceitável pelo mesmo raciocínio pragmático já documentado em `03 - ANDAMENTO_DO_PROJETO.md`, mas vale já anotar como novo item de Backlog, não repetir o mesmo susto sem registro)
- [ ] Gerar e aplicar migration
- [ ] Commit: `feat: model AtribuicaoFuncao`

---

## Etapa 4 — Criar as extensões (`DadosDiscente`, `DadosDocente`, `ExperienciaProfissional`)

Fazer uma de cada vez, cada uma com seu próprio commit — são independentes entre si.

### 4.1 — `DadosDiscente`

- [ ] Criar Model: `atribuicao` (`OneToOneField` → `AtribuicaoFuncao`), matrícula (RM, RA, código ANAC, código de matrícula ANAC), documentação de estrangeiro (passaporte, autorização de permanência — `blank=True`, já que a maioria não vai preencher), contato de emergência (nome, grau de parentesco, telefone, endereço — campos de texto simples), responsável legal (nome, endereço, identidade, órgão expedidor, data de emissão, grau/qualificação — campos de texto simples, todos `blank=True`, já que só se aplica a menores de idade)
- [ ] Migration + commit: `feat: extensao DadosDiscente`

### 4.2 — `DadosDocente`

- [ ] Criar Model: `atribuicao` (`OneToOneField` → `AtribuicaoFuncao`). Este Model **substitui** o que hoje é `VinculoDocente` — reavaliar quais campos de `VinculoDocente` (ex: `situacao`, que já existe em `AtribuicaoFuncao` agora) migram para cá vs. quais já ficam cobertos pela tabela comum
- [ ] `Capacidade` precisa de ajuste: hoje tem FK para `VinculoDocente`; passa a ter FK para `DadosDocente` (ou diretamente para `AtribuicaoFuncao` — decidir qual faz mais sentido semântico na hora)
- [ ] Migration + commit: `feat: extensao DadosDocente, ajusta FK de Capacidade`
- [ ] **Atualizar a especificação de `FormacaoDocente`** no Kanban (seção "📐 Especificações Detalhadas") — ela referencia `VinculoDocente`, precisa passar a referenciar `DadosDocente`

### 4.3 — `ExperienciaProfissional`

- [ ] Criar Model: `atribuicao` (FK → `AtribuicaoFuncao`, não 1:1 — é repetível, uma `AtribuicaoFuncao` pode ter várias experiências), `organizacao`, `cargo`, `periodo` (avaliar se `periodo` vira texto livre como no FOP 402, ou dois campos `data_inicio`/`data_fim` — mais estruturado, mas o formulário original usa texto livre tipo "1999 a 2009")
- [ ] Migration + commit: `feat: model ExperienciaProfissional`

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
