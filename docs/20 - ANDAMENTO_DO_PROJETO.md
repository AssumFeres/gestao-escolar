# Andamento do Projeto — 20

**Data:** 01/09/2026 (sessão iniciada na máquina do quartel, retomando o bug em aberto do diário 19)
**Branch:** `dev` (commits diretos)
**Sessão dedicada a: diagnosticar e resolver o bug em aberto "Docente não cadastra", avaliar uma proposta de arquitetura para eliminar `cloneNode()` de vez, e implementar 3 correções pequenas no formulário de cadastro.**

---

## Contexto

Retomando o bug registrado como prioridade máxima no Kanban ao final do diário 19: o cadastro de Docente tinha parado de funcionar por completo depois da correção do bug de `cloneNode()` perdendo o valor de `<select>`. O ambiente foi confirmado saudável (`migrate` + `pytest` 29 passed) antes de investigar.

---

## Diagnóstico via testes isolados pelo navegador

Em vez de instrumentar a `View` com `print()` de novo (arriscado, como o próprio diário 19 registrou um incidente de indentação), a investigação usou as ferramentas de desenvolvedor do navegador (Console + aba Rede), como o diário 19 já recomendava.

### Primeira descoberta: o "bug" era, na verdade, sucesso não reconhecido

Um teste de Docente **sem** preencher nenhuma tabela (Formação/Histórico/Pendências) funcionou perfeitamente: `POST /cadastros/novo/` retornou `302`, redirecionando para `/cadastros/docente/<id>/requisitos/` — uma tela (`PreencherRequisitosDocenteView`) que já existia no código como placeholder desde sessões anteriores, mas que **nunca tinha sido vista** por ninguém, porque todo cadastro de Docente até então falhava antes de alcançá-la. A pessoa responsável não reconheceu a tela e interpretou como um erro novo.

### Segunda descoberta, mais sistemática: teste isolado por bloco

A pessoa responsável testou, em sequência, Docente preenchendo só Histórico de Vínculo, só Formação, só Pendências, e combinações — anotando o status HTTP de cada tentativa. Padrão observado: blocos com campo obrigatório do Model **incompleto** (ex: Histórico com "Vínculo Formal" preenchido mas "Data de início" vazia) retornavam `200` (formulário re-renderizado com erro), nunca `302`.

**Causa raiz identificada pela própria pessoa responsável:** o `clean()` dos Forms (`b3c1e89`, sessão anterior) já rejeitava corretamente essas linhas incompletas no backend — mas o **JavaScript do botão "+ Adicionar" só verificava o campo-sinal** (`data-required`, ex: `vinculo_formal`), não os demais campos obrigatórios do Model (ex: `data_inicio`). Isso permitia adicionar uma linha incompleta na tabela-resumo, dando a falsa impressão de sucesso — só para o formulário inteiro ser rejeitado, silenciosamente e sem indicar qual campo faltava, no momento de clicar "Salvar".

**Não era uma regressão nova relacionada ao fix do `<select>`** — era um gap de validação já existente desde a correção anterior, só que mascarado até esse teste sistemático expor o padrão.

---

## Proposta de arquitetura recebida e avaliada: eliminar `cloneNode()` de vez

Durante a investigação, a pessoa responsável trouxe uma especificação de arquitetura elaborada em outra conversa (`ESPECIFICAÇÃO_DE_ARQUITETURA — CADASTRO_DE_PESSOA_E_REGISTROS_RELACIONADOS.md`), propondo substituir o mecanismo de Formsets + `cloneNode()` + `TOTAL_FORMS` por CRUDs independentes por entidade relacionada (Formação, Experiência, Histórico, Pendência, Capacidade), cada uma com seu próprio `ModelForm`/View/URL/modal, persistindo via Foreign Key real assim que a Pessoa existir — eliminando por completo o armazenamento temporário no DOM.

### Avaliação

A ideia foi considerada **arquiteturalmente correta e bem fundamentada** — ataca a causa raiz (fragilidade do clone) em vez de só o sintoma, resolve de quebra os itens já pendentes de Editar/Excluir nas linhas relacionadas, e converge com a ideia de popup para os blocos de cadastro já registrada no Backlog em 31/08. Dois problemas identificados no documento, que precisariam ser corrigidos antes de qualquer implementação:

- Assume `FormacaoDocente`/`ExperienciaProfissional`/etc. com FK direta para `Pessoa` — no código real, `FormacaoDocente` aponta para `DadosDocente`, e `ExperienciaProfissional`/`HistoricoVinculoFormal`/`PendenciaCadastro` apontam para `AtribuicaoFuncao`, nunca para `Pessoa` diretamente (decisão deliberada da migração `Funcao`, permitindo múltiplas Atribuições ao longo do tempo).
- Não contempla que, para Docente, `DadosDocente` só existe depois que `AtribuicaoFuncao` + `DadosDocente` forem criados juntos pelo `Service` atual — então o "primeiro salvamento" precisaria criar 3 entidades, não só `Pessoa`.

**Escala do esforço:** comparável à migração `Vinculo`→`Funcao` (múltiplas sessões), não um bugfix — exige `ModelForm`+View+URL+template parcial por entidade, e repensar o `CadastrarPessoaComFuncaoService` (que hoje cria tudo atômico numa chamada só).

**Decisão:** adiar a implementação. A pessoa responsável vai guardar a especificação para desenvolver **numa branch separada**, quando houver tempo dedicado — sem misturar com o trabalho incremental do CRUD simples em andamento. Consciente do trade-off: a correção pontual do `<select>` deixa uma fragilidade estrutural no sistema (qualquer `<select>` novo em Formset futuro reintroduz o mesmo risco), mas o custo de parar tudo agora para a reescrita não se justificava frente ao volume de trabalho ainda por vir no CRUD básico.

---

## Correções implementadas nesta sessão

### 1. Validação de linha completa antes de "+ Adicionar" (JavaScript)

Novo atributo `data-obrigatorios-completos` em `form_pessoa.html`, nos 3 blocos que precisam (Formação, Experiência, Histórico — espelhando exatamente os campos que os respectivos `clean()` já exigem em `forms.py`). `form-dinamico.js` passou a checar todos esses campos antes de permitir adicionar a linha, não só o campo-sinal, mostrando quais campos faltam.

### 2. Popup customizado substituindo `alert()`

A pessoa responsável notou que o `alert()` nativo do navegador mostra a origem da página ("127.0.0.1:8000 diz") de forma não removível e não estilizável (é uma caixa de diálogo do sistema operacional/navegador, não um elemento da página). Substituído por um popup próprio: overlay semitransparente cobrindo a tela, caixa branca centralizada com a mensagem e um botão "OK" (fecha também ao clicar fora da caixa). Sem temporizador — o usuário fecha quando quiser.

### 3. Nova regra de negócio: Histórico de Vínculo Formal obrigatório para Docente/Gestão

A pessoa responsável identificou que o sistema permitia cadastrar Docente/Gestão sem nenhum Vínculo Formal, quando essa informação deveria ser sempre obrigatória para essas categorias. **Decisão de escopo, discutida explicitamente:** implementar a regra só em `NovoCadastroPessoaView` (formulário HTML), não em `CadastrarPessoaComFuncaoService`. Motivo: o `Service` é usado também pela `CadastrarPessoaView` (API mínima), que nunca envia `historico_vinculo_formal` — tornar a regra obrigatória ali quebraria a API por completo para essas categorias, além de exigir ajuste em pelo menos 3 testes existentes que cadastram Docente/Gestão sem Histórico de propósito (testando outra coisa). Mantendo a regra só na View, nada disso é afetado.

`pytest` — `29 passed` depois de cada uma das 3 correções (nenhuma delas altera o `Service` nem cenários já cobertos pelos testes).

**Testado manualmente e confirmado, para todos os casos:** Docente sem Histórico → bloqueado com erro no topo da página; Gestão sem Histórico → mesmo bloqueio; com Histórico completo → cadastra normalmente; Discente → não afetado pela regra (correto, é exclusiva de Docente/Gestão).

**Commit:** `5735c5b` — `fix: valida campos obrigatorios antes de Adicionar + exige Vinculo Formal para Docente/Gestao`.

---

## Estado geral ao final desta sessão

| Item | Status |
|---|---|
| Bug "Docente não cadastra" (diário 19) | ✅ **Resolvido** — causa real era falta de validação de linha completa no JS, não uma regressão do fix de `<select>` |
| Validação de linha completa (Formação/Experiência/Histórico) | ✅ Implementada e testada manualmente |
| Popup customizado substituindo `alert()` | ✅ Implementado, centralizado, com botão OK |
| Regra: Vínculo Formal obrigatório para Docente/Gestão | ✅ Implementada só na View, decisão de escopo documentada |
| Especificação de arquitetura CRUD sem `cloneNode()` | 📝 Avaliada, considerada boa mas de grande escala — adiada para branch futura dedicada |
| Testes automatizados | 29 passed (sem alteração — mudanças de JS e regra específica de View, fora do escopo dos testes atuais) |

---

## Itens novos de Backlog identificados nesta sessão

- [ ] **Migração da arquitetura de cadastro para CRUDs independentes por entidade relacionada** (Formação, Experiência, Histórico, Pendência, Capacidade), eliminando `cloneNode()`/Formsets/`TOTAL_FORMS` como mecanismo de persistência — especificação completa recebida e avaliada em 01/09/2026 (ver `docs/20`), precisa de ajuste antes de implementar (FKs reais são para `DadosDocente`/`AtribuicaoFuncao`, não `Pessoa` diretamente; Docente precisa de 3 entidades criadas juntas no primeiro salvamento, não só `Pessoa`). Escala comparável à migração `Funcao`. **Planejado para branch separada, quando houver tempo dedicado — não misturar com o CRUD incremental em andamento.**
- [ ] Testes automatizados para a regra "Histórico de Vínculo Formal obrigatório para Docente/Gestão" e para a validação de linha completa do JS — nenhum dos dois tem cobertura automatizada ainda (reforça, mais uma vez, a lacuna de testes para `NovoCadastroPessoaView` e para o comportamento de JavaScript, sem runner de teste JS configurado no projeto).

---

## Próximos passos

Retomar o CRUD completo do módulo Cadastros (ver Kanban, lista "A Fazer") — já sem bloqueio, com a base do formulário de cadastro simples e validada. A migração de arquitetura maior (CRUDs por entidade) fica registrada como decisão futura, para quando a pessoa responsável tiver tempo de dedicar uma branch só para isso.
