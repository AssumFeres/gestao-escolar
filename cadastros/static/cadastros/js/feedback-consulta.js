// Mensagens de consulta sem mover o foco ou alterar a validação dos campos.
window.CadastroFeedback = {
    associar: function (campo, ids) {
        var descricoes = (campo.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean);
        ids.forEach(function (id) {
            if (document.getElementById(id) && descricoes.indexOf(id) === -1) descricoes.push(id);
        });
        campo.setAttribute('aria-describedby', descricoes.join(' '));
    },
    mostrar: function (regiao, mensagem, erro) {
        if (!regiao) return;
        regiao.textContent = '';
        regiao.className = mensagem ? (erro ? 'erro' : 'mensagem-consulta') : '';
        if (!mensagem) return;
        if (erro) {
            var icone = document.createElement('span');
            icone.className = 'icone-erro';
            icone.setAttribute('aria-hidden', 'true');
            icone.textContent = '⚠️';
            regiao.appendChild(icone);
        }
        var texto = document.createElement('span');
        texto.className = 'mensagem-erro-conteudo';
        texto.textContent = mensagem;
        regiao.appendChild(texto);
    }
};
