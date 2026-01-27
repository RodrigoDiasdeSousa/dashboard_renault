import pandas as pd

# ===============================
# FUNÇÃO PARA CARREGAR PESQUISAS
# ===============================
def carregar_pesquisas(caminho_csv):
    """
    Lê o CSV de pesquisas, filtra apenas Sales e limpa o ID localização.
    """
    df = pd.read_csv(caminho_csv, encoding="utf-8-sig")
    
    # Filtra apenas Sales
    df_sales = df[df["source"] == "Sales"].copy()
    
    # Limpa ID localização (remove 0 à frente e 'R' no final)
    df_sales["ID localização por marca"] = (
        df_sales["ID localização por marca"]
        .astype(str)
        .str.strip()
        .str.lstrip("0")
        .str.rstrip("R")
    )
    
    return df_sales

# ===============================
# FUNÇÃO PARA CARREGAR BIR/REGIÃO
# ===============================
def carregar_bir_regiao(caminho_excel, aba):
    """
    Lê o Excel da BIR/Região e padroniza ID localização.
    """
    df = pd.read_excel(caminho_excel, sheet_name=aba, header=2)
    df.columns = df.columns.str.strip()  # limpa espaços das colunas

    # Renomeia a coluna do ID para bater com o df_sales
    df = df.rename(columns={"N° BIR - 0": "ID localização por marca"})
    
    # Limpa o ID
    df["ID localização por marca"] = df["ID localização por marca"].astype(str).str.strip()
    
    # Mantém apenas as colunas necessárias
    df = df[["ID localização por marca", "NOME COMERCIAL", "REGIONAL", "GRUPO"]].copy()
    
    return df
