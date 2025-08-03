from django.db import models
from django.contrib.auth.models import User

# =============================================================================
# CATEGORIA BASE (ABSTRATA)
# =============================================================================

class CategoriaBase(models.Model):
    nome = models.CharField(max_length=100)
    icone = models.CharField(max_length=50, blank=True, null=True)
    
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
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

# =============================================================================
# MODELOS RELACIONADOS A DÚVIDAS/FAQ
# =============================================================================

class CategoriaFAQ(CategoriaBase):
    class Meta:
        verbose_name = 'Categoria de Dúvida'
        verbose_name_plural = 'Categorias de Dúvidas'
    
    def get_icone(self):
        icones = {
            'Geral': 'fas fa-info-circle',
            'Diagnóstico': 'fas fa-stethoscope',
            'Tratamento': 'fas fa-heartbeat',
            'Apoio': 'fas fa-hands-helping',
            'Conceitos': 'fas fa-book',
        }
        return icones.get(self.nome, 'fas fa-question-circle')

class FAQ(models.Model):
    categoria = models.ForeignKey(CategoriaFAQ, on_delete=models.CASCADE, related_name='faqs')
    pergunta = models.CharField(max_length=255)
    resposta = models.TextField()
    
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
    imagem = models.ImageField(upload_to='static/img/', blank=True, null=True)    
    
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
    imagem = models.ImageField(upload_to='static/img/contatos/')
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
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    icone_classe = models.CharField(max_length=50, default='fas fa-tools')
    tipo = models.ForeignKey(CategoriaFerramenta, on_delete=models.CASCADE, related_name='ferramentas')
    eh_gratuita = models.BooleanField(default=False)
    classificacao = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    categoria = models.CharField(max_length=100, choices=[
        ('pictogramas_escolares', 'Pictogramas Escolares'),
        ('alfabetizacao', 'Alfabetização'),
        ('brinquedos_brincadeiras', 'Brinquedos e Brincadeiras'),
        ('historias_sociais', 'Histórias Sociais'),
        ('atividades_diversas', 'Atividades Diversas')
    ])
    
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

