const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const tick = () => new Promise(resolve => setImmediate(resolve));

function ambiente(tipo) {
    const eventos = [], chamadas = [], ids = {};
    let focos = 0;
    function elemento() {
        let texto = '';
        return {
            attrs: {}, listeners: {}, children: [], value: '', className: '',
            get textContent() { return texto + this.children.map(el => el.textContent).join(''); },
            set textContent(v) { texto = v; this.children = []; },
            getAttribute(k) { return this.attrs[k] || null; },
            setAttribute(k,v) { this.attrs[k] = v; },
            addEventListener(k,v) { this.listeners[k] = v; },
            appendChild(el) { this.children.push(el); }, focus() { focos++; },
        };
    }
    for (const id of ['id_cpf', 'id_nome_completo', 'id_endereco_cep', 'id_endereco_logradouro', 'id_endereco_bairro', 'id_endereco_cidade', 'id_endereco_uf', 'ajuda-consulta-cpf', 'aviso-pessoa-encontrada', 'ajuda-consulta-cep', 'status-consulta-cep']) ids[id] = elemento();
    const campo = ids[tipo === 'cep' ? 'id_endereco_cep' : 'id_cpf'];
    const regiao = ids[tipo === 'cep' ? 'status-consulta-cep' : 'aviso-pessoa-encontrada'];
    campo.setAttribute('aria-describedby', 'erro-original');
    regiao.setAttribute('role', 'status');
    const contexto = vm.createContext({
        document: { getElementById: id => ids[id], addEventListener(k,v) { eventos.push(v); }, createElement: elemento },
        window: {}, fetch: url => new Promise(resolve => chamadas.push({ url, resolve })),
    });
    for (const nome of ['feedback-consulta.js', 'buscar-' + tipo + '.js']) {
        vm.runInContext(fs.readFileSync(path.join(__dirname, '../../static/cadastros/js/', nome), 'utf8'), contexto);
    }
    eventos.forEach(fn => fn());
    return {
        ids, campo, regiao, chamadas, get focos() { return focos; },
        consultar(valor) {
            campo.value = valor;
            if (tipo === 'cep') campo.listeners.blur();
            else { let prevenido = false; campo.listeners.keydown({ key: 'Enter', preventDefault() { prevenido = true; } }); assert.equal(prevenido, true); }
        },
        responder(indice, dados, status = 200) {
            chamadas[indice].resolve({ ok: status === 200, status, json: () => Promise.resolve(dados) });
            return tick();
        },
    };
}

test('CEP consulta no blur, anuncia e preenche os mesmos quatro campos sem mover foco', async () => {
    const a = ambiente('cep'); a.consultar('01001-000');
    assert.equal(a.chamadas[0].url, '/api/cadastros/cep/01001000/');
    assert.match(a.regiao.textContent, /Consultando/);
    await a.responder(0, { logradouro: 'Rua', bairro: 'Centro', cidade: 'Cidade', uf: 'SP' });
    assert.equal(a.ids.id_endereco_logradouro.value, 'Rua');
    assert.equal(a.ids.id_endereco_bairro.value, 'Centro');
    assert.equal(a.ids.id_endereco_cidade.value, 'Cidade');
    assert.equal(a.ids.id_endereco_uf.value, 'SP');
    assert.match(a.regiao.textContent, /preenchido/); assert.equal(a.focos, 0);
    assert.equal(a.campo.attrs['aria-describedby'], 'erro-original ajuda-consulta-cep status-consulta-cep');
});

test('CEP inexistente ou falha de servidor mantem dados e permite preenchimento manual', async () => {
    for (const status of [404, 500]) {
        const a = ambiente('cep'); a.ids.id_endereco_cidade.value = 'Preenchimento manual';
        a.consultar('01001000'); await a.responder(0, {}, status);
        assert.equal(a.ids.id_endereco_cidade.value, 'Preenchimento manual');
        assert.equal(a.regiao.className, 'erro'); assert.match(a.regiao.textContent, /manualmente/);
        assert.equal(a.focos, 0);
    }
});

test('CPF consulta com Enter, preenche dados e anuncia pessoa encontrada', async () => {
    const a = ambiente('cpf'); a.consultar('123.456.789-01');
    assert.equal(a.chamadas[0].url, '/api/cadastros/pessoa-por-cpf/12345678901/');
    await a.responder(0, { encontrada: true, pessoa: { nome_completo: 'Pessoa de teste', endereco_cidade: 'Cidade' } });
    assert.equal(a.ids.id_nome_completo.value, 'Pessoa de teste');
    assert.equal(a.ids.id_endereco_cidade.value, 'Cidade');
    assert.match(a.regiao.textContent, /Pessoa de teste/); assert.equal(a.focos, 0);
    assert.equal(a.campo.attrs['aria-describedby'], 'erro-original ajuda-consulta-cpf aviso-pessoa-encontrada');
});

test('CPF nao encontrado ou falha HTTP nao apaga preenchimento manual', async () => {
    for (const status of [200, 500]) {
        const a = ambiente('cpf'); a.ids.id_nome_completo.value = 'Nome manual';
        a.consultar('12345678901'); await a.responder(0, { encontrada: false }, status);
        assert.equal(a.ids.id_nome_completo.value, 'Nome manual');
        assert.match(a.regiao.textContent, /preenchendo/); assert.equal(a.focos, 0);
    }
});

for (const tipo of ['cep', 'cpf']) {
    test(tipo + ': respostas antigas e entrada alterada nao sobrescrevem dados atuais', async () => {
        const a = ambiente(tipo), campoAlvo = tipo === 'cep' ? a.ids.id_endereco_cidade : a.ids.id_nome_completo;
        a.consultar(tipo === 'cep' ? '01001000' : '12345678901');
        a.campo.listeners.input();
        a.consultar(tipo === 'cep' ? '02002000' : '10987654321');
        const resultado = nome => tipo === 'cep' ? { logradouro: 'Rua', bairro: 'Centro', cidade: nome, uf: 'SP' } : { encontrada: true, pessoa: { nome_completo: nome } };
        await a.responder(1, resultado('Atual')); await a.responder(0, resultado('Antigo'));
        assert.equal(campoAlvo.value, 'Atual');
        a.consultar(tipo === 'cep' ? '03003000' : '11111111111');
        a.campo.value = ''; a.campo.listeners.input();
        await a.responder(2, resultado('Ignorar'));
        assert.equal(campoAlvo.value, 'Atual'); assert.equal(a.regiao.textContent, '');
    });
    test(tipo + ': comprimento incompleto nao consulta nem altera validacao do campo', () => {
        const a = ambiente(tipo); a.consultar('123');
        assert.equal(a.chamadas.length, 0); assert.equal(a.regiao.className, 'erro');
        assert.equal(a.campo.attrs['aria-invalid'], undefined);
    });
}
