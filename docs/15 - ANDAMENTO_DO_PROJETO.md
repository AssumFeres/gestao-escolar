# Andamento do Projeto — 15

**Data:** 30/08/2026
**Branch:** `feature/refatoracao-funcao`
**Sessão dedicada à Etapa 9 (revisão geral) do plano de migração — a última etapa antes do Pull Request.**

---

## Contexto

Com as Etapas 1 a 8 concluídas em sessões anteriores, esta sessão foi inteiramente dedicada à revisão manual de ponta a ponta antes de declarar a migração pronta para `dev`. Essa revisão cumpriu exatamente o papel para o qual foi desenhada: encontrou **3 bugs reais** que nenhum teste automatizado tinha capturado, porque só se manifestam em uso real do formulário completo — validando a decisão de reservar uma sessão fresca só para isso, em vez de tentar fechar tudo no mesmo fôlego da Etapa 8.

---

## Bug 1 — `IntegrityError` de RM/RA/CANAC ao deixar campos vazios (redescoberto)

Reaparição do mesmo padrão de erro já visto e corrigido na Etapa 7.4 (string vazia `""` colidindo com outra string vazia na constraint `unique=True`) — mas desta vez o teste manual revelou que a correção anterior (`null=True` no Model) **não bastava por si só**: era preciso também garantir, na prática de uso real, que duas Pessoas reais não usassem intencionalmente o mesmo RM/RA/CANAC por engano de digitação (diferente do caso anterior, que era sobre campo *vazio*).

**Decisão de correção, mais robusta que um simples ajuste de Model:** em vez de deixar o banco reclamar com `IntegrityError` (mensagem técnica, difícil de traduzir de forma confiável para o usuário), o Service passou a **verificar antes** de tentar criar a Pessoa — se RM, RA ou CANAC já pertencem a outra Pessoa, levanta `ValidationError` com mensagem clara (`"RM '15' já está em uso por outra pessoa."`), no mesmo padrão já usado para a regra "Discente não acumula".

**Extensão do mesmo padrão para `codigo_matricula_anac` (CMA):** ao testar, ficou claro que esse campo (em `DadosDiscente`) merecia a mesma proteção — cada Código de Matrícula ANAC deveria ser único no sistema (é emitido pela ANAC por matrícula específica). O campo **não tinha `unique=True`** até então; foi adicionado (migration `0018`), junto da mesma checagem prévia amigável no Service.

**Incidente na aplicação da migration:** como já havia 2 registros de teste com `codigo_matricula_anac=""` no banco local, a migration falhou (`UNIQUE constraint failed`) ao tentar aplicar a nova constraint. Tentativa de corrigir via shell (`update(codigo_matricula_anac=None)`) também falhou, porque a migration ainda não tinha sido aplicada — a estrutura antiga do banco ainda exigia `NOT NULL`, criando uma dependência circular (não dá para limpar o campo antes de a migration permitir `NULL`, e a migration não aplica com dado duplicado presente). Resolvido apagando os 2 registros de teste por completo (sem valor real a preservar), o que desbloqueou a aplicação da migration.

**Lição prática, útil para o relatório do PI:** ilustra uma armadilha real e não óbvia de banco de dados — alterar uma constraint em uma tabela com dados existentes exige que os dados já estejam em conformidade com a nova regra *antes* da migração aplicar, e as ferramentas de correção de dados (shell, `update()`) só respeitam a estrutura *já aplicada* do banco, não a que está prestes a ser aplicada.

---

## Bug 2 — Formsets sem `management_form` no primeiro POST real (já historicamente corrigido, reforço da lição)

Este já tinha sido corrigido na Etapa 7.4; não reapareceu nesta sessão, mas a lição segue relevante: qualquer nova tela com Formset precisa lembrar de incluir `{{ formset.management_form }}` no template, sem exceção.

---

## Bug 3 — `funcao_categorias` ausente no re-render após `ValidationError` do Service

**O mais sutil dos três, e o que gerou a maior confusão durante o teste.** Ao tentar cadastrar um Discente com RM duplicado, a pessoa responsável relatou que a tela "recolheu" todos os blocos visuais depois do erro, dando a impressão de que os dados digitados tinham sido perdidos.

**Diagnóstico:** o contexto `funcao_categorias` (o mapa `{id: categoria}` usado pelo JavaScript para decidir quais blocos mostrar) tinha sido incluído corretamente em dois dos três pontos de renderização da View (`get()` e no re-render por falha de validação de Formset), mas **esquecido no terceiro** — o re-render específico do bloco `except ValidationError as e:`, que é justamente o caminho acionado pelas regras de negócio do Service (Discente acumulando Função, RM/RA/CANAC/CMA duplicado). Sem esse contexto, o JavaScript não sabia qual categoria estava selecionada e escondia todos os blocos condicionais por segurança — dando a falsa impressão de perda de dados, quando na verdade era só um problema de exibição.

**Esclarecido e reforçado com a pessoa responsável:** como todo o cadastro roda dentro de `transaction.atomic()`, um `ValidationError` desfaz **tudo** automaticamente — não existe cenário de dado salvo pela metade. A confusão visual não refletia nenhum risco real de integridade de dado, só uma experiência de usuário ruim.

**Correção:** uma linha adicionada — `'funcao_categorias': self._funcao_categorias()` — no `render()` dentro do bloco `except ValidationError`.

**Lição prática:** um contexto de template repetido em múltiplos pontos de retorno de uma View (aqui, 3 `return render(...)` diferentes dentro do mesmo método) é um ponto de manutenção frágil — fácil de atualizar dois lugares e esquecer o terceiro. Vale considerar, em revisão futura, extrair a montagem desse contexto para um método auxiliar único, chamado nos 3 pontos, para eliminar esse tipo de risco de raiz.

---

## Ampliação da tela de detalhe

A pessoa responsável notou, durante o teste, que a tela de detalhe mostrava poucos dados de `Pessoa` (só 5 campos básicos) e nenhum dos dados específicos por categoria. Quatro rodadas de ampliação:

### Rodada 1 — Pendências de Documentação
Primeira tabela nova adicionada, em formato leitura, resolvendo a lacuna mais imediata sentida (dados cadastrados mas invisíveis na tela).

### Rodada 2 — Formatação de data e layout compacto
- Data de nascimento aparecia em formato inglês (`Sept. 26, 1988`) por falta do filtro `|date:"d/m/Y"` no template — corrigido em toda a tela (nascimento, emissão de identidade, datas de Função).
- Layout da tabela principal reestruturado para **2 pares de campo por linha** (em vez de 1 por linha), reduzindo a altura da página; todos os campos de identificação ampliada de `Pessoa` passaram a aparecer.
- Padding vertical das linhas de tabela reduzido globalmente (`base.css`, de `0.6rem` para `0.3rem`), deixando toda tabela do sistema mais compacta, não só a de detalhe.

### Rodada 3 — Tabelas de Formação, Capacidades, Experiência Profissional, Histórico de Vínculo Formal
Adicionadas como tabelas de leitura, completando a exibição dos dados que já eram salvos desde a Etapa 7 mas nunca apareciam em lugar nenhum da interface. **Decisão registrada para o Backlog:** essas 4 tabelas devem, no futuro, virar um botão que abre um pop-up com os detalhes, em vez de ocupar espaço permanente na tela — não implementado agora, por ser mudança de interação (JavaScript novo), fora do escopo de "só mostrar os dados que faltavam".

### Rodada 4 — CEP e Dados do Discente (Matrícula ANAC, Contato de Emergência, Responsável Legal)
Campo `endereco_cep` isolado numa linha própria (antes só aparecia embutido no texto de `pessoa.endereco`). Novo bloco condicional — usando `{% with %}` e `{% if %}` sobre `atribuicao.dados_discente`, que existe apenas quando a categoria é Discente — mostrando Código de Matrícula ANAC, documentação de estrangeiro, contato de emergência e dados do responsável legal. Esclarecido que esse bloco aparecer só para Discente é o comportamento correto e esperado, não um bug: `DadosDiscente` só existe como registro quando a `AtribuicaoFuncao` é dessa categoria.

**Nota técnica registrada:** o acesso `atribuicao.dados_docente.formacoes.all` (e equivalentes) funciona sem erro para Pessoas que não são Docente/Gestão porque o Django trata falhas de resolução de variável em template (`ObjectDoesNotExist` em relações `OneToOneField` inexistentes) como silenciosas, retornando vazio — não é necessário `{% if %}` explícito para a maioria dos casos, só onde o template precisa reagir de forma diferente à ausência do dado (como no bloco de Discente, que imprime um título condicional).

---

## Testes automatizados adicionados

Dois novos testes em `test_cadastrar_pessoa.py`, cobrindo os cenários reais encontrados na revisão manual:
- `test_rejeita_registro_matricula_duplicado_com_mensagem_amigavel`
- `test_rejeita_codigo_matricula_anac_duplicado_com_mensagem_amigavel`

`pytest` — `18 passed` (16 anteriores + 2 novos).

Commit desta sessão: `7ee2ba4` — 7 arquivos alterados (`models.py`, `services.py`, `views.py`, `detalhe.html`, `base.css`, `test_cadastrar_pessoa.py`, migration `0018`).

---

## Estado geral ao final desta sessão

| Etapa do plano de migração | Status |
|---|---|
| Etapas 1 a 8 | ✅ Concluídas em sessões anteriores |
| Etapa 9 — Revisão geral | ✅ Concluída nesta sessão — 3 bugs reais encontrados e corrigidos, tela de detalhe ampliada, 2 testes novos |

**Migração completa.** Falta apenas: atualização final da documentação (Kanban, plano de migração) e abertura do Pull Request de `feature/refatoracao-funcao` para `dev`.

---

## Itens novos de Backlog identificados nesta sessão

- [ ] Transformar as tabelas de Formação, Capacidades, Experiência Profissional e Histórico de Vínculo Formal, na tela de detalhe, em um botão que abre pop-up — hoje ocupam espaço fixo na tela, mesmo quando vazias.
- [ ] Considerar extrair a montagem do contexto de template repetido nos 3 pontos de `return render(...)` de `NovoCadastroPessoaView.post()` para um método auxiliar único, reduzindo o risco de esquecer um contexto (como aconteceu com `funcao_categorias` nesta sessão) em futuras alterações.

---

## Próximos passos

Atualizar `docs/00 - KANBAN.md` e `docs/07 - PLANO_DE_MIGRACAO.md` fechando a Etapa 9, e abrir o Pull Request de `feature/refatoracao-funcao` para `dev`.
