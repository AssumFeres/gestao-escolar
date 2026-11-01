# Andamento do Projeto — 27

**Data:** 02/09/2026 (máquina do quartel)
**Branch:** `dev` (commits diretos)
**Sessão dedicada a: incluir os Requisitos de Contratação no cadastro inicial (item 1 da sequência combinada), com desdobramentos em validação de Data de Nascimento.**

---

## Contexto

Continuação direta do diário 26. Item 1 da sequência já definida: mover os Requisitos de Contratação (hoje só editáveis depois de a Pessoa já existir, via popup em `detalhe.html`) para dentro do próprio `form_pessoa.html`, coletados já no cadastro inicial.

---

## 1. Requisitos de Contratação no cadastro inicial

Confirmado com o `Service` (`CadastrarPessoaComFuncaoService.executar()`) que `dados_atribuicao` é espalhado direto (`**dados_atribuicao`) na criação da `AtribuicaoFuncao` — bastou adicionar as 2 chaves novas no dicionário montado pela `View`, sem tocar no `Service`.

- **`CadastrarPessoaForm`**: 2 campos novos, idênticos aos de `EditarRequisitoContratacaoForm` (`requisito_contratacao` via `RadioSelect`, `documento_comprobatorio` texto livre).
- **`NovoCadastroPessoaView.post()`**: os 2 campos só entram em `dados_atribuicao` quando `funcao.categoria != CategoriaFuncao.DISCENTE`.
- **`form_pessoa.html`**: novo `fieldset` com `data-categoria="DOCENTE,GESTAO"`, reaproveitando o mecanismo já existente (Etapa 7.4d) — nenhuma linha de JavaScript nova foi necessária para o mostrar/esconder.

---

## 2. Incidente: `TemplateSyntaxError` ao inserir o bloco novo manualmente

Ao inserir o trecho novo no `form_pessoa.html` manualmente (por instrução direta, sem eu reescrever o arquivo inteiro), o cadastro de Pessoa parou de funcionar com `Invalid block tag on line 10: 'endif', expected 'endblock'` — a mesma classe de problema já documentada no projeto (editor com "formatar ao salvar" corrompendo tags Django em arquivos `.html`), agora pela **segunda vez** na mesma série de sessões (a primeira foi em `detalhe.html`, diário 25). Resolvido reescrevendo o arquivo inteiro do zero, e não tentando uma correção cirúrgica.

**Padrão reconhecido:** esse tipo de corrupção acontece especificamente quando o `form_pessoa.html`/`detalhe.html` é editado manualmente fora do fluxo normal ("aqui está o arquivo pronto, substitua tudo"). A causa raiz exata (VSCode `formatOnSave`, ou outro editor/extensão) não foi confirmada nesta sessão — fica como investigação futura.

---

## 3. Bug real descoberto: cadastro não salvava, sem erro visível

Depois de corrigir a corrupção do template, um teste real de cadastro de Docente/Gestão não salvava (ficava na mesma tela) sem nenhuma mensagem de erro visível. Diagnóstico em 3 passos, sem adivinhar:

1. Confirmado que **não era** a validação de "Histórico de Vínculo Formal obrigatório" (não preenchida naquele teste, mas essa não era a causa).
2. Busca no código-fonte da página (`Ctrl+U`) por `class="erro"` — não encontrado, descartando erro **geral** (`non_field_errors`).
3. Busca por `errorlist` (classe usada pelo Django para erros de **campo individual**) — encontrado: `<ul class="errorlist"><li>Enter a valid date.</li></ul>` no campo Data de Nascimento, com valor `"12121-12-03"` (ano com 5 dígitos, erro de digitação real do teste).

**Causa raiz identificada:** o formulário sempre teve esse erro visível tecnicamente, mas **inconsistente** — vários campos do formulário (incluindo os 2 novos de Requisitos) nunca mostravam `.errors` no template, ao contrário de outros (Nome, CPF, Endereço). Um erro de campo que não aparece visualmente é, na prática, um erro invisível.

---

## 4. Correções decididas: travar a possibilidade de erro

A pessoa responsável pediu para "travar essa possibilidade de erro" — 2 frentes, mais uma terceira que surgiu durante a conversa:

1. **Garantir `.errors` em TODOS os campos** de `form_pessoa.html`, sem exceção — corrigido nesta sessão, reescrevendo o arquivo inteiro.
2. **Restringir o campo de Data de Nascimento** com `min`/`max` no HTML — decisão inicial foi `max="2070-12-31"` fixo, mas evoluiu (ver item 3 abaixo) para um `max` **dinâmico**, calculado como a data de hoje a cada exibição do formulário — mais correto e simples que manter um valor fixo distante.
3. **Alerta de menor de idade** (`form-dinamico.js`, calculado a partir da Data de Nascimento) — decisão final, depois de 2 rodadas de esclarecimento:
   - Vale para **qualquer categoria** (não só Discente) — serve também como sinal de atenção para um Docente/Gestão cadastrado por engano como menor.
   - **Não bloqueia** o cadastro em nenhum caso — é só um aviso informativo (mesmo para Docente/Gestão, onde ser menor de idade é uma situação estranha na prática).

### Desdobramento durante o teste: Data de Nascimento futura era aceita

Ao testar o alerta de menor de idade, a pessoa responsável percebeu que uma Data de Nascimento **no futuro** (ex: 2032) não disparava nenhum aviso e o cadastro era salvo normalmente — a lógica de cálculo de idade simplesmente ignorava datas futuras (idade calculada ficava negativa, fora da faixa `0-18` verificada).

**Decisão:** Data de Nascimento igual a hoje ou no futuro é **sempre inválida** (ninguém nasce no futuro) — diferente do alerta de menor de idade, essa é uma validação real, que **bloqueia** o cadastro (tanto no navegador quanto, de forma autoritativa, no backend via `clean_data_nascimento()`).

### Implementação final consolidada

- **`forms.py`**: `_validar_data_nascimento_nao_futura()` (função compartilhada), usada em `clean_data_nascimento()` de `CadastrarPessoaForm` e `EditarPessoaForm` — rejeita `valor >= date.today()`. O `max` do widget também passou a ser calculado dinamicamente (`date.today().isoformat()`) no `__init__` de cada Form, substituindo o valor fixo `2070-12-31` original — mais simples, já que a regra de negócio real é "nunca no futuro", não um limite arbitrário distante.
- **`form-dinamico.js`**: ao alterar a Data de Nascimento, primeiro checa se é hoje/futura (mostra erro e para), só depois calcula a idade para o alerta de menor de idade (não bloqueia).

`pytest` — `29 passed` durante toda a sessão. Testado manualmente com sucesso: campo Requisitos aparecendo só para Docente/Gestão, erro de data futura bloqueando corretamente (tanto a mensagem quanto o não-salvamento), aviso de menor de idade funcionando, regressão geral.

**Commit:** `2cbbc2e` — `feat: Requisitos de Contratacao no cadastro inicial + validacoes de Data de Nascimento`.

---

## Estado geral ao final desta sessão

| Item | Status |
|---|---|
| Requisitos de Contratação no cadastro inicial (item 1 da sequência) | ✅ Implementado e testado |
| `.errors` consistente em todos os campos de `form_pessoa.html` | ✅ Corrigido |
| Validação de Data de Nascimento futura (bloqueante) | ✅ Implementado e testado |
| Alerta de menor de idade (informativo, qualquer categoria) | ✅ Implementado e testado |
| Item 2 da sequência (busca por CPF, generalizada) | ⏳ Próximo passo |
| Item 3 (auditoria de campos FE 008/FOP 402) | ⏳ Depois do item 2 |
| Testes automatizados | 29 passed (sem alteração) |

---

## Itens novos de Backlog identificados nesta sessão

- [ ] **Investigar a causa raiz da corrupção de tags Django em `.html`** — segunda ocorrência na mesma série de sessões (diário 25 e esta), sempre ao editar manualmente `form_pessoa.html`/`detalhe.html` fora do fluxo de substituição completa do arquivo. Suspeita: `formatOnSave` do editor, mas não confirmado.
- [ ] Testes automatizados para `clean_data_nascimento()` (data futura rejeitada) — nenhum ainda.
- [ ] Considerar aplicar a mesma trava de Data de Nascimento (futura/idade) em qualquer outro campo de data análogo do sistema, se existir (ex: `data_emissao_identidade` também não deveria ser futura) — não avaliado nesta sessão.

---

## Próximos passos

Seguir a sequência já definida: busca de Pessoa por CPF, com reaproveitamento/edição de dados (generalizada, qualquer categoria); depois, a auditoria de campos Docente (FE 008) e Gestão (FOP 402) contra o formulário único atual.
