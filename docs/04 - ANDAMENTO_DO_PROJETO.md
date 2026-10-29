# Andamento do Projeto — 04

**Data:** 23/08/2026
**Branch:** `dev`
**Commits desta etapa:** `fbfc3b1`, `97e2915`, `f337e0d`, `78cf27f`

---

## O que foi feito

### 1. Campo `sigla` em `Disciplina`

Adicionado campo `sigla` (`CharField`, `max_length=3`, `unique=True`), com `RegexValidator` exigindo exatamente 3 letras maiúsculas (`^[A-Z]{3}$`). `__str__` atualizado para `"SIGLA - Nome"`. Migration `0002_disciplina_sigla` aplicada sem impacto em dados existentes (banco local estava vazio nessa máquina).

### 2. Terceiro endpoint de API — Cadastro de Pessoa

`POST /api/pessoas/pessoas/` — expõe o `CadastrarPessoaComVinculoService`, já existente desde a Etapa 1.

- `CadastrarPessoaInputSerializer` / `CadastrarPessoaOutputSerializer` adicionados.
- `CadastrarPessoaView` criada, lidando com a variação de campos por tipo de vínculo (ex: `numero_matricula` só é relevante para Discente).
- Testado com sucesso: `201 Created`, criando Pessoa + VinculoDiscente numa única chamada.

**Com isso, os 3 Services do projeto estão 100% expostos via API.**

### 3. Primeiras Template Views (HTML)

- `templates/base.html`: layout compartilhado (cabeçalho, navegação, bloco de conteúdo).
- `static/global/css/base.css`: estilo básico.
- `pessoas/templates/pessoas/lista.html` + `ListaPessoasView`: lista todas as Pessoas cadastradas.
- `pessoas/templates/pessoas/detalhe.html` + `DetalhePessoaView`: mostra dados completos de uma Pessoa e o histórico de todos os seus vínculos.

---

## 🐛 Bug de tooling: auto-format do VSCode corrompendo templates Django

Este foi o problema mais consumidor de tempo da sessão, e vale registrar em detalhe porque não é um erro de lógica — é um problema de ferramenta que qualquer integrante do grupo usando VSCode vai sofrer, se não corrigido.

### Sintoma

Repetidas vezes, ao criar ou editar arquivos `.html` com tags Django (`{% block %}`, `{% extends %}`), o servidor retornava `TemplateSyntaxError: Unclosed tag on line 1: 'block'`, mesmo com o conteúdo aparentemente correto ao visualizar no editor.

### Causa raiz

O VSCode, ao salvar arquivos `.html`, estava aplicando **formatação automática** (`formatOnSave`) que quebra linhas longas — mas o formatador HTML não reconhece `{% ... %}` como uma unidade indivisível (tag Django), e quebra a linha *no meio* da tag. Por exemplo:

```html
{% block title %}Pessoas - Sistema de Gestao Escolar{% endblock %}
```
virava, após salvar:
```html
{% extends 'base.html' %} {% block title %}Pessoas - Sistema de Gestao Escolar{%
endblock %} {% block content %}
```

Isso não é visível como "erro" no editor (o HTML resultante parece normal), só quebra quando o Django tenta interpretar a tag partida ao meio.

### Diagnóstico

Foi necessário, em mais de uma ocasião, usar `Get-Content` no PowerShell para inspecionar o conteúdo real do arquivo salvo em disco — o que revelou a quebra de linha no meio da tag, diferente do que aparecia visualmente no VSCode.

### Correção aplicada

1. **Correção pontual:** arquivos recriados via terminal (`Set-Content` com array de strings, uma linha por elemento) para garantir integridade byte a byte, contornando o problema imediato.
2. **Correção definitiva:** criado `.vscode/settings.json`, desabilitando `formatOnSave` para arquivos `.html`:
   ```json
   {
       "[html]": { "editor.formatOnSave": false },
       "[django-html]": { "editor.formatOnSave": false }
   }
   ```
   Esse arquivo foi **versionado no Git**, então qualquer colega que clonar o repositório já herda a configuração automaticamente — não é uma correção "só nessa máquina".

### Lição para o relatório do PI

Esse episódio é um bom exemplo de troubleshooting de ambiente de desenvolvimento, distinto de debug de código — vale mencionar na documentação como parte do processo real de desenvolvimento em equipe, já que configuração de editor divergente entre integrantes é uma fonte comum (e antes invisível) de bugs "fantasmas".

---

## Decisões de negócio esclarecidas nesta etapa

### `ativo` e `data_fim` em `Vinculo` são independentes, propositalmente

Questionado se `ativo=True` implicaria `data_fim` vazio. Resposta: não — são campos independentes, permitindo 4 combinações válidas (ex: vínculo ativo com término já programado; vínculo inativo sem data formal de encerramento). Template ajustado para mostrar "-----" quando `data_fim` está vazio, sem impor nenhuma regra de preenchimento obrigatório entre os dois campos.

### A tabela de vínculos no detalhe da Pessoa mostra o histórico completo, por design

Confirmado que `pessoa.vinculos.all()` retorna todos os vínculos de todos os subtipos (Discente, Docente, Gestão) que a Pessoa já teve, passados e presentes — consequência direta da decisão de Multi-table Inheritance tomada na fase de modelagem (Parte 2). Nenhum ajuste foi necessário para isso já funcionar; foi apenas confirmado que o comportamento observado era o esperado.

---

## Erros e correções desta etapa

| O que aconteceu | Causa | Como foi resolvido |
|---|---|---|
| `NameError: name 'CadastrarPessoaComVinculoService' is not defined` | Import duplicado e incompleto em `views.py` (duas linhas `from .services import ...` diferentes, nenhuma com o novo Service) | Consolidado em um único bloco de import, listando os 3 Services |
| `TemplateSyntaxError: Unclosed tag` (recorrente) | Ver seção "Bug de tooling" acima | `.vscode/settings.json` com `formatOnSave: false` para HTML |
| `{{ vinculo.vinculodocente\|default:"" }}` aparecendo como texto literal na página | Tentativa de identificar o subtipo de `Vinculo` encadeando 3 lookups de atributo direto no template — abordagem frágil | Criada property `tipo_legivel` no Model `Vinculo`, movendo a lógica para Python |

---

## Estado geral ao final desta etapa

| Camada | Status |
|---|---|
| Models | 9 entidades, completos para o escopo atual |
| Services | 3 de 3, testados (7 testes) |
| API (DRF) | 3 de 3 endpoints funcionando |
| Template Views | 2 (lista + detalhe de Pessoa) |
| Tooling | Bug de auto-format corrigido e versionado |

---

## Próximos passos

- Formulário de cadastro de Pessoa via Template View (POST, não só leitura).
- JavaScript pontual (busca de CEP no formulário).
- Testes automatizados para as Template Views.
