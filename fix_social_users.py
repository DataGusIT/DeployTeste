# fix_social_users.py
import os
import django

# Configura o ambiente do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centroespectro.settings')
django.setup()

# Importa os modelos necessários
from django.contrib.auth.models import User
from core.models import CustomUser

def fix_users():
    """
    Encontra todos os usuários base (User) que não têm um
    perfil CustomUser correspondente e cria o perfil que falta.
    """
    print("Iniciando verificação de usuários sem CustomUser...")

    # Pega todos os IDs de CustomUser que já existem
    existing_custom_user_ids = CustomUser.objects.values_list('user_ptr_id', flat=True)

    # Encontra os usuários base que NÃO estão na lista de CustomUsers
    # Isso é mais eficiente do que iterar e verificar com hasattr
    users_to_fix = User.objects.exclude(id__in=existing_custom_user_ids)

    if not users_to_fix:
        print("Todos os usuários já têm um perfil CustomUser. Nenhuma ação necessária.")
        return

    print(f"Encontrados {users_to_fix.count()} usuários para corrigir.")

    for user_base in users_to_fix:
        try:
            # Cria a instância CustomUser, ligando-a ao User base existente
            custom = CustomUser(user_ptr_id=user_base.id)

            # Copia todos os campos do modelo base para o modelo filho.
            # Isso garante que username, email, first_name, etc., sejam preservados.
            custom.__dict__.update(user_base.__dict__)

            # Salva a nova instância do CustomUser no banco de dados
            custom.save()
            
            print(f"  - Perfil CustomUser criado com sucesso para '{user_base.username}'.")
        except Exception as e:
            print(f"  - ERRO ao criar CustomUser para '{user_base.username}': {e}")

if __name__ == '__main__':
    fix_users()