#!/usr/bin/env python3
"""
Gera relatório completo em Markdown.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime


class ReportGenerator:

    def __init__(self, output_dir='../output'):
        self.output_dir = Path(output_dir)
        self.load_data()

    def load_data(self):
        """Carrega dados necessários"""
        print("Carregando dados para relatório...")
        self.structural = pd.read_csv(self.output_dir / 'structural_metrics.csv')
        self.structural_dict = dict(zip(self.structural['Metric'], self.structural['Value']))

        self.centrality = pd.read_csv(self.output_dir / 'centrality_metrics.csv')
        self.communities = pd.read_csv(self.output_dir / 'community_assignments.csv')
        self.bridging = pd.read_csv(self.output_dir / 'bridging_developers.csv')

    def generate_report(self):
        """Gera o relatório completo"""
        print("Gerando relatório markdown...")

        report = []

        # Header
        report.append("# Relatório de Análise de Rede de Colaboração")
        report.append(f"\n**Data da Análise:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("\n**Projeto:** Análise de Colaboração em Repositórios GitHub")
        report.append("\n**Instituição:** PUC Minas - Teoria de Grafos\n")

        report.append("---\n")

        # Sumário Executivo
        report.append("## 📊 Sumário Executivo\n")
        report.append(f"- **Vértices (Desenvolvedores):** {self.structural_dict.get('Vertices', 0)}")
        report.append(f"- **Arestas (Interações):** {self.structural_dict.get('Edges', 0)}")
        report.append(f"- **Comunidades Detectadas:** {self.structural_dict.get('NumberOfCommunities', 0)}")
        report.append(f"- **Desenvolvedores-Ponte:** {self.structural_dict.get('BridgingTiesCount', 0)}")
        report.append(f"- **Modularidade (Q):** {self.structural_dict.get('Modularity', 0):.4f}\n")

        # Interpretação da densidade
        density = self.structural_dict.get('Density', 0)
        if density < 0.1:
            density_interp = "**Rede esparsa** - colaboração distribuída entre muitos desenvolvedores"
        elif density < 0.3:
            density_interp = "**Densidade moderada** - colaboração razoavelmente distribuída"
        else:
            density_interp = "**Rede densa** - alta colaboração entre desenvolvedores"

        report.append(f"- **Densidade:** {density:.6f} - {density_interp}\n")

        # Interpretação da modularidade
        modularity = self.structural_dict.get('Modularity', 0)
        if modularity > 0.7:
            mod_interp = "**Muito forte** - comunidades muito bem definidas"
        elif modularity > 0.3:
            mod_interp = "**Significativa** - estrutura clara de comunidades"
        else:
            mod_interp = "**Fraca** - comunidades pouco definidas"

        report.append(f"- **Interpretação da Modularidade:** {mod_interp}\n")

        report.append("\n---\n")

        # Métricas Estruturais
        report.append("## 🔍 Métricas Estruturais\n")
        report.append("### Coesão e Conectividade\n")
        report.append(f"- **Coeficiente de Aglomeração:** {self.structural_dict.get('ClusteringCoefficient', 0):.6f}")
        report.append(f"  - Mede tendência de formação de grupos coesos")
        report.append(f"- **Diâmetro da Rede:** {self.structural_dict.get('Diameter', 0)}")
        report.append(f"  - Maior caminho mais curto entre quaisquer dois nós")
        report.append(f"- **Distância Média:** {self.structural_dict.get('AverageDistance', 0):.6f}")
        report.append(f"  - Média de passos necessários para conectar desenvolvedores\n")

        # Assortatividade
        assortativity = self.structural_dict.get('Assortativity', 0)
        if assortativity > 0.3:
            assort_interp = "**Assortativa positiva** - desenvolvedores influentes colaboram entre si"
        elif assortativity < -0.3:
            assort_interp = "**Disassortativa** - desenvolvedores influentes colaboram com periféricos"
        else:
            assort_interp = "**Neutra** - sem preferência significativa de conexão"

        report.append(f"- **Assortatividade:** {assortativity:.6f}")
        report.append(f"  - {assort_interp}\n")

        report.append("\n---\n")

        # Top Desenvolvedores
        report.append("## 👥 Top 10 Desenvolvedores\n")
        report.append("### Por PageRank\n")
        top10_pr = self.centrality.nlargest(10, 'PageRank')

        report.append("| Rank | Desenvolvedor | PageRank | Degree | Betweenness |")
        report.append("|------|--------------|----------|---------|-------------|")
        for i, row in enumerate(top10_pr.itertuples(), 1):
            report.append(f"| {i} | {row.Label} | {row.PageRank:.6f} | {row.DegreeCentrality:.6f} | {row.BetweennessCentrality:.6f} |")

        report.append("\n---\n")

        # Comunidades
        report.append("## 🏘️ Análise de Comunidades\n")

        comm_sizes = self.communities.groupby('CommunityID').size().sort_values(ascending=False)
        report.append(f"**Total de comunidades detectadas:** {len(comm_sizes)}\n")

        report.append("### Distribuição de Tamanhos\n")
        report.append("| Comunidade | Membros | % do Total |")
        report.append("|------------|---------|------------|")

        total_members = len(self.communities)
        for comm_id, size in comm_sizes.items():
            pct = (size / total_members) * 100
            report.append(f"| Comunidade {comm_id} | {size} | {pct:.2f}% |")

        report.append("\n---\n")

        # Bridging Ties
        report.append("## 🌉 Desenvolvedores-Ponte (Bridging Ties)\n")
        report.append("Desenvolvedores que conectam diferentes comunidades, essenciais para o fluxo de informação.\n")

        merged_bridging = self.bridging.merge(
            self.centrality[['Vertex', 'PageRank']],
            on='Vertex'
        )
        top10_bridges = merged_bridging.nlargest(10, 'BridgingStrength')

        report.append("| Rank | Desenvolvedor | Comunidade | Bridging Strength | PageRank |")
        report.append("|------|--------------|------------|-------------------|----------|")
        for i, row in enumerate(top10_bridges.itertuples(), 1):
            report.append(f"| {i} | {row.Label} | {row.CommunityID} | {row.BridgingStrength:.6f} | {row.PageRank:.6f} |")

        report.append("\n---\n")

        # Visualizações
        report.append("## 📈 Visualizações Geradas\n")
        report.append("1. **Distribuição de Graus** - `figures/fig1_degree_distribution.png`")
        report.append("2. **Distribuição de PageRank** - `figures/fig2_pagerank_distribution.png`")
        report.append("3. **Tamanhos das Comunidades** - `figures/fig3_community_sizes.png`")
        report.append("4. **Heatmap de Centralidades** - `figures/fig4_centrality_heatmap.png`")
        report.append("5. **Comparação de Grafos** - `figures/fig5_graph_comparison.png`")
        report.append("6. **Análise de Bridging** - `figures/fig6_bridging_analysis.png`\n")

        report.append("\n---\n")

        # Conclusões
        report.append("## 💡 Conclusões\n")

        report.append("### Estrutura da Rede\n")
        report.append(f"A rede analisada apresenta {self.structural_dict.get('Vertices', 0)} desenvolvedores ")
        report.append(f"conectados por {self.structural_dict.get('Edges', 0)} interações. ")

        if modularity > 0.3:
            report.append(f"A modularidade de {modularity:.4f} indica uma estrutura de comunidades significativa, ")
            report.append(f"com {self.structural_dict.get('NumberOfCommunities', 0)} comunidades bem definidas.\n")
        else:
            report.append(f"A modularidade de {modularity:.4f} sugere uma estrutura de comunidades menos definida.\n")

        report.append("\n### Centralização e Influência\n")
        top_dev = top10_pr.iloc[0]
        report.append(f"O desenvolvedor mais central é **{top_dev['Label']}** com PageRank de {top_dev['PageRank']:.6f}. ")
        report.append("A análise de múltiplas métricas de centralidade permite identificar diferentes tipos de influência na rede.\n")

        report.append("\n### Coesão e Bridging\n")
        report.append(f"Foram identificados {len(self.bridging)} desenvolvedores-ponte que conectam diferentes comunidades. ")
        report.append("Esses desenvolvedores são cruciais para a transferência de conhecimento e coordenação entre grupos.\n")

        report.append("\n---\n")

        # Footer
        report.append("## 📚 Referências\n")
        report.append("- Brandes, U. (2001). A faster algorithm for betweenness centrality.")
        report.append("- Blondel, V. D., et al. (2008). Fast unfolding of communities (Louvain).")
        report.append("- Newman, M. E. J., & Girvan, M. (2004). Finding and evaluating community structure.")
        report.append("- Page, L., et al. (1999). The PageRank citation ranking.")
        report.append("- Guimerà, R., & Amaral, L. A. N. (2005). Functional cartography of complex metabolic networks.\n")

        report.append("\n---\n")
        report.append(f"\n*Relatório gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}*\n")

        # Salva o relatório
        output_path = self.output_dir / 'RELATORIO_COMPLETO.md'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))

        print(f"✓ Relatório salvo: {output_path}")


def main():
    generator = ReportGenerator()
    generator.generate_report()


if __name__ == '__main__':
    main()
