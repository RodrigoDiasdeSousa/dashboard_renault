import pandas as pd

def calcular_nps(serie_notas: pd.Series) -> float:
    """
    Calcula NPS a partir de notas de 1 a 5
    1–3 = detratores
    4 = neutros
    5 = promotores
    """
    notas = serie_notas.dropna()

    if notas.empty:
        return None

    total = len(notas)
    promotores = (notas == 5).sum()
    detratores = (notas <= 3).sum()

    nps = ((promotores - detratores) / total) * 100
    return round(nps, 2)


def calcular_nps_ponderado(df: pd.DataFrame, colunas_nps: dict, pesos: dict) -> float:
    """
    Calcula o NPS ponderado a partir de múltiplas colunas de NPS e seus pesos.
    
    df: dataframe com os dados
    colunas_nps: dicionário {nome_nps: coluna_df}
    pesos: dicionário {nome_nps: peso_float}
    """
    total = 0
    for key, col in colunas_nps.items():
        nps = calcular_nps(df[col])
        peso = pesos.get(key, 0)
        if nps is not None:
            total += nps * peso
    return round(total, 1)
