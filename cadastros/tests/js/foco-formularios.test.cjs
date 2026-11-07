const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const codigo = fs.readFileSync(path.join(__dirname, '../../../static/global/js/foco-formularios.js'), 'utf8');
const chave = 'formulario-pagina-foco';

function tela({ url = 'http://127.0.0.1:8000/cadastros/novo/', storage = new Map(), bloqueado = false, configuracoes = [{campos:[{}]}] } = {}) {
    let foco = null;
    const eventos = {}, main = { listeners: {}, addEventListener(k,v) {this.listeners[k]=v;} };
    const forms = configuracoes.map(op => {
        const campos = (op.campos || []).map(c => ({
            ...c, tabIndex: c.tabIndex === undefined ? 0 : c.tabIndex,
            matches: () => !!c.disabled, closest: () => c.inert ? {} : null,
            getClientRects: () => c.hidden ? [] : [{}],
            getAttribute: nome => nome === 'aria-invalid' && c.invalido ? 'true' : null,
            focus() {foco=this;},
        }));
        return {method:op.method || 'post',target:op.target || '',action:op.action || url,campos,
            closest: () => op.popup ? {} : null,
            querySelector: () => op.senha ? {} : null,querySelectorAll: () => campos};
    });
    main.querySelectorAll = () => forms;
    vm.runInNewContext(codigo, {
        URL, window: { location:new URL(url),
            getComputedStyle: el => ({visibility:el.invisivel?'hidden':'visible'}),
            sessionStorage: {
                getItem(k) {if(bloqueado)throw Error('bloqueado');return storage.get(k)||null;},
                setItem(k,v) {if(bloqueado)throw Error('bloqueado');storage.set(k,v);},
                removeItem(k) {storage.delete(k);},
            },
        },
        document: {getElementById:()=>main,addEventListener(k,v){eventos[k]=v;}},
    });
    eventos.DOMContentLoaded();
    return {storage,forms,get foco(){return foco;},
        clicar(href,op={}) {
            const link = {href,target:op.target || '',hasAttribute:()=>!!op.download,closest:()=>op.popup?{}:null};
            main.listeners.click({button:0,...op,target:{closest:()=>link}});
        },
        enviar(form=forms[0],defaultPrevented=false) {main.listeners.submit({target:form,defaultPrevented});},
    };
}

test('link Cadastrar nova pessoa leva ao primeiro campo da pagina seguinte', () => {
    const origem=tela({url:'http://127.0.0.1:8000/cadastros/',configuracoes:[]});
    origem.clicar('http://127.0.0.1:8000/cadastros/novo/');
    const destino=tela({storage:origem.storage,configuracoes:[{campos:[{nome:'funcao'},{nome:'nome'}]}]});
    assert.equal(destino.foco,destino.forms[0].campos[0]);
    assert.equal(destino.storage.has(chave),false);
});

test('retorno de POST invalido prioriza o campo com erro', () => {
    const origem=tela();origem.enviar();
    const destino=tela({storage:origem.storage,configuracoes:[{campos:[{}, {invalido:true},{}]}]});
    assert.equal(destino.foco,destino.forms[0].campos[1]);
});

test('ignora controles ocultos, desabilitados, inert e fora da sequencia Tab', () => {
    const storage=new Map([[chave,'/cadastros/novo/']]);
    const destino=tela({storage,configuracoes:[{campos:[{hidden:true},{disabled:true},{inert:true},{invisivel:true},{tabIndex:-1},{}]}]});
    assert.equal(destino.foco,destino.forms[0].campos[5]);
});

test('formularios de busca e popup nao tomam o foco do formulario de pagina', () => {
    const storage=new Map([[chave,'/cadastros/novo/']]);
    const destino=tela({storage,configuracoes:[{method:'get',campos:[{}]},{popup:true,campos:[{}]},{campos:[{}]}]});
    assert.equal(destino.foco,destino.forms[2].campos[0]);
});

test('links internos, externos, de popup, download e nova aba nao guardam foco', () => {
    const a=tela();
    for(const op of [{ctrlKey:true},{shiftKey:true},{metaKey:true},{altKey:true},{button:1},{target:'_blank'},{download:true},{popup:true},{defaultPrevented:true}]) {
        a.clicar('http://127.0.0.1:8000/outro/',op);assert.equal(a.storage.has(chave),false);
    }
    a.clicar('http://127.0.0.1:8000/cadastros/novo/#id_nome');assert.equal(a.storage.has(chave),false);
    a.clicar('https://example.com/form/');assert.equal(a.storage.has(chave),false);
});

test('submit interceptado, GET, popup e outra aba nao registram entrada de pagina', () => {
    const a=tela({configuracoes:[{campos:[{}]},{method:'get'},{popup:true},{target:'_blank'}]});
    a.enviar(a.forms[0],true);
    for(const f of a.forms.slice(1))a.enviar(f);
    assert.equal(a.storage.has(chave),false);
});

test('acesso direto, outro destino e marcador consumido nao forçam foco', () => {
    assert.equal(tela().foco,null);
    const storage=new Map([[chave,'/outra/']]);assert.equal(tela({storage}).foco,null);
    assert.equal(storage.has(chave),false);
    storage.set(chave,'/cadastros/novo/');assert.ok(tela({storage}).foco);
    assert.equal(tela({storage}).foco,null);
});

test('armazenamento bloqueado nao quebra links e formulario com senha fica fora do escopo', () => {
    const bloqueada=tela({bloqueado:true});
    assert.doesNotThrow(()=>bloqueada.clicar('http://127.0.0.1:8000/outro/'));
    const storage=new Map([[chave,'/cadastros/novo/']]);
    assert.equal(tela({storage,configuracoes:[{senha:true,campos:[{}]}]}).foco,null);
});
