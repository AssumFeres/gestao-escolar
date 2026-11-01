# Plano de Testes Manuais — Sistema de Gestão Escolar EMCA

**Criado em:** 08/09/2026, ao final da sessão de correções do módulo Atribuição/Turma (`docs/39`).
**Como usar:** para cada teste, execute o passo a passo, compare com o "Resultado esperado", e preencha "Resultado encontrado" com o que realmente aconteceu (Passou / Falhou + descrição). Testes marcados com 🔴 são regressão de bugs já corrigidos nesta sessão — vale confirmar que continuam corrigidos depois de qualquer mudança futura.

---

## Bloco 1 — Cadastro de Pessoa

**Teste 01 — Criar aluno novo, testar preenchimento automático de CPF e API de CEP**
Resultado esperado: ao digitar um CPF já cadastrado, os campos da Pessoa devem se preencher sozinhos. Ao digitar um CEP válido, endereço/cidade/UF devem se preencher automaticamente via API.
Resultado encontrado —

**Teste 02 — Cadastrar aluno com CANAC preenchido e Código de Matrícula ANAC em branco**
Resultado esperado: o campo Código de Matrícula ANAC deve continuar vazio — não deve receber automaticamente o valor do CANAC.
Resultado encontrado —

**Teste 03 — Cadastrar dois alunos com o mesmo CPF**
Resultado esperado: o segundo cadastro deve reaproveitar/atualizar a Pessoa existente (busca por CPF), não criar uma duplicata.
Resultado encontrado —

**Teste 04 🔴 — Tentar dar Função Discente a alguém que já é Discente ativo**
Resultado esperado: bloqueado, com mensagem "Esta pessoa já possui a Função Discente ativa e não pode acumular outra Função."
Resultado encontrado —

**Teste 05 🔴 — Aluno que já se formou/encerrou vínculo tenta ser cadastrado como Discente de novo**
Resultado esperado: permitido — cria uma nova `AtribuicaoFuncao` (novo vínculo), sem reabrir a antiga.
Resultado encontrado —

---

## Bloco 2 — Catálogos (Disciplina, SubModulo, Módulo)

**Teste 06 — Cadastrar Disciplina com carga horária que não bate com o Programa de Instrução**
Resultado esperado: aviso claro de divergência, formulário não salva até corrigir.
Resultado encontrado —

**Teste 07 — Cadastrar SubModulo com sigla já existente**
Resultado esperado: mensagem de erro amigável (idealmente em português), sem tela de debug.
Resultado encontrado —

**Teste 08 — Vincular a mesma Disciplina a dois SubModulos diferentes**
Resultado esperado: sistema pede confirmação antes de permitir (não bloqueia automaticamente).
Resultado encontrado —

**Teste 09 — Alternar Ativo/Inativo de uma Disciplina/SubModulo/Módulo já vinculado em algum lugar**
Resultado esperado: toggle funciona, nunca há exclusão física.
Resultado encontrado —

---

## Bloco 3 — Ata

**Teste 10 — Criar uma Ata deixando o campo "numero" em branco**
Resultado esperado: gerado automaticamente no formato `XXX/AAAA` (3 dígitos), sequencial dentro do ano da `data` informada, por `tipo` (Ordinária/Extraordinária contam separado).
Resultado encontrado —

**Teste 11 — Criar duas Atas com o mesmo número, mas tipos diferentes (uma Ordinária, uma Extraordinária)**
Resultado esperado: permitido — a unicidade é por `(numero, tipo)`, não `numero` sozinho.
Resultado encontrado —

**Teste 12 — Criar Ata de Conselho de Ensino e vincular uma Pessoa (Discente ativo) a ela**
Resultado esperado: botão "+ Vincular Pessoa" aparece só para Ata de finalidade Orientação/Conselho de Ensino/Outro; dropdown mostra só Discente ativo.
Resultado encontrado —

**Teste 13 ⏳ — A Ata do Teste 12 aparece no Sumário Histórico de Vínculos da Pessoa vinculada?**
Resultado esperado: **a confirmar** — hoje a consulta do Sumário só olha `MatriculaTurma`, não `AtaPessoa`. Se este teste mostrar que deveria aparecer, é um gap a corrigir.
Resultado encontrado —

---

## Bloco 4 — Oferta de Módulo / Turma — Planejamento

**Teste 14 🔴 — Criar Turma com sigla já usada na mesma Oferta de Módulo**
Resultado esperado: mensagem "Já existe uma turma cadastrada com esta sigla, nesta Oferta de Módulo" — sem tela de debug.
Resultado encontrado —

**Teste 15 — Adicionar aluno a uma Turma Planejada, informando Código de Matrícula ANAC**
Resultado esperado: aluno aparece na lista, sem número (Nr) ainda.
Resultado encontrado —

**Teste 16 🔴 — Adicionar aluno com um Código de Matrícula ANAC já usado por outra Pessoa**
Resultado esperado: mensagem "Código de Matrícula ANAC 'X' já está em uso." — sem tela de debug.
Resultado encontrado —

**Teste 17 — Editar/Excluir aluno enquanto a Turma está Planejada**
Resultado esperado: os dois funcionam livremente (CRUD completo) só nesta fase.
Resultado encontrado —

**Teste 18 — Finalizar Planejamento de uma Turma com 3+ alunos**
Resultado esperado: pede Data de Início + Ata de Início; atribui número (Nr) em ordem alfabética por nome; Turma vira "Em Andamento"; botão Excluir some da lista.
Resultado encontrado —

**Teste 19 — Tentar excluir um aluno depois da Turma virar Em Andamento**
Resultado esperado: bloqueado (sem botão Excluir visível; se acessado direto por URL, deve dar mensagem clara, não 404 técnico).
Resultado encontrado —

---

## Bloco 5 — Turma — Em Andamento

**Teste 20 🔴 — Relocar um aluno para uma Turma ainda Planejada ou já Encerrada**
Resultado esperado: essas Turmas não devem aparecer no dropdown de destino — só Turmas Em Andamento.
Resultado encontrado —

**Teste 21 🔴 — Relocar um aluno informando uma data específica no campo "Data de Fim"**
Resultado esperado: a data informada deve ser usada nos dois eventos (saída da origem, entrada no destino) — não a data de hoje.
Resultado encontrado —

**Teste 22 — Confirmar que a Relocação nunca pede Ata**
Resultado esperado: campo Ata nunca aparece/nunca é exigido nesse fluxo — comportamento correto por desenho.
Resultado encontrado —

**Teste 23 — Marcar aluno como Reprovado, numa Turma de Módulo Básico**
Resultado esperado: pede Data de Fim + Ata de Encerramento (obrigatórios); fecha o vínculo institucional (`AtribuicaoFuncao` vira Inativo) — mesmo sendo Básico, porque é encerramento individual, não fim de ano.
Resultado encontrado —

**Teste 24 — Marcar aluno como Transferido, sem informar o Motivo (Abandonou/Solicitou)**
Resultado esperado: bloqueado, exige o motivo.
Resultado encontrado —

**Teste 25 — Marcar aluno como Matrícula Excluída**
Resultado esperado: funciona sem pedir Motivo de Saída (esse campo é só para Transferido).
Resultado encontrado —

**Teste 26 — Adicionar um novo aluno numa Turma já Em Andamento (não por relocação)**
Resultado esperado: entra no fim da lista (número = último + 1), sem exigir Ata (essa já foi definida no Finalizar Planejamento).
Resultado encontrado —

---

## Bloco 6 — Turma — Encerramento

**Teste 27 — Clicar em "Encerrar Turma" com algum aluno ainda Cursando**
Resultado esperado: abre a tela de revisão (checkbox "Aprovar" por aluno, marcado por padrão) — não encerra a Turma ainda.
Resultado encontrado —

**Teste 28 — Desmarcar um aluno na revisão antes de confirmar**
Resultado esperado: esse aluno continua Cursando; os outros viram Aprovado.
Resultado encontrado —

**Teste 29 🔴🔴 — Tentar encerrar a Turma de vez enquanto ainda sobra alguém Cursando**
Resultado esperado: **bloqueado** — o 2º clique de "Encerrar Turma" não deve estar disponível/funcionar enquanto houver `Cursando`. **Este é o teste mais importante da lista** — se falhar de novo, anотar exatamente os passos e telas usadas (inclusive se foi pelo Django Admin).
Resultado encontrado —

**Teste 30 — Encerrar uma Turma de Módulo Básico (sem ninguém Cursando)**
Resultado esperado: pede só Data de Encerramento (sem Ata); alunos Aprovados ficam "Aguardando Turma" — vínculo institucional continua Ativo.
Resultado encontrado —

**Teste 31 — Encerrar uma Turma de Módulo Especializado**
Resultado esperado: pede Data de Encerramento **e** Ata de Encerramento (obrigatória); alunos Aprovados têm o vínculo fechado (Inativo).
Resultado encontrado —

**Teste 32 — Encerrar uma Turma Extracurricular, com um aluno que também cursa uma Turma regular ao mesmo tempo**
Resultado esperado: o vínculo **não** fecha para esse aluno (ele continua Ativo, por causa da Turma regular acumulada) — mas fecha normalmente para quem só tinha o Extracurricular.
Resultado encontrado —

**Teste 33 🔴 — Tentar "+ Adicionar Aluno" numa Turma já Encerrada**
Resultado esperado: bloqueado com mensagem clara na interface (não uma página 404 técnica).
Resultado encontrado —

---

## Bloco 7 — Sumário Histórico de Vínculos

**Teste 34 🔴 — Ver o Sumário de um aluno recém-cadastrado, sem nenhuma Turma ainda**
Resultado esperado: aparece uma linha "Aguardando Atribuição" — mesmo que ele já tenha sido adicionado a uma Turma ainda Planejada (sem Finalizar Planejamento ainda).
Resultado encontrado —

**Teste 35 🔴 — Ver o Sumário depois de: Início na Turma X → Relocação para Y → Aprovação em Y**
Resultado esperado: **4 linhas separadas** — "Início na turma" (X), "Relocação - saída" (X), "Relocação - entrada" (Y), "Conclusão da turma" (Y) — cada uma com sua própria data.
Resultado encontrado —

**Teste 36 — Confirmar que a coluna "Situação" só muda na última linha**
Resultado esperado: todas as linhas de um vínculo mostram "Ativo", exceto a última — que reflete o estado atual (Ativo, se ainda em andamento; Inativo, se o vínculo já foi fechado).
Resultado encontrado —

**Teste 37 — Ver o Sumário de um Docente/Gestão sem data de fim**
Resultado esperado: 1 linha só, "Início de vínculo", situação Ativo.
Resultado encontrado —

**Teste 38 — Encerrar o vínculo de um Docente/Gestão (se a tela existir) ou verificar que ainda não existe**
Resultado esperado: **hoje não existe essa tela ainda** (item pendente no Backlog) — confirmar que essa lacuna é conhecida, não uma surpresa.
Resultado encontrado —

---

## Bloco 8 — Navegação

**Teste 39 🔴 — Navegar para "Gerenciar Alunos" de uma Turma qualquer**
Resultado esperado: o menu lateral continua aberto no grupo certo (Secretaria → Turma destacado) — não recolhe.
Resultado encontrado —

**Teste 40 — Clicar em qualquer item do menu ainda "Em Construção" (Dashboard, Treinamento, etc.)**
Resultado esperado: leva pra página genérica "Em Construção", mostrando o nome certo do módulo.
Resultado encontrado —

---

## Bloco 9 — Ambiente / Infraestrutura

**Teste 41 — Verificar o que aparece ao forçar um erro não tratado (ex: URL inválida)**
Resultado esperado: **hoje**, com `DEBUG=True`, aparece a tela de debug do Django (esperado em ambiente de desenvolvimento — nunca deve rodar assim em produção). Anotar só para lembrete futuro, não é bug a corrigir agora.
Resultado encontrado —

**Teste 42 — Testar a API de CEP com o Console do navegador aberto (F12)**
Resultado esperado: **a confirmar** — este teste já falhou uma vez sem detalhe do erro. Ao repetir, anotar qualquer mensagem de erro que aparecer no Console, e se a falha é sempre ou só às vezes.
Resultado encontrado —

---

## Observações gerais para preencher ao final

- Data em que os testes foram executados:
- Máquina/ambiente utilizado:
- Testes que falharam, com passos exatos de reprodução (tela por tela, valores digitados):
- Sugestões de teste que não estavam nesta lista:
