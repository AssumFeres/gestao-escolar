document.addEventListener('DOMContentLoaded', function () {
    const cepInput = document.getElementById('id_endereco_cep');
    if (!cepInput) return;
    const regiao = document.getElementById('status-consulta-cep');
    const feedback = window.CadastroFeedback;
    let consultaAtual = 0;
    feedback.associar(cepInput, ['ajuda-consulta-cep', 'status-consulta-cep']);
    cepInput.addEventListener('input', function () {
        consultaAtual++;
        feedback.mostrar(regiao, '');
    });

    cepInput.addEventListener('blur', function () {
        const consulta = ++consultaAtual;
        const cep = cepInput.value.replace(/\D/g, '');

        if (cep.length !== 8) {
            feedback.mostrar(regiao, cep ? 'Informe um CEP com 8 dígitos para consultar o endereço.' : '', true);
            return;
        }

        feedback.mostrar(regiao, 'Consultando o CEP...');
        fetch(`/api/cadastros/cep/${cep}/`)
            .then(function (response) {
                if (!response.ok) {
                    throw new Error(response.status === 404 ? 'nao-encontrado' : 'falha-consulta');
                }
                return response.json();
            })
            .then(function (data) {
                if (consulta !== consultaAtual || cepInput.value.replace(/\D/g, '') !== cep) return;
                document.getElementById('id_endereco_logradouro').value = data.logradouro;
                document.getElementById('id_endereco_bairro').value = data.bairro;
                document.getElementById('id_endereco_cidade').value = data.cidade;
                document.getElementById('id_endereco_uf').value = data.uf;
                feedback.mostrar(regiao, 'Endereço preenchido. Confira os dados e informe o número.');
            })
            .catch(function (erro) {
                if (consulta !== consultaAtual || cepInput.value.replace(/\D/g, '') !== cep) return;
                feedback.mostrar(regiao, erro.message === 'nao-encontrado'
                    ? 'CEP não encontrado. Confira o CEP ou preencha o endereço manualmente.'
                    : 'Não foi possível consultar o CEP. Tente novamente ou preencha o endereço manualmente.', true);
            });
    });
});
