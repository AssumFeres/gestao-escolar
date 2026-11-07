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
    var regiao = document.getElementById('aviso-pessoa-encontrada');
    var feedback = window.CadastroFeedback;
    var consultaAtual = 0;
    feedback.associar(cpfInput, ['ajuda-consulta-cpf', 'aviso-pessoa-encontrada']);
    cpfInput.addEventListener('input', function () {
        consultaAtual++;
        feedback.mostrar(regiao, '');
    });

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
        var consulta = ++consultaAtual;

        var cpf = cpfInput.value.replace(/\D/g, '');
        if (cpf.length !== 11) {
            feedback.mostrar(regiao, 'Informe um CPF com 11 dígitos para consultar uma pessoa.', true);
            return;
        }

        feedback.mostrar(regiao, 'Consultando o CPF...');
        fetch('/api/cadastros/pessoa-por-cpf/' + cpf + '/')
            .then(function (resposta) {
                if (!resposta.ok) throw new Error('Falha na consulta.');
                return resposta.json();
            })
            .then(function (dados) {
                if (consulta !== consultaAtual || cpfInput.value.replace(/\D/g, '') !== cpf) return;
                if (!dados.encontrada) {
                    feedback.mostrar(regiao, 'Pessoa não encontrada. Continue preenchendo o cadastro.');
                    return;
                }
                preencherCampos(dados.pessoa);
                feedback.mostrar(regiao, 'Pessoa já cadastrada: ' + dados.pessoa.nome_completo + '. Dados carregados — edite o que precisar antes de salvar.');
            })
            .catch(function () {
                if (consulta !== consultaAtual || cpfInput.value.replace(/\D/g, '') !== cpf) return;
                feedback.mostrar(regiao, 'Não foi possível consultar o CPF. Tente novamente ou continue preenchendo o cadastro.', true);
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

});
