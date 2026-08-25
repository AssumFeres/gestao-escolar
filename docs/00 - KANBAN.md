# Kanban do Projeto — Sistema de Gestão Escolar

Quadro de acompanhamento vivo. Diferente dos arquivos `NN - ANDAMENTO_DO_PROJETO.md` (que são um diário, fechados por data), este arquivo é **atualizado continuamente** — mova os itens entre colunas conforme o status muda.

**Como atualizar:** corte o item de uma coluna e cole na outra, mantendo o formato de checklist. Ao mover para "Concluído", adicione a data e o commit relacionado entre parênteses.

> **Nota de contexto (24/08/2026):** o módulo Pessoas está em plena refatoração — o modelo `Vinculo`/`FuncaoGestao`/`Habilitacao` foi substituído, em nível de design, pelo modelo `Funcao`/`AtribuicaoFuncao`. Raciocínio completo em `docs/06 - ANDAMENTO_DO_PROJETO.md`; execução passo a passo em `docs/07 - PLANO_DE_MIGRACAO.md`. Itens deste Kanban que mencionam `Vinculo`/`Habilitacao` estão sendo substituídos pelos itens da nova seção abaixo.

---

## 🔨 Em Andamento
*Sendo trabalhado agora*

- [ ] **Migração `Vinculo`/`FuncaoGestao`/`Habilitacao` → `Funcao`/`AtribuicaoFuncao`** — plano detalhado em `docs/07 - PLANO_DE_MIGRACAO.md`, 9 etapas. **Etapas 1, 2 e 3 concluídas (25/08/2026)** — `Pessoa` ampliada, catálogo `Funcao` criado e populado (9 Funções), `AtribuicaoFuncao` criado. Etapa 4 (as 3 extensões — `DadosDiscente`, `DadosDocente`, `ExperienciaProfissional`) é a maior do plano, deixada para sessão com mais tempo. Detalhe da sessão em `docs/08 - ANDAMENTO_DO_PROJETO.md`.

---

## 🧊 Backlog

*Ideias e sugestões — ainda não decidido quando/se entram no PI atual*

- [ ] Recuperação de senha para usuários administradores (Django já oferece nativo via `django.contrib.auth` — falta configurar backend de e-mail e templates)
- [ ] **Tela de login + estratégia de autenticação** — decidir se usuários do sistema (além do superusuário Admin) serão o `User` padrão do Django, vinculado a `Pessoa`, ou solução customizada.
- [ ] Avaliar GitHub Student Developer Pack (PyCharm Professional gratuito, entre outros benefícios)
- [ ] Melhorar Django Admin com Inlines (editar `AtribuicaoFuncao`/extensões na mesma tela de Pessoa) — paliativo até as Template Views customizadas cobrirem cadastro completo
- [ ] **Django Admin não aplica a regra "Discente não acumula outra Função"** — mesmo raciocínio pragmático já documentado para o caso antigo do `AssociarHabilitacaoService` (ver `03 - ANDAMENTO_DO_PROJETO.md`): o Admin conversa direto com `AtribuicaoFuncao.objects.create()`, sem passar pelo Service que vai aplicar essa regra. Registrado preventivamente desta vez, antes de alguém encontrar o bug na prática.
- [ ] Testes automatizados para as Template Views (`ListaPessoasView`, `DetalhePessoaView`, `NovoCadastroPessoaView`)
- [ ] **Cadastro de Formação do Docente (Graduação/Formação Profissional/Aperfeiçoamento) + vínculo com Requisitos de Contratação e Disciplina Habilitada, baseado no FE 008** — especificação completa no capítulo "📐 Especificações Detalhadas" no final deste documento. **Referência atualizada:** a especificação foi escrita contra `VinculoDocente`; ao implementar, ligar a `DadosDocente` (ver Migração acima).
- [ ] Definir quais campos de `Pessoa` são editáveis no fluxo de "segundo preenchimento" (CPF já existente) — hipótese registrada em `06 - ANDAMENTO_DO_PROJETO.md`: tudo exceto CPF, mas ainda não confirmado a fundo
- [ ] **Curso Inicial (Aviônica/Célula/GMP) + PI Inicial/Final + Ata de Vínculo, da FE 007** — depende do conceito de Módulo, que segue fora de escopo. Fica em branco no FE 007 gerado até então.
- [ ] **Motivo de encerramento de `AtribuicaoFuncao` para Discente** (Transferido / Reprovado / Aprovado / Matrícula Excluída) — capturar junto quando o item "Encerrar Vínculo/Atribuição" (ver lista "A Fazer") for implementado; não é só desativar, é registrar o motivo.
- [ ] Geração da Ficha de Matrícula FE 007 (e, no futuro, FE 008/FOP 402) preenchida a partir dos dados do sistema — requisito de output confirmado, não modelagem; provável uso futuro do fluxo de geração de `.docx`/PDF
- [ ] Validação de erros de negócio no formulário HTML mais amigável (hoje aparece como mensagem genérica no topo, sem destacar o campo)
- [ ] Máscaras de formato nos campos do formulário (CPF, CEP, telefone)
- [ ] Configurar `choices` para os campos `sexo`, `estado_civil`, `raca_cor` — usar como etapa disparadora para revisar todos os campos de identificação ampliada quanto à necessidade de lista fechada de valores, em vez de decidir campo a campo de forma avulsa
- [ ] Ajustar `verbose_name_plural` de `Funcao` no Admin (hoje exibido como "Funcaos")
- [ ] Avaliar dividir `pessoas/models.py` em uma pasta `models/` com um arquivo por classe/grupo de classes relacionadas, à medida que o arquivo cresce com a migração — refatoração puramente organizacional, sem mudança de comportamento
- [ ] Manter o docstring de índice no topo de `pessoas/models.py` sincronizado conforme classes são adicionadas/removidas durante a migração — hoje já está desatualizado
- [ ] **Teste manual a validar quando a Etapa 4/5 estiver pronta:** confirmar que o Admin realmente bloqueia a exclusão de uma `Funcao` que já tem `AtribuicaoFuncao` vinculada (`on_delete=PROTECT`), validando na prática a proteção contra perda de rastreabilidade
- [ ] Fixture versionada do catálogo `Funcao` — decisão tomada de popular manualmente por enquanto (9 Funções cadastradas via Admin na sessão de 25/08/2026); cada uma das 5 máquinas validadas precisa popular seu próprio catálogo até que isso seja versionado

---

## 📋 A Fazer — CRUD completo do módulo Pessoas

*Bloqueado até a migração em "Em Andamento" ser concluída — os itens abaixo dependem do modelo novo (`Funcao`/`AtribuicaoFuncao`) estar implementado.*

**Ordem sugerida, revisada em 24/08/2026 para refletir o novo modelo:**

1. [ ] **Editar Pessoa** (Update) — reaproveita o Form já existente, nova View de edição. Motivou toda a revisão arquitetural desta sessão; retomar assim que a migração estiver pronta.
2. [ ] **Tela de cadastro (FE 007) — Discente**: Pessoa + extensão Discente, com fluxo de buscar-ou-criar por CPF
3. [ ] **Tela de cadastro (FE 008) — Docente**: Pessoa + extensão Docente
4. [ ] **Tela de cadastro (FOP 402) — Gestão**: Pessoa + Experiência Profissional, com seleção da `Funcao` específica do catálogo
5. [ ] **Adicionar nova Função a uma Pessoa já existente** (acúmulo de cargo, ou segundo curso para Discente) — via busca por CPF
6. [ ] **Editar Atribuição de Função** (situação, datas)
7. [ ] **Encerrar Atribuição de Função** (`data_fim` + `ativo=False` + motivo, ver item correspondente no Backlog para o caso Discente)
8. [ ] **Excluir/inativar Pessoa**
9. [ ] **Tela de cadastro de Disciplina** (Create/Read/Update/Delete) — hoje só existe via Admin, não depende da migração

**Outras pendências antes do deploy:**
- [ ] Configurar PostgreSQL (atualmente em SQLite) via variável de ambiente
- [ ] Ajustes de `settings.py` para produção (`DEBUG=False`, `ALLOWED_HOSTS`, `SECRET_KEY` via `.env`)
- [ ] Configurar arquivos estáticos para produção (`whitenoise` ou equivalente)
- [ ] Escolher e configurar provedor de nuvem (Render ou Railway)
- [ ] Revisão de acessibilidade nos templates HTML
- [ ] Testes de Views/API (além dos testes de Service já existentes)
- [ ] Convidar colegas de grupo como collaborators no GitHub

---

## ✅ Concluído
*Feito, testado e versionado*

- [x] Repositório Git criado e configurado (branches `main`/`dev`) — 19/08/2026
- [x] `.gitignore` configurado — 19/08/2026 (`f27cb9f`)
- [x] Documentação de arquitetura (DDD/SOLID pragmático, camadas, decisões de modelagem) — 19/08/2026
- [x] Estrutura inicial do projeto Django — 20/08/2026 (`513ca35`)
- [x] Ambiente validado em 5 máquinas (casa, quartel, escola, notebook) — 20-24/08/2026
- [x] README de setup para o grupo — 20/08/2026
- [x] `BuscarEnderecoPorCepService` (Porta/Adaptador ViaCEP) + 1 teste — 20/08/2026 (`662f87f`)
- [x] Endpoint de API `GET /api/pessoas/cep/<cep>/` (`BuscarCepView`) — 21/08/2026 (`b244774`)
- [x] Layout base compartilhado (`templates/base.html` + `static/global/css/base.css`) — 23/08/2026 (`f337e0d`)
- [x] Bug de tooling corrigido: auto-format do VSCode quebrando templates Django — `.vscode/settings.json` versionado — 23/08/2026 (`78cf27f`)
- [x] JavaScript — busca automática de endereço por CEP no formulário — 24/08/2026 (`3a64172`)
- [x] **Redesenho arquitetural do módulo Pessoas** (`Vinculo`/`FuncaoGestao`/`Habilitacao` → `Funcao`/`AtribuicaoFuncao`), baseado em 3 formulários institucionais reais (FOP 402, FE 007, FE 008) — decisão de design fechada em 24/08/2026, ver `docs/06 - ANDAMENTO_DO_PROJETO.md`. **Execução ainda pendente**, ver "Em Andamento".

### Itens historicamente concluídos, agora em revisão pela migração
*Estes itens foram concluídos sob o modelo antigo (`Vinculo`/`FuncaoGestao`/`Habilitacao`) e serão removidos ou reescritos como parte da migração em andamento — mantidos aqui só como registro histórico do que já existiu, não como trabalho ainda válido:*

- [x] ~~Models: `Vinculo`, `VinculoDiscente`, `VinculoDocente`, `VinculoGestao`, `FuncaoGestao`, `Habilitacao`, `FuncaoGestaoHabilitacao`~~ — 20/08/2026 (`524e6e0`) — **substituídos**
- [x] ~~Django Admin registrado para essas 9 entidades~~ — 20/08/2026 (`524e6e0`) — **parcialmente substituído**
- [x] ~~`AssociarHabilitacaoService` + 2 testes~~ — 20/08/2026 (`89ed300`) — **removido, conceito absorvido pelo catálogo aberto `Funcao`**
- [x] ~~`CadastrarPessoaComVinculoService` + 4 testes~~ — 20/08/2026 (`b347ae3`) — **em reescrita** (evolui para buscar-ou-criar por CPF)
- [x] ~~Endpoint de API `POST /api/pessoas/funcoes-gestao/habilitacoes/`~~ — 21/08/2026 (`bb01f2e`) — **removido**
- [x] ~~Endpoint de API `POST /api/pessoas/pessoas/`~~ — 23/08/2026 (`97e2915`) — **em revisão**
- [x] ~~Campo `sigla` em `Disciplina`~~ — 23/08/2026 (`fbfc3b1`) — **não afetado pela migração**, mantido válido
- [x] ~~Template View — lista de Pessoas~~ — 23/08/2026 (`f337e0d`) — **em revisão**
- [x] ~~Template View — detalhe de Pessoa com histórico de vínculos~~ — 23/08/2026 (`78cf27f`) — **em revisão**
- [x] ~~Property `tipo_legivel` em `Vinculo`~~ — 23/08/2026 (`78cf27f`) — **provavelmente desnecessária no modelo novo** (não há mais subtipo por herança)
- [x] ~~Template View — formulário de cadastro de Pessoa (`NovoCadastroPessoaView`)~~ — 24/08/2026 (`3a64172`) — **em revisão**, vira 3 fluxos distintos por categoria de Função

---

## 🔭 Fora de Escopo (PI futuro)
*Não entra neste PI — mapeado como Bounded Context futuro, ver `documentacao_arquitetura.md` seção 5*

- [ ] Módulo Gestão de Turmas (`Turma`, `Modulo`, relação `Disciplina`↔`Modulo`) — confirmado fora de escopo em 24/08/2026, mesmo após a descoberta de que a FE 007 depende parcialmente disso (curso inicial, PI Inicial/Final)
- [ ] Módulo Atribuição de Instrutor
- [ ] Módulo Gestão de Treinamentos
- [ ] Módulo Diário de Classe (frequência, conteúdo, notas)

---

## Status Geral

| Métrica | Valor atual |
|---|---|
| Services implementados (modelo antigo, sob revisão) | 3 (1 removido, 1 em reescrita, 1 não afetado) |
| Endpoints de API implementados (modelo antigo, sob revisão) | 3 (1 removido, 1 em revisão, 1 não afetado) |
| Template Views implementadas (modelo antigo, sob revisão) | 3 (todas em revisão) |
| Testes automatizados | 7 (2 serão removidos com `AssociarHabilitacaoService`) |
| Models do modelo antigo | 9 (7 serão removidos, ver lista de migração) |
| Models do modelo novo | 3 implementados / 6 desenhados (`Pessoa` ampliada ✅, `Funcao` ✅, `AtribuicaoFuncao` ✅ — faltam `DadosDiscente`, `DadosDocente`, `ExperienciaProfissional`) |
| Catálogo `Funcao` populado | 9 Funções (ver Etapa 2 em `docs/07 - PLANO_DE_MIGRACAO.md`) |
| Última branch ativa | `feature/refatoracao-funcao` |
| Último commit | `193fd99` — `feat: model AtribuicaoFuncao` |

---
---

# 📐 Especificações Detalhadas de Itens do Backlog

*Este capítulo guarda o raciocínio completo e esboços de código para itens do Backlog que já foram discutidos em profundidade, mas ainda não entraram em desenvolvimento. Quando um item daqui for iniciado, mova a entrada correspondente do Backlog para "Em Andamento" e use esta seção como ponto de partida — não como código final, como referência de decisão já tomada.*

## Cadastro de Formação do Docente (baseado no FE 008)

**Origem:** Formulário FE 008 — Formulário de Cadastro de Instrutor e Atribuição de Disciplina (Rev. 01, 24/06/2026). Discutido em 23/08/2026.

> **⚠️ Nota de atualização (24/08/2026):** os esboços de código abaixo foram escritos contra `VinculoDocente`, que deixou de existir na migração registrada em `docs/06`/`07 - ANDAMENTO_DO_PROJETO.md` / `PLANO_DE_MIGRACAO.md`. O raciocínio de modelagem (tabela única com enum, requisitos como campos diretos por YAGNI, FK de comprovação) continua válido — só troque toda referência a `VinculoDocente` por `DadosDocente` ao implementar.

### Contexto do formulário

O FE 008 tem, entre outras, estas seções relevantes para `pessoas`:
- **Seção 3 — Graduação:** tabela com colunas Curso, Entidade, Cidade, UF, Ano de Conclusão.
- **Seção 4 — Formação Profissional:** mesmas colunas da seção 3.
- **Seção 5 — Aperfeiçoamento Profissional:** mesmas colunas da seção 3.
- **Seção 6 — Requisitos de Contratação:** dois critérios fixos, baseados na norma RBAC 141:
  - 2.3.1 — experiência docente comprovada (6 meses geral + 6 meses na área específica) — evidência em **texto livre** (análise de CV/declarações).
  - 2.3.2 — formação específica na área de atuação — evidência é uma **referência direta** a um dos cursos cadastrados nas seções 3/4/5 (identificados por numeração tipo "3.2", "4.1").
- **Seção 7 — Disciplina Habilitado(a) a Ministrar:** já corresponde ao Model `Capacidade` existente; falta o campo de documento comprobatório, que também é uma referência a um curso cadastrado (mesmo padrão do item 2.3.2).

### Decisão 1 — Tabela única para Graduação/Formação/Aperfeiçoamento

As três seções têm exatamente a mesma estrutura de colunas — só a categoria muda. Criar 3 Models seria duplicação (viola DRY) sem ganho de expressividade. Aqui, o padrão correto é **uma tabela + campo enum**.

```python
class TipoFormacaoDocente(models.TextChoices):
    GRADUACAO = 'GRADUACAO', 'Graduação'
    FORMACAO_PROFISSIONAL = 'FORMACAO_PROFISSIONAL', 'Formação Profissional'
    APERFEICOAMENTO_PROFISSIONAL = 'APERFEICOAMENTO_PROFISSIONAL', 'Aperfeiçoamento Profissional'


class FormacaoDocente(models.Model):
    dados_docente = models.ForeignKey('DadosDocente', on_delete=models.CASCADE, related_name='formacoes')
    tipo_formacao = models.CharField(max_length=30, choices=TipoFormacaoDocente.choices)
    curso = models.CharField(max_length=200)
    entidade = models.CharField(max_length=200)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    ano_conclusao = models.IntegerField()

    def __str__(self):
        return f"{self.curso} ({self.get_tipo_formacao_display()})"
```

**Nota sobre a numeração "3.1", "4.2", "5.3" do formulário físico:** é a posição do registro dentro do seu próprio tipo, usada como referência cruzada com a pasta física/digital do docente. Não precisa virar campo salvo no banco — pode ser calculada dinamicamente (property que conta a posição entre os registros do mesmo tipo e mesma pessoa) quando for implementado.

### Decisão 2 — Requisitos de Contratação: campos diretos em `DadosDocente`, não catálogo

Primeira proposta considerada foi um catálogo (`RequisitoContratacao` + tabela associativa) — descartada por ser over-engineering (**YAGNI**) para exatamente 2 critérios fixos, sem sinal de que vão crescer em variedade tão cedo.

```python
class DadosDocente(models.Model):
    atribuicao = models.OneToOneField('AtribuicaoFuncao', on_delete=models.CASCADE, related_name='dados_docente')

    # Requisito 2.3.1 — texto livre, análise de CV/declarações de serviço
    experiencia_docente_comprovada = models.TextField(
        blank=True,
        help_text="Análise de declarações de serviço, CV, etc. — comprovação de experiência docente (RBAC 141)."
    )

    # Requisito 2.3.2 — referência única a um curso já cadastrado
    formacao_especifica_comprobatoria = models.ForeignKey(
        'FormacaoDocente', on_delete=models.PROTECT, null=True, blank=True,
        related_name='comprova_requisito_para',
        help_text="Curso que comprova formação específica na área de atuação (RBAC 141)."
    )

    def possui_treinamento_valido(self) -> bool:
        return True
```

Se a EMCA um dia ampliar os critérios de contratação, a refatoração para um catálogo genérico deve ser feita **naquele momento**, com informação real sobre o novo formato — não especulativamente hoje.

### Decisão 3 — `Capacidade` ganha referência ao documento comprobatório

```python
class Capacidade(models.Model):
    dados_docente = models.ForeignKey('DadosDocente', on_delete=models.CASCADE, related_name='capacidades')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT, related_name='capacidades')
    formacao_comprobatoria = models.ForeignKey(
        'FormacaoDocente', on_delete=models.PROTECT, null=True, blank=True,
        help_text="Curso que comprova a capacidade de ministrar esta disciplina."
    )
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    # ... resto das constraints existentes inalteradas
```

### Resumo do impacto quando for implementado

| Model | Mudança |
|---|---|
| `FormacaoDocente` | **Novo** — Graduação/Formação Profissional/Aperfeiçoamento numa tabela só |
| `DadosDocente` | +2 campos (`experiencia_docente_comprovada`, `formacao_especifica_comprobatoria`) |
| `Capacidade` | FK trocada de `VinculoDocente` para `DadosDocente`, +1 campo (`formacao_comprobatoria`) |

### Campos de identificação vistos no FE 008, já resolvidos

~~O formulário também tem uma seção de identificação/documentos pessoais mais completa do que o `Pessoa` atual.~~ **Resolvido em 24/08/2026** — ver `docs/06 - ANDAMENTO_DO_PROJETO.md`, item 6: os campos de identificação ampliada (RG/identidade, naturalidade, nacionalidade, filiação, nível de instrução, estado civil, etc.) entraram em `Pessoa` como parte da migração.
