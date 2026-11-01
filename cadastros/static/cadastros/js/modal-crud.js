/**
 * cadastros/static/cadastros/js/modal-crud.js
 *
 * Popup/modal genérico para o CRUD independente (piloto docs/21) — carrega
 * o formulário via fetch() (a View responde com um fragmento HTML quando a
 * URL tem ?parcial=1, ver ModalCrudMixin em views.py), intercepta o submit
 * do formulário injetado e envia via fetch também, recebendo JSON de volta
 * no sucesso.
 *
 * Substitui modal-formacao.js (agora genérico, não mais específico de
 * Formação) — usado em qualquer página com um contêiner #modal-crud-overlay
 * e botões .btn-abrir-modal-crud (data-url apontando para a View certa).
 * O formulário injetado precisa da classe .form-modal-crud para o listener
 * de submit reconhecê-lo.
 */
document.addEventListener('DOMContentLoaded', function () {
    var overlay = document.getElementById('modal-crud-overlay');
    if (!overlay) return;

    var corpo = document.getElementById('modal-crud-corpo');
    var botaoFechar = document.getElementById('modal-crud-fechar');

    function abrirModal(url) {
        corpo.textContent = 'Carregando...';
        overlay.style.display = 'flex';

        var separador = url.indexOf('?') === -1 ? '?' : '&';
        fetch(url + separador + 'parcial=1')
            .then(function (resposta) { return resposta.text(); })
            .then(function (html) {
                corpo.innerHTML = html;
            })
            .catch(function () {
                corpo.textContent = 'Não foi possível carregar o formulário.';
            });
    }

    function fecharModal() {
        overlay.style.display = 'none';
        corpo.innerHTML = '';
    }

    document.querySelectorAll('.btn-abrir-modal-crud').forEach(function (botao) {
        botao.addEventListener('click', function () {
            abrirModal(botao.dataset.url);
        });
    });

    botaoFechar.addEventListener('click', fecharModal);
    overlay.addEventListener('click', function (evento) {
        if (evento.target === overlay) fecharModal();
    });

    // O <form> só existe depois do fetch acima, então o listener de submit
    // fica no contêiner que sempre existe (delegação de evento).
    corpo.addEventListener('submit', function (evento) {
        var form = evento.target;
        if (!form.classList.contains('form-modal-crud')) return;
        evento.preventDefault();

        fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
        })
            .then(function (resposta) { return resposta.text(); })
            .then(function (texto) {
                try {
                    var dados = JSON.parse(texto);
                    if (dados.sucesso) {
                        window.location.reload();
                        return;
                    }
                } catch (erro) {
                    // Não veio JSON -- o formulário voltou com erros de
                    // validação (HTML re-renderizado pelo Django). Mostra
                    // o HTML novo no lugar do formulário antigo, sem fechar
                    // o modal, para o usuário corrigir sem perder o contexto.
                    corpo.innerHTML = texto;
                }
            })
            .catch(function () {
                corpo.insertAdjacentHTML('afterbegin', '<p style="color:#c0392b;">Erro ao salvar. Tente novamente.</p>');
            });
    });
});
