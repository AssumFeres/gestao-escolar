# Andamento do Projeto — 43

**Data:** 10/09/2026  
**Branch:** `dev`  
**Sessão dedicada a: ajustes visuais nos formulários CRUD, correção da largura dos popups e refinamentos no detalhe de Pessoa.**

---

## 1. Contexto

Após o fechamento do `docs/42`, foi realizada uma nova rodada de ajustes predominantemente visuais no módulo `cadastros`.

Nesta sessão, parte das alterações foi feita diretamente pela pessoa responsável pelo projeto, principalmente nos templates parciais (`_form_*_fragment.html`), com foco em melhorar organização, distribuição dos campos e aparência dos formulários exibidos em popup.

Também foi identificado e corrigido um efeito colateral importante causado por uma alteração anterior no CSS dos modais: ao ampliar o popup de **Editar Pessoa**, a regra de largura havia sido aplicada ao container genérico do modal e, por consequência, **todos os popups CRUD passaram a ficar largos**.

---

## 2. Arquivos alterados nesta sessão

Segundo o `git status`, os seguintes arquivos foram modificados:

- `cadastros/templates/cadastros/_form_ata_fragment.html`
- `cadastros/templates/cadastros/_form_disciplina_fragment.html`
- `cadastros/templates/cadastros/_form_modulo_fragment.html`
- `cadastros/templates/cadastros/_form_oferta_modulo_fragment.html`
- `cadastros/templates/cadastros/_form_pessoa_editar_fragment.html`
- `cadastros/templates/cadastros/_form_submodulo_fragment.html`
- `cadastros/templates/cadastros/detalhe.html`
- `static/global/css/base.css`

---

## 3. Ajustes realizados nos formulários CRUD

Foram feitos ajustes de layout principalmente nos templates parciais usados em popup.

### 3.1 — `_form_ata_fragment.html`

Ajustes visuais no formulário de Ata, com reorganização dos campos para melhorar distribuição e leitura dentro do modal.

### 3.2 — `_form_disciplina_fragment.html`

Ajustes visuais no formulário de Disciplina, mantendo a funcionalidade existente e refinando a disposição dos campos.

### 3.3 — `_form_modulo_fragment.html`

Reorganização visual do formulário de Módulo, visando maior consistência com o padrão adotado nos demais cadastros.

### 3.4 — `_form_oferta_modulo_fragment.html`

Ajustes de layout no formulário de Oferta de Módulo, preservando a estrutura funcional já implementada.

### 3.5 — `_form_submodulo_fragment.html`

Reorganização visual do formulário de Submódulo, seguindo o padrão de melhoria dos demais popups CRUD.

### 3.6 — `_form_pessoa_editar_fragment.html`

Além dos ajustes visuais, este formulário passou a ser tratado como **exceção de largura**, pois é significativamente maior e utiliza uma distribuição mais ampla de campos.

---

## 4. Problema identificado — todos os popups ficaram largos

### 4.1 — Causa

Na alteração anterior do popup de Editar Pessoa, foi utilizada uma regra genérica semelhante a:

```css
#modal-crud-overlay > * {
    width: 90vw !important;
    max-width: 1400px !important;
}
```

Como `#modal-crud-overlay` é reutilizado por todos os popups CRUD, essa regra passou a afetar indiscriminadamente os demais formulários exibidos no modal.

Ou seja, a largura de **Editar Pessoa**, que deveria ser uma exceção, acabou se tornando o padrão global.

---

## 5. Correção aplicada — modal genérico + exceção para Editar Pessoa

A solução adotada foi separar o comportamento em dois níveis.

### 5.1 — Modal CRUD genérico

Os popups comuns voltaram a ter largura reduzida:

```css
#modal-crud-overlay > * {
    width: 90% !important;
    max-width: 600px !important;
}
```

Assim, os formulários menores retornam ao tamanho adequado.

### 5.2 — Classe genérica dos formulários

A classe comum continua sendo:

```html
class="form-modal-crud"
```

Ela permanece responsável apenas pelo comportamento genérico dos formulários exibidos em modal.

### 5.3 — Nova classe específica para Editar Pessoa

Foi criada uma especialização:

```html
class="form-modal-crud form-modal-crud-editar-pessoa"
```

A intenção é manter a classe genérica e acrescentar uma segunda classe apenas no formulário que realmente precisa de uma caixa maior.

### 5.4 — Largura específica do popup Editar Pessoa

O CSS identifica somente a caixa que contém o formulário especial:

```css
#modal-crud-overlay > *:has(.form-modal-crud-editar-pessoa) {
    width: 90vw !important;
    max-width: 1400px !important;
}
```

Resultado esperado:

- popups comuns → até `600px`;
- Editar Pessoa → até `1400px`.

Essa alteração corrige o efeito colateral sem necessidade de modificar todos os demais templates CRUD.

---

## 6. Responsividade preservada

O comportamento responsivo dos modais foi mantido:

- em telas intermediárias, o popup de Editar Pessoa pode ocupar mais largura;
- o grid interno de Editar Pessoa reduz de 4 para 2 colunas;
- em telas pequenas, os modais ocupam praticamente toda a largura disponível;
- o grid de Editar Pessoa passa para 1 coluna.

A correção da largura não altera o comportamento em dispositivos menores.

---

## 7. `detalhe.html`

O template de detalhe de Pessoa também recebeu novos ajustes de apresentação.

Foi preservado o padrão definido na sessão anterior:

- `fieldset` para agrupamentos semânticos;
- grids para dados individuais;
- tabelas para históricos e coleções;
- distribuição dos campos de modo a melhorar leitura e aproveitamento horizontal.

Entre os refinamentos já consolidados:

- Filiação 1 e Filiação 2 lado a lado;
- melhor agrupamento dos dados do Discente;
- manutenção da visualização em até 4 colunas nos blocos de detalhe.

---

## 8. Decisões consolidadas sobre popups

A partir desta sessão, fica estabelecido o seguinte padrão:

- `.form-modal-crud` → comportamento genérico para qualquer popup CRUD;
- `.form-modal-crud-editar-pessoa` → especialização exclusiva para Editar Pessoa;
- largura do modal não deve mais ser ampliada por regra genérica;
- quando um novo popup precisar de dimensões especiais, deve receber **classe própria**, sem alterar o comportamento dos demais;
- o CSS do container externo deve ser tratado com cuidado, pois ele é compartilhado por todos os modais carregados em `#modal-crud-overlay`.

---

## 9. Estado geral ao final da sessão

| Item | Status |
|---|---|
| Layout de `_form_ata_fragment.html` | ✅ Ajustado |
| Layout de `_form_disciplina_fragment.html` | ✅ Ajustado |
| Layout de `_form_modulo_fragment.html` | ✅ Ajustado |
| Layout de `_form_oferta_modulo_fragment.html` | ✅ Ajustado |
| Layout de `_form_submodulo_fragment.html` | ✅ Ajustado |
| Layout de `_form_pessoa_editar_fragment.html` | ✅ Ajustado |
| `detalhe.html` refinado | ✅ Ajustado |
| Popups comuns herdando largura de 1400px | ✅ Corrigido |
| Modal genérico limitado a aproximadamente 600px | ✅ Corrigido |
| Editar Pessoa mantendo popup amplo | ✅ Corrigido |
| Responsividade dos modais | ✅ Preservada |

---

## 10. Ponto de atenção para futuras alterações

Ao alterar qualquer regra relacionada a:

```css
#modal-crud-overlay
#modal-crud-overlay > *
#modal-crud-corpo
.form-modal-crud
```

é necessário considerar que essas estruturas são compartilhadas por vários CRUDs.

Portanto, qualquer necessidade específica de um formulário deve, preferencialmente, ser implementada com uma **classe especializada**, evitando efeitos colaterais em outros popups.

Exemplo do padrão correto:

```html
<form class="form-modal-crud form-modal-crud-editar-pessoa">
```

e não pela alteração direta da largura global do modal.

---

## 11. Próximos passos

- Testar visualmente todos os popups modificados.
- Confirmar se os formulários de Ata, Disciplina, Módulo, Submódulo e Oferta de Módulo voltaram ao tamanho adequado.
- Confirmar se Editar Pessoa continua com largura ampliada.
- Verificar comportamento em telas menores.
- Após validação visual, realizar `git add`, `commit` e `push` da sessão.
