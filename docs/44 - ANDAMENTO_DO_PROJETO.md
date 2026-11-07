# Andamento do Projeto — 44

**Data:** 07/11/2026

**Branch:** `main`

**Sessão dedicada a: auditoria da estrutura global, acessibilidade do menu, formulários e tabela de Disciplinas, padronização visual de erros e botões, correção de KP duplicado e continuidade do foco entre páginas e popups.**

---

## 1. Contexto

Após os ajustes de interface documentados no diário 43, foi iniciada uma frente incremental de acessibilidade. A referência de trabalho é WCAG 2.2 AA, com prioridade para HTML semântico, navegação por teclado e zoom de 200%.

A sessão seguiu o `AGENTS.md` e as skills `django-accessibility` e `code-change-verification`. A orientação foi começar pelos componentes compartilhados, com alterações pequenas e verificáveis, preservando regras de negócio.

Este diário reúne a auditoria inicial e os três primeiros lotes da sessão. O registro também servirá de evidência para a apresentação em PPTX do PI e para o relatório final; por isso, distingue implementação, verificação automatizada e validação manual.

---

## 2. Auditoria inicial — sem alterações de código

Foram identificados 83 templates, 27 fragmentos de formulário, 12 ocorrências do contêiner de modal CRUD e 36 tabelas nos diretórios examinados.

| Estrutura | Localização / funcionamento |
|---|---|
| Base global | `templates/base.html`, com cabeçalho, navegação lateral e `main` |
| Configuração de templates | `config/settings.py`, com diretório global e templates dos apps |
| Menu | `nucleo/menu.py` e `nucleo/context_processors.py`; marcação na base e interação em `sidebar.js` |
| Formulários reutilizados | Fragmentos `_form_*_fragment.html`, usados em páginas completas e popups |
| Modal CRUD | Marcação repetida em listas/detalhes; comportamento comum em `cadastros/static/cadastros/js/modal-crud.js` |
| JavaScript dinâmico | `form-dinamico.js`, `buscar-cep.js` e `buscar-cpf.js` |
| Estilos compartilhados | `static/global/css/base.css` |

Os principais pontos levantados foram: ausência de salto para o conteúdo, estados do menu comunicados apenas visualmente, inconsistências de labels em páginas específicas, necessidade de avaliar associação de erros aos campos, ausência de gestão de foco no modal CRUD e falta de anúncios explícitos nas atualizações dinâmicas.

Nas tabelas examinadas, existem cabeçalhos `th`, mas não foram encontrados `scope` ou `caption`; a necessidade desses recursos deverá ser avaliada conforme cada tabela. Contraste, foco e responsividade exigem validação visual, além da leitura do código.

A auditoria não constitui certificação de conformidade WCAG. As demais observações e exceções levantadas, incluindo o fragmento de matrícula, permanecem fora dos lotes implementados nesta sessão.

---

## 3. Arquivos alterados nesta sessão

- `templates/base.html`
- `AGENTS.md` (regra de consistência visual)
- `static/global/css/base.css`
- `static/global/js/sidebar.js`
- `templates/includes/campo_formulario.html` (novo)
- `templates/includes/resumo_erros_formulario.html` (novo)
- `templates/includes/icone_erro.html` (novo)
- `templates/includes/mensagem_erro.html` (novo)
- `cadastros/templates/cadastros/_form_disciplina_fragment.html`
- `cadastros/templates/cadastros/_form_modulo_fragment.html`
- `cadastros/templates/cadastros/_form_submodulo_fragment.html`
- `cadastros/templates/cadastros/_form_conteudo_programatico_fragment.html`
- `cadastros/templates/cadastros/detalhe_disciplina.html` (versão do JavaScript estático)
- `cadastros/templates/cadastros/form_pessoa.html`
- `cadastros/forms.py` (correção de validação do KP, seção 13)
- `cadastros/views.py` (disciplina disponível antes da validação, seção 13)
- `cadastros/static/cadastros/js/modal-crud.js` (recuperação de foco e saída por teclado)
- `cadastros/tests/test_views_conteudo_programatico.py` (novo)
- `docs/44 - ANDAMENTO_DO_PROJETO.md`

Nos lotes iniciais de acessibilidade, não houve alteração de models, views, forms, serviços, rotas, migrations ou dependências. A correção explicitamente solicitada para KP duplicado, descrita na seção 13, posteriormente exigiu alterações pontuais em forms/views e testes de regressão, preservando a regra de unicidade existente.

---

## 4. Lote 1 — salto para o conteúdo principal

### 4.1 — Problema identificado

A base já possuía `main`, mas não oferecia um mecanismo para ultrapassar o cabeçalho e o menu lateral usando teclado. Isso obrigava a percorrer os controles anteriores ao conteúdo em cada página.

### 4.2 — Solução implementada

Foi adicionado como primeiro link do `body` o texto **“Pular para o conteúdo principal”**, apontando para `#conteudo-principal`.

O `main` recebeu `id="conteudo-principal"` e `tabindex="-1"`, permitindo receber foco ao ativar o salto, sem criar uma parada adicional na sequência normal de Tab.

No CSS global, o link permanece visualmente oculto até receber foco. Ao ser focalizado, aparece em posição destacada, com contorno visível e largura limitada à janela, permitindo quebra de texto em telas estreitas. O destino também possui contorno de foco.

### 4.3 — Validação

- `git diff --check`: sem erros.
- Check do Django: sem problemas identificados.
- Suíte existente: **44 testes aprovados**.
- Validação manual informada pelo responsável pelo projeto nesta conversa: primeiro Tab revela o link; Enter leva ao conteúdo; a navegação continua corretamente; zoom de 200% mantém a interface legível.

**Lote 1 concluído, com validação manual confirmada pelo responsável.**

---

## 5. Lote 2 — acessibilidade do menu lateral

### 5.1 — Problema identificado

O menu já usava `nav`, botões nativos e links. Entretanto, os estados aberto/fechado e a indicação da página atual dependiam das classes visuais `aberto` e `ativo`. Não havia associação explícita entre cada botão e seu submenu.

### 5.2 — Solução implementada

- Navegação identificada por `aria-label="Navegação principal"`.
- Cada submenu recebeu um ID único, gerado pelo contador do loop do template.
- Cada botão recebeu `aria-controls` apontando para o submenu correspondente.
- O JavaScript passou a sincronizar `aria-expanded` e a classe `aberto` na inicialização e em cada abertura/fechamento.
- Links reconhecidos como ativos pelo contexto existente recebem `aria-current="page"`, tanto para rotas normais quanto para páginas em construção.
- Botões dos grupos e links dos submenus receberam contorno explícito em `:focus-visible`. A cor acompanha o texto, permitindo destaque nos fundos claros e escuros já existentes.

### 5.3 — Comportamentos preservados

O menu mantém o accordion: abrir um grupo fecha os demais; acionar novamente um grupo aberto o fecha. Enter e Espaço continuam usando o comportamento nativo dos botões, sem listeners de teclado adicionais.

Sem JavaScript, todos os submenus continuam visíveis. Por esse motivo, a marcação inicial usa `aria-expanded="true"`; ao ativar o accordion, o script atualiza o atributo para refletir o estado visual de cada grupo.

Foram preservados os seletores existentes, os destinos dos links, os critérios de item ativo e a definição dos grupos. Não foram adicionados papéis de menu de aplicação, pois a estrutura continua sendo navegação por links.

---

## 6. Verificações executadas

Comandos executados para o lote 2:

| Comando | Resultado |
|---|---|
| `git diff --check` | Sem erros de whitespace |
| `node --check static/global/js/sidebar.js` | Sintaxe JavaScript válida |
| `.\venv\Scripts\python.exe manage.py check` | `System check identified no issues (0 silenced)` |
| `.\venv\Scripts\python.exe -m pytest -p no:cacheprovider` | **44 passed in 2.77s** |

O runner identificado é pytest com pytest-django e `config.settings`, conforme `pytest.ini`. A execução desabilitou apenas o cache do pytest, cujo diretório apresentou acesso negado na inspeção. No lote 1, o Python do ambiente virtual também teve acesso negado dentro do sandbox; os checks e testes foram executados com autorização fora dele. Esses incidentes de ambiente não foram falhas dos testes da aplicação.

A revisão do diff confirmou alterações restritas à base, aos estilos, ao script do menu e à documentação. Nenhuma migration foi criada. Os testes existentes verificam regressões dos fluxos cobertos, mas não substituem a avaliação de acessibilidade no navegador.

---

## 7. Estado geral ao final deste registro

| Item | Status |
|---|---|
| Auditoria da estrutura global | Concluída por inspeção estática |
| Salto para o conteúdo principal | Implementado e validado manualmente pelo responsável |
| Menu com nome, associação de controles e estados acessíveis | Implementado e validado manualmente pelo responsável |
| Foco explícito no menu | Validado pelo responsável |
| Checks e testes automatizados do lote 2 | Aprovados — 44 testes |
| Formulários e mensagens — piloto de Disciplina | Funcionamento confirmado pelo responsável; padrão visual revisado conforme seção 11 |
| Checks e testes automatizados do lote 3 | Aprovados — 44 testes e quatro cenários de renderização |
| Expansão para Módulo, Submódulo e Conteúdo Programático | Implementada; validação manual pendente |
| KP duplicado e recuperação de foco no modal | Corrigidos; 52 testes aprovados e validação no navegador pendente |
| Diário para subsidiar PPTX e relatório do PI | Registrado neste documento |

---

## 8. Validação manual — lote 2

- Percorrer o menu com Tab e Shift+Tab, verificando ordem e contorno de foco.
- Abrir e fechar grupos com Enter e Espaço, inclusive fechando o grupo já aberto.
- Confirmar que links de grupos fechados não recebem foco e os de grupos abertos ficam disponíveis.
- Confirmar com leitor de tela o nome da navegação, os estados expandido/recolhido e a página atual.
- Recarregar páginas de diferentes grupos e conferir a abertura inicial e o item ativo.
- Desabilitar JavaScript e confirmar que todos os links permanecem visíveis e navegáveis.
- Conferir o menu com zoom de 200%, incluindo legibilidade e foco nos grupos abertos e fechados.

O responsável informou que os testes solicitados estão funcionando, com uma ressalva: Enter abre a tela, mas Espaço não. A descrição sugere o acionamento de um link de navegação, cujo comportamento nativo é abrir com Enter; Espaço normalmente rola a página. Os botões de grupo, por outro lado, devem abrir e fechar os submenus tanto com Enter quanto com Espaço (ao soltar a tecla).

A inspeção confirmou botões nativos nos grupos e links nativos nos destinos, sem interceptação de teclado no `sidebar.js`. A orientação anterior de teste foi esclarecida: Enter/Espaço se aplica aos botões de grupo; Enter se aplica aos links para telas. Não foi adicionada simulação de Espaço nos links.

Esta atualização alterou apenas o diário. Não foram repetidos testes automatizados por se tratar de registro documental; os resultados da seção 6 permanecem referentes à implementação do lote 2.

Após compreender a função de Espaço, o responsável confirmou: **“Então está tudo funcionando”**. A ressalva foi encerrada como esclarecimento do comportamento nativo, sem necessidade de correção de código. A validação manual do menu foi considerada concluída com base no relato do responsável; não houve execução adicional de testes no navegador pelo agente.

**Lote 2 concluído, com checks automatizados aprovados e validação manual confirmada pelo responsável.**

---

## 9. Decisões, limites e próximos passos

As melhorias foram concentradas em componentes reutilizados por todas as páginas que herdam a base, reduzindo duplicação e mantendo o escopo pequeno. A sessão não alterou autenticação, login, usuários, perfis, permissões nem regras de matrícula, turma, ata, histórico, relocação, aprovação, reprovação ou encerramento.

A referência WCAG orientou as decisões, mas conformidade global e ausência de regressões fora da cobertura existente não podem ser afirmadas apenas com estes testes.

Próximos passos:

1. Validação manual do menu lateral concluída e registrada; manter esses cenários nas próximas verificações de regressão.
2. Validar manualmente o piloto de Disciplina descrito na seção 10 antes de ampliar o padrão de formulários e mensagens para outras telas.
3. Continuar com tabelas, modais/foco, conteúdo dinâmico, CSS e páginas específicas, em lotes independentes.
4. Atualizar o diário com cada implementação, resultado e pendência, preservando evidências para a apresentação e o relatório final do PI.

---

## 10. Lote 3 — formulários e mensagens: piloto de Disciplina

### 10.1 — Escolha do piloto e problema identificado

O formulário de Disciplina foi escolhido por ser pequeno (cinco campos) e compartilhar o mesmo fragmento entre página completa e modal de criação/edição. Assim, a alteração pode ser validada em um fluxo limitado antes de ser repetida em outros formulários.

Os labels e os erros por campo já eram renderizados. A inspeção do Django 5.2.17 instalado confirmou que ele gera `aria-invalid`, IDs das listas de erros e associações `aria-describedby` automaticamente. Portanto, esses atributos não foram duplicados manualmente.

Foi encontrado um problema concreto no texto de ajuda: o campo de carga horária do Programa de Instrução já possuía `help_text` e podia referenciá-lo por `aria-describedby`, mas o template não renderizava o elemento de ajuda. Faltavam também indicação textual explícita de obrigatoriedade e um resumo dos erros.

### 10.2 — Componentes reutilizáveis criados

`templates/includes/campo_formulario.html` reúne label, indicação “Obrigatório”, ajuda, widget e erros textuais. O texto de ajuda usa o ID esperado pelo Django (`<auto_id>_helptext`), permitindo resolver a referência do campo. A lista nativa de erros é mantida para preservar seu ID e a associação automática ao widget.

O componente também respeita campos ocultos e a indicação `use_fieldset` dos widgets que precisam de agrupamento. A aplicação inicial, entretanto, se limita aos cinco campos de Disciplina; outros widgets e formulários ainda não foram homologados para adoção em massa.

`templates/includes/resumo_erros_formulario.html` apresenta a mensagem “Não foi possível salvar. Corrija os erros abaixo.”, os erros gerais e os erros por campo. Os erros de campos visíveis possuem links para os respectivos controles. O resumo usa `role="alert"` para favorecer o anúncio de erros após atualização dinâmica; esse anúncio ainda depende de validação com leitor de tela.

### 10.3 — Aplicação e estilos

O fragmento `_form_disciplina_fragment.html` passou a usar os dois includes. Os grids, a ordem dos campos, os labels, o CSRF, os nomes e IDs dos controles, a ação POST e a classe `.form-modal-crud` foram preservados.

O CSS acrescenta estilos limitados aos novos componentes: ajuda e obrigatoriedade legíveis, mensagens com texto e borda, quebra de mensagens longas e foco explícito nos campos e nos links do resumo. Não depende apenas de cor para identificar erros.

Não houve alteração de obrigatoriedade, validação, salvamento ou da regra que compara a soma das cargas teórica/prática com o Programa de Instrução. Nenhuma dependência nova foi introduzida.

### 10.4 — Verificação automatizada

| Verificação | Resultado |
|---|---|
| `.\venv\Scripts\python.exe manage.py check` | Sem problemas identificados |
| `.\venv\Scripts\python.exe -m pytest -p no:cacheprovider` | **44 passed in 2.76s** |
| Renderização da página completa, inicial e com erros | Dois cenários aprovados |
| Renderização do fragmento de modal, inicial e com erros | Dois cenários aprovados |
| `git diff --check` e revisão do diff | Sem erros; mudanças restritas aos componentes, piloto, CSS e diário |

A verificação pontual de HTML foi executada por script em memória, usando `render_to_string`, `RequestFactory`, o formulário real de Disciplina e `HTMLParser`. Não foi criado arquivo de teste adicional nem gravado cadastro. Foram conferidos:

- ausência de IDs duplicados;
- labels apontando para controles existentes;
- referências `aria-describedby` resolvendo elementos presentes no HTML;
- ajuda e erro simultaneamente associados ao campo inválido;
- `aria-invalid="true"` no campo com erro;
- cinco controles e respectivas indicações de obrigatoriedade;
- manutenção do CSRF, ação POST e classe usada pelo modal;
- resumo somente quando há erros e preservação dos erros gerais da regra de carga horária.

Essas verificações comprovam a estrutura renderizada; não comprovam comportamento de foco, anúncio por leitor de tela ou layout no navegador. A mudança final de CSS de foco foi revisada no diff, sem nova execução dos testes Python, pois não altera renderização ou lógica do Django.

### 10.5 — Validação manual pendente

1. Abrir “Nova Disciplina” e editar uma Disciplina já existente, verificando labels, indicação “Obrigatório” e ajuda do Programa de Instrução.
2. Percorrer os campos e o botão Salvar com Tab/Shift+Tab, conferindo o foco visível.
3. Informar, por exemplo, Programa de Instrução de 80h e cargas teórica/prática de 30h cada: a regra existente deve impedir o salvamento e exibir o erro geral no resumo. Corrigir para 40h + 40h e confirmar o fluxo normal de salvar.
4. Provocar um erro validado pelo servidor, como sigla já cadastrada, conferir o resumo e os erros junto ao campo; ativar o link do resumo e confirmar o foco no controle correspondente. Campos vazios podem ser bloqueados primeiro pela validação nativa do navegador.
5. Conferir leitura da ajuda, indicação de campo inválido e anúncio do resumo com leitor de tela.
6. Conferir criação/edição no modal e, quando acessada diretamente, na página completa, com zoom de 200%.

O foco após substituição dinâmica do conteúdo do modal continua pertencendo ao lote específico de modais/foco; este piloto não modifica o JavaScript do modal. A expansão do padrão para outros formulários deve ocorrer após a confirmação manual deste lote.

---

## 11. Revisão do lote 3 — preservação do padrão visual de erros

### 11.1 — Retorno do responsável e decisão

O responsável confirmou que o piloto funcionou, mas apontou que a barra vermelha lateral introduzia um padrão visual diferente do utilizado no aplicativo. Foi fornecida como referência a mensagem de erro do Cadastro de Pessoa: fundo rosado, borda fina e ícone de aviso em uma caixa à esquerda.

A decisão foi preservar esse padrão existente e centralizar sua reutilização. A identificação do campo inválido, a ajuda e os recursos acessíveis introduzidos no piloto permanecem. A barra lateral e o fundo branco dos erros do piloto foram retirados.

### 11.2 — Avaliação de contraste e acessibilidade

O contraste foi calculado a partir das cores do CSS, usando luminância relativa sRGB:

| Combinação | Razão de contraste | Resultado para texto comum |
|---|---|---|
| Texto `#a94442` sobre fundo `#f2dede` | 4,5313:1 | Atende ao mínimo AA de 4,5:1 |
| Azul global `#2f75b5` sobre o mesmo fundo | 3,7572:1 | Insuficiente; não foi mantido nos links do alerta |

Os links dentro de `.erro` agora herdam a cor do texto e possuem sublinhado, inclusive em hover. Isso mantém o contraste e identifica links sem depender apenas da cor. Os links do resumo continuam com contorno explícito de foco.

O ícone de aviso é decorativo (`aria-hidden="true"`), pois a mensagem textual comunica o problema. A borda e o ícone complementam o texto; a indicação do erro não depende exclusivamente deles. Os IDs e atributos associados aos campos foram preservados.

Essa avaliação aprova a combinação de cores do componente de erro, mas não equivale a uma auditoria de contraste ou conformidade de todas as telas do aplicativo. O contraste aprovado possui pouca margem acima do limite; mudanças futuras nas cores devem ser recalculadas.

Referências consultadas:

- [WCAG 2.2 — contraste mínimo (1.4.3)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- [WCAG 2.2 — uso da cor (1.4.1)](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)
- [WCAG 2.2 — identificação de erros (3.3.1)](https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html)

### 11.3 — Arquitetura de reutilização

- `includes/icone_erro.html`: ícone decorativo compartilhado.
- `includes/mensagem_erro.html`: caixa `.erro` com ícone, conteúdo e identificação opcional do campo.
- `includes/resumo_erros_formulario.html`: mesmo padrão visual, com resumo e links para os campos.
- `includes/campo_formulario.html`: passou a utilizar o componente compartilhado de mensagem.
- `cadastros/form_pessoa.html`: passou a reutilizar o mesmo componente para os erros gerais, substituindo a caixa aninhada que aplicava `.erro` ao próprio ícone.
- `base.css`: removido o estilo alternativo do piloto e consolidada a declaração duplicada do componente `.erro`, mantendo as cores existentes.

Foi acrescentada ao `AGENTS.md` a regra de consistência visual: reutilizar componentes existentes em todo o aplicativo, manter o padrão de erro e corrigir componentes compartilhados quando um requisito de acessibilidade exigir ajuste. Os próximos lotes deverão seguir essa orientação. Esta revisão não migrou todos os formulários e avisos antigos de uma só vez.

### 11.4 — Verificação e limites

- `manage.py check`: sem problemas identificados.
- Suíte existente: **44 passed in 2.82s**.
- Script em memória: quatro cenários de renderização de Disciplina aprovados (página completa e fragmento, iniciais e com erros), conferindo IDs únicos, labels, referências `aria-describedby`, erros gerais, `aria-invalid`, CSRF e ícone decorativo.
- Renderização isolada do componente usado no Cadastro de Pessoa: aprovada, com mensagem e ícone presentes.
- `git diff --check`: sem erros.

O responsável já confirmou o funcionamento do piloto anterior. A aparência revista, a quebra de texto em zoom de 200%, o foco dos links e os anúncios de erro no navegador ainda exigem validação manual após esta revisão. Não foram alteradas regras de validação, models, views, forms, serviços, rotas, autenticação ou permissões.

---

## 12. Expansão do lote de formulários — Módulo, Submódulo e Conteúdo Programático

### 12.1 — Aprovação e escopo

Após a revisão visual, o responsável aprovou o resultado do piloto de Disciplina e autorizou a expansão para um grupo pequeno de formulários. Nesta etapa, foram alterados somente os três fragmentos indicados abaixo, além deste diário. Os componentes, CSS e JavaScript compartilhados não precisaram de nova alteração.

| Fragmento | Campos mantidos, na ordem original |
|---|---|
| `_form_modulo_fragment.html` | nome, sigla, descrição |
| `_form_submodulo_fragment.html` | nome, sigla |
| `_form_conteudo_programatico_fragment.html` | ordem, descrição, observação |

As páginas completas estendem `base.html` e incluem esses mesmos fragmentos. Os modais os recebem pelo mecanismo existente de `ModalCrudMixin` e `modal-crud.js`. Assim, a expansão atende criação e edição sem duplicar marcação nas páginas completas.

### 12.2 — Melhorias implementadas

- Substituição da renderização repetida de cada campo pelo include `campo_formulario.html`.
- Identificação textual dos campos obrigatórios, respeitando o atributo `required` definido nos forms existentes; campos opcionais continuam opcionais.
- Renderização de ajuda quando disponível e preservação das associações nativas do Django entre controle, ajuda e erro.
- Inclusão de `resumo_erros_formulario.html` nos três formulários. Antes, esses fragmentos não renderizavam explicitamente os erros gerais (`non_field_errors`).
- Erros junto aos campos e resumo utilizando o padrão visual aprovado: fundo rosado, texto vermelho escuro, borda fina e ícone decorativo.
- Reutilização dos estilos existentes de foco e dos links do resumo para os controles inválidos.

Foram preservados títulos, grids, ordem e nomes dos campos, IDs dos widgets, CSRF, ação POST com `?parcial=1`, classe `.form-modal-crud`, botões e identificação da Disciplina no Conteúdo Programático. A renderização dos campos de texto longo continua usando os widgets definidos nos forms.

### 12.3 — Verificações executadas

| Verificação | Resultado |
|---|---|
| `.\venv\Scripts\python.exe manage.py check` | Sem problemas identificados |
| `.\venv\Scripts\python.exe -m pytest -p no:cacheprovider` | **44 passed in 2.58s** |
| Verificação de renderização em memória | **24 cenários aprovados**, oito por formulário |
| `git diff --check` restrito aos três fragmentos | Sem erros |
| Revisão do diff dos três fragmentos | Apenas adoção dos includes compartilhados e resumo de erros |

Os 24 cenários combinam criação/edição, página completa/fragmento e estado inicial/com erros. Foram usados os forms reais, `RequestFactory`, `render_to_string` e `HTMLParser`, sem salvar registros ou criar arquivos de teste. A indicação de edição foi verificada pelo contexto de template, sem executar uma atualização no banco.

Foram conferidos: IDs únicos; labels associados a controles existentes; referências `aria-describedby` válidas; nomes, IDs e ordem dos campos preservados; obrigatoriedade coerente com os forms; `aria-invalid` nos campos com erro; presença condicional do resumo; links para os campos; ícone decorativo; CSRF; ação POST e classe esperada pelo modal. Também foi adicionada uma mensagem geral apenas em memória para verificar sua exibição, sem modificar qualquer regra de validação.

A checagem global do diff encontrou um aviso de espaço em branco ao fim da linha 12 de `_form_disciplina_fragment.html`, fora dos três arquivos deste lote. Esse arquivo não foi alterado nesta expansão. O aviso não representa falha dos checks ou testes Django e não aparece na checagem restrita ao lote.

### 12.4 — Validação manual pendente

1. Abrir criação e edição de Módulo, Submódulo e Item do Conteúdo Programático, verificando o padrão visual e a identificação da Disciplina.
2. Percorrer campos, links de erro e botão Salvar com Tab/Shift+Tab; conferir foco e acionamento dos links com Enter.
3. Conferir que apenas campos obrigatórios recebem a indicação e que campos opcionais continuam aceitando vazio.
4. Provocar um erro validado pelo servidor, por exemplo uma sigla duplicada em Módulo/Submódulo, e conferir resumo, mensagem junto ao campo e navegação pelo link do resumo.
5. Corrigir o erro e conferir o salvamento pelos fluxos habituais, tanto na criação quanto na edição.
6. Conferir zoom de 200%, quebra de mensagens e leitura das associações/erros com leitor de tela, em página completa e modal.

O anúncio do resumo e a interação após a substituição do conteúdo do modal ainda dependem de teste no navegador. A gestão de foco do modal permanece para seu lote específico. Não houve alteração de regras de negócio, validações, autenticação, permissões, models, forms, views, serviços, rotas ou migrations.

Após a validação manual desta expansão, o próximo lote proposto é o de tabelas, começando por uma listagem simples e reutilizando o estilo existente.

---

## 13. Correção solicitada — KP repetido na mesma Disciplina e teclado após erro

### 13.1 — Relato e reprodução

Durante a validação manual, o responsável identificou que adicionar um Conteúdo Programático com número (KP/campo `ordem`) já utilizado na mesma Disciplina gerava erro não tratado e prejudicava a navegação por teclado, exigindo o mouse para sair.

Foram criados oito cenários de regressão no runner pytest existente. Antes da correção, quatro falharam com `IntegrityError: UNIQUE constraint failed` (duplicidade na criação e edição, em página completa e modal); os outros quatro, relativos a operações permitidas, passaram. Isso reproduziu a falha do servidor em banco de testes, sem modificar dados reais.

### 13.2 — Causa e tratamento no servidor

A regra `unique_ordem_por_disciplina` já existia no banco. Entretanto, `disciplina` não é um campo editável do formulário, e a validação automática da combinação não era suficiente. Na criação, a disciplina ainda só era associada à instância em `form_valid`, depois de `is_valid()`.

A view de criação agora associa a disciplina ao construir o formulário, antes de validá-lo. O `ConteudoProgramaticoModelForm.clean_ordem()` consulta a combinação disciplina/KP e devolve erro associado ao campo `ordem` quando necessário. Na edição, o próprio registro é excluído da consulta, permitindo manter seu número atual.

Mensagem apresentada no padrão visual existente:

> Já existe um item de conteúdo programático com este número (KP) nesta disciplina. Informe outro número.

O formulário retorna com erro de validação, mantendo os dados informados, o resumo e a associação acessível ao campo. Não há nova regra de negócio: a unicidade por disciplina e a restrição do banco permanecem intactas. O mesmo número continua permitido em disciplinas diferentes. A verificação anterior ao salvamento não substitui a restrição do banco em situações de concorrência entre requisições.

### 13.3 — Recuperação de foco e saída por teclado

Foi antecipada uma parte pontual do lote de foco dos modais para resolver o problema relatado no fluxo compartilhado de `modal-crud.js`:

- Ao abrir, o foco vai ao botão Fechar durante o carregamento e depois ao primeiro campo disponível.
- Após retorno do formulário com erros, o foco vai ao primeiro campo com `aria-invalid="true"`.
- `Esc` fecha o modal; o botão de fechar possui nome acessível “Fechar formulário”.
- Ao fechar, o foco retorna ao botão que abriu o modal, se ele ainda estiver no documento.
- Respostas HTTP de erro não são mais inseridas como se fossem um formulário válido; é exibida mensagem textual no componente visual `.erro`, com foco e sem remover os campos digitados em falhas de envio.
- Respostas recebidas depois de fechar o modal são ignoradas enquanto ele permanece fechado.

O comportamento é compartilhado pelos modais CRUD que usam esse script; por isso, outros formulários também devem entrar na verificação manual de regressão. Esta correção não equivale à conclusão da auditoria integral de modais: semântica de diálogo, contenção de foco e demais aspectos ainda pertencem ao lote específico.

### 13.4 — Verificações e resultados

| Verificação | Resultado |
|---|---|
| Reprodução anterior à correção | Quatro falhas de duplicidade e quatro cenários permitidos aprovados |
| Suíte completa após a correção | **52 passed in 2.62s** |
| `manage.py check` | Sem problemas identificados |
| `node --check cadastros/static/cadastros/js/modal-crud.js` | Sintaxe válida |
| Simulação em memória do script com Node, `vm` e DOM simplificado | Foco inicial, foco após erro, fechamento por Esc, retorno ao gatilho e recuperação de erro HTTP aprovados |
| `git diff --check` restrito aos arquivos desta correção | Sem erros |

Os oito testes adicionados cobrem, em página completa e resposta parcial: criação duplicada, correção do número após rejeição seguida de salvamento, edição para número duplicado sem alterar o registro original, edição mantendo o número atual e reutilização do número em outra disciplina. São oito casos parametrizados; a correção seguida de salvamento integra os testes de criação duplicada.

A simulação JavaScript verifica a lógica dos handlers com objetos simplificados; não substitui um navegador real, a navegação nativa por Tab ou o teste com leitor de tela. Não foram alterados models, migrations, URLs, campos, autenticação ou permissões. O aviso global de whitespace no fragmento de Disciplina, registrado na seção 12, continua fora desta correção.

### 13.5 — Validação manual pendente

1. Abrir “Adicionar Item” em uma Disciplina com KP já cadastrado e enviar o mesmo número: deve surgir o erro no padrão rosado e o foco deve retornar ao campo do KP, mantendo descrição e observação.
2. Corrigir para um número disponível e salvar normalmente; repetir o cenário na edição.
3. Após o erro, navegar com Tab/Shift+Tab, fechar com Esc e confirmar retorno ao botão “Adicionar Item” ou “Editar”.
4. Conferir o erro e sua associação ao campo com leitor de tela e zoom de 200%.
5. Conferir abertura, envio inválido e fechamento em outros modais CRUD, pois o script de foco é compartilhado.

---

## 14. Refinamento solicitado — mensagem explicativa e botão Cancelar

O responsável solicitou uma mensagem que identifique a causa do erro e oriente a recuperação, conforme o princípio de design citado por ele (Don Norman), além de um botão explícito para cancelar.

O erro de duplicidade no campo `ordem` passou a usar o texto solicitado:

> Não foi possível salvar porque este número de ordem já está em uso. Informe um número ainda não utilizado. Os dados preenchidos foram mantidos no formulário. Corrija o número de ordem e tente novamente ou feche a janela para cancelar.

A mensagem identifica a duplicidade somente quando ela é confirmada pela validação do formulário. Falhas de comunicação ou respostas HTTP de erro continuam com uma mensagem própria, agora explicitando falha na comunicação ou no servidor; não são classificadas indevidamente como número duplicado. O padrão visual compartilhado de erros foi preservado.

Foi acrescentado “Cancelar” ao fragmento de Conteúdo Programático, atendendo criação e edição:

- No modal, é um `button type="button"` com `data-fechar-modal-crud`, para fechar sem submeter o formulário e devolver o foco ao gatilho.
- Na página completa, é um link de navegação para o detalhe da Disciplina.
- O JavaScript trata o cancelamento por delegação no corpo do modal, de modo que continue funcionando após a substituição do formulário por uma resposta com erros.

Arquivos envolvidos: `cadastros/forms.py`, `_form_conteudo_programatico_fragment.html`, `cadastros/static/cadastros/js/modal-crud.js`, `cadastros/tests/test_views_conteudo_programatico.py` e este diário. Nenhuma regra de negócio foi alterada.

Verificações:

- **52 passed in 2.68s**, incluindo conferência do texto exato do erro e do controle Cancelar em página completa e resposta parcial.
- `manage.py check`: sem problemas identificados.
- `node --check` do script e `git diff --check` restrito à alteração: aprovados.
- Simulação em memória com Node e DOM simplificado: cancelamento delegado, reabertura e retorno do foco ao gatilho aprovados.

Falta conferir no navegador o novo texto, o acionamento de Cancelar por teclado (Enter/Espaço no botão), o retorno de foco após erro e o destino do link Cancelar na página completa. Cancelar descarta a edição local da janela e não submete o formulário; não desfaz um envio já iniciado anteriormente.

---

## 15. Ajuste de botões — geometria compartilhada e cancelamento resiliente

### 15.1 — Relato e aparência

O responsável apontou diferenças de formatação entre “Salvar Item” e “Cancelar” e informou que o cancelamento não funcionava no navegador. A diferença visual vinha da regra global `button[type="submit"]`, que aplicava fonte, margem e padding distintos aos botões de outros tipos.

Foram criadas as classes reutilizáveis `.btn-salvar` e `.btn-cancelar`, com mesma fonte, peso, altura de linha, padding, margem, largura mínima, alinhamento, borda e foco. As cores solicitadas foram aplicadas:

| Ação | Fundo | Texto | Contraste calculado |
|---|---|---|---|
| Salvar | `#002060` | `#FFFFFF` | 15,27:1 |
| Cancelar | `#6C757D` | `#FFFFFF` | 4,69:1 |

Ambas as combinações atendem ao mínimo de 4,5:1 para texto comum. Os estilos incluem hover e foco visível, sem alterar os botões antigos que ainda não adotaram essas classes. O formulário de Conteúdo Programático passou a usá-las, e a regra de reutilização foi acrescentada ao `AGENTS.md`.

### 15.2 — Cancelamento com e sem JavaScript

A versão anterior dependia exclusivamente do listener JavaScript para cancelar no modal. A simulação desse listener passa, mas isso não comprova que a página aberta pelo responsável tenha carregado a versão atualizada. Cache/JavaScript antigo é uma hipótese, não uma causa confirmada.

O controle agora permanece um botão nativo, acionável com Enter e Espaço, e possui uma alternativa independente do listener:

- O botão Cancelar está associado, pelo atributo HTML `form`, a um formulário GET separado, cujo destino é o detalhe da Disciplina.
- Esse formulário fica fora do formulário de salvamento, não possui campos e não exige validação dos campos obrigatórios do cadastro.
- Com o listener atualizado, o clique é interceptado, o modal fecha e o foco retorna ao gatilho.
- Sem esse listener, a ação nativa navega para o detalhe da Disciplina, sem executar o POST de salvamento.

A base passou a carregar o CSS com `?v=20261107-2`, e o detalhe de Disciplina usa a mesma versão no carregamento de `modal-crud.js`, evitando reutilização das URLs antigas após recarregar a página. Essas mudanças não atualizam retroativamente um script já executado em uma aba aberta: é necessário recarregar a página.

### 15.3 — Tentativa de teste real e verificações

Foi iniciada uma verificação no Edge pela skill de uso do computador. A ferramenta interrompeu o acesso porque não conseguiu determinar a URL atual no Windows com segurança suficiente para aplicar suas regras. Nenhuma interação com o formulário foi realizada por essa automação. Portanto, não foi possível reproduzir ou confirmar a falha no navegador nesta etapa.

Verificações concluídas:

- `manage.py check`: sem problemas identificados.
- Suíte completa na versão final: **52 passed in 2.91s**, incluindo presença das classes, associação do botão Cancelar ao formulário GET e destino correto em página e fragmento com erro.
- Simulação do handler delegado: cancelamento, fechamento e retorno do foco aprovados.
- Contrastes calculados em Node pela fórmula de luminância relativa sRGB.
- `node --check` do JavaScript: aprovado. A checagem de whitespace apontou um espaço em branco na linha 21 de `base.html`, fora da linha de carregamento de CSS alterada neste ajuste; esse trecho não foi modificado. Não houve falha de checks ou testes Django.

Foram alterados o fragmento de Conteúdo Programático, `base.css`, a URL do CSS na base, a URL do JavaScript no detalhe de Disciplina, os testes de regressão, o `AGENTS.md` e este diário. Não houve alteração de regras de negócio, banco, validações ou permissões.

### 15.4 — Confirmação pendente no navegador

Recarregar a página do detalhe da Disciplina; abrir criação/edição e conferir as dimensões e cores. Acionar Cancelar por mouse, Enter e Espaço, inclusive após erro de KP duplicado. Com o JavaScript atual, deve fechar o modal e retornar o foco; na alternativa nativa, deve navegar ao detalhe sem salvar. Conferir também zoom de 200%.

---

## 16. Cores dos botões por variáveis e nova cor de Cancelar

O responsável solicitou retirar as cores literais das classes de botões para facilitar a futura alternância de temas e alterar Cancelar para fundo `#B50A04` com texto `#F7F7F7`.

As cores foram centralizadas no `:root` de `base.css`:

- `--botao-salvar-fundo` e `--botao-salvar-fundo-hover` reutilizam as variáveis institucionais existentes; `--botao-salvar-texto` mantém o branco.
- `--botao-cancelar-fundo: #b50a04` e `--botao-cancelar-texto: #f7f7f7` aplicam as cores solicitadas.
- `--botao-cancelar-fundo-hover: #920803` define o estado hover.
- `--botao-foco` centraliza a cor do contorno de foco dos botões.

As regras de `.btn-salvar` e `.btn-cancelar` agora usam somente `var(...)` para cores de fundo, texto, hover e foco. As dimensões e o comportamento dos controles foram preservados. Isso permite sobrescrever essas variáveis em um tema futuro; não foi implementada alternância de modo claro/escuro nesta etapa.

A regra de estilo no `AGENTS.md` foi atualizada, substituindo o cinza aprovado anteriormente pelas novas cores e exigindo uso das variáveis. O carregamento do CSS na base passou a `?v=20261107-3` para atualizar a folha após recarregar a página.

Verificação:

- Contraste de `#F7F7F7` sobre `#B50A04`: **6,51:1**; em hover sobre `#920803`: **8,68:1**. Ambas as combinações atendem ao mínimo de 4,5:1 para texto comum.
- Inspeção automatizada do bloco de CSS: nenhuma cor literal nas regras dos botões Salvar/Cancelar.
- `manage.py check`: sem problemas identificados.
- Suíte existente: **52 passed in 3.09s**.
- `git diff --check` restrito a `base.css` e `AGENTS.md`: sem erros. O aviso de whitespace já registrado em outra linha de `base.html` não foi alterado.

Arquivos alterados nesta revisão: `static/global/css/base.css`, `templates/base.html`, `AGENTS.md` e este diário. Nenhuma regra de negócio, evento de cancelamento ou permissão foi modificada. Falta conferir no navegador a nova cor, hover e foco após recarregar a página.

---

## 17. Resumo de erros simplificado — um link por campo

Por solicitação do responsável, o resumo no início do formulário deixou de repetir as mensagens completas já exibidas junto aos campos. O link agora contém somente o nome do campo, por exemplo **“Ordem”**, sem dois-pontos ou texto de validação.

O componente compartilhado `resumo_erros_formulario.html` passou a gerar um item por campo inválido, mesmo que esse campo tenha mais de uma mensagem. A mensagem completa permanece junto ao controle, com sua associação acessível original. O cabeçalho “Não foi possível salvar. Corrija os erros abaixo.”, o padrão visual e os erros gerais do formulário foram preservados.

A regra foi registrada no `AGENTS.md` para manter a consistência nas próximas telas. A alteração beneficia os formulários que já usam o resumo compartilhado: Disciplina, Módulo, Submódulo e Conteúdo Programático.

Verificação: **52 passed in 2.90s**, `manage.py check` sem problemas e revisão do diff. Os testes do KP duplicado agora conferem o link `<a href="#id_ordem">Ordem</a>` e verificam que a mensagem completa aparece uma única vez no HTML, junto ao campo. Nenhuma regra de negócio ou validação foi alterada.

Arquivos alterados: `templates/includes/resumo_erros_formulario.html`, `cadastros/tests/test_views_conteudo_programatico.py`, `AGENTS.md` e este diário. Falta conferir visualmente o resumo e ativar o link por teclado no navegador.

---

## 18. Continuidade por teclado — retorno de foco após salvar popup

### 18.1 — Problema relatado e causa

O responsável relatou que, ao salvar um Conteúdo Programático aberto por teclado, precisava pressionar Tab muitas vezes para voltar ao ponto anterior. O nome do recurso foi esclarecido como **foco**.

O script já devolvia foco ao gatilho ao fechar/cancelar. Entretanto, no salvamento bem-sucedido, executava `window.location.reload()`, destruindo o elemento e sua referência em memória. A página recarregada iniciava uma nova sequência de navegação.

### 18.2 — Solução compartilhada

Antes do recarregamento por sucesso, `modal-crud.js` grava em `sessionStorage` um marcador contendo a página e seus parâmetros, a URL da ação do botão que abriu o popup e o índice entre botões com a mesma URL. Não são armazenados valores dos campos.

Na inicialização seguinte, o marcador é consumido e removido. Se a página e seus parâmetros correspondem e o botão ainda existe e está habilitado, o foco retorna a ele. Assim, o próximo Tab pode continuar a partir desse controle, em vez de reiniciar no cabeçalho.

O marcador é restrito à aba pelo armazenamento de sessão. Ele não é reaplicado em outra página/filtro e é usado uma única vez. Se o gatilho desapareceu, não há redirecionamento arbitrário de foco. Armazenamento bloqueado ou registro inválido não impedem o salvamento ou recarregamento; nesse caso, o retorno após recarga não está disponível.

O comportamento existente de fechamento, Cancelar e Esc continua devolvendo foco diretamente ao gatilho, sem depender desse marcador. A regra de preservar foco após salvar/recarregar foi acrescentada ao `AGENTS.md`.

### 18.3 — Arquivos e alcance

A lógica foi implementada somente no script compartilhado. Para carregar a atualização após recarregar a página, as doze telas que o utilizam passaram a referenciar `modal-crud.js?v=20261107-4`:

- Detalhes de Pessoa (`detalhe.html`), Ata, Disciplina, Módulo, Oferta de Módulo e Submódulo, em `cadastros/templates/cadastros/`.
- Listas de Atas, Disciplinas, Módulos, Ofertas de Módulo e Submódulos, no mesmo diretório.
- `atribuicao/templates/atribuicao/gerenciar_turma.html`.

Também foram atualizados o `AGENTS.md` e este diário. Os templates receberam apenas a atualização da versão do script neste lote; formulários, regras de negócio, URLs das ações, salvamento e permissões não foram alterados.

### 18.4 — Verificação

- `manage.py check`: sem problemas identificados.
- Suíte existente: **52 passed in 2.82s**.
- `node --check` do script e revisão do diff: aprovados para esta alteração.
- Simulação em memória com Node/`vm`: retorno ao gatilho exato após salvamento e recarga, inclusive quando há dois botões com a mesma URL; consumo único do marcador; não aplicação em página ou filtro diferente; comportamento com gatilho ausente, JSON inválido e armazenamento bloqueado. Todos os cenários passaram.

A simulação verifica a lógica, sem reproduzir o algoritmo nativo de Tab ou a rolagem de um navegador real. Nenhuma nova dependência foi adicionada.

### 18.5 — Teste manual pendente

1. Recarregar uma das telas para obter o script atualizado.
2. Usar Tab até “Adicionar Item”, abrir com Enter, preencher e salvar: após atualizar a página, o foco deve estar novamente em “Adicionar Item”.
3. Pressionar Tab e conferir a continuidade a partir desse ponto; repetir com “Editar”.
4. Conferir também Cancelar, Esc e erro de validação, mantendo os comportamentos de foco anteriores.
5. Repetir o fluxo em outro modal CRUD e conferir foco visível com zoom de 200%.

---

## 19. Continuidade do foco nas páginas principais — menu lateral

### 19.1 — Confirmação e novo relato

O responsável confirmou que o retorno de foco dos popups implementado na seção 18 funcionou. Em seguida, identificou a mesma perda de posição na navegação entre páginas principais: abrir “Secretaria” com Espaço e entrar em “Disciplinas” com Enter fazia a próxima navegação por Tab começar novamente no início da página.

A decisão foi estender o padrão de continuidade ao menu lateral de todas as páginas que herdam `base.html`: ao concluir a navegação, manter o foco no link acionado e seu grupo expandido. O funcionamento dos popups permanece como descrito na seção 18.

### 19.2 — Implementação global

`static/global/js/sidebar.js` registra antes da navegação normal o destino do link e o índice do grupo de origem, em um marcador de `sessionStorage` exclusivo do menu. Na página de destino, verifica o endereço, localiza o mesmo link no mesmo grupo, expande esse grupo, sincroniza `aria-expanded` e devolve o foco ao link.

Assim, o cenário “Secretaria → Disciplinas” deve continuar a partir de “Disciplinas” no próximo Tab/Shift+Tab, sem exigir percorrer novamente o cabeçalho. A posição é identificada pelo link e pelo grupo, evitando confusão quando URLs iguais aparecem em grupos diferentes.

O marcador é consumido uma única vez e não é aplicado em outro endereço. Cliques modificados para abrir outra aba/janela, botão secundário e destinos externos não registram retorno de foco. O script não cancela o comportamento nativo dos links nem redefine Enter ou Espaço. Sem armazenamento disponível, a navegação continua funcionando, mas o retorno entre páginas não é aplicado.

Não foi acrescentada mudança de foco automática em toda visita: acessos diretos sem marcador mantêm a navegação inicial normal e o link de salto. Esta implementação cobre o menu persistente na base; ela não tenta focalizar controles de uma página anterior que não existem no destino.

### 19.3 — Arquivos e verificações

Arquivos alterados nesta etapa:

- `static/global/js/sidebar.js` — persistência e restauração do link e grupo.
- `templates/base.html` — versão de carregamento do script `?v=20261107-5`.
- `AGENTS.md` — padrão global de continuidade de foco no menu lateral.
- Este diário.

Verificações:

- `manage.py check`: sem problemas identificados.
- Suíte existente: **52 passed in 3.04s**.
- `node --check static/global/js/sidebar.js`: aprovado.
- Diff de `sidebar.js` e `AGENTS.md`: sem erros de whitespace; o aviso anterior em outra linha da base continua fora desta alteração.
- Simulação em memória com Node/`vm`: foco no link de destino e grupo correto expandido, inclusive com URLs repetidas; sincronização do accordion/ARIA; consumo único; preservação de cliques para nova aba; endereço diferente; registro inválido e armazenamento bloqueado. Cenários aprovados.

Não houve alteração de regras de negócio, permissões, rotas ou critérios do servidor para identificar itens ativos. A expansão adicional no cliente preserva o grupo de onde a navegação partiu.

### 19.4 — Validação manual pendente

1. Recarregar a página para carregar a versão atual de `sidebar.js`.
2. Usar Tab até “Secretaria”, abrir com Espaço, chegar a “Disciplinas” e acionar Enter.
3. Na página nova, confirmar “Secretaria” aberto e “Disciplinas” com foco; usar Tab/Shift+Tab e conferir a continuidade.
4. Repetir entre outros grupos/páginas e conferir foco visível com zoom de 200%.
5. Confirmar que o retorno ao botão de origem após salvar/cancelar popup continua funcionando.

A verificação automatizada usa DOM simplificado e não substitui essa confirmação em navegador real.

---

## 20. Refinamento da navegação — entrada direta nos controles da tela

O responsável refinou o comportamento desejado: selecionar um item do submenu significa entrar na tela desse item. Portanto, o foco deve ir ao primeiro campo ou botão dessa tela, em vez de retornar ao link do menu e seguir para o próximo submenu. Esta decisão substitui o destino de foco estabelecido na seção 19, mantendo a preservação do grupo expandido.

### 20.1 — Comportamento implementado

Após a navegação originada no menu, `sidebar.js` mantém o grupo aberto e procura no `main#conteudo-principal` o primeiro controle disponível na ordem do documento: input visível, select, textarea, button ou link explicitamente marcado com papel de botão. Controles ocultos, invisíveis, desabilitados, em área `inert` ou fora da sequência de Tab são ignorados.

Se não houver controle elegível, o próprio `main` recebe foco usando o `tabindex="-1"` já existente. Não são adicionados valores positivos de tabindex nem alterada a ordem dos controles. Links comuns de navegação, como “Voltar”, não são escolhidos antes dos campos/botões.

Exemplo esperado: Secretaria → Disciplinas leva o foco ao botão “+ Nova Disciplina”. Em uma tela com filtros, ele vai ao primeiro campo ou botão disponível. O próximo Tab continua a partir desse ponto na tela.

O marcador continua sendo consumido uma única vez e só vale para o endereço de destino. Acesso direto à página, sem navegação registrada no menu, mantém a entrada normal. O retorno ao gatilho após salvar ou fechar popups permanece inalterado e separado deste comportamento.

### 20.2 — Arquivos e verificações

- `static/global/js/sidebar.js`: seleção e foco do primeiro controle disponível no conteúdo principal.
- `templates/base.html`: carregamento de `sidebar.js?v=20261107-6`.
- `AGENTS.md`: atualização do padrão global de foco para navegação pelo menu.
- Este diário: registro da nova decisão, substituindo o retorno ao link do submenu.

Resultados:

- `manage.py check`: sem problemas identificados.
- Suíte existente: **52 passed in 2.85s**.
- Sintaxe JavaScript e diff de `sidebar.js`/`AGENTS.md`: aprovados.
- Simulação em memória com Node/`vm`: primeiro campo/botão elegível, manutenção do grupo aberto, destino alternativo no `main`, consumo único do marcador, endereço diferente e exclusão de controles ocultos/invisíveis/desabilitados/inert/com tabindex negativo. Cenários aprovados.

Não houve alteração de regras de negócio, validações, rotas, permissões ou comportamento de salvamento.

### 20.3 — Validação manual pendente

Recarregar a página; navegar com Tab até Secretaria; abrir com Espaço e entrar em Disciplinas com Enter. Confirmar que o foco está em “+ Nova Disciplina” e que o próximo Tab segue nos controles da tela. Repetir em uma tela com campos/filtros e em uma página sem controles (foco no `main`), além de conferir que o retorno de foco dos popups continua funcionando. Conferir foco visível, leitor de tela e zoom de 200% no navegador real.

---

## 21. Foco dos botões — anel duplo de alto destaque

O responsável identificou que o contorno azul sobre botões azuis tinha pouco destaque visual e solicitou um padrão com duas sombras concêntricas: branca de 2px e escura de 5px, aplicado em `:focus-visible`.

O CSS compartilhado passou a usar:

```css
outline: none;
box-shadow:
  0 0 0 2px var(--foco-anel-interno),
  0 0 0 5px var(--foco-anel-externo);
```

As cores estão centralizadas no `:root`: `--foco-anel-interno: #ffffff` e `--foco-anel-externo: #111827`. A antiga variável `--botao-foco` foi substituída por essas duas variáveis, permitindo adaptações de tema sem cores literais nas regras dos controles.

O padrão atende botões nativos (inclusive os grupos do menu lateral e controles dos modais), inputs de ação e links com aparência/papel de botão já selecionados pelo CSS compartilhado. A regra específica de foco dos títulos da sidebar foi removida para não substituir o anel duplo; os links comuns dos submenus mantêm seu foco próprio.

Em modo de cores forçadas, a regra usa outline de 3px na cor de sistema `Highlight`, pois box-shadow pode ser suprimido pelo navegador nesse modo. Não foram alterados hover, cores normais dos botões ou eventos de teclado.

Arquivos alterados: `static/global/css/base.css`, `templates/base.html` (CSS `?v=20261107-4`), `AGENTS.md` (padrão de foco atualizado) e este diário.

Verificação: `manage.py check` sem problemas, **52 passed in 2.95s**, revisão das regras e `git diff --check` de `base.css`/`AGENTS.md` sem erros. As regras de negócio e permissões não foram alteradas.

Falta confirmar visualmente, após recarregar a página, o anel de foco com Tab/Shift+Tab em Salvar, Cancelar, Nova Disciplina, grupos do menu e controles dos modais. Conferir zoom de 200%, eventuais cortes do anel nas bordas dos contêineres e o outline alternativo em cores forçadas.

---

## 22. Botão de fechar dos popups — ícone invisível por herança de cor

O responsável enviou uma captura de “Novo SubMódulo” indicando ausência do botão de fechar. A região marcada corresponde ao canto superior direito. A inspeção confirmou o controle `#modal-crud-fechar` com o caractere `×` nos doze contêineres de modal CRUD.

A causa está no CSS: a regra genérica de `button` define texto branco, e o botão de fechar usa fundo transparente por estilo inline, sobre a caixa branca do modal. Sem cor própria, o ícone fica branco sobre branco.

A correção foi aplicada no componente compartilhado, sem repetir alterações nos doze templates. `#modal-crud-fechar` agora usa `--modal-fechar-texto` (associada a `--cor-texto`) e, em hover, `--modal-fechar-texto-hover` (associada a `--cor-primaria`). As variáveis foram definidas no `:root`. O botão conserva sua posição, seu nome acessível e o foco de anel duplo.

Arquivos alterados: `static/global/css/base.css`, `templates/base.html` (CSS `?v=20261107-5`) e este diário. Nenhum evento, regra de negócio ou permissão foi alterado.

Verificação: presença dos controles confirmada nos doze templates; `manage.py check` sem problemas; **52 passed in 2.78s**; checagem de whitespace de `base.css` sem erros. A confirmação foi feita por inspeção de código e da captura fornecida, sem nova interação automatizada com o navegador.

Falta recarregar a página, abrir um popup e confirmar visualmente o “×” no canto superior direito, incluindo hover e foco por Tab, e conferir seu fechamento por teclado.

---

## 23. Consolidação da sessão e próximo lote

Por solicitação do responsável, foi conferido o registro de toda a sequência de trabalho neste diário. As seções 1 a 22 preservam o contexto, decisões, implementações, resultados e revisões de comportamento; este fechamento consolida o estado atual e substitui os resumos intermediários para leitura do resultado final da sessão.

### 23.1 — Entregas consolidadas

| Frente | Resultado atual | Evidência / limite |
|---|---|---|
| Auditoria global | Base, menu, fragmentos, modais, tabelas, CSS/JS e runner mapeados | Inspeção estática inicial |
| Salto para conteúdo | Link no início da página e destino focalizável no `main` | Funcionamento manual confirmado pelo responsável |
| Menu lateral | Nome, associação de controles, estados expandidos e página atual | Validação inicial confirmada; foco refinado posteriormente |
| Navegação para telas | Ao entrar pelo submenu, foco no primeiro campo/botão disponível; sem controles, no `main` | Padrão final da seção 20; confirmação no navegador ainda pendente |
| Formulários | Componentes compartilhados aplicados em Disciplina, Módulo, Submódulo e Conteúdo Programático | Piloto aprovado; expansão e refinamentos têm verificações automatizadas e testes manuais indicados |
| Erros | Caixa rosada com ícone decorativo, mensagem completa junto ao campo e resumo com um link por campo | Visual aprovado; detalhes das associações verificados no HTML |
| KP duplicado | Erro associado ao campo, dados mantidos e possibilidade de corrigir e salvar | Reprodução da falha anterior e oito cenários de regressão |
| Cancelar | Controle nativo com fechamento por JS e alternativa GET sem salvamento | Testes de renderização e simulações aprovados |
| Botões | Geometria comum, cores em variáveis e Cancelar vermelho com texto claro | Contrastes calculados nas seções 15 e 16 |
| Foco visível | Anel duplo claro/escuro e alternativa para cores forçadas | CSS compartilhado; revisão visual final pendente |
| Foco dos popups | Retorno ao gatilho ao fechar e após salvar/recarregar | Retorno após salvar confirmado pelo responsável |
| Fechar popup | “×” com cor própria, corrigindo branco sobre branco | Correção compartilhada nos doze contêineres; confirmação visual pendente |
| Padrões futuros | Regras incorporadas ao `AGENTS.md` | Reutilização de componentes, variáveis e padrões de foco |
| Tabelas — piloto de Disciplinas | Cabeçalhos, identificação da tabela e contexto dos botões implementados | Seção 24; funcionamento confirmado pelo responsável |

### 23.2 — Verificação e evidências para o PI

A suíte passou de **44 para 52 testes**, com os oito casos parametrizados de regressão do Conteúdo Programático. Na execução mais recente: **52 aprovados em 2,78s**, e `manage.py check` sem problemas identificados. Os testes, as renderizações e simulações estão registrados nas respectivas etapas, sem apresentá-los como substitutos de testes no navegador ou de uma auditoria WCAG completa.

Para a apresentação e o relatório final, a sessão documenta uma evolução verificável: problemas de repetição de navegação por teclado, mensagens duplicadas, falha não tratada de KP e inconsistências visuais foram tratados em componentes compartilhados, com testes e preservação da regra de unicidade existente. Não foram medidas redução de tempo de tarefa ou conformidade integral; tais resultados não devem ser afirmados sem avaliação adicional.

Os registros diferenciam confirmações do responsável e verificações do agente. A tentativa de automação do Edge foi interrompida pela ferramenta por não conseguir identificar a URL com segurança, conforme seção 15; não foi usada como evidência de teste visual concluído.

Nenhuma migration, nova dependência, regra de autenticação ou permissão foi criada. A correção de validação em forms/views tratou a restrição de unicidade já existente, sem redefinir regras acadêmicas. As demais mudanças ficaram em apresentação, interação e documentação.

Esta consolidação alterou somente o diário, sem nova execução da suíte ou alteração de código.

### 23.3 — Próximo passo proposto: tabelas, começando por Disciplinas

Antes do próximo lote, confirmar no navegador os últimos ajustes de foco e o “×” de fechar. Em seguida, iniciar um piloto na tabela de `cadastros/templates/cadastros/lista_disciplinas.html`:

1. Conferir os cabeçalhos e incluir `scope="col"` onde apropriado.
2. Substituir o cabeçalho vazio da coluna de controles por “Ações”.
3. Avaliar uma legenda (`caption`) que ajude a identificar a tabela sem repetir conteúdo desnecessário.
4. Dar contexto aos controles de cada linha, preservando rótulos visuais, URLs e seletores existentes.
5. Conferir teclado, leitura dos cabeçalhos, foco e uso com zoom de 200%, mantendo o padrão visual aprovado.

Após revisar o diff, executar checks/testes relevantes e registrar o resultado neste diário. Somente depois da validação do piloto, ampliar o padrão para outras listagens. Nenhuma implementação do lote de tabelas foi realizada nesta consolidação.

---

## 24. Lote de tabelas — piloto na lista de Disciplinas

### 24.1 — Inspeção e escopo

O responsável autorizou iniciar o próximo lote. Foi escolhida `cadastros/templates/cadastros/lista_disciplinas.html`, conforme a proposta da seção 23. A página herda a base global e usa o script e o contêiner comuns dos modais CRUD.

A tabela já apresentava `thead`, `tbody`, cabeçalhos `th` e situação em texto (Ativa/Inativa), mas não explicitava o escopo dos cabeçalhos. A coluna de ações estava sem nome, e os botões de linhas diferentes apresentavam nomes acessíveis genéricos “Inativar”/“Reativar”.

### 24.2 — Alterações

- Os cinco cabeçalhos receberam `scope="col"`.
- O cabeçalho vazio foi substituído por **“Ações”**.
- Foi adicionada a legenda nativa `caption`: “Disciplinas cadastradas, cargas horárias e situação”. A classe reutilizável `.visualmente-oculto` mantém essa identificação disponível para tecnologias assistivas sem acrescentar uma linha visual à tabela.
- Cada botão de situação recebeu nome acessível que inclui a ação visível, o nome e a sigla da disciplina: por exemplo, “Inativar disciplina Matemática (MAT)”. O texto visível dos botões foi preservado, e o nome acessível começa pela mesma ação.

Foram mantidos dados, ordem das colunas, links, URLs de ação, seletores, classes dos botões, modal e mensagem de lista vazia. Não foram adicionadas paradas de Tab na tabela ou papéis ARIA redundantes. A única alteração visual intencional na tabela é o título da coluna “Ações”.

Arquivos deste lote: `cadastros/templates/cadastros/lista_disciplinas.html`, `static/global/css/base.css` (utilitário de conteúdo visualmente oculto), `templates/base.html` (CSS `?v=20261107-6`) e este diário.

### 24.3 — Verificações

| Verificação | Resultado |
|---|---|
| `manage.py check` | Sem problemas identificados |
| Suíte existente | **52 passed in 2.97s** |
| HTML renderizado — disciplinas ativas e inativas | Aprovado |
| HTML renderizado — somente disciplina inativa | Aprovado |
| HTML renderizado — lista vazia | Aprovado |
| Revisão do diff e checagem de whitespace da listagem e CSS | Sem erros neste lote |

A verificação em memória usou `render_to_string`, `RequestFactory`, `HTMLParser` e instâncias não salvas de Disciplina. Conferiu cinco cabeçalhos com escopo, legenda, nomes acessíveis de Inativar/Reativar, nomes com acentos e `&`, preservação dos destinos de detalhe/ação, classes e tipo dos botões, além da mensagem de lista vazia. Não houve gravação no banco nem criação de nova dependência.

A primeira tentativa do script pontual falhou numa comparação literal com acentos devido à conversão de caracteres ao enviar o código pelo PowerShell. A execução foi repetida com escapes Unicode explícitos e passou, sem modificar o template para contornar a conferência. A suíte Django não apresentou falhas.

Nenhuma regra de negócio, view, form, model, permissão ou mecanismo de ativação/inativação foi alterado. Os testes existentes e as conferências de HTML não substituem avaliação em navegador real.

### 24.4 — Validação manual e próximo passo

1. Recarregar a lista de Disciplinas e conferir que o layout permanece familiar, com a coluna “Ações” identificada.
2. Navegar com Tab/Shift+Tab pelos links de detalhe e botões; abrir uma confirmação de Inativar/Reativar e conferir o retorno de foco ao fechar, sem precisar confirmar uma mudança de situação apenas para testar.
3. Com leitor de tela, conferir a identificação da tabela, a leitura dos cabeçalhos e o nome da disciplina nos botões de ação.
4. Conferir zoom de 200%, quebra de textos e acesso à última coluna. Caso haja corte ou rolagem inadequada, ajustar em uma etapa pontual após essa observação.
5. Após aprovação do piloto, ampliar o padrão para outras listagens simples, mantendo o visual e os componentes existentes.

### 24.5 — Confirmação do responsável

Após a entrega e a orientação de validar teclado, leitor de tela e zoom de 200%, o responsável informou: **“ok - tudo funcionando”**. A validação manual do piloto de Disciplinas foi considerada concluída com base nesse relato, sem nova interação de navegador pelo agente.

O lote está concluído: implementação, checks, 52 testes aprovados e confirmação de funcionamento pelo responsável registrados. Esta atualização alterou apenas o diário, sem alteração de código ou nova execução da suíte.

Próximo lote proposto: aplicar o padrão aprovado às listas de Módulos e Submódulos, em uma expansão pequena, preservando estilos, rotas, seletores e regras de negócio.

---

## 25. Expansão autorizada — todas as tabelas dos templates do aplicativo

### 25.1 — Autorização e inventário

Após aprovar o piloto de Disciplinas, o responsável autorizou: **“Pode aplicar em todos”**. O escopo foi ampliado para as 36 tabelas encontradas em 23 templates de `cadastros`, `atribuicao` e `nucleo`, incluindo listagens, detalhes, históricos, gestão de alunos e tabelas preenchidas pelos formsets dinâmicos.

A tabela de Disciplinas já estava no padrão aprovado e não precisou de nova alteração. Foram atualizados os outros 22 templates, abrangendo 35 tabelas. A inspeção distinguiu tabelas de coleção (cabeçalhos de coluna) e tabelas com vários pares de rótulo e valor na mesma linha.

### 25.2 — Padrão aplicado e preservações

- Todas as 36 tabelas possuem uma legenda nativa `caption`, reutilizando `.visualmente-oculto` para preservar o layout aprovado. Nas páginas com várias tabelas ou funções, a legenda inclui o contexto pertinente.
- Cabeçalhos de listagens, históricos e formsets usam `scope="col"`.
- Cabeçalhos de colunas antes vazios passaram a indicar **“Ações”**.
- Nos cinco detalhes com dados apresentados em pares, foram criadas 23 associações explícitas: cabeçalho com ID único e `scope="row"`, célula de valor com `headers` apontando para aquele cabeçalho. Isso distingue, por exemplo, o valor de Situação do valor de Carga Horária na mesma linha.
- Foram acrescentados nomes acessíveis contextuais a 23 controles/links repetidos: ativar/inativar, editar, excluir, desvincular, encerrar vínculo, gerenciar alunos/contratos e acessar ofertas, conforme a entidade da linha. O nome acessível preserva a ação/texto visível.
- O `AGENTS.md` recebeu o padrão para futuras tabelas, incluindo uso do utilitário existente e associações explícitas quando houver vários pares por linha.

Não foram criados componentes visuais alternativos, nova biblioteca, paradas de Tab artificiais ou papéis de grid/tabela redundantes. Os textos visíveis dos controles foram preservados. As novas legendas não acrescentam linhas visíveis; a mudança visual intencional é a identificação das colunas “Ações” antes vazias.

Foram preservados dados, ordem das colunas, condições e loops Django, campos e gerenciamento dos formsets, atributos usados pelo JavaScript, classes, URLs e métodos de envio. A atualização não modificou ativação/inativação, exclusão, contratos, matrícula, aprovação ou encerramento. Não houve alteração de autenticação ou permissões.

### 25.3 — Arquivos alterados nesta expansão

Em `cadastros/templates/cadastros/`:

- `detalhe.html`, `detalhe_ata.html`, `detalhe_disciplina.html`, `detalhe_modulo.html`, `detalhe_oferta_modulo.html` e `detalhe_submodulo.html`.
- `form_pessoa.html` (somente as quatro tabelas de registros adicionados pelos formsets).
- `lista.html`, `lista_atas.html`, `lista_modulos.html`, `lista_ofertas_modulo.html`, `lista_submodulos.html` e `lista_turmas.html`.

Em `atribuicao/templates/atribuicao/`:

- `atribuicao.html`, `contratos.html`, `dashboard.html`, `gerenciar_turma.html`, `horarios.html` e `registro_instrucao.html`.

Em `nucleo/templates/nucleo/`:

- `auditoria_interna.html`, `registro_instrucao.html` e `treinamento.html`.

Também foram atualizados o `AGENTS.md` e este diário. Nenhum CSS, JavaScript, form, view, model, migration ou dependência foi alterado neste lote.

### 25.4 — Verificações e resultados

| Verificação | Resultado |
|---|---|
| `manage.py check` | Sem problemas identificados |
| Suíte completa existente | **52 passed in 2.83s** |
| Compilação dos templates com tabelas | **23 templates aprovados** |
| Renderização de todas as tabelas em quatro estados | **144 renderizações aprovadas** |
| Nomes acessíveis renderizados nas ações/links | **67 ocorrências conferidas** nos cenários exercitados |
| Comparação estrutural dos 22 arquivos com o início deste lote | Apenas legendas, associações de cabeçalhos e nomes acessíveis alterados |
| `git diff --check` restrito aos 22 templates | Sem erros |

A renderização foi executada em memória com Django, `HTMLParser` e objetos sintéticos, sem acesso de escrita ao banco. Os estados incluem dados preenchidos, variações de ativo/inativo e situação da turma, além de coleções vazias. As quatro tabelas dos formsets permanecem com `tbody` inicialmente vazio, como antes.

Foram verificados: uma legenda por tabela, escopo em todos os cabeçalhos, ausência de cabeçalhos vazios, IDs sem duplicação no bloco de tabela, resolução de cada `headers` para um ID presente e inclusão do texto visível no nome acessível dos controles rotulados. A compilação abrangeu as páginas completas; as renderizações pontuais exercitaram os blocos de tabela e seus contextos sintéticos.

A comparação com o estado anterior removeu apenas os acréscimos de acessibilidade e normalizou whitespace para conferir que dados, expressões e contratos existentes não foram modificados. Não foram executadas ações reais de exclusão, matrícula ou encerramento para essa avaliação.

A checagem ampla de todos os templates voltou a apontar o whitespace já registrado no fragmento de Disciplina, fora desta expansão. A checagem específica dos arquivos modificados neste lote passou. Os avisos anteriores não foram tratados como regressões deste lote.

### 25.5 — Validação manual e limites

O piloto de Disciplinas já foi validado pelo responsável. As demais telas ainda precisam de confirmação no navegador, em especial:

1. Listagens de Módulos, Submódulos, Ofertas, Turmas, Atas e Pessoas: leitura dos cabeçalhos e contexto dos controles por leitor de tela.
2. Detalhes de Disciplina/Módulo/Submódulo/Oferta/Ata: associação de cada rótulo ao valor correto nas linhas com vários pares.
3. Gestão de alunos e históricos de Pessoa: ordem de Tab, nomes das ações e abertura/fechamento de modais, sem confirmar operações destrutivas apenas para testar acessibilidade.
4. Cadastro de Pessoa: adicionar linhas nos quatro formsets e conferir alinhamento dos dados com os cabeçalhos.
5. Tabelas de contratos, horários, instruções, auditoria e treinamento: leitura, conteúdo vazio e zoom de 200%.

O lote não reescreveu os layouts ou corrigiu possíveis limitações anteriores de responsividade, contraste de estilos inline ou ações ainda não implementadas. Por exemplo, o atalho de planejamento no dashboard já apontava para `#`, e o botão Gerenciar de contratos não possuía ação configurada; apenas seus nomes acessíveis foram contextualizados. Esses comportamentos permanecem como antes.

As verificações automatizadas não certificam conformidade WCAG de todas as páginas nem substituem testes com leitor de tela e zoom. Após essa validação, o próximo lote proposto é concluir a acessibilidade dos modais compartilhados, especialmente semântica de diálogo e contenção de foco, reutilizando o comportamento de entrada/retorno de foco já implementado.

---

## 26. Lote de modais compartilhados — identificação, isolamento e teclado

### 26.1 — Escopo e componente reutilizável

O responsável autorizou o próximo lote após a expansão das tabelas. A inspeção confirmou doze cópias da estrutura do modal CRUD. Elas foram substituídas pelo include `templates/includes/modal_crud.html`, preservando os IDs `modal-crud-overlay`, `modal-crud-caixa`, `modal-crud-fechar` e `modal-crud-corpo`, os estilos existentes e os contratos de carregamento/envio.

O include foi aplicado aos seis detalhes e cinco listas de `cadastros` que já usavam o modal e a `atribuicao/gerenciar_turma.html` (as mesmas doze páginas enumeradas na seção 18). Todas carregam o script com `?v=20261107-7`.

### 26.2 — Comportamento implementado

- A caixa recebe `role="dialog"`, `aria-modal="true"`, destino de foco próprio e nome acessível inicial.
- Durante a abertura, o nome usa o rótulo do botão que acionou o popup. Após carregar o formulário, o diálogo passa a ser identificado por seu título, via `aria-labelledby`. O título mantém seu ID quando já possui um; caso contrário, recebe `modal-crud-titulo`.
- Tab no último controle retorna ao primeiro; Shift+Tab no primeiro retorna ao último. Controles ocultos, desabilitados, negativos na sequência de Tab ou dentro de área `inert` não são incluídos. Se não houver controles disponíveis, a caixa recebe foco.
- Uma proteção adicional redireciona foco que seja movido para fora do diálogo enquanto ele está aberto.
- Os ramos de conteúdo ao redor do popup ficam `inert` enquanto ele está aberto, incluindo cabeçalho, menu e conteúdo de fundo. O próprio caminho até o popup permanece ativo. Ao fechar, cada ramo recupera o estado que possuía antes da abertura, inclusive se já estava inativo por outro motivo.
- Uma região de status informa carregamento e salvamento, acompanhada de `aria-busy` no corpo do formulário.
- Foram preservados o foco inicial, o foco no campo inválido, Esc, fechamento por “×”, clique no fundo, Cancelar e retorno ao gatilho, inclusive após salvar/recarregar a página.
- O cancelamento delegado também reconhece os IDs de controles de matrícula e planejamento já existentes, para centralizar a liberação do fundo e o retorno de foco sem depender de scripts inline inseridos junto ao HTML.
- Respostas antigas de carregamento/envio são ignoradas se o popup foi fechado ou reaberto para outra operação, evitando substituir o formulário atual com conteúdo de uma abertura anterior.

Não houve alteração de regras acadêmicas, validações, URLs, permissões ou mecanismo de salvamento. Não foram adicionados campos aos formulários nem nova biblioteca. Os popups de avisos criados por `form-dinamico.js` continuam fora deste componente e permanecem para o lote de conteúdo dinâmico.

### 26.3 — Arquivos alterados

- `templates/includes/modal_crud.html` — novo componente compartilhado.
- Doze templates consumidores do modal, em `cadastros/templates/cadastros/` e `atribuicao/templates/atribuicao/gerenciar_turma.html` — substituição da marcação repetida pelo include e atualização da versão do script.
- `cadastros/static/cadastros/js/modal-crud.js` — nome, estados, isolamento, contenção e recuperação de foco.
- `cadastros/tests/js/modal-crud.test.cjs` — oito testes de regressão de interação, executados com recursos nativos do Node já disponível no ambiente.
- `AGENTS.md` — padrão de reutilização e comportamento dos modais.
- Este diário.

Nenhum CSS, form, view, model ou migration foi alterado neste lote.

### 26.4 — Verificações e resultados

| Verificação | Resultado |
|---|---|
| `manage.py check` | Sem problemas identificados |
| `python -m pytest -p no:cacheprovider -q --tb=short` pelo ambiente virtual | **52 passed in 2.90s** |
| `node --test cadastros/tests/js/modal-crud.test.cjs` | **8 testes aprovados** |
| `node --check cadastros/static/cadastros/js/modal-crud.js` | Sintaxe válida |
| Compilação dos templates consumidores | Doze templates aprovados |
| Renderização do include | Diálogo nomeado, IDs únicos, botão de fechar nomeado e região de status presentes |
| Revisão e checagem do diff restrita ao lote | Sem erros de whitespace |

Os testes Node são independentes da suíte pytest: não são apresentados como 60 testes Django. Usam `node:test`, `assert`, `vm` e um DOM simplificado, sem instalação de pacotes. Cobrem abertura/nome, estados de carregamento, preservação de `inert` anterior, Tab/Shift+Tab nas bordas e no meio, controles indisponíveis, foco fora do popup, erro de validação, cancelamento/clique no fundo, resposta antiga, falha HTTP e retorno ao gatilho após salvamento.

Os testes existentes e as verificações de renderização continuam aprovados. Os testes JavaScript verificam a lógica dos handlers, mas não simulam integralmente o navegador, o algoritmo nativo de Tab, os widgets de rádio/select ou os anúncios de leitor de tela.

### 26.5 — Validação manual pendente

1. Recarregar a página e abrir “Nova Disciplina” por teclado; conferir título, entrada de foco e anúncio do diálogo.
2. Percorrer os controles com Tab até o fim e Shift+Tab até o início: o foco deve circular dentro do popup, sem ir ao menu ou à página de fundo.
3. Fechar por Esc, “×” e Cancelar quando disponível; conferir liberação da página e retorno ao gatilho.
4. Enviar um KP repetido e conferir foco no campo, anúncio de erro, navegação pelo resumo e permanência do Tab no popup.
5. Corrigir e salvar; conferir atualização e retorno ao botão que abriu o popup.
6. Abrir uma confirmação de Inativar/Excluir e conferir o teclado e fechamento, sem efetivar mudança destrutiva apenas para testar.
7. Conferir um formulário longo, um com rádios/selects e os controles de cancelamento em Gestão de Alunos; verificar rolagem, foco visível e zoom de 200%.

O lote está implementado e passou nas verificações automatizadas; a validação no navegador e com leitor de tela continua pendente. Após ela, o próximo lote proposto é conteúdo dinâmico (avisos dos formsets e mensagens de CEP/CPF), mantendo os padrões aprovados.

### 26.6 — Confirmação do responsável

Após a entrega e as orientações de teste, o responsável informou **“ok - tudo funcionando”**. A validação manual do lote de modais foi considerada concluída com base nesse relato, sem nova execução de navegador pelo agente.

Lote concluído: componente compartilhado aplicado aos doze modais CRUD, 52 testes Django e oito testes JavaScript aprovados, check Django sem problemas e confirmação do responsável registrada. Esta atualização alterou somente o diário, sem nova alteração de código ou repetição dos testes.

Próximo lote proposto: acessibilidade do conteúdo dinâmico, começando pelos avisos dos formsets e pelas mensagens de consulta/preenchimento de CEP e CPF. Preservar APIs, critérios de validação, dados preenchidos e o padrão visual aprovado.

---

## 27. Conteúdo dinâmico — avisos, formsets e consultas de CEP/CPF

### 27.1 — Inspeção e decisões

Após a confirmação dos modais, o responsável autorizou este lote. Foram inspecionados `form-dinamico.js`, `buscar-cep.js`, `buscar-cpf.js` e a renderização de `form_pessoa.html`.

O popup de avisos dos formsets era construído separadamente, não tratava Esc nem devolvia foco. Falhas de consulta eram informadas apenas no console, e a inclusão de linhas não era anunciada. A decisão foi reutilizar o modal já validado e acrescentar feedback junto aos campos de consulta, mantendo os gatilhos e contratos existentes.

### 27.2 — Avisos no componente compartilhado

`form-dinamico.js` passou a solicitar os avisos pelo evento cancelável `modal-crud-aviso`. `modal-crud.js` trata o evento usando o mesmo diálogo, fundo inativo, contenção de Tab, Esc e retorno ao controle de origem. O aviso tem título “Aviso”, descrição associada à mensagem e botão “OK” no padrão aprovado. As mensagens de campos incompletos, edição indisponível, data futura e menor de idade foram preservadas.

O Cadastro de Pessoa agora inclui o modal compartilhado e seu script. Quando esse componente não trata o evento, o código mantém `window.alert()` como alternativa nativa, evitando perder o aviso em caso de falha no carregamento do componente.

Não foram alterados os critérios de data, maioridade, habilitação de campos por categoria ou permissão de edição. O aviso de menor de idade continua informativo; a validação definitiva permanece no servidor.

### 27.3 — Formsets

Cada bloco recebe uma região de status visualmente oculta. Ao adicionar uma linha, ela informa a inclusão e o total de registros da tabela. O foco vai ao primeiro campo da próxima linha, permitindo continuar o preenchimento sem voltar ao início.

A lógica existente de obrigatoriedade, clonagem de valores, renomeação de `name`/`id`/`for`, manutenção dos selects e atualização de `TOTAL_FORMS` foi preservada. A ordem dos blocos e as regras de exibição por categoria permanecem iguais.

### 27.4 — Consultas acessíveis e não bloqueantes

Foi criado `feedback-consulta.js`, compartilhado por CEP e CPF, para associar instruções e status ao campo e renderizar mensagens com segurança via `textContent`. A associação acrescenta referências a `aria-describedby` sem apagar ajuda ou erros anteriores.

`form_pessoa.html` possui regiões de status persistentes junto aos campos. O ID já usado `aviso-pessoa-encontrada` foi preservado como região de CPF; CEP recebeu `status-consulta-cep`. Ambas usam `role="status"` e `aria-atomic="true"`. Pequenas instruções esclarecem os gatilhos:

- CEP continua consultado ao sair do campo (`blur`), com oito dígitos normalizados, pela mesma URL `/api/cadastros/cep/<cep>/`.
- CPF continua consultado com Enter, sem submeter o cadastro, com onze dígitos normalizados, pela mesma URL `/api/cadastros/pessoa-por-cpf/<cpf>/`.

São informados carregamento, preenchimento, resultado não encontrado e falhas. Erros usam a caixa rosada e o ícone decorativo aprovados. Mensagens informativas reutilizam as cores do aviso de CPF já existente, agora em variáveis de tema: `--consulta-fundo`, `--consulta-borda` e `--consulta-texto`. O contraste calculado é **4,96:1**.

Os resultados não movem o foco. Nas falhas ou no CPF não encontrado, os dados manuais permanecem disponíveis e o usuário pode continuar o cadastro. O mapa de campos preenchidos por CPF e os quatro campos preenchidos por CEP foram preservados. O comprimento incompleto gera apenas orientação de consulta; não redefine a validação do formulário.

Cada consulta possui um identificador de execução e verifica o valor atual do campo antes de aplicar a resposta. Assim, uma resposta anterior não sobrescreve uma consulta mais recente ou uma entrada já alterada. Não há gravação de CPF/CEP no armazenamento de foco ou no diário.

### 27.5 — Arquivos alterados

- `cadastros/static/cadastros/js/feedback-consulta.js` (novo).
- `cadastros/static/cadastros/js/buscar-cep.js`, `buscar-cpf.js`, `form-dinamico.js` e `modal-crud.js`.
- `cadastros/templates/cadastros/form_pessoa.html` — instruções, status, include do modal e ordem/versionamento dos scripts (`20261107-8`).
- `static/global/css/base.css` — estilo informativo e variáveis de cor; `templates/base.html` carrega CSS `20261107-7`.
- `cadastros/tests/js/consultas.test.cjs` e `form-dinamico.test.cjs` (novos); `modal-crud.test.cjs` ampliado.
- `AGENTS.md` e este diário.

Não foram alterados endpoints, serializers, models, views, forms, serviços, migrations, autenticação ou permissões. Não foi instalada biblioteca nova.

### 27.6 — Verificações e resultados

| Verificação | Resultado |
|---|---|
| `manage.py check` | Sem problemas identificados |
| Suíte Django existente, versão final | **52 passed in 3.40s** |
| `node --test` com os três arquivos de testes JavaScript | **22 testes aprovados** |
| Sintaxe dos cinco scripts envolvidos | Aprovada |
| Renderização do cadastro inicial e com erros | IDs únicos, regiões de status, modal único, ordem de scripts e CSRF conferidos |
| Contraste do aviso informativo | 4,96:1 |
| Diff dos scripts, cadastro e CSS | Sem erros de whitespace no lote |

Os 22 testes JavaScript incluem os oito testes de modais anteriores, um cenário de aviso compartilhado, oito cenários de consultas e cinco de formsets. Foram conferidos endpoints e normalização, preenchimento e manutenção de dados, ausência de movimento de foco durante consultas, descrições anteriores preservadas, respostas antigas descartadas, mensagens de erro, clone de valores, renomeação de campos, `TOTAL_FORMS`, foco após inclusão, anúncios, avisos de data e exibição por categoria.

Os testes usam Node nativo e DOM simplificado, sem chamar serviços externos nem salvar cadastros. A renderização pontual usa um formulário sintético para conferir os elementos adicionados; os testes existentes de views e APIs continuam passando. Essas verificações não comprovam anúncios por leitor de tela ou comportamento completo do navegador.

### 27.7 — Validação manual pendente e próximo lote

1. Recarregar Cadastro de Pessoa e escolher uma função que apresente formsets.
2. Tentar adicionar uma linha incompleta: conferir o aviso no modal, Tab/Shift+Tab, botão OK/Esc e retorno ao controle de origem.
3. Adicionar uma linha completa: conferir tabela, anúncio da inclusão/quantidade, foco no primeiro campo da próxima linha e posterior salvamento normal.
4. Conferir os avisos de data futura e menor de idade, mantendo os critérios anteriores.
5. Informar CEP válido e sair do campo: conferir mensagem, endereço preenchido e continuidade do foco. Testar também CEP não encontrado/falha, mantendo preenchimento manual.
6. Consultar CPF existente e não encontrado com Enter: conferir resultado, preservação dos campos e ausência de envio involuntário do cadastro. Conferir leitura das instruções e status com leitor de tela.
7. Conferir mensagens e avisos com zoom de 200% e repetir um modal CRUD comum para verificar que os avisos não deixaram uma descrição ou foco residual.

Depois dessa validação, o próximo lote proposto é a revisão visual de contraste restante, zoom e responsividade, seguida da revisão dos formulários que ainda não utilizam os componentes compartilhados e da validação final dos fluxos principais.

---

## 28. Foco ao abrir formulários de página completa

### 28.1 — Relato e causa

O responsável identificou que, ao acionar “+ Cadastrar nova pessoa” com Enter, a tela seguinte reiniciava a navegação por Tab no cabeçalho. O retorno/entrada de foco já cobria menu lateral e popups, mas não os links de navegação presentes no conteúdo das páginas.

### 28.2 — Implementação compartilhada

Foi criado `static/global/js/foco-formularios.js`, carregado na base global. Ao seguir um link interno do conteúdo na mesma aba, ele registra apenas o endereço de destino em `sessionStorage`. Na página de destino, consome o marcador e localiza o primeiro formulário POST de página completa com controles disponíveis. O foco vai ao primeiro campo ou botão desse formulário.

No Cadastro de Pessoa, o primeiro controle é a seleção de Função, conforme a ordem existente. O próximo Tab deve continuar dentro do formulário. O código também registra envios normais de formulários POST; se a resposta mantém o endereço e apresenta erros, prioriza o primeiro campo com `aria-invalid="true"`.

O comportamento não captura ou cancela Enter globalmente, não muda o envio dos formulários e não altera a ordem de Tab. Links de âncora da própria página, links externos, downloads, novas abas e envios interceptados por outro script não registram entrada de foco. Buscas GET, formulários dentro de popup e formulários com senha ficam fora da seleção de destino.

São ignorados controles ocultos, invisíveis, desabilitados, dentro de área `inert` ou com tabindex negativo. O marcador é restrito à aba e consumido uma única vez. Sem marcador, endereço correspondente ou armazenamento disponível, mantém-se a entrada normal da página. Não são armazenados dados preenchidos.

Os comportamentos do menu e dos popups permanecem separados e não foram modificados neste lote. Não foram alteradas autenticação, permissões, validações, URLs ou regras de negócio.

### 28.3 — Arquivos alterados e verificação

- `static/global/js/foco-formularios.js` (novo).
- `templates/base.html` — carregamento do novo script com versão `20261107-9`.
- `cadastros/tests/js/foco-formularios.test.cjs` (novo).
- `AGENTS.md` — padrão de entrada em formulários de página completa.
- Este diário.

Resultados:

- `manage.py check`: sem problemas identificados.
- Suíte Django: **52 passed in 2.84s**.
- Suíte JavaScript (os quatro arquivos): **30 testes aprovados**, incluindo oito novos cenários de formulários de página completa.
- `node --check` do novo script e revisão do diff: aprovados.

Os novos testes cobrem a navegação “Cadastrar nova pessoa”, primeiro campo inválido após POST, controles indisponíveis, exclusão de GET/popup, links internos/externos e modificadores, envios interceptados, uso único do marcador e armazenamento bloqueado. Usam DOM simplificado e não comprovam, por si só, a navegação nativa de um navegador real.

### 28.4 — Validação manual pendente

Recarregar a lista de Pessoas. Usar Tab até “+ Cadastrar nova pessoa” e Enter: na nova página, o foco deve estar na seleção de Função, e o próximo Tab deve seguir para o campo seguinte. Repetir com outro formulário de página completa e conferir foco visível e zoom de 200%. Confirmar que abrir/fechar/salvar um popup e navegar pelo menu continuam com o comportamento já aprovado.

---

## 29. Fechamento da sessão para commit e ponto de retomada

O responsável solicitou adicionar os arquivos ao Git e criar um commit para continuar o trabalho posteriormente. Foi revisado o estado completo da sessão, incluindo componentes, estilos, templates, scripts, validação de KP, testes, instruções do projeto e este diário. Os ajustes presentes no cabeçalho e na organização dos campos de Disciplina foram preservados.

Na revisão final, foram removidos os espaços em branco isolados em `templates/base.html`, `_form_disciplina_fragment.html` e `includes/mensagem_erro.html`. Os dois primeiros geravam os avisos anotados anteriormente; o último foi detectado na conferência dos arquivos novos após adicioná-los ao índice. Não houve alteração funcional nessa limpeza.

Verificações imediatamente anteriores ao commit:

- `manage.py check`: sem problemas identificados.
- `python -m pytest -p no:cacheprovider -q --tb=short`: **52 passed in 2.86s**.
- Os quatro arquivos de testes JavaScript, executados com `node --test --test-reporter=dot`: **30 testes aprovados**.
- `git diff --check`: sem erros após a limpeza de whitespace.

O commit reúne as implementações e os registros das seções anteriores, com a mensagem **`feat: melhora acessibilidade e navegacao por teclado`**. Não inclui migrations, dependências novas, credenciais ou arquivos de banco. As alterações de forms/views preservam a restrição de unicidade existente e tratam o erro de KP; as demais mudanças são de interface, interação, testes e documentação.

### Retomada sugerida

1. Conferir no navegador os últimos ajustes de formulário de página completa e de mensagens de CEP/CPF/formsets, distinguindo o que já foi confirmado do que permanece pendente nas seções 27 e 28.
2. Prosseguir com a revisão visual de contraste restante, zoom de 200% e responsividade, mantendo o padrão aprovado e as cores em variáveis.
3. Revisar os formulários que ainda não usam os componentes compartilhados, em lotes pequenos.
4. Fazer a validação final dos fluxos principais por teclado e leitor de tela e consolidar as evidências para a apresentação e o relatório do PI.

O trabalho não deve ser considerado uma certificação integral WCAG. As confirmações manuais, os resultados automatizados e as limitações estão identificados nas respectivas etapas deste diário.
