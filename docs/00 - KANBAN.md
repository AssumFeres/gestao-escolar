# Kanban do Projeto — Sistema de Gestão Escolar

Quadro de acompanhamento vivo. Diferente dos arquivos `NN - ANDAMENTO_DO_PROJETO.md` (que são um diário, fechados por data), este arquivo é **atualizado continuamente** — mova os itens entre colunas conforme o status muda.

**Como atualizar:** corte o item de uma coluna e cole na outra, mantendo o formato de checklist. Ao mover para "Concluído", adicione a data e o commit relacionado entre parênteses.

---

## 🧊 Backlog
*Ideias e sugestões — ainda não decidido quando/se entram no PI atual*

- [ ] Recuperação de senha para usuários administradores (Django já oferece nativo via `django.contrib.auth` — falta configurar backend de e-mail e templates)
- [ ] Decidir estratégia de autenticação para `Pessoa` (aluno/docente) fazer login no sistema — usar `User` padrão do Django vinculado a `Pessoa`, ou solução customizada
- [ ] Avaliar GitHub Student Developer Pack (PyCharm Professional gratuito, entre outros benefícios)
- [ ] Melhorar Django Admin com Inlines (editar Vinculo/FuncaoGestao na mesma tela de Pessoa) — paliativo até as Template Views customizadas existirem
- [ ] **Reforçar `AssociarHabilitacaoService` também no nível do Model/banco** — o Django Admin, por ser genérico, não passa pelo Service e permite hoje criar `FuncaoGestaoHabilitacao` inválida (ver bug registrado em `docs/03 - ANDAMENTO_DO_PROJETO.md`). Opções: `clean()` no Model, `CHECK constraint` no Postgres futuramente, ou restringir o Admin para essa entidade.
- [ ] Adicionar campo `sigla` em `Disciplina` (ex: "AVI", "CEL", "GMP") — exige nova migration

---

## 📋 A Fazer
*Já decidido que entra neste PI, ainda não iniciado*

- [ ] Endpoint de API para `CadastrarPessoaComVinculoService`
- [ ] Template Views (HTML) para cadastro visual de Pessoa/Vínculo
- [ ] JavaScript pontual: busca automática de endereço por CEP, associação de habilitação sem reload
- [ ] Configurar PostgreSQL (atualmente em SQLite) via variável de ambiente
- [ ] Ajustes de `settings.py` para produção (`DEBUG=False`, `ALLOWED_HOSTS`, `SECRET_KEY` via `.env`)
- [ ] Configurar arquivos estáticos para produção (`whitenoise` ou equivalente)
- [ ] Escolher e configurar provedor de nuvem (Render ou Railway)
- [ ] Deploy inicial
- [ ] Revisão de acessibilidade nos templates HTML
- [ ] Testes de Views/API (além dos testes de Service já existentes)
- [ ] Convidar colegas de grupo como collaborators no GitHub

---

## 🔨 Em Andamento
*Sendo trabalhado agora*

- [ ] Camada de Views/API (DRF) — 2 de 3 Services já expostos (`BuscarEnderecoPorCepService`, `AssociarHabilitacaoService`); falta `CadastrarPessoaComVinculoService`

---

## ✅ Concluído
*Feito, testado e versionado*

- [x] Repositório Git criado e configurado (branches `main`/`dev`) — 19/08/2026
- [x] `.gitignore` configurado — 19/08/2026 (`f27cb9f`)
- [x] Documentação de arquitetura (DDD/SOLID pragmático, camadas, decisões de modelagem) — 19/08/2026
- [x] Estrutura inicial do projeto Django — 20/08/2026 (`513ca35`)
- [x] Models completos: Pessoa, Vinculo + 3 subtipos, FuncaoGestao, Habilitacao, Capacidade, Disciplina — 20/08/2026 (`524e6e0`)
- [x] Django Admin registrado para todas as 9 entidades — 20/08/2026 (`524e6e0`)
- [x] Ambiente validado em múltiplas máquinas (casa, quartel) — 20/08/2026
- [x] README de setup para o grupo — 20/08/2026
- [x] `AssociarHabilitacaoService` + 2 testes — 20/08/2026 (`89ed300`)
- [x] `CadastrarPessoaComVinculoService` + 4 testes — 20/08/2026 (`b347ae3`)
- [x] `BuscarEnderecoPorCepService` (Porta/Adaptador ViaCEP) + 1 teste — 20/08/2026 (`662f87f`)
- [x] Documentação de andamento (diário por etapa) — 20/08/2026
- [x] Endpoint de API `GET /api/pessoas/cep/<cep>/` (`BuscarCepView`) — 21/08/2026 (`b244774`)
- [x] Endpoint de API `POST /api/pessoas/funcoes-gestao/habilitacoes/` (`AssociarHabilitacaoView`) — 21/08/2026 (`bb01f2e`)
- [x] `__str__` adicionado em `VinculoDiscente`, `VinculoDocente`, `VinculoGestao`, `Habilitacao` — 21/08/2026 (`bb01f2e`)
- [x] Validação de ponta a ponta via API: bloqueio (Diretor) e sucesso (Coordenador) — 21/08/2026

---

## 🔭 Fora de Escopo (PI futuro)
*Não entra neste PI — mapeado como Bounded Context futuro, ver `documentacao_arquitetura.md` seção 5*

- [ ] Módulo Gestão de Turmas (`Turma`, `Modulo`, relação `Disciplina`↔`Modulo`)
- [ ] Módulo Atribuição de Instrutor
- [ ] Módulo Gestão de Treinamentos
- [ ] Módulo Diário de Classe (frequência, conteúdo, notas)

---

## Status Geral

| Métrica | Valor atual |
|---|---|
| Services implementados | 3 |
| Endpoints de API implementados | 2 de 3 |
| Testes automatizados | 7 (todos passando) |
| Models implementados | 9 |
| Última branch ativa | `dev` |
| Último commit | `bb01f2e` |
