import pandas as pd
from django.core.management.base import BaseCommand
from pesquisas.models import SurveyResponse
from django.utils.timezone import make_aware
from datetime import datetime

class Command(BaseCommand):
    help = 'Importa dados de pesquisas do CSV da Renault'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Caminho para o arquivo CSV')

    def handle(self, *args, **options):
        file_path = options['csv_file']
        
        try:
            # Lendo o CSV (ajuste o separador se necessário, ex: sep=';')
            df = pd.read_csv(file_path, sep=',')

            # O PULO DO GATO: dayfirst=True impede que 03/01 vire 1 de Março
            df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')

            # Remove linhas onde a data falhou na conversão
            df = df.dropna(subset=['date'])

            count = 0
            for _, row in df.iterrows():
                # Criando ou atualizando o registro no banco
                # Usamos o update_or_create para não duplicar se você rodar o script de novo
                SurveyResponse.objects.update_or_create(
                    # Se você tiver um ID único no CSV, use aqui. 
                    # Se não, deixaremos apenas o create:
                    customer_name=row.get('customer_name'),
                    date=row['date'].date(),
                    defaults={
                        'location_name': row.get('location_name'),
                        'model': row.get('model'),
                        'score_general': row.get('score_general'),
                        'score_delivery': row.get('score_delivery'),
                        'score_consultant': row.get('score_consultant'),
                        'comment': row.get('comment', ''),
                        'source': row.get('source', 'Sales'),
                    }
                )
                count += 1

            self.stdout.write(self.style.SUCCESS(f'Sucesso! {count} pesquisas importadas com datas corrigidas.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro na importação: {e}'))