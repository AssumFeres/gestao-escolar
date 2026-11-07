const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const codigo = fs.readFileSync(path.join(__dirname, '../../static/cadastros/js/form-dinamico.js'), 'utf8');

function ambiente({ tratarAviso = true } = {}) {
    const eventos = {}, avisos = [], alertas = [];
    let foco;
    function el(tagName = 'DIV') {
        return {
            tagName, attrs: {}, listeners: {}, children: [], style: {}, value: '',
            appendChild(x) { this.children.push(x); },
            addEventListener(k,v) { this.listeners[k] = v; },
            hasAttribute(k) { return k in this.attrs; },
            getAttribute(k) { return this.attrs[k]; },
            setAttribute(k,v) { this.attrs[k] = v; },
            focus() { foco = this; }, insertAdjacentElement(_,x) { this.inserido = x; },
        };
    }
    function campo(nome, valor) {
        const x = el('INPUT'); x.value = valor;
        x.attrs = { id: 'id_formacao-0-' + nome, name: 'formacao-0-' + nome };
        return x;
    }
    const curso = campo('curso',''), ano = campo('ano_conclusao','');
    const labels = [curso,ano].map(x => { const l=el('LABEL');l.attrs.for=x.attrs.id;return l; });
    const adicionar = el('BUTTON'), total = el('INPUT'); total.value = 1;
    const tabela = el(), hidden = el(), template = el();
    template.querySelectorAll = seletor => seletor === 'select' ? [] : seletor === 'input, select, label' ? [curso,ano,...labels] : [curso,ano];
    template.querySelector = () => curso;
    template.cloneNode = () => ({ style: {}, inputs: [curso,ano].map(x => ({attrs:{...x.attrs},value:x.value})), querySelectorAll: () => [] });
    const bloco = el();
    bloco.dataset = { prefix:'formacao', fields:'curso,ano_conclusao', labels:'Curso,Ano', required:'curso', obrigatoriosCompletos:'curso,ano_conclusao' };
    bloco.querySelector = seletor => ({'.formset-template':template,'.formset-hidden':hidden,'table tbody':tabela,'.btn-adicionar':adicionar}[seletor]);
    bloco.closest = () => ({ querySelector: () => ({textContent:'Formação'}) });
    const nascimento = el('INPUT');
    const categoria = el('SELECT'); categoria.value='docente';
    const docente = el(), discente = el(); docente.dataset={categoria:'DOCENTE'}; discente.dataset={categoria:'DISCENTE'};
    const dados = {textContent:JSON.stringify({docente:'DOCENTE',discente:'DISCENTE'})};
    vm.runInNewContext(codigo, {
        CustomEvent: function(tipo,opcoes) { this.type=tipo;this.detail=opcoes.detail; },
        document: {
            get activeElement() { return foco; },
            getElementById(id) {
                if(id==='id_formacao-TOTAL_FORMS') return total;
                if(id==='id_data_nascimento') return nascimento;
                if(id==='id_funcao') return categoria;
                if(id==='funcao-categorias-data') return dados;
                return [curso,ano].find(x=>x.attrs.id===id);
            },
            querySelectorAll: s => s==='.formset-bloco'?[bloco]:s==='.btn-adicionar'?[adicionar]:s==='[data-categoria]'?[docente,discente]:[],
            createElement:el, addEventListener(k,v) {eventos[k]=v;},
            dispatchEvent(e) {avisos.push(e);return !tratarAviso;},
        },
        window: {alert:m=>alertas.push(m)},
    });
    eventos.DOMContentLoaded();
    return {curso,ano,total,tabela,hidden,bloco,adicionar,nascimento,avisos,alertas,categoria,docente,discente,get foco(){return foco;},
        adicionarLinha() {adicionar.focus();adicionar.listeners.click({preventDefault(){}});},
    };
}

test('linha vazia e parcialmente preenchida mantem criterios e solicitam aviso', () => {
    const a=ambiente();a.adicionarLinha();
    assert.equal(a.tabela.children.length,0);assert.equal(a.total.value,1);
    assert.match(a.avisos[0].detail.mensagem,/Curso/);assert.equal(a.avisos[0].detail.gatilho,a.adicionar);
    a.curso.value='Curso';a.adicionarLinha();
    assert.match(a.avisos[1].detail.mensagem,/Ano/);assert.equal(a.total.value,1);
});

test('adicionar preserva valores clonados, renomeia campos e anuncia com foco no novo campo', () => {
    const a=ambiente();a.curso.value='Curso';a.ano.value='2025';a.adicionarLinha();
    assert.equal(a.tabela.children.length,1);assert.equal(a.total.value,2);
    assert.deepEqual(a.hidden.children[0].inputs.map(x=>x.value),['Curso','2025']);
    assert.equal(a.hidden.children[0].inputs[0].attrs.name,'formacao-0-curso');
    assert.equal(a.curso.attrs.name,'formacao-1-curso');assert.equal(a.curso.value,'');
    const estado=a.bloco.children[0];assert.equal(estado.attrs.role,'status');
    assert.match(estado.textContent,/Total de registros: 1/);assert.equal(a.foco,a.curso);
});

test('aviso nativo continua disponivel quando o componente nao tratar o evento', () => {
    const a=ambiente({tratarAviso:false});a.adicionarLinha();
    assert.equal(a.alertas.length,1);assert.match(a.alertas[0],/Curso/);
});

test('data futura e menor de idade mantem avisos sem alterar valor ou bloquear envio', () => {
    const a=ambiente();a.nascimento.focus();
    a.nascimento.value='3000-01-01';a.nascimento.listeners.change();
    assert.match(a.avisos[0].detail.mensagem,/futura/);assert.equal(a.nascimento.value,'3000-01-01');
    a.nascimento.value=(new Date().getFullYear()-5)+'-01-01';a.nascimento.listeners.change();
    assert.match(a.avisos[1].detail.mensagem,/menor de idade/);assert.equal(a.avisos[1].detail.gatilho,a.nascimento);
});

test('categorias continuam mostrando os mesmos blocos', () => {
    const a=ambiente();assert.equal(a.docente.style.display,'');assert.equal(a.discente.style.display,'none');
    a.categoria.value='discente';a.categoria.listeners.change();
    assert.equal(a.docente.style.display,'none');assert.equal(a.discente.style.display,'');
});
