/**
 * cadastros/static/cadastros/js/form-dinamico.js
 *
 * Quatro responsabilidades (Etapa 7.4d):
 *  1. Mostrar/esconder QUALQUER elemento com o atributo `data-categoria`, em
 *     qualquer nível de aninhamento, comparando com a categoria da Funcao
 *     escolhida no dropdown. `data-categoria` aceita uma ou mais categorias
 *     separadas por vírgula (ex: "DOCENTE,GESTAO" para o bloco de Vínculo
 *     Formal, que se aplica às duas categorias). Elementos sem esse atributo
 *     nunca são tocados — ficam sempre visíveis, por definição.
 *  2. "Adicionar linha" nos Formsets (Formacao, Experiencia, Historico,
 *     Pendencia): le os valores do "formulario-modelo" visivel, adiciona uma
 *     linha na tabela-resumo, guarda o formulario preenchido (oculto) para
 *     ser enviado no POST, e reindexa o formulario visivel para a proxima
 *     entrada, em branco.
 *  3. Mensagens de aviso (campo obrigatorio faltando) via um popup proprio,
 *     centralizado na tela, com botao "OK" -- em vez de alert() nativo do
 *     navegador (que sempre mostra a origem da pagina, "127.0.0.1:8000
 *     diz", e nao pode ser estilizado) e sem depender de um temporizador
 *     (o usuario fecha quando quiser, lendo com calma).
 *  4. Botao "Editar" (desabilitado de proposito) ao lado de cada "+
 *     Adicionar" no cadastro inicial -- editar uma linha ja adicionada ao
 *     Formset exigiria reconstruir o formulario a partir da tabela-resumo
 *     (nao trivial com cloneNode(), ver docs/21), entao por enquanto o botao
 *     so avisa que a edicao de verdade acontece depois, na tela de
 *     Requisitos do Docente (ja implementada para Formacao, ver
 *     modal-formacao.js) -- evita frustrar quem tenta clicar em "Editar"
 *     esperando algo que ainda nao existe.
 */
document.addEventListener('DOMContentLoaded', function () {

    // ---------- 0. Popup de aviso centralizado (substitui alert()) ----------

    function mostrarToast(mensagem) {
        var popupAnterior = document.getElementById('popup-formset');
        if (popupAnterior) {
            popupAnterior.remove();
        }

        var overlay = document.createElement('div');
        overlay.id = 'popup-formset';
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.4)';
        overlay.style.zIndex = '9999';
        overlay.style.display = 'flex';
        overlay.style.alignItems = 'center';
        overlay.style.justifyContent = 'center';

        var caixa = document.createElement('div');
        caixa.style.backgroundColor = '#ffffff';
        caixa.style.color = '#333333';
        caixa.style.padding = '24px 28px';
        caixa.style.borderRadius = '8px';
        caixa.style.boxShadow = '0 8px 24px rgba(0, 0, 0, 0.35)';
        caixa.style.maxWidth = '360px';
        caixa.style.fontSize = '1rem';
        caixa.style.lineHeight = '1.5';
        caixa.style.textAlign = 'center';

        var texto = document.createElement('p');
        texto.textContent = mensagem;
        texto.style.margin = '0 0 18px 0';

        var botaoOk = document.createElement('button');
        botaoOk.type = 'button';
        botaoOk.textContent = 'OK';
        botaoOk.style.backgroundColor = '#c0392b';
        botaoOk.style.color = '#ffffff';
        botaoOk.style.border = 'none';
        botaoOk.style.borderRadius = '6px';
        botaoOk.style.padding = '8px 24px';
        botaoOk.style.fontSize = '0.95rem';
        botaoOk.style.cursor = 'pointer';

        function fecharPopup() {
            overlay.remove();
        }

        botaoOk.addEventListener('click', fecharPopup);
        overlay.addEventListener('click', function (evento) {
            if (evento.target === overlay) fecharPopup();
        });

        caixa.appendChild(texto);
        caixa.appendChild(botaoOk);
        overlay.appendChild(caixa);
        document.body.appendChild(overlay);
        botaoOk.focus();
    }

    // ---------- 1. Mostrar/esconder por categoria (generalizado) ----------

    var categoriasDataEl = document.getElementById('funcao-categorias-data');
    var categoriasPorFuncao = categoriasDataEl ? JSON.parse(categoriasDataEl.textContent) : {};
    var selectFuncao = document.getElementById('id_funcao');

    function atualizarBlocosPorCategoria() {
        if (!selectFuncao) return;
        var categoriaAtual = categoriasPorFuncao[selectFuncao.value] || null;

        document.querySelectorAll('[data-categoria]').forEach(function (elemento) {
            var categoriasPermitidas = elemento.dataset.categoria
                .split(',')
                .map(function (c) { return c.trim(); });
            var deveMostrar = categoriaAtual !== null && categoriasPermitidas.indexOf(categoriaAtual) !== -1;
            elemento.style.display = deveMostrar ? '' : 'none';
        });
    }

    if (selectFuncao) {
        selectFuncao.addEventListener('change', atualizarBlocosPorCategoria);
        atualizarBlocosPorCategoria();
    }

    // ---------- 2. Formsets dinamicos: Adicionar linha ----------

    function initFormsetDinamico(bloco) {
        var prefix = bloco.dataset.prefix;
        var campos = bloco.dataset.fields.split(',');
        var labels = bloco.dataset.labels.split(',');
        var campoObrigatorio = bloco.dataset.required;

        var obrigatoriosCompletos = bloco.dataset.obrigatoriosCompletos
            ? bloco.dataset.obrigatoriosCompletos.split(',')
            : [campoObrigatorio];

        var totalFormsInput = document.getElementById('id_' + prefix + '-TOTAL_FORMS');
        var templateArea = bloco.querySelector('.formset-template');
        var hiddenArea = bloco.querySelector('.formset-hidden');
        var tabelaBody = bloco.querySelector('table tbody');
        var botaoAdicionar = bloco.querySelector('.btn-adicionar');

        function idDoCampo(indice, campo) {
            return 'id_' + prefix + '-' + indice + '-' + campo;
        }

        botaoAdicionar.addEventListener('click', function (evento) {
            evento.preventDefault();

            var indiceAtual = parseInt(totalFormsInput.value, 10) - 1;
            var inputObrigatorio = document.getElementById(idDoCampo(indiceAtual, campoObrigatorio));

            if (!inputObrigatorio || !inputObrigatorio.value) {
                var indicePosicaoLabel = campos.indexOf(campoObrigatorio);
                var nomeLabel = labels[indicePosicaoLabel] || campoObrigatorio;
                mostrarToast('Preencha pelo menos o campo "' + nomeLabel + '" antes de adicionar.');
                return;
            }

            var camposFaltando = [];
            obrigatoriosCompletos.forEach(function (campo) {
                var input = document.getElementById(idDoCampo(indiceAtual, campo));
                if (!input || !input.value) {
                    var indicePosicao = campos.indexOf(campo);
                    camposFaltando.push(labels[indicePosicao] || campo);
                }
            });
            if (camposFaltando.length > 0) {
                mostrarToast('Preencha também: ' + camposFaltando.join(', ') + '.');
                return;
            }

            var linha = document.createElement('tr');
            campos.forEach(function (campo) {
                var input = document.getElementById(idDoCampo(indiceAtual, campo));
                var celula = document.createElement('td');
                if (input && input.tagName === 'SELECT') {
                    var opcaoSelecionada = input.options[input.selectedIndex];
                    celula.textContent = opcaoSelecionada ? opcaoSelecionada.text : '';
                } else {
                    celula.textContent = input ? input.value : '';
                }
                linha.appendChild(celula);
            });
            tabelaBody.appendChild(linha);

            var clone = templateArea.cloneNode(true);

            var selectsOriginais = templateArea.querySelectorAll('select');
            var selectsClone = clone.querySelectorAll('select');
            selectsOriginais.forEach(function (selectOriginal, indice) {
                selectsClone[indice].value = selectOriginal.value;
            });

            clone.style.display = 'none';
            hiddenArea.appendChild(clone);

            var novoIndice = indiceAtual + 1;
            var elementosParaRenomear = templateArea.querySelectorAll('input, select, label');
            elementosParaRenomear.forEach(function (elemento) {
                ['name', 'id', 'for'].forEach(function (atributo) {
                    if (elemento.hasAttribute(atributo)) {
                        var valorAtual = elemento.getAttribute(atributo);
                        var valorNovo = valorAtual.replace(
                            prefix + '-' + indiceAtual + '-',
                            prefix + '-' + novoIndice + '-'
                        );
                        elemento.setAttribute(atributo, valorNovo);
                    }
                });
            });
            templateArea.querySelectorAll('input[type=text], input[type=number], input[type=date]').forEach(function (el) {
                el.value = '';
            });
            templateArea.querySelectorAll('select').forEach(function (el) {
                el.selectedIndex = 0;
            });

            totalFormsInput.value = novoIndice + 1;
        });
    }

    document.querySelectorAll('.formset-bloco').forEach(initFormsetDinamico);

    // ---------- 4. Botão "Editar" desabilitado (aviso) ao lado de "+ Adicionar" ----------

    document.querySelectorAll('.btn-adicionar').forEach(function (botaoAdicionar) {
        var botaoEditar = document.createElement('button');
        botaoEditar.type = 'button';
        botaoEditar.textContent = 'Editar';
        botaoEditar.className = 'btn-adicionar';
        botaoEditar.style.marginLeft = '8px';
        botaoEditar.addEventListener('click', function (evento) {
            evento.preventDefault();
            mostrarToast(
                'A edição só é possível depois que o cadastro desta Função for finalizado. ' +
                'Salve o cadastro e edite pela tela de detalhe/Requisitos do Docente.'
            );
        });
        botaoAdicionar.insertAdjacentElement('afterend', botaoEditar);
    });
});

