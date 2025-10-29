# core/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import CustomUser, RelatorioDesempenho

# =============================================================================
# FORMULÁRIOS DE USUÁRIOS
# =============================================================================

class CustomUserCreationForm(UserCreationForm):
    """Formulário de criação de usuário customizado (CORRIGIDO)"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu e-mail'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='Nome',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Sobrenome',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu sobrenome'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def clean_email(self):
        """
        Validação extra para garantir que o email não esteja em uso.
        Permite uma mensagem de erro mais clara do que a padrão.
        """
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Este endereço de e-mail já está em uso. Por favor, utilize outro."
            )
        return email

class CustomAuthenticationForm(AuthenticationForm):
    """Formulário de autenticação customizado (CORRIGIDO)"""
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


class UserProfileForm(forms.ModelForm):
    """Formulário de perfil do usuário (ATUALIZADO)"""
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
    # NOVO CAMPO ADICIONADO
    username = forms.CharField(
        max_length=150,
        required=True,
        label='Nome de usuário',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        # ADICIONADO 'username' À LISTA DE CAMPOS
        fields = ['username', 'first_name', 'last_name', 'email']

    # =====================================================================
    #  NOVO MÉTODO DE VALIDAÇÃO INTELIGENTE
    # =====================================================================
    def clean_username(self):
        """
        Verifica se o nome de usuário já existe, mas permite que o usuário
        mantenha seu próprio nome de usuário atual.
        """
        username = self.cleaned_data.get('username')
        
        # Compara o novo username com o que já está no banco para este usuário.
        # self.instance.pk se refere ao ID do usuário que está sendo editado.
        # Se o username existe E pertence a um usuário DIFERENTE, então acusa o erro.
        if CustomUser.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Um usuário com este nome de usuário já existe.")
            
        return username

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
        fields = ['titulo', 'relato']