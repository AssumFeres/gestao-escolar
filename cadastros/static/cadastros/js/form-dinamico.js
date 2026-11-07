/**
 * cadastros/static/cadastros/js/form-dinamico.js
 *
 * Responsabilidades (Etapa 7.4d + ajustes posteriores):
 *  1. Mostrar/esconder QUALQUER elemento com o atributo `data-categoria`.
 *  2. "Adicionar linha" nos Formsets (Formacao, Experiencia, Historico, Pendencia).
 *  3. Popup proprio de aviso (substitui alert() nativo do navegador).
 *  4. Botao "Editar" (desabilitado de proposito) ao lado de cada "+ Adicionar".
 *  5. Data de Nascimento: valida no cliente (feedback imediato, a validacao
 *     de verdade e no backend, forms.py::clean_data_nascimento) duas coisas
 *     diferentes:
 *     a) Data igual a hoje ou no futuro -- sempre invalida (ninguem nasce no
 *        futuro), aviso de ERRO.
 *     b) Idade calculada menor que 18 anos -- aviso informativo, NAO
 *        bloqueia o cadastro (esperado para Discente; para Docente/Gestao
 *        e uma situacao estranha mas a decisao de 02/09/2026 foi so avisar).
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
        botaoEditar.className = 'btn-adicionar';
        botaoEditar.style.marginLeft = '8px';
        botaoEditar.textContent = 'Editar';
        botaoEditar.addEventListener('click', function (evento) {
            evento.preventDefault();
            mostrarToast(
                'A edição só é possível depois que o cadastro desta Função for finalizado. ' +
                'Salve o cadastro e edite pela tela de detalhe/Requisitos do Docente.'
            );
        });
        botaoAdicionar.insertAdjacentElement('afterend', botaoEditar);
    });

    // ---------- 5. Data de Nascimento: futura (erro) + menor de idade (aviso) ----------

    var campoDataNascimento = document.getElementById('id_data_nascimento');
    if (campoDataNascimento) {
        campoDataNascimento.addEventListener('change', function () {
            if (!campoDataNascimento.value) return;

            var partes = campoDataNascimento.value.split('-');
            var nascimento = new Date(
                parseInt(partes[0], 10), parseInt(partes[1], 10) - 1, parseInt(partes[2], 10)
            );
            var agora = new Date();
            var hojeSemHora = new Date(agora.getFullYear(), agora.getMonth(), agora.getDate());

            // a) Data igual a hoje ou no futuro -- sempre invalida.
            if (nascimento >= hojeSemHora) {
                mostrarToast('Data de nascimento inválida: não pode ser hoje nem uma data futura.');
                return;
            }

            // b) Idade menor que 18 anos -- so aviso, nao bloqueia.
            var idade = agora.getFullYear() - nascimento.getFullYear();
            var aniversarioJaFezEsteAno = (
                agora.getMonth() > nascimento.getMonth() ||
                (agora.getMonth() === nascimento.getMonth() && agora.getDate() >= nascimento.getDate())
            );
            if (!aniversarioJaFezEsteAno) {
                idade -= 1;
            }

            if (idade < 18) {
                mostrarToast(
                    'Atenção: com essa Data de Nascimento, a pessoa tem ' + idade + ' ano(s) ' +
                    '(menor de idade). Para Discente isso é esperado (preencha o Responsável Legal). ' +
                    'Para Docente ou Gestão, confira se a data está correta antes de salvar.'
                );
            }
        });
    }
});
