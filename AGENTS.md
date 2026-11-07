# AGENTS.md — Sistema de Gestão Escolar EMCA

## Objetivo do repositório
Sistema de gestão escolar em Django. Preserve regras de negócio existentes e faça alterações incrementais, pequenas e verificáveis.

## Prioridade atual
Melhorar a acessibilidade da interface sem reescrever desnecessariamente o sistema e sem alterar regras de negócio.
Referência:
- WCAG 2.2 AA;
- HTML semântico antes de ARIA;
- navegação por teclado;
- zoom de 200%.

## Fora do escopo atual
Não implementar ou modificar autenticação, login, perfis, usuários ou permissões, salvo solicitação explícita.
Não alterar regras de matrícula, turma, ata, histórico, relocação, aprovação, reprovação ou encerramento apenas por motivo visual/acessibilidade.

## Antes de alterar código
1. Inspecione a estrutura do repositório.
2. Identifique herança dos templates e componentes reutilizados.
3. Localize `base.html`, menus, cabeçalhos, modais, includes/fragments e JS/CSS comuns.
4. Descubra o runner de testes já utilizado.
5. Prefira corrigir componentes compartilhados a repetir correções.

## Templates Django
- Preserve `{% csrf_token %}`, nomes de campos, URLs, `name=`, `id=` e seletores usados por JavaScript, salvo necessidade real.
- Use `header`, `nav`, `main`, `section`, `footer`, `button`, `table`, `th` etc.
- Mantenha hierarquia lógica de títulos.
- Preferencialmente um `h1` principal por página.
- Inclua mecanismo de “pular para o conteúdo principal” quando aplicável.
- Use `lang="pt-BR"`.

## Formulários
- Todo campo relevante deve possuir `label`.
- Placeholder não substitui label.
- Campos obrigatórios devem ser identificáveis.
- Mensagens de erro devem ser textuais e associadas ao campo.
- Use `aria-describedby`, `aria-invalid` e `aria-live` somente quando apropriado.
- Não dependa somente de cor.

## Botões, links e controles
- `button` para ações; `a` para navegação.
- Evite `div`/`span` clicável quando elemento nativo resolve.
- Controles com ícone devem possuir nome acessível.
- Evite textos genéricos como “clique aqui”.

## Teclado e foco
- Ações essenciais devem funcionar por teclado.
- Ordem de foco lógica.
- Foco visível.
- Ao abrir modal, mover foco para o modal.
- Ao fechar, devolver foco ao controle que abriu.
- Após salvar um popup com recarregamento da página, restaurar o foco no controle que o abriu, quando ele ainda existir, para permitir continuar a navegação por Tab.
- Ao navegar por um link do menu lateral, manter o grupo expandido e mover o foco para o primeiro campo ou botão visível e habilitado do conteúdo principal da página de destino; se não houver, focar o próprio `main`. O próximo Tab deve continuar a navegação dentro da tela, sem percorrer novamente o menu.
- Ao abrir formulário de página completa por um link no conteúdo, mover o foco ao primeiro campo ou botão disponível do formulário; ao retornar com erros após envio normal, priorizar o primeiro campo inválido. Reutilize `global/js/foco-formularios.js`, preservando links internos, novas abas, formulários de busca e o comportamento separado dos popups.
- `Esc` deve fechar modais quando apropriado.
- Nos modais CRUD, reutilize `templates/includes/modal_crud.html` e `modal-crud.js`: diálogo com nome acessível, Tab/Shift+Tab contidos no popup e fundo inativo somente enquanto aberto, restaurando seu estado ao fechar. Preserve IDs, classes e contratos com os formulários.

## Tabelas
- `th` para cabeçalhos.
- `scope="col"`/`scope="row"` quando apropriado.
- `caption` quando melhora a compreensão.
- Não usar tabela apenas para layout.
- Reutilize o padrão validado: legenda `caption` com `.visualmente-oculto` quando não for necessário exibi-la, cabeçalhos de coluna com `scope="col"`, coluna “Ações” identificada e nomes acessíveis com contexto nos controles repetidos. Em tabelas de pares rótulo/valor, associe cada célula ao cabeçalho correto com IDs únicos e `headers`, especialmente quando há vários pares na mesma linha.

## Imagens e visual
- Imagens informativas: `alt` útil.
- Decorativas: `alt=""`.
- Não depender apenas de cor.
- Verificar contraste e foco.

## JavaScript e conteúdo dinâmico
- Prefira comportamento nativo.
- Mudanças dinâmicas importantes devem ser perceptíveis por tecnologias assistivas.
- Autocomplete, mensagens, carregamentos e atualizações devem continuar utilizáveis por teclado.
- Preserve API de CEP e autocomplete.
- Não introduza biblioteca nova sem necessidade.
- Nas consultas de CEP/CPF, reutilize `feedback-consulta.js`, regiões `role="status"` e associações por `aria-describedby`, preservando descrições existentes e sem mover o foco ao receber respostas. Mantenha falhas visíveis, preenchimento manual disponível e ignore respostas de consultas substituídas.
- Avisos dos formsets devem reutilizar o modal compartilhado pelo evento `modal-crud-aviso`, com retorno de foco; após incluir uma linha, anunciar a inclusão e focalizar o primeiro campo da próxima linha sem alterar os dados clonados ou o gerenciamento do formset.

## Consistência visual e mensagens de erro
- Reutilize os padrões e componentes existentes em todo o aplicativo; não crie estilos alternativos para o mesmo tipo de mensagem.
- Para erros de formulário, use o padrão `.erro`: fundo `#f2dede`, texto `#a94442`, borda `#ebccd1` e ícone de aviso decorativo, acompanhado de mensagem textual.
- Reutilize `templates/includes/mensagem_erro.html` e `templates/includes/resumo_erros_formulario.html`, preservando IDs e associações dos erros aos campos.
- No resumo de erros, mostre um link por campo inválido, usando somente o nome do campo; mantenha a mensagem completa junto ao controle, sem repeti-la no link. Preserve a exibição de erros gerais do formulário.
- Links dentro de mensagens devem manter contraste e sublinhado. Não use apenas cor ou ícone para comunicar um erro.
- Para ações de formulário, reutilize `.btn-salvar` e `.btn-cancelar`, com a mesma geometria e foco visível. Defina suas cores pelas variáveis `--botao-salvar-*` e `--botao-cancelar-*` no `:root`, incluindo hover e texto; não grave cores diretamente nessas classes. No tema atual, Salvar usa fundo `#002060`; Cancelar usa fundo `#B50A04` e texto `#F7F7F7`.
- O foco de botões usa anel duplo em `:focus-visible`: 2px na cor `--foco-anel-interno` e 5px na cor `--foco-anel-externo` (atualmente branco e `#111827`). Reutilize esse padrão, com outline do sistema em cores forçadas.
- Se um padrão existente não atender à acessibilidade, ajuste o componente compartilhado e documente a decisão no diário de trabalho; mantenha o mesmo padrão nas telas seguintes.

## Estratégia
Trabalhe em lotes:
1. `base.html` e estrutura global;
2. menu e landmarks;
3. formulários e mensagens;
4. tabelas;
5. modais/foco;
6. JavaScript dinâmico;
7. CSS de foco, contraste, zoom e responsividade;
8. páginas específicas.

Após cada lote:
- revise o diff;
- rode checks;
- rode testes relevantes;
- confirme ausência de regressão funcional.

## Verificação
Descubra primeiro os comandos realmente configurados.
Quando disponíveis:
- `python manage.py check`
- `pytest`
- `python manage.py test`

Não invente dependências/comandos.
Se houver falha preexistente, registre separadamente.

## Critérios mínimos
- Tab/Shift+Tab;
- Enter/Space quando aplicável;
- foco visível;
- labels;
- erros compreensíveis;
- títulos/landmarks;
- tabelas adequadas;
- modais com foco coerente;
- zoom 200%;
- sem regressão funcional aparente.

## Skills
Para acessibilidade, use `django-accessibility`.
Após alterações, use `code-change-verification`.

## Resumo final obrigatório
Informe:
1. arquivos alterados;
2. problemas corrigidos;
3. checks/testes executados;
4. resultados;
5. pontos que ainda exigem teste manual;
6. riscos ou regras de negócio não alteradas.
