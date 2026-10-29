# Andamento do Projeto — 24

**Data:** 02/09/2026 (máquina de casa)
**Branch:** `dev` (commits diretos)
**Sessão dedicada a: fechar o "D" que faltava em Formação (Delete) e implementar o CRUD completo (Create/Update/Delete) de `ExperienciaProfissional`, replicando o padrão via popup já validado duas vezes.**

---

## Contexto

Continuação direta do diário 23 (CRUD de `HistoricoVinculoFormal` fechado e testado). Antes de avançar para Experiência, uma revisão rápida das regras de negócio por entidade revelou uma lacuna real: `FormacaoDocente` nunca teve Delete implementado, apesar de a regra de negócio permitir exclusão real (diferente de `HistoricoVinculoFormal`, que nunca permite). Decisão: fechar essa lacuna e implementar Experiência no mesmo fôlego, já que as duas usam o mesmo padrão (Delete real).

---

## Tabela de regras de negócio consolidada

| Entidade | Create | Update | Delete |
|---|---|---|---|
| Formação | ✅ (diário 22) | ✅ (diário 22) | ✅ (esta sessão) |
| Vínculo Formal | ✅ (diário 23) | ⚠️ restrito, só Encerrar (diário 23) | ❌ nunca (regra de negócio) |
| Experiência Profissional | ✅ (esta sessão) | ✅ (esta sessão) | ✅ (esta sessão) |

---

## Implementação

### 1. Delete de `FormacaoDocente`

`ExcluirFormacaoDocenteView` (`DeleteView`), usando um template de confirmação **genérico** — `_confirmar_exclusao_fragment.html`, com `{{ object }}` (aproveitando o `__str__` de qualquer Model) para mostrar o que será excluído, sem precisar de um fragmento específico por entidade.

### 2. `ModalCrudMixin` estendido para `DeleteView`

O mixin já tratava `form_valid()` para `CreateView`/`UpdateView`. `DeleteView` não usa `form_valid()` — usa `delete()`. Adicionado um `delete()` sobrescrito no mixin, com a mesma lógica (JSON no sucesso quando `?parcial=1`, comportamento normal de redirect senão). Como o `get_template_names()` já era genérico, a página de confirmação (tanto a completa quanto o fragmento do popup) funcionou sem nenhuma mudança adicional.

### 3. CRUD completo de `ExperienciaProfissional`

Estrutura idêntica às duas entidades anteriores: `ExperienciaProfissionalModelForm` (`organizacao`, `cargo`, `data_inicio`, `data_fim`, com os widgets de data corretos desde o início — lição do diário 23 já aplicada), 3 Views (`Adicionar`/`Editar`/`Excluir`), `AtribuicaoFuncao` como pai resolvido pela URL.

**Nenhuma linha de JavaScript nova foi necessária** — `modal-crud.js`, generalizado na sessão anterior, funcionou de primeira para a terceira entidade sem ajuste algum. Isso confirma que a decisão de generalizar o mecanismo logo depois do primeiro piloto (Formação) foi acertada.

### 4. `detalhe.html` — seção de Experiência reestruturada

Antes, a tabela de Experiência Profissional simplesmente listava tudo, sem distinção por `AtribuicaoFuncao`. Reestruturada no mesmo padrão já usado para Histórico de Vínculo (agrupada por Função, com botão "+ Adicionar" por grupo), visível só para categoria **Gestão** (`atribuicao.funcao.categoria == 'GESTAO'`) — únicas Pessoas que têm essa entidade, conforme o `Service`.

`pytest` — `29 passed`, sem alteração (mudanças de View/Form/Template, sem cobertura automatizada ainda — item já no Backlog).

**Testado manualmente, todos com sucesso:**
- Excluir Formação (popup de confirmação, linha some da tabela)
- Adicionar/Editar/Excluir Experiência Profissional
- Regressão: Formação Adicionar/Editar e Vínculo Adicionar/Encerrar continuam funcionando

**Commit:** `6878fd9` — `feat: Delete de FormacaoDocente + CRUD completo (Create/Update/Delete) de ExperienciaProfissional`.

---

## Bug reportado durante o teste — registrado para investigação, não diagnosticado

Ao testar o **cadastro inicial** de uma Pessoa (mecanismo antigo, Formset + `cloneNode()` — não o CRUD novo), a pessoa responsável adicionou 2 linhas de Experiência Profissional via "+ Adicionar" e submeteu o formulário. A submissão falhou por uma regra de negócio do `Service` (CANAC duplicado — comportamento correto do sistema). Ao reaparecer a tela com o erro, **a 2ª linha de Experiência "sumiu"**.

**Decisão explícita:** registrar como investigação, não como bug já diagnosticado — uma suspeita foi anotada (o template só renderiza manualmente `experiencia_formset.0`, nunca re-desenha linhas já "adicionadas" via JS quando o servidor re-envia a página inteira após um erro), mas não foi confirmada com reprodução controlada. Criada uma seção nova no Kanban, **"🔎 Investigação de Possíveis Bugs"**, separada do Backlog normal — reservada para relatos que ainda precisam de diagnóstico antes de qualquer tentativa de correção.

---

## Estado geral ao final desta sessão

| Item | Status |
|---|---|
| Delete de `FormacaoDocente` | ✅ Implementado e testado |
| CRUD completo de `ExperienciaProfissional` (Create/Update/Delete) | ✅ Implementado e testado |
| Template de confirmação de exclusão genérico | ✅ Criado, reutilizado por 2 entidades já |
| `ModalCrudMixin` funcionando com `DeleteView` | ✅ Confirmado |
| Bug: 2ª linha de Formset perdida no re-render após erro | 📝 Registrado para investigação (seção nova no Kanban) |
| Testes automatizados | 29 passed (sem alteração) |

---

## Itens novos de Backlog/Investigação identificados nesta sessão

- [ ] **Nova seção "🔎 Investigação de Possíveis Bugs" criada no Kanban** — para relatos que precisam de diagnóstico antes de virar item de Backlog normal com correção proposta.
- [ ] **Segunda linha de Formset "perdida" ao re-renderizar após erro do Service, no cadastro inicial de Pessoa** — ver detalhes na seção de investigação do Kanban. Suspeita: template só renderiza `formset.0`, não re-popula linhas já adicionadas via JS depois de um reload completo do servidor.
- [ ] Testes automatizados para `ExcluirFormacaoDocenteView`, `AdicionarExperienciaProfissionalView`, `EditarExperienciaProfissionalView`, `ExcluirExperienciaProfissionalView` — nenhum ainda.
- [ ] Aplicar o mesmo padrão de CRUD via popup para `PendenciaCadastro` (única entidade repetível do cadastro inicial que ainda não tem CRUD independente) — deve ser a mais simples das 4, já que não tem regra de "nunca excluir" nem múltiplos campos obrigatórios condicionais.

---

## Próximos passos

Replicar o mesmo padrão de CRUD via popup para `PendenciaCadastro` — a última das 4 entidades repetíveis do cadastro inicial, fechando a migração de arquitetura `docs/21` para todas elas (só `Capacidade`, ligada à tela de Requisitos ainda placeholder, ficaria de fora por enquanto). Depois, investigar o bug reportado sobre a 2ª linha de Formset perdida, e retomar o encerramento de `AtribuicaoFuncao` para Discente.
