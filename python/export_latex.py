#!/usr/bin/env python3
"""
Exporta tabelas CSV para formato LaTeX.
"""

import pandas as pd
from pathlib import Path


class LaTeXExporter:

    def __init__(self, output_dir='../output'):
        self.output_dir = Path(output_dir)
        self.tables_dir = self.output_dir / 'tables'

    def export_all_tables(self):
        print("\n" + "="*60)
        print("  EXPORTANDO TABELAS PARA LATEX")
        print("="*60)

        latex_content = []

        # Header
        latex_content.append("% Tabelas geradas automaticamente")
        latex_content.append("% Compilar com pdflatex ou xelatex\n")
        latex_content.append("\\documentclass{article}")
        latex_content.append("\\usepackage[utf8]{inputenc}")
        latex_content.append("\\usepackage[T1]{fontenc}")
        latex_content.append("\\usepackage[portuguese]{babel}")
        latex_content.append("\\usepackage{booktabs}")
        latex_content.append("\\usepackage{longtable}")
        latex_content.append("\\usepackage{geometry}")
        latex_content.append("\\geometry{margin=2cm}")
        latex_content.append("\n\\begin{document}\n")

        # Tabela 1: Métricas Estruturais
        print("\nProcessando Tabela 1: Métricas Estruturais...")
        df1 = pd.read_csv(self.tables_dir / 'table1_structural_metrics.csv')
        latex_content.append("\\section*{Tabela 1: Métricas Estruturais Gerais}")
        latex_content.append(df1.to_latex(index=False, escape=False,
                                          column_format='ll',
                                          caption="Métricas Estruturais do Grafo Integrado",
                                          label="tab:structural"))
        latex_content.append("\n\\clearpage\n")

        # Tabela 2: Top Desenvolvedores
        print("Processando Tabela 2: Top Desenvolvedores...")
        df2 = pd.read_csv(self.tables_dir / 'table2_top_developers.csv')
        latex_content.append("\\section*{Tabela 2: Top 10 Desenvolvedores por Centralidade}")
        latex_content.append(df2.to_latex(index=False, escape=False,
                                          column_format='clrrrr',
                                          caption="Top 10 Desenvolvedores por Métricas de Centralidade",
                                          label="tab:topdevs"))
        latex_content.append("\n\\clearpage\n")

        # Tabela 3: Comunidades
        print("Processando Tabela 3: Resumo das Comunidades...")
        df3 = pd.read_csv(self.tables_dir / 'table3_communities.csv')
        latex_content.append("\\section*{Tabela 3: Resumo das Comunidades}")
        latex_content.append(df3.to_latex(index=False, escape=False,
                                          column_format='crll',
                                          caption="Resumo das Comunidades Detectadas",
                                          label="tab:communities"))
        latex_content.append("\n\\clearpage\n")

        # Tabela 4: Bridging Developers
        print("Processando Tabela 4: Bridging Developers...")
        df4 = pd.read_csv(self.tables_dir / 'table4_bridging_developers.csv')
        latex_content.append("\\section*{Tabela 4: Top 10 Desenvolvedores-Ponte}")
        latex_content.append(df4.to_latex(index=False, escape=False,
                                          column_format='clcrrr',
                                          caption="Top 10 Desenvolvedores-Ponte (Bridging Ties)",
                                          label="tab:bridging"))
        latex_content.append("\n\\clearpage\n")

        # Tabela 5: Grafos Separados
        print("Processando Tabela 5: Grafos Separados...")
        df5 = pd.read_csv(self.tables_dir / 'table5_separated_graphs.csv')
        latex_content.append("\\section*{Tabela 5: Estatísticas dos Grafos Separados}")
        latex_content.append(df5.to_latex(index=False, escape=False,
                                          column_format='lrrr',
                                          caption="Comparação dos Três Grafos Separados",
                                          label="tab:separated"))
        latex_content.append("\n\\clearpage\n")

        # Tabela 6: Correlação
        print("Processando Tabela 6: Matriz de Correlação...")
        df6 = pd.read_csv(self.tables_dir / 'table6_correlation_matrix.csv', index_col=0)
        latex_content.append("\\section*{Tabela 6: Matriz de Correlação entre Métricas}")
        latex_content.append(df6.to_latex(escape=False,
                                          column_format='l' + 'r'*len(df6.columns),
                                          caption="Correlação entre Métricas de Centralidade e Bridging",
                                          label="tab:correlation",
                                          float_format="%.4f"))
        latex_content.append("\n")

        # Footer
        latex_content.append("\\end{document}")

        # Salva arquivo LaTeX
        output_path = self.tables_dir / 'all_tables.tex'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(latex_content))

        print(f"\n✓ Arquivo LaTeX salvo: {output_path}")
        print("\nPara compilar:")
        print(f"  cd {self.tables_dir}")
        print("  pdflatex all_tables.tex")

        # Também salva tabelas individuais
        print("\nGerando arquivos LaTeX individuais...")
        self._save_individual_tables()

    def _save_individual_tables(self):
        """Salva cada tabela em arquivo LaTeX separado"""
        tables = [
            ('table1_structural_metrics.csv', 'Métricas Estruturais', 'll'),
            ('table2_top_developers.csv', 'Top Desenvolvedores', 'clrrrr'),
            ('table3_communities.csv', 'Comunidades', 'crll'),
            ('table4_bridging_developers.csv', 'Bridging Developers', 'clcrrr'),
            ('table5_separated_graphs.csv', 'Grafos Separados', 'lrrr'),
        ]

        for csv_file, title, col_format in tables:
            df = pd.read_csv(self.tables_dir / csv_file)
            tex_file = csv_file.replace('.csv', '.tex')

            latex_table = df.to_latex(index=False, escape=False,
                                      column_format=col_format,
                                      caption=title)

            output_path = self.tables_dir / tex_file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(latex_table)

            print(f"  ✓ {tex_file}")

        # Correlação (tem índice)
        df6 = pd.read_csv(self.tables_dir / 'table6_correlation_matrix.csv', index_col=0)
        latex_table = df6.to_latex(escape=False,
                                   column_format='l' + 'r'*len(df6.columns),
                                   caption="Matriz de Correlação",
                                   float_format="%.4f")

        output_path = self.tables_dir / 'table6_correlation_matrix.tex'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(latex_table)

        print(f"  ✓ table6_correlation_matrix.tex")


def main():
    exporter = LaTeXExporter()
    exporter.export_all_tables()


if __name__ == '__main__':
    main()
