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
- `Esc` deve fechar modais quando apropriado.

## Tabelas
- `th` para cabeçalhos.
- `scope="col"`/`scope="row"` quando apropriado.
- `caption` quando melhora a compreensão.
- Não usar tabela apenas para layout.

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
