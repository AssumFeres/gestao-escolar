# Andamento do Projeto — 08

**Data:** 25/08/2026
**Branch:** `feature/refatoracao-funcao`
**Sessão de tempo limitado (1h30)** — trabalho feito em passos pequenos, do menos complexo ao mais complexo, seguindo `docs/07 - PLANO_DE_MIGRACAO.md`.

---

## O que foi feito

### 1. Confirmação do ponto de partida

Branch `feature/refatoracao-funcao` criada a partir de `dev`. `pytest` rodado antes de qualquer alteração — `7 passed`, confirmando estado limpo antes de começar a migração.

Confirmado, via `git branch -a`, que uma branch criada localmente com `git checkout -b` **não aparece no GitHub** até o primeiro `git push -u origin <branch>` — comportamento esperado do Git, não uma falha do comando. A branch já existia corretamente, só não tinha sido enviada ainda.

### 2. Etapa 1 — Ampliação de `Pessoa`

Adicionados os 12 campos de identificação ampliada definidos em `06 - ANDAMENTO_DO_PROJETO.md` (`sexo`, `identidade`, `data_emissao_identidade`, `orgao_expedidor_identidade`, `naturalidade`, `uf_naturalidade`, `nacionalidade`, `filiacao_1`, `filiacao_2`, `nivel_instrucao`, `estado_civil`, `raca_cor`), todos `blank=True`. Confirmado que `data_nascimento` já existia no Model desde antes — não foi duplicado.

Confirmado que `cpf` já tinha `unique=True` desde a modelagem original — nenhuma alteração necessária ali, item do plano já resolvido sem ação.

**Decisão registrada, não executada agora:** `sexo`, `estado_civil` e `raca_cor` ficaram como `CharField` livre, sem `choices`. Decisão consciente de não travar valores agora — vira item de Backlog próprio, para forçar uma avaliação completa de quais campos desse grupo precisam de lista fechada, em vez de decidir às pressas no meio da migração.

Migration `0004_pessoa_data_emissao_identidade_pessoa_estado_civil_and_more` gerada e aplicada.

### 3. Migration pendente de sessão anterior, identificada e resolvida

Ao rodar `makemigrations` pela primeira vez, apareceu uma migration inesperada, não relacionada ao trabalho do dia: `0003_alter_disciplina_sigla`. Investigação mostrou que era só a formalização da mensagem de erro do `RegexValidator` em `Disciplina.sigla` (o texto `'Sigla deve conter exatamente 3 letras maiúsculas...'`), já presente no código-fonte de uma sessão anterior mas nunca registrada como migration. Sem efeito sobre dados existentes (`AlterField` de mensagem de validador, não da regra em si). Aplicada junto da `0004`, sem risco.

**Lição prática:** `makemigrations` detecta qualquer diferença acumulada entre o código e o histórico de migrations, não só a mudança que você acabou de fazer — vale sempre ler a saída do comando com atenção antes de assumir que ele só capturou o que você tinha em mente.

**Causa provável da primeira tentativa não ter gerado nada sobre `Pessoa`:** o arquivo `models.py` tinha sido editado no VS Code mas não salvo antes do primeiro `makemigrations` — o comando rodou sem nenhum efeito sobre `Pessoa` naquela vez, só pegando a `0003` pendente. Resolvido salvando o arquivo antes de rodar de novo.

`pytest` confirmado — `7 passed`. Commit: `feat: amplia Pessoa com campos de identificacao (FE 007/FE 008)`. Enviado ao GitHub com `git push -u origin feature/refatoracao-funcao`.

### 4. Etapa 2 — Criação de `Funcao`

Model `Funcao` criado: `id` + `nome` (`CharField`, `unique=True`) + `__str__`. Registrado no Admin.

**Discussão de design relevante, com correção de entendimento:** foi levantada a dúvida se `unique=True` em `Funcao.nome` limitaria quantas pessoas poderiam ocupar a mesma Função (ex: impedir 2 "Auxiliar Administrativo"). Esclarecido que não — `unique=True` está no **catálogo** (evita duas linhas chamadas "Aux Adm" por duplicidade/erro de digitação), e não tem relação com quantas `AtribuicaoFuncao` podem referenciar a mesma linha. Quem liga pessoas a cargos é `AtribuicaoFuncao` (Etapa 3, ainda não implementada), sem trava de unicidade prevista ali. `unique=True` mantido em `Funcao.nome`.

Migration `0005_funcao` gerada e aplicada. `pytest` — `7 passed`.

---

## 🔒 Nota de segurança de regra de negócio (importante, registrar com destaque)

Durante a discussão de edição/exclusão de `Funcao`, surgiu uma pergunta legítima: *"se eu editar 'Discente' para 'Aluno' no catálogo, perco a rastreabilidade do histórico daquele aluno? A regra de negócio 'Discente não acumula Função' quebra?"*

**Esclarecido:**
- **Editar o nome de uma `Funcao` é seguro e não apaga histórico.** A relação entre `AtribuicaoFuncao` e `Funcao` é por `id` interno, não por texto. Renomear só troca o rótulo exibido; toda atribuição antiga continua ligada à mesma linha do catálogo.
- **Excluir uma `Funcao` que já tem gente vinculada será bloqueado estruturalmente**, quando a Etapa 3 implementar a FK com `on_delete=PROTECT` (mesmo padrão já usado em `Disciplina` → `Capacidade`).
- **O ponto real de atenção, e que precisa virar regra explícita para quem for codar a Etapa 3/6:** a regra de negócio "Discente não pode acumular outra Função" **não pode ser implementada comparando o texto `Funcao.nome`** (ex: `if funcao.nome == "Discente"`). Se o catálogo for renomeado no futuro, essa comparação pararia de funcionar silenciosamente — falha de segurança de dados sutil, sem erro visível. A regra deve ser ancorada na **estrutura**: verificar se existe (ou vai existir) um `DadosDiscente` associado àquela `AtribuicaoFuncao`, não no texto do nome escolhido no catálogo.

Esta nota foi replicada em `docs/07 - PLANO_DE_MIGRACAO.md`, na Etapa 2, como lembrete obrigatório para quem for implementar a validação nas Etapas 3/6 — não é uma correção de bug (nada está quebrado hoje, `AtribuicaoFuncao` nem existe ainda), é uma decisão de design a não esquecer.

---

## Itens novos de Backlog identificados nesta sessão

- [ ] Configurar `choices` para `sexo`, `estado_civil`, `raca_cor` — usar como etapa disparadora para revisar todos os campos de identificação ampliada quanto à necessidade de lista fechada de valores, em vez de decidir campo a campo de forma avulsa.
- [ ] Ajustar o nome de exibição de `Funcao` no Admin (aparece pluralizado como "Funcaos", sem acento — cosmético, `verbose_name_plural` resolve quando for conveniente).

---

## Estado do catálogo `Funcao` ao final da sessão

**9 Funções cadastradas pelo Admin**, refletindo a realidade real da organização, não uma lista hipotética:

1. Auxiliar Administrativo
2. Secretária
3. Coordenador de Curso GMP
4. Coordenador de Curso Célula
5. Coordenador de Curso Aviônicos
6. Gerente de Qualidade
7. Diretor
8. Discente - Aluno
9. Docente - Instrutor

**Decisões esclarecidas durante a população:**
- **GSO (Gerente de Segurança Operacional) não entra no catálogo** — não se aplica à realidade da organização, cargo opcional por natureza, não faz falta.
- **Diretor = Gestor Responsável** — mesmo cargo, nomenclaturas diferentes entre EMCA e ANAC/FOP 402 para a mesma função na prática. Uma linha só, não duas.

Commit da Etapa 2 fechado com essas 9 Funções já populadas (dado de banco não entra no commit em si, só o schema — mas fica registrado aqui, no diário, qual era o estado do catálogo no momento do fechamento da etapa).

### Incidente durante a população: registro no Admin não aparecia

Depois de criar o Model `Funcao` e registrá-lo em `admin.py`, a tela do Admin não mostrava a seção "Funcaos" — só os models antigos apareciam. Causa: mesmo padrão já visto na Etapa 1 (arquivo editado no VS Code, mas não salvo antes de rodar o servidor) ou, alternativamente, o `runserver` não recarregando sozinho a tempo. Resolvido reiniciando o servidor (`Ctrl+C` e `python manage.py runserver` de novo) e atualizando a página.

### Discussão de design: `unique=True` em `Funcao.nome` não limita quantidade de pessoas por cargo

Foi levantada a dúvida (legítima, expõe uma confusão comum entre "catálogo" e "atribuição") se `unique=True` no nome da Função impediria ter, por exemplo, 2 Auxiliares Administrativos na escola. Esclarecido que não: `unique=True` está no **catálogo** (evita duas linhas "Aux Adm" por duplicidade/erro de digitação), não na **atribuição** — quantas pessoas podem ocupar a mesma Função é regulado por `AtribuicaoFuncao` (Etapa 3), sem nenhuma trava de unicidade ali. `unique=True` mantido.

### Discussão de design: editar vs. excluir `Funcao`

Perguntado se editar o nome de uma `Funcao` já vinculada a pessoas quebraria rastreabilidade ou a regra "Discente não acumula". Esclarecido com detalhe (ver seção "🔒 Nota de segurança de regra de negócio" abaixo) que editar é seguro — a relação é por `id`, não por texto — e que excluir uma `Funcao` em uso será bloqueado estruturalmente pelo `on_delete=PROTECT`, já planejado para a FK de `AtribuicaoFuncao`. Sugestão de "alerta visual" foi substituída pela proteção nativa do banco, que já cumpre esse papel — registrado como item de teste manual a validar quando a Etapa 3 estivesse pronta (ver abaixo, já concluído).

---

## Etapa 3 — Criação de `AtribuicaoFuncao`

Model criado: `pessoa` (FK → `Pessoa`, `CASCADE`), `funcao` (FK → `Funcao`, `PROTECT`), `situacao`, `data_inicio`, `data_fim` (nullable), `ativo`, `related_name='atribuicoes'` em ambas as FKs de origem (para uso futuro tipo `pessoa.atribuicoes.all()`, no mesmo espírito do `pessoa.vinculos.all()` já existente). Registrado no Admin.

### Dois erros de organização de código, ambos resolvidos rapidamente

1. **`NameError: name 'Funcao' is not defined`** — a classe `AtribuicaoFuncao` foi colada no início do arquivo `models.py` (logo após `Pessoa`), mas referenciava `Funcao`, que só existe no final do arquivo (após `Capacidade`). Python lê o arquivo de cima para baixo e precisa que uma classe já esteja definida antes de ser referenciada por outra. Resolvido movendo `AtribuicaoFuncao` para depois de `Funcao`.

2. **`NameError: name 'AtribuicaoFuncao' is not defined`** (em `admin.py`) — a linha `admin.site.register(AtribuicaoFuncao)` foi adicionada, mas o nome não tinha sido incluído no bloco de `import` no topo do arquivo. Mesma lógica do erro anterior, entre arquivos em vez de dentro de um só. Resolvido adicionando `AtribuicaoFuncao` ao `from .models import (...)`.

**Lição prática, útil para o relatório do PI:** ambos os erros eram de **ordem de definição/import**, não de lógica de negócio — categoria de erro comum e didática para ilustrar como o Python resolve nomes em tempo de execução, lendo o arquivo sequencialmente.

Migration `0006_atribuicaofuncao` gerada e aplicada sem incidente após as correções. `pytest` — `7 passed`. Commit `feat: model AtribuicaoFuncao` (`193fd99`), enviado ao GitHub.

**Nota à parte:** o primeiro `git push` dessa etapa falhou com `Could not resolve host: github.com` — instabilidade momentânea de rede, sem relação com Git ou código. Segunda tentativa, alguns segundos depois, funcionou normalmente.

---

## Reflexão sobre organização do código

Ao colar o `models.py` inteiro nesta sessão, foi expressa uma preocupação legítima: todas as classes do domínio (`Pessoa`, `Vinculo` e subtipos, `FuncaoGestao`, `Habilitacao`, `Disciplina`, `Capacidade`, `Funcao`, `AtribuicaoFuncao`) vivem num único arquivo, o que dificulta a localização visual à medida que o arquivo cresce.

Esclarecido que:
- O arquivo já tem um índice (docstring no topo listando cada classe e seu propósito) — hoje desatualizado, útil manter sincronizado conforme a migração avança.
- Django permite trocar `models.py` por uma pasta `models/` com um arquivo por classe ou grupo de classes relacionadas — refatoração puramente organizacional, sem mudança de comportamento.

**Decisão:** não fazer agora (tempo curto, prioridade é fechar a migração funcional primeiro). Registrado como item de Backlog para avaliação futura.

---

## Estado geral ao final desta sessão

| Etapa do plano de migração | Status |
|---|---|
| Antes de começar (branch, pytest) | ✅ Concluído |
| Etapa 1 — Ampliar `Pessoa` | ✅ Concluído, commitado (`feat: amplia Pessoa...`), enviado ao GitHub |
| Etapa 2 — Criar `Funcao` | ✅ Concluído, catálogo com 9 Funções populado, commitado (`44c142c`), enviado ao GitHub |
| Etapa 3 — Criar `AtribuicaoFuncao` | ✅ Concluído, commitado (`193fd99`), enviado ao GitHub |
| Etapa 4 em diante | Não iniciadas — Etapa 4 identificada como a maior do plano (3 sub-partes independentes: `DadosDiscente`, `DadosDocente`, `ExperienciaProfissional`), deixada deliberadamente para uma sessão com mais tempo disponível |

---

## Itens novos de Backlog identificados nesta sessão (consolidado)

- [ ] Configurar `choices` para `sexo`, `estado_civil`, `raca_cor` (Etapa 1) — revisar todos os campos de identificação ampliada quanto à necessidade de lista fechada de valores.
- [ ] Ajustar o nome de exibição de `Funcao` no Admin (aparece pluralizado como "Funcaos" — cosmético, `verbose_name_plural` resolve).
- [ ] Avaliar dividir `pessoas/models.py` em uma pasta `models/` com um arquivo por classe/grupo, à medida que o arquivo cresce com a migração — refatoração organizacional, sem mudança de comportamento.
- [ ] Manter o docstring de índice no topo de `models.py` sincronizado conforme classes são adicionadas/removidas na migração.

---

## Próximos passos

Etapa 4 do plano de migração — criar as 3 extensões (`DadosDiscente`, `DadosDocente`, `ExperienciaProfissional`), uma de cada vez, cada uma com seu próprio commit. Ao implementar a regra de negócio "Discente não acumula outra Função" (Etapa 6), lembrar de checar a existência de `DadosDiscente`, nunca o texto de `Funcao.nome` (ver nota de segurança acima).
