#!/usr/bin/env python3
"""
Análises temporais e classificação de papéis de desenvolvedores.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

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


class AdditionalAnalysis:

    def __init__(self, data_dir='../data', output_dir='../output'):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.figures_dir = self.output_dir / 'figures'
        self.tables_dir = self.output_dir / 'tables'

        # Garante que diretórios existem
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.tables_dir.mkdir(parents=True, exist_ok=True)

        self.load_data()

    def load_data(self):
        print("Carregando dados para análises adicionais...")

        # Força leitura com 7 colunas (CSV malformado tem coluna extra)
        self.interactions = pd.read_csv(
            self.data_dir / 'interactions.csv',
            names=['Source', 'Target', 'Type', 'Weight', 'EXTRA', 'Timestamp', 'Context'],
            skiprows=1  # Pula header original
        )

        # Remove coluna extra
        self.interactions = self.interactions.drop(columns=['EXTRA'])

        print(f"  ✓ Type corrigido: {self.interactions['Type'].iloc[0]}")

        # Converte timestamps com formato flexível
        self.interactions['Timestamp'] = pd.to_datetime(
            self.interactions['Timestamp'],
            format='mixed',
            errors='coerce'
        )

        # Dados de centralidade
        self.centrality = pd.read_csv(self.output_dir / 'centrality_metrics.csv')

        # Bridging developers
        bridging_path = self.output_dir / 'bridging_developers.csv'
        if bridging_path.exists():
            self.bridging = pd.read_csv(bridging_path)
        else:
            print("  ⚠ AVISO: bridging_developers.csv não encontrado")
            self.bridging = pd.DataFrame(columns=['Vertex', 'BridgingStrength'])

        # Comunidades
        self.communities = pd.read_csv(self.output_dir / 'community_assignments.csv')

        print(f"  ✓ {len(self.interactions)} interações carregadas")
        print(f"  ✓ {len(self.centrality)} desenvolvedores carregados")

    # ==================== ANÁLISE TEMPORAL ====================

    def figure7_temporal_nodes(self):
        """Figura 7: Série Temporal - Nós Ativos por Período"""
        print("\nGerando Figura 7: Nós Ativos por Período...")

        # Agrupa por mês
        self.interactions['YearMonth'] = self.interactions['Timestamp'].dt.to_period('M')

        # Conta nós únicos por mês (source + target)
        active_nodes_per_month = []

        for period in sorted(self.interactions['YearMonth'].unique()):
            period_data = self.interactions[self.interactions['YearMonth'] == period]
            active = set(period_data['Source']) | set(period_data['Target'])
            active_nodes_per_month.append({
                'Period': period.to_timestamp(),
                'ActiveNodes': len(active)
            })

        df_nodes = pd.DataFrame(active_nodes_per_month)

        # Plota
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(df_nodes['Period'], df_nodes['ActiveNodes'],
                marker='o', linewidth=2, markersize=6, color='#2E86AB')

        ax.fill_between(df_nodes['Period'], df_nodes['ActiveNodes'],
                        alpha=0.3, color='#2E86AB')

        ax.set_xlabel('Período (Mês)', fontsize=12)
        ax.set_ylabel('Número de Desenvolvedores Ativos', fontsize=12)
        ax.set_title('Figura 7: Evolução de Desenvolvedores Ativos ao Longo do Tempo',
                     fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Rotaciona labels do eixo X
        plt.xticks(rotation=45, ha='right')

        output_path = self.figures_dir / 'fig7_temporal_nodes.png'
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Salva: {output_path}")

        return df_nodes

    def figure8_temporal_interactions(self):
        """Figura 8: Série Temporal - Interações por Período"""
        print("\nGerando Figura 8: Interações por Período...")

        # Agrupa interações por mês
        interactions_per_month = self.interactions.groupby('YearMonth').size().reset_index(name='Count')
        interactions_per_month['Period'] = interactions_per_month['YearMonth'].apply(lambda x: x.to_timestamp())

        # Plota
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.bar(interactions_per_month['Period'], interactions_per_month['Count'],
               width=20, color='#A23B72', alpha=0.7, edgecolor='black')

        # Adiciona linha de tendência
        z = np.polyfit(range(len(interactions_per_month)),
                      interactions_per_month['Count'], 1)
        p = np.poly1d(z)
        ax.plot(interactions_per_month['Period'],
               p(range(len(interactions_per_month))),
               "--", color='red', linewidth=2, label='Tendência Linear')

        ax.set_xlabel('Período (Mês)', fontsize=12)
        ax.set_ylabel('Número de Interações', fontsize=12)
        ax.set_title('Figura 8: Evolução do Volume de Interações ao Longo do Tempo',
                     fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.xticks(rotation=45, ha='right')

        output_path = self.figures_dir / 'fig8_temporal_interactions.png'
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Salva: {output_path}")

        return interactions_per_month

    def figure9_activity_heatmap(self):
        """Figura 9: Heatmap de Atividade (Mês × Ano)"""
        print("\nGerando Figura 9: Heatmap de Atividade...")

        # Extrai ano e mês
        self.interactions['Year'] = self.interactions['Timestamp'].dt.year
        self.interactions['Month'] = self.interactions['Timestamp'].dt.month

        # Cria pivot table
        heatmap_data = self.interactions.groupby(['Year', 'Month']).size().reset_index(name='Count')
        pivot = heatmap_data.pivot(index='Month', columns='Year', values='Count')
        pivot = pivot.fillna(0)

        # Plota heatmap
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlOrRd',
                    linewidths=0.5, cbar_kws={'label': 'Número de Interações'},
                    ax=ax)

        ax.set_xlabel('Ano', fontsize=12)
        ax.set_ylabel('Mês', fontsize=12)
        ax.set_title('Figura 9: Heatmap de Atividade por Mês e Ano',
                     fontsize=14, fontweight='bold')

        # Labels dos meses
        month_labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                       'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        ax.set_yticklabels(month_labels, rotation=0)

        output_path = self.figures_dir / 'fig9_activity_heatmap.png'
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Salva: {output_path}")

    def figure11_monthly_detailed(self):
        """Figura 11: Análise Temporal Detalhada Mês a Mês (Duplo Eixo Y)"""
        print("\nGerando Figura 11: Análise Temporal Detalhada Mês a Mês...")

        # Agrupa por mês
        self.interactions['YearMonth'] = self.interactions['Timestamp'].dt.to_period('M')

        # Conta interações por mês
        interactions_per_month = self.interactions.groupby('YearMonth').size().reset_index(name='Interactions')
        interactions_per_month['Period'] = interactions_per_month['YearMonth'].apply(lambda x: x.to_timestamp())

        # Conta nós únicos por mês
        active_nodes_per_month = []
        for period in sorted(self.interactions['YearMonth'].unique()):
            period_data = self.interactions[self.interactions['YearMonth'] == period]
            active = set(period_data['Source']) | set(period_data['Target'])
            active_nodes_per_month.append({
                'Period': period.to_timestamp(),
                'ActiveNodes': len(active)
            })
        df_nodes = pd.DataFrame(active_nodes_per_month)

        # Merge dados
        monthly_data = interactions_per_month.merge(df_nodes, on='Period')

        # Cria figura com dois eixos Y
        fig, ax1 = plt.subplots(figsize=(16, 8))

        # Eixo Y1: Interações (barras)
        color1 = '#2E86AB'
        ax1.bar(monthly_data['Period'], monthly_data['Interactions'],
                width=20, alpha=0.6, color=color1, label='Interações', edgecolor='black')
        ax1.set_xlabel('Mês/Ano', fontsize=13, fontweight='bold')
        ax1.set_ylabel('Número de Interações', fontsize=13, fontweight='bold', color=color1)
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.grid(True, alpha=0.3, axis='y')

        # Eixo Y2: Desenvolvedores Ativos (linha)
        ax2 = ax1.twinx()
        color2 = '#E63946'
        ax2.plot(monthly_data['Period'], monthly_data['ActiveNodes'],
                marker='o', linewidth=3, markersize=8, color=color2,
                label='Desenvolvedores Ativos')
        ax2.set_ylabel('Desenvolvedores Ativos', fontsize=13, fontweight='bold', color=color2)
        ax2.tick_params(axis='y', labelcolor=color2)

        # Título
        plt.title('Figura 11: Evolução Mensal Detalhada - Interações vs Desenvolvedores Ativos',
                 fontsize=15, fontweight='bold', pad=20)

        # Rotaciona labels do eixo X
        ax1.tick_params(axis='x', rotation=45)
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Adiciona anotações nos picos
        max_interactions_idx = monthly_data['Interactions'].idxmax()
        max_nodes_idx = monthly_data['ActiveNodes'].idxmax()

        # Anota pico de interações
        ax1.annotate(f"Pico: {monthly_data.loc[max_interactions_idx, 'Interactions']} interações",
                    xy=(monthly_data.loc[max_interactions_idx, 'Period'],
                        monthly_data.loc[max_interactions_idx, 'Interactions']),
                    xytext=(20, 20), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'),
                    fontsize=10, fontweight='bold')

        # Anota pico de desenvolvedores
        ax2.annotate(f"Pico: {monthly_data.loc[max_nodes_idx, 'ActiveNodes']} devs",
                    xy=(monthly_data.loc[max_nodes_idx, 'Period'],
                        monthly_data.loc[max_nodes_idx, 'ActiveNodes']),
                    xytext=(-60, -30), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.5', fc='lightgreen', alpha=0.7),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'),
                    fontsize=10, fontweight='bold')

        # Legendas combinadas
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)

        # Adiciona grid secundário
        ax1.grid(True, alpha=0.2, linestyle='--', axis='x')

        # Layout ajustado
        fig.tight_layout()

        output_path = self.figures_dir / 'fig11_monthly_detailed.png'
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()
        print(f"  ✓ Salva: {output_path}")

        return monthly_data

    def table_temporal_stats(self):
        """Tabela: Estatísticas Temporais"""
        print("\nGerando Tabela: Estatísticas Temporais...")

        # Calcula estatísticas
        interactions_per_month = self.interactions.groupby('YearMonth').size()

        # Identifica picos e vales
        peak_month = interactions_per_month.idxmax()
        valley_month = interactions_per_month.idxmin()

        stats = {
            'Métrica': [
                'Período Analisado (Início)',
                'Período Analisado (Fim)',
                'Total de Meses',
                'Média de Interações/Mês',
                'Desvio Padrão',
                'Mês com Maior Atividade',
                'Pico de Atividade',
                'Mês com Menor Atividade',
                'Vale de Atividade',
                'Taxa de Crescimento Mensal (%)'
            ],
            'Valor': [
                self.interactions['Timestamp'].min().strftime('%Y-%m'),
                self.interactions['Timestamp'].max().strftime('%Y-%m'),
                len(interactions_per_month),
                f"{interactions_per_month.mean():.2f}",
                f"{interactions_per_month.std():.2f}",
                peak_month.to_timestamp().strftime('%Y-%m'),
                interactions_per_month.max(),
                valley_month.to_timestamp().strftime('%Y-%m'),
                interactions_per_month.min(),
                f"{((interactions_per_month.iloc[-1] / interactions_per_month.iloc[0]) - 1) * 100:.2f}%"
            ]
        }

        df_stats = pd.DataFrame(stats)

        output_path = self.tables_dir / 'table7_temporal_stats.csv'
        df_stats.to_csv(output_path, index=False)
        print(f"  ✓ Salva: {output_path}")

        return df_stats

    # ==================== CLASSIFICAÇÃO DE PAPÉIS ====================

    def classify_roles(self):
        """Classifica desenvolvedores em Core/Peripheral/Connector"""
        print("\nClassificando desenvolvedores em papéis...")

        # Merge com bridging
        merged = self.centrality.copy()

        if not self.bridging.empty:
            merged = merged.merge(
                self.bridging[['Vertex', 'BridgingStrength']],
                on='Vertex',
                how='left'
            )
        else:
            merged['BridgingStrength'] = 0.0

        merged['BridgingStrength'] = merged['BridgingStrength'].fillna(0)

        # Calcula percentis
        q1_degree = merged['DegreeCentrality'].quantile(0.25)
        q3_degree = merged['DegreeCentrality'].quantile(0.75)

        q1_pr = merged['PageRank'].quantile(0.25)
        q3_pr = merged['PageRank'].quantile(0.75)

        q3_betweenness = merged['BetweennessCentrality'].quantile(0.75)

        # Função de classificação
        def classify(row):
            # CONNECTOR: Alto betweenness OU alto bridging strength
            if (row['BetweennessCentrality'] > q3_betweenness or
                row['BridgingStrength'] > 0):
                return 'Connector'

            # CORE: Alto degree E alto PageRank
            elif (row['DegreeCentrality'] > q3_degree and
                  row['PageRank'] > q3_pr):
                return 'Core'

            # PERIPHERAL: Baixo degree E baixo PageRank
            elif (row['DegreeCentrality'] < q1_degree and
                  row['PageRank'] < q1_pr):
                return 'Peripheral'

            # INTERMEDIÁRIO: Não se encaixa claramente em nenhum
            else:
                return 'Intermediate'

        merged['Role'] = merged.apply(classify, axis=1)

        print(f"  ✓ Classificação concluída")
        print(f"    - Core: {(merged['Role'] == 'Core').sum()}")
        print(f"    - Peripheral: {(merged['Role'] == 'Peripheral').sum()}")
        print(f"    - Connector: {(merged['Role'] == 'Connector').sum()}")
        print(f"    - Intermediate: {(merged['Role'] == 'Intermediate').sum()}")

        return merged

    def figure10_role_distribution(self, role_data):
        """Figura 10: Distribuição de Papéis"""
        print("\nGerando Figura 10: Distribuição de Papéis...")

        # Conta papéis
        role_counts = role_data['Role'].value_counts()
        role_pcts = (role_counts / len(role_data) * 100).round(2)

        # Cores customizadas
        colors = {
            'Core': '#E63946',
            'Connector': '#F1A208',
            'Peripheral': '#457B9D',
            'Intermediate': '#A8DADC'
        }

        # Cria figura com 2 subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # Subplot 1: Gráfico de pizza
        wedges, texts, autotexts = ax1.pie(
            role_counts,
            labels=role_counts.index,
            autopct='%1.1f%%',
            colors=[colors.get(role, '#CCCCCC') for role in role_counts.index],
            startangle=90,
            textprops={'fontsize': 12}
        )

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax1.set_title('Proporção de Papéis na Rede', fontsize=14, fontweight='bold')

        # Subplot 2: Gráfico de barras
        bars = ax2.bar(role_counts.index, role_counts.values,
                       color=[colors.get(role, '#CCCCCC') for role in role_counts.index],
                       edgecolor='black', linewidth=1.5)

        # Adiciona valores no topo das barras
        for i, (bar, count, pct) in enumerate(zip(bars, role_counts.values, role_pcts.values)):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{count}\n({pct}%)',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')

        ax2.set_ylabel('Número de Desenvolvedores', fontsize=12)
        ax2.set_title('Contagem por Papel', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')

        plt.suptitle('Figura 10: Classificação de Desenvolvedores por Papel na Rede',
                    fontsize=16, fontweight='bold', y=1.02)

        output_path = self.figures_dir / 'fig10_role_distribution.png'
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Salva: {output_path}")

    def table_role_classification(self, role_data):
        """Tabela: Classificação Completa de Papéis"""
        print("\nGerando Tabela: Classificação de Papéis...")

        # Seleciona colunas relevantes
        table = role_data[['Vertex', 'Label', 'Role', 'DegreeCentrality',
                          'BetweennessCentrality', 'ClosenessCentrality',
                          'PageRank', 'BridgingStrength']].copy()

        # Ordena por papel (Core > Connector > Intermediate > Peripheral) e PageRank
        role_order = {'Core': 0, 'Connector': 1, 'Intermediate': 2, 'Peripheral': 3}
        table['RoleOrder'] = table['Role'].map(role_order)
        table = table.sort_values(['RoleOrder', 'PageRank'], ascending=[True, False])
        table = table.drop('RoleOrder', axis=1)

        # Renomeia colunas
        table.columns = ['Vertex', 'Desenvolvedor', 'Papel', 'Degree',
                        'Betweenness', 'Closeness', 'PageRank', 'Bridging Strength']

        output_path = self.tables_dir / 'table8_role_classification.csv'
        table.to_csv(output_path, index=False)
        print(f"  ✓ Salva: {output_path}")

        return table

    def table_role_statistics(self, role_data):
        """Tabela: Estatísticas por Papel"""
        print("\nGerando Tabela: Estatísticas por Papel...")

        # Agrupa por papel e calcula estatísticas
        stats = role_data.groupby('Role').agg({
            'Vertex': 'count',
            'DegreeCentrality': ['mean', 'median'],
            'BetweennessCentrality': ['mean', 'median'],
            'PageRank': ['mean', 'median'],
            'BridgingStrength': ['mean', 'median']
        }).round(6)

        # Flatten multi-index columns
        stats.columns = ['_'.join(col).strip() for col in stats.columns.values]
        stats = stats.reset_index()

        # Renomeia
        stats.columns = [
            'Papel', 'Quantidade',
            'Degree Médio', 'Degree Mediano',
            'Betweenness Médio', 'Betweenness Mediano',
            'PageRank Médio', 'PageRank Mediano',
            'Bridging Médio', 'Bridging Mediano'
        ]

        # Adiciona percentual
        total = stats['Quantidade'].sum()
        stats['% do Total'] = (stats['Quantidade'] / total * 100).round(2)

        # Reordena colunas
        cols = ['Papel', 'Quantidade', '% do Total'] + [c for c in stats.columns if c not in ['Papel', 'Quantidade', '% do Total']]
        stats = stats[cols]

        output_path = self.tables_dir / 'table9_role_statistics.csv'
        stats.to_csv(output_path, index=False)
        print(f"  ✓ Salva: {output_path}")

        return stats

    # ==================== ANÁLISE DE VOLUME DE ATIVIDADE ====================

    def table10_developer_activity_volume(self, top_n=30):
        """Tabela 10: Ranking de Desenvolvedores por Volume de Atividade"""
        print(f"\nGerando Tabela 10: Top {top_n} Desenvolvedores por Volume de Atividade...")

        # Conta interações por desenvolvedor (apenas como Source - quem fez a ação)
        activity_counts = self.interactions.groupby('Source').agg({
            'Type': 'count',  # Total de interações
        }).rename(columns={'Type': 'Total'})

        # Conta por tipo de interação
        type_counts = self.interactions.groupby(['Source', 'Type']).size().unstack(fill_value=0)

        # Merge
        activity = activity_counts.join(type_counts, how='left').fillna(0)

        # Garante que todas as colunas de tipo existam
        for interaction_type in ['COMMENT_ISSUE', 'COMMENT_PR', 'ISSUE_CLOSE',
                                'PR_REVIEW', 'PR_APPROVAL', 'PR_MERGE']:
            if interaction_type not in activity.columns:
                activity[interaction_type] = 0

        # Seleciona e renomeia colunas
        activity = activity.reset_index()
        activity.columns.name = None
        activity = activity.rename(columns={'Source': 'Developer'})

        # Ordena por total
        activity = activity.sort_values('Total', ascending=False)

        # Adiciona ranking
        activity.insert(0, 'Rank', range(1, len(activity) + 1))

        # Seleciona top N
        top_activity = activity.head(top_n)

        # Reordena colunas
        cols_order = ['Rank', 'Developer', 'Total',
                     'COMMENT_ISSUE', 'COMMENT_PR', 'ISSUE_CLOSE',
                     'PR_REVIEW', 'PR_APPROVAL', 'PR_MERGE']

        # Garante que todas as colunas existem
        for col in cols_order:
            if col not in top_activity.columns:
                top_activity[col] = 0

        top_activity = top_activity[cols_order]

        # Renomeia para português
        top_activity.columns = [
            'Rank', 'Desenvolvedor', 'Total',
            'Comentários Issue', 'Comentários PR', 'Fechamentos',
            'Reviews', 'Aprovações', 'Merges'
        ]

        # Converte para int
        int_cols = ['Total', 'Comentários Issue', 'Comentários PR', 'Fechamentos',
                   'Reviews', 'Aprovações', 'Merges']
        for col in int_cols:
            top_activity[col] = top_activity[col].astype(int)

        output_path = self.tables_dir / 'table10_developer_activity_volume.csv'
        top_activity.to_csv(output_path, index=False)
        print(f"  ✓ Salva: {output_path}")
        print(f"  ✓ Top 3 mais ativos:")
        for i in range(min(3, len(top_activity))):
            dev = top_activity.iloc[i]
            print(f"    {i+1}. {dev['Desenvolvedor']}: {dev['Total']} interações")

        return top_activity

    def figure12_top_developers_activity(self, top_n=20):
        """Figura 12: Top Desenvolvedores por Volume Total de Atividade"""
        print(f"\nGerando Figura 12: Top {top_n} Desenvolvedores por Atividade...")

        # Conta interações por desenvolvedor
        activity_counts = self.interactions.groupby('Source').size().reset_index(name='Total')
        activity_counts = activity_counts.sort_values('Total', ascending=True).tail(top_n)

        # Cria gráfico de barras horizontais
        fig, ax = plt.subplots(figsize=(12, 10))

        bars = ax.barh(activity_counts['Source'], activity_counts['Total'],
                      color='#2A9D8F', edgecolor='black', linewidth=1.2)

        # Adiciona valores nas barras
        for i, (dev, total) in enumerate(zip(activity_counts['Source'], activity_counts['Total'])):
            ax.text(total + 1, i, str(total),
                   va='center', ha='left', fontsize=10, fontweight='bold')

        ax.set_xlabel('Número Total de Interações', fontsize=12, fontweight='bold')
        ax.set_ylabel('Desenvolvedor', fontsize=12, fontweight='bold')
        ax.set_title(f'Figura 12: Top {top_n} Desenvolvedores por Volume de Atividade',
                    fontsize=14, fontweight='bold', pad=15)
        ax.grid(True, alpha=0.3, axis='x')

        # Destaca top 3
        for i in range(len(bars)):
            if i >= len(bars) - 3:  # Últimos 3 (mais ativos)
                bars[i].set_color('#E63946')

        output_path = self.figures_dir / 'fig12_top_developers_activity.png'
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()
        print(f"  ✓ Salva: {output_path}")

    def figure13_activity_composition(self, top_n=15):
        """Figura 13: Composição de Atividade dos Top Desenvolvedores"""
        print(f"\nGerando Figura 13: Composição de Atividade (Top {top_n})...")

        # USA A MESMA LÓGICA DA TABELA 10 (que funciona!)
        # Conta por tipo de interação (igual linha 534 da table10)
        type_counts = self.interactions.groupby(['Source', 'Type']).size().unstack(fill_value=0)

        # Pega top N desenvolvedores por total
        type_counts['Total'] = type_counts.sum(axis=1)
        top_devs = type_counts.nlargest(top_n, 'Total')
        pivot = top_devs.drop('Total', axis=1)

        # Ordena tipos (do mais leve ao mais pesado)
        type_order = ['COMMENT_ISSUE', 'COMMENT_PR', 'ISSUE_CLOSE',
                     'PR_REVIEW', 'PR_APPROVAL', 'PR_MERGE']
        available_types = [col for col in type_order if col in pivot.columns]

        if len(available_types) == 0:
            print("  ⚠ AVISO: Sem tipos válidos para figura 13")
            return

        pivot = pivot[available_types]

        # Cores por tipo
        colors = {
            'COMMENT_ISSUE': '#A8DADC',
            'COMMENT_PR': '#457B9D',
            'ISSUE_CLOSE': '#1D3557',
            'PR_REVIEW': '#F1A208',
            'PR_APPROVAL': '#E76F51',
            'PR_MERGE': '#E63946'
        }

        # Cria gráfico de barras empilhadas
        fig, ax = plt.subplots(figsize=(14, 10))

        pivot.plot(kind='barh', stacked=True, ax=ax,
                  color=[colors.get(col, '#CCCCCC') for col in pivot.columns],
                  edgecolor='black', linewidth=0.5)

        ax.set_xlabel('Número de Interações', fontsize=12, fontweight='bold')
        ax.set_ylabel('Desenvolvedor', fontsize=12, fontweight='bold')
        ax.set_title(f'Figura 13: Composição de Atividade por Tipo (Top {top_n} Desenvolvedores)',
                    fontsize=14, fontweight='bold', pad=15)
        ax.legend(title='Tipo de Interação', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3, axis='x')

        output_path = self.figures_dir / 'fig13_activity_composition.png'
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()
        print(f"  ✓ Salva: {output_path}")

    def figure14_activity_distribution(self):
        """Figura 14: Distribuição de Atividade entre Desenvolvedores"""
        print(f"\nGerando Figura 14: Distribuição de Atividade...")

        # Conta interações por desenvolvedor
        activity = self.interactions.groupby('Source').size().sort_values(ascending=False)

        # Estatísticas
        mean_val = activity.mean()
        median_val = activity.median()
        p75 = activity.quantile(0.75)
        p90 = activity.quantile(0.90)
        p95 = activity.quantile(0.95)

        # Concentração: top 10% concentra quanto % das interações?
        top10_devs = int(len(activity) * 0.1)
        top10_interactions = activity.head(top10_devs).sum()
        total_interactions = activity.sum()
        concentration = (top10_interactions / total_interactions) * 100

        # Cria figura com 2 subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # Subplot 1: Histograma
        ax1.hist(activity.values, bins=50, color='#2A9D8F', edgecolor='black', alpha=0.7)
        ax1.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Média: {mean_val:.1f}')
        ax1.axvline(median_val, color='orange', linestyle='--', linewidth=2, label=f'Mediana: {median_val:.1f}')
        ax1.axvline(p90, color='purple', linestyle='--', linewidth=2, label=f'P90 (90% abaixo): {p90:.1f}')

        ax1.set_xlabel('Número de Interações', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Número de Desenvolvedores', fontsize=12, fontweight='bold')
        ax1.set_title('Histograma: Distribuição de Atividade', fontsize=13, fontweight='bold')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)

        # Subplot 2: Curva de Lorenz (concentração)
        sorted_activity = np.sort(activity.values)
        cumsum_activity = np.cumsum(sorted_activity)
        cumsum_activity = cumsum_activity / cumsum_activity[-1]  # Normaliza para [0, 1]
        lorenz_x = np.linspace(0, 1, len(cumsum_activity))

        ax2.plot(lorenz_x, cumsum_activity, color='#E63946', linewidth=2, label='Curva de Lorenz')
        ax2.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Igualdade Perfeita')
        ax2.fill_between(lorenz_x, cumsum_activity, lorenz_x, alpha=0.3, color='#E63946')

        ax2.set_xlabel('Proporção de Desenvolvedores', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Proporção de Interações', fontsize=12, fontweight='bold')
        ax2.set_title('Curva de Lorenz: Concentração de Atividade', fontsize=13, fontweight='bold')
        ax2.legend(loc='lower right')
        ax2.grid(True, alpha=0.3)

        # Texto com estatísticas (canto superior esquerdo, longe da legenda)
        stats_text = f"Top 10% concentra {concentration:.1f}% das interações\n"
        stats_text += f"Total: {len(activity)} desenvolvedores, {total_interactions} interações"
        ax2.text(0.02, 0.70, stats_text, transform=ax2.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                fontsize=10, fontweight='bold')

        plt.suptitle('Figura 14: Distribuição de Atividade entre Desenvolvedores',
                    fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()

        output_path = self.figures_dir / 'fig14_activity_distribution.png'
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()
        print(f"  ✓ Salva: {output_path}")
        print(f"  ✓ Top 10% ({top10_devs} devs) concentra {concentration:.1f}% das interações")

    def analyze_community_cohesion(self):
        """Analisa densidade intra vs inter-comunidades"""
        print(f"\nAnalisando coesão das comunidades...")

        # Carrega dados de comunidades
        communities = pd.read_csv(self.output_dir / 'community_assignments.csv')

        # Cria mapa de vértice -> comunidade
        vertex_to_comm = dict(zip(communities['Label'], communities['CommunityID']))

        # Calcula arestas intra e inter-comunidades
        community_stats = {}

        for comm_id in communities['CommunityID'].unique():
            comm_members = set(communities[communities['CommunityID'] == comm_id]['Label'])

            # Filtra interações envolvendo membros da comunidade
            comm_interactions = self.interactions[
                (self.interactions['Source'].isin(comm_members)) |
                (self.interactions['Target'].isin(comm_members))
            ]

            # Conta arestas intra-comunidade (ambos source e target na mesma comunidade)
            intra_edges = len(comm_interactions[
                (comm_interactions['Source'].isin(comm_members)) &
                (comm_interactions['Target'].isin(comm_members))
            ])

            # Conta arestas inter-comunidade (um dentro, outro fora)
            inter_edges = len(comm_interactions[
                (comm_interactions['Source'].isin(comm_members)) &
                (~comm_interactions['Target'].isin(comm_members))
            ]) + len(comm_interactions[
                (~comm_interactions['Source'].isin(comm_members)) &
                (comm_interactions['Target'].isin(comm_members))
            ])

            # Calcula densidades
            n = len(comm_members)
            max_intra = n * (n - 1)  # arestas possíveis dentro
            density_intra = intra_edges / max_intra if max_intra > 0 else 0

            # Razão intra/inter (quanto maior, mais coesa a comunidade)
            ratio = intra_edges / inter_edges if inter_edges > 0 else float('inf')

            community_stats[comm_id] = {
                'Size': n,
                'IntraEdges': intra_edges,
                'InterEdges': inter_edges,
                'IntraDensity': density_intra,
                'IntraInterRatio': ratio
            }

        # Converte para DataFrame
        stats_df = pd.DataFrame.from_dict(community_stats, orient='index')
        stats_df.index.name = 'CommunityID'
        stats_df = stats_df.reset_index()
        stats_df = stats_df.sort_values('Size', ascending=False)

        # Salva tabela
        output_path = self.tables_dir / 'table11_community_cohesion.csv'
        stats_df.to_csv(output_path, index=False, float_format='%.6f')
        print(f"  ✓ Tabela salva: {output_path}")

        # Gera figura comparativa (Top 20 comunidades)
        top20 = stats_df.head(20)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # Subplot 1: Densidade Intra-comunidade
        ax1.barh(range(len(top20)), top20['IntraDensity'], color='#2A9D8F', alpha=0.7)
        ax1.set_yticks(range(len(top20)))
        ax1.set_yticklabels([f"C{c} (n={s})" for c, s in zip(top20['CommunityID'], top20['Size'])])
        ax1.set_xlabel('Densidade Intra-comunidade', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Comunidade (tamanho)', fontsize=11, fontweight='bold')
        ax1.set_title('(a) Densidade Interna das Comunidades', fontsize=12, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        ax1.invert_yaxis()

        # Subplot 2: Razão Intra/Inter
        # Limita valores infinitos para visualização
        ratios = top20['IntraInterRatio'].replace([float('inf')], top20['IntraInterRatio'][top20['IntraInterRatio'] != float('inf')].max() * 1.5)

        ax2.barh(range(len(top20)), ratios, color='#E76F51', alpha=0.7)
        ax2.set_yticks(range(len(top20)))
        ax2.set_yticklabels([f"C{c} (n={s})" for c, s in zip(top20['CommunityID'], top20['Size'])])
        ax2.set_xlabel('Razão Intra/Inter-comunidade', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Comunidade (tamanho)', fontsize=11, fontweight='bold')
        ax2.set_title('(b) Coesão: Arestas Internas vs Externas', fontsize=12, fontweight='bold')
        ax2.axvline(1.0, color='red', linestyle='--', linewidth=2, label='Razão = 1.0 (limite)')
        ax2.legend()
        ax2.grid(axis='x', alpha=0.3)
        ax2.invert_yaxis()

        plt.suptitle('Figura 15: Análise de Coesão das Comunidades', fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()

        fig_path = self.figures_dir / 'fig15_community_cohesion.png'
        plt.savefig(fig_path, bbox_inches='tight', dpi=300)
        plt.close()
        print(f"  ✓ Figura salva: {fig_path}")

        # Estatísticas globais
        avg_intra_density = stats_df['IntraDensity'].mean()
        avg_ratio = stats_df[stats_df['IntraInterRatio'] != float('inf')]['IntraInterRatio'].mean()

        print(f"  ✓ Densidade intra-comunidade média: {avg_intra_density:.6f}")
        print(f"  ✓ Razão intra/inter média: {avg_ratio:.2f}")

        return stats_df

    def analyze_community_function(self):
        """Caracterização funcional: tipos de interação por comunidade"""
        print(f"\nAnalisando caracterização funcional das comunidades...")

        # Carrega dados de comunidades
        communities = pd.read_csv(self.output_dir / 'community_assignments.csv')
        vertex_to_comm = dict(zip(communities['Label'], communities['CommunityID']))

        # Para cada comunidade, conta tipos de interação
        functional_data = []

        for comm_id in communities['CommunityID'].unique():
            comm_members = set(communities[communities['CommunityID'] == comm_id]['Label'])

            # Filtra interações DENTRO da comunidade
            comm_interactions = self.interactions[
                (self.interactions['Source'].isin(comm_members)) &
                (self.interactions['Target'].isin(comm_members))
            ]

            if len(comm_interactions) == 0:
                continue

            # Conta por tipo
            type_counts = comm_interactions['Type'].value_counts()
            total = len(comm_interactions)

            functional_data.append({
                'CommunityID': comm_id,
                'Size': len(comm_members),
                'TotalInteractions': total,
                'COMMENT_ISSUE_pct': (type_counts.get('COMMENT_ISSUE', 0) / total) * 100,
                'COMMENT_PR_pct': (type_counts.get('COMMENT_PR', 0) / total) * 100,
                'ISSUE_CLOSE_pct': (type_counts.get('ISSUE_CLOSE', 0) / total) * 100,
                'PR_REVIEW_pct': (type_counts.get('PR_REVIEW', 0) / total) * 100,
                'PR_APPROVAL_pct': (type_counts.get('PR_APPROVAL', 0) / total) * 100,
                'PR_MERGE_pct': (type_counts.get('PR_MERGE', 0) / total) * 100,
            })

        func_df = pd.DataFrame(functional_data)
        func_df = func_df.sort_values('TotalInteractions', ascending=False)

        # Classifica comunidades por função dominante
        interaction_cols = ['COMMENT_ISSUE_pct', 'COMMENT_PR_pct', 'ISSUE_CLOSE_pct',
                           'PR_REVIEW_pct', 'PR_APPROVAL_pct', 'PR_MERGE_pct']
        func_df['DominantType'] = func_df[interaction_cols].idxmax(axis=1).str.replace('_pct', '')

        # Salva tabela
        output_path = self.tables_dir / 'table12_community_function.csv'
        func_df.to_csv(output_path, index=False, float_format='%.2f')
        print(f"  ✓ Tabela salva: {output_path}")

        # Gera figura de heatmap (Top 15 comunidades por volume)
        top15 = func_df.head(15)

        # Prepara matriz para heatmap
        heatmap_data = top15[interaction_cols].values
        labels = [f"C{c}\n(n={s})" for c, s in zip(top15['CommunityID'], top15['Size'])]

        fig, ax = plt.subplots(figsize=(12, 10))

        im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')

        # Configurações dos eixos
        ax.set_xticks(range(len(interaction_cols)))
        ax.set_xticklabels(['Comment\nIssue', 'Comment\nPR', 'Issue\nClose',
                           'PR\nReview', 'PR\nApproval', 'PR\nMerge'],
                          fontsize=10, fontweight='bold')
        ax.set_yticks(range(len(top15)))
        ax.set_yticklabels(labels, fontsize=9)

        # Adiciona valores no heatmap
        for i in range(len(top15)):
            for j in range(len(interaction_cols)):
                text = ax.text(j, i, f'{heatmap_data[i, j]:.1f}%',
                             ha="center", va="center", color="black", fontsize=8)

        ax.set_title('Figura 16: Caracterização Funcional das Comunidades (Top 15)\n% de cada tipo de interação dentro da comunidade',
                    fontsize=13, fontweight='bold', pad=20)

        # Colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Percentual (%)', fontsize=11, fontweight='bold')

        plt.tight_layout()

        fig_path = self.figures_dir / 'fig16_community_function.png'
        plt.savefig(fig_path, bbox_inches='tight', dpi=300)
        plt.close()
        print(f"  ✓ Figura salva: {fig_path}")

        # Mostra distribuição de tipos dominantes
        dominant_counts = func_df['DominantType'].value_counts()
        print(f"\n  Distribuição de funções dominantes:")
        for dtype, count in dominant_counts.items():
            print(f"    {dtype}: {count} comunidades")

        return func_df

    def run_all(self):
        """Executa todas as análises adicionais"""
        print("\n" + "="*70)
        print("ANÁLISES ADICIONAIS: TEMPORAL, PAPÉIS E VOLUME DE ATIVIDADE")
        print("="*70)

        # Análises Temporais
        print("\n--- ANÁLISE TEMPORAL ---")
        self.figure7_temporal_nodes()
        self.figure8_temporal_interactions()
        self.figure9_activity_heatmap()
        self.figure11_monthly_detailed()
        self.table_temporal_stats()

        # Classificação de Papéis
        print("\n--- CLASSIFICAÇÃO DE PAPÉIS ---")
        role_data = self.classify_roles()
        self.figure10_role_distribution(role_data)
        self.table_role_classification(role_data)
        self.table_role_statistics(role_data)

        # Análise de Volume de Atividade
        print("\n--- VOLUME DE ATIVIDADE ---")
        self.table10_developer_activity_volume(top_n=30)
        self.figure12_top_developers_activity(top_n=20)
        self.figure13_activity_composition(top_n=15)
        self.figure14_activity_distribution()

        # Análises de Comunidades
        print("\n--- ANÁLISE DE COMUNIDADES ---")
        self.analyze_community_cohesion()
        self.analyze_community_function()

        print("\n" + "="*70)
        print("✓ ANÁLISES ADICIONAIS CONCLUÍDAS!")
        print("="*70)
        print("\nArquivos gerados:")
        print("  Figuras:")
        print("    • figures/fig7_temporal_nodes.png")
        print("    • figures/fig8_temporal_interactions.png")
        print("    • figures/fig9_activity_heatmap.png")
        print("    • figures/fig10_role_distribution.png")
        print("    • figures/fig11_monthly_detailed.png")
        print("    • figures/fig12_top_developers_activity.png")
        print("    • figures/fig13_activity_composition.png")
        print("    • figures/fig14_activity_distribution.png")
        print("    • figures/fig15_community_cohesion.png")
        print("    • figures/fig16_community_function.png")
        print("  Tabelas:")
        print("    • tables/table7_temporal_stats.csv")
        print("    • tables/table8_role_classification.csv")
        print("    • tables/table9_role_statistics.csv")
        print("    • tables/table10_developer_activity_volume.csv")
        print("    • tables/table11_community_cohesion.csv")
        print("    • tables/table12_community_function.csv")


def main():
    analyzer = AdditionalAnalysis()
    analyzer.run_all()


if __name__ == '__main__':
    main()
