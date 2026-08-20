# Andamento do Projeto — 02

**Data:** 20/08/2026
**Branch:** `dev`
**Commit desta etapa:** `662f87f`

---

## O que foi feito

### 1. `BuscarEnderecoPorCepService`

Terceiro Service implementado, fechando o padrão Porta/Adaptador que estava planejado desde a fase de modelagem.

- **Porta** (`infraestrutura/cep/ports.py`): `AbstractCepClient`, interface abstrata com o método `buscar_endereco(cep) -> Endereco`.
- **Adaptador** (`infraestrutura/cep/adapters.py`): `ViaCepClient`, implementação concreta que consome a API pública ViaCEP.
- **Service** (`pessoas/services.py`): `BuscarEnderecoPorCepService`, recebe o cliente de CEP por injeção de dependência (`cliente_cep=None`, com `ViaCepClient()` como padrão) — permite trocar o provedor ou usar um mock em teste sem alterar o Service.

A pasta `infraestrutura/` foi criada na **raiz do projeto**, fora do app `pessoas/`, como definido na Parte 5 da arquitetura — reforça que é uma capacidade técnica genérica, não específica do domínio de Pessoas.

### 2. Teste automatizado

`pessoas/tests/test_buscar_cep.py` — testa o Service usando `unittest.mock.Mock` no lugar do `ViaCepClient` real, validando que:
- o Service retorna o `Endereco` fornecido pelo cliente injetado;
- o método `buscar_endereco` do cliente é chamado exatamente uma vez, com o CEP correto.

Nenhuma chamada de rede real acontece durante o teste — validação direta do valor prático do DIP aplicado no Service.

**Resultado:** `7 passed` (4 de `CadastrarPessoaComVinculoService` + 2 de `AssociarHabilitacaoService` + 1 novo).

---

## Incidente registrado: pastas criadas no lugar errado

Durante a criação da `infraestrutura/`, os comandos foram executados a partir de dentro da pasta `pessoas/` (em vez da raiz do projeto), o que gerou:

- `infraestrutura/` criada dentro de `pessoas/` (deveria estar na raiz);
- uma pasta duplicada `pessoas/pessoas/`, com uma cópia parcial de `services.py` (só a classe nova) e o teste `test_buscar_cep.py`.

**Resolução:**
1. `infraestrutura/` movida para a raiz do projeto com `Move-Item`.
2. Conteúdo de `pessoas/pessoas/services.py` (a classe `BuscarEnderecoPorCepService`) mesclado manualmente no `pessoas/services.py` correto.
3. `test_buscar_cep.py` movido para `pessoas/tests/`, junto dos demais testes.
4. Pasta duplicada `pessoas/pessoas/` removida com `Remove-Item -Recurse -Force`.
5. Suíte de testes rodada novamente para confirmar integridade (`7 passed`).

Nenhum código foi perdido. Nenhum commit foi feito enquanto a estrutura estava incorreta — o problema foi identificado e corrigido antes de qualquer `git add`.

**Lição prática:** conferir o prompt do terminal (pasta atual) antes de rodar comandos que criam arquivos ou pastas, especialmente `mkdir` e `code`.

---

## Estado dos Services ao final desta etapa

| Service | Status | Testes |
|---|---|---|
| `AssociarHabilitacaoService` | ✅ | 2 |
| `CadastrarPessoaComVinculoService` | ✅ | 4 |
| `BuscarEnderecoPorCepService` | ✅ | 1 |

**Total: 7 testes, todos passando.**

---

## Próximos passos (não iniciados nesta etapa)

- Camada de Views/API (DRF) expondo os três Services.
- Serializers de entrada/saída.
