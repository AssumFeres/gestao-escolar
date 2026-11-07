---
name: code-change-verification
description: Use após alterações no projeto Django para revisar o diff, executar checks e testes existentes e detectar regressões antes de concluir a tarefa.
---

# Code Change Verification

## Processo
1. Revise `git diff`.
2. Confirme que só arquivos necessários foram alterados.
3. Verifique migrations inesperadas.
4. Descubra o runner de testes configurado.
5. Execute checks/testes existentes.

## Comandos
Quando configurados:
- `python manage.py check`
- `pytest`
- `python manage.py test`

Se houver lint/format/type-check configurado, execute também.

## Para templates/JS/CSS
Verifique:
- sintaxe de templates;
- seletores JS preservados;
- `id`, `name`, URLs e ações preservados;
- modais e formulários continuam abrindo/enviando.

## Para acessibilidade
Faça verificação manual mínima:
- Tab/Shift+Tab;
- Enter/Space;
- foco visível;
- foco de modal;
- labels/erros;
- zoom 200%.

## Falhas
- diferencie falha causada pela mudança de falha preexistente;
- não corrija automaticamente código fora do escopo;
- registre a falha.

## Saída
Informe comandos, resultados, arquivos alterados, riscos remanescentes e testes manuais necessários.
