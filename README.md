# SalesInsight PY

Análise de dados de vendas em Python, feita como mini-projeto avaliativo
do Módulo 01 (Semana 08) do curso Desenvolvimento de IA para Análise
Preditiva [T3].

O script lê um CSV de vendas, limpa os registros, calcula receita por
período/produto/categoria/região, segmenta os clientes por faixa de gasto
e exporta tudo em CSV, JSON e PNG.

## O que o projeto analisa

- Receita total e volume de vendas por mês e por trimestre
- Top 5 produtos e o total por categoria
- Desempenho e ticket médio por região
- Segmentação de clientes em Bronze, Prata e Ouro
- Relação entre quantidade vendida e receita de cada transação

## Requisitos

Python 3.10 ou superior e as quatro bibliotecas:

```bash
pip install pandas numpy matplotlib seaborn
```

## Como executar

Clona o repositório e roda o script:

```bash
python salesinsight.py
```

Se a pasta não tiver um `vendas.csv`, o script gera um com 200 registros
sintéticos — inclusive com a sujeira que a etapa de limpeza precisa tratar
(nulos, data inválida, espaço sobrando e nome de cliente escrito de quatro
formas diferentes). Depois disso, todas as saídas vão para `outputs/`.

Para usar outro dataset, é só pôr o seu CSV no lugar do `vendas.csv` com
as colunas `id_venda`, `data_venda`, `cliente`, `produto`, `categoria`,
`regiao`, `quantidade` e `preco_unitario`.

## Estrutura

```
salesinsight-py/
|-- salesinsight.py         # fluxo inteiro
|-- vendas.csv              # dataset (gerado pelo script)
|-- README.md
|-- planejamento/
|   `-- tarefas-kanban.md   # quadro usado pra organizar o trabalho
`-- outputs/
    |-- metricas_por_mes.csv
    |-- segmentacao_clientes.csv
    |-- estatisticas_gerais.json
    `-- graficos/
        |-- receita_por_mes.png
        |-- top_produtos.png
        |-- quantidade_vs_receita.png
        `-- painel_resumo.png
```

## Decisões técnicas

Duas coisas que vale explicar.

**Descartar registro em vez de tentar consertar.** Data ilegível e
quantidade ou preço vazio não têm como ser recuperados — não existe
"meio preço". Mandar embora essas linhas é melhor do que preencher com
zero, porque zero contaminaria a média e os gráficos sem deixar rastro de
que houve perda. O relatório de limpeza mostra quantas linhas saíram em
cada etapa.

**Normalizar o nome do cliente em vez de descartar.** Os nomes chegam em
`Cliente_007`, `cliente#007`, `CLIENTE-007` e `Cliente_007!!`. Meu
primeiro jeito de resolver foi apagar os caracteres estranhos com regex,
mas aí `cliente#016` virava `CLIENTE016`: o mesmo cliente passava a contar
duas vezes na segmentação e acabava em dois segmentos diferentes. Agora
`normalizar_cliente()` pega só os dígitos e remonta o nome, e o
`segmentacao_clientes.csv` sai com 50 clientes em vez de 58.

Usei também `np.select` para as faixas de receita em lugar de um laço com
`if`: são condições vetoriais, então o pandas resolve a coluna inteira de
uma vez. E as figuras 3 e 4 (dispersão e painel) são cópias adaptadas da
2 e da 1 respectivamente, reaproveitando o `fig, ax` que já existia,
porque refazer do zero só repetiria código.

## Conceitos aplicados (Semanas 01 a 08)

Lógica de programação, tipos de dados, operadores, condicionais, laços,
listas/tuplas/dicionários, leitura e escrita de CSV e JSON, módulo
`datetime`, expressões regulares, funções com parâmetro/retorno/docstring,
funções lambda, função que recebe função como argumento, Series e
DataFrames, filtros booleanos, `groupby` com agregação, `to_numpy()`,
operações vetorizadas, broadcasting, filtragem booleana de array, gráfico
de linha, de barras e de dispersão, customização de figura, subplots e
`savefig`, e classes com construtor, atributos de instância e métodos
usando `self`.

## Versionamento

O repositório segue um GitFlow simplificado: `main` recebe o código
final, `develop` acumula as etapas, e cada bloco de trabalho tem sua
branch (`feat/leitura-limpeza`, `feat/analise-metricas`,
`feat/visualizacoes`, `feat/classe-analisador`). As mensagens de commit
seguem o padrão de conventional commits.

## Ferramentas

- Python 3.10+
- pandas, numpy, matplotlib, seaborn
- Módulos da biblioteca padrão: `os`, `re`, `json`, `random`, `datetime`
- Git e GitHub para versionamento
- Quadro Kanban em Markdown dentro de `planejamento/`
