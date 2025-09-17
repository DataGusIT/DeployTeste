from django.db import models
from django.contrib.auth.models import User


# =============================================================================
# LISTA DE ÍCONES PREDEFINIDOS PARA O ADMIN
# Formato: (valor_no_banco, 'Rótulo no Admin')
# =============================================================================
ICON_CHOICES = [
    # Ícones para FAQ
    ('fas fa-book-open', 'Livro Aberto (Definições, Contexto)'),
    ('fas fa-stethoscope', 'Estetoscópio (Diagnóstico, Tratamento)'),
    ('fas fa-gavel', 'Martelo (Legislação, Direitos)'),
    ('fas fa-graduation-cap', 'Chapéu de Formatura (Educação)'),
    ('fas fa-comment-medical', 'Balão de Fala (Terapias)'),
    
    # Ícones para Contatos
    ('fas fa-hands-helping', 'Mãos Ajudando (Apoio, ONGs)'),
    ('fas fa-clinic-medical', 'Clínica (Clínicas, Hospitais)'),
    ('fas fa-user-md', 'Médico (Profissionais de Saúde)'),
    ('fas fa-users', 'Grupo de Pessoas (Grupos de Apoio)'),
    ('fas fa-building-ngo', 'Prédio (Associações)'),

    # Ícones Gerais
    ('fas fa-info-circle', 'Círculo de Informação (Geral)'),
    ('fas fa-question-circle', 'Círculo de Interrogação (Padrão)'),
    ('fas fa-tools', 'Ferramentas (Ferramentas)'),
]

# =============================================================================
# CATEGORIA BASE (ABSTRATA)
# =============================================================================

class CategoriaBase(models.Model):
    nome = models.CharField(max_length=100)
    # AGORA UM CAMPO DE ESCOLHA!
    icone = models.CharField(
        max_length=50, 
        choices=ICON_CHOICES, # Usa a lista de ícones como opções
        default='fas fa-question-circle', # Ícone padrão
        verbose_name='Ícone'
    )
    
    class Meta:
        abstract = True
        
    def __str__(self):
        return self.nome
        
    def nome_slug(self):
        return self.nome.lower().replace(" ", "-")

# =============================================================================
# MODELOS RELACIONADOS A USUÁRIOS
# =============================================================================

class CustomUser(User):
    # Campos adicionais
    is_admin = models.BooleanField(default=False)
    # MODIFICAÇÃO: Adicionado campo para identificar professores
    is_professor = models.BooleanField('É professor?', default=False)
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

# =============================================================================
# NOVOS MODELOS: ALUNO E RELATÓRIO DE DESEMPENHO
# =============================================================================
# NOVA CLASSE PARA AS TURMAS
class Turma(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name='Nome da Turma')
    
    class Meta:
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'
        ordering = ['nome']

    def __str__(self):
        return self.nome
    
class Aluno(models.Model):
    # NÍVEIS DE SUPORTE (BASEADO NO DSM-5)
    NIVEL_AUTISMO_CHOICES = [
        (1, 'Nível 1 - Exige apoio'),
        (2, 'Nível 2 - Exige apoio substancial'),
        (3, 'Nível 3 - Exige apoio muito substancial'),
    ]

    nome_completo = models.CharField(max_length=255, verbose_name='Nome Completo do Aluno')
    data_nascimento = models.DateField(verbose_name='Data de Nascimento')
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')
    
    turma = models.ForeignKey(
        Turma, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='alunos', 
        verbose_name='Turma Regular'
    )
    
    # NOVO CAMPO: NÍVEL DE AUTISMO
    nivel_autismo = models.IntegerField(
        choices=NIVEL_AUTISMO_CHOICES,
        null=True,
        blank=True, # Torna o campo opcional
        verbose_name='Nível de Suporte (Autismo)'
    )

    # NOVO CAMPO: LAUDO
    laudo_url = models.URLField(
        max_length=1024,
        blank=True,
        null=True,
        verbose_name='Laudo (URL do Arquivo)'
    )
    
    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'
        ordering = ['nome_completo']

    def __str__(self):
        return self.nome_completo

class RelatorioDesempenho(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='relatorios', verbose_name='Aluno')
    # MODIFICAÇÃO: Usamos CustomUser para referenciar o professor
    professor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='relatorios_criados', verbose_name='Professor')
    titulo = models.CharField(max_length=200, verbose_name='Título do Relatório')
    relato = models.TextField(verbose_name='Relato de Desempenho')
    data_relatorio = models.DateTimeField(auto_now_add=True, verbose_name='Data do Relatório')
    
    class Meta:
        verbose_name = 'Relatório de Desempenho'
        verbose_name_plural = 'Relatórios de Desempenho'
        ordering = ['-data_relatorio']

    def __str__(self):
        return f"Relatório para {self.aluno.nome_completo} em {self.data_relatorio.strftime('%d/%m/%Y')}"


# =============================================================================
# MODELOS RELACIONADOS A DÚVIDAS/FAQ
# =============================================================================

class CategoriaFAQ(CategoriaBase):
    class Meta:
        verbose_name = 'Categoria de Dúvida'
        verbose_name_plural = 'Categorias de Dúvidas'

class FAQ(models.Model):
    categoria = models.ForeignKey(CategoriaFAQ, on_delete=models.CASCADE, related_name='faqs')
    pergunta = models.CharField(max_length=255)
    resposta = models.TextField()
    fonte = models.URLField(max_length=255, blank=True, null=True, verbose_name='Fonte')

    def __str__(self):
        return self.pergunta

class UserSavedFAQ(models.Model):
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE, 
        related_name='saved_faqs',
        verbose_name='Usuário'
    )
    faq = models.ForeignKey(
        'FAQ', 
        on_delete=models.CASCADE, 
        related_name='saved_by_users',
        verbose_name='Dúvida Frequente'
    )
    data_salva = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Salvamento'
    )
    
    def __str__(self):
        return f"{self.user.username} - {self.faq.pergunta[:50]}..."
    
    class Meta:
        verbose_name = 'Dúvida Salva'
        verbose_name_plural = 'Dúvidas Salvas'
        ordering = ['-data_salva']
        unique_together = ['user', 'faq']  # Evita duplicatas
        indexes = [
            models.Index(fields=['user', '-data_salva']),
            models.Index(fields=['faq']),
        ]

# =============================================================================
# MODELOS RELACIONADOS A CONTATOS
# =============================================================================

class CategoriaContato(CategoriaBase):
    class Meta:
        verbose_name = 'Categoria de Contato'
        verbose_name_plural = 'Categorias de Contatos'


class Contato(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    imagem_url = models.URLField(max_length=1024, blank=True, null=True, verbose_name="URL da Imagem")
    
    # Campos de endereço
    rua = models.CharField(max_length=200, blank=True, null=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=50)
    cep = models.CharField(max_length=9, blank=True, null=True)
    
    # Contato
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    site = models.URLField(blank=True, null=True)
    horario_funcionamento = models.CharField(max_length=100)
    
    # Redes sociais
    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True, help_text="Número com código do país (ex: 5511999999999)")
    linkedin = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)
    
    # Galeria de fotos - será uma relação com outro modelo
    categoria = models.ForeignKey(CategoriaContato, on_delete=models.CASCADE, related_name='contatos', null=True, blank=True)
    atendimento_presencial = models.BooleanField(default=True)
    atendimento_online = models.BooleanField(default=False)
    
    # Campos adicionais para melhor experiência
    especialidades = models.TextField(blank=True, null=True, help_text="Liste as especialidades separadas por vírgula")
    convenios = models.TextField(blank=True, null=True, help_text="Convênios aceitos")
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome
    
    def endereco_completo(self):
        """Retorna o endereço completo formatado"""
        endereco = []
        if self.rua:
            endereco.append(f"{self.rua}")
            if self.numero:
                endereco[-1] += f", {self.numero}"
        if self.complemento:
            endereco.append(self.complemento)
        if self.bairro:
            endereco.append(self.bairro)
        endereco.append(f"{self.cidade}, {self.estado}")
        if self.cep:
            endereco.append(f"CEP: {self.cep}")
        return " - ".join(endereco)
    
    def endereco_para_maps(self):
        """Retorna endereço formatado para Google Maps"""
        endereco_parts = []
        if self.rua:
            endereco_parts.append(self.rua)
            if self.numero:
                endereco_parts.append(self.numero)
        if self.bairro:
            endereco_parts.append(self.bairro)
        endereco_parts.extend([self.cidade, self.estado])
        return ", ".join(endereco_parts)

    class Meta:
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'
    
class UserSavedContato(models.Model):
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE, 
        related_name='saved_contatos',
        verbose_name='Usuário'
    )
    contato = models.ForeignKey(
        'Contato', 
        on_delete=models.CASCADE, 
        related_name='saved_by_users',
        verbose_name='Contato'
    )
    data_salva = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Salvamento'
    )
    
    def __str__(self):
        return f"{self.user.username} - {self.contato.nome}"
    
    class Meta:
        verbose_name = 'Contato Salvo'
        verbose_name_plural = 'Contatos Salvos'
        ordering = ['-data_salva']
        unique_together = ['user', 'contato']  # Evita duplicatas
        indexes = [
            models.Index(fields=['user', '-data_salva']),
            models.Index(fields=['contato']),
        ]
    

# Modelo para galeria de fotos do contato
class FotoContato(models.Model):
    contato = models.ForeignKey(Contato, on_delete=models.CASCADE, related_name='fotos')
    imagem_url = models.URLField(max_length=1024, blank=True, null=True, verbose_name="URL da Imagem")
    legenda = models.CharField(max_length=200, blank=True, null=True)
    ordem = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['ordem']
        verbose_name = 'Foto do Contato'
        verbose_name_plural = 'Fotos dos Contatos'

# =============================================================================
# MODELOS RELACIONADOS A FERRAMENTAS
# =============================================================================

class CategoriaFerramenta(CategoriaBase):
    class Meta:
        verbose_name = 'Categoria de Ferramenta'
        verbose_name_plural = 'Categorias de Ferramentas'

class Ferramenta(models.Model):
    # OPÇÕES PARA O NOVO CAMPO 'PUBLICO_ALVO'
    PUBLICO_CHOICES = [
        ('pais_familiares', 'Pais e Familiares'),
        ('professores', 'Professores'),
        ('terapeutas', 'Terapeutas'),
        ('criancas_jovens', 'Crianças e Jovens'),
        ('todos', 'Todos os Públicos'),
    ]

    # --- CAMPOS EXISTENTES ---
    nome = models.CharField(max_length=200, verbose_name="Nome da Ferramenta")
    descricao = models.TextField(verbose_name="Descrição")
    icone_classe = models.CharField(max_length=50, default='fas fa-tools', verbose_name="Ícone (Classe Font Awesome)")
    categoria = models.ForeignKey(CategoriaFerramenta, on_delete=models.CASCADE, related_name='ferramentas')
    eh_gratuita = models.BooleanField(default=True, verbose_name="É Gratuita?")
    classificacao = models.DecimalField(max_digits=3, decimal_places=1, default=0.0, verbose_name="Classificação (0.0 a 5.0)")
    apenas_para_professores = models.BooleanField('Apenas para professores?', default=False)
    
    # --- NOVOS CAMPOS ---
    imagem_capa_url = models.URLField(
        max_length=1024,
        blank=True,
        null=True,
        verbose_name="URL da Imagem de Capa"
    )
    
    arquivo_pdf_url = models.URLField(
        max_length=1024,
        blank=True,
        null=True,
        verbose_name="URL do Arquivo PDF"
    )

    publico_alvo = models.CharField(
        max_length=50,
        choices=PUBLICO_CHOICES,
        blank=True,
        null=True,
        verbose_name="Público-Alvo"
    )

    habilidades_desenvolvidas = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Habilidades Desenvolvidas",
        help_text="Ex: Comunicação, Interação Social, Coordenação Motora"
    )

    autor = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Autor/Fonte"
    )
    
    def __str__(self):
        return self.nome


class UserDownload(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='downloads')
    ferramenta = models.ForeignKey(Ferramenta, on_delete=models.CASCADE)
    data_download = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.ferramenta.nome} - {self.data_download.strftime('%d/%m/%Y %H:%M')}"
    
    class Meta:
        verbose_name = 'Download'
        verbose_name_plural = 'Downloads'
        ordering = ['-data_download']