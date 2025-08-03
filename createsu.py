import os
import django
from django.contrib.auth import get_user_model

# Configura o ambiente do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centroespectro.settings')
django.setup()

User = get_user_model()

# --------------- MUDE ESSES VALORES ---------------
# O nome de usuário que você quer
ADMIN_USERNAME = 'admin'

# O e-mail que você quer
ADMIN_EMAIL = 'admin@gmail.com'

# A senha que você quer. Use uma senha FORTE e TEMPORÁRIA.
ADMIN_PASSWORD = 'admin1234'  # Mude para uma senha forte e temporária
# ----------------------------------------------------

# Verifica se o usuário já não existe
if not User.objects.filter(username=ADMIN_USERNAME).exists():
    print(f"Criando superusuário: {ADMIN_USERNAME}")
    User.objects.create_superuser(
        username=ADMIN_USERNAME,
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD
    )
    print("Superusuário criado com sucesso!")
else:
    print(f"Superusuário '{ADMIN_USERNAME}' já existe. Nenhuma ação foi tomada.")