---
name: django-accessibility
description: Use para auditar ou implementar acessibilidade em templates Django, formulários, tabelas, menus, modais, CSS e JavaScript, com foco em WCAG 2.2 AA, teclado e tecnologias assistivas.
---

# Django Accessibility

## Objetivo
Melhorar acessibilidade sem reescrever desnecessariamente páginas e sem alterar regras de negócio.

## Processo
1. Identifique herança de templates e componentes reutilizáveis.
2. Comece pelos componentes globais.
3. Faça mudanças pequenas e revisáveis.
4. Use HTML semântico antes de ARIA.
5. Preserve nomes de campos, URLs, seletores JS e contratos com views/forms.
6. Não altere models/regras de negócio sem solicitação explícita.
7. Ao terminar, execute a skill `code-change-verification`.

## Checklist
### Estrutura
- `lang="pt-BR"`;
- `main` identificável;
- navegação em `nav`;
- títulos coerentes;
- skip link quando aplicável.

### Formulários
- label associado;
- placeholder não substitui label;
- obrigatoriedade clara;
- erro associado ao campo;
- `aria-invalid`/`aria-describedby` quando necessário;
- erro não depende só de cor.

### Controles
- `button` para ações;
- `a` para navegação;
- nomes acessíveis em ícones;
- estados acessíveis quando aplicável.

### Teclado
- ações essenciais sem mouse;
- ordem de foco lógica;
- foco visível;
- sem armadilhas de teclado.

### Modais
- título/nome acessível;
- foco entra no modal;
- foco fica coerente;
- fecha por teclado quando apropriado;
- foco retorna ao gatilho.

### Tabelas
- `th`;
- `scope` quando necessário;
- `caption` quando útil;
- ações com nomes acessíveis.

### Conteúdo dinâmico
- mensagens importantes anunciáveis quando necessário;
- autocomplete por teclado;
- atualizações não removem foco sem motivo.

### Visual
- contraste adequado;
- estado não depende só de cor;
- foco visível;
- zoom 200%.

## Evite
- ARIA redundante;
- `tabindex` positivo;
- `div`/`span` clicável quando `button` resolve;
- mudanças globais de CSS sem revisão;
- framework novo sem necessidade.

## Saída esperada
Informe problemas encontrados, correções, arquivos alterados, itens que exigem validação manual e pontos que dependem de decisão de negócio.
