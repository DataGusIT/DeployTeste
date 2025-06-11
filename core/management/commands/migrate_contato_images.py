import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Contato

class Command(BaseCommand):
    help = 'Migra as imagens existentes da pasta contatos/ para static/img/ e atualiza os registros do banco de dados'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando migração de imagens...')
        
        # Origem e destino das imagens
        origem_dir = os.path.join(settings.MEDIA_ROOT, 'contatos')
        destino_dir = os.path.join(settings.BASE_DIR, 'static', 'img')
        
        # Cria o diretório de destino se não existir
        if not os.path.exists(destino_dir):
            os.makedirs(destino_dir)
            self.stdout.write(f'Diretório criado: {destino_dir}')
        
        # Verifica se o diretório de origem existe
        if not os.path.exists(origem_dir):
            self.stdout.write(self.style.WARNING('Diretório de origem não encontrado. Continuando apenas com a atualização do banco de dados.'))
        else:
            # Lista todos os contatos com imagens
            contatos = Contato.objects.exclude(imagem='').exclude(imagem__isnull=True)
            self.stdout.write(f'Encontrados {contatos.count()} contatos com imagens para migrar')
            
            # Para cada contato, move a imagem e atualiza o registro
            for contato in contatos:
                try:
                    # Obtém apenas o nome do arquivo da imagem (sem o caminho)
                    nome_arquivo = os.path.basename(contato.imagem.name)
                    
                    # Caminho completo dos arquivos de origem e destino
                    arquivo_origem = os.path.join(settings.MEDIA_ROOT, contato.imagem.name)
                    arquivo_destino = os.path.join(destino_dir, nome_arquivo)
                    
                    # Move o arquivo
                    if os.path.exists(arquivo_origem):
                        shutil.copy2(arquivo_origem, arquivo_destino)
                        self.stdout.write(f'Imagem copiada: {nome_arquivo}')
                        
                        # Atualiza o registro no banco de dados
                        novo_caminho = f'static/img/{nome_arquivo}'
                        contato.imagem = novo_caminho
                        contato.save(update_fields=['imagem'])
                        self.stdout.write(f'Registro atualizado para: {novo_caminho}')
                    else:
                        self.stdout.write(self.style.WARNING(f'Arquivo não encontrado: {arquivo_origem}'))
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Erro ao migrar {contato.nome}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Migração de imagens concluída!'))