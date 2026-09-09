# Plano de Testes Manuais — Sistema de Gestão Escolar EMCA

**Criado em:** 08/09/2026, ao final da sessão de correções do módulo Atribuição/Turma (`docs/39`).

**Como usar:** para cada teste, execute o passo a passo, compare com o **Resultado esperado** e preencha **Resultado encontrado** com o que realmente aconteceu. Sempre que houver falha, registrar os passos exatos para reprodução, os valores utilizados e, quando aplicável, a mensagem apresentada pelo sistema.

### Legenda

- 🔴 **Regressão:** bug já identificado/corrigido que deve ser retestado após alterações futuras.
- ⭐ **Regra crítica de negócio:** falha pode comprometer o fluxo ou a consistência dos dados.
- ✅ **Passou:** comportamento encontrado corresponde ao esperado.
- ❌ **Falhou:** comportamento encontrado diverge do esperado.
- ⚠️ **Parcial:** parte do comportamento funcionou, mas ainda existe alguma inconsistência.
- ⏳ **A confirmar:** regra ou comportamento ainda depende de definição/validação.

### Classificação dos testes

Nem todo comportamento diferente do "ideal futuro" deve ser tratado como bug. Neste plano:

- **Regressão/bug:** comportamento que deveria funcionar segundo regra já definida/implementada e deixou de funcionar ou está incorreto.
- **Recurso adiado:** melhoria já identificada, mas conscientemente ainda não implementada.
- **Regra a definir:** necessidade plausível que ainda depende de decisão de negócio antes de virar critério de aceitação.
- **Exploratório:** teste destinado a descobrir o comportamento atual e levantar lacunas, sem pressupor que já exista uma implementação homologada.

### Registro recomendado quando houver falha

No campo **Resultado encontrado**, registrar preferencialmente:

- Status: ✅ Passou / ❌ Falhou / ⚠️ Parcial;
- descrição objetiva do comportamento encontrado;
- dados utilizados no teste;
- tela/URL em que ocorreu;
- severidade sugerida: Crítica / Alta / Média / Baixa;
- mensagem de erro exibida, quando houver.

---

## Bloco 1 — Cadastro de Pessoa

**Teste 01 — Criar aluno novo, testar preenchimento automático de CPF e API de CEP**
Resultado esperado: ao digitar um CPF já cadastrado, os campos da Pessoa devem se preencher sozinhos. Ao digitar um CEP válido, endereço/cidade/UF devem se preencher automaticamente via API.
Resultado encontrado —
1.1 CPF PREENCHIDO - CARREGOU AS INFORMAÇÕES
1.1.1 Só funciona com o CPF - com 11 digitos - colocar máscara de entrada de dados ###.###.###-##
1.2 CEP via API - funcionou
1.2.1 - A entrada deve ser somente números - colocar máscara de entrada de dados ##.###-###
Observação:
Alteração realizado no form_pessoa.html - trazendo o campo Função como sendo primeiro a ser preenchido de forma a configurar o form para aquela função

**Teste 01.a - editar pessoa cadastrada**
Resultado esperado: Salvar a edição e popup estar visível na tela.
Resultado encontrado:
01.a.1 Salvou as alterações do cadastro - manteve sem edição o nº do CPF
01.a.2 Popup maior que o monitor - escondeu o botão salvar - Realizei ajuste no CSS base.css e no \_form_pessoa_fragment.html (solicitar para te manter atualizado com os arquivos)
observação:
git commit -m "feat: ajusta popup de edição de pessoa com 4 colunas e rolagem"
commit a5495014476cd2ec02c2955ee0197c1a1164552e (HEAD -> dev, origin/dev)
Author: AssumFeres <107887188+AssumFeres@users.noreply.github.com>
Date: Tue Sep 8 20:16:19 2026 -0300

    feat: ajusta popup de edição de pessoa com 4 colunas e rolagem

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

## Bloco 10 — Validação e Normalização de Dados

**Teste 43 — Tentar salvar cadastros deixando campos obrigatórios em branco**  
Executar o teste em Pessoa, Disciplina, SubModulo, Módulo, Turma e Ata, conforme os campos obrigatórios existentes em cada cadastro.  
Resultado esperado: o registro não deve ser salvo; os campos inválidos devem ser indicados de forma clara na própria interface, sem tela de debug.  
Resultado encontrado —

**Teste 44 ⏳ — Cadastrar Nome/Sigla com espaços antes e depois do conteúdo — RECURSO ADIADO**  
Exemplo: `  MAVIT  `.  
Situação atual: a normalização automática de espaços ainda não foi implementada por decisão de prioridade.  
Resultado esperado hoje: **não classificar como bug caso o sistema preserve os espaços**. Este teste fica registrado para futura implementação da normalização.  
Resultado encontrado —

**Teste 45 ⏳ — Testar diferença entre maiúsculas e minúsculas em Nome/Sigla — RECURSO ADIADO**  
Exemplo: cadastrar `mavit` e depois tentar cadastrar `MAVIT`.  
Situação atual: a conversão automática para maiúsculas e a normalização de caixa ainda não foram implementadas por decisão de prioridade.  
Resultado esperado hoje: **não classificar como bug caso o sistema ainda diferencie ou preserve a caixa digitada**. Este teste fica registrado para futura implementação.  
Resultado encontrado —

**Teste 46 ⭐ — Testar Código de Matrícula ANAC no formato real fornecido pelo S141**  
Testar, por exemplo: `239.MAVIT.25.00062`, `239.MCELT.25.00001` e `239.MGMP.26.00125`.  
Resultado esperado: o valor deve ser aceito e armazenado como texto, exatamente no formato informado; o sistema não deve tentar convertê-lo para número.  
Resultado encontrado —

---

## Bloco 11 — Consistência de Datas

> **Observação:** os Testes 47, 48 e 49 representam regras de negócio ainda não decididas nem implementadas. Eles não devem ser tratados como falha/regressão até que a regra seja formalmente definida.

**Teste 47 ⏳ — Data de Encerramento anterior à Data de Início da Turma — REGRA A DEFINIR**  
Pergunta de negócio: o sistema deverá sempre bloquear uma Data de Encerramento anterior à Data de Início?  
Situação atual: essa validação específica ainda não foi definida/implementada.  
Resultado esperado hoje: **não classificar como bug**; registrar apenas o comportamento encontrado para futura decisão.  
Resultado encontrado —

**Teste 48 ⏳ — Data de Relocação anterior ao início da participação do aluno na Turma de origem — REGRA A DEFINIR**  
Pergunta de negócio: uma relocação retroativa anterior ao início do aluno deve ser sempre proibida ou pode existir alguma exceção administrativa?  
Situação atual: a regra ainda não foi definida/implementada.  
Resultado esperado hoje: **não classificar como bug**; registrar apenas o comportamento encontrado.  
Resultado encontrado —

**Teste 49 ⏳ — Data de Aprovação/Reprovação anterior à entrada do aluno na Turma — REGRA A DEFINIR**  
Pergunta de negócio: o sistema deverá bloquear automaticamente qualquer data final anterior à entrada do aluno na Turma?  
Situação atual: a validação ainda não foi definida/implementada.  
Resultado esperado hoje: **não classificar como bug**; registrar apenas o comportamento encontrado.  
Resultado encontrado —

**Teste 50 🔴 — Informar data de evento diferente da data atual**  
Resultado esperado: o Sumário Histórico deve registrar a data informada no formulário como data efetiva do evento, e não substituir automaticamente por `today()`/data do lançamento.  
Observação: essa regra já foi identificada e corrigida no fluxo de Relocação; o teste serve para confirmar a regressão e verificar se o mesmo comportamento é respeitado nos demais status/eventos.  
Resultado encontrado —

---

## Bloco 12 — Integridade do Sumário Histórico

**Teste 51 ⭐ — Alterar dados atuais da Pessoa depois de existirem eventos históricos**  
Criar eventos no histórico e, depois, editar dados cadastrais da Pessoa.  
Resultado esperado: os eventos anteriores não devem desaparecer nem ter suas datas, Turmas, Atas, status ou tipos de evento alterados indevidamente.  
Resultado encontrado —

**Teste 52 ⭐ — Confirmar que um novo evento nunca apaga eventos anteriores**  
Executar uma sequência como: Aguardando Atribuição → Início na Turma → Relocação → Conclusão.  
Resultado esperado: cada etapa deve acrescentar um novo registro cronológico; eventos anteriores devem permanecer disponíveis para consulta.  
Resultado encontrado —

**Teste 53 — Inativar Disciplina/SubModulo/Módulo e consultar registros históricos antigos**  
Resultado esperado: o item inativado deve continuar aparecendo corretamente em registros históricos já existentes, mas deve deixar de estar disponível para novas atribuições quando a regra de negócio assim exigir.  
Resultado encontrado —

---

## Bloco 13 — Repetição de Ações / Duplo Clique

> **Observação:** nos Testes 54 a 57, o principal risco esperado hoje não é necessariamente a criação de registros duplicados. As Services já possuem validações de estado, mas algumas Views podem não capturar o `ValidationError`, fazendo a segunda requisição resultar em tela de debug/erro técnico. Portanto, registrar separadamente: **duplicou dados?** e **a interface tratou a segunda ação de forma amigável?**

**Teste 54 ⭐ — Dar duplo clique em "Finalizar Planejamento"**  
Resultado esperado: a operação deve ocorrer apenas uma vez; não pode criar eventos, numerações ou alterações duplicadas. A segunda requisição, se rejeitada pela regra de negócio, deve ser tratada sem tela de debug.  
Resultado encontrado —

**Teste 55 ⭐ — Dar duplo clique em uma ação de Relocação**  
Resultado esperado: deve existir apenas uma saída da Turma de origem e uma entrada na Turma de destino. A segunda requisição não deve exibir erro técnico cru ao usuário.  
Resultado encontrado —

**Teste 56 ⭐ — Dar duplo clique em Aprovar/Reprovar/Transferir aluno**  
Resultado esperado: deve ser gerado apenas um evento final para a operação escolhida. Se a segunda tentativa for rejeitada por estado inválido, a mensagem deve ser amigável.  
Resultado encontrado —

**Teste 57 ⭐ — Dar duplo clique em "Encerrar Turma"**  
Resultado esperado: a Turma deve ser encerrada uma única vez, sem duplicar eventos, vínculos ou alterações de status. A segunda requisição não deve resultar em tela de debug.  
Resultado encontrado —

**Teste 58 ⭐ — Dar duplo clique ao criar uma Ata**  
Resultado esperado: apenas uma Ata deve ser criada. Este caso merece atenção especial porque a numeração automática pode gerar uma segunda Ata válida se duas submissões forem processadas.  
Resultado encontrado —

---

## Bloco 14 — Concorrência Simples / Duas Abas

**Teste 59 — Abrir o mesmo registro em duas abas do navegador e editar nas duas**  
Passo sugerido: abrir uma Pessoa ou Turma em duas abas; salvar uma alteração na Aba A; depois salvar outra alteração a partir da Aba B, que ainda contém dados antigos.  
Resultado esperado: observar e registrar o comportamento do sistema. Alterações mais recentes não devem ser perdidas silenciosamente sem que o comportamento seja conhecido.  
Resultado encontrado —

---

## Bloco 15 — Acessibilidade — TESTES EXPLORATÓRIOS

> **Observação:** este bloco representa a primeira avaliação sistemática de acessibilidade das telas. Eventuais falhas devem ser registradas como **lacunas de acessibilidade a tratar**, e não como regressões de uma funcionalidade anteriormente homologada.

**Teste 60 — Navegar pelas telas principais utilizando apenas o teclado**  
Utilizar `Tab`, `Shift + Tab`, `Enter` e, quando aplicável, `Esc`.  
Resultado esperado: campos, links, botões e ações principais devem ser alcançáveis e acionáveis sem uso do mouse.  
Resultado encontrado —

**Teste 61 — Testar foco ao abrir formulários em popup/modal**  
Resultado esperado: o foco deve ir para o conteúdo do modal; a navegação por `Tab` deve permanecer lógica; o botão Cancelar/Fechar deve ser acessível pelo teclado.  
Resultado encontrado —

**Teste 62 — Verificar associação entre Label e campo de formulário**  
Resultado esperado: ao clicar no texto do label, o foco deve ir para o respectivo campo sempre que aplicável.  
Resultado encontrado —

**Teste 63 — Verificar mensagens de erro sem depender somente de cor**  
Resultado esperado: erros devem possuir texto/indicação compreensível além da mudança de cor de fundo ou borda.  
Resultado encontrado —

**Teste 64 — Testar páginas principais com zoom do navegador em 200%**  
Resultado esperado: conteúdo permanece utilizável; campos, textos, menus e botões não devem ficar inacessíveis ou sobrepostos de forma que impeça o uso.  
Resultado encontrado —

---

## Bloco 16 — Compatibilidade entre Navegadores — TESTES EXPLORATÓRIOS

> **Observação:** este bloco é exploratório. O sistema ainda não passou por uma rodada formal de testes cross-browser; diferenças encontradas devem ser registradas como compatibilidade a avaliar, não como regressão automática.

**Teste 65 — Executar o fluxo principal no Microsoft Edge**  
Testar principalmente JavaScript, menus, modais, autocomplete, API de CEP e campos de data.  
Resultado esperado: funcionamento normal.  
Resultado encontrado —

**Teste 66 — Executar o fluxo principal no Google Chrome**  
Testar principalmente JavaScript, menus, modais, autocomplete, API de CEP e campos de data.  
Resultado esperado: funcionamento normal e equivalente ao Edge.  
Resultado encontrado —

**Teste 67 — Executar o fluxo principal no Firefox, se disponível**  
Resultado esperado: as funções essenciais devem continuar utilizáveis; registrar eventuais diferenças de comportamento.  
Resultado encontrado —

---

## Bloco 17 — API de CEP / Tratamento de Falhas Externas

**Teste 68 — Informar um CEP inexistente**  
Resultado esperado: apresentar mensagem amigável de CEP não encontrado, sem quebrar o formulário.  
Resultado encontrado —

**Teste 69 — Informar um CEP incompleto ou com formato inválido**  
Resultado esperado: não executar consulta indevida; informar formato inválido ou aguardar o preenchimento completo.  
Resultado encontrado —

**Teste 70 ⭐ — Testar cadastro com a API de CEP indisponível**  
Pode ser testado temporariamente sem conexão de rede ou simulando falha da chamada externa.  
Resultado esperado: a falha da API não deve impedir o cadastro da Pessoa; o endereço deve poder ser preenchido manualmente e a mensagem apresentada deve ser amigável.  
Resultado encontrado —

---

## Bloco 18 — Persistência dos Dados

**Teste 71 ⭐ — Salvar uma alteração, sair da tela e consultar novamente**  
Executar após alterações importantes, como CANAC, Código de Matrícula ANAC, Ata, status e datas.  
Resultado esperado: os dados devem permanecer exatamente como foram gravados após recarregar a página ou voltar posteriormente ao registro.  
Resultado encontrado —

**Teste 72 ⭐ — Confirmar persistência após Relocação**  
Resultado esperado: após sair da tela e voltar, a matrícula de origem deve permanecer como Relocada, a de destino como Cursando e os dois eventos devem permanecer no Sumário Histórico.  
Resultado encontrado —

**Teste 73 ⭐ — Confirmar persistência após Encerramento/Aprovação**  
Resultado esperado: após recarregar ou retornar ao sistema, Turma, status do aluno, vínculo e histórico devem manter o estado final correto.  
Resultado encontrado —

---

## Bloco 19 — Exclusão Lógica / Itens Inativos

**Teste 74 — Inativar item de catálogo e tentar utilizá-lo em novo cadastro/vínculo**  
Aplicar a Disciplina, SubModulo e Módulo conforme a lógica existente.  
Resultado esperado: o item continua armazenado para preservar o histórico, mas não deve ser oferecido para novas operações quando estiver Inativo.  
Resultado encontrado —

**Teste 75 — Reativar item anteriormente inativado**  
Resultado esperado: o item volta a ficar disponível para novas operações sem perder seus vínculos e registros históricos anteriores.  
Resultado encontrado —

---

## Bloco 20 — Cenário Completo de Aceitação

**Teste 76 ⭐ — Executar o ciclo completo de um aluno do cadastro à conclusão**

Passo sugerido:

1. cadastrar uma nova Pessoa;
2. criar vínculo Discente;
3. informar CANAC;
4. manter Código de Matrícula ANAC inicialmente em branco;
5. verificar "Aguardando Atribuição" no Sumário Histórico;
6. adicionar o aluno a uma Turma Planejada;
7. informar Código de Matrícula ANAC no formato real do S141;
8. finalizar o planejamento com Data de Início e Ata de Início;
9. verificar "Início na turma" no histórico;
10. relocar o aluno para outra Turma Em Andamento;
11. verificar "Relocação - saída" e "Relocação - entrada";
12. definir a situação final do aluno;
13. aprovar/concluir quando aplicável;
14. encerrar a Turma conforme o tipo de Módulo;
15. sair da tela e consultar novamente o aluno;
16. conferir situação final do vínculo;
17. conferir todo o Sumário Histórico em ordem cronológica.

Resultado esperado: todo o fluxo deve funcionar sem telas de debug, sem duplicidades, sem perda de eventos anteriores e respeitando as regras de negócio de cada etapa.  
Resultado encontrado —

---

## Guia de Execução — O que rodar agora

| Bloco/Testes   | Tratamento                                                                           |
| -------------- | ------------------------------------------------------------------------------------ |
| Blocos 1 a 9   | Rodar normalmente                                                                    |
| Teste 43       | Rodar normalmente                                                                    |
| Testes 44 e 45 | ⏳ Recurso adiado — não classificar como bug                                         |
| Teste 46       | Rodar normalmente                                                                    |
| Testes 47 a 49 | ⏳ Regra de negócio a definir — não classificar como bug                             |
| Teste 50       | Rodar como regressão/consistência                                                    |
| Bloco 12       | Rodar normalmente                                                                    |
| Testes 54 a 57 | Rodar verificando tanto duplicidade quanto tratamento amigável da segunda requisição |
| Teste 58       | Rodar normalmente, com atenção para possível criação de duas Atas                    |
| Bloco 14       | Rodar normalmente                                                                    |
| Blocos 15 e 16 | Exploratórios — executar conforme disponibilidade                                    |
| Blocos 17 a 20 | Rodar normalmente                                                                    |

---

## Observações gerais para preencher ao final

- Data em que os testes foram executados:
- Máquina/ambiente utilizado:
- Navegador e versão:
- Base/banco utilizado no teste:
- Testes que falharam, com passos exatos de reprodução (tela por tela, valores digitados):
- Falhas classificadas como Crítica/Alta:
- Sugestões de teste que não estavam nesta lista:
