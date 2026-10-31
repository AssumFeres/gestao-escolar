# Andamento do Projeto — Sistema de Gestão Escolar

## Módulo: Gestão de Pessoas

Este documento registra o que foi efetivamente implementado, testado e versionado no projeto até o momento. Complementa a `documentacao_arquitetura.md` (decisões de design) e o `GUIA_DE_SETUP.md` (onboarding técnico) — aqui o foco é **status real do código**, não teoria.

---

## 1. Ambiente e Infraestrutura

| Item | Status | Observações |
|---|---|---|
| Repositório Git | ✅ Criado | `github.com/AssumFeres/gestao-escolar`, privado |
| Estratégia de branches | ✅ Ativa | `main` (estável) + `dev` (trabalho atual) |
| `.gitignore` | ✅ Configurado | Exclui `venv/`, `db.sqlite3`, `.env`, `__pycache__/` |
| Ambiente virtual | ✅ Funcional | Testado em 2 máquinas (casa e quartel) |
| Django | ✅ Instalado | Versão 5.2.17 |
| Banco de dados | ✅ SQLite (dev) | PostgreSQL planejado para produção/nuvem — ainda não configurado |
| pytest + pytest-django | ✅ Configurado | `pytest.ini` na raiz, testes rodando em <0.3s |
| README de setup | ✅ Criado | Guia completo para novos integrantes do grupo, testado na prática (inclui troubleshooting real de erros enfrentados) |

### Multi-máquina — validado

O fluxo `git clone` → `venv` → `pip install` → `migrate` → `createsuperuser` foi testado com sucesso em duas máquinas diferentes (casa e quartel), confirmando que o projeto é portátil e não depende de configuração específica de nenhuma máquina.

**Lição registrada:** `git status` sozinho não detecta commits novos no remoto — é necessário `git fetch`/`git pull` para atualizar. Isso já está documentado no guia de setup, seção "Erros comuns".

---

## 2. Models Implementados

Todos em `pessoas/models.py`, aplicados via migration `0001_initial`.

| Model | Tipo de relação | Observação de design |
|---|---|---|
| `Pessoa` | — | `Endereco` como Value Object embutido (campos prefixados, sem tabela própria) |
| `Vinculo` | Multi-table inheritance (base) | Tabela própria, permite consulta genérica `pessoa.vinculos.all()` |
| `VinculoDiscente` | Herda de `Vinculo` | Campo exclusivo: `numero_matricula` |
| `VinculoDocente` | Herda de `Vinculo` | Método `possui_treinamento_valido()` — stub, aguarda módulo de Treinamentos |
| `VinculoGestao` | Herda de `Vinculo` | Associado a `FuncaoGestao` |
| `FuncaoGestao` | FK → `VinculoGestao` | Enum `TipoFuncaoGestao` (Diretor, GQ, Coordenador, Secretaria) |
| `Habilitacao` | — | Catálogo de habilitações técnicas |
| `FuncaoGestaoHabilitacao` | Tabela associativa | Só deve existir quando `tipo_funcao = COORDENADOR` — regra aplicada no Service, não no Model |
| `Disciplina` | — | Versão mínima (sem campo `modulo` ainda, reservado para o Bounded Context de Turmas) |
| `Capacidade` | FK → `VinculoDocente` (não → `Pessoa`) | Reforça no schema a exclusividade: só quem tem `VinculoDocente` pode ter Capacidade |

**Validado via Django Admin:** todos os 9 models registrados em `admin.py`, cadastro manual testado (Pessoa + VinculoDocente com FK funcionando).

---

## 3. Services Implementados

Todos em `pessoas/services.py`.

### 3.1 `AssociarHabilitacaoService`

Associa uma `Habilitacao` a uma `FuncaoGestao`, validando a invariante de domínio: **só Coordenador pode ter Habilitação**.

- Lança `ValidationError` se a função não for `COORDENADOR`.
- Usa `transaction.atomic()` para garantir consistência.

### 3.2 `CadastrarPessoaComVinculoService`

Orquestra a criação de uma `Pessoa` junto com seu primeiro `Vinculo` (Discente, Docente ou Gestão), numa única transação.

- Recebe `dados_pessoa` (dict), `tipo_vinculo` (string) e `dados_vinculo` (dict).
- Mapeia o tipo para a classe de Vínculo correta (`VinculoDiscente`/`VinculoDocente`/`VinculoGestao`).
- Lança `ValidationError` para tipo de vínculo inválido, sem chegar a criar a Pessoa.

---

## 4. Testes Automatizados

**Status atual: 6 testes, todos passando.**

```
pessoas/tests/test_services.py .............................. (2 testes)
pessoas/tests/test_cadastrar_pessoa.py ....................... (4 testes)

6 passed in 0.27s
```

| Arquivo | Cenários cobertos |
|---|---|
| `test_services.py` | Associação de Habilitação aceita (Coordenador) e rejeitada (Diretor) |
| `test_cadastrar_pessoa.py` | Cadastro com vínculo Discente, cadastro com vínculo Docente, rejeição de tipo inválido, verificação de atomicidade da transação |

Todos os testes usam `@pytest.mark.django_db` e rodam contra um banco de teste isolado (criado e destruído automaticamente pelo pytest-django a cada execução) — não afetam o `db.sqlite3` de desenvolvimento.

**Nota técnica pendente:** o teste `test_nao_cria_pessoa_quando_tipo_vinculo_invalido` confirma que a Pessoa não é criada com tipo de vínculo inválido, mas o cenário não testa exatamente a reversão de uma transação parcialmente executada (a validação do tipo acontece antes do bloco `transaction.atomic()`, então a Pessoa nunca chega a ser criada nesse caso). Não é um bug — o comportamento está correto — mas o teste poderia ser mais preciso sobre o que está validando. Revisar quando houver um cenário real de falha no meio da transação.

---

## 5. Histórico de Commits Relevantes (branch `dev`)

| Commit | Descrição |
|---|---|
| `chore: adiciona .gitignore inicial` | Primeiro commit, antes de qualquer código |
| `feat: estrutura inicial do projeto Django` | `manage.py`, `config/`, `requirements.txt` |
| `feat: models de Pessoa, Vinculo, FuncaoGestao, Capacidade e admin` | Model layer completo + Django Admin |
| `docs: adiciona guia de setup para o grupo` | `README.md` |
| `feat: AssociarHabilitacaoService com testes automatizados` | Primeiro Service + 2 testes |
| `chore: adiciona __init__.py em pessoas/tests` | Correção de estrutura de pacote |
| `feat: CadastrarPessoaComVinculoService com testes automatizados` | Segundo Service + 4 testes |

---

## 6. O Que Ainda Falta (Escopo Atual do PI)

- [ ] `BuscarEnderecoPorCepService` (integração com API externa ViaCEP — Porta/Adaptador)
- [ ] Camada de Views/API (DRF) expondo os Services já prontos
- [ ] Serializers de entrada/saída
- [ ] Template Views (HTML) para cadastro visual de Pessoa/Vínculo
- [ ] JavaScript pontual (busca de CEP, associação de habilitação sem reload)
- [ ] Configuração de PostgreSQL (ainda em SQLite)
- [ ] Deploy em nuvem
- [ ] Testes de Views/API (além dos testes de Service já existentes)
- [ ] Adequação de acessibilidade nos templates HTML

## 7. Fora do Escopo Deste PI (lembrete)

Turma, Módulo (relação com Disciplina), Atribuição de Instrutor, Gestão de Treinamentos, Diário de Classe — mapeados como Bounded Contexts futuros, ver `documentacao_arquitetura.md`, seção 5.

---

*Última atualização: commit `b347ae3` na branch `dev`.*
