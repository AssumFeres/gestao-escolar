Vamos continuar o projeto Gestão Escolar (PI de Engenharia da Computação). Já tivemos uma conversa anterior longa, encerrada por tamanho — a continuidade agora vem inteiramente da documentação em `docs/`, não de um resumo manual.

**Antes de qualquer coisa, leia:**
1. `docs/00 - KANBAN.md` — estado atual do projeto (Concluído / A Fazer / Backlog)
2. `docs/16 - PLANO_DE_MIGRACAO_APP_CADASTROS.md` — o plano que vamos executar agora: renomear o app Django `pessoas` para `cadastros` (7 etapas, nenhuma ainda executada)

**Onde paramos:** acabamos de fechar por completo a migração `Vinculo`/`FuncaoGestao`/`Habilitacao` → `Funcao`/`AtribuicaoFuncao` (mesclada em `dev`, ver `docs/06` a `docs/15 - ANDAMENTO_DO_PROJETO.md` para o histórico completo). Hoje vamos começar a próxima frente: renomear o app `pessoas` para `cadastros`, já com duas decisões confirmadas no plano — (1) resetar o banco local e as migrations antigas, já que não há dado real ainda; (2) a URL pública também muda, de `/pessoas/` para `/cadastros/`.

**Como prefiro trabalhar:** passo a passo, um comando por vez, eu colo o resultado antes do próximo passo. Commits pequenos e frequentes, sempre com `git status` antes de `git add`. Documentar no fim da sessão (diário numerado, próximo é `17`, e atualizar o Kanban).

**Para começar:** confirme que leu os dois documentos, e comece pela Etapa 1 do plano (`feature/rename-pessoas-cadastros` a partir de `dev`, depois renomear pasta e caminhos internos).
