# -*- coding: utf-8 -*-
"""
SalesInsight PY — análise e visualização de dados de vendas
Mini-Projeto Avaliativo · Módulo 01 · Semana 08

O script inteiro roda em um único main(): gera o vendas.csv se ele ainda
não existir, passa pelas etapas de limpeza, transformação, agregação e
visualização, e deixa tudo exportado em outputs/.

Escopo: só o que caiu nas semanas 01 a 08. Não tem modelo preditivo aqui.
"""

import os
import re
import json
import random
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# Configuração visual. Escolhi uma paleta quente de propósito, porque as
# cores padrão do matplotlib (aquele azul/verde/laranja de sempre) ficavam
# parecendo exemplo de biblioteca.
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["axes.edgecolor"] = "#9E9E9E"

AZUL = "#1D3557"
VERMELHO = "#E63946"
AMARELO = "#E9C46A"
VERDE = "#2A9D8F"
PALETA = ["#1D3557", "#E63946", "#E9C46A", "#2A9D8F", "#6D597A"]

# Nomes de cliente chegam com varias grafias diferentes no dataset sujo
# ("Cliente_007", "cliente#007", "CLIENTE-007", "  Cliente_007!!").
# Estes dois padroes ficam compilados aqui porque sao usados em varios pontos.
PADRAO_CLIENTE = re.compile(r"^Cliente_\d{3}$")
SO_DIGITOS = re.compile(r"\D+")


# ---------------------------------------------------------------- RF01
def gerar_dataset_vendas(n_registros=200, seed=42):
    """
    Monta um dataset sintetico de vendas e ja Planta a sujeira que a
    etapa de limpeza vai ter que resolver: nulos, data invalida, espacos
    sobrando e nomes de cliente escritos de varias formas.
    """
    random.seed(seed)
    np.random.seed(seed)

    produtos = ["Notebook", "Smartphone", "Tablet", "Monitor",
                "Teclado", "Mouse", "Headset"]
    categorias = {"Notebook": "Computadores", "Smartphone": "Celulares",
                  "Tablet": "Celulares", "Monitor": "Computadores",
                  "Teclado": "Perifericos", "Mouse": "Perifericos",
                  "Headset": "Perifericos"}
    precos = {"Notebook": 3500, "Smartphone": 2200, "Tablet": 1800,
              "Monitor": 1200, "Teclado": 250, "Mouse": 120,
              "Headset": 350}
    regioes = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]

    data_inicio = datetime(2025, 1, 1)
    linhas = []

    for i in range(n_registros):
        produto = random.choice(produtos)
        categoria = categorias[produto]      # pega antes de sujar o nome
        quantidade = random.randint(1, 10)
        preco = round(precos[produto] * random.uniform(0.85, 1.15), 2)
        dia = data_inicio + timedelta(days=random.randint(0, 364))
        cliente = f"Cliente_{random.randint(1, 50):03d}"

        if random.random() < 0.05:
            quantidade = None
        if random.random() < 0.04:
            preco = None
        if random.random() < 0.06:
            produto = f"  {produto} "          # espaço sobrando
        if random.random() < 0.03:
            dia = None
        if random.random() < 0.10:                # nome com separador trocado
            cliente = random.choice([
                cliente.upper().replace("_", "-"),   # CLIENTE-007
                cliente + "!!",                        # Cliente_007!!
                f"  {cliente}",                        # espaço nas pontas
                cliente.replace("Cliente_", "cliente#"),  # cliente#007
            ])

        linhas.append({
            "id_venda": i + 1,
            "data_venda": dia.strftime("%Y-%m-%d") if dia else "DATA INVALIDA",
            "cliente": cliente,
            "produto": produto,
            "categoria": categoria,
            "regiao": random.choice(regioes),
            "quantidade": quantidade,
            "preco_unitario": preco,
        })

    return pd.DataFrame(linhas)


# ---------------------------------------------------------------- RF02
def inspecionar_dados(df):
    """Mostra o estado do dataset antes de qualquer tratamento."""
    print("\n=== INSPEÇÃO INICIAL DO DATASET ===")
    print(f"Shape: {df.shape}")
    print(f"\nColunas: {list(df.columns)}")
    print(f"\nTipos de dados:\n{df.dtypes}")
    print(f"\nValores nulos por coluna:\n{df.isnull().sum()}")
    print(f"\nPrimeiros registros:\n{df.head()}")


# ---------------------------------------------------------------- RF03
def normalizar_cliente(nome):
    """
    Deixa todo nome de cliente no formato Cliente_NNN.

    Em vez de tentar apagar os caracteres esquisitos um a um, eu pego só
    os dígitos e remonto o nome. Funciona para as quatro variações que o
    gerador produz e evita que o mesmo cliente acabe entrando duas vezes
    na segmentação (ex.: "cliente#016" viraria "CLIENTE016" e contaria
    separado do "Cliente_016").
    """
    digitos = SO_DIGITOS.sub("", str(nome))
    if digitos:
        return f"Cliente_{int(digitos):03d}"
    return str(nome).strip()


def limpar_dados(df):
    """
    Trata o dataset e devolve (df_limpo, relatorio).

    O relatorio guarda quantas linhas entraram, quantas saíram em cada
    etapa e quantas sobraram, para dar print no console.
    """
    inicial = len(df)
    removidos = {}

    # espaço sobrando nas colunas de texto
    for col in ["cliente", "produto", "categoria", "regiao"]:
        df[col] = df[col].astype(str).str.strip()

    # data: o que não converter vira NaT e sai na hora
    df["data_venda"] = pd.to_datetime(df["data_venda"], errors="coerce")
    antes = len(df)
    df = df.dropna(subset=["data_venda"])
    removidos["datas invalidas"] = antes - len(df)

    # sem quantidade ou preço não dá para calcular receita
    antes = len(df)
    df = df.dropna(subset=["quantidade", "preco_unitario"])
    removidos["nulos em quantidade/preco"] = antes - len(df)

    df["quantidade"] = df["quantidade"].astype(int)
    df["preco_unitario"] = df["preco_unitario"].astype(float)

    # nomes de cliente fora do padrao são normalizados, não descartados
    antes = int((~df["cliente"].str.match(PADRAO_CLIENTE)).sum())
    df["cliente"] = df["cliente"].apply(normalizar_cliente)
    removidos["nomes de cliente normalizados"] = antes

    relatorio = {
        "registros_iniciais": inicial,
        "ajustes na limpeza": removidos,
        "registros_finais": len(df),
    }

    print("\n=== RELATÓRIO DE LIMPEZA ===")
    print(f"Registros iniciais: {inicial}")
    for motivo, qtd in removidos.items():
        print(f"  {motivo}: {qtd}")
    print(f"Registros finais: {len(df)}")
    return df, relatorio


# ---------------------------------------------------------------- RF04
def criar_colunas_derivadas(df):
    """Cria receita, mês/trimestre/ano e a faixa de receita do item."""
    df["receita_total"] = df["quantidade"] * df["preco_unitario"]
    df["mes"] = df["data_venda"].dt.month
    df["trimestre"] = "Q" + df["data_venda"].dt.quarter.astype(str)
    df["ano"] = df["data_venda"].dt.year
    df["mes_nome"] = df["mes"].map({
        1: "Janeiro", 2: "Fevereiro", 3: "Marco", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
    })

    # np.select em vez de laço com if: resolve as três faixas de uma vez,
    # já que são condições vetoriais, não um caso por linha
    condicoes = [
        df["receita_total"] < 500,
        (df["receita_total"] >= 500) & (df["receita_total"] < 5000),
        df["receita_total"] >= 5000,
    ]
    df["faixa_receita_item"] = np.select(
        condicoes, ["Baixo Valor", "Medio Valor", "Alto Valor"],
        default="Nao Classificado",
    )
    return df


# ---------------------------------------------------------------- RF05
def calcular_metricas(df):
    """Agrega o dataset por mês, produto, categoria e região."""
    por_mes = (df.groupby("mes")
                 .agg(receita_total=("receita_total", "sum"),
                      quantidade=("quantidade", "sum"),
                      n_vendas=("id_venda", "count"))
                 .reset_index()
                 .sort_values("mes"))

    top_produtos = (df.groupby("produto")
                      .agg(receita_total=("receita_total", "sum"))
                      .reset_index()
                      .sort_values("receita_total", ascending=False)
                      .head(5))

    por_categoria = (df.groupby("categoria")
                       .agg(receita_total=("receita_total", "sum"))
                       .reset_index()
                       .sort_values("receita_total", ascending=False))

    por_regiao = (df.groupby("regiao")
                    .agg(receita_total=("receita_total", "sum"),
                         n_vendas=("id_venda", "count"))
                    .reset_index())
    por_regiao["ticket_medio"] = (por_regiao["receita_total"]
                                  / por_regiao["n_vendas"])

    metricas = {
        "por_mes": por_mes,
        "top_produtos": top_produtos,
        "por_categoria": por_categoria,
        "por_regiao": por_regiao,
    }

    print("\n=== POR MÊS ===")
    print(por_mes.to_string(index=False))
    print("\n=== TOP PRODUTOS ===")
    print(top_produtos.to_string(index=False))
    print("\n=== POR CATEGORIA ===")
    print(por_categoria.to_string(index=False))
    print("\n=== POR REGIÃO ===")
    print(por_regiao.to_string(index=False))
    return metricas


