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
    var caixa = document.getElementById('modal-crud-caixa');
    var status = document.getElementById('modal-crud-status');
    var botaoFechar = document.getElementById('modal-crud-fechar');
    var gatilhoModal = null;
    var chaveFoco = 'modal-crud-foco-retorno';
    var fundoInativo = [];
    var aberturaAtual = 0;
    botaoFechar.setAttribute('aria-label', 'Fechar formulário');

    function estaDisponivel(elemento) {
        return !elemento.matches(':disabled') && elemento.tabIndex >= 0 &&
            !elemento.closest('[inert]') && elemento.getClientRects().length > 0 &&
            window.getComputedStyle(elemento).visibility === 'visible';
    }

    function controlesDoModal() {
        return Array.from(caixa.querySelectorAll('a[href], button, input:not([type="hidden"]), select, textarea, [tabindex], [contenteditable="true"]')).filter(estaDisponivel);
    }

    function bloquearFundo() {
        if (fundoInativo.length) return;
        // Mantém o caminho até o modal ativo e bloqueia os ramos ao redor.
        var ramo = overlay;
        while (ramo && ramo !== document.body) {
            var pai = ramo.parentElement;
            if (!pai) break;
            Array.from(pai.children).forEach(function (elemento) {
                if (elemento === ramo || /^(SCRIPT|STYLE|LINK)$/.test(elemento.tagName)) return;
                fundoInativo.push({ elemento: elemento, anterior: elemento.inert });
                elemento.inert = true;
            });
            ramo = pai;
        }
    }

    function liberarFundo() {
        fundoInativo.forEach(function (item) {
            item.elemento.inert = item.anterior;
        });
        fundoInativo = [];
    }

    function anunciarCarregamento(mensagem) {
        corpo.setAttribute('aria-busy', mensagem ? 'true' : 'false');
        status.textContent = mensagem;
    }

    function atualizarNomeDoDialogo() {
        var titulo = corpo.querySelector('h1, h2, h3, h4, h5, h6');
        if (!titulo) return;
        if (!titulo.id) titulo.id = 'modal-crud-titulo';
        caixa.setAttribute('aria-labelledby', titulo.id);
        caixa.removeAttribute('aria-label');
    }

    function botoesComUrl(url) {
        return Array.from(document.querySelectorAll('.btn-abrir-modal-crud')).filter(function (botao) {
            return botao.dataset.url === url;
        });
    }

    function guardarFocoParaRecarga() {
        if (!gatilhoModal) return;
        try {
            window.sessionStorage.setItem(chaveFoco, JSON.stringify({
                pagina: window.location.pathname + window.location.search,
                url: gatilhoModal.dataset.url,
                indice: botoesComUrl(gatilhoModal.dataset.url).indexOf(gatilhoModal),
            }));
        } catch (erro) {
            // Armazenamento indisponível não deve impedir o salvamento.
        }
    }

    function restaurarFocoAposRecarga() {
        try {
            var registro = window.sessionStorage.getItem(chaveFoco);
            window.sessionStorage.removeItem(chaveFoco);
            if (!registro) return;
            var retorno = JSON.parse(registro);
            if (retorno.pagina !== window.location.pathname + window.location.search) return;
            var botao = botoesComUrl(retorno.url)[retorno.indice];
            if (botao && !botao.disabled) botao.focus();
        } catch (erro) {
            // Registro inválido ou bloqueado: mantém a navegação normal.
        }
    }

    function focarFormulario() {
        atualizarNomeDoDialogo();
        // Prefere o primeiro erro, mesmo quando há campos válidos antes dele.
        var campo = Array.from(corpo.querySelectorAll('[aria-invalid="true"]')).find(estaDisponivel) ||
            Array.from(corpo.querySelectorAll('input:not([type="hidden"]), select, textarea')).find(estaDisponivel);
        (campo || botaoFechar).focus();
    }

    function lerResposta(resposta) {
        if (!resposta.ok) throw new Error('Falha na resposta do servidor.');
        return resposta.text();
    }

    function criarMensagem(mensagem) {
        var erro = document.createElement('div');
        erro.className = 'erro';
        erro.setAttribute('role', 'alert');
        erro.tabIndex = -1;
        var icone = document.createElement('span');
        icone.className = 'icone-erro';
        icone.setAttribute('aria-hidden', 'true');
        icone.textContent = '⚠️';
        var texto = document.createElement('div');
        texto.className = 'mensagem-erro-conteudo';
        texto.textContent = mensagem;
        erro.appendChild(icone);
        erro.appendChild(texto);
        return erro;
    }

    function mostrarErro(mensagem) {
        var erro = criarMensagem(mensagem);
        corpo.prepend(erro);
        erro.focus();
    }

    function iniciarModal(gatilho) {
        var abertura = ++aberturaAtual;
        gatilhoModal = gatilho;
        caixa.removeAttribute('aria-labelledby');
        caixa.removeAttribute('aria-describedby');
        caixa.setAttribute('aria-label', gatilho.getAttribute('aria-label') || gatilho.textContent.trim() || 'Formulário');
        corpo.textContent = '';
        overlay.style.display = 'flex';
        botaoFechar.focus();
        bloquearFundo();
        anunciarCarregamento('');
        return abertura;
    }

    function abrirModal(url, gatilho) {
        var abertura = iniciarModal(gatilho);
        corpo.textContent = 'Carregando...';
        anunciarCarregamento('Carregando formulário.');

        var separador = url.indexOf('?') === -1 ? '?' : '&';
        fetch(url + separador + 'parcial=1')
            .then(lerResposta)
            .then(function (html) {
                if (overlay.style.display === 'none' || abertura !== aberturaAtual) return;
                anunciarCarregamento('');
                corpo.innerHTML = html;
                focarFormulario();
            })
            .catch(function () {
                if (overlay.style.display === 'none' || abertura !== aberturaAtual) return;
                anunciarCarregamento('');
                corpo.textContent = '';
                mostrarErro('Não foi possível carregar o formulário. Feche e tente novamente.');
            });
    }

    function fecharModal() {
        aberturaAtual++;
        overlay.style.display = 'none';
        corpo.innerHTML = '';
        anunciarCarregamento('');
        liberarFundo();
        if (gatilhoModal && gatilhoModal.isConnected) gatilhoModal.focus();
    }

    document.querySelectorAll('.btn-abrir-modal-crud').forEach(function (botao) {
        botao.addEventListener('click', function () {
            abrirModal(botao.dataset.url, botao);
        });
    });

    document.addEventListener('modal-crud-aviso', function (evento) {
        if (!evento.detail || !evento.detail.mensagem) return;
        evento.preventDefault();
        iniciarModal(evento.detail.gatilho || document.activeElement);
        var titulo = document.createElement('h3');
        titulo.id = 'modal-crud-titulo';
        titulo.textContent = 'Aviso';
        corpo.appendChild(titulo);
        var mensagem = criarMensagem(evento.detail.mensagem);
        mensagem.id = 'modal-crud-aviso-texto';
        corpo.appendChild(mensagem);
        caixa.setAttribute('aria-describedby', mensagem.id);
        var ok = document.createElement('button');
        ok.type = 'button';
        ok.className = 'btn-salvar';
        ok.textContent = 'OK';
        ok.addEventListener('click', fecharModal);
        corpo.appendChild(ok);
        atualizarNomeDoDialogo();
        ok.focus();
    });

    botaoFechar.addEventListener('click', fecharModal);
    corpo.addEventListener('click', function (evento) {
        if (evento.target.closest('[data-fechar-modal-crud], #modal-crud-cancelar-btn, #modal-cancelar-planejamento')) {
            evento.preventDefault();
            fecharModal();
        }
    });
    overlay.addEventListener('click', function (evento) {
        if (evento.target === overlay) fecharModal();
    });
    document.addEventListener('keydown', function (evento) {
        if (overlay.style.display === 'none') return;
        if (evento.key === 'Escape') {
            evento.preventDefault();
            fecharModal();
        } else if (evento.key === 'Tab') {
            var controles = controlesDoModal();
            var primeiro = controles[0];
            var ultimo = controles[controles.length - 1];
            var atual = document.activeElement;
            if (!primeiro) {
                evento.preventDefault();
                caixa.focus();
            } else if (evento.shiftKey && (atual === primeiro || controles.indexOf(atual) === -1)) {
                evento.preventDefault();
                ultimo.focus();
            } else if (!evento.shiftKey && (atual === ultimo || controles.indexOf(atual) === -1)) {
                evento.preventDefault();
                primeiro.focus();
            }
        }
    });
    document.addEventListener('focusin', function (evento) {
        if (overlay.style.display !== 'none' && !caixa.contains(evento.target)) {
            focarFormulario();
        }
    });
    restaurarFocoAposRecarga();

    // O <form> só existe depois do fetch acima, então o listener de submit
    // fica no contêiner que sempre existe (delegação de evento).
    corpo.addEventListener('submit', function (evento) {
        var form = evento.target;
        if (!form.classList.contains('form-modal-crud')) return;
        evento.preventDefault();
        var abertura = aberturaAtual;
        anunciarCarregamento('Salvando formulário.');

        fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
        })
            .then(lerResposta)
            .then(function (texto) {
                if (overlay.style.display === 'none' || abertura !== aberturaAtual) return;
                anunciarCarregamento('');
                try {
                    var dados = JSON.parse(texto);
                    if (dados.sucesso) {
                        guardarFocoParaRecarga();
                        window.location.reload();
                        return;
                    }
                } catch (erro) {
                    // Não veio JSON -- o formulário voltou com erros de
                    // validação (HTML re-renderizado pelo Django). Mostra
                    // o HTML novo no lugar do formulário antigo, sem fechar
                    // o modal, para o usuário corrigir sem perder o contexto.
                    corpo.innerHTML = texto;
                    focarFormulario();
                }
            })
            .catch(function () {
                if (overlay.style.display === 'none' || abertura !== aberturaAtual) return;
                anunciarCarregamento('');
                mostrarErro('Não foi possível confirmar o salvamento devido a uma falha na comunicação ou no servidor. Os dados preenchidos continuam no formulário. Tente novamente ou feche a janela para cancelar.');
            });
    });
});
