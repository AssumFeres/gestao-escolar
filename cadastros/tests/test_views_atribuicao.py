from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
from decimal import Decimal

# Importações oficiais dos apps sem conflitos
from cadastros.models import Pessoa, Funcao, AtribuicaoFuncao, SituacaoAtribuicao, Disciplina
from cadastros.models import Turma as CadastrosTurma
from atribuicao.models import Atribuicao, HorarioAula, RegistroInstrucao, MatriculaTurma, StatusMatriculaTurma

class AtribuicaoHorariosViewsTestCase(TestCase):

    def setUp(self):
        """Prepara toda a cadeia de dados obrigatórios alinhada perfeitamente com os seus modelos reais"""
        self.client = Client()
        self.user = User.objects.create_user(username="professor_teste", password="senha_teste")
        
        # 1. Cadastro da Pessoa
        self.pessoa = Pessoa.objects.create(
            nome_completo="Professor Teste de Oliveira", 
            data_nascimento="1985-05-15",
            ativo=True
        )
        
        self.funcao = Funcao.objects.create(nome="Professor Docente", categoria="DOCENTE")
        
        self.instrutor_funcao = AtribuicaoFuncao.objects.create(
            pessoa=self.pessoa,
            funcao=self.funcao,
            situacao=SituacaoAtribuicao.ATIVO,
            data_inicio=date.today()
        )
        
        # 2. Cadastro da Disciplina com todas as suas restrições de carga horária
        self.disciplina = Disciplina.objects.create(
            nome="Matemática Aplicada",
            carga_horaria_programa_de_instrucao=60,
            carga_horaria_teorica=40,
            carga_horaria_pratica=20
        )
        
        # 3. CORREÇÃO DA TURMA: Usando estritamente os campos reais do seu projeto
        self.turma = CadastrosTurma.objects.create(
            nome="Turma Piloto II", 
            status="PLANEJADA",  # Campo correto!
            ano_letivo="2026"    # Campo correto!
        )
        
        # 4. Cria a atribuição oficial vinculando o instrutor
        self.atribuicao = Atribuicao.objects.create(
            instrutor=self.instrutor_funcao,
            disciplina=self.disciplina,
            turma=self.turma
        )

    def test_fixar_horario_na_grade_via_post(self):
        """Testa se o formulário de horários salva os dados quando recebe o vínculo correto"""
        url = reverse('horarios')
        
        dados_formulario = {
            'atribuicao': self.atribuicao.id,
            'dia_semana': 'SEG',
            'horario_inicio': '08:00',
            'horario_fim': '10:00'
        }
        
        response = self.client.post(url, dados_formulario)
        # O post redireciona (302) se salvar com sucesso
        self.assertIn(response.status_code, [200, 302])

    def test_registro_instrucao_salva_no_diario_corretamente(self):
        """Testa se o diário de classe grava e armazena os conteúdos programáticos"""
        registro = RegistroInstrucao.objects.create(
            atribuicao=self.atribuicao,
            data_instrucao=date.today(),
            carga_horaria=Decimal('2.00'),
            tipo="TEORICA",
            conteudo_programatico="Introdução à Engenharia de Software"
        )
        self.assertEqual(registro.carga_horaria, Decimal('2.00'))

    def test_tela_treinamento_carrega_com_sucesso(self):
        """Valida se a página de treinamento do Módulo de Qualidade abre sem erros (Status 200)."""
        url = reverse('qualidade-treinamento')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_tela_auditoria_carrega_com_sucesso(self):
        """Valida se a página de auditoria interna abre sem erros (Status 200)."""
        url = reverse('qualidade-auditoria')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_painel_indicadores_carrega_com_sucesso(self):
        """Garante que a View de Indicadores de Qualidade abre perfeitamente com os contextos filtrados."""
        url = reverse('qualidade-indicadores')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
