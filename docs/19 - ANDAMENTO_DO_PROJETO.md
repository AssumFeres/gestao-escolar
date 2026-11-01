# Andamento do Projeto — 19

**Data:** 31/08/2026
**Branch:** `dev` (commits diretos)
**Sessão dedicada a: implementar `choices` para os campos `sexo`, `estado_civil` e `raca_cor` (item do Backlog), e investigar um bug de dados "sumindo" nos Formsets de Pendência e Formação — investigação interrompida por troca de máquina, com um problema novo (Docente não cadastra) em aberto.**

---

## Contexto

Sessão realizada em outra máquina (`C:\projetos\gestao-escolar`, Python 3.10.11). Objetivo original: fechar o item de Backlog "Configurar `choices` para os campos `sexo`, `estado_civil`, `raca_cor`", com as opções já definidas pela pessoa responsável numa sessão anterior:

- **Sexo:** Masculino, Feminino
- **Raça/Cor:** Branca, Preta, Amarela, Parda, Indígena, Não Declarada
- **Estado civil:** Solteiro(a), Casado(a), Separado(a) Judicialmente, Divorciado(a), Viúvo(a)

---

## Parte 1 — `choices` implementados e testados (✅ concluído)

Seguindo o padrão já usado no projeto (`TextChoices`, como `TipoFormacaoDocente`/`CategoriaFuncao`):

- **`cadastros/models.py`**: 3 `TextChoices` novos (`Sexo`, `RacaCor`, `EstadoCivil`) adicionados antes da classe `Pessoa`; `choices=` aplicado aos 3 campos existentes (`max_length` de todos já era suficiente para os códigos escolhidos — nenhum campo precisou aumentar de tamanho).
- **Migration `0002_alter_pessoa_estado_civil_alter_pessoa_raca_cor_and_more`**: gerada e aplicada, só `AlterField`, sem risco a dado existente.
- **`cadastros/forms.py`**: os 3 `CharField` de texto livre trocados por `ChoiceField`, com opção vazia `'---------'` no topo (mesmo padrão de `tipo_formacao`/`tipo`).
- **`cadastros/templates/cadastros/detalhe.html`**: as 3 exibições trocadas de valor cru para `get_<campo>_display` (mesma convenção já usada para `pendencia.get_tipo_display`/`formacao.get_tipo_formacao_display`), evitando mostrar o código interno (`SOLTEIRO`) em vez do texto legível ("Solteiro(a)").

`pytest` — `29 passed` depois de cada uma das 3 mudanças (Model, Form, Template). Testado manualmente pelo navegador: dropdowns aparecendo corretamente no formulário, opções certas, e teste de cadastro de Diretor e Coordenador confirmando que o texto legível aparece na tela de detalhe.

**Commit:** parte de `dca5ab5` (junto da Parte 2, ver abaixo — não foram separados em commits distintos, decisão tomada no momento por já estarem os dois prontos ao mesmo tempo para commitar).

---

## Parte 2 — Bug descoberto: dados de Pendência (e Formação) "sumindo" antes do banco

### Sintoma relatado

Ao testar o cadastro com `choices` prontos, a pessoa responsável cadastrou 2 Pendências de Documentação numa Pessoa — a tabela-resumo na tela mostrava as linhas corretamente antes de salvar, mas depois de salvo, **nenhuma das duas aparecia no banco nem na tela de detalhe**.

### Diagnóstico via `print()` temporário na View

Seguindo o mesmo método já usado com sucesso no diário 14 (instrumentar `NovoCadastroPessoaView.post()` com `print()` para inspecionar o que chega do formulário), foi confirmado:

```python
cleaned_data: [{'tipo': '', 'descricao': 'dfasdfdasf'}, {'tipo': '', 'descricao': 'fdsafas'}, {'tipo': '', 'descricao': 'dfasfdas'}, {}]
```

O campo `tipo` chegava **vazio** em todas as linhas, embora `descricao` estivesse correto. Como `_CAMPO_PREENCHIDO['pendencia'] = 'tipo'` é o campo-sinal que `_linhas_preenchidas()` usa para decidir se uma linha do Formset é "de verdade" (não só a linha `extra=1` em branco), as 3 linhas eram descartadas silenciosamente antes de chegar ao `Service` — davam a impressão de terem "sumido".

**Incidente à parte, durante a instrumentação:** o bloco de `print()` foi colado por engano no corpo da classe `NovoCadastroPessoaView` (fora de qualquer método), causando `NameError: name 'request' is not defined` já na inicialização do servidor. Diagnosticado e corrigido reescrevendo o arquivo `views.py` inteiro (mais confiável, nessa situação, do que tentar um `replace` textual cirúrgico via PowerShell — tentativa anterior de remoção por correspondência de texto exato falhou silenciosamente, deixando os dois blocos, certo e errado, coexistindo no arquivo).

### Causa raiz: `cloneNode()` não preserva a opção selecionada de um `<select>`

A pessoa responsável já suspeitava corretamente que o problema estava "entre preencher e salvar" — a investigação confirmou o mecanismo exato. Em `form-dinamico.js`, ao clicar "+ Adicionar", o código clona o bloco de formulário visível para guardá-lo oculto (`clone = templateArea.cloneNode(true)`), a ser enviado no POST junto com o formulário principal. **Comportamento documentado e conhecido dos navegadores:** `cloneNode()` clona a estrutura e o texto digitado em `<input>` corretamente, mas **não preserva a opção atualmente selecionada de um `<select>`** — o clone sempre volta para a opção padrão do HTML (o placeholder "---------"), mesmo que o usuário tenha escolhido outra na tela.

A tabela-resumo mostrava o texto certo porque lê o valor do `<select>` **antes** do clone quebrar, direto do elemento ainda vivo na tela — por isso a experiência visual (linha aparecendo certa) não combinava com o dado realmente enviado (campo vazio).

**Escopo do impacto:** esse bug afeta qualquer campo `<select>` (`ChoiceField`/`ModelChoiceField`) dentro de qualquer bloco de Formset, não só Pendência:
- `Pendência.tipo` — confirmado
- `FormacaoDocente.tipo_formacao` — não é o campo-sinal (`curso` é), então não causa descarte de linha, mas o valor em si também se perdia silenciosamente, sendo salvo como vazio mesmo quando selecionado
- `HistoricoVinculoFormal.vinculo_formal` — é o campo-sinal; mesmo padrão de descarte de linha esperado, ainda não confirmado em teste manual

### Correção aplicada

Em `form-dinamico.js`, depois de clonar, copiar manualmente o `.value` de cada `<select>` do formulário original para o `<select>` correspondente no clone (mesma ordem no DOM, garantida porque o clone tem exatamente a mesma estrutura):

```javascript
var selectsOriginais = templateArea.querySelectorAll('select');
var selectsClone = clone.querySelectorAll('select');
selectsOriginais.forEach(function (selectOriginal, indice) {
    selectsClone[indice].value = selectOriginal.value;
});
```

### Validação parcial: funcionou para Gestão, não para Docente

Testado manualmente com **Diretor** e **Coordenador de Curso Aviônicos** (categoria Gestão) — cadastro funcionou corretamente após a correção.

**Testado com Docente e o cadastro parou de funcionar por completo — nem a `Pessoa` é criada.** Diferente do sintoma original (dado descartado silenciosamente, redirecionamento normal), agora nada acontece de efeito visível esperado: não gerou erro 500, não ficou visivelmente preso na mesma tela com mensagem de erro. Comportamento exato não totalmente caracterizado — a pessoa responsável precisou parar a sessão para trocar de máquina antes de aprofundar.

**Estado deixado deliberadamente em aberto, documentado com precisão no commit** (`dca5ab5`): o `pytest` automatizado continua `29 passed`, confirmando que a base de Service/Form segue sã — o problema é específico do fluxo manual via navegador com a categoria Docente, ainda não coberto por nenhum teste automatizado (reforça a prioridade do item já em Backlog sobre testes de View).

---

## Estado geral ao final desta sessão

| Item | Status |
|---|---|
| `choices` de Sexo/Estado Civil/Raça-Cor (Model, Form, Template) | ✅ Concluído e testado (`pytest` 29 passed, manual Diretor/Coordenador) |
| Bug do `cloneNode()` perdendo valor de `<select>` — diagnóstico | ✅ Causa raiz identificada e documentada |
| Bug do `cloneNode()` — correção em `form-dinamico.js` | ✅ Aplicada, validada para categoria Gestão |
| Regressão nova: Docente não cadastra `Pessoa` após a correção | 🔴 **Aberto** — causa não diagnosticada, investigação interrompida |
| Testes automatizados | 29 passed (sem alteração — bug e correção são de frontend puro, sem cobertura de teste JS no projeto) |

---

## Próximos passos (retomar em outra máquina)

1. **Prioridade imediata:** reproduzir o cadastro de Docente e capturar, desta vez, o comportamento exato — reativar temporariamente um `print()` (desta vez dentro de `post()`, com cuidado de indentação) ou usar as ferramentas de desenvolvedor do navegador (aba Network) para ver se o POST chega a ser enviado, e com qual payload, antes de reintroduzir qualquer instrumentação no back-end.
2. Hipóteses a descartar, em ordem de suspeita:
   - O JavaScript de "Adicionar" quebrando de alguma forma específica ao bloco de Formação (que tem 2 campos `<select>` na mesma linha — `tipo_formacao` e nenhum outro, então não é isso; conferir se `data-fields`/ordem dos `querySelectorAll('select')` bate exatamente entre original e clone quando há mistura de campos texto/select na mesma linha).
   - Cache de navegador ainda servindo uma versão inconsistente do JS (Ctrl+F5 já foi tentado sem sucesso, mas vale conferir a aba Network se o arquivo `.js` realmente veio do servidor, não do cache, e se é o conteúdo esperado).
   - Algum erro de JavaScript no console do navegador (F12 → Console) impedindo o `submit` do formulário de completar, sem chegar a gerar requisição HTTP nenhuma.
3. Depois de resolvido: adicionar teste manual explícito dos 3 fluxos (Discente/Docente/Gestão) com Formações/Pendências/Histórico preenchidos como parte do checklist padrão, já que esse tipo de bug (clone de `<select>`) só se manifesta em uso real do formulário, não em testes de `Service`.
4. Retomar o CRUD completo do módulo Cadastros (ver Kanban) só depois de fechar essa regressão — um bug de cadastro básico não corrigido bloqueia a confiança nas próximas telas.
