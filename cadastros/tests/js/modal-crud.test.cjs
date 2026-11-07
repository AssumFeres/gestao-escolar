const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const codigo = fs.readFileSync(path.join(__dirname, '../../static/cadastros/js/modal-crud.js'), 'utf8');
const tick = () => new Promise(resolve => setImmediate(resolve));

// DOM simplificado: testa os handlers; teclado nativo e leitor de tela exigem navegador.
function ambiente(storage = new Map()) {
    const eventos = {};
    let ativo, html = '', titulo, campos = [], recargas = 0;
    const chamadas = [];
    function elemento(tagName = 'DIV') {
        return {
            tagName, attrs: {}, listeners: {}, children: [], inert: false,
            tabIndex: 0, isConnected: true, visible: true, textContent: '',
            setAttribute(k, v) { this.attrs[k] = v; },
            getAttribute(k) { return this.attrs[k] || null; },
            removeAttribute(k) { delete this.attrs[k]; },
            addEventListener(k, v) { this.listeners[k] = v; },
            matches() { return !!this.disabled; },
            closest() { return this.inert ? this : null; },
            getClientRects() { return this.visible ? [{}] : []; },
            focus() { ativo = this; },
            appendChild(el) { this.children.push(el); },
            prepend(el) { this.children.unshift(el); },
        };
    }
    function filhos(pai, elementos) {
        pai.children = elementos;
        elementos.forEach(el => { el.parentElement = pai; });
    }
    const body = elemento(), header = elemento(), layout = elemento(), nav = elemento();
    const main = elemento(), fundo = elemento(), preInert = elemento(), overlay = elemento();
    preInert.inert = true;
    filhos(body, [header, layout]); filhos(layout, [nav, main]);
    filhos(main, [fundo, preInert, overlay]);
    overlay.style = { display: 'none' };
    const caixa = elemento(), corpo = elemento(), fechar = elemento('BUTTON'), status = elemento();
    const salvar = elemento('BUTTON'), cancelar = elemento('BUTTON');
    const gatilho = elemento('BUTTON'); gatilho.dataset = { url: '/form/' }; gatilho.textContent = 'Novo item';
    Object.defineProperty(corpo, 'innerHTML', {
        get() { return html; },
        set(valor) {
            html = valor; corpo.children = [];
            titulo = valor.includes('<h3>') ? { id: '' } : null;
            campos = valor.includes('<form') ? [elemento('INPUT')] : [];
            if (campos[0]) campos[0].invalido = valor.includes('aria-invalid');
        },
    });
    corpo.querySelector = () => titulo || corpo.children.find(el => el.tagName === 'h3') || null;
    corpo.querySelectorAll = seletor => seletor.startsWith('[aria-invalid') ? campos.filter(el => el.invalido) : campos;
    caixa.querySelectorAll = () => [fechar, ...campos, salvar, cancelar];
    caixa.contains = el => [caixa, corpo, fechar, salvar, cancelar, ...campos, ...corpo.children].includes(el);
    const ids = { 'modal-crud-overlay': overlay, 'modal-crud-caixa': caixa,
        'modal-crud-corpo': corpo, 'modal-crud-status': status, 'modal-crud-fechar': fechar };
    vm.runInNewContext(codigo, {
        document: {
            body, get activeElement() { return ativo; },
            getElementById: id => ids[id], querySelectorAll: () => [gatilho],
            addEventListener(k, v) { eventos[k] = v; }, createElement: elemento,
        },
        window: {
            getComputedStyle: () => ({ visibility: 'visible' }),
            sessionStorage: { getItem: k => storage.get(k) || null, setItem: (k,v) => storage.set(k,v), removeItem: k => storage.delete(k) },
            location: { pathname: '/lista/', search: '', reload() { recargas++; } },
        },
        fetch: () => new Promise(resolve => chamadas.push(resolve)), FormData: function () {},
    });
    eventos.DOMContentLoaded();
    function resposta(indice, texto, ok = true) {
        chamadas[indice]({ ok, text: () => Promise.resolve(texto) });
        return tick();
    }
    return {
        eventos, caixa, corpo, fechar, salvar, cancelar, gatilho, overlay, status, fundo, header, nav, preInert, storage,
        get ativo() { return ativo; }, get campos() { return campos; }, get recargas() { return recargas; },
        abrir() { gatilho.listeners.click(); }, resposta,
        enviar() { corpo.listeners.submit({ target: { action: '/salvar/', classList: { contains: () => true } }, preventDefault() {} }); },
        tecla(key, shiftKey = false) {
            let prevenido = false;
            eventos.keydown({ key, shiftKey, preventDefault() { prevenido = true; } });
            return prevenido;
        },
    };
}

test('carregamento, nome pelo titulo e fundo inativo reversivel', async () => {
    const a = ambiente(); a.abrir();
    assert.equal(a.ativo, a.fechar);
    assert.equal(a.caixa.attrs['aria-label'], 'Novo item');
    assert.equal(a.corpo.attrs['aria-busy'], 'true');
    for (const el of [a.header, a.nav, a.fundo]) assert.equal(el.inert, true);
    await a.resposta(0, '<h3>Titulo</h3><form>campos</form>');
    assert.equal(a.caixa.attrs['aria-labelledby'], 'modal-crud-titulo');
    assert.equal(a.caixa.attrs['aria-label'], undefined);
    assert.equal(a.corpo.attrs['aria-busy'], 'false');
    assert.equal(a.ativo, a.campos[0]);
    assert.equal(a.tecla('Escape'), true);
    assert.equal(a.ativo, a.gatilho);
    for (const el of [a.header, a.nav, a.fundo]) assert.equal(el.inert, false);
    assert.equal(a.preInert.inert, true);
});

test('Tab e Shift+Tab circulam entre as bordas sem alterar o meio', async () => {
    const a = ambiente(); a.abrir(); await a.resposta(0, '<form>campos</form>');
    a.cancelar.focus(); assert.equal(a.tecla('Tab'), true); assert.equal(a.ativo, a.fechar);
    assert.equal(a.tecla('Tab', true), true); assert.equal(a.ativo, a.cancelar);
    a.campos[0].focus(); assert.equal(a.tecla('Tab'), false);
    a.eventos.focusin({ target: a.gatilho }); assert.equal(a.ativo, a.campos[0]);
});

test('controles ocultos/desabilitados sao ignorados e caixa recebe foco se necessario', async () => {
    const a = ambiente(); a.abrir(); await a.resposta(0, '<form>campos</form>');
    a.cancelar.disabled = true; a.salvar.visible = false;
    a.fechar.focus(); a.tecla('Tab', true); assert.equal(a.ativo, a.campos[0]);
    a.fechar.visible = false; a.campos[0].visible = false;
    a.tecla('Tab'); assert.equal(a.ativo, a.caixa);
});

test('erro de validacao atualiza titulo, foco e estado de carregamento', async () => {
    const a = ambiente(); a.abrir(); await a.resposta(0, '<h3>Titulo</h3><form>campos</form>');
    a.enviar(); assert.equal(a.status.textContent, 'Salvando formulário.');
    await a.resposta(1, '<h3>Titulo</h3><form aria-invalid="true">Erro</form>');
    assert.equal(a.ativo, a.campos[0]);
    assert.equal(a.caixa.attrs['aria-labelledby'], 'modal-crud-titulo');
    assert.equal(a.corpo.attrs['aria-busy'], 'false');
});

test('cancelar delegado e clique no fundo liberam pagina e devolvem foco', async () => {
    for (const modo of ['cancelar', 'fundo']) {
        const a = ambiente(); a.abrir(); await a.resposta(0, '<form>campos</form>');
        if (modo === 'cancelar') a.corpo.listeners.click({ target: { closest: () => a.cancelar }, preventDefault() {} });
        else a.overlay.listeners.click({ target: a.overlay });
        assert.equal(a.overlay.style.display, 'none'); assert.equal(a.fundo.inert, false);
        assert.equal(a.ativo, a.gatilho);
    }
});

test('resposta antiga nao substitui um popup reaberto', async () => {
    const a = ambiente(); a.abrir(); a.tecla('Escape'); a.abrir();
    await a.resposta(0, '<h3>Antigo</h3><form>antigo</form>');
    assert.equal(a.corpo.innerHTML, '');
    await a.resposta(1, '<h3>Novo</h3><form>novo</form>');
    assert.match(a.corpo.innerHTML, /novo/);
});

test('falha HTTP preserva formulario e permite sair por Esc', async () => {
    const a = ambiente(); a.abrir(); await a.resposta(0, '<form>dados</form>');
    a.enviar(); await a.resposta(1, 'erro interno', false);
    assert.equal(a.corpo.innerHTML, '<form>dados</form>');
    assert.equal(a.corpo.children[0].attrs.role, 'alert');
    assert.equal(a.ativo, a.corpo.children[0]);
    a.tecla('Escape'); assert.equal(a.fundo.inert, false); assert.equal(a.ativo, a.gatilho);
});

test('salvamento mantem restauracao do gatilho apos recarregar', async () => {
    const a = ambiente(); a.abrir(); await a.resposta(0, '<form>dados</form>');
    a.enviar(); await a.resposta(1, '{"sucesso":true}');
    assert.equal(a.recargas, 1);
    const b = ambiente(a.storage); assert.equal(b.ativo, b.gatilho);
    assert.equal(b.storage.has('modal-crud-foco-retorno'), false);
});

test('aviso usa o dialogo compartilhado e devolve foco pelo OK ou Esc', () => {
    for (const modo of ['ok', 'esc']) {
        const a = ambiente(); let tratado = false;
        a.eventos['modal-crud-aviso']({ detail: { mensagem: 'Preencha o curso.', gatilho: a.gatilho }, preventDefault() { tratado = true; } });
        assert.equal(tratado, true);
        assert.equal(a.caixa.attrs['aria-labelledby'], 'modal-crud-titulo');
        assert.equal(a.caixa.attrs['aria-describedby'], 'modal-crud-aviso-texto');
        const ok = a.corpo.children.at(-1);
        assert.equal(ok.textContent, 'OK'); assert.equal(a.ativo, ok);
        assert.equal(a.fundo.inert, true);
        if (modo === 'ok') ok.listeners.click(); else a.tecla('Escape');
        assert.equal(a.fundo.inert, false); assert.equal(a.ativo, a.gatilho);
    }
});
