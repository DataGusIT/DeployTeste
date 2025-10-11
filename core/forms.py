from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import CustomUser, RelatorioDesempenho

# =============================================================================
# FORMULÁRIOS DE USUÁRIOS
# =============================================================================

class CustomUserCreationForm(UserCreationForm):
    """Formulário de criação de usuário customizado (CORRIGIDO)"""
    # Não precisa redefinir username, password1, e password2.
    # Apenas defina os campos extras que você quer no formulário.
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu e-mail'
        })
    )
    first_name = forms.CharField(
        max_length=150, # O padrão do AbstractUser é 150
        required=True,
        label='Nome',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome'
        })
    )
    last_name = forms.CharField(
        max_length=150, # O padrão do AbstractUser é 150
        required=True,
        label='Sobrenome',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu sobrenome'
        })
    )

    class Meta(UserCreationForm.Meta):
        # Herda da Meta da classe base
        model = CustomUser
        # Adiciona os novos campos à lista de campos existentes
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

class CustomAuthenticationForm(AuthenticationForm):
    """Formulário de autenticação customizado (CORRIGIDO)"""
    # A customização dos widgets está correta.
    username = forms.CharField(
        max_length=100,
        required=True,
        label='Nome de usuário',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome de usuário'
        })
    )
    password = forms.CharField(
        max_length=50,
        required=True,
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sua senha'
        })
    )

    # REMOVA COMPLETAMENTE A CLASSE META DAQUI
    # class Meta:
    #     model = CustomUser
    #     fields = ['username', 'password']

class UserProfileForm(forms.ModelForm):
    """Formulário de perfil do usuário"""
    first_name = forms.CharField(
        max_length=100, 
        required=True, 
        label='Nome', 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=100, 
        required=True, 
        label='Sobrenome', 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']

# =============================================================================
# NOVO FORMULÁRIO: RELATÓRIO DE DESEMPENHO
# =============================================================================

class RelatorioDesempenhoForm(forms.ModelForm):
    titulo = forms.CharField(
        label='Título do Relatório',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ex: Progresso na comunicação social'
        })
    )
    relato = forms.CharField(
        label='Relato Detalhado',
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 8,
            'placeholder': 'Descreva aqui o desempenho, progressos, desafios e atividades realizadas pelo aluno.'
        })
    )

    class Meta:
        model = RelatorioDesempenho
        # O professor e o aluno serão definidos na view, não no formulário
        fields = ['titulo', 'relato']