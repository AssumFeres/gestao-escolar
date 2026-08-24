"""
pessoas/forms.py

Form de entrada para a Template View de cadastro. Espelha os campos
do CadastrarPessoaInputSerializer (API), mas é usado pela interface HTML.
"""

from django import forms


class CadastrarPessoaForm(forms.Form):
    TIPO_VINCULO_CHOICES = [
        ('DISCENTE', 'Discente'),
        ('DOCENTE', 'Docente'),
        ('GESTAO', 'Gestao'),
    ]

    nome_completo = forms.CharField(max_length=200, label="Nome completo")
    cpf = forms.CharField(max_length=11, label="CPF")
    data_nascimento = forms.DateField(
        label="Data de nascimento", widget=forms.DateInput(attrs={'type': 'date'})
    )
    email = forms.EmailField(label="E-mail")
    telefone = forms.CharField(max_length=20, label="Telefone")

    endereco_cep = forms.CharField(max_length=8, label="CEP")
    endereco_logradouro = forms.CharField(max_length=200, label="Logradouro")
    endereco_numero = forms.CharField(max_length=10, label="Numero")
    endereco_complemento = forms.CharField(max_length=100, required=False, label="Complemento")
    endereco_bairro = forms.CharField(max_length=100, label="Bairro")
    endereco_cidade = forms.CharField(max_length=100, label="Cidade")
    endereco_uf = forms.CharField(max_length=2, label="UF")

    tipo_vinculo = forms.ChoiceField(choices=TIPO_VINCULO_CHOICES, label="Tipo de vinculo")
    data_inicio = forms.DateField(
        label="Data de inicio do vinculo", widget=forms.DateInput(attrs={'type': 'date'})
    )
    situacao = forms.CharField(max_length=30, initial="ATIVO", label="Situacao")
    numero_matricula = forms.CharField(
        max_length=20, required=False, label="Numero de matricula (somente Discente)"
    )

