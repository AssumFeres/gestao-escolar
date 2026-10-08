import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from cadastros.models import Turma, Modulo, OfertaModulo
from atribuicao.models import Atribuicao, HorarioAula, RegistroInstrucao, Disciplina

@pytest.mark.django_db
class TestAtribuicaoHorariosViews:

    @pytest.fixture
    def setup_dados(self):
        """Prepara toda a cadeia de dados obrigatórios exigida pelas restrições do banco"""
        instrutor = User.objects.create_user(username="professor_teste", password="senha_teste")
        
        # Inserida a Disciplina local correta do app atribuicao
        disciplina = Disciplina.objects.create(
            nome="Matemática Aplicada"
        )
        
        # 1. Cria o Módulo Base usando apenas os campos de texto essenciais
        modulo = Modulo.objects.create(
            nome="Módulo de Tecnologia",
            sigla="TEC",
            ativo=True
        )
        
        # 2. Cria a Oferta de Módulo respeitando a data_inicio e o ano_letivo exigidos pelo banco
        oferta = OfertaModulo.objects.create(
            modulo=modulo,
            ano_letivo=2026,
            data_inicio="2026-02-01",
            ativo=True
        )
        
        # 3. Cria a Turma vinculada obrigatoriamente à Oferta de Módulo
        turma = Turma.objects.create(
            nome="Turma Piloto II", 
            situacao="PLANEJADA",
            oferta_modulo=oferta
        )
        
        # 4. Cria o vínculo mestre de Atribuição que o formulário exige
        atribuicao = Atribuicao.objects.create(
            instrutor=instrutor,
            disciplina=disciplina,
            turma=turma,
            ano_letivo=2026
        )
        return atribuicao

    def test_fixar_horario_na_grade_via_post(self, client, setup_dados):
        """Testa se o formulário de horários salva os dados quando recebe o vínculo correto"""
        atribuicao = setup_dados
        url = reverse('horarios')
        
        dados_formulario = {
            'atribuicao': atribuicao.id,
            'dia_semana': 'SEG',
            'horario_inicio': '08:00',
            'horario_fim': '10:00'
        }
        
        response = client.post(url, dados_formulario)
        assert response.status_code in [200, 302]
        assert HorarioAula.objects.filter(dia_semana='SEG', atribuicao=atribuicao).exists()

    def test_registro_instrucao_lista_dados_corretamente(self, client, setup_dados):
        """Testa se a tela do diário de classe carrega o histórico de aulas do banco"""
        atribuicao = setup_dados
        
        RegistroInstrucao.objects.create(
            instrutor=atribuicao.instrutor,
            atribuicao=atribuicao,
            data_instrucao="2026-10-08",
            carga_horaria=2.00,
            tipo="Teórica",
            conteudo_programatico="Introdução à Engenharia de Software"
        )
        
        url = reverse('registro_instrucao')
        response = client.get(url)
        
        assert response.status_code == 200
        assert "Introdução à Engenharia de Software" in response.content.decode('utf-8')
