# Andamento do Projeto — 03

**Data:** 21/08/2026
**Branch:** `dev`
**Commit desta etapa:** `bb01f2e`

---

## O que foi feito

### 1. Endpoint de API — Busca de CEP

`GET /api/pessoas/cep/<cep>/` — expõe o `BuscarEnderecoPorCepService` (já existente) via DRF.

- `pessoas/serializers.py`: `BuscarCepInputSerializer`, `EnderecoOutputSerializer`.
- `pessoas/views.py`: `BuscarCepView`.
- `pessoas/api_urls.py`: rota `cep/<str:cep>/`.
- `config/urls.py`: inclusão de `pessoas.api_urls` sob `api/pessoas/`.

Testado no navegador com CEP real (`01310100`) — retornou `200 OK` com o endereço da Av. Paulista, incluindo o campo `complemento` retornado pela própria ViaCEP.

### 2. Endpoint de API — Associar Habilitação

`POST /api/pessoas/funcoes-gestao/habilitacoes/` — expõe o `AssociarHabilitacaoService`.

- `FuncaoGestaoHabilitacaoInputSerializer` / `FuncaoGestaoHabilitacaoOutputSerializer` adicionados.
- `AssociarHabilitacaoView` criada.
- Rota adicionada em `api_urls.py`.

Testado nos dois cenários pela interface navegável do DRF:
- Função **Diretor** + Habilitação → `400 Bad Request`, mensagem de erro correta.
- Função **Coordenador** + Habilitação → `201 Created`.

### 3. `__str__` adicionado aos Models

`VinculoDiscente`, `VinculoDocente`, `VinculoGestao` e `Habilitacao` não tinham `__str__`, o que fazia o Django Admin exibir nomes genéricos (`VinculoGestao object (1)`, `Habilitacao object (4)`), dificultando a seleção nos formulários. Corrigido — não exigiu migration, é só representação visual.

---

## 🐛 Bug detectado: Django Admin não respeita a regra de negócio do Service

Este é o achado mais importante da sessão, e vale registrar com destaque.

### O que aconteceu

Ao testar o cenário de bloqueio (Função Diretor não pode ter Habilitação), o teste foi feito **duas vezes por caminhos diferentes**:

1. Via **endpoint da API** (`AssociarHabilitacaoView`) → bloqueado corretamente (`400`).
2. Via **Django Admin**, criando um registro de `FuncaoGestaoHabilitacao` diretamente na tela `Change funcao gestao habilitacao` → **aceito indevidamente**, associando uma Habilitação ("AVI - Aviônicos") a uma Função de Gestão do tipo Diretor.

### Causa raiz

O Django Admin gera formulários que conversam **diretamente com o Model e o banco** (`FuncaoGestaoHabilitacao.objects.create()`), sem passar pelo `AssociarHabilitacaoService`. A regra de negócio ("só Coordenador pode ter Habilitação") só existe dentro do Service — nunca foi replicada no Model nem no banco. Ou seja: **a arquitetura em camadas funcionou exatamente como desenhada** — o problema é que o Admin é uma porta de entrada que não está conectada à camada de Service, e isso não tinha sido percebido antes por nunca termos testado a criação por ali.

### Correção aplicada nesta etapa

O registro inválido criado durante o teste foi apagado manualmente pelo Admin, para não deixar dado inconsistente no banco de desenvolvimento.

### Correção estrutural — pendente, registrada no Kanban (Backlog)

A vulnerabilidade em si **não foi corrigida ainda** — decisão consciente de continuar o roteiro de Views/API e tratar isso como item de backlog, com três opções possíveis a avaliar:
1. Reforçar a validação também no `Model`, via método `clean()`.
2. Adicionar `CHECK constraint` no PostgreSQL (quando migrarmos do SQLite).
3. Restringir/desabilitar a criação manual de `FuncaoGestaoHabilitacao` pelo Admin, forçando todo cadastro a passar pela API/Service.

### Lição para o relatório do PI

Esse episódio é um bom exemplo prático para discutir na fundamentação teórica: a abordagem "DDD pragmático" adotada (Parte 2 da documentação de arquitetura) aceita conscientemente que o Django Admin é uma interface **fora do controle do Service** — o que é uma concessão válida para produtividade, mas exige decisão explícita sobre quais entidades podem ser editadas livremente pelo Admin e quais não podem, por terem invariantes de domínio sensíveis.

---

## Erros e mal-entendidos do dia (e como foram resolvidos)

| O que aconteceu | Causa | Como foi resolvido |
|---|---|---|
| `ModuleNotFoundError: No module named 'pessoas.services'` | Arquivo criado no editor mas não salvo antes de rodar o comando | Reabrir o arquivo, colar o conteúdo, `Ctrl+S`, confirmar com `dir` que o tamanho em bytes não é zero |
| `ModuleNotFoundError: No module named 'pessoas.api_urls'` | Mesma causa — `serializers.py` não existia ainda quando `views.py` tentou importá-lo, quebrando a cadeia de import | Confirmado com `dir pessoas\serializers.py`; arquivo criado e salvo |
| Confusão sobre cor **laranja** nos nomes de arquivo no VSCode (`urls.py`, `views.py`, `serializers.py`) | Interpretado como possível erro | Esclarecido: é o indicador padrão do Explorador de Arquivos do VSCode para status Git — **`U`** (Untracked, arquivo novo não commitado) e **`M`** (Modified, arquivo existente alterado). Não indica erro de código. |
| Fluxo do Django Admin pareceu "ao contrário" do esperado (esperava escolher tipo de vínculo antes de preencher dados da Pessoa) | Django Admin gera uma tela por Model registrado; como `Vinculo` aponta para `Pessoa` (não o contrário), o cadastro precisa ser feito em duas telas separadas, começando pela Pessoa | Explicado o motivo estrutural; solução real (Inlines ou Template Views customizadas) adiada para o Backlog |
| `HTTP 405 Method Not Allowed` ao acessar a URL do endpoint de Habilitação diretamente no navegador | Acessar uma URL pelo navegador sempre gera um `GET`; a view só aceita `POST` | Não era erro — o formulário de teste da própria página do DRF (campo "Content", com JSON manual, ou trocando o "Media type") permite enviar o `POST` corretamente |
| Testou o registro de `FuncaoGestaoHabilitacao` pelo Admin, esperando que a regra de negócio fosse aplicada | Ver seção "Bug detectado" acima | Registro incorreto apagado; correção estrutural movida para o Backlog |

---

## Estado dos endpoints ao final desta etapa

| Endpoint | Método | Status | Testado |
|---|---|---|---|
| `/api/pessoas/cep/<cep>/` | GET | ✅ | Sim — CEP real, `200 OK` |
| `/api/pessoas/funcoes-gestao/habilitacoes/` | POST | ✅ | Sim — bloqueio (`400`) e sucesso (`201`) |
| Endpoint de `CadastrarPessoaComVinculoService` | — | ⏳ Não iniciado | — |

---

## Próximos passos

- Endpoint de API para `CadastrarPessoaComVinculoService`.
- Avaliar, junto com o grupo, qual das 3 opções de correção do bug do Admin adotar.
