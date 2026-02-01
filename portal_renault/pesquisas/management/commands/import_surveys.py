import pandas as pd
from django.core.management.base import BaseCommand
from pesquisas.models import SurveyResponse

class Command(BaseCommand):
    help = 'Importa pesquisas pulando linhas com erro de formatação'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_path = kwargs['csv_file']
        self.stdout.write(f"📂 Lendo arquivo: {csv_path}...")

        try:
            # Tenta ler o CSV forçando vírgula e pulando linhas ruins
            # on_bad_lines='skip' -> Ignora linhas que têm mais colunas que o cabeçalho
            df = pd.read_csv(
                csv_path, 
                sep=',',             # Força separador vírgula (mais comum)
                on_bad_lines='skip', # A MÁGICA: Pula a linha 3 que está travando
                engine='python', 
                encoding='utf-8-sig'
            )
            
            # Limpa espaços em branco nos nomes das colunas
            df.columns = df.columns.str.strip()

            print(f"📊 Linhas lidas com sucesso: {len(df)}")
            if 'source' in df.columns:
                print(f"🏷️  Tipos encontrados: {df['source'].unique()}")

            # Limpa o banco antigo
            deleted, _ = SurveyResponse.objects.all().delete()
            print(f"🗑️  Banco limpo: {deleted} registros antigos apagados.")
            
            # Mapeamento de colunas
            col_geral = "Pontuação geral"
            col_entrega = "Entrega do veículo - satisfação com a entrega"
            col_consultor = next((c for c in df.columns if "competência do consultor de vendas" in c), None)

            objs = []
            for index, row in df.iterrows():
                
                # Função para converter notas com segurança
                def get_score(col_name):
                    if not col_name or col_name not in row: return None
                    val = row[col_name]
                    try:
                        return int(float(val))
                    except:
                        return None

                # Tenta pegar a data
                try:
                    dt = pd.to_datetime(row.get('Response Date'), dayfirst=True, errors='coerce').date()
                except:
                    dt = None

                # Limpeza do ID da loja
                loja_raw = str(row.get('ID localização por marca', ''))
                loja_clean = loja_raw.strip().lstrip('0').rstrip('R')

                objs.append(SurveyResponse(
                    source=row.get('source', 'Indefinido'),
                    date=dt,
                    location_name=loja_clean,
                    customer_name=str(row.get('Review author', '')),
                    model=str(row.get('Model', '')),
                    
                    score_general=get_score(col_geral),
                    score_delivery=get_score(col_entrega),
                    score_consultant=get_score(col_consultor),
                    
                    comment=str(row.get('Comentário', ''))
                ))

            # Salva no banco
            SurveyResponse.objects.bulk_create(objs)
            self.stdout.write(self.style.SUCCESS(f'✅ SUCESSO! {len(objs)} pesquisas importadas.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro crítico: {e}"))
            # Se der erro mesmo assim, tenta imprimir o erro detalhado
            import traceback
            traceback.print_exc()