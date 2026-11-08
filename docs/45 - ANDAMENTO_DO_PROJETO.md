# Andamento do Projeto — 45

**Data:** 08/11/2026

**Branch:** `main`

**Sessão dedicada a: conclusão dos lotes de interface/acessibilidade, contraste e responsividade, formulários, foco, rótulos e tabelas; correção do vínculo Pessoa/Ata; auditoria final, validação do responsável e organização das próximas ações.**

---

## 1. Contexto e ponto de partida

O responsável solicitou retomar o projeto. Foi consultado o fechamento do diário 44, que propõe revisar contraste, zoom de 200% e responsividade, continuar a adoção dos componentes de formulário e realizar a validação final dos fluxos principais.

O histórico local estava no commit `543c5bc` (`feat: melhora acessibilidade e navegacao por teclado`), sem alterações locais pendentes. A retomada seguiu o `AGENTS.md` e as skills `django-accessibility` e `code-change-verification`.

Este diário dá continuidade ao registro que subsidiará a apresentação e o relatório do PI. As confirmações da sessão anterior permanecem no diário 44; não foram consideradas evidência de validação visual das novas alterações.

---

## 2. Inspeção e problemas identificados

A base global carrega `static/global/css/base.css`. Foram revisados os tokens de cores, estilos dos campos, layout com sidebar, breakpoints e a ficha de Pessoa que usa `.grid-detalhes-4`.

| Ponto | Evidência anterior |
|---|---|
| Texto secundário | `#64748b` sobre `#f4f7fa`: 4,43:1; sobre `#eaf0f8`: 4,15:1 |
| Links de texto | `#2f75b5` sobre `#eaf0f8`: 4,23:1 |
| Bordas dos campos | `#cbd5e1` sobre branco: 1,48:1 |
| Layout estreito | Sidebar com base fixa de 220px, sem regra para empilhar menu e conteúdo |
| Detalhe de Pessoa | Grid de quatro colunas sem redução própria para telas estreitas |
| Campos e agrupamentos | Ausência de limite global de largura dos campos e `min-width` mínimo dos fieldsets |

Os cálculos usam as cores declaradas no CSS e luminância relativa sRGB; não são amostras de pixels da tela. A avaliação de contraste é restrita às combinações identificadas. Os problemas de layout foram identificados por inspeção das regras, ainda sem medição de renderização no navegador.

---

## 3. Alterações de contraste

Foram feitos ajustes nas variáveis compartilhadas:

- Criada `--cor-link: #26669f`, usada nos links comuns. O azul institucional `--cor-primaria` e o destaque existente foram preservados.
- Alterada `--cor-texto-secundario` para `#526178`, escurecendo discretamente os textos auxiliares que usam a variável.
- Criada `--cor-borda-controle: #7b8794`, aplicada somente às bordas dos campos já estilizados pela regra global. A borda estrutural de tabelas, cards e fieldsets permanece em `--cor-borda`.

| Variável | Menor razão nos três fundos globais avaliados |
|---|---|
| `--cor-link` | 5,26:1 |
| `--cor-texto-secundario` | 5,48:1 |
| `--cor-borda-controle` | 3,19:1 |

Os três fundos avaliados são `--fundo-card`, `--fundo-pagina` e `--fundo-secao`. As razões mínimas dos textos superam 4,5:1; a borda supera 3:1. A distinção da borda é relevante quando necessária para perceber o campo, conforme o critério de contraste não textual.

Não foram alterados os fundos institucionais, cores de Salvar/Cancelar, caixas de erro, mensagens de consulta ou anel duplo de foco aprovados na sessão anterior. Regras mais específicas, inclusive cores inline, continuam exigindo revisão própria.

---

## 4. Adaptação para telas estreitas

- Inputs, selects e textareas receberam `max-width: 100%` e `box-sizing: border-box`, para respeitar a largura disponível.
- Fieldsets receberam `min-width: 0`, permitindo reduzir sua largura dentro dos grids.
- O link do cabeçalho recebeu limites de largura; em telas até 700px, seu título pode quebrar palavras longas.
- Até 700px, menu e conteúdo passam a ficar um acima do outro, retirando a reserva lateral fixa de 220px. O accordion, links e comportamento de foco permanecem os mesmos.
- Nesse breakpoint, o padding do cabeçalho e do conteúdo passa a 1rem.
- A ficha de Pessoa passa de quatro para duas colunas até 1000px e para uma coluna até 700px. Valores longos podem quebrar dentro de cada cartão.

Os limites são definidos em pixels CSS; o zoom do navegador pode reduzir a largura disponível e acionar os breakpoints. Isso precisa ser confirmado no navegador: apenas a existência dessas regras não comprova uso adequado em 200% ou conformidade de reflow.

---

## 5. Arquivos alterados

- `static/global/css/base.css` — variáveis de contraste, limites de campos e breakpoints.
- `templates/base.html` — CSS atualizado para `?v=20261108-1`, para obter a folha nova após recarregar a página.
- `docs/45 - ANDAMENTO_DO_PROJETO.md` — registro desta sessão.

Não foram alterados JS, IDs, seletores, campos, URLs, formulários, validações, models, views, autenticação, permissões ou regras de negócio. Não foram criadas migrations ou dependências.

---

## 6. Verificações executadas

| Verificação | Resultado |
|---|---|
| `manage.py check` pelo ambiente virtual | Sem problemas identificados |
| `python -m pytest -p no:cacheprovider -q --tb=short` | **52 passed in 3.02s** |
| Quatro arquivos JS com `node --test --test-reporter=dot` | **30 testes aprovados** |
| Cálculo pontual de contraste em Node | Limites de 4,5:1 para os textos e 3:1 para as bordas atendidos nos três fundos avaliados |
| Revisão do diff e `git diff --check` | Sem erros |

Foram usados os runners existentes. Não foram criados testes que apenas repetissem as regras de CSS. Os testes JS mantêm as limitações de DOM simplificado documentadas no diário anterior. As verificações automatizadas não demonstram o layout real, o algoritmo nativo de Tab ou anúncios por leitor de tela.

A inspeção de status ainda informa acesso negado ao diretório ignorado `.pytest_cache`; o runner continua sendo executado sem o cache. Não houve falha nos testes.

---

## 7. Referências de acessibilidade

- [WCAG 2.2 — Contraste mínimo de texto, 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- [WCAG 2.2 — Contraste não textual, 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)
- [WCAG 2.2 — Redimensionamento de texto, 1.4.4](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html)
- [WCAG 2.2 — Reflow, 1.4.10](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html)

Zoom de 200% e reflow são avaliações relacionadas, mas distintas. A referência de reflow inclui largura equivalente a 320px CSS e exceções para conteúdo que exige disposição em duas dimensões, como tabelas de dados; isso não dispensa verificar acesso e leitura dessas tabelas.

---

## 8. Validação manual pendente

1. Recarregar uma tela principal e conferir as cores dos links, textos auxiliares e bordas dos campos.
2. Testar zoom de 200% na lista, cadastro e detalhe de Pessoa. Conferir campos, labels, mensagens e cartões de dados, sem sobreposição ou perda de conteúdo.
3. Reduzir a janela até 700px CSS ou menos: confirmar menu acima do conteúdo, grupos acessíveis, título legível e navegação por Tab preservada.
4. Conferir que, ao entrar pelo menu ou abrir formulário de página completa, o foco continua no primeiro controle disponível; repetir com popup, Esc, Cancelar e salvamento.
5. Conferir a ficha de Pessoa em larguras acima de 1000px, entre 701–1000px e até 700px.
6. Identificar tabelas ou páginas com estilos inline que ainda causem cortes ou rolagem inadequada. Não foi aplicada ocultação global de overflow para esconder esses problemas.

---

## 9. Estado e próximos passos

O primeiro lote de hoje está implementado e verificado automaticamente. A validação visual permanece pendente. Não é uma certificação WCAG global nem a conclusão da revisão de contraste/responsividade de todas as telas.

Após a confirmação, tratar tabelas largas e layouts inline por exemplos concretos, mantendo alterações pequenas. Em seguida, continuar a adoção dos componentes compartilhados nos formulários restantes e realizar a validação final dos fluxos principais.

---

## 10. Confirmação do responsável e próximo lote proposto

Após a entrega e as orientações para conferir o cadastro, detalhe de Pessoa, menu e zoom de 200%, o responsável informou **“Está tudo funcionando”**. A validação manual deste primeiro lote foi considerada concluída com base nesse relato, sem teste adicional de navegador pelo agente.

Não foi relatado corte ou problema de rolagem específico que exija outra alteração de layout neste momento. A revisão de tabelas largas e estilos inline permanece condicionada à identificação de exemplos concretos durante a validação final.

O próximo lote proposto é aplicar os componentes de campos e resumo de erros já aprovados aos formulários de Ata, Oferta de Módulo e Turma. A inspeção dos três fragmentos confirmou que ainda renderizam os campos diretamente. A expansão deve manter campos, URLs, seletores, valores, validações e regras de negócio, com atenção à criação e edição em página e modal.

Depois desse lote, continuar com os formulários restantes e realizar uma rodada final dos fluxos principais por teclado, leitor de tela e zoom. Os checks e testes serão executados após cada alteração de código e registrados aqui.

Esta atualização alterou apenas o diário; não foram implementadas mudanças nos formulários nem repetidos testes automatizados.

---

## 11. Formulários de Ata, Oferta de Módulo e Turma

### 11.1 — Autorização e inspeção

O responsável autorizou executar o lote proposto na seção 10. Foram revisados os três fragmentos, suas páginas completas, os forms existentes e os includes de campo e resumo de erros.

Os três formulários compartilham a renderização entre página completa e modal. Ata e Oferta ainda não apresentavam resumo de erros gerais; Turma apresentava `non_field_errors` sem o resumo padronizado. O número da Ata tinha ajuda em vermelho inline e sem o elemento com ID esperado pelo Django para a associação automática.

### 11.2 — Alterações aplicadas

Os campos passaram a usar `includes/campo_formulario.html`, que reúne label, indicação de obrigatoriedade, ajuda e mensagem de erro junto ao controle. O resumo usa `includes/resumo_erros_formulario.html`, mantendo um link com o nome de cada campo inválido, sem repetir ali sua mensagem completa.

| Formulário | Campos preservados, na ordem original |
|---|---|
| Ata | número, tipo, finalidade, data, assunto, observação |
| Oferta de Módulo | módulo, ano letivo, data de início, observação |
| Turma | nome, sigla, período, observação |

Na Ata, foram preservados os três fieldsets e seus grids. Os agrupamentos receberam legendas visualmente ocultas: “Identificação da ata”, “Finalidade e data” e “Assunto e observação”. A ajuda de número usa o estilo compartilhado e o ID `id_numero_helptext`, referenciado pelo campo. O número continua opcional: a instrução de deixá-lo em branco para geração automática foi mantida integralmente.

Os botões Salvar receberam a classe existente `.btn-salvar`. Foram preservados títulos, textos de contexto, grids, valores, nomes e IDs dos campos, CSRF, método e ação POST, URLs e classe `.form-modal-crud`. Não foi criado outro padrão de cor, erro ou foco.

Nenhuma regra de negócio foi alterada. A situação da Turma continua somente informativa na edição, sem campo para modificá-la. Os campos `ativo` e `data_fim` da Oferta continuam fora desse formulário, seguindo o fluxo próprio de encerramento. A filtragem de módulos ativos e as validações existentes não foram modificadas.

### 11.3 — Arquivos deste lote

- `cadastros/templates/cadastros/_form_ata_fragment.html`.
- `cadastros/templates/cadastros/_form_oferta_modulo_fragment.html`.
- `cadastros/templates/cadastros/_form_turma_fragment.html`.
- Este diário.

Não foram alterados forms, views, models, rotas, CSS, JavaScript, migrations, autenticação ou permissões neste lote. Os ajustes de CSS registrados nas seções anteriores permanecem como alterações da primeira etapa de hoje.

### 11.4 — Verificação

| Verificação | Resultado |
|---|---|
| `manage.py check` | Sem problemas identificados |
| Suíte Django existente | **52 passed in 3.04s** |
| Renderização inicial/com erros, criação/edição, página/fragmento | **24 cenários aprovados**, oito por formulário |
| Revisão e `git diff --check` dos três fragmentos | Sem erros |

A verificação em memória utilizou os forms reais, `RequestFactory`, `render_to_string` e `HTMLParser`, sem salvar registros. Para renderizar o dropdown de Módulo sem depender dos dados locais, suas opções foram fornecidas somente nas instâncias usadas pelo script de conferência; o queryset e o código de produção não foram alterados.

Foram conferidos IDs únicos, labels com destino válido, referências de `aria-describedby`, `aria-invalid`, ordem e nomes dos controles, obrigatoriedade coerente com o form, erros gerais, links resumidos para campos inválidos, CSRF, ação POST e classe do modal. Também foram conferidos o texto de ajuda e a opcionalidade do número da Ata, as três legendas e a ausência dos campos de situação/encerramento que não pertencem a esses formulários.

Essas renderizações não exercitam salvamento real de Atas/Ofertas/Turmas nem substituem testes de teclado e leitor de tela no navegador. Os testes JavaScript não foram repetidos neste lote, pois nenhum script ou contrato de evento foi alterado.

### 11.5 — Validação manual pendente

1. Abrir criação e edição de Ata, Oferta de Módulo e Turma, conferindo o visual e os campos obrigatórios/opcionais.
2. Na Ata, conferir a ajuda de número e o fluxo habitual com número em branco, sem alterar a regra de geração automática.
3. Provocar um erro do servidor, como uma sigla já utilizada na mesma Oferta ao editar/criar Turma, e conferir resumo, link para o campo e mensagem junto ao controle.
4. Percorrer campos e botões com Tab/Shift+Tab; conferir abertura, fechamento e retorno de foco no modal, além da entrada no primeiro campo em página completa.
5. Conferir os anúncios e associações com leitor de tela e zoom de 200%.

Após aprovação, ampliar os componentes aos formulários restantes em outro lote delimitado, mantendo a separação entre melhorias de acessibilidade e regras acadêmicas.

---

## 12. Formulários de vínculo — Ata/Pessoa, Submódulo/Disciplina e Módulo/Submódulo

### 12.1 — Escopo autorizado e implementação

O responsável autorizou o próximo passo. Foram escolhidos três formulários pequenos de associação, que compartilham a renderização entre página completa e modal. Os fragmentos passaram a usar `campo_formulario.html`, `resumo_erros_formulario.html` e a classe de botão `.btn-salvar` aprovada.

| Fragmento | Campos preservados |
|---|---|
| `_form_ata_pessoa_fragment.html` | pessoa |
| `_form_submodulo_disciplina_fragment.html` | disciplina, ordem |
| `_form_modulo_submodulo_fragment.html` | submódulo, ordem |

Foram mantidos os títulos, o contexto da entidade de origem, nomes e IDs dos campos, ordem, CSRF, ação POST com `?parcial=1`, classe `.form-modal-crud` e texto “Vincular”. Os erros gerais permanecem visíveis no resumo; os erros dos campos usam um link resumido e mensagem completa junto ao controle, sem duplicação no link.

Arquivos alterados neste lote: os três fragmentos acima e este diário. Não foram alterados filtros de opções, critérios de vínculo, validações, forms, views, models, URLs, CSS, JavaScript, autenticação ou permissões.

### 12.2 — Falha preexistente descoberta em Ata/Pessoa

Ao instanciar o form real para a conferência de renderização, `AtaPessoaModelForm.__init__()` falhou com:

```text
django.core.exceptions.FieldError:
Unsupported lookup 'ativo' for ManyToOneRel or join on the field not permitted.
```

O filtro de pessoas em `cadastros/forms.py` usa `atribuicoes__ativo=True`. O model relacionado `AtribuicaoFuncao` possui `situacao`, e não o campo `ativo`. Esse filtro já consta em `HEAD` e `cadastros/forms.py` não tem alterações locais neste lote, confirmando que a falha antecede as mudanças de template.

O problema impede montar o formulário de vínculo de pessoa à Ata antes de renderizar a página ou o popup. A suíte existente de 52 testes continua passando, mas não cobre esse fluxo suficientemente para detectar essa falha.

Conforme a orientação de verificação de não corrigir automaticamente código fora do escopo, o filtro foi preservado e a falha registrada separadamente. A correção funcional deve preservar a regra de apresentar discentes com atribuição ativa, sem ampliar indevidamente a elegibilidade. Ela é recomendada antes de dar esse fluxo como validado.

### 12.3 — Verificação dos templates e limites

| Verificação | Resultado |
|---|---|
| `manage.py check` | Sem problemas identificados |
| Suíte Django existente | **52 passed in 2.99s** |
| Submódulo/Disciplina — página/fragmento, inicial/com erros | Quatro renderizações aprovadas |
| Módulo/Submódulo — página/fragmento, inicial/com erros | Quatro renderizações aprovadas |
| Ata/Pessoa — montagem normal | Falha preexistente de lookup, descrita acima |
| Ata/Pessoa — template com o filtro isolado somente em memória | Quatro renderizações aprovadas; não valida o fluxo real |
| Revisão e `git diff --check` dos três fragmentos | Sem erros |

O script pontual utilizou os forms reais, `RequestFactory`, `render_to_string` e `HTMLParser`, sem salvar dados. Para verificar apenas o template de Ata/Pessoa apesar do problema anterior, `unittest.mock.patch` substituiu temporariamente, dentro do processo do script, o retorno do filtro por um queryset vazio. As opções de seleção usadas na renderização foram sintéticas. Nenhum patch foi aplicado ao código de produção ou ao banco.

Nos doze cenários de template foram conferidos IDs únicos, labels associados, referências de `aria-describedby`, `aria-invalid`, obrigatoriedade, erros gerais, links por campo, nomes e ordem dos controles, CSRF, ação POST, classe do modal e botão padronizado. Os oito cenários dos dois vínculos curriculares não precisaram desse isolamento do filtro de Pessoa.

As opções sintéticas e a renderização em memória não exercitam a seleção real de candidatos, validações de duplicidade ou salvamento de vínculos. Não foram repetidos testes JavaScript porque nenhum script foi alterado.

### 12.4 — Próximo passo e validação manual

Priorizar a correção separada do filtro de Ata/Pessoa, com teste de regressão para a abertura e elegibilidade das opções. Depois, validar esse formulário no navegador.

Nos vínculos curriculares, abrir “Vincular Disciplina” e “Vincular Submódulo”, conferir indicação de obrigatoriedade, primeiro foco, Tab/Shift+Tab, mensagens ao tentar um vínculo ou uma ordem já utilizados, fechamento/retorno ao gatilho e zoom de 200%. Os critérios de duplicidade já existentes permanecem inalterados.

Este lote de templates está implementado e verificado com os limites acima; o fluxo real de Ata/Pessoa não deve ser anunciado como funcionando antes da correção preexistente e validação correspondente.

---

## 13. Correção do filtro de Pessoa/Ata e testes de regressão

### 13.1 — Solicitação e correção

Após o registro da falha anterior, o responsável autorizou seguir ao próximo passo e perguntou se o trabalho já estava concluído. Foi priorizada a correção funcional que impedia montar o formulário de vínculo Pessoa/Ata.

`AtaPessoaModelForm` passou de `atribuicoes__ativo=True` para `atribuicoes__situacao=SituacaoAtribuicao.ATIVO`, reutilizando o enum existente. O critério continua exigindo dados de Discente e situação ativa na mesma atribuição. Foram preservados o filtro conjunto, `distinct()`, a ordenação por nome e a rejeição de vínculo duplicado.

Não foi criada uma nova regra de elegibilidade: a consulta foi ajustada ao campo atual do model. Autenticação, permissões, models, migrations, views, URLs e fluxos acadêmicos não foram modificados.

### 13.2 — Testes com dados reais em banco isolado

Foi criado `cadastros/tests/test_views_ata_pessoa.py`, com quinze cenários de regressão. Diferentemente do isolamento de renderização descrito na seção 12, esses testes instanciam o form real sem substituir o filtro e exercitam as views com banco de testes do Django.

Os cenários verificam:

- Opções restritas a pessoa com atribuição discente ativa.
- Abertura da página completa e do fragmento de modal sem `FieldError`.
- Salvamento de vínculo válido e resposta JSON/redirect conforme o modo.
- Rejeição de discente inativo, docente sem dados de Discente e pessoa sem atribuição.
- Rejeição de pessoa com vínculo discente inativo e outra atribuição ativa, evitando misturar condições de relações diferentes.
- Erro no campo ao repetir um vínculo, mantendo somente o registro original.

As operações de gravação ocorreram somente no banco de testes, sem alterar cadastros reais.

### 13.3 — Resultados e arquivos

| Verificação | Resultado |
|---|---|
| Suíte Django completa | **67 passed in 3.39s** — 52 anteriores e 15 novos |
| `manage.py check` | Sem problemas identificados |
| Revisão do diff e `git diff --check` | Sem erros |

Arquivos alterados neste passo: `cadastros/forms.py`, `cadastros/tests/test_views_ata_pessoa.py` (novo) e este diário. Nenhum template, CSS ou JavaScript foi alterado nesta correção; os componentes do lote anterior foram preservados. Não houve repetição dos testes JS porque não há mudança nesses scripts.

**A falha preexistente da seção 12 está corrigida e coberta por testes de abertura e salvamento.** A confirmação manual no navegador continua necessária: abrir “Vincular Pessoa” em uma Ata, conferir as opções e testar um vínculo válido/duplicado, além de teclado, foco e zoom.

### 13.4 — O que falta para o fechamento

A revisão de acessibilidade ainda não está encerrada. Após confirmar este fluxo, resta continuar a adoção dos componentes nos formulários restantes (como registros complementares de Pessoa, edição de Pessoa e ações de encerramento/confirmação) e executar a validação final dos fluxos principais com teclado, leitor de tela e zoom de 200%.

Problemas visuais específicos de tabelas largas ou estilos inline devem ser tratados quando identificados, sem reescrever telas já aprovadas. A aprovação automatizada não deve ser apresentada como certificação de conformidade WCAG global.

---

## 14. Padronização dos registros complementares de Pessoa

### 14.1 — Escopo e implementação

Com autorização para continuar, foi aplicado o padrão aprovado de acessibilidade aos formulários de Formação, Experiência Profissional, Histórico de Vínculo Formal e Pendências de Cadastro. Foram reutilizados `campo_formulario.html` e `resumo_erros_formulario.html`, mantendo a apresentação de erros existente e os links do resumo identificados pelo nome do campo.

Os campos passaram a apresentar obrigatoriedade conforme o form real, ajuda e erros associados ao controle. Os agrupamentos receberam legendas visualmente ocultas e os botões de envio passaram a utilizar `btn-salvar`, com as variáveis de cor e o foco já aprovados. Não foram criados estilos ou scripts novos.

No Histórico de Vínculo, foi corrigido o fechamento ausente do fieldset externo no modo de inclusão. Foram preservados os campos distintos de inclusão e encerramento, inclusive a obrigatoriedade definida atualmente nos forms. Na edição de Pendência, o checkbox “Resolvida” mantém seu label nativo; foi retirada a instrução dependente de mouse e sua marcação `<i>` incorreta. O checkbox continua disponível somente na edição.

### 14.2 — Falha preexistente encontrada na página de Formação

A página completa de Formação referenciava `preencher-requisitos-docente` no botão “Voltar”. Esse nome não existe nas URLs atuais e provocava `NoReverseMatch` na renderização completa, embora o fragmento de popup não contenha esse link.

Como a navegação pertence ao formulário deste lote, o link foi corrigido para `detalhe-pessoa`, usando `dados_docente.atribuicao.pessoa_id`. Esse é o mesmo destino já adotado pelo `get_success_url()` das views de inclusão e edição de Formação. Não houve mudança nas views, validações ou dados.

### 14.3 — Arquivos alterados neste lote

- `cadastros/templates/cadastros/_form_formacao_fragment.html`.
- `cadastros/templates/cadastros/_form_experiencia_fragment.html`.
- `cadastros/templates/cadastros/_form_historico_vinculo_fragment.html`.
- `cadastros/templates/cadastros/_form_pendencia_fragment.html`.
- `cadastros/templates/cadastros/form_formacao.html` — correção do link de retorno.
- Este diário.

### 14.4 — Verificações e resultados

| Verificação | Resultado |
|---|---|
| `python manage.py check` com o Python do ambiente virtual | Sem problemas identificados |
| `python -m pytest -p no:cacheprovider -q --tb=short` | **67 passed in 3.58s** |
| Renderização dos quatro fluxos | **32 cenários aprovados** |
| Revisão do diff e `git diff --check` | Sem erros |

O script pontual utilizou os forms reais, `RequestFactory`, `render_to_string` e `HTMLParser`, sem gravar no banco. Foram cobertos os modos de inclusão/edição de Formação, Experiência e Pendência, e inclusão/encerramento de Vínculo; cada modo foi renderizado como página e fragmento, inicialmente e com erros.

Foram conferidos nomes e ordem dos controles, IDs únicos, labels, referências de `aria-describedby`, `aria-invalid`, obrigatoriedade conforme o form, erros gerais e links por campo, CSRF, ação POST, classe do modal, botão padronizado, fechamento dos fieldsets e destino do link de retorno das páginas. As opções de Vínculo foram sintéticas apenas no processo do script, sem alterar o queryset de produção. Essa verificação não substitui o teste de elegibilidade ou salvamento real. Os testes JavaScript não foram repetidos porque nenhum script foi alterado neste lote.

### 14.5 — Validação manual e continuidade

Ainda é necessário abrir os quatro fluxos no navegador e conferir Tab/Shift+Tab, Enter/Espaço conforme o controle, primeiro foco, apresentação e leitura dos erros, fechamento e retorno do popup, e zoom de 200%. Na Pendência, conferir também o checkbox “Resolvida” por teclado; no Vínculo, testar os dois modos; na Formação, conferir a página completa e o link “Voltar”. Não houve confirmação manual deste lote até este registro.

Autenticação, permissões, regras de contratação, cadastro de Pessoa e encerramento de vínculos não foram alterados. Nenhum model, migration, view, serviço ou JavaScript mudou neste lote. A revisão global ainda requer os formulários restantes e validação manual final, sem declaração de conformidade WCAG integral.

### 14.6 — Retorno do responsável após a entrega

O responsável confirmou: “Ok - está tudo funcionando”. A confirmação registra o funcionamento do lote de Formação, Experiência, Histórico de Vínculo e Pendências após a entrega. O relato não detalha os controles, tecnologias assistivas ou níveis de zoom utilizados; portanto, não equivale à comprovação individual de todos os itens da seção 14.5 nem à conclusão da auditoria global.

Alteração desta atualização restrita ao diário. Nenhum código foi modificado e não houve necessidade de repetir a suíte de testes.

---

## 15. Edição de Pessoa e requisitos de contratação

### 15.1 — Solicitação e alterações

Após confirmar o funcionamento do lote anterior, o responsável autorizou o próximo lote: edição de Pessoa e requisitos de contratação. Foram utilizadas as skills `django-accessibility` e `code-change-verification`.

Em `_form_pessoa_editar_fragment.html`, os 33 blocos repetidos de campos foram substituídos pelo include `campo_formulario.html`. Foram adicionados o resumo de erros aprovado e a classe `btn-salvar`. Permanecem os quatro grupos e sua ordem visual, os títulos, o CPF apenas informativo e não editável, a identificação da Pessoa e as classes utilizadas pelo modal.

Em `_form_requisito_contratacao_fragment.html`, os dois campos passaram a utilizar o mesmo include, com resumo de erros, botão padronizado e legenda visualmente oculta para o agrupamento externo. O campo de opções utiliza o fieldset/legend nativo previsto no componente compartilhado, associando a ajuda e o erro ao grupo; as opções individuais continuam com labels e estado inválido fornecidos pelo Django.

Não houve alteração dos forms, views, models, serviços, URLs, scripts, CSS, obrigatoriedade, opções de contratação, permissões ou regras de negócio. As páginas completas continuam herdando `base.html` e incluindo os mesmos fragmentos. A consulta de CEP/CPF e o comportamento de foco compartilhado não foram modificados.

### 15.2 — Arquivos deste lote

- `cadastros/templates/cadastros/_form_pessoa_editar_fragment.html`.
- `cadastros/templates/cadastros/_form_requisito_contratacao_fragment.html`.
- Este diário.

### 15.3 — Verificações executadas

| Verificação | Resultado |
|---|---|
| `python manage.py check` pelo ambiente virtual | Sem problemas identificados |
| `python -m pytest -p no:cacheprovider -q --tb=short` | **67 passed in 3.26s** |
| Renderizações dos dois formulários reais | **12 cenários aprovados** |
| Revisão do diff e `git diff --check` | Sem erros |

O script pontual renderizou os dois fluxos como página completa e fragmento, em estado inicial, com erros de campos e com erro geral. Foram comparados os controles com a renderização dos templates em `HEAD`, confirmando preservação de nomes, IDs, ordem, tipos, valores, seleção, obrigatoriedade e limites de datas. Também foram conferidos IDs únicos, labels, legendas, referências de ajuda/erro, `aria-invalid`, CSRF, ação do formulário, classes do modal e botão padronizado. Não houve gravação no banco.

Uma asserção inicial do script pressupunha que todo campo produziria link no resumo. A inspeção confirmou que o Django não fornece `id_for_label` para o grupo RadioSelect; por isso, o resumo compartilhado existente apresenta o nome desse grupo como texto, enquanto os demais campos utilizam links. O script foi corrigido para conferir esse contrato, sem mudar o componente global. O erro detalhado do grupo permanece associado pelo fieldset e as opções recebem `aria-invalid`. Não foram repetidos os testes JavaScript porque os scripts não mudaram.

### 15.4 — Conferência manual pendente

Abrir “Editar Pessoa” no popup e como página completa, conferir o foco inicial, percorrer os quatro grupos com Tab/Shift+Tab, provocar um erro de campo e conferir o resumo, a mensagem próxima ao campo e a manutenção dos dados. Testar salvamento, fechamento e retorno do foco, além de zoom de 200%.

Em Requisitos de Contratação, conferir o anúncio da legenda e ajuda pelo leitor de tela, navegação no grupo com as setas, seleção por Espaço, passagem para o documento comprobatório e salvamento/fechamento. O lote está implementado e verificado automaticamente, ainda sem confirmação manual específica do responsável. Não representa conclusão da auditoria global de acessibilidade.

---

## 16. Retorno do foco em Filtrar e Limpar na lista de Pessoas

### 16.1 — Problema relatado e correção

O responsável relatou que, ao acionar “Filtrar” ou “Limpar” na lista de Pessoas, o foco retornava ao início da página. Solicitou que o foco permanecesse no controle acionado após a navegação.

A lista utiliza um formulário GET para filtrar e um link para limpar os parâmetros. Foi criado o comportamento compartilhado `foco-filtros.js`, com adesão explícita por `data-restaurar-foco-filtros` no formulário e `data-foco-filtro` nos controles. Os dois controles da lista receberam IDs estáveis. O script guarda somente o caminho de destino e o ID do controle no `sessionStorage` e consome o marcador na próxima página, restaurando o foco se o caminho e o controle forem compatíveis e o elemento estiver disponível.

O submit nativo usa `SubmitEvent.submitter`; se não houver submitter no envio implícito por Enter, utiliza o botão de envio marcado. O link continua sendo navegação nativa. Não há captura de teclas, alteração de consultas, prevenção do envio ou requisição adicional. O marcador não contém nomes, filtros ou dados das pessoas. Cliques modificados, navegação para outra aba e eventos cancelados não geram retorno. Falha de armazenamento não impede a filtragem.

O script foi incluído em `base.html` para consumir o marcador mesmo ao chegar a outro caminho, evitando um retorno posterior indevido. Somente o formulário de Pessoas aderiu ao comportamento neste lote. Os scripts existentes de sidebar, formulários e modais foram preservados.

### 16.2 — Arquivos alterados neste passo

- `cadastros/templates/cadastros/lista.html` — marcadores e IDs dos controles.
- `static/global/js/foco-filtros.js` — novo comportamento reutilizável.
- `templates/base.html` — inclusão do script com versão de cache.
- `cadastros/tests/js/foco-filtros.test.cjs` — seis testes de regressão.
- Este diário.

### 16.3 — Verificação

| Verificação | Resultado |
|---|---|
| `node --test cadastros/tests/js/*.test.cjs` | **36 testes aprovados**, incluindo os seis novos |
| `python manage.py check` pelo ambiente virtual | Sem problemas identificados |
| `python -m pytest -p no:cacheprovider -q --tb=short` | **67 passed in 3.23s** |
| Renderização da lista com e sem resultados | Dois cenários aprovados |
| Revisão do diff e `git diff --check` | Sem erros |

Os testes JavaScript usam DOM simulado e verificam retorno a Filtrar, retorno a Limpar, envio implícito sem submitter, consumo único do marcador, isolamento de outras páginas e formulários, cliques modificados e falhas de armazenamento. A renderização verificou os campos GET originais, marcadores, IDs e inclusão do script sem gravar dados. O cenário sem resultados no teste de foco simula a URL de busca; a presença dos controles nesse estado foi conferida separadamente pela renderização Django. Esses testes não equivalem à navegação em navegador real.

### 16.4 — Conferência manual pendente

Na lista de Pessoas, chegar a “Filtrar” com Tab e pressionar Enter ou Espaço; após a resposta, confirmar o foco no mesmo botão e a continuidade com Tab/Shift+Tab. Repetir com uma busca sem resultados. Depois acionar “Limpar” com Enter e conferir o foco no próprio link, inclusive quando não houver filtros preenchidos. Como link nativo, “Limpar” é acionado por Enter; Espaço mantém o comportamento padrão de rolagem.

Regras de negócio, permissões, parâmetros de busca, views e filtros do banco permaneceram intactos. Ainda não houve confirmação manual específica desta correção.

---

## 17. Auditoria final de acessibilidade — diagnóstico e pendências de fechamento

### 17.1 — Solicitação, escopo e conclusão

O responsável solicitou a auditoria final para verificar se a etapa de acessibilidade poderia ser encerrada. Foram relidos `AGENTS.md`, `django-accessibility` e `code-change-verification`. A auditoria foi realizada sobre a árvore de trabalho atual, incluindo os lotes ainda não commitados, com referência ao commit `543c5bc` para distinguir problemas anteriores.

**Resultado: a auditoria está concluída, mas a implementação global ainda não pode ser considerada encerrada.** Foram confirmadas duas falhas preexistentes de compilação de templates e pendências de erros, labels e consistência em telas específicas. Os testes existentes passam, mas não cobrem todos esses caminhos.

Nesta etapa foi alterado somente este diário. Nenhum código foi corrigido durante a auditoria, nenhum registro de produção foi gravado e nenhuma regra de negócio ou permissão foi modificada. Não houve teste em navegador real, leitor de tela ou zoom nesta execução; as confirmações anteriores do responsável permanecem registradas nos lotes correspondentes e não foram ampliadas para outras telas.

### 17.2 — Estrutura e cobertura inspecionadas

Foram inventariados e compilados os **88 templates locais** de `templates`, `cadastros/templates`, `atribuicao/templates` e `nucleo/templates`. Foram localizados os formulários, a herança de `base.html`, os includes, os fragmentos de modais, as tabelas e os scripts/estilos compartilhados.

| Área | Evidência encontrada | Limite da conclusão |
|---|---|---|
| Estrutura global | `base.html` possui idioma português, viewport, header, nav nomeado, main identificado e link de salto | Ordem de leitura e comportamento visual requerem navegador |
| Menu lateral | Botões nativos, `aria-expanded`, submenus identificados, estado atual e foco de entrada no conteúdo | Fluxos completos e leitor de tela ainda precisam de confirmação final |
| Formulários já migrados | Includes de campo, ajuda, erro e resumo; sem duplicar mensagens completas nos links | Não se aplica automaticamente ao cadastro inicial nem aos fragmentos antigos |
| Modal compartilhado | Diálogo nomeado, fechamento por teclado, contenção de Tab, fundo inativo e retorno do foco | Depende do contrato de classe/HTML de cada fragmento |
| JavaScript dinâmico | Feedback de CEP/CPF, avisos de formset e foco cobertos por testes com DOM simulado | Não equivale a teste de navegador/tecnologia assistiva |
| Tabelas | **36 tabelas em 23 templates**; contagem de captions corresponde à de tabelas; nenhum `th` sem `scope` ou `id` na varredura | É inspeção estática, sem nova validação de cada estado de dados, associação dinâmica ou rolagem |
| Foco dos filtros | Lista de Pessoas aderiu ao retorno de foco de Filtrar/Limpar; testes específicos passam | A confirmação manual solicitada na seção 16 continua pendente |

A compilação aprovou **86 templates e encontrou falha em dois**. Templates de página que incluem os fragmentos problemáticos podem compilar isoladamente e falhar apenas quando renderizados; essa diferença foi verificada nos achados abaixo.

### 17.3 — Achados confirmados e prioridades

#### A1 — Alta: Matrícula e Finalizar Planejamento não renderizam

Arquivos:

- `atribuicao/templates/atribuicao/_form_matricula_fragment.html`, especialmente a herança inserida na linha 24 e o fechamento na linha 36.
- `atribuicao/templates/atribuicao/_form_finalizar_planejamento_fragment.html`, especialmente a herança inserida na linha 25 e o fechamento na linha 34.

Os fragmentos misturam um condicional de modo parcial com `{% extends %}` e blocos de página completa. O compilador Django lança `TemplateSyntaxError: Invalid block tag ... 'endif'`. A falha foi reproduzida nos dois fragmentos e nas duas páginas que os incluem: **quatro renderizações falharam**, independentemente de dados do banco. Os mesmos dois arquivos extraídos de `HEAD` também falharam ao compilar, comprovando que o problema é anterior aos lotes atuais.

Há ainda um segundo problema de integração no código desses fragmentos: seus formulários parciais não possuem a classe `form-modal-crud`, exigida pelo listener de envio em `modal-crud.js`. Essa incompatibilidade é observável no código, mas o efeito no navegador fica encoberto pela falha de compilação. Os scripts de fechamento inline são redundantes com a delegação já existente e não devem ser usados como garantia de execução após `innerHTML`.

Correção proposta: manter a herança exclusivamente nas páginas completas, deixar os fragmentos somente com seu conteúdo, restaurar o contrato de classe do modal e reutilizar componentes de campos/erros e botões. Preservar CSRF, URLs, nomes dos campos, opções, serviços e regras de matrícula/abertura. Acrescentar testes de renderização de página/fragmento e de integração do envio antes de considerar esses fluxos concluídos.

#### A2 — Alta: erros e múltiplas linhas no cadastro inicial de Pessoa

Arquivo: `cadastros/templates/cadastros/form_pessoa.html`, especialmente linha 25 e blocos de formsets a partir das linhas 173, 207, 239 e 288.

O cadastro inicial ainda usa marcação própria. Não apresenta o resumo compartilhado dos erros de campos; os formsets renderizam apenas o índice `.0` e não exibem os erros individuais ou `non_form_errors` nesse template.

Foi renderizado o template com os forms/formsets reais, querysets vazios apenas no processo do script e duas linhas de Formação contendo ano inválido. As duas linhas tiveram erro real de validação. A resposta HTML apresentou `aria-describedby="id_formacao-0-ano_conclusao_error"` sem o elemento correspondente e não apresentou o campo `id_formacao-1-ano_conclusao`. Isso confirma ausência de mensagem associada e ausência da segunda linha na resposta renderizada, sem afirmar que os dados tenham sido apagados do banco. O texto de ajuda de `situacao` também é referenciado por `aria-describedby` mas não existe no HTML inicial nem no inválido.

Correção proposta: tratar esse cadastro como lote próprio; apresentar todos os erros e reconstituir todas as linhas enviadas na resposta inválida, preservando prefixos, IDs, TOTAL_FORMS, categorias, API de CEP/CPF e o comportamento de inclusão. Testar especialmente falha no segundo registro, manutenção dos valores e foco no erro visível. Não basta substituir includes mecanicamente, pois o JavaScript atual clona e renomeia os controles.

#### A3 — Alta: 13 controles sem label associado em quatro telas com rotas

| Template em `atribuicao/templates/atribuicao/` | Controles confirmados | Referências |
|---|---|---|
| `atribuicao.html` | Instrutor, Disciplina e Turma | Linhas 14, 21 e 28 |
| `horarios.html` | Atribuição, Dia da Semana, Início e Fim | Linhas 14, 21, 28 e 32 |
| `registro_instrucao.html` | Data, Carga Horária, Tipo e Conteúdo | Linhas 18, 23, 28 e 37 |
| `contratos.html` | Pesquisa e Status | Linhas 39 e 42 |

Os labels visuais das três primeiras telas não possuem `for` e não envolvem os controles; os controles tampouco possuem IDs ou nomes acessíveis alternativos. Em Contratos, placeholder e opções não substituem um label. Essas telas constam das views e URLs de Atribuição; não foram descartadas como arquivos sem uso.

Correção proposta: associar labels e IDs, preservando os `name`, métodos, opções e processamento. Ajustar o formulário GET de Contratos ao componente de retorno do foco se esse comportamento for requerido ali também. Conferir os títulos das páginas de Atribuição/Horários/Registro, que começam com `h4` sob o `h1` global.

#### A4 — Média: encerramentos, status e confirmações ainda fora do padrão aprovado

Permanecem com marcação própria de campos e/ou mensagens:

- `cadastros/templates/cadastros/_form_encerrar_oferta_modulo_fragment.html`.
- `atribuicao/templates/atribuicao/_form_encerrar_turma_fragment.html`.
- `atribuicao/templates/atribuicao/_form_status_matricula_fragment.html`.
- `atribuicao/templates/atribuicao/_form_revisar_aprovacao_fragment.html`.

Em Status, textos de ajuda são exibidos em `<small>` sem os IDs esperados por `aria-describedby`. No encerramento de Oferta, o template não apresenta `non_field_errors`; isso é lacuna de apresentação caso o form produza erro geral, não um teste de que tal erro é necessariamente produzido em todos os envios. Revisar Aprovação utiliza nomes de alunos como labels dos checkboxes; essa associação deve ser preservada ao padronizar.

Há também botões de envio sem `btn-salvar` em Módulo/Submódulo e nos quatro fragmentos de ativar/inativar. O estilo genérico global já lhes fornece fundo institucional e foco; a ausência da classe é diferença de padronização, não prova isolada de falha WCAG. A confirmação de exclusão ainda tem cores inline e fieldset sem legenda. Recomenda-se um lote pequeno de componentes e mensagens, sem modificar regras de encerramento, aprovação, relocação, exclusão ou reativação.

#### A5 — Média/baixa: contraste residual, responsividade e resumo de opções

Os textos de diagnóstico com caminhos de templates usam `#999` em fonte pequena: contraste calculado de **2,85:1 no branco** e **2,65:1 no fundo `#f4f7fa`**. Exemplo: `cadastros/templates/cadastros/detalhe.html:641`. Convém retirar esses diagnósticos da interface de uso ou aplicar a variável de texto secundário, mantendo informações de implementação fora dos fluxos do usuário.

As cores aprovadas continuam adequadas nas combinações calculadas: erro `#a94442`/`#f2dede` **4,53:1**; Salvar branco/`#002060` **15,27:1**; Cancelar `#f7f7f7`/`#b50a04` **6,51:1**. Esses cálculos não validam todos os estados de interação nem todos os estilos inline. Persistem cores/bordas inline fora das variáveis e layouts com larguras mínimas, como o campo Nome da lista e a composição lateral de Registro de Instrução. Overflow, corte do anel de foco, rolagem das tabelas e modais a 200% permanecem itens de teste visual, sem classificação automática como falhas confirmadas.

O resumo compartilhado usa texto simples para RadioSelect quando `campo.id_for_label` é vazio, conforme registrado na seção 15. Isso não torna o grupo sem nome — há legend e labels individuais —, mas ainda difere da exigência interna de link por campo inválido. Uma melhoria compartilhada deve apontar para uma opção focável do grupo e ser verificada nos modos normal/modal; não se deve criar um link para um elemento que não receba foco.

### 17.4 — Exclusões e limites de escopo

A varredura encontrou também dois controles de login sem associação explícita e cinco em `nucleo/templates/nucleo/registro_instrucao.html`. Login/autenticação permanece fora do escopo por instrução do projeto. O template de Registro em Núcleo não foi encontrado como destino das views/URLs inspecionadas; o Registro roteado usa o template de Atribuição e já está em A3. Esses achados não autorizam implementar autenticação nem duplicar correções em uma tela sem uso confirmado.

Não houve auditoria do Django Admin, aplicação de tema escuro, teste automatizado de acessibilidade com biblioteca nova, teste de todas as URLs/estados de banco ou medição de comportamento com leitor de tela. O diário distingue falha confirmada de hipótese que exige navegador. A autorização de auditoria não foi tratada como confirmação manual de Filtrar/Limpar ou do lote de edição de Pessoa/Requisitos.

### 17.5 — Verificações desta auditoria

| Verificação | Resultado |
|---|---|
| Compilação dos 88 templates locais | **86 aprovados; 2 falhas preexistentes confirmadas** |
| Renderização dos fluxos de Matrícula/Planejamento | **4 falhas**, explicadas em A1 |
| Compilação dos dois fragmentos extraídos de `HEAD` | Mesmas falhas, anteriores às alterações atuais |
| Novo Cadastro inicial e com formset inválido de duas linhas | Achados de apresentação confirmados em A2 |
| Inventário estático de tabelas | 36 tabelas/23 arquivos; captions e cabeçalhos identificados |
| `python manage.py check` pelo ambiente virtual | Sem problemas identificados |
| `python -m pytest -p no:cacheprovider -q --tb=short` | **67 passed in 3.40s** |
| `node --test --test-reporter=dot cadastros/tests/js/*.test.cjs` | **36 testes aprovados** |
| Revisão do diff e `git diff --check` | Sem erros de whitespace |

As verificações de templates/formsets foram scripts pontuais em memória, sem arquivos de teste novos ou gravação no banco. Os testes Django utilizam o banco isolado de testes. A compilação global demonstrou uma lacuna da suíte: o check Django e os 67 testes não certificam a renderização de todos os templates. Na descoberta de arquivos, `.pytest_cache` continuou com acesso negado, já conhecido; a auditoria usou somente as pastas explícitas de templates e o pytest foi executado sem o cacheprovider. Essa restrição não explica as duas falhas de sintaxe.

### 17.6 — Ordem proposta para fechar a implementação

1. **Matrícula e Planejamento:** corrigir os dois fragmentos e sua integração com o modal; testar páginas/fragmentos e respostas inválidas, sem tocar nos serviços acadêmicos.
2. **Cadastro inicial de Pessoa:** erros de todos os formsets, manutenção das linhas e dados após falha, ajuda e resumo; preservar APIs e gerenciamento dinâmico.
3. **Labels e ações restantes:** primeiro os 13 controles de Atribuição, Horários, Registro e Contratos; depois um lote de encerramentos/status e outro de confirmações/botões, reutilizando os componentes aprovados.
4. **Acabamento compartilhado:** resumo navegável para opções, diagnósticos de baixo contraste e estilos inline relevantes, com revisão de impacto nas telas já aprovadas.
5. **Aceite manual final:** percorrer os fluxos abaixo, registrar resultados e eventuais exceções. Só então declarar a etapa interna concluída, sem apresentar isso como certificação de conformidade WCAG integral.

| Fluxo de aceite | Conferências mínimas |
|---|---|
| Base/menu | Primeiro Tab, salto, abertura do submenu, entrada no conteúdo e foco visível |
| Pessoas/lista | Filtrar/Limpar com e sem resultados; retorno e continuação com Tab/Shift+Tab |
| Pessoa/cadastro | Consulta CEP/CPF, troca de categoria, duas linhas de formset, erro e preservação dos valores |
| Pessoa/edição e requisitos | Primeiro foco, labels/legenda, setas/Espaço nas opções, salvamento e retorno |
| Popups curriculares | Abrir, navegar, provocar erro, cancelar/Esc, salvar e retornar ao gatilho |
| Matrícula/Planejamento/encerramentos | Abertura normal/modal, erros legíveis e saídas por teclado; não efetivar ações irreversíveis em produção para testar |
| Atribuição/Horários/Registro/Contratos | Labels anunciados, foco, filtros e disposição dos controles |
| Todos os fluxos anteriores | Leitor de tela, zoom de 200%, legibilidade, rolagem e ausência de foco encoberto |

**Próximo lote recomendado: A1 — Matrícula e Finalizar Planejamento**, por serem falhas de abertura confirmadas, com correção limitada a templates/integração e cobertura de regressão.

---

## 18. Correção de Matrícula e Finalizar Planejamento — achado A1

### 18.1 — Autorização e implementação

Após receber o diagnóstico da auditoria final, o responsável autorizou o próximo passo. Foram corrigidos os dois fragmentos que falhavam na compilação, utilizando as skills `django-accessibility` e `code-change-verification`.

A herança de `base.html` e os blocos de página foram removidos dos fragmentos, permanecendo exclusivamente nas páginas completas já existentes. Foi removido também o caractere `<` solto no início do fragmento de Matrícula. Os títulos usam `h3` no popup e `h2` na página completa.

Os dois formulários agora possuem `form-modal-crud`, permitindo que o listener compartilhado intercepte seu envio no popup. As ações preservam os nomes das URLs de inclusão/edição/planejamento e recebem `?parcial=1` somente no modo parcial. Na página completa, o envio continua normal e recebe redirecionamento; no popup, recebe o JSON de sucesso previsto nas views.

Foram reutilizados os includes de campos e resumo de erros, com labels, ajuda, indicação de obrigatoriedade e erros associados. Os botões usam `btn-salvar` e `btn-cancelar`, sem novas cores ou estilos inline. Permanecem os IDs `modal-crud-cancelar-btn` e `modal-cancelar-planejamento`, tratados pela delegação de fechamento existente. Os scripts inline que apenas ocultavam o overlay foram removidos, para usar o fechamento completo com restauração do fundo/foco. Na página completa, Cancelar/Voltar são links nativos para Gerenciar Turma, evitando botões sem ação fora do popup.

O aviso sobre início da turma, congelamento da chamada e numeração alfabética foi preservado. Não foram alterados os forms, views, serviços, models, permissões, elegibilidade, geração da numeração ou transições acadêmicas.

### 18.2 — Arquivos alterados neste lote

- `atribuicao/templates/atribuicao/_form_matricula_fragment.html`.
- `atribuicao/templates/atribuicao/_form_finalizar_planejamento_fragment.html`.
- `cadastros/tests/test_views_matricula_planejamento.py` — novo, seguindo a organização existente da suíte pytest.
- Este diário.

As páginas `form_matricula.html` e `form_finalizar_planejamento.html`, o JavaScript e o CSS compartilhados não precisaram de mudanças.

### 18.3 — Cobertura de regressão e resultados

Foram acrescentados **18 testes**, combinando três fluxos (adicionar matrícula, editar matrícula e finalizar planejamento), dois modos (página/popup) e três situações (GET inicial, POST inválido e POST válido). Os testes usam views/forms/serviços reais e banco isolado, sem substituir o processamento por mocks.

Na abertura e na resposta inválida, foram verificados formulário único, modo POST, ação correta, CSRF, classe de integração do modal, nomes/ordem dos controles, IDs únicos, labels, referências de ajuda/erro, resumo, botão e controle de cancelamento correto para cada modo. O envio inválido preserva o código preenchido, não adiciona matrícula e mantém a turma Planejada. O POST válido é enviado para a `action` extraída do HTML, cobrindo a separação de JSON e redirecionamento.

No salvamento, a inclusão cria a matrícula e mantém o código ANAC; a edição atualiza o código sem criar matrícula adicional; o planejamento mantém o comportamento existente: avança a turma para Em Andamento, numera duas matrículas pela ordem alfabética e grava data/ata de início. Essas operações foram realizadas somente no banco de testes.

| Verificação | Resultado |
|---|---|
| Arquivo de regressão novo, executado isoladamente | **18 passed in 1.06s** |
| Suíte Django completa | **85 passed in 3.44s** — 67 anteriores + 18 novos |
| `python manage.py check` pelo ambiente virtual | Sem problemas identificados |
| Compilação de todos os templates locais | **88 aprovados, nenhuma falha de compilação** |
| `node --test --test-reporter=dot cadastros/tests/js/*.test.cjs` | **36 testes aprovados** |
| Revisão do diff e `git diff --check` | Sem erros |

**As duas falhas de compilação da seção 17/A1 estão resolvidas**, assim como a incompatibilidade da classe dos formulários parciais. Os testes JavaScript existentes continuam aprovados; sua execução usa DOM simulado e não representa teste no navegador da integração completa com esses endpoints.

### 18.4 — Validação manual e continuidade

Em uma turma de teste, abrir Adicionar Aluno, Editar Matrícula e Finalizar Planejamento. Conferir foco inicial, Tab/Shift+Tab, labels/ajuda, erro de campo, manutenção de dados e seleção, Cancelar/Voltar, Esc, fechamento e retorno ao gatilho. Testar também as páginas completas e zoom de 200%, com leitor de tela quando disponível. A efetivação da abertura deve ser testada somente em dados apropriados de teste, pois mantém seus efeitos acadêmicos existentes. Não houve validação em navegador real nesta execução.

O restante da auditoria continua pendente. **Próximo lote recomendado: A2 — cadastro inicial de Pessoa**, com apresentação dos erros e preservação de todas as linhas de formset após envio inválido, mantendo categorias, APIs e gerenciamento dinâmico.

---

## 19. Cadastro inicial de Pessoa — erros e recuperação dos formsets (A2)

### 19.1 — Solicitação e diagnóstico

O responsável autorizou o lote do cadastro inicial de Pessoa. Foram aplicadas as skills `django-accessibility` e `code-change-verification`, preservando regras e validações existentes.

O template apresentava apenas o índice `.0` de Formação, Experiência, Histórico de Vínculo e Pendências, apesar de o servidor devolver os formsets completos após erro. Além de omitir registros enviados, faltavam mensagens junto aos controles dos formsets e o elemento de ajuda referenciado por Situação. A correção trata a apresentação e a continuidade da navegação, sem alterar validações ou processamento dos dados.

### 19.2 — Implementação e comportamento

Os cinquenta campos principais passaram a reutilizar `campo_formulario.html`, incluindo obrigatoriedade conforme o form, labels nativos, ajuda e erros associados. Permanecem nomes, IDs, grids, agrupamentos e seletores. Os rótulos personalizados dos contatos/responsável passam a usar os labels definidos nos forms. Foram preservados os IDs das instruções e regiões de status de CEP/CPF, as consultas existentes e seus eventos. O botão Salvar utiliza a classe aprovada `btn-salvar`.

Foi criado um único resumo para o cadastro, no estilo aprovado `.erro`, com links identificados pelo nome do campo. Para formsets, o link acrescenta grupo e número do registro, por exemplo “Formação — Registro 2: Ano de conclusão”; a mensagem completa continua junto ao campo. Erros gerais do cadastro, de cada linha e dos formsets também são apresentados. O trecho de links foi extraído para um include reutilizado pelo resumo global, preservando seu contrato anterior, inclusive o comportamento já documentado para RadioSelect.

O include dos formsets renderiza todas as linhas recebidas, com legendas “Registro 1”, “Registro 2” etc., os quatro campos de gerenciamento de cada coleção e as mensagens pertinentes. A última linha conserva `.formset-template`, usada pelo botão Adicionar; as anteriores ficam visíveis e editáveis na resposta inválida. Não são criadas linhas extras no servidor nem recalculados seus índices. Na primeira abertura, permanece o comportamento de adicionar registros à tabela e manter os controles correspondentes no contêiner oculto.

Na resposta inválida, `data-recuperado` ativa o modo de correção: todas as linhas reaparecem como campos e as tabelas vazias deixam de ser exibidas. Ao adicionar mais um registro nesse estado, o JavaScript preserva a linha atual visível antes da próxima, mantém os valores/opções selecionados, avança o índice e o TOTAL_FORMS e focaliza o primeiro campo novo. Os erros antigos continuam no registro correspondente; a nova linha não herda `aria-invalid`, mensagens ou referências de erro do registro anterior. Labels, IDs e referências de ajuda acompanham o novo prefixo.

Os blocos com erros do servidor permanecem visíveis mesmo se pertencem a outra categoria, permitindo acessar e corrigir erros que o backend efetivamente devolveu. Os critérios de categoria e as validações não mudaram; quando não há erros, a exibição continua seguindo a função escolhida. O script compartilhado `foco-formularios.js` permanece responsável por priorizar o primeiro campo inválido disponível no retorno de POST normal; não foi criada outra rotina concorrente de foco.

Se o gerenciamento inválido não produzir nenhuma linha, o botão Adicionar desse bloco é desabilitado para evitar exceção JavaScript. O erro de gerenciamento continua visível; esse tratamento defensivo não inventa registros nem altera os dados aceitos pelo servidor.

### 19.3 — Arquivos alterados neste lote

- `cadastros/templates/cadastros/form_pessoa.html`.
- `cadastros/templates/cadastros/_campos_formset_cadastro.html` — novo.
- `cadastros/templates/cadastros/_resumo_erros_cadastro_pessoa.html` — novo.
- `cadastros/templates/cadastros/_itens_erros_formset.html` — novo.
- `templates/includes/itens_erros_formulario.html` — novo componente de links.
- `templates/includes/resumo_erros_formulario.html` — reutilização do componente de links.
- `cadastros/static/cadastros/js/form-dinamico.js` — recuperação e referências das linhas; versão do script atualizada na página.
- `cadastros/tests/js/form-dinamico.test.cjs`.
- `cadastros/tests/test_views_cadastro_acessibilidade.py` — novo.
- Este diário.

Nenhum form, view, serviço, model, migration, CSS ou script das consultas CEP/CPF foi alterado neste lote. A alteração anterior em `cadastros/forms.py`, ainda presente na árvore de trabalho, pertence à correção de Ata/Pessoa documentada na seção 13.

### 19.4 — Cobertura e resultados

Foram acrescentados seis testes Django de integração: abertura inicial com associações válidas; erros reais na segunda linha dos quatro formsets; retorno inválido seguido de correção/salvamento para Docente e Gestão; erro geral de vínculo obrigatório; e erro de gerenciamento ausente. Eles verificam IDs únicos, destinos dos links, labels, referências de ajuda/erro, quantidade/valores das linhas, seleções, resumo único e ausência de gravação quando inválido. Nos dois casos de correção, verificam duas formações ou duas experiências conforme a categoria, dois vínculos e duas pendências, com serviços reais no banco isolado de testes.

Quatro novos testes JavaScript cobrem inclusão após recuperação, preservação de erros no registro anterior e limpeza da próxima linha, bloco com erro fora da categoria selecionada, ausência de linha com gerenciamento inválido e manutenção do dropdown selecionado. Os testes anteriores continuam verificando os critérios do botão Adicionar, valores clonados, anúncios, foco, categorias, consultas e modais. O ambiente JavaScript usa DOM simulado.

| Verificação | Resultado |
|---|---|
| Novo arquivo Django, primeira execução isolada | **6 passed in 1.21s** |
| Suíte Django completa, execução final | **91 passed in 3.83s** — 85 anteriores + 6 novos |
| `node --test --test-reporter=dot cadastros/tests/js/*.test.cjs` | **40 testes aprovados** — 36 anteriores + 4 novos |
| `python manage.py check` pelo ambiente virtual | Sem problemas identificados |
| Compilação dos templates locais | **92 aprovados** — 88 anteriores + 4 includes novos |
| Revisão do diff e `git diff --check` | Sem erros de whitespace |

O Git emite avisos de normalização LF/CRLF em arquivos existentes; não foram tratados como falha funcional. A restrição anterior de acesso a `.pytest_cache` permanece separada dos resultados e o pytest foi executado sem cacheprovider. Nenhum dado de produção foi gravado.

### 19.5 — Validação manual e continuidade

Ainda é necessário validar em navegador real: escolher uma categoria, preencher/adicionar pelo menos dois registros, provocar erro na segunda linha e conferir valores/opções mantidos, links do resumo, foco e correção dos campos. Depois adicionar outro registro nessa resposta, verificar Tab/Shift+Tab, o anúncio de inclusão, ausência de IDs/referências indevidas e salvamento após correção. Conferir CEP/CPF, mudança de categoria, leitor de tela e zoom de 200%. A interface da resposta inválida apresenta campos editáveis por registro, em vez de tabelas vazias; esse estado visual também requer aceite do responsável.

O achado A2 foi tratado neste lote com a cobertura descrita. Regras de contratação, idade, exigência de vínculo, categorias, gravação e permissões foram preservadas. A auditoria global ainda tem A3 (labels em telas de Atribuição/Horários/Registro/Contratos), A4 (ações restantes) e A5 (acabamento), além do aceite manual final. O próximo lote recomendado é A3.

---

## 20. Indicação de obrigatoriedade e posição da ajuda dos campos

### 20.1 — Solicitação e referência de acessibilidade

O responsável solicitou substituir a palavra “Obrigatório”, repetida acima de cada campo, pelo padrão exemplificado com asterisco no label e orientação abaixo do controle. Perguntou se a WCAG exige escrever a palavra em cada campo.

Foi consultada a orientação oficial [W3C/WAI — técnica H90: indicação de campos obrigatórios por label/legend](https://www.w3.org/WAI/WCAG22/Techniques/html/H90). Essa técnica apresenta alternativas de texto ou símbolo, explicando o significado do asterisco no início do formulário. Não exige repetir a palavra junto a todo campo. Técnicas são exemplos de atendimento e não uma certificação automática de conformidade.

Decisão adotada: label/legend com `*` nos campos cujo form define `required=True`, uma instrução por formulário — “Campos marcados com * são obrigatórios” — e ajuda abaixo do controle. O atributo nativo `required` e as informações acessíveis continuam sob responsabilidade do Django; não foi adicionado `aria-required` redundante. O asterisco utiliza `abbr` com título “Obrigatório” e não comunica o estado apenas por cor.

### 20.2 — Implementação compartilhada

Foi criada uma biblioteca local de template tags, sem dependência externa, para acrescentar o indicador ao conteúdo do label/legend nativo do Django. Essa escolha preserva a associação por `for`, atributos, escape do texto e comportamento de grupos, sem construir labels manualmente em cada template.

`campo_formulario.html` passou a renderizar o controle antes do texto de ajuda, preservando os IDs de ajuda/erro e `aria-describedby`. A marcação explícita “Obrigatório” acima do input foi removida. Campos opcionais e ocultos não recebem asterisco. A instrução geral só aparece quando há ao menos um campo visível obrigatório e é incluída pelos resumos compartilhados, tanto no cadastro inicial quanto nos formulários que já usam esses componentes.

A cor do indicador usa a nova variável `--cor-indicador-obrigatorio`, referenciando a variável existente do fundo de Cancelar; não foi fixada cor na classe. Foram mantidos o tema atual, o foco e os scripts de navegação/consulta. A versão do CSS em `base.html` foi atualizada para evitar cache antigo.

A mudança alcança os formulários que já usam o componente compartilhado. Os templates legados identificados na auditoria continuam previstos nos próximos lotes; não se afirmou que todas as telas do aplicativo já foram migradas.

### 20.3 — Edição encontrada em paralelo e arquivos

Durante a verificação, o `help_text` de Situação já havia sido removido em `cadastros/forms.py`. Essa edição foi preservada; não se recriou o texto nem se alteraram escolhas ou obrigatoriedade. Foi removido somente o espaço em branco residual na linha dessa remoção. O teste anterior que pressupunha aquela ajuda específica passou a conferir as ajudas que estiverem efetivamente definidas no form. Os novos testes exercitam explicitamente ajuda e erro em campos controlados.

Arquivos alterados/criados neste passo:

- `cadastros/templatetags/__init__.py` e `cadastros/templatetags/acessibilidade.py` — novos.
- `templates/includes/campo_formulario.html`.
- `templates/includes/instrucoes_obrigatoriedade.html` — novo.
- `templates/includes/resumo_erros_formulario.html`.
- `cadastros/templates/cadastros/_resumo_erros_cadastro_pessoa.html`.
- `static/global/css/base.css` e `templates/base.html`.
- `cadastros/tests/test_campos_obrigatorios.py` — novo.
- `cadastros/tests/test_views_cadastro_acessibilidade.py` — ajuste da checagem de ajuda.
- `cadastros/forms.py` — somente limpeza de whitespace neste passo, preservando a remoção de ajuda encontrada.
- Este diário.

### 20.4 — Verificações e resultados

Dez cenários novos verificam campos obrigatórios/opcionais com input, select e grupo de opções, asterisco dentro do label/legend, título do símbolo, ajuda após o controle, atributos nativos, campos ocultos, instrução única, escape do label e associação do erro. O select do teste possui opção vazia, respeitando a regra nativa do Django para emitir `required`, sem forçar atributos em produção.

| Verificação | Resultado |
|---|---|
| Suíte Django completa | **101 passed in 3.73s** — 91 anteriores + 10 novos |
| `python manage.py check` pelo ambiente virtual | Sem problemas identificados |
| Testes JavaScript existentes | **40 aprovados** |
| Compilação dos templates locais | **93 aprovados** |
| Renderização pontual do exemplo CEP | Label com asterisco, input `required`, ajuda abaixo e referência válida |
| Revisão do diff e `git diff --check` | Sem erros de whitespace após limpeza da linha residual |

As verificações não incluíram navegador real. Ainda é necessário conferir o aspecto visual do asterisco e da instrução, leitura do estado obrigatório, foco, Tab/Shift+Tab e zoom de 200%, em página e popup. Regras de negócio, obrigatoriedade definida nos forms, permissões, APIs, modelos e serviços permaneceram intactos.

---

## 21. Correção de português nos rótulos dos formulários

O responsável apontou rótulos como “Funcao” em vez de “Função”. A revisão encontrou quatro rótulos explícitos sem acentos no cadastro inicial e outros textos gerados automaticamente pelos nomes dos campos dos models.

Em `cadastros/forms.py`, foram corrigidos “Função”, “Situação”, “Número” e “Data de início”. Foi criado o dicionário compartilhado `_ROTULOS_FORMULARIO`, aplicado por `Meta.labels` aos 23 ModelForms de Cadastros, para corrigir e harmonizar rótulos como “Descrição”, “Módulo”, “Submódulo”, “Período”, “Observação”, “Filiação”, “Organização”, “Nível de instrução”, “Documento comprobatório” e “Carga horária teórica/prática”. Campos de endereço e siglas reutilizam nomes legíveis como “Logradouro”, “CEP” e “UF”, coerentes com o cadastro inicial.

Isso altera somente a apresentação dos formulários e os textos que seus componentes de label/legend e resumo obtêm dos forms. Não foram renomeados campos Python, `name`, IDs, URLs, escolhas ou valores gravados. Models e banco não foram alterados; não foi necessária migration. As correções anteriores de Ata/Pessoa e a remoção de ajuda de Situação foram preservadas. Os forms de Atribuição foram inspecionados e seus labels explícitos já possuíam os acentos necessários, sem alteração neste passo.

Foram utilizadas as skills `django-accessibility` e `code-change-verification`. Arquivos alterados neste lote: `cadastros/forms.py` e este diário. Não houve mudança em templates, CSS, JavaScript, serviços, validações, regras acadêmicas ou permissões.

| Verificação | Resultado |
|---|---|
| `python manage.py check` pelo ambiente virtual | Sem problemas identificados |
| Suíte Django existente | **101 passed in 3.54s** |
| Inventário dos labels efetivos de Cadastros | 154 ocorrências de campos conferidas; grafias antigas selecionadas não reapareceram |
| Renderização pontual de Função, Situação, Número e Data de início | Textos corrigidos, nomes e IDs preservados |
| Revisão do diff e `git diff --check` | Sem erros de whitespace |

Não foram criados testes permanentes para uma correção textual nem repetidos testes JavaScript, pois os scripts não mudaram. A conferência pontual não gravou dados. A validação visual em navegador e a pronúncia pelo leitor de tela permanecem pendentes. Esta revisão de labels não substitui os lotes de associação dos labels legados, encerramentos e acabamento ainda listados na auditoria.

---

## 22. Associação dos 13 labels de Atribuição, Horários, Registro e Contratos (A3)

### 22.1 — Autorização e correção

O responsável autorizou o lote de associação dos labels identificado na auditoria. Foram utilizadas as skills `django-accessibility` e `code-change-verification`, com alteração limitada à apresentação e sem mudanças no processamento.

| Tela | Campos associados por `for` e `id` | Quantidade |
|---|---|---|
| Atribuição | Instrutor/Professor, Disciplina e Turma | 3 |
| Horários | Atribuição, Dia da Semana, Horário de Início e Horário de Fim | 4 |
| Registro de Instrução | Data, Carga Horária, Tipo e Conteúdo | 4 |
| Contratos | Pesquisa e Situação do contrato | 2 |

Os onze controles das três primeiras telas já tinham labels visuais, mas sem associação programática. Seus labels agora usam o asterisco aprovado e uma instrução única de obrigatoriedade no início de cada formulário, mantendo os atributos `required` existentes. O indicador foi extraído para a tag compartilhada `indicador_obrigatorio`, reutilizada tanto nos forms Django quanto nesses controles HTML manuais, sem estilos ou cores alternativos.

Em Contratos foram acrescentados labels visíveis “Pesquisar contratos” e “Situação do contrato”. Os campos foram agrupados individualmente para manter label acima do controle e alinhamento da linha de filtro. Os dois continuam opcionais, sem asterisco; placeholder, pesquisa preenchida, opções e valores foram preservados. Não houve alteração do retorno de foco de filtros neste lote.

Nomes, tipos, classes e estilos dos controles, opções, `step`, obrigatoriedade e métodos GET/POST permaneceram iguais. Os IDs foram acrescentados porque esses controles não os possuíam. CSRF e o restante dos templates foram preservados. Views, forms, serviços, models, banco, autenticação, permissões e regras de negócio não foram alterados.

### 22.2 — Arquivos alterados neste lote

- `atribuicao/templates/atribuicao/atribuicao.html`.
- `atribuicao/templates/atribuicao/horarios.html`.
- `atribuicao/templates/atribuicao/registro_instrucao.html`.
- `atribuicao/templates/atribuicao/contratos.html`.
- `cadastros/templatetags/acessibilidade.py` — extração do indicador reutilizável.
- `templates/includes/instrucoes_obrigatoriedade.html` — suporte explícito aos formulários HTML manuais e reutilização do indicador.
- Este diário.

### 22.3 — Verificações e resultados

| Verificação | Resultado |
|---|---|
| `python manage.py check` pelo ambiente virtual | Sem problemas identificados |
| Suíte Django existente | **101 passed in 3.66s** |
| Quatro telas renderizadas em dois estados | **8 cenários aprovados** |
| Compilação dos templates locais | **93 aprovados** |
| Revisão do diff e `git diff --check` | Sem erros de whitespace |

O script pontual utilizou o renderer Django e `HTMLParser`, com opções vazias/preenchidas e parâmetros de pesquisa sintéticos. Foram comparados os controles renderizados com os templates em `HEAD`: todos os atributos anteriores, opções e métodos foram preservados, excetuando somente o acréscimo dos IDs. Cada um dos treze controles possui exatamente um label correspondente; os IDs são únicos. Foram conferidos também a quantidade de asteriscos nos labels e a instrução única nas três telas com campos obrigatórios.

Não houve gravação de dados, criação de testes permanentes para marcação simples ou repetição da suíte JavaScript, pois nenhum script mudou. As renderizações não exercitam todos os estados de tabelas ou os fluxos reais de salvamento e não equivalem a teste de navegador.

### 22.4 — Validação manual e continuidade

Abrir as quatro telas e conferir a leitura dos labels ao receber foco, ativação do controle ao clicar no label, Tab/Shift+Tab, visibilidade do foco, asteriscos e zoom de 200%. Em Contratos, conferir especialmente a disposição dos labels e campos com largura reduzida. Não houve validação no navegador nesta execução.

O achado A3, relativo aos treze labels sem associação nessas telas, está implementado. A revisão de hierarquia de títulos e layouts permanece no acabamento A5, sem ser anunciada como concluída por esta correção. O próximo lote recomendado é A4: encerramentos, status e confirmações restantes, preservando os serviços e regras acadêmicas.

### 22.5 — Confirmação do responsável

Após a entrega, o responsável confirmou: “OK - TUDO FUNCIONANDO”. Fica registrado o aceite de funcionamento do lote dos treze labels. O relato não especifica leitor de tela ou nível de zoom utilizado; não foi interpretado como comprovação individual de todos os critérios de acessibilidade nem como encerramento da revisão global.

Esta atualização alterou somente o diário, sem mudanças em código ou necessidade de repetir testes.

---

## 23. Encerramentos, status e confirmações — lote A4

O responsável autorizou executar A4 e, na sequência, A5. Neste primeiro lote foram padronizados onze fragmentos: Status de Matrícula, Encerrar Turma, Revisar Aprovação, Encerrar Oferta, quatro confirmações de ativação/inativação, Módulo, Submódulo e confirmação de exclusão.

Os campos e erros utilizam os includes aprovados, com ajuda associada e resumo. Foram mantidos os nomes dos alunos nos labels dos checkboxes de aprovação e seus estados definidos pelo form. Os envios utilizam `btn-salvar`; o cancelamento em popup utiliza um include novo, `templates/includes/cancelar_modal.html`, com botão nativo e `data-fechar-modal-crud`, tratado pelo fechamento compartilhado. Nas páginas completas permanecem os links Voltar existentes. As ações POST acrescentam `?parcial=1` apenas no popup, preservando o contrato de redirecionamento da página completa. O aviso e as condições por categoria de encerramento foram preservados; sua marcação reutiliza `.erro`. A confirmação de exclusão recebeu legenda no fieldset e perdeu a cor inline alternativa do botão.

Arquivos deste lote: os onze fragmentos em `cadastros/templates/cadastros/` e `atribuicao/templates/atribuicao/`, o include de cancelamento, `cadastros/tests/test_views_matricula_planejamento.py` e este diário. Não foram alterados forms, views, serviços, models ou permissões.

Foram adicionados 44 cenários de renderização: onze fluxos, página/popup e estado inicial/com erro geral. Utilizam forms reais e banco de testes para os dados necessários; verificam ação, método, campos, IDs únicos, labels, referências de ajuda/erro e disponibilidade do cancelamento no modo correto. As mensagens gerais das confirmações sem campos são inseridas somente pelo teste para conferir sua apresentação; isso não afirma que tais erros ocorram normalmente em produção. O teste de Disciplina utiliza uma instância com cargas horárias válidas para respeitar a validação existente, sem modificar o model.

| Verificação | Resultado |
|---|---|
| Arquivo de regressão de Matrícula/Planejamento e ações | **62 passed in 1.20s** — 18 anteriores + 44 novos |
| Suíte Django completa | **145 passed in 3.88s** |
| `manage.py check` | Sem problemas identificados |
| Revisão do diff e `git diff --check` | Sem erros de whitespace |

### 23.1 — Falhas funcionais preexistentes separadas do lote visual

A inspeção das views revelou que `EncerrarTurmaView` implementa somente POST, enquanto seu form exige `turma` no construtor e a chamada atual não passa esse argumento. `RevisarAprovacaoView` implementa somente GET. A chamada das views via `RequestFactory`, sem banco, confirmou **HTTP 405 no GET de Encerrar Turma e no POST de Revisar Aprovação**. Instanciar `EncerrarTurmaForm({})`, como na view atual, confirmou `KeyError: 'turma'`. A implementação correspondente já existe em `HEAD`.

Nenhuma dessas views foi modificada: integrar esses fluxos acadêmicos exige correção funcional separada com testes específicos, além da apresentação dos templates. Os 145 testes aprovados não certificam esses endpoints incompletos. O lote A4 está implementado em apresentação; os dois fluxos não devem ser declarados integralmente funcionais até essa correção. As verificações não gravaram dados de produção nem efetivaram encerramento/aprovação.

Ainda é necessária conferência manual dos formulários acessíveis: Tab/Shift+Tab, erros, cancelamento/Esc, retorno do foco, leitor de tela e zoom de 200%. A execução prossegue para A5, conforme já autorizado.

---

## 24. Acabamento de acessibilidade — lote A5 e fechamento dos dois lotes autorizados

### 24.1 — Alterações compartilhadas e limites

Na sequência de A4, foi executado o acabamento autorizado, sem aguardar outra confirmação. Foram mantidas as skills `django-accessibility` e `code-change-verification` e a separação entre apresentação e regras acadêmicas.

- **Títulos:** 26 títulos principais de fragmentos passaram de `h3` para `h2`, com `.titulo-formulario` mantendo tamanho e cor do padrão anterior. Os títulos dos grupos de edição de Pessoa passaram de `h4` para `h3`, sob o `h2` principal. As seções de Atribuição, Horários e Registro passaram a usar `h2`. Foram acrescentados títulos de aba próprios em Atribuição, Horários, Contratos, Relatórios e Painel de Gestão. O nome do diálogo continua sendo obtido pelo JavaScript compartilhado, que já reconhece esses níveis de heading.
- **Contraste e limpeza:** foram retiradas 61 notas de diagnóstico que exibiam caminhos internos de templates com texto `#999`. Foram substituídas bordas claras inline dos controles encontrados pela variável existente `--cor-borda-controle`, sem redefinir campos ou inserir cores novas em classes. O foco visível foi estendido aos controles HTML manuais e links, mantendo o anel duplo dos botões e do link do cabeçalho escuro. Foram preservadas alternativas do sistema em cores forçadas.
- **Tabelas:** as 36 tabelas receberam um contêiner `.tabela-responsiva` com rolagem horizontal, `tabindex="0"`, região nomeada e foco visível. Caption, cabeçalhos, IDs, associações de dados e conteúdo foram preservados. Os seletores JavaScript de tabelas continuam por descendência. O contêiner recebe padding para acomodar o foco dos controles próximos às bordas; o comportamento visual precisa de aceite em navegador.
- **Larguras:** foram retiradas larguras mínimas de 260px nos filtros de Pessoas/Contratos. Os painéis de Registro de Instrução passaram das larguras fixas de 35%/65% para flex com quebra de linha, dimensões mínimas flexíveis e `min-width:0`. O histórico pode rolar dentro da tabela, sem obrigar o formulário a permanecer estreito ao lado.
- **Resumo de erros de opções:** o componente agora aponta para a primeira opção habilitada quando o grupo RadioSelect não fornece `id_for_label`, em vez de apresentar apenas texto. O link continua contendo somente o nome do campo, com contexto de registro quando aplicável. Erros de campos ocultos não recebem link inútil.

O ajuste atua sobre os componentes e templates locais. Não constitui implementação de tema escuro, revisão do Django Admin ou alteração de login/autenticação; `nucleo/login.html` não foi editado. Não foram modificados dados cadastrados, valores de escolhas, validações, serviços, modelos, migrations ou permissões.

### 24.2 — Arquivos envolvidos no acabamento

- Templates de `cadastros/templates/cadastros/`: remoção dos diagnósticos, títulos de fragmentos, contêineres das tabelas e largura do filtro de Pessoas.
- Templates de `atribuicao/templates/atribuicao/`: mesmos ajustes, títulos de aba/seções e composição responsiva de Registro de Instrução.
- Templates de `nucleo/templates/nucleo/`, exceto login: remoção de diagnósticos e contêineres das tabelas existentes.
- `static/global/css/base.css` e `templates/base.html`: estilos compartilhados e versão de cache `20261108-4`.
- `cadastros/templatetags/acessibilidade.py` e `templates/includes/itens_erros_formulario.html`: destino focável dos links de erro de grupos.
- `cadastros/tests/test_campos_obrigatorios.py`: dois testes novos para destino do grupo e ausência de link para campo oculto.
- `cadastros/tests/test_views_matricula_planejamento.py`: atualização da expectativa de título para `h2`; mantém as demais verificações de fluxo e renderização.
- Este diário.

Nenhuma view, serviço ou model foi modificado nos dois lotes. O diff geral também contém o trabalho dos lotes anteriores do dia, ainda não commitado; os resultados desta seção não representam um commit ou push novo.

### 24.3 — Verificação dos dois lotes

| Verificação | Resultado final |
|---|---|
| Suíte Django completa | **147 passed in 3.85s** — 101 anteriores + 44 cenários A4 + 2 cenários A5 |
| `python manage.py check` pelo ambiente virtual | Sem problemas identificados |
| Testes JavaScript existentes | **40 aprovados** |
| Compilação de todos os templates locais | **94 aprovados**, incluindo o novo include de cancelamento |
| Inventário das tabelas | 36 tabelas e 36 contêineres com acesso por teclado |
| Diagnósticos com caminho de template e `#999` | Nenhum remanescente na varredura fora de login |
| Estrutura do CSS | Chaves balanceadas; não equivale a validação de layout |
| Revisão do diff e `git diff --check` | Sem erros de whitespace |

Os testes que antes esperavam `h3` no popup foram atualizados para o novo `h2`, coerente com a correção semântica; a regressão de abertura, envio e apresentação de erros continuou sendo verificada. O teste de confirmação de Disciplina usa uma instância com cargas horárias preenchidas, evitando exercitar um model incompleto que não representa o registro existente da confirmação. Nenhuma regra foi afrouxada para aprovar os testes.

As verificações automatizadas e de renderização ocorreram sem gravar dados de produção. Não houve navegação visual, medição de overflow por pixels, teste de zoom real ou leitura por tecnologia assistiva nesta execução. A aprovação dos testes não elimina as falhas preexistentes de endpoints documentadas em 23.1.

### 24.4 — Resultado e pendências que permanecem

**Os dois lotes de interface autorizados, A4 e A5, foram implementados em sequência.** O trabalho de implementação desta lista de apresentação foi concluído, com os limites e falhas funcionais separados acima.

O aceite manual final deve conferir: primeiro Tab e salto; navegação pelo menu; filtros; campos e links de erro, inclusive RadioSelect; inclusão e recuperação de múltiplas linhas; abertura/cancelamento/salvamento dos popups; retorno de foco; rolagem das tabelas por teclado; modo de cores forçadas; títulos anunciados; e zoom de 200%. Em Registro de Instrução e Contratos, conferir especialmente o rearranjo dos painéis e filtros. Nas tabelas, verificar também se o anel dos botões é mostrado integralmente junto às bordas dos contêineres.

**Pendência funcional independente:** Encerrar Turma e Revisar Aprovação continuam exigindo correção das views e testes de integração, conforme 23.1. A abertura GET de Encerrar Turma e o envio POST de Revisar Aprovação retornam 405; a construção atual do form de encerramento também omite `turma`. Não se deve apresentar o aplicativo inteiro como concluído ou esses fluxos como funcionais antes dessa correção e do aceite manual. Nenhum encerramento ou aprovação foi efetivado para testar em produção.

---

## 25. Fechamento do dia — validação do responsável e próximas ações

### 25.1 — Validação manual informada em 08/11/2026

Após a entrega dos lotes, o responsável informou: **“Validei no navegador teclado, leitor de tela e zoom 200%”**. Fica registrado o aceite manual relatado para a interface entregue. Essa confirmação atualiza as pendências de validação geral dos registros anteriores, que descreviam o estado no momento de cada entrega; eles foram mantidos como histórico cronológico.

A validação foi realizada pelo responsável, não pelo agente. Não foram informados navegador, leitor de tela ou suas versões. Não se atribuiu a esse relato uma certificação WCAG nem a resolução das falhas funcionais de Encerrar Turma/Revisar Aprovação. As falhas continuam abertas e separadas do aceite de acessibilidade.

### 25.2 — Síntese dos trabalhos de hoje para o PI

- Ajustes de contraste, variáveis de cor, foco e responsividade da estrutura compartilhada.
- Adoção dos componentes de campos/ajuda/erros e botões nos formulários curriculares, complementares de Pessoa, edição, requisitos, encerramentos e confirmações.
- Recuperação de todas as linhas dos quatro formsets do cadastro inicial após erro, preservando valores, seleção, índices e gerenciamento; resumo com identificação do registro.
- Indicação de obrigatoriedade com asterisco, explicação única e ajuda abaixo do controle; correção dos rótulos em português.
- Associação de treze labels nas telas de Atribuição, Horários, Registro e Contratos.
- Retorno do foco em Filtrar/Limpar da lista de Pessoas e preservação dos comportamentos compartilhados de navegação e modais.
- Correção do filtro preexistente de Pessoa/Ata e das falhas de compilação/integração de Matrícula e Planejamento.
- Acabamento dos títulos, retirada de diagnósticos internos com baixo contraste e rolagem das tabelas por teclado.
- Auditoria documentada, ampliação da cobertura de regressão e organização das falhas funcionais que ficaram fora do lote de interface.

Resultado automatizado final já executado e detalhado nas seções anteriores: **147 testes Django aprovados, 40 testes JavaScript aprovados, 94 templates compilados e check Django sem problemas**. A validação manual acima foi acrescentada após esses resultados. Na revisão do fechamento, também foram corrigidos caracteres de acentuação que haviam sido substituídos por `?` em cinco títulos de aba e na legenda da confirmação de exclusão; o mesmo problema foi corrigido no cabeçalho do inventário gerado. Trata-se de reparo textual das edições anteriores, sem mudança funcional. A suíte completa não foi repetida por essas correções de texto; os templates foram recompilados e o inventário/diff conferidos.

### 25.3 — Ordem de trabalho registrada no Kanban

O arquivo existente do quadro é `docs/00 - KANBAN.md`. Foi adicionada uma seção no início com a ordem expressamente solicitada, prevalecendo sobre a fila histórica:

1. **Primeira ação: corrigir Encerrar Turma e Revisar Aprovação.** Registrar e tratar os dois retornos 405, a ausência de `turma` ao construir o form e a incompatibilidade da chamada do serviço com sua assinatura de data/ata. Integrar página/popup e cobrir o comportamento com testes sem modificar as regras acadêmicas. As falhas não foram corrigidas nesta atualização.
2. **Depois: mapear as alterações de outro DEV nas sete telas indicadas.** Além de Treinamento, o responsável acrescentou Auditoria Interna, Indicadores de Qualidade, Atribuição, Horário, Relatórios e Registro de Instrução. A intenção é separar os escopos e identificar o que foi alterado, sua origem e seus efeitos. Iniciar pelos templates abaixo e pelas views/rotas correspondentes, ampliando o levantamento aos arquivos relacionados conforme evidência. Comparar histórico/base/estado atual e apresentar tabela por tela/arquivo, alterações, autor/commit comprovados e impacto. Os ajustes de acessibilidade realizados hoje devem ser distinguidos das contribuições anteriores, sem atribuir a um único autor tudo que estiver no mesmo arquivo.

| Tela incluída no mapeamento | Template de entrada |
|---|---|
| Treinamento | `nucleo/templates/nucleo/treinamento.html` |
| Auditoria Interna | `nucleo/templates/nucleo/auditoria_interna.html` |
| Indicadores de Qualidade | `nucleo/templates/nucleo/indicadores_qualidade.html` |
| Atribuição | `atribuicao/templates/atribuicao/atribuicao.html` |
| Horário | `atribuicao/templates/atribuicao/horarios.html` |
| Relatórios | `atribuicao/templates/atribuicao/relatorios.html` |
| Registro de Instrução | `atribuicao/templates/atribuicao/registro_instrucao.html` |

O mapeamento das sete telas **ainda não foi executado**; não houve reversão de contribuições, divisão em branches/commits ou reescrita do histórico. A solicitação desta etapa foi registrar a intenção e a sequência de trabalho, não realizar essa separação agora. Essa complementação alterou somente o diário e o Kanban, sem mudanças no aplicativo.

### 25.4 — Estado da entrega

Os lotes de apresentação previstos e a validação manual relatada estão registrados. As correções funcionais permanecem como prioridade 1, e o mapeamento das sete telas como prioridade 2. Não houve commit ou push nesta atualização. Regras de negócio, permissões e dados de produção não foram modificados.

O inventário final abaixo completa o diário com todos os arquivos novos/modificados identificados na árvore de trabalho, para rastreabilidade da apresentação e do relatório do PI.

---

## 26. Inventário final dos arquivos novos e modificados no fechamento de 08/11/2026

Fonte: `git status --porcelain=v1 -z --untracked-files=all`, com referência ao commit atual `543c5bc`. No início da retomada, a árvore estava limpa, conforme seção 1. No fechamento há **96 arquivos: 81 modificados e 15 novos**, incluindo este diário e o Kanban atualizado. Arquivos ignorados pelo Git, como caches, não integram o inventário.

A lista registra o estado local ainda não commitado e inclui as alterações de apresentação, correções, testes e documentação da sessão. Não é uma atribuição de autoria por arquivo nem o mapeamento das contribuições do outro DEV, que continua como ação futura. Edições diretas do responsável e trabalho anterior dentro de um mesmo arquivo devem ser distinguidos pelo histórico e pelo diff quando necessário.

| Estado | Arquivo |
|---|---|
| Modificado | `atribuicao/templates/atribuicao/_form_encerrar_turma_fragment.html` |
| Modificado | `atribuicao/templates/atribuicao/_form_finalizar_planejamento_fragment.html` |
| Modificado | `atribuicao/templates/atribuicao/_form_matricula_fragment.html` |
| Modificado | `atribuicao/templates/atribuicao/_form_revisar_aprovacao_fragment.html` |
| Modificado | `atribuicao/templates/atribuicao/_form_status_matricula_fragment.html` |
| Modificado | `atribuicao/templates/atribuicao/atribuicao.html` |
| Modificado | `atribuicao/templates/atribuicao/contratos.html` |
| Modificado | `atribuicao/templates/atribuicao/dashboard.html` |
| Modificado | `atribuicao/templates/atribuicao/form_encerrar_turma.html` |
| Modificado | `atribuicao/templates/atribuicao/form_finalizar_planejamento.html` |
| Modificado | `atribuicao/templates/atribuicao/form_matricula.html` |
| Modificado | `atribuicao/templates/atribuicao/form_revisar_aprovacao.html` |
| Modificado | `atribuicao/templates/atribuicao/form_status_matricula.html` |
| Modificado | `atribuicao/templates/atribuicao/gerenciar_turma.html` |
| Modificado | `atribuicao/templates/atribuicao/horarios.html` |
| Modificado | `atribuicao/templates/atribuicao/registro_instrucao.html` |
| Modificado | `atribuicao/templates/atribuicao/relatorios.html` |
| Modificado | `cadastros/forms.py` |
| Modificado | `cadastros/static/cadastros/js/form-dinamico.js` |
| Novo | `cadastros/templates/cadastros/_campos_formset_cadastro.html` |
| Modificado | `cadastros/templates/cadastros/_confirmar_exclusao_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_ata_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_ata_pessoa_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_conteudo_programatico_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_disciplina_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_encerrar_oferta_modulo_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_experiencia_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_formacao_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_historico_vinculo_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_modulo_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_modulo_submodulo_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_oferta_modulo_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_pendencia_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_pessoa_editar_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_requisito_contratacao_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_submodulo_disciplina_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_submodulo_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_toggle_ativo_conteudo_programatico_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_toggle_ativo_disciplina_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_toggle_ativo_modulo_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_toggle_ativo_submodulo_fragment.html` |
| Modificado | `cadastros/templates/cadastros/_form_turma_fragment.html` |
| Novo | `cadastros/templates/cadastros/_itens_erros_formset.html` |
| Novo | `cadastros/templates/cadastros/_resumo_erros_cadastro_pessoa.html` |
| Modificado | `cadastros/templates/cadastros/detalhe.html` |
| Modificado | `cadastros/templates/cadastros/detalhe_ata.html` |
| Modificado | `cadastros/templates/cadastros/detalhe_disciplina.html` |
| Modificado | `cadastros/templates/cadastros/detalhe_modulo.html` |
| Modificado | `cadastros/templates/cadastros/detalhe_oferta_modulo.html` |
| Modificado | `cadastros/templates/cadastros/detalhe_submodulo.html` |
| Modificado | `cadastros/templates/cadastros/form_ata.html` |
| Modificado | `cadastros/templates/cadastros/form_ata_pessoa.html` |
| Modificado | `cadastros/templates/cadastros/form_conteudo_programatico.html` |
| Modificado | `cadastros/templates/cadastros/form_disciplina.html` |
| Modificado | `cadastros/templates/cadastros/form_encerrar_oferta_modulo.html` |
| Modificado | `cadastros/templates/cadastros/form_formacao.html` |
| Modificado | `cadastros/templates/cadastros/form_modulo.html` |
| Modificado | `cadastros/templates/cadastros/form_modulo_submodulo.html` |
| Modificado | `cadastros/templates/cadastros/form_oferta_modulo.html` |
| Modificado | `cadastros/templates/cadastros/form_pessoa.html` |
| Modificado | `cadastros/templates/cadastros/form_submodulo.html` |
| Modificado | `cadastros/templates/cadastros/form_submodulo_disciplina.html` |
| Modificado | `cadastros/templates/cadastros/form_toggle_ativo_conteudo_programatico.html` |
| Modificado | `cadastros/templates/cadastros/form_toggle_ativo_disciplina.html` |
| Modificado | `cadastros/templates/cadastros/form_toggle_ativo_modulo.html` |
| Modificado | `cadastros/templates/cadastros/form_toggle_ativo_submodulo.html` |
| Modificado | `cadastros/templates/cadastros/form_turma.html` |
| Modificado | `cadastros/templates/cadastros/lista.html` |
| Modificado | `cadastros/templates/cadastros/lista_atas.html` |
| Modificado | `cadastros/templates/cadastros/lista_disciplinas.html` |
| Modificado | `cadastros/templates/cadastros/lista_modulos.html` |
| Modificado | `cadastros/templates/cadastros/lista_ofertas_modulo.html` |
| Modificado | `cadastros/templates/cadastros/lista_submodulos.html` |
| Modificado | `cadastros/templates/cadastros/lista_turmas.html` |
| Novo | `cadastros/templatetags/__init__.py` |
| Novo | `cadastros/templatetags/acessibilidade.py` |
| Novo | `cadastros/tests/js/foco-filtros.test.cjs` |
| Modificado | `cadastros/tests/js/form-dinamico.test.cjs` |
| Novo | `cadastros/tests/test_campos_obrigatorios.py` |
| Novo | `cadastros/tests/test_views_ata_pessoa.py` |
| Novo | `cadastros/tests/test_views_cadastro_acessibilidade.py` |
| Novo | `cadastros/tests/test_views_matricula_planejamento.py` |
| Modificado | `docs/00 - KANBAN.md` |
| Novo | `docs/45 - ANDAMENTO_DO_PROJETO.md` |
| Modificado | `nucleo/templates/nucleo/auditoria_interna.html` |
| Modificado | `nucleo/templates/nucleo/home.html` |
| Modificado | `nucleo/templates/nucleo/registro_instrucao.html` |
| Modificado | `nucleo/templates/nucleo/treinamento.html` |
| Modificado | `static/global/css/base.css` |
| Novo | `static/global/js/foco-filtros.js` |
| Modificado | `templates/base.html` |
| Modificado | `templates/includes/campo_formulario.html` |
| Novo | `templates/includes/cancelar_modal.html` |
| Novo | `templates/includes/instrucoes_obrigatoriedade.html` |
| Novo | `templates/includes/itens_erros_formulario.html` |
| Modificado | `templates/includes/resumo_erros_formulario.html` |
