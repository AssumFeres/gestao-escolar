const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const codigo = fs.readFileSync(path.join(__dirname, '../../../static/global/js/foco-filtros.js'), 'utf8');
const chave = 'filtros-retorno-foco';

function tela({ storage = new Map(), url = 'http://localhost/cadastros/', bloqueado = false, indisponivel = false, marcado = true } = {}) {
    const eventos = {};
    let foco = null;
    const form = { method: 'get', target: '', action: url, matches: () => marcado,
        querySelector: () => filtrar };
    function controle(id) {
        return { id, tabIndex: 0, target: '', href: 'http://localhost/cadastros/',
            matches: seletor => seletor === ':disabled' ? indisponivel : marcado,
            closest: seletor => seletor === '[inert]' ? null : (marcado ? form : null),
            hasAttribute: () => false, getClientRects: () => [{}], focus() { foco = this; } };
    }
    const filtrar = controle('filtrar-pessoas'), limpar = controle('limpar-filtros-pessoas');
    vm.runInNewContext(codigo, {
        URL, window: { location: new URL(url), getComputedStyle: () => ({ visibility: 'visible' }),
            sessionStorage: {
                getItem(k) { if (bloqueado) throw Error('bloqueado'); return storage.get(k) || null; },
                setItem(k,v) { if (bloqueado) throw Error('bloqueado'); storage.set(k,v); },
                removeItem(k) { storage.delete(k); },
            } },
        document: { addEventListener(k,v) { eventos[k] = v; },
            getElementById(id) { return [filtrar,limpar].find(c => c.id === id); } },
    });
    eventos.DOMContentLoaded();
    return { form, filtrar, limpar, storage, get foco() { return foco; },
        enviar(op = {}) { eventos.submit({ target: form, submitter: filtrar, ...op }); },
        limparFiltros(op = {}) { eventos.click({ button: 0, target: { closest: () => limpar }, ...op }); },
    };
}

test('Filtrar retorna ao botão após GET, inclusive quando a busca não produz resultados', () => {
    const origem = tela(); origem.enviar();
    const destino = tela({ storage: origem.storage, url: 'http://localhost/cadastros/?nome=Inexistente&ativo=&categoria=' });
    assert.equal(destino.foco, destino.filtrar);
    assert.equal(destino.storage.has(chave), false);
    assert.equal(tela({ storage: destino.storage }).foco, null);
});

test('Limpar retorna ao próprio link na lista sem parâmetros', () => {
    const origem = tela({ url: 'http://localhost/cadastros/?nome=Maria' }); origem.limparFiltros();
    const destino = tela({ storage: origem.storage });
    assert.equal(destino.foco, destino.limpar);
});

test('envio implícito por Enter usa o botão padrão quando não há submitter', () => {
    const origem = tela(); origem.enviar({ submitter: null });
    const destino = tela({ storage: origem.storage });
    assert.equal(destino.foco, destino.filtrar);
});

test('GET sem adesão, POST, evento cancelado e outra aba não registram retorno', () => {
    const semAdesao = tela({ marcado: false }); semAdesao.enviar();
    assert.equal(semAdesao.storage.size, 0);
    const a = tela(); a.enviar({ defaultPrevented: true });
    a.form.method = 'post'; a.enviar();
    a.form.method = 'get'; a.form.target = '_blank'; a.enviar();
    assert.equal(a.storage.size, 0);
});

test('cliques modificados, outra aba e destino externo não deixam marcador', () => {
    const a = tela();
    for (const op of [{ ctrlKey: true }, { metaKey: true }, { shiftKey: true }, { altKey: true }, { button: 1 }, { defaultPrevented: true }]) a.limparFiltros(op);
    a.limpar.target = '_blank'; a.limparFiltros();
    a.limpar.target = ''; a.limpar.href = 'https://example.com/'; a.limparFiltros();
    assert.equal(a.storage.size, 0);
});

test('outra página, controle indisponível, marcador inválido ou storage bloqueado não tomam o foco', () => {
    const origem = tela(); origem.enviar();
    const destino = tela({ storage: origem.storage, url: 'http://localhost/outro/' });
    assert.equal(destino.foco, null); assert.equal(destino.storage.size, 0);
    origem.enviar(); assert.equal(tela({ storage: origem.storage, indisponivel: true }).foco, null);
    assert.doesNotThrow(() => tela({ storage: new Map([[chave, 'invalido']]) }));
    const bloqueada = tela({ bloqueado: true });
    assert.doesNotThrow(() => bloqueada.enviar());
    assert.doesNotThrow(() => bloqueada.limparFiltros());
    assert.equal(tela().foco, null);
});
