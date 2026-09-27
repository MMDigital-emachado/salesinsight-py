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


