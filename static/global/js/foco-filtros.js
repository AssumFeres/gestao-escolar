// Retorno ao controle acionado após uma navegação de filtros GET, por adesão.
document.addEventListener('DOMContentLoaded', function () {
    var chave = 'filtros-retorno-foco';
    var seletor = 'form[data-restaurar-foco-filtros]';

    function guardar(controle, destino) {
        if (!controle || !controle.id) return;
        try {
            var url = new URL(destino, window.location.href);
            if (url.origin !== window.location.origin) return;
            window.sessionStorage.setItem(chave, JSON.stringify({ caminho: url.pathname, id: controle.id }));
        } catch (erro) {
            // O filtro continua funcionando se o armazenamento estiver indisponível.
        }
    }

    document.addEventListener('submit', function (evento) {
        var form = evento.target;
        if (evento.defaultPrevented || !form.matches(seletor) || form.method.toLowerCase() !== 'get') return;
        if (form.target && form.target !== '_self') return;
        var controle = evento.submitter || form.querySelector('button[type="submit"][data-foco-filtro]');
        if (controle && controle.matches('[data-foco-filtro]')) guardar(controle, form.action);
    });

    document.addEventListener('click', function (evento) {
        if (evento.defaultPrevented || evento.ctrlKey || evento.metaKey || evento.shiftKey || evento.altKey) return;
        if (evento.button !== undefined && evento.button !== 0) return;
        var link = evento.target.closest('a[data-foco-filtro][href]');
        if (!link || !link.closest(seletor) || link.hasAttribute('download')) return;
        if (link.target && link.target !== '_self') return;
        guardar(link, link.href);
    });

    try {
        var salvo = window.sessionStorage.getItem(chave);
        window.sessionStorage.removeItem(chave);
        if (!salvo) return;
        var retorno = JSON.parse(salvo);
        if (retorno.caminho !== window.location.pathname) return;
        var controle = document.getElementById(retorno.id);
        if (!controle || !controle.closest(seletor) || !controle.matches('[data-foco-filtro]')) return;
        if (controle.matches(':disabled') || controle.closest('[inert]') || controle.tabIndex < 0) return;
        var estilo = window.getComputedStyle(controle);
        if (!controle.getClientRects().length || estilo.visibility !== 'visible') return;
        controle.focus();
    } catch (erro) {
        // Marcador inválido não interfere com a entrada normal na página.
    }
});
