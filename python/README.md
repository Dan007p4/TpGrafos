# Scripts Python - Visualização e Análise

Scripts para gerar visualizações e tabelas do trabalho.

## Pré-requisitos

1. Python 3.8+
2. Dados exportados pelo programa Java (arquivos CSV em `../output/`)

## Instalação

```bash
pip install -r requirements.txt
```

## Scripts Disponíveis

### 1. analysis_visualizer.py

Gera figuras e tabelas principais.

```bash
python analysis_visualizer.py
```

Saídas:
- `../output/figures/fig1_degree_distribution.png` - Distribuição de Degree Centrality
- `../output/figures/fig2_betweenness_distribution.png` - Distribuição de Betweenness Centrality
- `../output/figures/fig3_closeness_distribution.png` - Distribuição de Closeness Centrality
- `../output/figures/fig4_pagerank_distribution.png` - Distribuição de PageRank + Top 10
- `../output/figures/fig5_community_sizes.png` - Tamanhos das comunidades
- `../output/figures/fig6_centrality_heatmap.png` - Heatmap de centralidades (Top 20)
- `../output/figures/fig7_graph_comparison.png` - Comparação dos 3 grafos separados
- `../output/figures/fig8_bridging_analysis.png` - Análise de Bridging Strength
- `../output/tables/table1_structural_metrics.csv`
- `../output/tables/table2_top_developers.csv`
- `../output/tables/table3_communities.csv`
- `../output/tables/table4_bridging_developers.csv`
- `../output/tables/table5_separated_graphs.csv`
- `../output/tables/table6_correlation_matrix.csv`

### 2. additional_analysis.py

Gera análises temporais, classificação de papéis e volume de atividade.

```bash
python additional_analysis.py
```

Análises Temporais:
- `../output/figures/fig7_temporal_nodes.png` - Evolução de desenvolvedores ativos
- `../output/figures/fig8_temporal_interactions.png` - Volume de interações ao longo do tempo
- `../output/figures/fig9_activity_heatmap.png` - Heatmap de atividade (mês × ano)
- `../output/figures/fig11_monthly_detailed.png` - Análise temporal detalhada mês a mês (duplo eixo Y)
- `../output/tables/table7_temporal_stats.csv` - Estatísticas temporais (picos, vales, tendências)

Classificação de Papéis:
- `../output/figures/fig10_role_distribution.png` - Distribuição de papéis na rede
- `../output/tables/table8_role_classification.csv` - Classificação completa de todos os desenvolvedores
- `../output/tables/table9_role_statistics.csv` - Estatísticas por papel

Volume de Atividade:
- `../output/figures/fig12_top_developers_activity.png` - Top 20 desenvolvedores por volume total
- `../output/figures/fig13_activity_composition.png` - Composição de atividade por tipo
- `../output/figures/fig14_activity_distribution.png` - Distribuição e concentração de atividade
- `../output/tables/table10_developer_activity_volume.csv` - Ranking Top 30 com breakdown por tipo

Análise de Comunidades:
- `../output/figures/fig15_community_cohesion.png` - Densidade intra vs inter-comunidades
- `../output/figures/fig16_community_function.png` - Caracterização funcional das comunidades
- `../output/tables/table11_community_cohesion.csv` - Métricas de coesão por comunidade
- `../output/tables/table12_community_function.csv` - Tipos de interação dominantes por comunidade

### 3. generate_report.py

Gera relatório completo em Markdown.

```bash
python generate_report.py
```

Saída: `../output/RELATORIO_COMPLETO.md`

### 4. export_latex.py

Converte tabelas CSV para formato LaTeX.

```bash
python export_latex.py
```

Saídas:
- `../output/tables/all_tables.tex` - Documento LaTeX completo com todas as tabelas
- `../output/tables/table1_structural_metrics.tex`
- `../output/tables/table2_top_developers.tex`
- `../output/tables/table3_communities.tex`
- `../output/tables/table4_bridging_developers.tex`
- `../output/tables/table5_separated_graphs.tex`
- `../output/tables/table6_correlation_matrix.tex`

## Workflow Completo

1. Execute o programa Java para gerar os CSVs
2. Execute os scripts Python na ordem:

```bash
# Gera todas as figuras e tabelas principais (Fig 1-8, Tabelas 1-6)
python analysis_visualizer.py

# Gera análises adicionais: temporal, papéis e volume (Fig 7-13, Tabelas 7-10)
python additional_analysis.py

# Gera relatório markdown completo
python generate_report.py

# Exporta tabelas para LaTeX (opcional)
python export_latex.py
```

## Estrutura de Saída

```
../output/
├── data/
│   └── interactions.csv
├── figures/
│   ├── fig1_degree_distribution.png          (Degree Centrality)
│   ├── fig2_betweenness_distribution.png     (Betweenness Centrality)
│   ├── fig3_closeness_distribution.png       (Closeness Centrality)
│   ├── fig4_pagerank_distribution.png        (PageRank + Top 10)
│   ├── fig5_community_sizes.png              (Tamanhos comunidades)
│   ├── fig6_centrality_heatmap.png           (Heatmap centralidades)
│   ├── fig7_graph_comparison.png             (Comparação 3 grafos)
│   ├── fig8_bridging_analysis.png            (Bridging Strength)
│   ├── fig7_temporal_nodes.png               [ADICIONAL - Temporal]
│   ├── fig8_temporal_interactions.png        [ADICIONAL - Temporal]
│   ├── fig9_activity_heatmap.png             [ADICIONAL - Temporal]
│   ├── fig10_role_distribution.png           [ADICIONAL - Papéis]
│   ├── fig11_monthly_detailed.png            [ADICIONAL - Temporal]
│   ├── fig12_top_developers_activity.png     [ADICIONAL - Volume]
│   └── fig13_activity_composition.png        [ADICIONAL - Volume]
├── tables/
│   ├── table1_structural_metrics.csv
│   ├── table2_top_developers.csv
│   ├── table3_communities.csv
│   ├── table4_bridging_developers.csv
│   ├── table5_separated_graphs.csv
│   ├── table6_correlation_matrix.csv
│   ├── table7_temporal_stats.csv         [ADICIONAL]
│   ├── table8_role_classification.csv    [ADICIONAL]
│   ├── table9_role_statistics.csv        [ADICIONAL]
│   ├── table10_developer_activity_volume.csv [ADICIONAL]
│   ├── all_tables.tex
│   └── [arquivos .tex individuais]
├── RELATORIO_COMPLETO.md
└── [outros arquivos GEXF e CSV]
```

## Notas

- Análise Temporal requer que `interactions.csv` tenha timestamps válidos
- Classificação de Papéis funciona mesmo sem bridging developers
- Volume de Atividade conta apenas interações como Source (quem fez a ação)
- Figuras geradas em alta resolução (300 DPI)
- Scripts funcionam mesmo se alguns arquivos CSV estiverem faltando

## Troubleshooting

Erro "FileNotFoundError":
- Execute o programa Java primeiro
- Verifique arquivos CSV em `../output/`

Erro "ModuleNotFoundError":
- Execute: `pip install -r requirements.txt`
