#!/usr/bin/env python3
"""
Script para corrigir separadores decimais em CSVs
Substitui vírgulas por pontos apenas em valores numéricos
"""

import re
import shutil
from pathlib import Path

def fix_decimal_separators(file_path):
    """
    Corrige separadores decimais em um arquivo CSV.
    Substitui padrões como 0,123456 por 0.123456
    """
    # Backup
    backup_path = str(file_path) + '.backup'
    shutil.copy(str(file_path), backup_path)

    with open(backup_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Padrão: número seguido de vírgula e mais dígitos (decimal)
    # Mas NÃO quando a vírgula é seguida por espaço ou letra (delimitador CSV)
    fixed_content = re.sub(r'(\d),(\d)', r'\1.\2', content)

    with open(str(file_path), 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    print(f"[OK] Fixed: {str(file_path)}")
    print(f"  Backup: {backup_path}")

def main():
    output_dir = Path('output')

    csv_files = [
        'centrality_metrics.csv',
        'bridging_developers.csv',
        'structural_metrics.csv'
    ]

    print("Corrigindo separadores decimais nos CSVs...\n")

    for csv_file in csv_files:
        file_path = output_dir / csv_file
        if file_path.exists():
            fix_decimal_separators(file_path)
        else:
            print(f"[WARN] Arquivo nao encontrado: {file_path}")

    print("\n[OK] Todos os arquivos corrigidos!")
    print("\nVerificando primeiras linhas de centrality_metrics.csv:")

    with open(output_dir / 'centrality_metrics.csv', 'r') as f:
        for i, line in enumerate(f):
            if i < 5:
                print(f"  {line.rstrip()}")
            else:
                break

if __name__ == '__main__':
    main()
