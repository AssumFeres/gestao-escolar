# ESPECIFICAÇÃO DE ARQUITETURA — CADASTRO DE PESSOA E REGISTROS RELACIONADOS

## 1. Contexto do projeto

Estou desenvolvendo um sistema Web de Gestão Escolar utilizando Django.

Existe uma entidade principal denominada `Pessoa` e diversas entidades relacionadas a ela, armazenadas em tabelas próprias do banco de dados, como, por exemplo:

- `cadastros_formacaodocente`
- `cadastros_experienciaprofissional`
- `cadastros_capacidades`
- histórico de vínculo formal
- pendências de documentação
- futuramente outras entidades relacionadas à Pessoa

A entidade `Pessoa` deve ser o registro principal.

As demais entidades devem possuir relacionamento com Pessoa por meio de Foreign Key.

Conceitualmente:

```text
Pessoa
│
├── Formação Docente
├── Experiência Profissional
├── Capacidades
├── Histórico de Vínculo Formal
├── Pendências
└── outros registros futuros
```

Não alterar os nomes reais dos Models, campos ou tabelas sem antes verificar o código existente em `models.py`.

---

# 2. Situação atual

Atualmente existe um template principal denominado:

```text
form_pessoa.html
```

Esse template contém tanto os campos da Pessoa quanto blocos de registros relacionados.

Entre esses blocos existem atualmente:

## Formação Docente

Prefixo atual do formset:

```text
formacao
```

Campos:

```text
tipo_formacao
curso
entidade
cidade
uf
ano_conclusao
```

## Experiência Profissional

Prefixo:

```text
experiencia
```

Campos:

```text
organizacao
cargo
data_inicio
data_fim
```

## Histórico de Vínculo Formal

Prefixo:

```text
historico
```

Campos:

```text
vinculo_formal
data_inicio
data_fim
```

## Pendência de Documentação

Prefixo:

```text
pendencia
```

Campos:

```text
tipo
descricao
```

Existe também a entidade de Capacidades, que deverá seguir posteriormente o mesmo padrão arquitetural. Antes de implementá-la, devem ser consultados seus Model e Form reais para identificar os campos corretos.

---

# 3. Problema da arquitetura atual

Atualmente os registros relacionados utilizam Django Formsets associados a um JavaScript denominado:

```text
cadastros/static/cadastros/js/form-dinamico.js
```

Ao clicar em:

```text
+ Adicionar
```

o sistema não grava imediatamente o registro no banco.

O JavaScript:

1. lê os dados preenchidos;
2. cria uma linha visual na tabela;
3. executa:

```javascript
templateArea.cloneNode(true)
```

4. cria uma cópia oculta do formulário preenchido;
5. armazena essa cópia dentro de `.formset-hidden`;
6. limpa e reindexa o formulário visível;
7. aumenta o `TOTAL_FORMS`;
8. somente quando o usuário clica posteriormente em `Salvar` todo o formulário é enviado ao Django.

Portanto, atualmente existe um estado intermediário:

```text
Usuário preenche
      ↓
Adicionar
      ↓
registro aparece na tabela HTML
      ↓
NÃO existe ainda no banco
      ↓
dados permanecem temporariamente no DOM
      ↓
Salvar Pessoa
      ↓
POST geral
      ↓
Django Formsets
      ↓
Banco
```

Essa arquitetura já apresentou problemas especificamente com campos `<select>` porque `cloneNode(true)` não necessariamente preserva corretamente o estado selecionado.

Foi criada uma primeira correção copiando manualmente o `.value` dos `<select>` originais para os `<select>` clonados.

Essa solução pode permanecer temporariamente, mas NÃO deve ser considerada a arquitetura definitiva.

---

# 4. Decisão arquitetural

A arquitetura deverá migrar de:

```text
Formsets + cloneNode + armazenamento temporário no DOM
```

para:

```text
Pessoa persistida
+
CRUD independente das entidades relacionadas
+
Foreign Keys reais
+
templates parciais/modais
```

O princípio central deverá ser:

> Se um registro aparece na tabela de Formação, Experiência, Capacidade, Histórico ou Pendência, esse registro deve existir efetivamente no banco de dados.

Portanto, não deverá mais existir uma linha na tabela representando apenas um dado temporário armazenado no navegador.

---

# 5. A tela de Pessoa deve permanecer visualmente única

IMPORTANTE:

Não quero transformar o cadastro da Pessoa em várias páginas independentes.

Para o usuário, a interface deve continuar sendo uma única tela de Pessoa.

Exemplo:

```text
---------------------------------------------------
DADOS DA PESSOA
---------------------------------------------------

Nome
CPF
Nascimento
E-mail
Telefone
Endereço
Função
etc.

---------------------------------------------------
FORMAÇÃO DOCENTE
---------------------------------------------------

[ + Adicionar Formação ]

Tipo       Curso       Entidade      Ano      Ações
---------------------------------------------------
Graduação  Engenharia  UNITAU        2020     Editar Excluir


---------------------------------------------------
EXPERIÊNCIA PROFISSIONAL
---------------------------------------------------

[ + Adicionar Experiência ]

Organização    Cargo       Início      Fim       Ações
-------------------------------------------------------
Empresa A      Mecânico    2020        2023      Editar Excluir


---------------------------------------------------
CAPACIDADES
---------------------------------------------------

[ + Adicionar Capacidade ]

...
```

Portanto:

```text
uma tela
```

mas internamente:

```text
vários CRUDs independentes
```

---

# 6. Templates separados NÃO significam páginas separadas

Os formulários das entidades relacionadas devem preferencialmente ser implementados em templates parciais.

Uma estrutura possível é:

```text
templates/
└── cadastros/
    ├── form_pessoa.html
    │
    └── partials/
        ├── _formacao_docente.html
        ├── _experiencia_profissional.html
        ├── _historico_vinculo.html
        ├── _pendencia.html
        └── _capacidade.html
```

Outra possibilidade:

```text
templates/
└── cadastros/
    ├── form_pessoa.html
    │
    └── modais/
        ├── form_formacao.html
        ├── form_experiencia.html
        ├── form_historico.html
        ├── form_pendencia.html
        └── form_capacidade.html
```

O importante não é o nome exato das pastas.

O importante é separar responsabilidades.

Cada entidade relacionada deverá possuir seu próprio:

```text
ModelForm
View
URL
template parcial/modal
validação
CRUD
```

sem deixar de aparecer integrada ao cadastro da Pessoa.

---

# 7. Regra fundamental: Pessoa precisa existir antes dos filhos

Uma entidade relacionada não deve ser criada antes que Pessoa possua uma Primary Key.

Exemplo:

```text
FormacaoDocente
    pessoa = ForeignKey(Pessoa)
```

Para gravar:

```text
FormacaoDocente
pessoa_id = 35
```

a Pessoa de ID 35 precisa existir.

Portanto existem dois estados diferentes da tela.

---

# 8. ESTADO 1 — Pessoa nova, ainda não persistida

URL conceitual:

```text
/cadastros/pessoas/nova/
```

Nesse momento:

```text
pessoa.pk = None
```

O usuário pode preencher:

```text
Nome
CPF
Data de nascimento
E-mail
Endereço
Função
etc.
```

Se ele simplesmente clicar em:

```text
Salvar
```

o comportamento deverá ser o CREATE normal da Pessoa.

Mas existe outro cenário.

O usuário preenche os dados da Pessoa e antes de clicar no botão principal Salvar clica em:

```text
+ Adicionar Formação
```

Esse botão deve possuir um comportamento especial.

---

# 9. Comportamento de "+ Adicionar" quando Pessoa ainda não existe

Ao clicar:

```text
+ Adicionar Formação
```

devem ocorrer logicamente duas operações sequenciais:

```text
1. validar e persistir Pessoa
2. abrir cadastro de Formação
```

Fluxo:

```text
Pessoa nova
      ↓
usuário preenche dados
      ↓
+ Adicionar Formação
      ↓
validar Pessoa
      ↓
dados inválidos?
   ├── SIM → permanecer na tela mostrando erros
   │
   └── NÃO
         ↓
      salvar Pessoa
         ↓
      obter pessoa.pk
         ↓
      exemplo: pessoa.pk = 35
         ↓
      entrar no modo de edição da Pessoa 35
         ↓
      abrir modal "Adicionar Formação"
```

Depois dessa primeira persistência, a Pessoa não deverá voltar a ser tratada como uma nova Pessoa.

---

# 10. Estratégia recomendada para a PRIMEIRA IMPLEMENTAÇÃO

Como o CRUD ainda está em desenvolvimento, NÃO começar tornando tudo AJAX.

Primeiro implementar uma solução tradicional e robusta usando Django.

Uma estratégia recomendada é usar um parâmetro indicando qual ação deve ocorrer depois de salvar Pessoa.

Exemplo conceitual:

```text
acao_pos_salvar = formacao
```

ou:

```text
next_action = add_formacao
```

O botão:

```text
+ Adicionar Formação
```

pode enviar o formulário principal informando que, depois de persistir Pessoa, o sistema deve abrir o cadastro de Formação.

Fluxo:

```text
POST /pessoas/nova/
      ↓
PessoaForm.is_valid()
      ↓
Pessoa salva
      ↓
id = 35
      ↓
redirect
      ↓
/pessoas/35/editar/?modal=formacao
```

A tela continua visualmente sendo a mesma página.

Depois do redirecionamento, o JavaScript percebe:

```text
?modal=formacao
```

e abre automaticamente:

```text
Modal Formação
```

Isso evita, na primeira implementação:

- AJAX complexo;
- criação duplicada de Pessoa;
- manipulação complicada de estado;
- dependência excessiva de JavaScript;
- dificuldade de depuração.

Depois que tudo estiver funcional, o fluxo poderá ser aprimorado com `fetch()` sem mudar a arquitetura do backend.

---

# 11. ESTADO 2 — Pessoa já persistida

Quando estivermos em:

```text
/cadastros/pessoas/35/editar/
```

já sabemos:

```python
pessoa.pk == 35
```

Então os botões relacionados não precisam mais salvar Pessoa para obter uma FK.

Exemplo:

```text
+ Adicionar Formação
```

pode simplesmente abrir:

```text
Modal Formação
```

e posteriormente realizar:

```text
POST /cadastros/pessoas/35/formacoes/nova/
```

O Django recebe o formulário e associa obrigatoriamente:

```python
formacao.pessoa = pessoa
```

onde Pessoa é obtida pelo servidor a partir da URL.

---

# 12. Não confiar no pessoa_id enviado pelo navegador

IMPORTANTE para integridade.

Não implementar algo como:

```html
<input type="hidden" name="pessoa_id" value="35">
```

e simplesmente confiar nesse valor.

O relacionamento deve preferencialmente ser determinado no backend.

Exemplo conceitual:

```python
pessoa = get_object_or_404(Pessoa, pk=pessoa_id)

registro = form.save(commit=False)
registro.pessoa = pessoa
registro.save()
```

Assim, a FK é controlada pelo servidor.

---

# 13. CRUD de Pessoa

Antes da arquitetura dos modais ser considerada concluída, implementar corretamente pelo menos:

```text
CREATE Pessoa
READ Pessoa
UPDATE Pessoa
```

DELETE poderá ser implementado de acordo com as regras de negócio.

Rotas conceituais:

```text
/cadastros/pessoas/nova/
/cadastros/pessoas/<pk>/
/cadastros/pessoas/<pk>/editar/
```

Os nomes reais podem utilizar `name=` apropriados e namespaces Django.

Exemplo conceitual:

```text
cadastros:pessoa_create
cadastros:pessoa_detail
cadastros:pessoa_update
```

---

# 14. CRUD das entidades relacionadas

Cada entidade deverá possuir seu CRUD próprio.

## Formação Docente

Exemplos conceituais:

```text
/pessoas/35/formacoes/nova/
/formacoes/81/editar/
/formacoes/81/excluir/
```

## Experiência Profissional

```text
/pessoas/35/experiencias/nova/
/experiencias/42/editar/
/experiencias/42/excluir/
```

## Histórico de Vínculo

```text
/pessoas/35/historicos/novo/
/historicos/17/editar/
/historicos/17/excluir/
```

## Pendência

```text
/pessoas/35/pendencias/nova/
/pendencias/26/editar/
/pendencias/26/excluir/
```

## Capacidade

```text
/pessoas/35/capacidades/nova/
/capacidades/52/editar/
/capacidades/52/excluir/
```

Os nomes definitivos deverão seguir os Models reais e a convenção já existente no projeto.

---

# 15. ModelForms próprios

Não concentrar todos esses registros no `PessoaForm`.

Deve existir separação semelhante a:

```text
PessoaForm

FormacaoDocenteForm

ExperienciaProfissionalForm

HistoricoVinculoForm

PendenciaForm

CapacidadeForm
```

Cada ModelForm deve validar somente sua entidade.

Django deverá continuar sendo responsável pela validação efetiva.

JavaScript pode ajudar na interface, mas não substitui:

```python
form.is_valid()
```

---

# 16. Comportamento do modal

Exemplo de Formação:

```text
┌────────────────────────────────────────────┐
│ ADICIONAR FORMAÇÃO                         │
│                                            │
│ Tipo:       [Graduação                ▼]  │
│ Curso:      [Engenharia                  ] │
│ Entidade:   [UNITAU                      ] │
│ Cidade:     [Taubaté                     ] │
│ UF:         [SP                       ▼]  │
│ Ano:        [2020                        ] │
│                                            │
│ [Cancelar]                     [Salvar]    │
└────────────────────────────────────────────┘
```

Ao clicar em Salvar:

```text
ModelForm
   ↓
validação Django
   ↓
válido?
  ├─ NÃO
  │    ↓
  │ mostrar erros no próprio modal
  │
  └─ SIM
       ↓
   salvar registro
       ↓
   FK = Pessoa atual
       ↓
   atualizar tabela
```

---

# 17. Tabelas passam a representar registros reais

Depois da alteração:

```text
FORMAÇÃO

ID   Tipo        Curso          Entidade       Ações
-------------------------------------------------------
81   Graduação   Engenharia     UNITAU          Editar Excluir
94   Técnico     Mecânica       SENAI           Editar Excluir
```

O ID pode não ser exibido ao usuário, mas deverá existir internamente.

Cada linha representa um objeto real:

```text
FormacaoDocente(pk=81)
FormacaoDocente(pk=94)
```

Portanto:

```text
linha HTML = objeto existente no banco
```

Essa regra deve valer para todas as tabelas relacionadas.

---

# 18. EDITAR registro relacionado

Cada linha deve futuramente possuir:

```text
[Editar]
```

Ao clicar:

```text
Editar
   ↓
obter registro pelo PK
   ↓
abrir modal preenchido
   ↓
alterar dados
   ↓
ModelForm(instance=registro)
   ↓
save()
   ↓
atualizar tabela
```

Não editar uma cópia temporária no DOM.

Editar sempre o registro real.

---

# 19. EXCLUIR registro relacionado

Cada linha deverá possuir:

```text
[Excluir]
```

O fluxo deverá ser:

```text
Excluir
   ↓
confirmação
   ↓
POST para endpoint de exclusão
   ↓
Django verifica registro
   ↓
Django verifica pertencimento à Pessoa
   ↓
registro.delete()
   ↓
atualiza tabela
```

Preferir POST para exclusão.

Não utilizar GET para realizar exclusões.

---

# 20. Segurança da relação Pessoa × registro

Ao editar ou excluir um registro relacionado, verificar a relação.

Exemplo:

```text
Pessoa 35
Formação 81
```

O servidor deve garantir que:

```text
Formação 81 pertence à Pessoa 35
```

Especialmente se a URL tiver ambos os identificadores.

Não confiar apenas na informação presente no navegador.

---

# 21. O papel do JavaScript depois da refatoração

JavaScript continuará sendo utilizado.

Mas sua responsabilidade será diferente.

Hoje ele participa do mecanismo de persistência indireta:

```text
clonar
reindexar
guardar formulário oculto
controlar TOTAL_FORMS
```

Na arquitetura nova, JavaScript deverá cuidar predominantemente de:

```text
abrir modal
fechar modal
carregar formulário
enviar formulário opcionalmente via fetch
exibir erros
atualizar visualmente tabela
confirmar exclusão
mostrar/esconder blocos da interface
```

Persistência permanece responsabilidade de:

```text
Django
ModelForm
Model
Banco
```

---

# 22. O código de categoria deve ser preservado

O atual `form-dinamico.js` possui duas responsabilidades diferentes:

```text
1. mostrar/esconder blocos conforme categoria
2. administrar formsets dinâmicos
```

A lógica de categoria não deve ser descartada junto com os formsets.

Ela poderá continuar existindo.

Idealmente, posteriormente separar responsabilidades.

Exemplo:

```text
cadastros/static/cadastros/js/
│
├── buscar-cep.js
├── categorias-pessoa.js
└── relacionados-pessoa.js
```

Onde:

```text
categorias-pessoa.js
```

controla:

```text
data-categoria
DOCENTE
DISCENTE
GESTAO
```

e:

```text
relacionados-pessoa.js
```

controla os modais e os CRUDs relacionados.

Essa divisão é recomendada, mas não precisa ser feita imediatamente.

---

# 23. O que será removido da arquitetura final

Depois que todos os CRUDs relacionados estiverem implementados, remover dos respectivos blocos:

```text
formset management_form
```

por exemplo:

```django
{{ formacao_formset.management_form }}
```

e remover:

```html
<div class="formset-hidden" style="display:none"></div>
```

Também deixará de ser necessária a lógica associada a:

```javascript
cloneNode(true)
```

```javascript
TOTAL_FORMS
```

reindexação:

```text
formacao-0-campo
formacao-1-campo
formacao-2-campo
```

e cópia manual do estado dos `<select>`.

A arquitetura não deverá depender mais de clones ocultos para persistência.

---

# 24. NÃO remover tudo imediatamente

A migração deve ser incremental.

Não refatorar simultaneamente todos os blocos.

Escolher primeiro uma entidade piloto.

Recomendação:

```text
FormacaoDocente
```

porque possui:

- vários campos;
- um `<select>`;
- relação com Pessoa;
- tabela;
- necessidade futura de Editar/Excluir;
- é um bom exemplo para validar toda a arquitetura.

Depois que Formação funcionar completamente, reproduzir o padrão nas demais entidades.

---

# 25. Ordem de implementação recomendada

## ETAPA 1 — revisar estrutura atual

Antes de alterar código, analisar:

```text
models.py
forms.py
views.py
urls.py
form_pessoa.html
form-dinamico.js
```

Identificar:

- Model Pessoa;
- PK de Pessoa;
- Foreign Keys existentes;
- Models relacionados;
- nomes reais dos campos;
- validações existentes;
- `on_delete`;
- constraints;
- `related_name`;
- formsets existentes;
- comportamento atual da view de Pessoa.

NÃO inventar Models novos se eles já existirem.

---

## ETAPA 2 — concluir CREATE de Pessoa

Garantir:

```text
PessoaForm
→ validação
→ Pessoa.objects...
→ registro persistido
→ PK disponível
```

Ao salvar Pessoa nova, redirecionar para sua URL de edição.

Exemplo:

```text
/pessoas/nova/
          ↓
save
          ↓
Pessoa 35
          ↓
/pessoas/35/editar/
```

Isso é importante para evitar reenvio de formulário e duplicação.

Usar padrão:

```text
POST
↓
REDIRECT
↓
GET
```

Post/Redirect/Get.

---

## ETAPA 3 — implementar UPDATE de Pessoa

A mesma tela deverá atender Pessoa já existente.

Exemplo:

```text
/pessoas/35/editar/
```

A view deverá carregar:

```text
PessoaForm(instance=pessoa)
```

e também consultar os registros relacionados já persistidos.

Exemplo conceitual:

```python
formacoes = ...
experiencias = ...
historicos = ...
pendencias = ...
capacidades = ...
```

Utilizar os relacionamentos reais existentes no Model.

---

## ETAPA 4 — implementar Formação como CRUD piloto

Criar/ajustar:

```text
FormacaoDocenteForm
```

Criar:

```text
formacao_create
formacao_update
formacao_delete
```

Criar URLs.

Criar template parcial/modal.

Na tela da Pessoa, consultar e apresentar as formações existentes.

---

## ETAPA 5 — botão "+ Adicionar Formação"

Para Pessoa existente:

```text
botão
↓
abre modal
↓
preenche
↓
Salvar
↓
Django
↓
FormacaoDocente
↓
FK Pessoa
```

Para Pessoa nova:

```text
botão
↓
salva Pessoa
↓
redirect para edição
↓
abre automaticamente modal Formação
```

---

## ETAPA 6 — Editar e Excluir Formação

Completar o CRUD piloto antes de copiar o padrão.

Somente considerar Formação concluída quando possuir:

```text
CREATE
READ/listagem
UPDATE
DELETE
```

---

## ETAPA 7 — replicar arquitetura

Depois aplicar o padrão a:

```text
ExperienciaProfissional
HistoricoVinculo
Pendencia
Capacidade
```

e posteriormente às demais entidades relacionadas.

---

## ETAPA 8 — retirar Formsets antigos

Somente depois que uma entidade estiver funcionando no novo padrão, retirar daquela entidade:

```text
management_form
formset-template
formset-hidden
cloneNode
TOTAL_FORMS
```

Evitar uma migração "big bang".

---

# 26. Primeira versão pode funcionar sem AJAX

IMPORTANTE:

Modal não implica obrigatoriamente AJAX.

A primeira versão pode utilizar formulários tradicionais Django.

Fluxo:

```text
Modal
  ↓
POST
  ↓
Django
  ↓
save
  ↓
redirect para Pessoa
```

Exemplo:

```text
POST /pessoas/35/formacoes/nova/
                ↓
salva
                ↓
redirect
                ↓
/pessoas/35/editar/#formacoes
```

Essa solução é mais simples para:

- testar;
- depurar;
- validar Models;
- validar ModelForms;
- validar Foreign Keys;
- validar URLs;
- validar regras de negócio.

Depois poderá ser adicionada uma camada AJAX.

---

# 27. Segunda versão: AJAX/fetch como melhoria de interface

Quando o CRUD tradicional estiver funcionando, poderá ser implementado:

```javascript
fetch()
```

Fluxo:

```text
Modal
 ↓
fetch POST
 ↓
Django
 ↓
ModelForm
 ↓
JSON
 ↓
JS
 ↓
fecha modal
 ↓
atualiza tabela sem recarregar página
```

Exemplo de resposta conceitual:

```json
{
    "success": true,
    "id": 81
}
```

ou, em caso de erro:

```json
{
    "success": false,
    "errors": {
        "curso": ["Este campo é obrigatório."]
    }
}
```

Não implementar manualmente no JavaScript regras de validação que já pertencem ao Django.

---

# 28. Outra alternativa válida para AJAX

Em vez de retornar dados JSON e reconstruir a linha inteira pelo JavaScript, o Django pode retornar HTML renderizado de um template parcial.

Exemplo:

```text
partials/_linha_formacao.html
```

Django renderiza:

```html
<tr data-id="81">
    ...
</tr>
```

e JavaScript apenas insere o HTML recebido.

Essa alternativa reduz duplicação entre:

```text
HTML definido no template Django
```

e:

```text
HTML construído manualmente no JavaScript
```

É uma abordagem interessante para este projeto.

---

# 29. CSRF

Todos os POSTs devem continuar protegidos por CSRF.

Em formulário tradicional:

```django
{% csrf_token %}
```

Em `fetch()`, enviar corretamente o token CSRF conforme o padrão Django.

Não desativar CSRF para simplificar AJAX.

---

# 30. Transações e comportamento quando Formação falhar

Considerar Pessoa e registros relacionados como operações independentes depois da persistência inicial.

Exemplo:

```text
Pessoa salva com ID 35
↓
usuário tenta adicionar Formação
↓
Formação contém erro
```

Resultado esperado:

```text
Pessoa 35 continua salva
Formação não é salva
Modal apresenta erros
```

Não apagar ou reverter Pessoa porque a Formação apresentou erro.

Essa independência é desejável.

---

# 31. Evitar duplicação de Pessoa

A primeira persistência deve alterar claramente o estado da tela de:

```text
CREATE
```

para:

```text
UPDATE
```

Depois que Pessoa possuir ID, os novos POSTs da tela principal deverão atualizar aquela Pessoa.

Nunca criar uma nova Pessoa a cada clique em:

```text
+ Adicionar
```

Por isso o redirect para:

```text
/pessoas/<pk>/editar/
```

é importante.

---

# 32. Tratamento do botão principal Salvar

O botão principal:

```text
Salvar
```

continua existindo.

Com Pessoa nova:

```text
Salvar
→ CREATE
→ redirect para editar
```

Com Pessoa existente:

```text
Salvar
→ UPDATE
→ redirect/feedback
```

Os botões:

```text
+ Adicionar Formação
+ Adicionar Experiência
+ Adicionar Capacidade
...
```

não deverão fazer parte do mesmo Formset.

Eles representam ações independentes sobre entidades relacionadas.

---

# 33. Alterações não salvas na Pessoa

Há um ponto importante.

Imagine Pessoa 35 já existente.

O usuário altera:

```text
telefone
endereço
e-mail
```

mas ainda não clicou em Salvar.

Depois clica:

```text
+ Adicionar Formação
```

É necessário definir comportamento consistente.

Recomendação inicial:

Ao acionar qualquer botão de cadastro relacionado, salvar/validar também as alterações pendentes do formulário principal antes de abrir o modal.

Assim evita-se:

```text
usuário acredita que modificou Pessoa
↓
abre modal
↓
navegação/reload
↓
alterações são perdidas
```

Portanto, conceitualmente:

```text
+ Adicionar relacionado
        ↓
PessoaForm possui alterações?
        ↓
validar/salvar Pessoa
        ↓
abrir modal
```

Porém, depois que a interface utilizar AJAX completamente, essa regra pode ser refinada.

O principal requisito é nunca perder silenciosamente alterações da Pessoa.

---

# 34. Blocos por categoria

O sistema atualmente utiliza:

```html
data-categoria="DISCENTE"
data-categoria="DOCENTE"
data-categoria="GESTAO"
data-categoria="DOCENTE,GESTAO"
```

Essa lógica deve permanecer.

Quando Função determinar a categoria:

```text
DISCENTE
DOCENTE
GESTAO
```

mostrar os blocos aplicáveis.

Porém, ocultar visualmente um campo não deve ser a única regra de segurança ou negócio.

O backend deverá continuar validando o que pode ou não ser associado àquela Pessoa, conforme as regras reais do projeto.

---

# 35. Arquitetura conceitual final

```text
NAVEGADOR
│
│
├── form_pessoa.html
│     │
│     ├── PessoaForm
│     │
│     ├── tabela Formação
│     ├── tabela Experiência
│     ├── tabela Histórico
│     ├── tabela Pendências
│     └── tabela Capacidades
│
│
├── Modal Formação
├── Modal Experiência
├── Modal Histórico
├── Modal Pendência
└── Modal Capacidade
       │
       ↓
URLs Django
       │
       ↓
Views
       │
       ↓
ModelForms
       │
       ↓
Models
       │
       ↓
BANCO DE DADOS
       │
       ├── Pessoa
       ├── FormacaoDocente
       ├── ExperienciaProfissional
       ├── Historico...
       ├── Pendencia...
       └── Capacidade
```

---

# 36. Responsabilidade de cada camada

## Template

Responsável por:

```text
estrutura visual
campos
tabelas
botões
modais
exibição de erros
```

Não responsável por persistência.

---

## JavaScript

Responsável por:

```text
comportamento da interface
modal
fetch opcional
atualização visual
categorias
interações
```

Não deve ser a fonte da verdade dos registros persistidos.

---

## Django View

Responsável por:

```text
receber requisição
obter Pessoa
instanciar ModelForm
validar
associar Foreign Key
salvar
editar
excluir
responder/redirect
```

---

## ModelForm

Responsável por:

```text
campos permitidos
validação
normalização dos dados
mensagens de erro
```

---

## Model

Responsável por:

```text
estrutura da entidade
relacionamentos
constraints
regras intrínsecas ao dado
```

---

## Banco

Fonte definitiva dos registros.

---

# 37. Fonte da verdade

Depois da refatoração, a regra deverá ser:

```text
Banco de dados = fonte da verdade
```

Não:

```text
DOM escondido = fonte temporária
```

Quando carregar Pessoa 35:

```text
Django consulta o banco
↓
renderiza as tabelas
```

A página deve conseguir ser fechada e aberta novamente sem perder nenhum registro já adicionado.

---

# 38. Não usar acesso direto às tabelas SQL

Embora as tabelas possam possuir nomes como:

```text
cadastros_formacaodocente
cadastros_experienciaprofissional
cadastros_capacidades
```

utilizar preferencialmente Django ORM.

Exemplo conceitual:

```python
FormacaoDocente.objects...
```

e não SQL manual.

Respeitar os Models existentes.

---

# 39. Foreign Keys

Antes de alterar qualquer Model, verificar se as Foreign Keys já existem.

Conceitualmente espera-se algo semelhante a:

```text
FormacaoDocente
    → pessoa

ExperienciaProfissional
    → pessoa

Capacidade
    → pessoa
```

Mas NÃO modificar `on_delete`, `related_name`, constraints ou migrations sem analisar o código e as regras existentes.

Não assumir automaticamente `CASCADE`.

---

# 40. Deleção de Pessoa

A arquitetura deve estar preparada para a seguinte questão futura:

```text
O que acontece quando Pessoa é excluída?
```

Como existem vários registros dependentes, a decisão depende das regras do sistema.

Pode envolver:

```text
CASCADE
PROTECT
RESTRICT
soft delete
Pessoa.ativo = False
```

Não definir isso arbitrariamente nesta refatoração.

Analisar primeiro o Model e as regras do sistema.

---

# 41. Identificação interna de linhas

Cada linha relacionada deve possuir internamente seu PK.

Por exemplo:

```html
<tr data-id="81">
```

ou utilizar a PK diretamente nas URLs dos botões.

Isso permitirá:

```text
Editar registro 81
Excluir registro 81
```

Não identificar registros pelo número da linha da tabela.

---

# 42. Não usar índice visual como identidade

Na arquitetura antiga existiam índices:

```text
formacao-0
formacao-1
formacao-2
```

Eles eram índices do Formset.

Na nova arquitetura:

```text
PK do banco
```

é a identidade.

Exemplo:

```text
Formação PK 81
Formação PK 94
```

Isso é mais robusto.

---

# 43. Testes mínimos

Criar testes principalmente para o backend.

## Pessoa

Testar:

```text
CREATE válido
CREATE inválido
UPDATE
```

## Formação

Testar:

```text
criar Formação para Pessoa existente
não criar Formação inválida
associar FK correta
editar
excluir
```

## Segurança da relação

Testar que um registro pertencente à Pessoa A não seja alterado indevidamente por uma rota referente à Pessoa B.

## Campos Select

O problema antigo de `<select>` deixa de depender de `cloneNode`.

Ainda assim testar que valores como:

```text
tipo_formacao
vinculo_formal
tipo de pendência
```

sejam persistidos corretamente.

---

# 44. Critério para considerar a migração de uma entidade concluída

Por exemplo, Formação somente estará concluída quando:

1. Pessoa persistida possui PK;
2. botão Adicionar Formação funciona;
3. formulário específico abre;
4. ModelForm valida;
5. registro é persistido com FK correta;
6. registro aparece na tabela;
7. recarregar página mantém registro;
8. Editar funciona;
9. Excluir funciona;
10. erros aparecem corretamente;
11. não existe clone oculto;
12. não depende de `TOTAL_FORMS`;
13. não depende de índice do Formset.

Depois disso, usar Formação como padrão para os outros CRUDs.

---

# 45. Estratégia de refatoração

NÃO reescrever todo o projeto.

Executar incrementalmente:

```text
1. estabilizar Pessoa
2. criar CRUD Formação
3. substituir somente o formset Formação
4. testar
5. migrar Experiência
6. testar
7. migrar Histórico
8. testar
9. migrar Pendências
10. testar
11. migrar Capacidades
12. limpar JavaScript antigo
```

Sempre preservar partes funcionando enquanto outra entidade está sendo migrada.

---

# 46. Resultado arquitetural desejado

Ao final, quero possuir uma interface semelhante à atual, porém com arquitetura:

```text
Pessoa
→ entidade principal persistida

Formação
→ registros próprios persistidos

Experiência
→ registros próprios persistidos

Histórico
→ registros próprios persistidos

Pendências
→ registros próprios persistidos

Capacidades
→ registros próprios persistidos
```

Todos relacionados por FK.

A interface deve continuar parecendo uma única ficha/cadastro de Pessoa.

Os templates separados existem apenas para modularizar o código e alimentar os modais/componentes da mesma tela.

---

# 47. Fluxo final resumido — Pessoa nova

```text
/pessoas/nova/
        ↓
preenche Pessoa
        ↓
+ Adicionar Formação
        ↓
validar PessoaForm
        ↓
salvar Pessoa
        ↓
Pessoa.pk = 35
        ↓
redirect /pessoas/35/editar/?modal=formacao
        ↓
abre modal Formação
        ↓
preenche Formação
        ↓
salvar
        ↓
FormacaoDocente(pessoa_id=35)
        ↓
registro aparece na tabela
```

---

# 48. Fluxo final resumido — Pessoa existente

```text
/pessoas/35/editar/
        ↓
+ Adicionar Formação
        ↓
abre modal
        ↓
preenche
        ↓
POST
        ↓
FormacaoDocenteForm
        ↓
form.is_valid()
        ↓
registro.pessoa = Pessoa 35
        ↓
save()
        ↓
tabela atualizada
```

---

# 49. Fluxo final resumido — edição

```text
Pessoa 35
↓
Formação 81
↓
Editar
↓
modal preenchido
↓
POST
↓
ModelForm(instance=Formação 81)
↓
save
↓
tabela atualizada
```

---

# 50. Fluxo final resumido — exclusão

```text
Pessoa 35
↓
Formação 81
↓
Excluir
↓
confirmar
↓
POST
↓
Django verifica propriedade
↓
delete
↓
tabela atualizada
```

---

# 51. Diretriz específica sobre `cloneNode()`

Não gastar mais esforço tentando transformar o mecanismo baseado em:

```javascript
cloneNode(true)
```

na arquitetura permanente.

A correção atual dos `<select>` pode continuar temporariamente enquanto a migração não for concluída.

Entretanto, o objetivo é eliminar completamente o uso de clones ocultos como mecanismo para armazenar dados que posteriormente serão enviados ao banco.

`cloneNode()` pode eventualmente continuar sendo utilizado para algum efeito puramente visual, mas não deve participar da persistência dos registros relacionados.

---

# 52. Diretriz para implementação pela IA

Antes de produzir alterações definitivas:

1. analisar os arquivos existentes;
2. não presumir nomes de Models;
3. não presumir nomes de Foreign Keys;
4. não criar Models duplicados;
5. não alterar migrations desnecessariamente;
6. preservar regras existentes;
7. preservar `buscar-cep.js`;
8. preservar a lógica `data-categoria`;
9. separar a lógica dos formsets da lógica de categoria;
10. implementar primeiro Pessoa;
11. usar Formação como CRUD piloto;
12. testar o fluxo completo;
13. somente depois replicar o padrão.

Quando for necessário alterar código, apresentar claramente:

```text
arquivo
trecho atual
trecho novo
motivo da alteração
```

Evitar reescrever arquivos inteiros desnecessariamente.

---

# 53. Arquitetura escolhida em uma frase

A arquitetura definitiva será:

> **Uma Pessoa persistida como entidade principal e vários CRUDs independentes de entidades relacionadas por Foreign Key, apresentados visualmente dentro da mesma tela através de tabelas e formulários modais, eliminando o armazenamento temporário baseado em Django Formsets, `cloneNode()`, `TOTAL_FORMS` e formulários ocultos.**

Essa é a direção arquitetural que deve orientar as próximas alterações do projeto.