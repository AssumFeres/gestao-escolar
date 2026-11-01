# Andamento do Projeto — 11

**Data:** 25/08/2026
**Branch:** `feature/refatoracao-funcao`
**Sessão dedicada à "fase pesada" da migração** — Etapa 5b (remover `Vinculo` e subtipos) + Etapa 6 (reescrever o Service de cadastro), feitas juntas por decisão de sessões anteriores, dada a interdependência entre elas.

---

## Contexto e escopo combinado antes de começar

A pessoa responsável pelo projeto trouxe, no início da sessão, uma visão maior do formulário de cadastro final: uma tela "dinâmica" com 3 fluxos por categoria (Discente/FE 007, Docente/FE 008, Gestão/FOP 402), cada um com Pessoa + campos específicos daquela categoria. Ficou combinado que essa experiência completa é trabalho da **Etapa 7**, tratada como etapa própria — a sessão de hoje resolve só a base (Model + Service), com um formulário de transição simplificado, sem os campos específicos por categoria.

Também foi decidido, quando questionado sobre o nível de detalhe do Service novo, que ele **não deveria criar as extensões** (`DadosDiscente`/`DadosDocente`) nesta etapa — só `Pessoa` + `AtribuicaoFuncao` genérica. Isso manteve a Etapa 6 enxuta e evitou antecipar decisões de UX que pertencem à Etapa 7.

---

## Sequência executada

Diferente das etapas anteriores (que podiam ser feitas isoladamente), esta exigiu uma ordem cuidadosa para manter o projeto rodável o máximo de passos possível: reescrever o Service primeiro, depois ajustar quem o consome (Views, Forms, Serializers, Templates), e só então remover `Vinculo` do `models.py`.

### 1. Reescrita do Service

`CadastrarPessoaComVinculoService` foi **renomeado** para `CadastrarPessoaComFuncaoService`, refletindo que "vínculo" já tinha saído do vocabulário do domínio desde o redesenho arquitetural (`docs/06`). Novo comportamento: `Pessoa.objects.get_or_create(cpf=..., defaults=...)` busca ou cria a Pessoa; se a Pessoa já existia, verifica a regra de negócio antes de criar a nova `AtribuicaoFuncao`.

**Regra "Discente não acumula" implementada exatamente como planejado na nota de segurança da Etapa 2:** a checagem usa `pessoa.atribuicoes.filter(dados_discente__isnull=False).exists()` — estrutura, não texto de `Funcao.nome`.

### 2. Efeito em cascata nos consumidores do Service

Como já esperado pela experiência da Etapa 5a (onde uma dependência não mapeada de `AssociarHabilitacaoService` só apareceu ao rodar o projeto), a troca do Service exigiu ajustar, em sequência:

- **`pessoas/serializers.py`** — `CadastrarPessoaInputSerializer` trocou `tipo_vinculo`/`numero_matricula` por `funcao_id`; output trocou `tipo_vinculo`/`vinculo_id` por `funcao`/`atribuicao_id`. Aproveitado para remover `FuncaoGestaoHabilitacaoInputSerializer`/`OutputSerializer`, que tinham ficado órfãos desde a Etapa 5a (a View que os usava já tinha sido removida, mas os serializers em si continuavam no arquivo, sem uso).
- **`pessoas/views.py`** — `CadastrarPessoaView` (API) reescrita para buscar a `Funcao` via `get_object_or_404` e montar `dados_atribuicao` no lugar de `dados_vinculo`. `NovoCadastroPessoaView` (Template) ajustada de forma equivalente.
- **`pessoas/forms.py`** — `CadastrarPessoaForm` perdeu o `ChoiceField` fixo de `tipo_vinculo` (3 opções) e o campo `numero_matricula`; ganhou `funcao = forms.ModelChoiceField(queryset=Funcao.objects.all())`, um dropdown com as 9 Funções do catálogo. **Decisão explícita de não incluir RM/RA/CANAC nem outros campos de identificação ampliada neste form** — são campos de `Pessoa`, mas a pessoa responsável preferiu manter o escopo de hoje enxuto, deixando a experiência completa para a Etapa 7.
- **`pessoas/templates/pessoas/detalhe.html`** — trocado `pessoa.vinculos.all()`/`vinculo.tipo_legivel` por `pessoa.atribuicoes.all()`/`atribuicao.funcao.nome`, incluindo a coluna de Situação, ausente na versão antiga por estar dentro de cada subtipo.
- **`pessoas/templates/pessoas/form_pessoa.html`** — confirmado que **não precisava de nenhuma alteração**, por usar `{{ form.as_p }}` (renderização automática por campo do Form, sem listar campos por nome no template).
- **`pessoas/templates/pessoas/lista.html`** — confirmado que não dependia de nada de `Vinculo`, sem alteração.

### 3. Reescrita dos testes (`test_cadastrar_pessoa.py`)

Os 4 testes antigos foram reescritos quase por completo, porque o comportamento testado mudou de natureza:

- `test_cadastra_pessoa_nova_com_funcao` — substitui os dois testes antigos de "cadastra com Discente"/"cadastra com Docente" (que testavam subtipos que não existem mais) por um único teste genérico, já que `Funcao` não tem mais subtipos de Model para diferenciar.
- `test_reaproveita_pessoa_existente_pelo_cpf` — **teste novo**, cobrindo o coração da Etapa 6: uma segunda Função para o mesmo CPF não duplica `Pessoa`.
- `test_rejeita_acumulo_de_funcao_para_discente` e `test_nao_cria_segunda_atribuicao_quando_discente_tenta_acumular` — substituem o antigo teste de "tipo de vínculo inválido" (`ESTAGIARIO`), que não tem mais equivalente direto no modelo novo (catálogo aberto não tem um conjunto fechado de tipos para rejeitar). Cobrem, em vez disso, a regra de negócio real do domínio.

### 4. Incidente: `services.py` com conteúdo parcial

Ao colar o arquivo `services.py` de volta para conferência, percebeu-se que ele continha **só** a classe `CadastrarPessoaComFuncaoService`, sem o docstring do topo, os imports (`ValidationError`, `transaction`, `ViaCepClient`) e sem a classe `BuscarEnderecoPorCepService` inteira. Isso gerou um `ImportError` real ao rodar `pytest` (`cannot import name 'BuscarEnderecoPorCepService'`), distinto do erro esperado (o antigo `CadastrarPessoaComVinculoService` não existir mais nos testes ainda não atualizados).

**Causa provável:** ao longo da conversa, duas versões diferentes do arquivo foram compartilhadas (uma intermediária, de rascunho, e a versão final) — o que ficou salvo foi um recorte de uma dessas versões, não o arquivo completo. Resolvido substituindo o arquivo inteiro pela versão correta, com todos os elementos.

**Lição prática:** ao pedir para colar um arquivo "inteiro" para conferência, vale desconfiar se o conteúdo aparenta estar incompleto (falta de docstring, de imports esperados, de classes que deveriam estar lá) — isso é mais rápido de detectar do que esperar o erro aparecer no terminal.

### 5. Remoção de `Vinculo` e subtipos (Etapa 5b)

Com o Service novo e todos os consumidores já ajustados, a remoção de `Vinculo`, `VinculoDiscente`, `VinculoDocente`, `VinculoGestao` do `models.py` e do Admin foi direta, sem incidentes — diferente da Etapa 5a, porque desta vez todas as dependências já tinham sido mapeadas e resolvidas antes da remoção em si.

Migration `0013_remove_vinculo_pessoa_and_more` — notável por remover também os campos `vinculo_ptr` (as FKs internas que o Django cria automaticamente para implementar Multi-table Inheritance), evidenciando de forma concreta, no próprio nome da migration, o que a herança de Model estava fazendo por baixo dos panos.

### 6. Validação: automatizada e manual

`pytest` — `5 passed`. Além disso, foi feito um **teste manual completo pelo navegador**: cadastro de uma Pessoa nova via `/pessoas/novo/`, escolha de Função pelo dropdown, redirecionamento para a tela de detalhe, confirmação visual da seção "Funcoes" mostrando Função, Situação, Data início, Data fim e Ativo corretamente. Validação de ponta a ponta (Form → View → Service → Model → Template), não só dos testes automatizados isolados.

Commit único, cobrindo as duas etapas combinadas: `refactor: remove Vinculo e subtipos, reescreve CadastrarPessoaComFuncaoService com fluxo buscar-ou-criar por CPF` (`cf7846f`) — 9 arquivos alterados, 175 inserções, 165 remoções.

---

## Estado geral ao final desta sessão

| Etapa do plano de migração | Status |
|---|---|
| Etapas 1 a 5a | ✅ Concluídas em sessões anteriores |
| Etapa 5b — Remover `Vinculo` e subtipos | ✅ Concluída nesta sessão |
| Etapa 6 — Reescrever o Service | ✅ Concluída nesta sessão |
| Etapa 7 — Views/Templates | Parcialmente concluída (o necessário para não quebrar); os 3 formulários especializados por categoria seguem pendentes, como etapa própria |
| Etapa 8 — Endpoint de API | Parcialmente concluída (serializers/view atualizados); faltam testes de View/API |
| Etapa 9 — Fechamento | Não iniciada |

**Modelo antigo:** totalmente removido do código (`Vinculo` e subtipos, `FuncaoGestao`, `Habilitacao`, `FuncaoGestaoHabilitacao`, `AssociarHabilitacaoService`). O sistema roda inteiramente sobre `Funcao`/`AtribuicaoFuncao` e as 3 extensões.

---

## Próximos passos

Duas frentes possíveis, não necessariamente na mesma sessão:
1. **Etapa 7 completa** — os 3 formulários especializados (FE 007/Discente, FE 008/Docente, FOP 402/Gestão), com seleção inicial de categoria e campos dinâmicos, incluindo a criação das extensões (`DadosDiscente`/`DadosDocente`) no momento do cadastro — trabalho de UX e Views, tratado como bloco próprio, como já decidido em sessões anteriores.
2. **Etapa 9** — fechamento formal da migração (testes de View/API pendentes da Etapa 8, revisão geral, atualização final do Kanban, Pull Request de `feature/refatoracao-funcao` para `dev`).
