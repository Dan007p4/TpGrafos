#!/usr/bin/env python3
"""
Gera visualizações e tabelas da análise de grafos.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os
from pathlib import Path

# Configuração de estilo
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    try:
        plt.style.use('seaborn-darkgrid')
    except:
        plt.style.use('default')

sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['figure.figsize'] = (10, 6)


class GraphAnalysisVisualizer:

    def __init__(self, output_dir='../output'):
        self.output_dir = Path(output_dir)
        self.figures_dir = self.output_dir / 'figures'
        self.tables_dir = self.output_dir / 'tables'

        # Cria diretórios de saída
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.tables_dir.mkdir(parents=True, exist_ok=True)

        # Carrega dados
        self.load_data()

    def load_data(self):
        print("Carregando dados...")

        try:
            # Dados brutos - corrige CSV malformado (7 colunas mas 6 no header)
            self.interactions = pd.read_csv(
                self.output_dir / '../data/interactions.csv',
                names=['Source', 'Target', 'Type', 'Weight', 'EXTRA', 'Timestamp', 'Context'],
                skiprows=1
            )
            self.interactions = self.interactions.drop(columns=['EXTRA'])

            self.edges = pd.read_csv(self.output_dir / 'graph_edges.csv')

            # Métricas de centralidade
            self.centrality = pd.read_csv(self.output_dir / 'centrality_metrics.csv')

            # Comunidades
            self.communities = pd.read_csv(self.output_dir / 'community_assignments.csv')

            # Bridging developers
            self.bridging = pd.read_csv(self.output_dir / 'bridging_developers.csv')

            # Métricas estruturais
            self.structural = pd.read_csv(self.output_dir / 'structural_metrics.csv')
            self.structural_dict = dict(zip(self.structural['Metric'], self.structural['Value']))

            print(f"✓ {len(self.centrality)} vértices carregados")
            print(f"✓ {len(self.edges)} arestas carregadas")
            print(f"✓ {self.structural_dict.get('NumberOfCommunities', 0)} comunidades detectadas")
            print(f"✓ {len(self.bridging)} bridging ties identificados")

        except Exception as e:
            print(f"✗ Erro ao carregar dados: {e}")
            print("Certifique-se de que o programa Java foi executado e os CSVs foram gerados.")
            raise

    # ========================================================================
    # GERAÇÃO DE FIGURAS
    # ========================================================================

    def figure1_degree_distribution(self):
        """Figura 1: Distribuição de Degree Centrality Normalizada"""
        print("\nGerando Figura 1: Distribuição de Degree Centrality...")

        # Usa a Degree Centrality normalizada (0 a 1) do CSV
        degree_centrality = self.centrality['DegreeCentrality']

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

        # Histograma com bins mais largos
        n, bins, patches = ax1.hist(degree_centrality, bins=40, edgecolor='black',
                                     linewidth=1.2, alpha=0.8, color='steelblue',
                                     rwidth=0.95)  # rwidth controla a largura das barras

        ax1.set_xlabel('Degree Centrality (normalizada)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Número de Desenvolvedores', fontsize=12, fontweight='bold')
        ax1.set_title('Distribuição de Degree Centrality', fontsize=14, fontweight='bold', pad=15)
        ax1.grid(True, alpha=0.3, axis='y', linestyle='--')
        ax1.set_xlim(-0.02, 1.02)  # Pequena margem para melhor visualização

        # Adiciona linha vertical na média
        mean_val = degree_centrality.mean()
        ax1.axvline(mean_val, color='red', linestyle='--', linewidth=2,
                   label=f'Média: {mean_val:.4f}', alpha=0.7)
        ax1.legend(fontsize=11, loc='upper right')

        # Estatísticas detalhadas
        stats_data = {
            'Métrica': ['Mínimo', 'Q1 (25%)', 'Mediana', 'Q3 (75%)', 'Máximo',
                       'Média', 'Desvio Padrão', 'Coef. Variação'],
            'Valor': [
                f"{degree_centrality.min():.6f}",
                f"{degree_centrality.quantile(0.25):.6f}",
                f"{degree_centrality.median():.6f}",
                f"{degree_centrality.quantile(0.75):.6f}",
                f"{degree_centrality.max():.6f}",
                f"{degree_centrality.mean():.6f}",
                f"{degree_centrality.std():.6f}",
                f"{(degree_centrality.std() / degree_centrality.mean()):.4f}"
            ]
        }

        # Cria tabela de estatísticas
        ax2.axis('tight')
        ax2.axis('off')

        table = ax2.table(cellText=[[stats_data['Métrica'][i], stats_data['Valor'][i]]
                                     for i in range(len(stats_data['Métrica']))],
                         colLabels=['Métrica', 'Valor'],
                         cellLoc='left',
                         loc='center',
                         colWidths=[0.5, 0.35])

        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 2.2)

        # Estiliza cabeçalho
        for i in range(2):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')

        # Estiliza linhas alternadas
        for i in range(1, len(stats_data['Métrica']) + 1):
            if i % 2 == 0:
                table[(i, 0)].set_facecolor('#E8F0FF')
                table[(i, 1)].set_facecolor('#E8F0FF')

        ax2.set_title('Estatísticas Descritivas', fontsize=14, fontweight='bold', pad=20)

        plt.suptitle('Figura 1: Análise de Degree Centrality',
                    fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        output_path = self.figures_dir / 'fig1_degree_distribution.png'
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()
        print(f"  ✓ Salva: {output_path}")

    def figure2_betweenness_distribution(self):
        """Figura 2: Distribuição de Betweenness Centrality Normalizada"""
        print("\nGerando Figura 2: Distribuição de Betweenness Centrality...")

        # Usa a Betweenness Centrality normalizada do CSV
        betweenness_centrality = self.centrality['BetweennessCentrality']

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

        # Histograma com bins mais largos
        n, bins, patches = ax1.hist(betweenness_centrality, bins=40, edgecolor='black',
                                     linewidth=1.2, alpha=0.8, color='#E63946',
                                     rwidth=0.95)

        ax1.set_xlabel('Betweenness Centrality (normalizada)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Número de Desenvolvedores', fontsize=12, fontweight='bold')
        ax1.set_title('Distribuição de Betweenness Centrality', fontsize=14, fontweight='bold', pad=15)
        ax1.grid(True, alpha=0.3, axis='y', linestyle='--')
        ax1.set_xlim(-0.02, max(1.02, betweenness_centrality.max() * 1.05))

        # Adiciona linha vertical na média
        mean_val = betweenness_centrality.mean()
        ax1.axvline(mean_val, color='darkred', linestyle='--', linewidth=2,
                   label=f'Média: {mean_val:.4f}', alpha=0.7)
        ax1.legend(fontsize=11, loc='upper right')

        # Estatísticas detalhadas
        stats_data = {
            'Métrica': ['Mínimo', 'Q1 (25%)', 'Mediana', 'Q3 (75%)', 'Máximo',
                       'Média', 'Desvio Padrão', 'Coef. Variação'],
            'Valor': [
                f"{betweenness_centrality.min():.6f}",
                f"{betweenness_centrality.quantile(0.25):.6f}",
                f"{betweenness_centrality.median():.6f}",
                f"{betweenness_centrality.quantile(0.75):.6f}",
                f"{betweenness_centrality.max():.6f}",
                f"{betweenness_centrality.mean():.6f}",
                f"{betweenness_centrality.std():.6f}",
                f"{(betweenness_centrality.std() / betweenness_centrality.mean()) if betweenness_centrality.mean() > 0 else 0:.4f}"
            ]
        }

        # Cria tabela de estatísticas
        ax2.axis('tight')
        ax2.axis('off')

        table = ax2.table(cellText=[[stats_data['Métrica'][i], stats_data['Valor'][i]]
                                     for i in range(len(stats_data['Métrica']))],
                         colLabels=['Métrica', 'Valor'],
                         cellLoc='left',
                         loc='center',
                         colWidths=[0.5, 0.35])

        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 2.2)

        # Estiliza cabeçalho
        for i in range(2):
            table[(0, i)].set_facecolor('#E63946')
            table[(0, i)].set_text_props(weight='bold', color='white')

        # Estiliza linhas alternadas
        for i in range(1, len(stats_data['Métrica']) + 1):
            if i % 2 == 0:
                table[(i, 0)].set_facecolor('#FFE8E8')
                table[(i, 1)].set_facecolor('#FFE8E8')

        ax2.set_title('Estatísticas Descritivas', fontsize=14, fontweight='bold', pad=20)

        plt.suptitle('Figura 2: Análise de Betweenness Centrality',
                    fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        output_path = self.figures_dir / 'fig2_betweenness_distribution.png'
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()
        print(f"  ✓ Salva: {output_path}")

    def figure3_closeness_distribution(self):
        """Figura 3: Distribuição de Closeness Centrality Normalizada"""
        print("\nGerando Figura 3: Distribuição de Closeness Centrality...")

        # Usa a Closeness Centrality normalizada do CSV
        closeness_centrality = self.centrality['ClosenessCentrality']

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

        # Histograma com bins mais largos
        n, bins, patches = ax1.hist(closeness_centrality, bins=40, edgecolor='black',
                                     linewidth=1.2, alpha=0.8, color='#2A9D8F',
                                     rwidth=0.95)

        ax1.set_xlabel('Closeness Centrality (normalizada)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Número de Desenvolvedores', fontsize=12, fontweight='bold')
        ax1.set_title('Distribuição de Closeness Centrality', fontsize=14, fontweight='bold', pad=15)
        ax1.grid(True, alpha=0.3, axis='y', linestyle='--')
        ax1.set_xlim(-0.02, 1.02)

        # Adiciona linha vertical na média
        mean_val = closeness_centrality.mean()
        ax1.axvline(mean_val, color='darkgreen', linestyle='--', linewidth=2,
                   label=f'Média: {mean_val:.4f}', alpha=0.7)
        ax1.legend(fontsize=11, loc='upper right')

        # Estatísticas detalhadas
        stats_data = {
            'Métrica': ['Mínimo', 'Q1 (25%)', 'Mediana', 'Q3 (75%)', 'Máximo',
                       'Média', 'Desvio Padrão', 'Coef. Variação'],
            'Valor': [
                f"{closeness_centrality.min():.6f}",
                f"{closeness_centrality.quantile(0.25):.6f}",
                f"{closeness_centrality.median():.6f}",
                f"{closeness_centrality.quantile(0.75):.6f}",
                f"{closeness_centrality.max():.6f}",
                f"{closeness_centrality.mean():.6f}",
                f"{closeness_centrality.std():.6f}",
                f"{(closeness_centrality.std() / closeness_centrality.mean()) if closeness_centrality.mean() > 0 else 0:.4f}"
            ]
        }

        # Cria tabela de estatísticas
        ax2.axis('tight')
        ax2.axis('off')

        table = ax2.table(cellText=[[stats_data['Métrica'][i], stats_data['Valor'][i]]
                                     for i in range(len(stats_data['Métrica']))],
                         colLabels=['Métrica', 'Valor'],
                         cellLoc='left',
                         loc='center',
                         colWidths=[0.5, 0.35])

        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 2.2)

        # Estiliza cabeçalho
        for i in range(2):
            table[(0, i)].set_facecolor('#2A9D8F')
            table[(0, i)].set_text_props(weight='bold', color='white')

        # Estiliza linhas alternadas
        for i in range(1, len(stats_data['Métrica']) + 1):
            if i % 2 == 0:
                table[(i, 0)].set_facecolor('#E0F4F1')
                table[(i, 1)].set_facecolor('#E0F4F1')

        ax2.set_title('Estatísticas Descritivas', fontsize=14, fontweight='bold', pad=20)

        plt.suptitle('Figura 3: Análise de Closeness Centrality',
                    fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        output_path = self.figures_dir / 'fig3_closeness_distribution.png'
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()
        print(f"  ✓ Salva: {output_path}")

    def figure4_pagerank_distribution(self):
        """Figura 4: Distribuição de PageRank com Top 10"""
        print("\nGerando Figura 4: Distribuição de PageRank...")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Histograma + boxplot
        ax1.hist(self.centrality['PageRank'], bins=50, edgecolor='black', alpha=0.7)
        ax1.set_xlabel('PageRank')
        ax1.set_ylabel('Frequência')
        ax1.set_title('Distribuição de PageRank')
        ax1.grid(True, alpha=0.3)

        # Top 10 desenvolvedores
        top10 = self.centrality.nlargest(10, 'PageRank')
        ax2.barh(range(10), top10['PageRank'].values)
        ax2.set_yticks(range(10))
        ax2.set_yticklabels(top10['Label'].values)
        ax2.set_xlabel('PageRank')
        ax2.set_title('Top 10 Desenvolvedores (PageRank)')
        ax2.invert_yaxis()
        ax2.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        output_path = self.figures_dir / 'fig4_pagerank_distribution.png'
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Salva: {output_path}")

    def figure5_community_sizes(self):
        """Figura 5: Tamanhos das Comunidades"""
        print("\nGerando Figura 5: Tamanhos das Comunidades...")

        community_sizes = self.communities.groupby('CommunityID').size().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(10, max(6, len(community_sizes) * 0.4)))

        colors = sns.color_palette("husl", len(community_sizes))
        ax.barh(range(len(community_sizes)), community_sizes.values, color=colors)
        ax.set_yticks(range(len(community_sizes)))
        ax.set_yticklabels([f'Comunidade {cid}' for cid in community_sizes.index])
        ax.set_xlabel('Número de Membros')
        ax.set_title('Tamanho das Comunidades Detectadas')
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        output_path = self.figures_dir / 'fig5_community_sizes.png'
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Salva: {output_path}")

    def figure6_centrality_heatmap(self):
        """Figura 6: Heatmap de Centralidades (Top 20)"""
        print("\nGerando Figura 6: Heatmap de Centralidades...")

        # Seleciona top 20 por PageRank
        top20 = self.centrality.nlargest(20, 'PageRank')

        # Normaliza as métricas para [0, 1]
        metrics = ['DegreeCentrality', 'BetweennessCentrality', 'ClosenessCentrality', 'PageRank']
        normalized = top20[metrics].copy()
        for col in metrics:
            normalized[col] = (normalized[col] - normalized[col].min()) / \
                              (normalized[col].max() - normalized[col].min())

        # Cria heatmap
        fig, ax = plt.subplots(figsize=(10, 12))
        sns.heatmap(normalized.values,
                    xticklabels=['Degree', 'Betweenness', 'Closeness', 'PageRank'],
                    yticklabels=top20['Label'].values,
                    cmap='YlOrRd',
                    annot=False,
                    cbar_kws={'label': 'Valor Normalizado'},
                    ax=ax)

        ax.set_title('Top 20 Desenvolvedores - Comparação de Centralidades (Normalizado)')
        ax.set_xlabel('Métrica de Centralidade')
        ax.set_ylabel('Desenvolvedor')

        plt.tight_layout()
        output_path = self.figures_dir / 'fig6_centrality_heatmap.png'
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Salva: {output_path}")

    def figure7_graph_comparison(self):
        """Figura 7: Comparação dos 3 Grafos Separados"""
        print("\nGerando Figura 7: Comparação dos Grafos Separados...")

        # Nota: Como não temos métricas dos grafos separados exportadas,
        # vamos criar uma visualização conceitual
        # Idealmente, você deveria exportar métricas de cada grafo separadamente

        # Dados fictícios para demonstração - AJUSTE CONFORME NECESSÁRIO
        graph_data = {
            'Grafo': ['Comentários', 'Fechamentos', 'Reviews'],
            'Vértices': [100, 80, 90],  # Placeholder
            'Arestas': [500, 200, 350],  # Placeholder
            'Densidade': [0.05, 0.03, 0.04],  # Placeholder
        }
        df_graphs = pd.DataFrame(graph_data)

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # Vértices
        axes[0].bar(df_graphs['Grafo'], df_graphs['Vértices'], color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        axes[0].set_ylabel('Quantidade')
        axes[0].set_title('Número de Vértices')
        axes[0].grid(True, alpha=0.3, axis='y')

        # Arestas
        axes[1].bar(df_graphs['Grafo'], df_graphs['Arestas'], color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        axes[1].set_ylabel('Quantidade')
        axes[1].set_title('Número de Arestas')
        axes[1].grid(True, alpha=0.3, axis='y')

        # Densidade
        axes[2].bar(df_graphs['Grafo'], df_graphs['Densidade'], color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        axes[2].set_ylabel('Densidade')
        axes[2].set_title('Densidade do Grafo')
        axes[2].grid(True, alpha=0.3, axis='y')

        plt.suptitle('Comparação dos 3 Grafos Separados', fontsize=14, fontweight='bold')
        plt.tight_layout()
        output_path = self.figures_dir / 'fig7_graph_comparison.png'
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Salva: {output_path}")
        print("  ⚠ NOTA: Valores placeholder. Exporte métricas dos grafos separados para dados reais.")

    def figure8_bridging_analysis(self):
        """Figura 8: Análise de Bridging Strength vs PageRank"""
        print("\nGerando Figura 8: Análise de Bridging Strength...")

        # Verifica se há bridging developers
        if self.bridging.empty:
            print("  ⚠ AVISO: Nenhum bridging tie detectado no grafo.")
            print("  ℹ Gerando figura placeholder...")

            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5,
                   'Nenhum Bridging Tie Detectado\n\n' +
                   'O algoritmo não identificou desenvolvedores que conectam\n' +
                   'diferentes comunidades neste grafo.',
                   ha='center', va='center', fontsize=14)
            ax.set_xlabel('Bridging Strength')
            ax.set_ylabel('PageRank')
            ax.set_title('Figura 8: Análise de Bridging Strength vs PageRank')

            output_path = self.figures_dir / 'fig8_bridging_analysis.png'
            plt.savefig(output_path, bbox_inches='tight')
            plt.close()
            print(f"  ✓ Salva: {output_path} (placeholder)")
            return

        # Merge bridging com centrality
        merged = self.bridging.merge(
            self.centrality[['Vertex', 'PageRank']],
            on='Vertex'
        )

        fig, ax = plt.subplots(figsize=(12, 8))

        # Scatter plot colorido por comunidade
        communities_unique = merged['CommunityID'].unique()
        colors = sns.color_palette("husl", len(communities_unique))

        for i, comm_id in enumerate(communities_unique):
            comm_data = merged[merged['CommunityID'] == comm_id]
            ax.scatter(comm_data['BridgingStrength'],
                      comm_data['PageRank'],
                      label=f'Comunidade {comm_id}',
                      s=100,
                      alpha=0.6,
                      color=colors[i])

        # Destaca top 10 bridges
        top10_bridges = merged.nlargest(10, 'BridgingStrength')
        ax.scatter(top10_bridges['BridgingStrength'],
                  top10_bridges['PageRank'],
                  s=200,
                  facecolors='none',
                  edgecolors='red',
                  linewidths=2,
                  label='Top 10 Bridges',
                  zorder=5)

        # Anota top 10 (com ajuste de posição para evitar sobreposição)
        for idx, row in top10_bridges.iterrows():
            # Alterna posicionamento para reduzir sobreposição
            offset_x = 5 if idx % 2 == 0 else -5
            offset_y = 5 if idx % 3 == 0 else -8
            ha = 'left' if offset_x > 0 else 'right'

            ax.annotate(row['Label'],
                       (row['BridgingStrength'], row['PageRank']),
                       xytext=(offset_x, offset_y),
                       textcoords='offset points',
                       fontsize=7,
                       ha=ha,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

        ax.set_xlabel('Bridging Strength')
        ax.set_ylabel('PageRank')
        ax.set_title('Relação entre Bridging Strength e PageRank')
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = self.figures_dir / 'fig8_bridging_analysis.png'
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Salva: {output_path}")

    # ========================================================================
    # GERAÇÃO DE TABELAS
    # ========================================================================

    def table1_structural_metrics(self):
        """Tabela 1: Métricas Estruturais Gerais"""
        print("\nGerando Tabela 1: Métricas Estruturais...")

        # Extrai métricas do grafo integrado
        data = {
            'Métrica': [
                'Vértices',
                'Arestas',
                'Densidade',
                'Coef. Aglomeração',
                'Diâmetro',
                'Distância Média',
                'Assortatividade',
                'Modularidade',
                'Nº Comunidades'
            ],
            'Grafo Integrado': [
                self.structural_dict.get('Vertices', 0),
                self.structural_dict.get('Edges', 0),
                f"{self.structural_dict.get('Density', 0):.6f}",
                f"{self.structural_dict.get('ClusteringCoefficient', 0):.6f}",
                self.structural_dict.get('Diameter', 0),
                f"{self.structural_dict.get('AverageDistance', 0):.6f}",
                f"{self.structural_dict.get('Assortativity', 0):.6f}",
                f"{self.structural_dict.get('Modularity', 0):.6f}",
                self.structural_dict.get('NumberOfCommunities', 0)
            ]
        }

        df = pd.DataFrame(data)

        output_path = self.tables_dir / 'table1_structural_metrics.csv'
        df.to_csv(output_path, index=False)
        print(f"  ✓ Salva: {output_path}")

        return df

    def table2_top_developers(self):
        """Tabela 2: Top 10 Desenvolvedores por Centralidade"""
        print("\nGerando Tabela 2: Top 10 Desenvolvedores...")

        top10 = self.centrality.nlargest(10, 'PageRank').copy()
        top10['Rank'] = range(1, 11)

        # Formata valores
        table = top10[['Rank', 'Label', 'DegreeCentrality', 'BetweennessCentrality',
                      'ClosenessCentrality', 'PageRank']].copy()
        table.columns = ['Rank', 'Desenvolvedor', 'Degree', 'Betweenness', 'Closeness', 'PageRank']

        for col in ['Degree', 'Betweenness', 'Closeness', 'PageRank']:
            table[col] = table[col].apply(lambda x: f"{x:.6f}")

        output_path = self.tables_dir / 'table2_top_developers.csv'
        table.to_csv(output_path, index=False)
        print(f"  ✓ Salva: {output_path}")

        return table

    def table3_community_summary(self):
        """Tabela 3: Resumo das Comunidades"""
        print("\nGerando Tabela 3: Resumo das Comunidades...")

        # Agrupa por comunidade
        comm_summary = self.communities.groupby('CommunityID').agg(
            Membros=('Vertex', 'count')
        ).reset_index()

        # Calcula percentual
        total = len(self.communities)
        comm_summary['% Total'] = (comm_summary['Membros'] / total * 100).apply(lambda x: f"{x:.2f}%")

        # Encontra top contribuidor por comunidade (maior PageRank)
        # Remove Label do centrality para evitar duplicação (communities já tem Label)
        merged = self.communities.merge(
            self.centrality[['Vertex', 'PageRank']],
            on='Vertex'
        )

        # Encontra top contribuidor manualmente para cada comunidade
        top_contribs = []
        for comm_id in comm_summary['CommunityID']:
            comm_data = merged[merged['CommunityID'] == comm_id].copy()
            if len(comm_data) > 0:
                # Ordena por PageRank e pega o primeiro
                comm_data_sorted = comm_data.sort_values('PageRank', ascending=False)
                top_dev = comm_data_sorted.iloc[0]['Label']
            else:
                top_dev = 'N/A'
            top_contribs.append(top_dev)

        comm_summary['Top Contribuidor'] = top_contribs

        # Ordena por número de membros
        comm_summary = comm_summary.sort_values('Membros', ascending=False)

        output_path = self.tables_dir / 'table3_communities.csv'
        comm_summary.to_csv(output_path, index=False)
        print(f"  ✓ Salva: {output_path}")

        return comm_summary

    def table4_bridging_developers(self):
        """Tabela 4: Top 10 Bridging Developers"""
        print("\nGerando Tabela 4: Top 10 Bridging Developers...")

        # Verifica se há bridging developers
        if self.bridging.empty:
            print("  ⚠ AVISO: Nenhum bridging tie detectado.")
            # Cria tabela vazia
            table = pd.DataFrame(columns=['Rank', 'Desenvolvedor', 'Comunidade',
                                         'Bridging Strength', 'Comunidades Conectadas', 'PageRank'])
            output_path = self.tables_dir / 'table4_bridging_developers.csv'
            table.to_csv(output_path, index=False)
            print(f"  ✓ Salva: {output_path} (vazia)")
            return table

        # Merge com PageRank
        merged = self.bridging.merge(
            self.centrality[['Vertex', 'PageRank']],
            on='Vertex'
        )

        # Top 10 (ou menos se não houver 10)
        n = min(10, len(merged))
        top10 = merged.nlargest(n, 'BridgingStrength').copy()
        top10['Rank'] = range(1, n + 1)

        # Formata
        table = top10[['Rank', 'Label', 'CommunityID', 'BridgingStrength',
                      'ConnectedCommunities', 'PageRank']].copy()
        table.columns = ['Rank', 'Desenvolvedor', 'Comunidade', 'Bridging Strength',
                        'Comunidades Conectadas', 'PageRank']

        table['Bridging Strength'] = table['Bridging Strength'].apply(lambda x: f"{x:.6f}")
        table['PageRank'] = table['PageRank'].apply(lambda x: f"{x:.6f}")

        output_path = self.tables_dir / 'table4_bridging_developers.csv'
        table.to_csv(output_path, index=False)
        print(f"  ✓ Salva: {output_path}")

        return table

    def table5_separated_graphs(self):
        """Tabela 5: Estatísticas dos Grafos Separados"""
        print("\nGerando Tabela 5: Grafos Separados...")

        # PLACEHOLDER - você deve exportar métricas dos grafos separados
        data = {
            'Métrica': ['Vértices', 'Arestas', 'Densidade', 'Clustering'],
            'Grafo 1 (Comentários)': ['100', '500', '0.050', '0.35'],
            'Grafo 2 (Fechamentos)': ['80', '200', '0.031', '0.28'],
            'Grafo 3 (Reviews)': ['90', '350', '0.043', '0.32']
        }

        df = pd.DataFrame(data)

        output_path = self.tables_dir / 'table5_separated_graphs.csv'
        df.to_csv(output_path, index=False)
        print(f"  ✓ Salva: {output_path}")
        print("  ⚠ NOTA: Valores placeholder. Implemente exportação de métricas por grafo.")

        return df

    def table6_correlation_matrix(self):
        """Tabela 6: Matriz de Correlação entre Métricas"""
        print("\nGerando Tabela 6: Matriz de Correlação...")

        # Merge bridging com centrality
        merged = self.centrality.merge(
            self.bridging[['Vertex', 'BridgingStrength']],
            on='Vertex',
            how='left'
        )
        merged['BridgingStrength'].fillna(0, inplace=True)

        # Calcula correlação
        metrics = ['DegreeCentrality', 'BetweennessCentrality', 'ClosenessCentrality',
                  'PageRank', 'BridgingStrength']
        corr_matrix = merged[metrics].corr()

        # Formata
        corr_matrix.index = ['Degree', 'Betweenness', 'Closeness', 'PageRank', 'Bridging Str']
        corr_matrix.columns = ['Degree', 'Betweenness', 'Closeness', 'PageRank', 'Bridging Str']

        output_path = self.tables_dir / 'table6_correlation_matrix.csv'
        corr_matrix.to_csv(output_path, float_format='%.4f')
        print(f"  ✓ Salva: {output_path}")

        return corr_matrix

    def figure15_centrality_distributions(self):
        """Figura 15: Distribuições Comparativas das 3 Métricas de Centralidade"""
        print("\nGerando Figura 15: Distribuições de Centralidade Comparadas...")

        # Cria figura com 3 subplots lado a lado
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

        # Subplot 1: Degree Centrality
        degree_vals = self.centrality['DegreeCentrality'].values
        mean_degree = degree_vals.mean()
        median_degree = np.median(degree_vals)

        ax1.hist(degree_vals, bins=50, color='#2A9D8F', edgecolor='black', alpha=0.7)
        ax1.axvline(mean_degree, color='red', linestyle='--', linewidth=2,
                   label=f'Média: {mean_degree:.4f}')
        ax1.axvline(median_degree, color='orange', linestyle='--', linewidth=2,
                   label=f'Mediana: {median_degree:.4f}')

        ax1.set_xlabel('Degree Centrality', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Número de Desenvolvedores', fontsize=12, fontweight='bold')
        ax1.set_title('(a) Distribuição de Degree Centrality', fontsize=13, fontweight='bold')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)

        # Subplot 2: Betweenness Centrality
        betw_vals = self.centrality['BetweennessCentrality'].values
        mean_betw = betw_vals.mean()
        median_betw = np.median(betw_vals)

        ax2.hist(betw_vals, bins=50, color='#457B9D', edgecolor='black', alpha=0.7)
        ax2.axvline(mean_betw, color='red', linestyle='--', linewidth=2,
                   label=f'Média: {mean_betw:.4f}')
        ax2.axvline(median_betw, color='orange', linestyle='--', linewidth=2,
                   label=f'Mediana: {median_betw:.4f}')

        ax2.set_xlabel('Betweenness Centrality', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Número de Desenvolvedores', fontsize=12, fontweight='bold')
        ax2.set_title('(b) Distribuição de Betweenness Centrality', fontsize=13, fontweight='bold')
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)

        # Subplot 3: Closeness Centrality
        clos_vals = self.centrality['ClosenessCentrality'].values
        mean_clos = clos_vals.mean()
        median_clos = np.median(clos_vals)

        ax3.hist(clos_vals, bins=50, color='#E76F51', edgecolor='black', alpha=0.7)
        ax3.axvline(mean_clos, color='red', linestyle='--', linewidth=2,
                   label=f'Média: {mean_clos:.4f}')
        ax3.axvline(median_clos, color='orange', linestyle='--', linewidth=2,
                   label=f'Mediana: {median_clos:.4f}')

        ax3.set_xlabel('Closeness Centrality', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Número de Desenvolvedores', fontsize=12, fontweight='bold')
        ax3.set_title('(c) Distribuição de Closeness Centrality', fontsize=13, fontweight='bold')
        ax3.legend(loc='upper right')
        ax3.grid(True, alpha=0.3)

        plt.suptitle('Figura 15: Comparação das Distribuições de Centralidade',
                    fontsize=15, fontweight='bold', y=1.02)
        plt.tight_layout()

        output_path = self.figures_dir / 'fig15_centrality_distributions.png'
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()
        print(f"  ✓ Salva: {output_path}")

    # ========================================================================
    # MAIN EXECUTION
    # ========================================================================

    def generate_all_figures(self):
        """Gera todas as 9 figuras principais"""
        print("\n" + "="*60)
        print("  GERANDO FIGURAS")
        print("="*60)

        self.figure1_degree_distribution()
        self.figure2_betweenness_distribution()
        self.figure3_closeness_distribution()
        self.figure4_pagerank_distribution()
        self.figure5_community_sizes()
        self.figure6_centrality_heatmap()
        self.figure7_graph_comparison()
        self.figure8_bridging_analysis()
        self.figure15_centrality_distributions()

        print(f"\n✓ Todas as 9 figuras salvas em: {self.figures_dir}")

    def generate_all_tables(self):
        """Gera todas as 6 tabelas"""
        print("\n" + "="*60)
        print("  GERANDO TABELAS")
        print("="*60)

        self.table1_structural_metrics()
        self.table2_top_developers()
        self.table3_community_summary()
        self.table4_bridging_developers()
        self.table5_separated_graphs()
        self.table6_correlation_matrix()

        print(f"\n✓ Todas as 6 tabelas salvas em: {self.tables_dir}")

    def run(self):
        """Executa geração completa"""
        print("\n" + "="*60)
        print("  VISUALIZADOR DE ANÁLISE DE GRAFOS")
        print("  PUC Minas - Teoria de Grafos")
        print("="*60)

        self.generate_all_figures()
        self.generate_all_tables()

        print("\n" + "="*60)
        print("  CONCLUÍDO")
        print("="*60)
        print(f"\nFiguras: {self.figures_dir}")
        print(f"Tabelas: {self.tables_dir}")
        print("\nPróximos passos:")
        print("  1. Verifique as figuras geradas")
        print("  2. Use python/export_latex.py para gerar tabelas LaTeX")
        print("  3. Use python/generate_report.py para gerar relatório markdown")


def main():
    """Função principal"""
    visualizer = GraphAnalysisVisualizer()
    visualizer.run()


if __name__ == '__main__':
    main()
