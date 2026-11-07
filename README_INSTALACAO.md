# Pacote Codex — Acessibilidade EMCA

Copie o conteúdo deste pacote para a raiz do repositório Django.

Estrutura:

seu-repositorio/
├── AGENTS.md
└── .agents/
    └── skills/
        ├── django-accessibility/
        │   └── SKILL.md
        └── code-change-verification/
            └── SKILL.md

## Primeiro prompt sugerido

Leia o AGENTS.md e use a skill django-accessibility. Faça primeiro uma auditoria da estrutura global de templates, sem alterar código. Identifique base.html, menus, formulários compartilhados, modais, tabelas e JavaScript comum. Depois proponha uma ordem de implementação em pequenos lotes, priorizando mudanças reutilizáveis e de baixo risco. Não altere regras de negócio.

Depois da auditoria, implemente um lote de cada vez e use `code-change-verification` após cada lote.
