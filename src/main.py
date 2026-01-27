import pandas as pd
from src.load_data import carregar_pesquisas, carregar_bir_regiao
from src.nps import calcular_nps_ponderado, calcular_nps

# ===============================
# CAMINHOS
# ===============================
CAMINHO_PESQUISAS = r"C:\Users\pm27676\OneDrive - Alliance\Área de Trabalho\Dash_py\data\pesquisas.csv"
CAMINHO_REGIAO = r"C:\Users\pm27676\OneDrive - Alliance\Área de Trabalho\Dash_py\data\Lista de E-mails da Rede.xlsx"
ABA_REGIAO = "Lista de Concessionárias"

# ===============================
# CARREGAR DADOS
# ===============================
df_sales = carregar_pesquisas(CAMINHO_PESQUISAS)
df_regiao = carregar_bir_regiao(CAMINHO_REGIAO, ABA_REGIAO)

# ===============================
# MERGE PARA PEGAR REGIONAL
# ===============================
df_sales = df_sales.merge(
    df_regiao[["ID localização por marca", "REGIONAL", "NOME COMERCIAL"]],
    on="ID localização por marca",
    how="left"
)

# ===============================
# VALIDAÇÃO DO MERGE
# ===============================
ids_sem_match = df_sales[df_sales["REGIONAL"].isna()]["ID localização por marca"].tolist()
if ids_sem_match:
    print("IDs sem match:", ids_sem_match)

# ===============================
# DEFINIÇÃO DAS COLUNAS DE NPS E PESOS
# ===============================
colunas_nps = {
    "geral": "Pontuação geral",
    "consultor": (
        "O quanto você está satisfeito com a competência do consultor de vendas?\n"
        "Clique nas estrelas para indicar sua classificação (1 estrela = Muito insatisfeito, 5 estrelas = Muito satisfeito)"
    ),
    "entrega": "Entrega do veículo - satisfação com a entrega"
}

pesos = {"geral": 0.5, "consultor": 0.25, "entrega": 0.25}

# ===============================
# NPS FINAL PONDERADO
# ===============================
nps_final = calcular_nps_ponderado(df_sales, colunas_nps, pesos)
print("\nNPS FINAL PONDERADO (todas as Sales):", nps_final)

# ===============================
# NPS POR REGIONAL
# ===============================
print("\nRESUMO NPS POR REGIONAL:")
for regiao, grupo in df_sales.groupby("REGIONAL"):
    if pd.isna(regiao):
        continue
    nps_regiao = calcular_nps_ponderado(grupo, colunas_nps, pesos)
    print(f"{regiao}: {nps_regiao}")

# ===============================
# RESUMO FINAL
# ===============================
print("\nNúmero total de registros Sales:", df_sales.shape[0])
print("Número de registros com REGIONAL ausente:", len(ids_sem_match))
