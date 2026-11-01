document.addEventListener('DOMContentLoaded', function () {
    const cepInput = document.getElementById('id_endereco_cep');
    if (!cepInput) return;

    cepInput.addEventListener('blur', function () {
        const cep = cepInput.value.replace(/\D/g, '');

        if (cep.length !== 8) {
            return;
        }

        fetch(`/api/cadastros/cep/${cep}/`)
            .then(function (response) {
                if (!response.ok) {
                    throw new Error('CEP nao encontrado');
                }
                return response.json();
            })
            .then(function (data) {
                document.getElementById('id_endereco_logradouro').value = data.logradouro;
                document.getElementById('id_endereco_bairro').value = data.bairro;
                document.getElementById('id_endereco_cidade').value = data.cidade;
                document.getElementById('id_endereco_uf').value = data.uf;
            })
            .catch(function () {
                console.warn('Nao foi possivel buscar o endereco para este CEP.');
            });
    });
});
