/**
 * cadastros/static/cadastros/js/form-dinamico.js
 *
 * Duas responsabilidades (Etapa 7.4d):
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
 */
document.addEventListener('DOMContentLoaded', function () {

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
                alert('Preencha pelo menos o campo "' + nomeLabel + '" antes de adicionar.');
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

            // Bug conhecido de navegador: cloneNode() NÃO preserva a opção
            // selecionada de um <select> — o clone sempre volta para a opção
            // padrão do HTML, mesmo que o usuário tenha escolhido outra na
            // tela. Corrigido copiando manualmente o .value de cada <select>
            // original para o <select> correspondente no clone, na mesma
            // ordem em que aparecem no DOM (querySelectorAll é determinístico
            // aqui porque o clone tem exatamente a mesma estrutura).
            // Descoberto em teste manual em 31/08/2026 — afetava Pendência
            // (campo 'tipo'), Formação (campo 'tipo_formacao') e, por
            // extensão, Histórico de Vínculo Formal (campo 'vinculo_formal').
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
});
