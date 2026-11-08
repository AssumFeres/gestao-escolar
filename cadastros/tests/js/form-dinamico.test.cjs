const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const codigo = fs.readFileSync(path.join(__dirname, '../../static/cadastros/js/form-dinamico.js'), 'utf8');

function ambiente({ tratarAviso = true, recuperado = false, indice = 0, erros = false, semLinha = false } = {}) {
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
            removeAttribute(k) { delete this.attrs[k]; },
            querySelector() { return null; },
            focus() { foco = this; }, insertAdjacentElement(_,x) { this.inserido = x; },
        };
    }
    function campo(nome, valor) {
        const x = el('INPUT'); x.value = valor;
        x.attrs = { id: 'id_formacao-' + indice + '-' + nome, name: 'formacao-' + indice + '-' + nome };
        return x;
    }
    const curso = campo('curso',''), ano = campo('ano_conclusao','');
    const labels = [curso,ano].map(x => { const l=el('LABEL');l.attrs.for=x.attrs.id;return l; });
    const adicionar = el('BUTTON'), total = el('INPUT'); total.value = indice + 1;
    const tabela = el(), hidden = el(), template = el();
    const ajuda = el(), erro = {remove() {this.removido = true;}};
    ajuda.attrs.id = ano.attrs.id + '_helptext';
    if (erros) {
        ano.attrs['aria-invalid'] = 'true';
        ano.attrs['aria-describedby'] = ajuda.attrs.id + ' ' + ano.attrs.id + '_error';
    }
    const recuperados = [], legenda = el('LEGEND');
    template.parentNode = {insertBefore(clone, referencia) {assert.equal(referencia,template);recuperados.push(clone);}};
    template.querySelectorAll = seletor => {
        if (seletor === 'select') return [curso,ano].filter(x => x.tagName === 'SELECT');
        if (seletor === '.erro, .errorlist') return erros ? [erro] : [];
        if (seletor.startsWith('[name]')) return [curso,ano,...labels,ajuda];
        return [curso,ano];
    };
    template.querySelector = seletor => seletor === 'legend' ? legenda : curso;
    template.cloneNode = () => ({ style: {}, attrs: {}, setAttribute(k,v){this.attrs[k]=v;}, inputs: [curso,ano].map(x => ({tagName:x.tagName,attrs:{...x.attrs},value:x.tagName === 'SELECT' ? '' : x.value})), querySelectorAll() { return this.inputs.filter(x => x.tagName === 'SELECT'); } });
    const bloco = el();
    bloco.dataset = { prefix:'formacao', recuperado:String(recuperado), fields:'curso,ano_conclusao', labels:'Curso,Ano', required:'curso', obrigatoriosCompletos:'curso,ano_conclusao' };
    bloco.querySelector = seletor => ({'.formset-template':semLinha ? null : template,'.formset-hidden':hidden,'table tbody':recuperado ? null : tabela,'.btn-adicionar':adicionar}[seletor]);
    bloco.closest = () => ({ querySelector: () => ({textContent:'Formação'}) });
    const nascimento = el('INPUT');
    const categoria = el('SELECT'); categoria.value='docente';
    const docente = el(), discente = el(); docente.dataset={categoria:'DOCENTE'}; discente.dataset={categoria:'DISCENTE'};
    docente.querySelector = () => erros ? {} : null;
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
    return {curso,ano,total,tabela,hidden,bloco,adicionar,nascimento,avisos,alertas,categoria,docente,discente,recuperados,ajuda,erro,legenda,get foco(){return foco;},
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

test('apos POST invalido, adicionar conserva registro editavel e avanca o indice sem ocultar erros anteriores', () => {
    const a=ambiente({recuperado:true,indice:1,erros:true});
    a.curso.value='Curso mantido';a.ano.value='2025';a.adicionarLinha();
    assert.equal(a.hidden.children.length,0);assert.equal(a.tabela.children.length,0);
    assert.equal(a.recuperados.length,1);
    assert.equal(a.recuperados[0].attrs.class,'formset-recuperado');
    assert.equal(a.recuperados[0].inputs[0].attrs.name,'formacao-1-curso');
    assert.equal(a.recuperados[0].inputs[1].attrs['aria-invalid'],'true');
    assert.equal(a.recuperados[0].inputs[0].value,'Curso mantido');
    assert.equal(a.total.value,3);assert.equal(a.curso.attrs.name,'formacao-2-curso');
    assert.equal(a.ano.attrs['aria-invalid'],undefined);
    assert.equal(a.ano.attrs['aria-describedby'],'id_formacao-2-ano_conclusao_helptext');
    assert.equal(a.ajuda.attrs.id,'id_formacao-2-ano_conclusao_helptext');
    assert.equal(a.erro.removido,true);assert.equal(a.legenda.textContent,'Registro 3');
    assert.equal(a.foco,a.curso);
});

test('bloco com erro do servidor permanece visivel mesmo se a categoria selecionada for outra', () => {
    const a=ambiente({erros:true});a.categoria.value='discente';a.categoria.listeners.change();
    assert.equal(a.docente.style.display,'');assert.equal(a.discente.style.display,'');
});

test('management form invalido sem linhas nao quebra o restante do cadastro', () => {
    const a=ambiente({semLinha:true});assert.equal(a.adicionar.disabled,true);
    a.categoria.value='discente';assert.doesNotThrow(()=>a.categoria.listeners.change());
});

test('selecao do dropdown e preservada ao adicionar apos recuperacao de erro', () => {
    const a=ambiente({recuperado:true,indice:1});
    a.curso.tagName='SELECT';a.curso.value='2';a.curso.selectedIndex=1;
    a.curso.options=[{text:'Primeiro vinculo'},{text:'Segundo vinculo'}];
    a.ano.value='2025';a.adicionarLinha();
    assert.equal(a.recuperados[0].inputs[0].value,'2');
    assert.equal(a.curso.selectedIndex,0);
});
