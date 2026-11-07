// Entrada em formulários de página completa, separada do foco dos popups.
document.addEventListener('DOMContentLoaded', function () {
    var conteudo = document.getElementById('conteudo-principal');
    if (!conteudo) return;
    var chave = 'formulario-pagina-foco';

    function guardar(destino) {
        try {
            var url = new URL(destino, window.location.href);
            if (url.origin !== window.location.origin) return;
            window.sessionStorage.setItem(chave, url.pathname + url.search);
        } catch (erro) {
            // Falha de armazenamento não deve impedir a navegação.
        }
    }

    function disponivel(controle) {
        return !controle.matches(':disabled') && controle.tabIndex >= 0 &&
            !controle.closest('[inert]') && controle.getClientRects().length > 0 &&
            window.getComputedStyle(controle).visibility === 'visible';
    }

    function formularioDePagina(form) {
        return form.method.toLowerCase() === 'post' &&
            !form.closest('#modal-crud-overlay') && !form.querySelector('input[type="password"]');
    }

    conteudo.addEventListener('click', function (evento) {
        if (evento.defaultPrevented || evento.ctrlKey || evento.metaKey || evento.shiftKey || evento.altKey) return;
        if (evento.button !== undefined && evento.button !== 0) return;
        var link = evento.target.closest('a[href]');
        if (!link || link.hasAttribute('download') || (link.target && link.target !== '_self')) return;
        if (link.closest('#modal-crud-overlay')) return;
        var destino = new URL(link.href, window.location.href);
        // Links do resumo e do salto permanecem na própria página.
        if (destino.pathname === window.location.pathname && destino.search === window.location.search) return;
        guardar(destino.href);
    });

    conteudo.addEventListener('submit', function (evento) {
        var form = evento.target;
        if (evento.defaultPrevented || !formularioDePagina(form)) return;
        if (form.target && form.target !== '_self') return;
        guardar(form.action);
    });

    try {
        var destino = window.sessionStorage.getItem(chave);
        window.sessionStorage.removeItem(chave);
        if (destino !== window.location.pathname + window.location.search) return;
        var forms = Array.from(conteudo.querySelectorAll('form')).filter(formularioDePagina);
        for (var i = 0; i < forms.length; i++) {
            var campos = Array.from(forms[i].querySelectorAll('input:not([type="hidden"]), select, textarea, button')).filter(disponivel);
            if (!campos.length) continue;
            var invalido = campos.find(function (campo) { return campo.getAttribute('aria-invalid') === 'true'; });
            (invalido || campos[0]).focus();
            break;
        }
    } catch (erro) {
        // Sem marcador válido, mantém a entrada normal e o link de salto.
    }
});
