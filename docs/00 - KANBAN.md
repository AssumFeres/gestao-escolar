# Kanban do Projeto — Sistema de Gestão Escolar

Quadro de acompanhamento vivo. Diferente dos arquivos `NN - ANDAMENTO_DO_PROJETO.md` (que são um diário, fechados por data), este arquivo é **atualizado continuamente** — mova os itens entre colunas conforme o status muda.

**Como atualizar:** corte o item de uma coluna e cole na outra, mantendo o formato de checklist. Ao mover para "Concluído", adicione a data e o commit relacionado entre parênteses.

---

## 🧊 Backlog
*Ideias e sugestões — ainda não decidido quando/se entram no PI atual*

- [ ] Recuperação de senha para usuários administradores (Django já oferece nativo via `django.contrib.auth` — falta configurar backend de e-mail e templates)
- [ ] **Tela de login + estratégia de autenticação** — decidir se usuários do sistema (além do superusuário Admin) serão o `User` padrão do Django, vinculado a `Pessoa`, ou solução customizada. Django já oferece views nativas de login/logout em `django.contrib.auth.views`, mas a estratégia de "quem pode logar e o que vê" precisa ser definida antes de construir a tela.
- [ ] Avaliar GitHub Student Developer Pack (PyCharm Professional gratuito, entre outros benefícios)
- [ ] Melhorar Django Admin com Inlines (editar Vinculo/FuncaoGestao na mesma tela de Pessoa) — paliativo até as Template Views customizadas cobrirem cadastro completo
- [ ] **Reforçar `AssociarHabilitacaoService` também no nível do Model/banco** — o Django Admin, por ser genérico, não passa pelo Service e permite hoje criar `FuncaoGestaoHabilitacao` inválida (ver `docs/03 - ANDAMENTO_DO_PROJETO.md`). Opções: `clean()` no Model, `CHECK constraint` no Postgres futuramente, ou restringir o Admin para essa entidade.
- [ ] Testes automatizados para as Template Views (`ListaPessoasView`, `DetalhePessoaView`, `NovoCadastroPessoaView`)
- [ ] **Cadastro de Formação do Docente (Graduação/Formação Profissional/Aperfeiçoamento) + vínculo com Requisitos de Contratação e Disciplina Habilitada, baseado no FE 008** — especificação completa esboçada no capítulo "📐 Especificações Detalhadas" no final deste documento.
- [ ] Campos adicionais de identificação de Pessoa vistos no FE 008 (RG, título de eleitor, estado civil, naturalidade, nacionalidade, filiação 1/2, nível de instrução) — avaliar quais são realmente necessários antes de adicionar
- [ ] Validação de erros de negócio no formulário HTML mais amigável (hoje aparece como mensagem genérica no topo, sem destacar o campo)
- [ ] Esconder/mostrar campos do formulário de Pessoa dinamicamente conforme `tipo_vinculo` escolhido (ex: `numero_matricula` só faz sentido para Discente) — candidato a JavaScript
- [ ] Máscaras de formato nos campos do formulário (CPF, CEP, telefone)

---

## 📋 A Fazer — CRUD completo do módulo Pessoas
*Antes de avançar para PostgreSQL/deploy, o módulo precisa ter Create+Read+Update+Delete funcional via interface, não só via Admin/API. Levantamento feito em 24/08/2026.*

**Ordem sugerida de implementação** (cada item pequeno, testável isoladamente):

1. [ ] **Editar Pessoa** (Update) — reaproveita `CadastrarPessoaForm`, nova View de edição
2. [ ] **Tela de cadastro de Habilitação** (Create/Read/Update/Delete) — CRUD simples, sem regra de negócio complexa
3. [ ] **Tela de cadastro de FuncaoGestao** — depende de um `VinculoGestao` existente
4. [ ] **Tela de Associar Habilitação a Coordenador** — reaproveita `AssociarHabilitacaoService` (já pronto e testado via API), só falta o HTML
5. [ ] **Adicionar segundo vínculo a uma Pessoa já existente** (hoje só é possível criar o primeiro vínculo, junto com a Pessoa)
6. [ ] **Editar Vínculo** (situação, datas)
7. [ ] **Encerrar Vínculo** (`data_fim` + `ativo=False`)
8. [ ] **Excluir/inativar Pessoa**
9. [ ] **Tela de cadastro de Disciplina** (Create/Read/Update/Delete) — hoje só existe via Admin

**Outras pendências antes do deploy:**
- [ ] Configurar PostgreSQL (atualmente em SQLite) via variável de ambiente
- [ ] Ajustes de `settings.py` para produção (`DEBUG=False`, `ALLOWED_HOSTS`, `SECRET_KEY` via `.env`)
- [ ] Configurar arquivos estáticos para produção (`whitenoise` ou equivalente)
- [ ] Escolher e configurar provedor de nuvem (Render ou Railway)
- [ ] Revisão de acessibilidade nos templates HTML
- [ ] Testes de Views/API (além dos testes de Service já existentes)
- [ ] Convidar colegas de grupo como collaborators no GitHub

---

## 🔨 Em Andamento
*Sendo trabalhado agora*

*(vazio no momento — mova um item de "A Fazer" para cá quando começar)*

---

## ✅ Concluído
*Feito, testado e versionado*

- [x] Repositório Git criado e configurado (branches `main`/`dev`) — 19/08/2026
- [x] `.gitignore` configurado — 19/08/2026 (`f27cb9f`)
- [x] Documentação de arquitetura (DDD/SOLID pragmático, camadas, decisões de modelagem) — 19/08/2026
- [x] Estrutura inicial do projeto Django — 20/08/2026 (`513ca35`)
- [x] Models completos: Pessoa, Vinculo + 3 subtipos, FuncaoGestao, Habilitacao, Capacidade, Disciplina — 20/08/2026 (`524e6e0`)
- [x] Django Admin registrado para todas as 9 entidades — 20/08/2026 (`524e6e0`)
- [x] Ambiente validado em 5 máquinas (casa, quartel, escola, notebook) — 20-24/08/2026
- [x] README de setup para o grupo — 20/08/2026
- [x] `AssociarHabilitacaoService` + 2 testes — 20/08/2026 (`89ed300`)
- [x] `CadastrarPessoaComVinculoService` + 4 testes — 20/08/2026 (`b347ae3`)
- [x] `BuscarEnderecoPorCepService` (Porta/Adaptador ViaCEP) + 1 teste — 20/08/2026 (`662f87f`)
- [x] Endpoint de API `GET /api/pessoas/cep/<cep>/` (`BuscarCepView`) — 21/08/2026 (`b244774`)
- [x] Endpoint de API `POST /api/pessoas/funcoes-gestao/habilitacoes/` (`AssociarHabilitacaoView`) — 21/08/2026 (`bb01f2e`)
- [x] Endpoint de API `POST /api/pessoas/pessoas/` (`CadastrarPessoaView`) — 23/08/2026 (`97e2915`)
- [x] Campo `sigla` em `Disciplina` (3 letras maiúsculas, validado por regex) — 23/08/2026 (`fbfc3b1`)
- [x] Layout base compartilhado (`templates/base.html` + `static/global/css/base.css`) — 23/08/2026 (`f337e0d`)
- [x] Template View — lista de Pessoas (`ListaPessoasView`) — 23/08/2026 (`f337e0d`)
- [x] Template View — detalhe de Pessoa com histórico completo de vínculos (`DetalhePessoaView`) — 23/08/2026 (`78cf27f`)
- [x] Property `tipo_legivel` em `Vinculo` — 23/08/2026 (`78cf27f`)
- [x] Bug de tooling corrigido: auto-format do VSCode quebrando templates Django — `.vscode/settings.json` versionado — 23/08/2026 (`78cf27f`)
- [x] Especificação detalhada de Formação do Docente (FE 008) registrada no Backlog — 23/08/2026 (`9b9a2cd`)
- [x] Template View — formulário de cadastro de Pessoa (`NovoCadastroPessoaView`, Create) — 24/08/2026 (`3a64172`)
- [x] JavaScript — busca automática de endereço por CEP no formulário — 24/08/2026 (`3a64172`)

---

## 🔭 Fora de Escopo (PI futuro)
*Não entra neste PI — mapeado como Bounded Context futuro, ver `documentacao_arquitetura.md` seção 5*

- [ ] Módulo Gestão de Turmas (`Turma`, `Modulo`, relação `Disciplina`↔`Modulo`)
- [ ] Módulo Atribuição de Instrutor
- [ ] Módulo Gestão de Treinamentos
- [ ] Módulo Diário de Classe (frequência, conteúdo, notas)

---

## Status Geral

| Métrica | Valor atual |
|---|---|
| Services implementados | 3 (100%) |
| Endpoints de API implementados | 3 (100% dos Services existentes) |
| Template Views implementadas | 3 (lista, detalhe, cadastro de Pessoa) |
| CRUD completo do módulo Pessoas | Parcial — ver checklist "A Fazer" (Create parcial + Read; falta Update/Delete e CRUD de entidades relacionadas) |
| Testes automatizados | 7 (todos passando) |
| Models implementados | 9 |
| Última branch ativa | `dev` |
| Último commit | `3a64172` |

---
---

# 📐 Especificações Detalhadas de Itens do Backlog

*Este capítulo guarda o raciocínio completo e esboços de código para itens do Backlog que já foram discutidos em profundidade, mas ainda não entraram em desenvolvimento. Quando um item daqui for iniciado, mova a entrada correspondente do Backlog para "Em Andamento" e use esta seção como ponto de partida — não como código final, como referência de decisão já tomada.*

## Cadastro de Formação do Docente (baseado no FE 008)

**Origem:** Formulário FE 008 — Formulário de Cadastro de Instrutor e Atribuição de Disciplina (Rev. 01, 24/06/2026). Discutido em 23/08/2026.

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

As três seções têm exatamente a mesma estrutura de colunas — só a categoria muda. Criar 3 Models seria duplicação (viola DRY) sem ganho de expressividade, diferente do caso `Vinculo` (onde os subtipos têm campos genuinamente diferentes). Aqui, o padrão correto é **uma tabela + campo enum**, seguindo o mesmo raciocínio já usado em `FuncaoGestao.tipo_funcao`.

```python
class TipoFormacaoDocente(models.TextChoices):
    GRADUACAO = 'GRADUACAO', 'Graduação'
    FORMACAO_PROFISSIONAL = 'FORMACAO_PROFISSIONAL', 'Formação Profissional'
    APERFEICOAMENTO_PROFISSIONAL = 'APERFEICOAMENTO_PROFISSIONAL', 'Aperfeiçoamento Profissional'


class FormacaoDocente(models.Model):
    vinculo_docente = models.ForeignKey(VinculoDocente, on_delete=models.CASCADE, related_name='formacoes')
    tipo_formacao = models.CharField(max_length=30, choices=TipoFormacaoDocente.choices)
    curso = models.CharField(max_length=200)
    entidade = models.CharField(max_length=200)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    ano_conclusao = models.IntegerField()

    def __str__(self):
        return f"{self.curso} ({self.get_tipo_formacao_display()})"
```

**Nota sobre a numeração "3.1", "4.2", "5.3" do formulário físico:** é a posição do registro dentro do seu próprio tipo, usada como referência cruzada com a pasta física/digital do docente. Não precisa virar campo salvo no banco — pode ser calculada dinamicamente (property que conta a posição entre os registros do mesmo tipo e mesma pessoa) quando for implementado, evitando duplicar informação derivável.

### Decisão 2 — Requisitos de Contratação: campos diretos em `VinculoDocente`, não catálogo

Primeira proposta considerada foi um catálogo (`RequisitoContratacao` + tabela associativa, no padrão de `Habilitacao`) — descartada por ser over-engineering (princípio **YAGNI**) para exatamente 2 critérios fixos, sem sinal de que vão crescer em variedade tão cedo. Os dois requisitos têm naturezas de evidência diferentes entre si, então viram dois campos distintos:

```python
class VinculoDocente(Vinculo):
    situacao = models.CharField(max_length=30)

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

    def __str__(self):
        return f"{self.pessoa.nome_completo} - Docente"

    def possui_treinamento_valido(self) -> bool:
        return True
```

Se a EMCA um dia ampliar os critérios de contratação, a refatoração para um catálogo genérico deve ser feita **naquele momento**, com informação real sobre o novo formato — não especulativamente hoje.

### Decisão 3 — `Capacidade` ganha referência ao documento comprobatório

A Seção 7 do formulário já é o que `Capacidade` modela; só falta o campo de evidência, seguindo o mesmo padrão de FK única (não M2M) da Decisão 2:

```python
class Capacidade(models.Model):
    vinculo_docente = models.ForeignKey(VinculoDocente, on_delete=models.CASCADE, related_name='capacidades')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT, related_name='capacidades')
    formacao_comprobatoria = models.ForeignKey(
        'FormacaoDocente', on_delete=models.PROTECT, null=True, blank=True,
        help_text="Curso que comprova a capacidade de ministrar esta disciplina."
    )
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    # ... constraints existentes inalteradas
```

### Resumo do impacto quando for implementado

| Model | Mudança |
|---|---|
| `FormacaoDocente` | **Novo** — Graduação/Formação Profissional/Aperfeiçoamento numa tabela só |
| `VinculoDocente` | +2 campos (`experiencia_docente_comprovada`, `formacao_especifica_comprobatoria`) |
| `Capacidade` | +1 campo (`formacao_comprobatoria`) |
| Migrations necessárias | 1 nova migration (novo Model) + 1 alteração em `VinculoDocente` + 1 alteração em `Capacidade` — podem ser feitas numa única migration se aplicadas juntas |

### Campos de identificação vistos no FE 008, ainda não avaliados

O formulário também tem uma seção de identificação/documentos pessoais (RG, título de eleitor, passaporte, CPF, estado civil, naturalidade, nacionalidade, filiação 1/2, nível de instrução) mais completa do que o `Pessoa` atual. Não foi discutido em profundidade — fica registrado que existe, para avaliação futura de quais desses campos são realmente necessários no escopo do sistema (nem todo campo de um formulário físico institucional precisa virar campo de banco).
