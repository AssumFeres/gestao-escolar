# Andamento do Projeto — 42

**Data:** 09/09/2026  
**Branch:** `dev`  
**Sessão dedicada a: fechamento da regra de exclusividade da Função Discente e padronização visual/estrutural das telas de Lista, Detalhe e Cadastro de Pessoa.**

---

## 1. Contexto

A sessão concentrou duas frentes principais do módulo `cadastros`:

1. **regra de negócio de Funções**, especialmente a exclusividade da categoria Discente; e
2. **melhoria de UX**, reorganizando a forma como os dados de Pessoa são pesquisados, exibidos e cadastrados.

A regra adotada para toda a reorganização visual foi preservar integralmente os dados já existentes no sistema: **nenhum campo deveria ser removido da interface durante a mudança de layout**.

Arquivos principalmente envolvidos nesta sessão:

- `cadastros/services.py`
- `cadastros/views.py`
- `cadastros/templates/cadastros/lista.html`
- `cadastros/templates/cadastros/detalhe.html`
- `cadastros/templates/cadastros/form_pessoa.html`
- CSS base/global utilizado pelo módulo de cadastros

---

## 2. Regra de negócio — exclusividade da Função Discente

### 2.1 — Problema identificado

A regra existente protegia apenas um dos sentidos:

- se a Pessoa já possuía **Discente ativo**, não podia receber outra Função.

Porém, o sentido inverso ainda era possível:

- uma Pessoa com **Docente ativo** ou **Gestão ativa** ainda podia ser cadastrada como Discente.

Isso deixava a regra assimétrica.

### 2.2 — Regra final definida

A regra foi fechada da seguinte forma:

- **Discente ativo → Docente:** bloqueado.
- **Discente ativo → Gestão:** bloqueado.
- **Docente ativo → Discente:** bloqueado.
- **Gestão ativa → Discente:** bloqueado.
- **Docente + Gestão:** permitido.
- Funções **INATIVAS** não impedem novo vínculo.
- Um ex-Discente pode futuramente assumir Docente/Gestão.
- Um ex-Docente ou ex-Gestor pode futuramente assumir Discente.
- Uma passagem antiga como Discente nunca é reaberta; se houver novo vínculo, cria-se nova `AtribuicaoFuncao`.

### 2.3 — `CadastrarPessoaComFuncaoService`

O `CadastrarPessoaComFuncaoService` foi alterado para consultar as atribuições ativas da Pessoa antes de criar uma nova atribuição.

Foi acrescentado `SituacaoAtribuicao` aos imports locais do Service e criada a validação das categorias ativas.

A nova lógica impede:

- qualquer nova Função quando já existe Discente ativo;
- criação de Discente quando já existe Docente ou Gestão ativa.

A criação de **Docente + Gestão** continua liberada.

### 2.4 — Segundo caminho protegido: `ObterOuCriarAtribuicaoDiscenteService`

Foi identificado um segundo caminho capaz de criar Discente: o `ObterOuCriarAtribuicaoDiscenteService`, usado no fluxo de matrícula em Turma.

Antes da correção, esse Service:

1. procurava Discente ativo;
2. se não encontrasse, criava uma nova atribuição Discente.

Não havia verificação de Docente/Gestão ativa nesse fluxo.

O Service foi alterado para:

1. reaproveitar o Discente ativo, se existir;
2. verificar se há outra Função ativa;
3. bloquear a criação de Discente quando existir Docente ou Gestão ativa;
4. criar nova atribuição Discente somente quando a regra permitir.

### 2.5 — Teste manual

A correção foi testada na interface.

Ao tentar cadastrar como Discente uma Pessoa que já possuía Docente/Gestão ativa, o sistema bloqueou corretamente com a mensagem:

> Esta pessoa já possui uma Função ativa de Docente ou Gestão e não pode ser cadastrada como Discente enquanto esse vínculo estiver ativo.

**Resultado:** regra funcionando conforme esperado.

Nenhuma alteração de Model foi necessária; portanto, **não houve `makemigrations` nem `migrate`** nesta correção.

---

## 3. Tratamento amigável do `ValidationError`

### 3.1 — Problema visual

A mensagem de regra de negócio inicialmente aparecia na tela assim:

```text
['Esta pessoa já possui uma Função ativa de Docente ou Gestão ...']
```

Os colchetes e aspas vinham do uso de:

```python
form.add_error(None, str(e))
```

### 3.2 — Correção

Na View do formulário HTML, o erro passou a ser entregue diretamente ao Django:

```python
form.add_error(None, e)
```

Com isso, o `ValidationError` passou a ser renderizado corretamente por `form.non_field_errors`, sem representação de lista.

**Resultado final:**

```text
Esta pessoa já possui uma Função ativa de Docente ou Gestão e não pode ser cadastrada como Discente enquanto esse vínculo estiver ativo.
```

---

## 4. Padronização visual das mensagens de erro

A apresentação de `form.non_field_errors` foi centralizada no CSS para evitar estilos diferentes em cada formulário.

O bloco HTML passou a utilizar a classe `.erro`, permitindo que todos os formulários sigam o mesmo padrão visual.

Foi adotado:

- fundo de erro: `#F2DEDE`;
- borda em tom suave de vermelho;
- texto em vermelho escuro;
- espaçamento interno;
- `border-radius`;
- remoção do marcador padrão da `<ul class="errorlist">`;
- inclusão do ícone de atenção `⚠️`;
- ajuste de tamanho/alinhamento do ícone.

A decisão foi manter o tratamento no CSS, e não repetir estilos inline em cada template.

---

## 5. Lista de Pessoas — busca, filtros e exibição

### 5.1 — Filtros adicionados

A `ListaPessoasView` passou a permitir pesquisa e filtragem por:

- **Nome** — busca parcial com `icontains`;
- **Situação da Pessoa** — Todos / Ativos / Inativos;
- **Categoria da Função** — Discente / Docente / Gestão.

Também foi aplicado:

- `prefetch_related('atribuicoes__funcao')`;
- ordenação alfabética por nome;
- `Lower('nome_completo')` para ordenação sem depender de caixa;
- `distinct()` no filtro por categoria, evitando duplicidade de Pessoas quando há mais de uma atribuição correspondente.

Os filtros utilizados são devolvidos ao contexto para permanecerem preenchidos após a pesquisa.

### 5.2 — Melhoria na coluna Categoria/Função

A tabela mostrava informações como:

```text
Discente - Discente - Aluno
```

Isso acontecia porque a interface concatenava:

- categoria: `Discente`;
- nome da Função: `Discente - Aluno`.

Foi decidido **não alterar o cadastro de Funções**, pois Categoria e Função cumprem papéis diferentes:

- **Categoria** é uma classificação utilizada pelo sistema;
- **Função** é o nome operacional apresentado ao usuário.

A coluna foi simplificada para exibir somente:

```text
Discente - Aluno
Docente - Instrutor
Coordenador
...
```

A categoria permanece disponível para filtros e regras, mas deixa de poluir a leitura da tabela.

**Resultado:** lista mais clara para a secretaria e demais usuários comuns.

---

## 6. `detalhe.html` — redesenho da ficha da Pessoa

### 6.1 — Problema anterior

A tela de detalhe utilizava principalmente tabelas no formato:

```text
Nome do campo | Valor | Nome do campo | Valor
```

Apesar de funcional, a leitura ficava pesada e pouco semelhante a uma ficha cadastral.

### 6.2 — Novo padrão visual

Os dados individuais passaram a ser apresentados como **cards/campos dentro de grids**, organizados por `fieldset`.

Foi adotado um grid principal de até **4 colunas**, com responsividade para telas menores.

O novo padrão utiliza classes como:

- `.grid-detalhes-4`
- `.dado-detalhe`
- `.dado-rotulo`
- `.dado-valor`
- classes de `span` para campos que precisam ocupar mais espaço

As tabelas foram mantidas somente onde fazem sentido: registros repetíveis e históricos.

### 6.3 — Organização dos dados cadastrais

Os dados da Pessoa foram reorganizados em agrupamentos visuais, mantendo os campos existentes.

Exemplos de agrupamento:

- Dados Pessoais;
- Documentos;
- Contatos/Identificadores;
- Endereço.

A regra foi utilizar até quatro dados por linha quando a natureza dos campos permitisse.

### 6.4 — Dados do Discente

O bloco de Discente foi refinado para ficar hierarquicamente organizado.

Estrutura final:

```text
Dados do Discente
└── Discente - Aluno
    ├── Código de Matrícula ANAC
    ├── Contatos de Emergência
    │   ├── Nome
    │   ├── Parentesco
    │   ├── Telefone
    │   └── Endereço
    └── Responsável
        ├── Nome
        ├── Qualificação
        ├── Endereço
        ├── Identidade
        ├── Órgão Expedidor
        └── Data de Emissão
```

O `fieldset` principal identifica a Função do Discente e contém dois `fieldset` internos:

- **Contatos de Emergência**
- **Responsável**

Isso melhorou a separação semântica dos dados.

### 6.5 — Filiação

No bloco de Dados Pessoais, `Filiação 1` e `Filiação 2` estavam ficando em linhas diferentes por causa do `span` aplicado ao grid.

O `span` foi removido e os dois campos passaram a ficar lado a lado.

**Resultado:** melhor aproveitamento horizontal e leitura mais natural.

### 6.6 — Decisão de manter tabelas nos registros repetíveis

Não foram transformadas em cards as estruturas em que a leitura tabular é mais adequada:

- Sumário Histórico de Vínculos;
- Pendências de Documentação;
- Formação;
- Disciplinas Habilitadas;
- Experiência Profissional;
- Histórico de Vínculo Formal.

Essas áreas continuam usando tabelas, envolvidas por `fieldset` quando aplicável.

---

## 7. `form_pessoa.html` — reorganização do cadastro

O formulário de cadastro recebeu o mesmo princípio visual da tela de detalhe.

A regra inicial foi:

- 1 campo → uma coluna;
- 2 campos → grid de 2;
- 3 campos → grid de 3;
- mais de 3 → preferencialmente grid de 4.

Durante o refinamento, foram criados grids de 5 e 6 colunas para grupos específicos em que todos os campos devem permanecer na mesma linha.

### 7.1 — Função

Mantido em **grid de 3 colunas**:

- Função;
- Data de início;
- Situação.

### 7.2 — Dados Básicos

Foi decidido manter os cinco campos principais na mesma linha.

Novo **grid de 5 colunas**:

1. Nome Completo
2. CPF
3. Data de Nascimento
4. E-mail
5. Telefone

Os contatos complementares permanecem separados:

- E-mail 2
- Telefone 2 / Celular

em grid de 2 colunas.

### 7.3 — Identificadores

Mantido em **grid de 3 colunas**:

- CANAC;
- RM;
- RA.

### 7.4 — Identificação Ampliada

O bloco anteriormente muito extenso foi dividido por grupos documentais, usando `fieldset` internos.

#### Grupo 1 — Dados Pessoais

Grid de 4 colunas:

- Sexo
- Raça/Cor
- Estado Civil
- Nível de Instrução
- Naturalidade
- UF de Naturalidade
- Nacionalidade

Como são sete campos, são distribuídos em uma linha de quatro e outra de três.

#### Grupo 2 — Identidade (RG)

Grid de 3 colunas:

- Identidade
- Data de Emissão
- Órgão Expedidor

#### Grupo 3 — Passaporte / Permanência

Grid de 2 colunas:

- Passaporte
- Autorização de Permanência

#### Grupo 4 — Título de Eleitor

Grid de 3 colunas:

- Título de Eleitor
- Zona Eleitoral
- Seção Eleitoral

#### Grupo 5 — Filiação

Grid de 2 colunas:

- Filiação 1
- Filiação 2

Essa divisão deixou o formulário mais próximo da lógica dos documentos reais utilizados no cadastro.

### 7.5 — Endereço

Os sete campos de endereço passaram a utilizar grid de 4 colunas:

- CEP;
- Logradouro;
- Número;
- Complemento;
- Bairro;
- Cidade;
- UF.

Distribuição natural: quatro campos na primeira linha e três na segunda.

### 7.6 — Dados do Discente

Mantido o `fieldset` principal **Dados do Discente (FE 007)**.

#### Matrícula

- Código de Matrícula ANAC — campo único.

#### Contato de Emergência

Grid de 4 colunas:

- Nome
- Parentesco
- Telefone
- Endereço

#### Responsável Legal

Grid de 4 colunas:

- Nome
- Endereço
- Identidade
- Órgão Expedidor
- Data de Emissão
- Qualificação

Os seis campos ocupam quatro posições na primeira linha e duas na segunda.

### 7.7 — Formação — FE 008

A Formação possui seis campos:

- Tipo
- Curso
- Entidade
- Cidade
- UF
- Ano

Foi criado um **grid de 6 colunas**, permitindo que todos os seis permaneçam na mesma linha em telas largas.

O comportamento do Formset foi preservado:

- `management_form`;
- `data-prefix`;
- `data-fields`;
- `data-labels`;
- `data-obrigatorios-completos`;
- `data-required`;
- botão `+ Adicionar`;
- tabela de itens adicionados.

### 7.8 — Experiência Profissional

Os quatro campos passaram a ficar em **grid de 4 colunas**:

- Organização;
- Cargo;
- Data de início;
- Data de fim.

O Formset e sua tabela foram preservados.

### 7.9 — Histórico de Vínculo Formal

Mantido em **grid de 3 colunas**:

- Vínculo Formal;
- Data de início;
- Data de fim.

### 7.10 — Requisitos de Contratação

Os dois campos passaram a ficar lado a lado em **grid de 2 colunas**:

- Requisito de Contratação;
- Documento Comprobatório.

### 7.11 — Pendências de Documentação

Mantido em **grid de 2 colunas**:

- Tipo;
- Descrição.

A estrutura dinâmica do Formset foi preservada.

---

## 8. Novas classes de grid no CSS

O CSS já possuía:

- `.grid-2-colunas`
- `.grid-3-colunas`
- `.grid-4-colunas`

Para atender ao novo layout foram acrescentadas:

### Grid de 5 colunas

```css
.grid-5-colunas {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 16px;
    width: 100%;
}
```

### Grid de 6 colunas

```css
.grid-6-colunas {
    display: grid;
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 16px;
    width: 100%;
}
```

Também foi prevista responsividade:

- em larguras intermediárias, grids de 5/6 passam para 3 colunas;
- em telas pequenas, passam para 1 coluna.

A intenção é preservar a leitura em desktop sem quebrar o formulário em resoluções menores.

---

## 9. Decisões de UX consolidadas nesta sessão

- Categoria e Função continuam separadas no domínio, mas a Lista exibe apenas o nome da Função.
- `fieldset` passou a representar agrupamentos semânticos de dados.
- Grid é utilizado para dados individuais.
- Tabela continua sendo utilizada para coleções/históricos.
- Campos relacionados documentalmente ficam agrupados.
- Erros gerais de formulário seguem uma aparência visual única.
- A distribuição em colunas pode variar de 2 a 6 conforme o grupo de dados, em vez de forçar toda a aplicação a um único número de colunas.
- Nenhum campo existente deve ser removido apenas para facilitar o layout.

---

## 10. Estado geral ao final da sessão

| Item | Status |
|---|---|
| Exclusividade Discente → outras Funções | ✅ Corrigida |
| Exclusividade Docente/Gestão → Discente | ✅ Corrigida |
| Fluxo alternativo de criação de Discente pela Turma | ✅ Protegido |
| Mensagem `ValidationError` com `['...']` | ✅ Corrigida no formulário HTML |
| Estilo visual dos erros de formulário | ✅ Padronizado |
| Filtro da Lista por nome | ✅ Implementado |
| Filtro da Lista por Pessoa ativa/inativa | ✅ Implementado |
| Filtro da Lista por categoria | ✅ Implementado |
| Ordenação alfabética da Lista | ✅ Implementada |
| Categoria/Função repetitiva na Lista | ✅ Simplificada para Função |
| `detalhe.html` em formato de ficha | ✅ Reestruturado |
| Dados do Discente agrupados por `fieldset` | ✅ Reestruturados |
| Filiação 1 e 2 lado a lado | ✅ Ajustado |
| Cadastro — Dados Básicos em 5 colunas | ✅ Ajustado |
| Cadastro — Identificação Ampliada por grupos | ✅ Reestruturada |
| Cadastro — Formação em 6 colunas | ✅ Ajustada |
| Cadastro — demais grupos em grids coerentes | ✅ Ajustados |
| Migração de banco nesta sessão | Não necessária |

---

## 11. Pontos para observar em testes futuros

- Testar os novos grids em resoluções menores para confirmar a responsividade real no navegador.
- Confirmar visualmente todos os grupos condicionais para Discente, Docente e Gestão após troca da Função no formulário dinâmico.
- Confirmar que o Formset de Formação continua funcionando normalmente com o grid de 6 colunas, especialmente o botão `+ Adicionar`.
- Confirmar que os Formsets de Experiência, Histórico de Vínculo e Pendências continuam preservando corretamente os valores ao adicionar itens.
- Avaliar futuramente se o formato de erro da API também deve ser normalizado, pois a correção desta sessão foi aplicada ao formulário HTML.
- Manter testes da regra de exclusividade do Discente nos dois caminhos de criação para evitar regressão.

---

## 12. Próximos passos

A estrutura visual de Pessoa ficou consideravelmente mais organizada e coerente entre:

- Lista;
- Cadastro;
- Detalhe;
- mensagens de validação.

O próximo ciclo pode seguir para novos testes funcionais do cadastro já com o layout refinado, verificando principalmente os Formsets e os comportamentos condicionais por categoria de Função antes de avançar para novas funcionalidades.
