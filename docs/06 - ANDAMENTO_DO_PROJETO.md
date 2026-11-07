# Andamento do Projeto — 06

**Data:** 24/08/2026
**Branch:** `dev`
**Commits desta etapa:** nenhum ainda — sessão puramente de arquitetura/design, sem código escrito. Ver `docs/07 - PLANO_DE_MIGRACAO.md` para a execução.

---

## Contexto

Sessão iniciada com a intenção original de implementar o item 1 do Kanban ("Editar Pessoa"). Durante a etapa de desenho da tela, a conversa revelou uma limitação estrutural no modelo atual de `Vinculo`/`FuncaoGestao`/`Habilitacao` que motivou uma revisão arquitetural completa do módulo Pessoas — não uma correção pontual, um redesenho.

**Gatilho:** ao planejar as telas de "pré-cadastro" e "cadastro" da escola, ficou claro que `TipoFuncaoGestao` (hoje um `TextChoices` fechado com 4 valores: Diretor, GQ, Coordenador, Secretaria) não comporta a realidade real da organização — cargos como "Auxiliar Administrativo", "Gestor Responsável", "Gerente de Segurança Operacional" e combinações específicas como "Coordenador de Curso de Aviônica" apareceram como necessidade concreta, não hipotética.

---

## Documentos institucionais analisados nesta sessão

Três formulários reais da organização (EMCA/ANAC) foram trazidos e analisados em profundidade, cada um mapeado para uma categoria de Função:

| Formulário | Categoria | Conteúdo relevante extraído |
|---|---|---|
| **FOP 402** (Cadastro de Pessoal da Organização Requerente — ANAC) | Gestão | Confirma o padrão de nome composto no cargo (ex: "COORDENADOR DE CURSO DE AVIÔNICA" como um único rótulo, não uma composição de Cargo + Habilitação via join). Traz a seção "Experiência Profissional" (Organização/Cargo/Período, repetível) e a "Declaração de Acúmulo de Cargos". Confirma que "Licenças/Habilitações Requeridas" é exclusivo de Examinador Credenciado — cargo que não será implementado. |
| **FE 007** (Ficha de Matrícula, Rev. 02, 23/06/2026) | Discente | Traz o conjunto mais completo de campos de identificação pessoal (sexo, identidade, órgão expedidor, naturalidade, nacionalidade, filiação 1/2, nível de instrução, estado civil, raça/cor — coincidindo com o que já havia sido visto no FE 008). Traz campos exclusivos de Discente: RM, RA, códigos ANAC, curso inicial (Aviônica/Célula/GMP — amarrado ao conceito de Módulo), documentação de estrangeiro, contato de emergência, responsável legal (para menores de idade), e termos/declarações. |
| **FE 008** (já analisado em sessão anterior) | Docente | Base da especificação de `FormacaoDocente` já registrada no Kanban (seção "📐 Especificações Detalhadas") — mantida sem alteração. |

---

## Decisões tomadas, em ordem cronológica de discussão

### 1. `Vinculo` como hierarquia fixa (MTI) é abandonado

O conceito de "Vínculo" com 3 subtipos fixos via Multi-table Inheritance (Discente/Docente/Gestão) sai de cena. A palavra "vínculo" também é abandonada — o novo termo é **Função**.

### 2. `Funcao` vira catálogo aberto (Princípio Aberto/Fechado aplicado literalmente)

`Funcao` passa a ser uma tabela simples (`id` + `nome`), cadastrável livremente pela tela, sem qualquer alteração de código para admitir um cargo novo. Isso resolve o problema original: Diretor, GQ, Secretaria, Aux Adm, Gestor Responsável, GSO, "Coordenador de Curso de Aviônica" — tudo cabe como linha de catálogo.

Discussão explícita do porquê: a estrutura fica **fechada para modificação** (o schema genérico nunca muda para acomodar cargo novo) e **aberta para extensão** (quando um cargo específico exige dado estruturado — não apenas nome — cria-se uma extensão nova, sem tocar no catálogo).

### 3. `Habilitacao` e `FuncaoGestaoHabilitacao` são eliminados

Confirmado pelo FOP 402: a especialização (ex: "de Aviônica") já vem embutida no nome da Função, não como associação separada. Isso elimina `Habilitacao`, `FuncaoGestaoHabilitacao` e, por consequência, o `AssociarHabilitacaoService` (com seus 2 testes) e o endpoint de API correspondente — todos deixam de fazer sentido no novo modelo.

**Nota:** o bug histórico do Admin bypassando esse Service (registrado em `03 - ANDAMENTO_DO_PROJETO.md`) fica automaticamente resolvido — não por correção, mas por remoção do próprio cenário que o causava.

### 4. `AtribuicaoFuncao` substitui `Vinculo` como tabela comum

Nova tabela central: liga `Pessoa` + `Funcao`, carregando os dados que qualquer atribuição de função tem em comum — situação, data de início, data de fim, ativo. Toda Função, sem exceção, passa por aqui.

### 5. Estratégia técnica de extensão: FK 1:1 opcional, não Multi-table Inheritance

Decisão explicitamente **não** seguir o mesmo padrão de herança que `Vinculo` usava — mesmo sendo um padrão já testado em produção — porque a semântica do caso mudou: não é mais "é um tipo de Vínculo" (is-a), é "tem um perfil de dados adicional, quando aplicável" (has-a). Extensões viram tabelas independentes com `OneToOneField` apontando de volta para `AtribuicaoFuncao`, em vez de herdar dela.

Discutido com profundidade o trade-off entre as duas abordagens antes da escolha (ver seção "Explicação MTI vs. FK 1:1" no histórico da conversa). Escolha final: **FK 1:1**, por simplicidade — decisão consciente da pessoa responsável pelo projeto, informada, não por familiaridade prévia (era a primeira vez ouvindo sobre MTI).

### 6. Campos de identificação pessoal ampliada entram em `Pessoa`

Confirmado que o conjunto de campos vistos tanto no FE 007 quanto no FE 008 (sexo, identidade, data de emissão, órgão expedidor, naturalidade, UF de naturalidade, nacionalidade, filiação 1/2, nível de instrução, data de nascimento, estado civil, raça/cor) é dado de identificação da Pessoa em geral, não exclusivo de nenhuma categoria de Função. Resolve definitivamente o item que estava em aberto desde a sessão 05, registrado no Kanban.

### 7. Extensão Discente

Sem tabela própria de responsável legal ou contato de emergência — decisão explícita de simplificação ("mesmo se tiver dois ou três irmãos na escola, raramente os três serão menores"). Ambos viram blocos de campos de texto simples, prefixados, dentro da própria extensão Discente — mesmo padrão já usado para `Endereco` como Value Object embutido em `Pessoa`.

Campos confirmados na extensão Discente:
- Matrícula (RM, RA, código ANAC, código de matrícula ANAC)
- Documentação de estrangeiro (passaporte, autorização de permanência) — exclusiva daqui, não entra em `Pessoa`
- Contato de emergência (nome, grau de parentesco, telefone, endereço) — campos de texto simples, sem entidade própria
- Responsável legal (nome, endereço, identidade, órgão expedidor, data de emissão, grau/qualificação) — campos de texto simples, sem entidade própria, reaproveitados nas seções de assinatura do FE 007 quando o documento for gerado

**Adiado para desenvolvimento futuro (fora desta sessão):** curso inicial (Aviônica/Célula/GMP), PI Inicial/Final, Ata de Vínculo — amarrados ao conceito de Módulo, que segue fora de escopo. Vai ficar em branco no FE 007 impresso por enquanto.

**Insight capturado para o backlog do item "Encerrar Vínculo"/"Encerrar Atribuição de Função":** o rastreio de trajetória do aluno (Transferido / Reprovado / Aprovado / Matrícula Excluída) é o motivo do encerramento da atribuição — não um campo à parte. Quando esse item da lista "A Fazer" for implementado, ele precisa carregar não só a desativação, mas o motivo.

**Termos/declarações do FE 007 (Ciência, Uso de Imagem):** não entram no modelo de dados. A assinatura física já é a prova de consentimento; essas seções do documento gerado são texto legal fixo, sem campo de banco correspondente.

### 8. `ExperienciaProfissional` liga a `AtribuicaoFuncao`, exclusiva de Gestão

Decisão revisada durante a própria sessão: a primeira hipótese (ligar a `Pessoa`, como histórico único da pessoa) foi descartada quando ficou claro que Experiência Profissional só se aplica a cargos de Gestão — nem Docente, nem Discente. Ligando a `AtribuicaoFuncao`, a restrição já é natural (só telas de Função de Gestão mostram essa seção), sem necessidade de regra de negócio extra no código.

### 9. Fluxo de cadastro: buscar-ou-criar por CPF

Confirmado o fluxo real de composição da escola:
- **Primeiro preenchimento** (CPF novo): cria `Pessoa` + `AtribuicaoFuncao` + extensão, numa operação só.
- **Segundo preenchimento** (CPF já existente — segundo curso, acúmulo de função, mudança de categoria): busca `Pessoa` existente pelo CPF, permite editar campos gerais (exceto CPF — critério exato de quais campos são editáveis fica para avaliação futura), e cria apenas a nova `AtribuicaoFuncao` + extensão, sem duplicar `Pessoa`.

Isso implica que `Pessoa.cpf` precisa de constraint de unicidade no banco (`unique=True`) — a verificar no início da implementação, pois não há confirmação registrada de que já existe.

O Service que hoje é `CadastrarPessoaComVinculoService` evolui de "sempre cria Pessoa nova" para "busca ou cria Pessoa, depois cria a Atribuição" — orquestração real, continua justificando a existência de um Service (não é caso de remover a camada, como se cogitou para "Editar Pessoa" simples).

### 10. Três telas de cadastro, uma por formulário/categoria

Confirmado que os 3 formulários institucionais mapeiam diretamente para as 3 categorias de Função:

| Formulário | Categoria | Carrega |
|---|---|---|
| FE 007 | Discente | Pessoa (completo) + extensão Discente — fluxo mais usado, carregado direto |
| FE 008 | Docente | Pessoa + extensão Docente |
| FOP 402 | Gestão (qualquer cargo do catálogo que não seja Discente/Docente) | Pessoa + Experiência Profissional |

Dentro de "Gestão", a escolha de qual `Funcao` específica do catálogo (Diretor, Coordenador de Curso de X, etc.) não muda a estrutura do formulário — todos usam o mesmo FOP 402. Só a categoria (Discente / Docente / Gestão) determina qual conjunto de campos aparece.

### 11. Objetivo de output confirmado

O sistema deve, no fim, **gerar a Ficha de Matrícula FE 007** (e presumivelmente os outros dois formulários) a partir dos dados cadastrados — não só armazená-los. Isso não muda o modelo de dados agora, mas é um requisito confirmado para desenvolvimento futuro (provavelmente geração de `.docx`/PDF preenchido).

---

## Impacto no que já estava implementado

Esta revisão invalida trabalho já commitado. Lista de itens que serão removidos ou reescritos (detalhado no plano de migração, `docs/07 - PLANO_DE_MIGRACAO.md`):

- Models: `Vinculo`, `VinculoDiscente`, `VinculoDocente`, `VinculoGestao`, `FuncaoGestao`, `Habilitacao`, `FuncaoGestaoHabilitacao`
- Service: `AssociarHabilitacaoService` (2 testes)
- Endpoint de API: `POST /api/pessoas/funcoes-gestao/habilitacoes/`
- Partes de `CadastrarPessoaComVinculoService` que mapeiam tipo de vínculo para subclasse (a lógica de "buscar ou criar por CPF" é nova, não substituição direta)
- Template Views que dependem da estrutura de `Vinculo` (lista, detalhe) — precisam de revisão, não necessariamente reescrita total
- Especificação de `FormacaoDocente` no Kanban precisa de pequeno ajuste: hoje referencia `VinculoDocente`, passa a referenciar a extensão Docente nova

**Decisão consciente registrada:** a pessoa responsável pelo projeto foi avisada do custo dessa mudança (models, Service e testes já commitados sendo descartados) antes de prosseguir, e optou por seguir mesmo assim — juízo tomado com informação completa, não por entusiasmo do momento.

---

## Modelo de dados resultante (referência rápida)

| Entidade | Natureza | Conteúdo |
|---|---|---|
| `Pessoa` | Existente, ampliada | Dados atuais + identificação ampliada (sexo, identidade, órgão expedidor, data emissão, naturalidade, UF, nacionalidade, filiação 1/2, nível de instrução, data nascimento, estado civil, raça/cor) + `Endereco` (VO, inalterado) |
| `Funcao` | Nova | Catálogo aberto: `id`, `nome` |
| `AtribuicaoFuncao` | Nova, substitui `Vinculo` | `pessoa` (FK), `funcao` (FK), situação, data início, data fim, ativo |
| `DadosDiscente` | Nova (extensão via FK 1:1) | matrícula (RM/RA/códigos ANAC), documentação de estrangeiro, contato de emergência (campos simples), responsável legal (campos simples) |
| `DadosDocente` | Nova (extensão via FK 1:1) | Substitui o que hoje é `VinculoDocente` + `Capacidade` — capacidades, formação (FE 008, já especificado no Kanban), requisitos de contratação |
| `ExperienciaProfissional` | Nova | organização, cargo, período — FK para `AtribuicaoFuncao`, só relevante quando a Função é de Gestão |

**Removidos:** `Vinculo`, `VinculoDiscente`, `VinculoDocente`, `VinculoGestao`, `FuncaoGestao`, `Habilitacao`, `FuncaoGestaoHabilitacao`.

**Regra de negócio única remanescente:** uma Pessoa com Função de Discente não pode acumular nenhuma outra Função. Todas as demais categorias podem acumular.

---

## Próximos passos

Executar o plano de migração registrado em `docs/07 - PLANO_DE_MIGRACAO.md` — nenhum código foi alterado nesta sessão, ela foi inteiramente de design.
