# Andamento do Projeto — 31

**Data:** 04/09/2026 (presumido — sessão de continuação direta do diário 29/30)
**Branch:** `dev` (sessão sem commit — dedicada só a revisar e fechar o desenho da estrutura curricular, sem nenhuma linha de código)
**Sessão dedicada a: revisar a especificação trazida pela pessoa responsável (`.txt` com Módulos/SubModulos/Disciplinas/Turmas/Atas), corrigir e confirmar o desenho final antes de implementar.**

---

## Contexto

Continuação direta de `docs/29`/`docs/30`. A pessoa responsável trouxe uma especificação própria, mais detalhada que o desenho inicial da sessão anterior, com uma correção estrutural importante: tabelas intermediárias (M2M) em vez de FK direta entre Disciplina→SubModulo→Módulo.

---

## Avaliação da especificação trazida

**Melhorias confirmadas em relação ao desenho de `docs/29`:**

1. **`SubModuloDisciplina`/`ModuloSubModulo` (tabelas intermediárias com `ordem` própria)** em vez de FK direta (`Disciplina.submodulo`, `SubModulo.modulo`) — correção real: uma Disciplina pode pertencer a mais de um SubModulo, e um SubModulo a mais de um Módulo (ex: "Regulamentação" pode se repetir em módulos diferentes). FK direta do desenho anterior travava isso incorretamente.
2. **`ConteudoProgramatico` como tabela própria** (com `ordem`, `descricao`, `disciplina` FK), em vez de `Disciplina.conteudo_programatico` como texto livre — permite reaproveitamento futuro por um módulo de consumo (ver abaixo).
3. **Padrão `ativo` (soft-deactivate)** em todos os catálogos, complementar ao `on_delete=PROTECT` já usado no projeto — desativar sem apagar, sem sumir do histórico, sem impedir a exclusão de fato quando cabível.
4. **`OfertaModulo`** como nome da entidade que une Módulo a um ano letivo/período — substitui o termo provisório "ModuloAno" usado em `docs/30`.

---

## Decisões confirmadas nesta sessão

- **`Disciplina.sigla`**: mantém a regra já implementada (`CharField(max_length=3)`, `RegexValidator` de 3 letras maiúsculas, `unique=True`) — a proposta do `.txt` (`CharField(10)`, sem regex) não se aplica.
- **`Disciplina.nome`**: mantém `unique=True`. Colisão de nome entre disciplinas de contextos diferentes se resolve prefixando o nome (ex: "Sistema de Comunicação - AVI" vs. "Sistema de Comunicação - CEL"), não relaxando a constraint.
- **`carga_horaria` é fracionária**, múltiplos de 0,75h (1 tempo de aula = 45min); a carga total de uma Disciplina é sempre múltiplo de 5 tempos (3,75h). Validação (`% 3.75 == 0`) registrada para implementação futura, não bloqueante agora.
- **`SubModulo.carga_horaria` é campo CALCULADO**, não editável manualmente — soma das `carga_horaria` das Disciplinas ligadas via `SubModuloDisciplina`. Não pode divergir do Programa de Instrução aprovado (o valor calculado É o valor oficial, não uma segunda fonte que possa contradizer o documento).
- **Ordem do Conteúdo Programático**: campo numérico simples, definido no cadastro — sem necessidade de interface drag-and-drop por enquanto.
- **`OfertaModulo` e `Turma` ENTRAM em `cadastros`** (decisão que estende o limite de "prateleira" definido em `docs/29`) — justificativa: nenhuma das duas referencia `Pessoa`, então são estrutura (quantas turmas existem, de qual módulo, em qual ano), não evento de vínculo. O módulo Atribuição é, nas palavras da pessoa responsável, "uma extensão do cadastro" — cadastros vai até a estrutura anual; Atribuição começa exatamente onde `Pessoa` entra na equação.

## Achado novo: módulo futuro "Registro de Instrução"

Durante a resposta sobre a ordem do Conteúdo Programático, a pessoa responsável revelou uma peça nova do sistema, ainda não mapeada em nenhum documento anterior: um módulo onde o **instrutor** visualiza o conteúdo programático completo de uma Disciplina (definido em `cadastros`) e faz **Update** em cada item, marcando o dia em que foi ministrado e o tipo de aula (prática/teórica/mista). Esse módulo:
- **Consome** `ConteudoProgramatico` de `cadastros` (leitura), mas não pertence a `cadastros`.
- É distinto do módulo Atribuição (`TurmaAluno`) e do módulo Treinamento (já mencionado em sessões anteriores) — parece mais próximo do futuro "Módulo Diário de Classe", já registrado como Fora de Escopo no Kanban, mas focado especificamente no cumprimento do conteúdo programático por Disciplina/Turma, não em frequência/notas. Precisa de uma sessão própria para mapear a relação exata com o Diário de Classe.

---

## Estrutura final fechada (documentação, sem código)

```
Disciplina (nome único, sigla 3 letras única + regex, carga_horaria fracionária,
            tempos_aula CALCULADO = carga_horaria / 0,75, ativo, timestamps)
  ├── ConteudoProgramatico (disciplina FK CASCADE; ordem; descricao; observacao;
  │                         ativo; UNIQUE(disciplina, ordem))
  │                         — consumido futuramente pelo módulo Registro de Instrução
  └── SubModuloDisciplina (submodulo FK; disciplina FK; ordem;
                           UNIQUE(submodulo,disciplina); UNIQUE(submodulo,ordem))
       │
       ▼
     SubModulo (nome; codigo opcional único; carga_horaria CALCULADA — soma via
                SubModuloDisciplina, não editável; ativo; timestamps)
       │
       └── ModuloSubModulo (modulo FK; submodulo FK; ordem;
                             UNIQUE(modulo,submodulo); UNIQUE(modulo,ordem))
             │
             ▼
           Modulo (nome único, texto livre — "Básico", "Especializado em Aviônica",
                    etc.; codigo opcional único; descricao; ativo; timestamps)
             │
             ▼
           OfertaModulo (modulo FK PROTECT; ano_letivo; periodo choices
                         MATUTINO/VESPERTINO/NOTURNO; data_inicio/fim opcional;
                         situacao choices PLANEJADA/EM_ANDAMENTO/ENCERRADA;
                         observacao)
             │
             ▼
           Turma (oferta_modulo FK PROTECT; nome; sigla; capacidade_maxima
                  opcional; situacao choices; observacao;
                  UNIQUE(oferta_modulo, sigla))

Ata (numero único; tipo ORDINARIA/EXTRAORDINARIA; data; assunto opcional;
     observacao; timestamps) — catálogo independente, sem campo de motivo;
     motivo/contexto de uso vira TurmaAluno.ata_inicio/ata_termino no futuro
     módulo Atribuição.
```

**Módulo Atribuição (futuro) fica reduzido a uma peça só:** `TurmaAluno` — o vínculo Pessoa↔Turma (Discente), com `ata_inicio`/`ata_termino`, `data_inicio`/`data_fim`, `status`. Bem mais enxuto do que o desenho inicial de `docs/30`, já que `OfertaModulo`/`Turma` migraram para `cadastros`.

---

## Estado geral ao final desta sessão

| Item | Status |
|---|---|
| Especificação de Módulo/SubModulo/Disciplina/Turma/Ata revisada e corrigida | ✅ Fechada, documentada |
| Decisão: `OfertaModulo`/`Turma` entram em `cadastros` | ✅ Confirmada |
| Módulo Atribuição reduzido a `TurmaAluno` | ✅ Atualizado em `docs/30` |
| Módulo novo "Registro de Instrução" identificado | 📝 Registrado, não mapeado em detalhe |
| Implementação (models, migrations, Admin) | ⏳ Não iniciada — próxima sessão |

---

## Próximos passos

Implementar a estrutura fechada acima: `Disciplina` (ajustes), `ConteudoProgramatico`, `SubModulo`, `SubModuloDisciplina`, `Modulo`, `ModuloSubModulo`, `OfertaModulo`, `Turma`, `Ata` — todas em `cadastros`, Admin-only por enquanto. Depois, mapear em detalhe a relação entre "Registro de Instrução" e o já registrado "Módulo Diário de Classe" (Fora de Escopo).
