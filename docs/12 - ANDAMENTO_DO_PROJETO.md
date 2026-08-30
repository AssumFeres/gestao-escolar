# Andamento do Projeto — 12

**Data:** 25/08/2026
**Branch:** `feature/refatoracao-funcao`
**Sessão dedicada ao início da Etapa 7 completa** (os 3 formulários especializados por categoria) — sessão interrompida antes do fim, com ponto de retomada claro registrado.

---

## Decisões de escopo e fluxo, tomadas antes de codar

### Escopo: formulário mais completo possível desde já

Ao planejar a Etapa 7, surgiu a pergunta de fazer uma versão enxuta (poucos campos por categoria) e completar depois, ou já implementar todos os campos das 3 extensões de uma vez. Decisão explícita da pessoa responsável pelo projeto: **ir pelo caminho mais completo possível, para evitar retrabalho** — mesmo sabendo que isso aumenta o tamanho da tarefa de hoje. Registrado aqui para não ser reconsiderado por engano numa sessão futura, já que foi uma escolha consciente, não uma omissão.

### Fluxo: dropdown único + JavaScript, não 3 telas separadas

A decisão inicial (dada no começo da sessão) tinha sido por 3 URLs/Views/Forms separados, um por categoria — mais simples de implementar, repetindo um padrão já dominado. No meio da conversa, surgiu a pergunta de se seria possível ter **um único dropdown**, listando as 9 Funções do catálogo inteiro, com a decisão de qual bloco de campos mostrar sendo **estrutural** (baseada na categoria da Função escolhida), não uma segunda camada de escolha.

Isso é possível, mas implica em uma tela só, com JavaScript reagindo à escolha do dropdown para mostrar/esconder os campos certos — sem isso, a única alternativa seria recarregar a página a cada escolha. A pessoa responsável reconheceu esse caminho como mais alinhado ao objetivo do PI de ter "script web com propósito de negócio real" (mesmo espírito documentado do JS de busca de CEP, ver diário 05), e decidiu seguir por ele, revertendo a escolha inicial de 3 telas separadas.

**Decisão final de fluxo:** 1 tela, 1 dropdown com as 9 Funções, JavaScript mostra o bloco de campos certo conforme a categoria da Função escolhida.

---

## Sub-etapas planejadas para a Etapa 7 completa

Dado o tamanho da tarefa, foi organizada em 5 sub-etapas, no mesmo espírito da Etapa 4:

1. **7.1** — Adicionar `categoria` a `Funcao` (mecanismo estrutural para a interface decidir o formulário)
2. **7.2** — Expandir o Service para criar as extensões (`DadosDiscente`/`DadosDocente`/`ExperienciaProfissional`) junto do cadastro
3. **7.3** — Expandir o Form com todos os campos das 3 categorias
4. **7.4** — Template + JavaScript, agrupando campos por categoria e alternando a exibição
5. **7.5** — Testes do Service expandido

---

## 7.1 — Adicionar `categoria` a `Funcao` ✅ Concluída

### Mecanismo

Criado enum `CategoriaFuncao` (`DISCENTE`/`DOCENTE`/`GESTAO`) e campo `categoria` em `Funcao`. Importante deixar claro, e já documentado no próprio código via docstring: este campo serve **só para a interface decidir qual formulário exibir** — não é, e não deve se tornar, mecanismo de regra de negócio. A regra "Discente não acumula Função" continua sendo verificada pela existência estrutural de `DadosDiscente`, não por este campo nem pelo nome da `Funcao` — a mesma separação de responsabilidades já estabelecida na Etapa 2 continua válida e não foi comprometida por essa adição.

### Migração de dado real, em duas etapas — decisão pedagógica

Como `Funcao` já tinha 9 registros reais no banco (alguns já com `AtribuicaoFuncao` apontando para eles, incluindo o teste manual da sessão anterior), adicionar `categoria` como campo obrigatório de uma vez geraria o problema de "qual valor aplicar às linhas existentes" — o Django ofereceria um valor one-off, mas aplicar o mesmo valor às 9 Funções estaria errado para a maioria delas.

Foi cogitado, como atalho, apagar as 9 Funções e recriá-las já com a categoria certa — descartado ao se perceber que `AtribuicaoFuncao` já tinha registro real dependendo delas (o `on_delete=PROTECT`, decisão de sessões anteriores, bloquearia a exclusão de qualquer forma). Isso rendeu uma boa discussão pedagógica: a técnica de "campo temporariamente opcional → popular manualmente → tornar obrigatório numa segunda migration" não é uma ginástica desnecessária para poucos registros — é a mesma técnica usada independente do volume de dados, e o motivo de precisar dela aqui não é a quantidade de linhas, é já ter histórico real dependendo delas.

**Execução:**
- Migration `0014_funcao_categoria` — campo `categoria` criado com `blank=True` temporário, sem pedido de valor one-off
- As 9 Funções classificadas manualmente pelo Admin: "Discente - Aluno" → Discente; "Docente - Instrutor" → Docente; as demais 7 (Auxiliar Administrativo, Secretária, 3 Coordenadores de Curso, Gerente de Qualidade, Diretor) → Gestão
- Migration `0015_alter_funcao_categoria` — campo tornado obrigatório (`AlterField`, sem `blank`); sem pedido de valor one-off, confirmando que as 9 já estavam corretamente classificadas

### Incidente: duas classes `Funcao` no mesmo arquivo

Ao adicionar o enum e o campo, o novo bloco (`CategoriaFuncao` + `Funcao` com `categoria`) foi colado no **final** do arquivo, mas a classe `Funcao` **antiga** (sem `categoria`) continuava no meio do arquivo, logo depois de `Disciplina`. Isso não gera erro do Python (a segunda definição de uma classe silenciosamente substitui a primeira), mas é uma armadilha real: código confuso, fácil de editar a definição errada por engano numa sessão futura.

**Resolvido** entregando o arquivo `models.py` completo já corrigido: a `Funcao` antiga removida, e o bloco `CategoriaFuncao` + `Funcao` nova movido para a posição correta (depois de `Disciplina`, antes de `AtribuicaoFuncao`, que depende dela — mesma regra de ordem de definição já vista em etapas anteriores). Aproveitado para atualizar o índice do docstring no topo do arquivo, que estava desatualizado desde a Etapa 5b (ainda citava `Vinculo`/`FuncaoGestao`/`Habilitacao`).

**Lição prática:** ao adicionar uma classe nova que já existe em outro ponto do arquivo (por exemplo, ao evoluir uma classe existente em vez de criar uma nova), vale considerar entregar o arquivo completo para revisão em vez de só o trecho novo — reduz o risco de duplicação silenciosa que o Python não vai sinalizar como erro.

`pytest` — `5 passed` em ambas as migrations. Commit: `feat: adiciona categoria a Funcao (Discente/Docente/Gestao), em duas migrations` (`36bf1fd`).

---

## 7.2 — Expandir o Service ⏸️ Sessão interrompida neste ponto

Decisão de mecanismo já fechada antes da interrupção: o Service vai decidir qual extensão criar checando `funcao.categoria` (estrutural), nunca por nome — mesmo princípio já aplicado.

Ficou em aberto o **formato de entrada** do Service. Proposta em discussão no momento da pausa: dois parâmetros novos, `dados_extensao: dict = None` (para `DadosDiscente`/`DadosDocente`, extensões 1:1) e `experiencias: list = None` (para `ExperienciaProfissional`, repetível, só relevante quando `categoria == GESTAO`). Não houve tempo de avaliar se esse é o melhor formato ou se vale buscar algo mais unificado — **retomar a próxima sessão exatamente por essa decisão**, antes de escrever qualquer código novo no Service.

---

## Estado geral ao final desta sessão

| Etapa/sub-etapa | Status |
|---|---|
| Etapas 1 a 6 | ✅ Concluídas em sessões anteriores |
| Etapa 7.1 — Categoria em Funcao | ✅ Concluída nesta sessão |
| Etapa 7.2 — Expandir o Service | ⏸️ Parada em ponto de decisão de design |
| Etapas 7.3, 7.4, 7.5 | ⏳ Não iniciadas |
| Etapa 8 (parcial) | Concluída em sessão anterior, como efeito colateral da Etapa 6 |
| Etapa 9 | Não iniciada |

---

## Próximos passos

Retomar a Etapa 7.2 exatamente no ponto de decisão registrado acima: fechar o formato de entrada do Service (dois parâmetros separados `dados_extensao`/`experiencias`, ou um formato mais unificado) antes de escrever qualquer código. Depois, seguir para 7.3 (Form), 7.4 (Template + JS) e 7.5 (testes), nessa ordem.
