from django.shortcuts import render
from django.db.models import Count, Avg
from django.db.models.functions import TruncMonth
from .models import SurveyResponse
import json

def calculate_nps_stats(queryset, score_field):
    """Retorna estatísticas detalhadas do NPS"""
    valid = queryset.exclude(**{f"{score_field}__isnull": True})
    total = valid.count()
    
    if total == 0:
        return {'nps': 0, 'p': 0, 'n': 0, 'd': 0, 'total': 0}

    promoters = valid.filter(**{f"{score_field}": 5}).count()
    neutrals = valid.filter(**{f"{score_field}": 4}).count()
    detractors = valid.filter(**{f"{score_field}__lte": 3}).count()
    
    nps = ((promoters - detractors) / total) * 100
    
    return {
        'nps': round(nps, 1),
        'p': promoters, 
        'n': neutrals, 
        'd': detractors,
        'total': total,
        'p_pct': round((promoters/total)*100, 1), # Porcentagem
        'n_pct': round((neutrals/total)*100, 1),
        'd_pct': round((detractors/total)*100, 1),
    }

def dashboard_view(request):
    current_source = request.GET.get('source', 'Sales')
    
    # Filtra dados principais
    qs = SurveyResponse.objects.filter(source=current_source)
    
    # 1. KPIs Principais
    stats_geral = calculate_nps_stats(qs, 'score_general')
    stats_delivery = calculate_nps_stats(qs, 'score_delivery')
    stats_consultant = calculate_nps_stats(qs, 'score_consultant')
    
    nps_index = (0.5 * stats_geral['nps']) + (0.25 * stats_delivery['nps']) + (0.25 * stats_consultant['nps'])

    # 2. Dados para Gráfico: Evolução Mensal (Últimos 12 meses)
    # Agrupa por mês
    timeline_data = qs.annotate(month=TruncMonth('date')).values('month').annotate(
        avg_score=Avg('score_general'),
        count=Count('id')
    ).order_by('month')
    
    # Prepara listas para o JavaScript
    chart_dates = [x['month'].strftime('%b/%Y') if x['month'] else 'N/D' for x in timeline_data]
    chart_scores = [round(x['avg_score'], 2) if x['avg_score'] else 0 for x in timeline_data]
    chart_counts = [x['count'] for x in timeline_data]

    # 3. Dados para Gráfico: Distribuição de Notas (Geral)
    # Conta quantos 1, 2, 3, 4, 5 existem
    dist_data = qs.values('score_general').annotate(qtd=Count('id')).order_by('score_general')
    dist_map = {1:0, 2:0, 3:0, 4:0, 5:0}
    for item in dist_data:
        if item['score_general'] in dist_map:
            dist_map[item['score_general']] = item['qtd']
            
    chart_dist_values = [dist_map[1], dist_map[2], dist_map[3], dist_map[4], dist_map[5]]

    # 4. Ranking de Lojas (Melhores e Piores)
    # Apenas lojas com pelo menos 3 avaliações para ser justo
    lojas_stats = qs.values('location_name').annotate(
        media=Avg('score_general'),
        total=Count('id')
    ).filter(total__gte=1).order_by('-media')

    top_lojas = lojas_stats[:5]
    bottom_lojas = lojas_stats.reverse()[:5]

    context = {
        'current_source': current_source,
        'nps_index': round(nps_index, 1),
        'stats_geral': stats_geral,
        'stats_delivery': stats_delivery,
        'stats_consultant': stats_consultant,
        
        # Dados Gráficos (convertidos para JSON string segura)
        'chart_dates': json.dumps(chart_dates),
        'chart_scores': json.dumps(chart_scores),
        'chart_counts': json.dumps(chart_counts),
        'chart_dist_values': json.dumps(chart_dist_values),
        
        # Tabelas
        'top_lojas': top_lojas,
        'bottom_lojas': bottom_lojas,
    }
    
    return render(request, 'dashboard.html', context)