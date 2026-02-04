from django.shortcuts import render
from django.db.models import Count, Avg, Case, When
from django.db.models.functions import TruncMonth
from .models import SurveyResponse
import json
import datetime
import pandas as pd
import os

# --- FUNÇÃO AUXILIAR DE CÁLCULO (NPS PADRÃO) ---
def calculate_nps_stats(queryset, score_field):
    valid = queryset.exclude(**{f"{score_field}__isnull": True})
    total = valid.count()
    
    if total == 0:
        return {'nps': 0, 'media': 0, 'total': 0, 'p': 0, 'd': 0, 'p_pct': 0}

    promoters = valid.filter(**{f"{score_field}": 5}).count()
    detractors = valid.filter(**{f"{score_field}__lte": 3}).count()
    avg_val = valid.aggregate(a=Avg(score_field))['a'] or 0
    
    nps = ((promoters - detractors) / total) * 100
    
    return {
        'nps': round(nps, 1),
        'media': round(avg_val, 1),
        'total': total,
        'p': promoters, 
        'd': detractors,
        'p_pct': round((promoters/total)*100, 1),
    }

# --- 1. PÁGINA: VISÃO GERAL (Estratégico/Ranking/Gráficos) ---
def visao_geral(request):
    current_source = request.GET.get('source', 'Sales')
    hoje = datetime.date.today()
    
    # --- DEFINIÇÃO DO QS (Resolve o NameError) ---
    qs = SurveyResponse.objects.filter(
        source=current_source, 
        date__lte=hoje
    ).exclude(date__isnull=True)

    # 1. KPIs de Topo (Acumulado Total)
    stats_geral = calculate_nps_stats(qs, 'score_general')
    stats_delivery = calculate_nps_stats(qs, 'score_delivery')
    stats_consultant = calculate_nps_stats(qs, 'score_consultant')
    
    # Cálculo Ponderado Renault (50% Geral, 25% Entrega, 25% Consultor)
    nps_index_total = (0.5 * stats_geral['nps']) + (0.25 * stats_delivery['nps']) + (0.25 * stats_consultant['nps'])

    # 2. Agrupamento para o Ranking (Resolve o FieldError)
    lojas_stats = qs.values('location_name').annotate(
        media=Avg('score_general'),
        total=Count('id')
    ).filter(total__gte=1)

    # 3. Lógica do PROCX (Excel: Coluna D -> Retorna Coluna F)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho_excel = os.path.join(base_dir, 'Lista de E-mails da Rede.xlsx')
    
    ranking_final = []
    try:
        # 1. Carrega a planilha (D=3, F=5)
        df_rede = pd.read_excel(caminho_excel, sheet_name='Lista de Concessionárias', usecols=[3, 5])
        df_rede.columns = ['id_planilha', 'nome_oficial']
        
        # 2. Padronização Crítica:
        # Convertemos para string, removemos espaços e garantimos que 
        # o Python não se perca com números decimais (.0) que o Excel às vezes cria
        df_rede['id_planilha'] = df_rede['id_planilha'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        
        df_ranking = pd.DataFrame(list(lojas_stats))
        
        if not df_ranking.empty:
            # Padroniza o ID que vem do banco de dados também
            df_ranking['location_name'] = df_ranking['location_name'].astype(str).str.strip()

            # 3. O Merge (O "PROCX" que agora vai casar)
            df_final = pd.merge(
                df_ranking, 
                df_rede, 
                left_on='location_name', 
                right_on='id_planilha', 
                how='left'
            )
            
            # 4. Fallback: Se não achou na planilha (NaN), mostra o ID original
            df_final['nome_exibicao'] = df_final['nome_oficial'].fillna(df_final['location_name'])
            
            # Ordenar pela média e transformar em dicionário para o Django
            ranking_final = df_final.sort_values(by='media', ascending=False).to_dict('records')
            
    except Exception as e:
        print(f"Erro Crítico no PROCX: {e}")
        ranking_final = list(lojas_stats.order_by('-media'))

    # 4. Dados para o Gráfico de Evolução (Linha)
    evolution_qs = qs.annotate(month_date=TruncMonth('date')).values('month_date').annotate(
        total=Count('id'),
        p_gen=Count(Case(When(score_general=5, then=1))),
        d_gen=Count(Case(When(score_general__lte=3, then=1))),
        p_del=Count(Case(When(score_delivery=5, then=1))),
        d_del=Count(Case(When(score_delivery__lte=3, then=1))),
        p_con=Count(Case(When(score_consultant=5, then=1))),
        d_con=Count(Case(When(score_consultant__lte=3, then=1)))
    ).order_by('month_date')

    chart_dates, chart_scores = [], []
    for item in evolution_qs:
        chart_dates.append(item['month_date'].strftime('%b/%y'))
        t = item['total']
        if t > 0:
            n_gen = ((item['p_gen'] - item['d_gen']) / t) * 100
            n_del = ((item['p_del'] - item['d_del']) / t) * 100
            n_con = ((item['p_con'] - item['d_con']) / t) * 100
            # Aplica pesos mensais no gráfico
            chart_scores.append(round((0.5 * n_gen) + (0.25 * n_del) + (0.25 * n_con), 2))
        else:
            chart_scores.append(0)

    context = {
        'current_source': current_source,
        'nps_index': round(nps_index_total, 1),
        'stats_geral': stats_geral,
        'stats_delivery': stats_delivery,
        'stats_consultant': stats_consultant,
        'chart_dates': json.dumps(chart_dates),
        'chart_scores': json.dumps(chart_scores),
        'chart_dist_values': json.dumps([
            qs.filter(score_general=1).count(), qs.filter(score_general=2).count(),
            qs.filter(score_general=3).count(), qs.filter(score_general=4).count(),
            qs.filter(score_general=5).count()
        ]),
        'top_lojas': ranking_final[:5],
        'bottom_lojas': ranking_final[::-1][:5],
    }
    return render(request, 'visao_geral.html', context)

# --- 2. PÁGINA: DETALHAMENTO (Lupa/Operacional) ---
def detalhamento_view(request):
    current_source = request.GET.get('source', 'Sales')
    date_str = request.GET.get('date', datetime.date.today().strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        selected_date = datetime.date.today()

    qs_base = SurveyResponse.objects.filter(source=current_source)

    # Cálculo do Dia
    qs_dia = qs_base.filter(date=selected_date)
    stats_dia_gen = calculate_nps_stats(qs_dia, 'score_general')
    stats_dia_del = calculate_nps_stats(qs_dia, 'score_delivery')
    stats_dia_con = calculate_nps_stats(qs_dia, 'score_consultant')
    nps_dia_index = (0.5 * stats_dia_gen['nps']) + (0.25 * stats_dia_del['nps']) + (0.25 * stats_dia_con['nps'])

    # Cálculo do Mês (MTD)
    qs_mes = qs_base.filter(date__year=selected_date.year, date__month=selected_date.month)
    stats_mes_gen = calculate_nps_stats(qs_mes, 'score_general')
    stats_mes_del = calculate_nps_stats(qs_mes, 'score_delivery')
    stats_mes_con = calculate_nps_stats(qs_mes, 'score_consultant')
    nps_mes_index = (0.5 * stats_mes_gen['nps']) + (0.25 * stats_mes_del['nps']) + (0.25 * stats_mes_con['nps'])

    context = {
        'current_source': current_source,
        'selected_date': selected_date.strftime('%Y-%m-%d'),
        'nps_dia_index': round(nps_dia_index, 1),
        'total_dia': qs_dia.count(),
        'nps_mes_index': round(nps_mes_index, 1),
        'total_mes': qs_mes.count(),
        'pesquisas_dia': qs_dia.order_by('-score_general'),
    }
    return render(request, 'detalhamento.html', context)