# Andamento do Projeto — 28

**Data:** 03/09/2026 (máquina da escola)
**Branch:** `dev` (commits diretos)
**Sessão dedicada a: fechar o item 1 da sequência (busca de Pessoa por CPF, com reaproveitamento/edição de dados) e realizar a auditoria de campos (item 2) contra as fichas oficiais FE 007, FE 008 e FOP 402.**

---

## Contexto

Continuação direta do diário 27. Sequência confirmada no fim daquela sessão:
1. Busca de Pessoa por CPF (esta sessão)
2. Auditoria de campos FE 008/FOP 402 (esta sessão)
3. Editar Atribuição de Função
4. Encerrar Atribuição de Função
5. Adicionar Nova Função a Pessoa existente
6. Limpeza de códigos mortos
7. Validação de CPF (só números/máscara)
8. Máscara de telefone
9. Indicação visual de campos obrigatórios

---

## 1. Busca de Pessoa por CPF — com um bug real descoberto e corrigido

Antes de implementar a tela, uma checagem no `Service` revelou que "reaproveitar/editar dados" **não funcionava de verdade**: `Pessoa.objects.get_or_create(cpf=..., defaults=dados_pessoa)` — quando a Pessoa já existe, o Django **ignora** o parâmetro `defaults` por completo (comportamento documentado do próprio `get_or_create`, não um bug introduzido agora). Ou seja, o sistema sempre soube "reaproveitar" uma Pessoa existente, mas nunca soube **atualizar** os dados dela — mesmo que o formulário trouxesse informação nova ou corrigida.

### Correção no `Service`

- Busca a Pessoa existente **antes** das checagens de duplicidade (RM/RA/CANAC), excluindo a própria Pessoa encontrada dessas checagens (senão o valor dela mesma "colidiria" com ela).
- Quando a Pessoa já existe: atualiza de verdade todos os campos com o que veio do formulário (`setattr` + `save()`), exceto `cpf` (imutável).

### Dois bugs adicionais encontrados e corrigidos no mesmo arquivo

Durante a edição manual do `services.py` (que sofreu o mesmo problema de indentação corrompida já visto antes), a pessoa responsável pediu para eu simplesmente reescrever o arquivo inteiro em vez de continuar investigando byte a byte — decisão correta, mais rápida. Ao reescrever, encontrei 2 problemas reais, não relacionados à correção pedida:

1. **`AtribuicaoFuncao.objects.create(...)` duplicado** — o bloco aparecia 2 vezes seguidas no método, o que criaria 2 `AtribuicaoFuncao` idênticas por cadastro. Bug real, silencioso (nenhum teste cobria esse cenário de duplicação).
2. **`PreencherRequisitosEDisciplinasDocenteService` com campos mortos** — referenciava `dados_docente.experiencia_docente_comprovada`/`formacao_especifica_comprobatoria`, campos que não existem mais em `DadosDocente` desde a migração dos Requisitos de Contratação para `AtribuicaoFuncao` (diário 25). Removido, com nota explicando que esse `Service` nunca chegou a ser conectado a nenhuma tela (a tela de Requisitos foi eliminada na Etapa B) — limpeza completa registrada no Backlog (item 6 da sequência).

### Implementação da busca

- **`BuscarPessoaPorCpfView`** (API) — mesmo padrão de `BuscarCepView` já existente.
- **`PessoaOutputSerializer`** — `ModelSerializer` (não `Serializer` manual, diferente do resto do arquivo) para evitar declarar ~26 campos à mão, já que é só leitura.
- **`buscar-cpf.js`** — ao apertar Enter no campo CPF (só dispara com exatamente 11 dígitos), busca e pré-preenche os campos comuns; mostra um aviso visual "Pessoa já cadastrada"; se não encontrar, não faz nada (cadastro continua normal).

`pytest` — `29 passed`. Testado manualmente com sucesso: CPF novo (nada acontece), CPF existente (pré-preenche + aviso), editar e salvar (confirmado no Admin que o dado foi realmente atualizado).

**Observação da própria pessoa responsável durante o teste:** ao reenviar o formulário para uma Pessoa já existente, uma nova `AtribuicaoFuncao` foi criada mesmo a Pessoa já tendo aquela Função — **comportamento esperado por enquanto**, não um bug do item 1. É exatamente a lacuna que os itens 3-5 da sequência (Editar/Encerrar/Adicionar Função) devem fechar.

**Commit:** `59331b4` — `feat: busca de Pessoa por CPF, com reaproveitamento/edicao de dados (docs/27, item 1)`.

---

## 2. Auditoria de campos — FE 007, FE 008, FOP 402

Documentos lidos na íntegra (`.docx`/`.doc` convertido) e comparados campo a campo contra `form_pessoa.html` + `Pessoa` + `DadosDiscente` + `DadosDocente` + `ExperienciaProfissional` + `AtribuicaoFuncao`.

### Resultado geral: a maior parte já confere

Praticamente todos os campos de identificação, endereço, documentação, Responsável Legal e Contato de Emergência da **FE 007** já existem no sistema, nome por nome. Os **Requisitos de Contratação** da FE 008 (seção 6, códigos 2.3.1/2.3.2) batem exatamente com `AtribuicaoFuncao.requisito_contratacao` — confirma que a numeração usada nas conversas anteriores veio direto do documento oficial. A **Experiência Profissional** da FOP 402 bate exatamente com o Model `ExperienciaProfissional`.

### Achados confirmando decisões já tomadas (sem lacuna nova)

- **Ata de Vínculo Inicial/Final** (FE 007) — confirma o campo que a pessoa responsável já tinha mencionado querer adicionar para Discente, lá na conversa sobre encerramento de `AtribuicaoFuncao`. Continua dependente de Módulo (fora de escopo), sem mudança de plano.
- **Data Término/Desligamento do Vínculo** (FE 008) — bate exatamente com o item 4 da sequência ("Encerrar Atribuição de Função"), já planejado. Confirma o design, não é lacuna nova.
- **Vinculação ao Programa de Instrução** (Básico/Aviônica/Célula/GMP, FE 008) — mesma dependência de Módulo do item de Discente, mas agora identificada também para **Docente**.

### 5 lacunas novas apresentadas, com decisão de cada uma

| # | Lacuna | Origem | Decisão |
|---|---|---|---|
| 1 | Autorização de Uso de Imagem | FE 007 (Discente) | ❌ **Rejeitada** — pertence a um futuro módulo de Relatório, como campo de texto trazendo a confirmação/assinatura do responsável, não como campo de `Pessoa`/`DadosDiscente`. |
| 2 | Título de Eleitor + Zona + Seção | FE 008 (Docente) | ✅ **Aprovada** |
| 3 | Passaporte/Autorização de Permanência devem estar em `Pessoa`, não só `DadosDiscente` | FE 008 mostra a mesma seção para Docente | ✅ **Aprovada** — muda estrutura, não só adiciona campo (mover de `DadosDiscente` para `Pessoa`, possível migração de dado existente) |
| 4 | E-mail 2 | FE 008 (Docente) | ✅ **Aprovada** |
| 5 | Telefone 2 / Celular | FOP 402 (Gestão) | ✅ **Aprovada** |

*(Uma 6ª lacuna menor, "Licenças/Habilitações Requeridas para Examinador Credenciado", foi identificada mas nem chegou a ser apresentada como prioritária — nicho demais, um único tipo de cargo entre vários.)*

### Achado de brinde: catálogo de Disciplinas

A Seção 10 da FE 008 lista as 23 disciplinas do Módulo Básico + as disciplinas específicas de Aviônica/Célula/GMP — conteúdo real e completo, útil para popular o catálogo de `Disciplina` (hoje só gerenciável via Admin) quando chegar a hora.

---

## Estado geral ao final desta sessão

| Item | Status |
|---|---|
| Busca de Pessoa por CPF (item 1) | ✅ Implementada e testada |
| Bug do `get_or_create` ignorando `defaults` | ✅ Corrigido |
| Bug do `AtribuicaoFuncao.objects.create` duplicado | ✅ Corrigido |
| Campos mortos em `PreencherRequisitosEDisciplinasDocenteService` | ✅ Removidos |
| Auditoria de campos FE 007/FE 008/FOP 402 (item 2) | ✅ Concluída, 5 lacunas avaliadas |
| Implementação das 4 lacunas aprovadas (itens 2-5 da tabela) | 📝 Vira o item 01 da próxima sessão |
| Testes automatizados | 29 passed (sem alteração) |

---

## Itens novos de Backlog identificados nesta sessão

- [ ] **Adicionar Título de Eleitor + Zona + Seção** em `Pessoa` — aprovado em 03/09/2026, ver `docs/28`.
- [ ] **Mover Passaporte/Autorização de Permanência de `DadosDiscente` para `Pessoa`** — aprovado em 03/09/2026; é uma mudança estrutural (não só adicionar campo), avaliar necessidade de migrar dado já existente de Discentes cadastrados. Ver `docs/28`.
- [ ] **Adicionar E-mail 2** em `Pessoa` — aprovado em 03/09/2026.
- [ ] **Adicionar Telefone 2 / Celular** em `Pessoa` — aprovado em 03/09/2026.
- [ ] **Popular o catálogo de `Disciplina`** com o conteúdo real da Seção 10 da FE 008 (23 disciplinas do Módulo Básico + específicas de Aviônica/Célula/GMP) — quando a tela de CRUD de Disciplina for implementada.
- [ ] **Autorização de Uso de Imagem** — não faz parte de `Pessoa`/`DadosDiscente`; fica para um futuro módulo de Relatório, como campo de texto trazendo a confirmação do responsável.

---

## Próximos passos

**Primeira coisa da próxima sessão:** implementar as 4 lacunas aprovadas na auditoria (Título de Eleitor+Zona+Seção, mover Passaporte/Autorização de Permanência para `Pessoa`, E-mail 2, Telefone 2/Celular) — fecha de vez o item de auditoria. Depois, seguir para Editar Atribuição de Função, Encerrar Atribuição de Função, e Adicionar Nova Função a Pessoa existente, na ordem já confirmada.
