# Andamento do Projeto — 35

**Data:** 06-07/09/2026
**Branch:** `dev`
**Sessão dedicada a: construir a tela de navegação inicial (sidebar por ator), a partir de um modelo trazido pela pessoa responsável (slides em `.pptx`) — app novo `nucleo`, menu centralizado, e 2 rodadas de correção de bugs reais encontrados em uso.**

---

## 1. Modelo trazido e evolução (slides 1-4)

A pessoa responsável trouxe um modelo visual em 4 versões progressivas: grade simples de 8 módulos (slide 1) → agrupamento por ator (Gestão/Qualidade/Secretaria/Coordenação/Instrutores, slide 2) → sidebar accordion com cabeçalho de usuário (slide 3) → sidebar com grupo expandido e destaque visual (slide 4).

**Esclarecido antes de codar:** o agrupamento por ator é só uma "camada superficial de links", **não é controle de acesso** — não filtra por permissão, só organiza visualmente. Controle de acesso de verdade fica para quando login/autenticação existir (confirmado como item de Backlog futuro, incluindo recuperação de senha por e-mail e autenticação em dois fatores).

**Descoberta durante a análise:** o agrupamento por ator não bate 1:1 com `CategoriaFuncao` (só tem 3 baldes: Discente/Docente/Gestão) — os 5 atores do modelo são mais finos que isso (Diretor, Gerente de Qualidade e Coordenador de Curso são todos `categoria=GESTAO` hoje, mas são 3 grupos diferentes no menu). Registrado como ponto de atenção para quando o controle de acesso de verdade for desenhado.

---

## 2. App novo `nucleo` — sem models, sem migration

Criado para hospedar a "casca" do sistema: tela inicial (`/`), página genérica "Em Construção" (para qualquer módulo do menu ainda sem tela própria), e o `menu.py` (fonte única do menu, injetada em todo template via `context_processor` — nenhuma View existente precisou ser tocada).

**Bug real corrigido de saída:** `base.html` tinha um link morto (`<a href="/pessoas/">`) — sobra esquecida do rename `pessoas`→`cadastros` (diário 17, 31/08/2026), nunca atualizada porque na época `base.html` não era foco de nenhuma sessão. Motivo original de a pessoa responsável abrir esta frente: notou a falta de "porta de saída" numa tela.

---

## 3. `base.html`/`base.css` reestruturados

Sidebar com accordion (JS, `sidebar.js`) — progressive enhancement: sem JavaScript, todos os submenus continuam visíveis e clicáveis (só não tem o efeito de abrir/fechar); com JS, vira accordion de verdade. Cabeçalho ganhou área de usuário + botão de logout — ambos **placeholder**, já que não existe login/sessão real ainda.

**Mudança de layout que afeta toda página existente:** `main` deixou de ficar centralizado com `max-width:900px` — passou a ocupar o espaço ao lado do sidebar. Testado e confirmado que as telas já existentes (Disciplina, Módulo, Ata) continuam renderizando corretamente com o `base.html` novo.

**Gap identificado durante o levantamento de telas:** `Turma` nunca teve lista própria — só existia dentro do detalhe de uma Oferta de Módulo específica (decisão consciente de design, ver `docs/34`). Resolvido criando `lista_turmas.html` (lista global, só leitura, cada linha leva pro detalhe da Oferta correspondente) — sem criar `detalhe_turma.html` própria, decisão confirmada pela pessoa responsável (Turma não tem nenhum "filho" pra mostrar, criar uma segunda superfície de edição seria redundante).

---

## 4. Rodada de correções visuais — 3 problemas reais encontrados em uso

Depois de operar o sistema de verdade, a pessoa responsável relatou 3 problemas:

### 4.1 — Cor de fundo do grupo aberto
Pedido inicial: trocar branco por `#F4F7FA` (mesmo tom da área de trabalho) — implementado numa primeira rodada aplicando a cor tanto no título do grupo quanto no submenu inteiro. **Corrigido depois**, quando a pessoa responsável esclareceu que só o título do grupo deveria mudar de cor — o fundo do submenu em si nunca deveria ter mudado, sempre `#002060`.

### 4.2 — Bug real: os 3 "Relatórios" abrindo juntos
Ao clicar em "Relatórios" (existe em 3 grupos — Gestão, Secretaria, Coordenação), os três grupos acendiam ao mesmo tempo. **Causa raiz:** cada item sem tela própria virava uma URL `/em-construcao/<rótulo>/`, usando o **texto visível** como identificador — como os três compartilham o mesmo texto "Relatórios", o sistema não conseguia distingui-los.

**Correção:** cada item sem tela própria ganhou uma `chave` única, invisível (ex: `relatorios-gestao`, `relatorios-secretaria`, `relatorios-coordenacao`), separada do `label` (o texto mostrado). A URL passou a usar a chave; a tela "Em Construção" busca o texto certo pra exibir procurando essa chave em `menu.py` — nenhuma duplicação de nome em dois lugares.

### 4.3 — Destaque do item ativo incompleto
Pedido: negrito **e** itálico no item ativo (só tinha negrito). Corrigido junto da correção do item 4.1 (cor do fundo).

**Lição de processo registrada:** essas 3 correções expuseram um problema real no próprio processo de edição desta sessão — várias tentativas de editar os arquivos grandes (`views.py`, `base.html`, `base.css`) por substituição de texto **corromperam silenciosamente** o conteúdo (a ferramenta reportava sucesso, mas o texto novo não entrava, ou apagava trecho vizinho). Só foram pegos porque, a partir de um certo ponto, passou a se validar com testes funcionais reais (Django rodando de verdade, requisições simuladas), não só checagem de sintaxe. Fica como prática a reforçar: sempre que possível, validar comportamento de verdade, não só "o arquivo compila".

---

## 5. Decisão de arquitetura do menu: Opção A confirmada

Discutida a estrutura de fundo do `menu.py`: **Opção A** (cada ator tem sua própria lista explícita de itens, escrita à mão — se um "módulo" aparece pra vários atores, cada ocorrência é uma entrada própria, com sua própria chave/URL) **vs. Opção B** (cada módulo declara quais atores podem vê-lo, o menu de cada ator seria filtrado a partir de uma lista única de módulos).

**Confirmado: Opção A**, que já era a implementada. Motivo: o próprio caso "Relatórios" prova que não é o mesmo módulo repetido — são recortes diferentes por trás do mesmo nome. A Opção B resolveria um problema (módulo idêntico duplicado) que não existe no caso real do projeto, e tende a misturar "o que aparece no menu" com "quem tem permissão" — dois conceitos que a própria pessoa responsável fez questão de manter separados desde o início desta frente.

---

## 6. Limpeza final: links "Voltar" redundantes com o sidebar

Removidos, por decisão da pessoa responsável, os links `<a href="/cadastros/">Voltar para Pessoas</a>` de 6 telas de lista (Disciplinas, SubModulos, Modulos, Ofertas de Módulo, Atas, Turmas) — não eram só redundantes com o sidebar, estavam **errados de verdade** (o texto sempre dizia "Voltar para Pessoas", mesmo em telas que não têm nada a ver com Pessoa — sobra de copy-paste da primeira tela feita). Mantidos, por ora, os links "Voltar" dentro dos popups em página cheia (fallback sem JS) — esses têm função diferente (cancelar uma ação, voltar pro contexto imediato), não de navegação entre módulos.

---

## Estado geral ao final desta sessão

| Item | Status |
|---|---|
| App `nucleo` (tela inicial, "Em Construção", menu centralizado) | ✅ Implementado |
| Sidebar por ator, accordion, progressive enhancement | ✅ Implementado e testado |
| Link morto `/pessoas/` | ✅ Corrigido |
| `lista_turmas.html` (gap identificado) | ✅ Implementada |
| Bug dos 3 "Relatórios" acendendo juntos | ✅ Corrigido (chave única por item) |
| Cor de fundo do grupo aberto / destaque negrito+itálico | ✅ Corrigidos |
| Decisão de arquitetura do menu (Opção A) | ✅ Confirmada, sem mudança de código |
| Links "Voltar" redundantes/errados nas 6 listas | ✅ Removidos |
| Login/autenticação real | ⏳ Continua como pré-requisito futuro, não iniciado |

---

## Itens novos de Backlog

- [ ] **Login/autenticação de verdade** (com recuperação de senha por e-mail, e autenticação em dois fatores no futuro) — pré-requisito para o cabeçalho de usuário/logout deixarem de ser placeholder, e para o menu por ator eventualmente virar controle de acesso real.
- [ ] **Reconciliar o agrupamento por ator com `Funcao`/`CategoriaFuncao`** quando o controle de acesso for desenhado — hoje o menu é mais fino que os 3 baldes de `CategoriaFuncao` existentes.
- [ ] Abrir automaticamente o grupo da página atual foi resolvido nesta sessão (cálculo no servidor) — mas o **accordion "lembrar" a escolha do usuário entre cliques dentro da mesma sessão** (ex: usuário abre outro grupo manualmente, navega, e o grupo aberto manualmente deveria persistir) não foi implementado — hoje sempre reflete só a URL atual.
- [ ] Considerar revisar os links "Voltar" das telas de **detalhe** (Disciplina/SubModulo/Modulo/OfertaModulo/Ata) — hoje redundantes com o sidebar mas não errados; não removidos nesta sessão, mencionados como possível limpeza futura.

---

## Próximos passos

Retomar o bug/numeração automática de `Ata` (`docs/34`, item em aberto). Depois, considerar o próximo módulo a receber tela própria, seguindo a ordem de prioridade ainda não definida entre Treinamento/Atribuição/Registro de Instrução/Horários/Contratos/Relatórios/Dashboard (`docs/32`).
