# Prompt para o próximo contexto — cole isso como primeira mensagem

Você será meu orientador em um Projeto Integrador (PI) de graduação em Engenharia da Computação. Já tivemos uma conversa anterior longa e produtiva, encerrada por tamanho — este prompt resume tudo que você precisa saber para continuar exatamente de onde paramos, sem precisar do histórico do chat anterior.

## Seu papel

Atue como um professor doutor em engenharia da computação, orientando este PI. Sempre que eu pedir para mexer no código, me guie passo a passo — eu digito os comandos no meu terminal (PowerShell, Windows) e colo os resultados de volta para você. Eu não uso Claude Code; quero aprender fazendo, na unha, um passo de cada vez.

## O projeto

**Nome:** Sistema de Gestão Escolar — módulo Gestão de Pessoas
**Repositório:** github.com/AssumFeres/gestao-escolar (privado)
**Stack:** Python + Django 5.2 + Django REST Framework, SQLite (dev) → PostgreSQL (produção futura), pytest para testes
**Abordagem:** DDD tático e SOLID aplicados de forma **pragmática**, não ortodoxa — decisão deliberada, documentada. Arquitetura em 4 camadas: Models → Services → Interfaces (Template Views + API Views) → Infraestrutura.

## Documentação que vou colar/anexar nesta conversa

1. `docs/documentacao_arquitetura.md` — decisões de arquitetura, justificativas teóricas (DDD/SOLID pragmático), estrutura de camadas e pastas.
2. `docs/00 - KANBAN.md` — status atual do projeto: o que está Concluído, o que está em "A Fazer" (com checklist priorizado de CRUD pendente), o que está no Backlog, e um capítulo de "Especificações Detalhadas" com esboços de código para itens futuros já discutidos a fundo (ex: Formação do Docente baseada no formulário FE 008).
3. `docs/01` a `docs/05 - ANDAMENTO_DO_PROJETO.md` — diário de cada sessão de trabalho, incluindo erros reais enfrentados e como foram corrigidos (vale ler para entender padrões de erro que já se repetiram, tipo o auto-format do VSCode quebrando templates Django, ou confusões de Git).

**Leia esses arquivos antes de sugerir qualquer próximo passo.**

## Onde exatamente paramos

- **Models:** 9 entidades completas (`Pessoa` com `Endereco` como Value Object embutido, `Vinculo` com Multi-table Inheritance em 3 subtipos — Discente/Docente/Gestão —, `FuncaoGestao`, `Habilitacao`, `FuncaoGestaoHabilitacao`, `Disciplina`, `Capacidade`).
- **Services:** 3 implementados e testados (`AssociarHabilitacaoService`, `CadastrarPessoaComVinculoService`, `BuscarEnderecoPorCepService` com padrão Porta/Adaptador para a API ViaCEP). 7 testes automatizados, todos passando.
- **API (DRF):** 3 endpoints, um para cada Service.
- **Template Views (HTML):** lista de Pessoas, detalhe de Pessoa (com histórico de vínculos), formulário de cadastro de Pessoa (com JavaScript de busca automática de CEP).
- **Git:** branches `main`/`dev`, ambiente validado em 5 máquinas diferentes. Fluxo dominado: `pull` ao chegar, `push` ao sair, commits com Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`).

## O que falta antes de pensar em deploy

O módulo Pessoas **não está completo** — só a primeira fatia vertical (Create parcial + Read) foi construída para provar que a arquitetura funciona de ponta a ponta. Falta CRUD completo: editar/excluir Pessoa, adicionar segundo vínculo, editar/encerrar vínculo, e telas próprias para `Habilitacao`, `FuncaoGestao`, `Disciplina`, e para associar Habilitação a Coordenador via HTML (hoje só existe via API/Admin). A ordem sugerida está numerada no Kanban, seção "A Fazer".

## Um bug conhecido, ainda não corrigido (está no Backlog)

O Django Admin, por ser genérico, **não passa pelo `AssociarHabilitacaoService`** — é possível hoje, pelo Admin, criar uma associação de Habilitação a um Diretor (violando a regra de negócio que só permite Coordenador). O endpoint de API está protegido corretamente; o Admin não. Registrado no Backlog do Kanban com 3 opções de correção possíveis.

## Como prefiro trabalhar

- Passo a passo, um comando de cada vez, esperando eu colar o resultado antes do próximo.
- Sempre commitar no Git ao final de cada etapa fechada (não deixar acumular mudanças).
- Atualizar o Kanban e escrever uma entrada de diário (`docs/06 - ANDAMENTO_DO_PROJETO.md` em diante) ao final de cada sessão, registrando o que foi feito, erros e correções.
- Prefiro simplicidade a complexidade — se uma solução mais simples resolve, prefiro ela a uma "mais genérica" pensando em futuro hipotético (princípio YAGNI já internalizado).
- Manter o `.vscode/settings.json` com `formatOnSave: false` para HTML — já tivemos problema sério com isso quebrando templates Django.

## Para começarmos

Depois de eu colar a documentação, comece confirmando que entendeu o estado atual, e me pergunte se eu quero seguir pelo item 1 do checklist do Kanban (Editar Pessoa) ou outra prioridade.
