/**
 * cadastros/static/cadastros/js/buscar-cpf.js
 *
 * Busca de Pessoa por CPF (docs/27) — ao apertar Enter no campo CPF,
 * consulta /api/cadastros/pessoa-por-cpf/<cpf>/ e, se encontrar, pré-
 * preenche os demais campos comuns da Pessoa com os dados já cadastrados.
 * O usuário pode editar o que precisar antes de salvar — ao submeter, o
 * Service atualiza a Pessoa existente de verdade (não ignora mais os
 * dados do formulário como antes de 02/09/2026).
 *
 * Não bloqueia nada: se o CPF não for encontrado, o cadastro continua
 * normal (formulário em branco, cria do zero).
 */
document.addEventListener('DOMContentLoaded', function () {
    var cpfInput = document.getElementById('id_cpf');
    if (!cpfInput) return;

    var mapaCampos = {
        nome_completo: 'id_nome_completo',
        data_nascimento: 'id_data_nascimento',
        email: 'id_email',
        telefone: 'id_telefone',
        registro_matricula: 'id_registro_matricula',
        registro_aluno: 'id_registro_aluno',
        codigo_anac: 'id_codigo_anac',
        sexo: 'id_sexo',
        identidade: 'id_identidade',
        data_emissao_identidade: 'id_data_emissao_identidade',
        orgao_expedidor_identidade: 'id_orgao_expedidor_identidade',
        naturalidade: 'id_naturalidade',
        uf_naturalidade: 'id_uf_naturalidade',
        nacionalidade: 'id_nacionalidade',
        filiacao_1: 'id_filiacao_1',
        filiacao_2: 'id_filiacao_2',
        nivel_instrucao: 'id_nivel_instrucao',
        estado_civil: 'id_estado_civil',
        raca_cor: 'id_raca_cor',
        endereco_cep: 'id_endereco_cep',
        endereco_logradouro: 'id_endereco_logradouro',
        endereco_numero: 'id_endereco_numero',
        endereco_complemento: 'id_endereco_complemento',
        endereco_bairro: 'id_endereco_bairro',
        endereco_cidade: 'id_endereco_cidade',
        endereco_uf: 'id_endereco_uf',
    };

    cpfInput.addEventListener('keydown', function (evento) {
        if (evento.key !== 'Enter') return;
        evento.preventDefault(); // não deixa o Enter submeter o formulário

        var cpf = cpfInput.value.replace(/\D/g, '');
        if (cpf.length !== 11) {
            return;
        }

        fetch('/api/cadastros/pessoa-por-cpf/' + cpf + '/')
            .then(function (resposta) { return resposta.json(); })
            .then(function (dados) {
                if (!dados.encontrada) {
                    removerAviso();
                    return;
                }
                preencherCampos(dados.pessoa);
                mostrarAviso(dados.pessoa.nome_completo);
            })
            .catch(function () {
                console.warn('Não foi possível buscar a Pessoa por este CPF.');
            });
    });

    function preencherCampos(pessoa) {
        Object.keys(mapaCampos).forEach(function (chave) {
            var elemento = document.getElementById(mapaCampos[chave]);
            if (!elemento) return;
            var valor = pessoa[chave];
            elemento.value = (valor === null || valor === undefined) ? '' : valor;
        });
    }

    function removerAviso() {
        var avisoAnterior = document.getElementById('aviso-pessoa-encontrada');
        if (avisoAnterior) avisoAnterior.remove();
    }

    function mostrarAviso(nome) {
        removerAviso();

        var aviso = document.createElement('div');
        aviso.id = 'aviso-pessoa-encontrada';
        aviso.textContent = 'Pessoa já cadastrada: ' + nome + '. Dados carregados — edite o que precisar antes de salvar.';
        aviso.style.backgroundColor = '#fff3cd';
        aviso.style.border = '1px solid #ffeeba';
        aviso.style.color = '#856404';
        aviso.style.padding = '10px 14px';
        aviso.style.borderRadius = '6px';
        aviso.style.marginTop = '0.5rem';

        var fieldsetPai = cpfInput.closest('fieldset');
        fieldsetPai.insertAdjacentElement('afterend', aviso);
    }
});
