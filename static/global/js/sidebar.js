// sidebar.js
// Accordion do menu lateral (agrupado por ator). Progressive enhancement:
// sem este script, todos os submenus continuam visíveis e clicáveis
// (a classe 'js-ativo' só é adicionada aqui, via JS) — ninguém fica sem
// acesso a um link só porque o JS falhou ao carregar.

document.addEventListener('DOMContentLoaded', function () {
    var sidebar = document.getElementById('sidebar-navegacao');
    if (!sidebar) {
        return;
    }

    sidebar.classList.add('js-ativo');

    var grupos = sidebar.querySelectorAll('.sidebar-grupo');
    var chaveFoco = 'sidebar-foco-retorno';

    function guardarFoco(link, indiceGrupo, evento) {
        if (evento.defaultPrevented || evento.ctrlKey || evento.metaKey || evento.shiftKey || evento.altKey) return;
        if (evento.button !== undefined && evento.button !== 0) return;
        if (link.target && link.target !== '_self') return;
        try {
            var destino = new URL(link.href, window.location.href);
            if (destino.origin !== window.location.origin) return;
            window.sessionStorage.setItem(chaveFoco, JSON.stringify({
                pagina: destino.origin + destino.pathname + destino.search,
                href: link.href,
                grupo: indiceGrupo,
            }));
        } catch (erro) {
            // Sem armazenamento, o link continua com sua navegação nativa.
        }
    }

    function definirExpandido(grupo, expandido) {
        grupo.classList.toggle('aberto', expandido);
        grupo.querySelector('.sidebar-grupo-titulo').setAttribute('aria-expanded', String(expandido));
    }

    function focarConteudo() {
        var conteudo = document.getElementById('conteudo-principal');
        if (!conteudo) return;
        var controles = conteudo.querySelectorAll('input:not([type="hidden"]), select, textarea, button, a[role="button"]');
        var primeiro = Array.from(controles).find(function (controle) {
            return !controle.matches(':disabled') && controle.tabIndex >= 0 &&
                !controle.closest('[inert]') && controle.getClientRects().length > 0 &&
                window.getComputedStyle(controle).visibility === 'visible';
        });
        (primeiro || conteudo).focus();
    }

    grupos.forEach(function (grupo, indiceGrupo) {
        var titulo = grupo.querySelector('.sidebar-grupo-titulo');
        definirExpandido(grupo, grupo.classList.contains('aberto'));
        grupo.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function (evento) {
                guardarFoco(link, indiceGrupo, evento);
            });
        });
        titulo.addEventListener('click', function () {
            var jaAberto = grupo.classList.contains('aberto');
            // Fecha os outros grupos abertos, abre só o clicado (comportamento
            // de accordion — só um grupo expandido por vez).
            grupos.forEach(function (outro) {
                definirExpandido(outro, false);
            });
            if (!jaAberto) {
                definirExpandido(grupo, true);
            }
        });
    });

    try {
        var registro = window.sessionStorage.getItem(chaveFoco);
        window.sessionStorage.removeItem(chaveFoco);
        if (!registro) return;
        var retorno = JSON.parse(registro);
        if (retorno.pagina !== window.location.origin + window.location.pathname + window.location.search) return;
        var grupoRetorno = grupos[retorno.grupo];
        if (!grupoRetorno) return;
        var linkRetorno = Array.from(grupoRetorno.querySelectorAll('a')).find(function (link) {
            return link.href === retorno.href;
        });
        if (!linkRetorno) return;
        grupos.forEach(function (grupo) {
            definirExpandido(grupo, grupo === grupoRetorno);
        });
        focarConteudo();
    } catch (erro) {
        // Registro inválido ou bloqueado não altera o acesso ao menu.
    }
});
