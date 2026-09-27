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


# ---------------------------------------------------------------- RF06
def segmentar_clientes(df):
    """Soma o gasto de cada cliente e classifica em Bronze, Prata ou Ouro."""
    gasto = (df.groupby("cliente")["receita_total"]
               .sum()
               .reset_index()
               .rename(columns={"receita_total": "total_gasto"}))

    gasto["segmento"] = gasto["total_gasto"].apply(
        lambda v: "Bronze" if v < 5000 else ("Prata" if v <= 15000 else "Ouro")
    )
    gasto = gasto.sort_values("total_gasto", ascending=False)

    print("\n=== TOP 10 CLIENTES ===")
    print(gasto.head(10).to_string(index=False))
    print("\n=== DISTRIBUIÇÃO POR SEGMENTO ===")
    print(gasto["segmento"].value_counts().to_string())
    return gasto


# ---------------------------------------------------------------- RF07
def calcular_estatisticas_numpy(df):
    """
    Opera direto sobre o array de receita_total, sem laço for em cima dele.
    Inclui o detalhe do ddof: np.std() usa ddof=0 e pandas .std() usa ddof=1,
    então os dois números não batem na última casa e isso é esperado.
    """
    receitas = df["receita_total"].to_numpy()

    media = np.mean(receitas)
    acima_da_media = receitas[receitas > media]      # filtragem booleana
    # broadcasting: subtrai o menor e divide pela amplitude, tudo de uma vez
    receitas_norm = (receitas - receitas.min()) / (receitas.max() - receitas.min())

    estatisticas = {
        "media": media,
        "mediana": np.median(receitas),
        "desvio_padrao": np.std(receitas),
        "soma_receitas": np.sum(receitas),
        "minimo": np.min(receitas),
        "maximo": np.max(receitas),
        "vendas_acima_da_media": int(acima_da_media.size),
        "normalizado_min": float(receitas_norm.min()),
        "normalizado_max": float(receitas_norm.max()),
    }

    print("\n=== ESTATÍSTICAS COM NUMPY ===")
    for chave, valor in estatisticas.items():
        if isinstance(valor, float):
            print(f"  {chave}: {valor:.2f}")
        else:
            print(f"  {chave}: {valor}")
    return estatisticas


# ---------------------------------------------------------------- RF08
def grafico_receita_por_mes(por_mes):
    """Linha: receita total ao longo dos 12 meses."""
    fig, ax = plt.subplots()
    ax.plot(por_mes["mes"], por_mes["receita_total"],
            marker="o", linewidth=2, color=AZUL, label="Receita total")
    ax.set_title("Receita total por mês")
    ax.set_xlabel("Mês")
    ax.set_ylabel("Receita total (R$)")
    ax.set_xticks(range(1, 13))
    ax.legend()
    fig.tight_layout()
    fig.savefig("outputs/graficos/receita_por_mes.png", dpi=150)
    plt.close(fig)


def grafico_top_produtos(top_produtos):
    """Barras horizontais: os 5 produtos que mais faturaram."""
    fig, ax = plt.subplots()
    sns.barplot(data=top_produtos, y="produto", x="receita_total",
                hue="produto", legend=False, palette=PALETA, ax=ax)
    ax.set_title("Top 5 produtos por receita")
    ax.set_xlabel("Receita total (R$)")
    ax.set_ylabel("Produto")
    fig.tight_layout()
    fig.savefig("outputs/graficos/top_produtos.png", dpi=150)
    plt.close(fig)


def grafico_quantidade_vs_receita(df):
    """Dispersão: quantidade x receita, com uma cor por categoria."""
    fig, ax = plt.subplots()
    sns.scatterplot(data=df, x="quantidade", y="receita_total",
                    hue="categoria", palette=PALETA, ax=ax)
    ax.set_title("Quantidade x receita por transação")
    ax.set_xlabel("Quantidade vendida")
    ax.set_ylabel("Receita total (R$)")
    ax.legend(title="Categoria")
    fig.tight_layout()
    fig.savefig("outputs/graficos/quantidade_vs_receita.png", dpi=150)
    plt.close(fig)


def grafico_painel_resumo(df, metricas):
    """Painel 2x2 juntando as três visões anteriores com a receita por região."""
    por_mes = metricas["por_mes"]
    top_produtos = metricas["top_produtos"]
    por_regiao = metricas["por_regiao"]

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))

    axes[0, 0].plot(por_mes["mes"], por_mes["receita_total"],
                    marker="o", color=AZUL)
    axes[0, 0].set_title("Receita por mês")
    axes[0, 0].set_xlabel("Mês")
    axes[0, 0].set_ylabel("Receita total (R$)")

    axes[0, 1].barh(top_produtos["produto"], top_produtos["receita_total"],
                    color=VERMELHO)
    axes[0, 1].set_title("Top produtos")
    axes[0, 1].set_xlabel("Receita total (R$)")
    axes[0, 1].set_ylabel("Produto")

    axes[1, 0].scatter(df["quantidade"], df["receita_total"],
                       c=df["receita_total"], cmap="YlOrRd")
    axes[1, 0].set_title("Quantidade x receita")
    axes[1, 0].set_xlabel("Quantidade vendida")
    axes[1, 0].set_ylabel("Receita total (R$)")

    axes[1, 1].bar(por_regiao["regiao"], por_regiao["receita_total"],
                   color=VERDE)
    axes[1, 1].set_title("Receita por região")
    axes[1, 1].set_xlabel("Região")
    axes[1, 1].set_ylabel("Receita total (R$)")
    axes[1, 1].tick_params(axis="x", rotation=20)

    fig.suptitle("SalesInsight PY — painel de resumo", fontsize=16)
    fig.tight_layout()
    fig.savefig("outputs/graficos/painel_resumo.png", dpi=150)
    plt.close(fig)


def visualizar(df, metricas):
    """
    Gera as quatro figuras exigidas.

    Recebe o DataFrame limpo como parâmetro de propósito: antes eu usava
    uma variável global setada em outro método, e isso quebrava se
    alguém chamasse visualizar() fora da ordem do main().
    """
    os.makedirs("outputs/graficos", exist_ok=True)
    grafico_receita_por_mes(metricas["por_mes"])
    grafico_top_produtos(metricas["top_produtos"])
    grafico_quantidade_vs_receita(df)
    grafico_painel_resumo(df, metricas)
    print("\n4 figuras exportadas em outputs/graficos/.")


# ---------------------------------------------------------------- RF09
def processar_coluna(df, coluna, funcao_transformacao, nome_saida=None):
    """
    Aplica uma função a uma coluna e devolve o DataFrame.
    Serve para mostrar função Passando função como argumento.
    """
    nome_saida = nome_saida or f"{coluna}_transformado"
    df[nome_saida] = df[coluna].apply(funcao_transformacao)
    return df


class AnalisadorDeVendas:
    """Guarda o estado do fluxo e vai chamando as funções acima na ordem."""

    def __init__(self, caminho_arquivo):
        self.caminho_arquivo = caminho_arquivo
        self.df_bruto = None
        self.df_limpo = None
        self.metricas = {}
        self.clientes = None
        self.estatisticas = None
        self.relatorio_limpeza = {}

    def carregar(self):
        self.df_bruto = pd.read_csv(self.caminho_arquivo)
        print(f"[Analisador] {len(self.df_bruto)} registros lidos.")

    def limpar(self):
        self.df_limpo, self.relatorio_limpeza = limpar_dados(self.df_bruto.copy())

    def transformar(self):
        self.df_limpo = criar_colunas_derivadas(self.df_limpo)
        # as mesmas funções de ordem superior, com lambdas diferentes
        self.df_limpo = processar_coluna(
            self.df_limpo, "receita_total",
            lambda x: round(x / 1000, 2), nome_saida="receita_em_milhares")
        self.df_limpo = processar_coluna(
            self.df_limpo, "quantidade",
            lambda q: "Alto Volume" if q > 5 else "Baixo Volume",
            nome_saida="perfil_volume")

    def analisar(self):
        self.metricas = calcular_metricas(self.df_limpo)
        self.clientes = segmentar_clientes(self.df_limpo)
        self.estatisticas = calcular_estatisticas_numpy(self.df_limpo)

    def visualizar(self):
        visualizar(self.df_limpo, self.metricas)

    def resumo(self):
        print("\n=== RESUMO EXECUTIVO ===")
        print(f"Registros processados: {self.relatorio_limpeza['registros_finais']}")
        print(f"Clientes distintos: {len(self.clientes)}")
        print(f"Receita total: R$ {self.estatisticas['soma_receitas']:,.2f}")
        maior = self.metricas["por_regiao"].nlargest(1, "ticket_medio")
        print(f"Melhor ticket médio: {maior['regiao'].iloc[0]} "
              f"(R$ {maior['ticket_medio'].iloc[0]:,.2f})")


