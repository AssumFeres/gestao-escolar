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
    grupos.forEach(function (grupo) {
        var titulo = grupo.querySelector('.sidebar-grupo-titulo');
        titulo.addEventListener('click', function () {
            var jaAberto = grupo.classList.contains('aberto');
            // Fecha os outros grupos abertos, abre só o clicado (comportamento
            // de accordion — só um grupo expandido por vez).
            grupos.forEach(function (outro) {
                outro.classList.remove('aberto');
            });
            if (!jaAberto) {
                grupo.classList.add('aberto');
            }
        });
    });
});
