# Análise de Redes de Colaboração em Repositórios GitHub

Sistema para mineração, análise e visualização de redes de colaboração entre desenvolvedores em repositórios GitHub.

## Pré-requisitos

### Software Necessário

1. **Java 17+** (JDK)
   - Download: https://adoptium.net/
   - Verificar instalação: `java -version`

2. **Python 3.8+**
   - Download: https://www.python.org/downloads/
   - Verificar instalação: `python --version`

3. **Git** (opcional, para clonar repositório)
   - Download: https://git-scm.com/downloads
   - Verificar instalação: `git --version`

**Nota**: Maven NÃO precisa ser instalado! O projeto usa Maven Wrapper (`mvnw.cmd` no Windows ou `./mvnw` no Linux/Mac) que baixa automaticamente a versão correta do Maven.

### Token do GitHub

Você precisa de um Personal Access Token do GitHub:

1. Acesse: https://github.com/settings/tokens
2. Clique em "Generate new token (classic)"
3. Selecione os escopos: `repo`, `read:org`, `read:user`
4. Copie o token gerado (guarde em local seguro!)

## Instalação

### 1. Clonar ou baixar o projeto

```bash
git clone https://github.com/seu-usuario/grafos-tp.git
cd grafos-tp
```

Ou baixe o ZIP e extraia em uma pasta.

### 2. Configurar token do GitHub

Edite o arquivo `src/main/resources/application.yaml`:

```yaml
github:
  token: SEU_TOKEN_AQUI
  repository: facebook/react  # ou outro repositório que quiser analisar
```

### 3. Instalar dependências Python

```bash
cd python
pip install -r requirements.txt
cd ..
```

## Uso

### Passo 1: Compilar o projeto Java

**Windows:**
```bash
mvnw.cmd clean compile
```

**Linux/Mac:**
```bash
./mvnw clean compile
```

### Passo 2: Executar a mineração e análise

**Windows:**
```bash
mvnw.cmd exec:java -Dexec.mainClass="br.pucminas.grafos.GrafosApplication"
```

**Linux/Mac:**
```bash
./mvnw exec:java -Dexec.mainClass="br.pucminas.grafos.GrafosApplication"
```

Este comando vai:
- Minerar dados do GitHub via API (~45 min para repositórios grandes)
- Construir o grafo de colaboração
- Calcular todas as métricas (PageRank, Betweenness, Closeness, etc)
- Detectar comunidades
- Exportar CSVs e arquivos GEXF para `output/`

**Saída esperada:**
```
=== Minerando Issues ===
Total de issues coletadas: 1234
Processadas 10 issues...
Processadas 20 issues...
...
=== Minerando Pull Requests ===
...
=== Calculando PageRank ===
✓ PageRank calculado (100 iterações)
...
✓ Dados exportados para: output/
```

### Passo 3: Gerar visualizações e tabelas

```bash
cd python
python analysis_visualizer.py
```

Gera 9 figuras principais e 6 tabelas em `output/figures/` e `output/tables/`.

### Passo 4: Gerar análises adicionais

```bash
python additional_analysis.py
```

Gera análises temporais, classificação de papéis, volume de atividade e análise de comunidades (mais 10 figuras e 6 tabelas).

### Passo 5 (Opcional): Gerar relatório

```bash
python generate_report.py
```

Cria `output/RELATORIO_COMPLETO.md` com todas as análises consolidadas.

### Passo 6 (Opcional): Exportar para LaTeX

```bash
python export_latex.py
```

Converte todas as tabelas CSV para formato LaTeX em `output/tables/*.tex`.

## Estrutura de Saída

Após executar todos os scripts, você terá:

```
output/
├── figures/
│   ├── fig1_degree_distribution.png
│   ├── fig2_betweenness_distribution.png
│   ├── fig3_closeness_distribution.png
│   ├── fig4_pagerank_distribution.png
│   ├── fig5_community_sizes.png
│   ├── fig6_centrality_heatmap.png
│   ├── fig7_graph_comparison.png
│   ├── fig8_bridging_analysis.png
│   ├── fig7_temporal_nodes.png
│   ├── fig8_temporal_interactions.png
│   ├── fig9_activity_heatmap.png
│   ├── fig10_role_distribution.png
│   ├── fig11_monthly_detailed.png
│   ├── fig12_top_developers_activity.png
│   ├── fig13_activity_composition.png
│   ├── fig14_activity_distribution.png
│   ├── fig15_community_cohesion.png
│   └── fig16_community_function.png
├── tables/
│   ├── table1_structural_metrics.csv
│   ├── table2_top_developers.csv
│   ├── table3_communities.csv
│   ├── table4_bridging_developers.csv
│   ├── table5_separated_graphs.csv
│   ├── table6_correlation_matrix.csv
│   ├── table7_temporal_stats.csv
│   ├── table8_role_classification.csv
│   ├── table9_role_statistics.csv
│   ├── table10_developer_activity_volume.csv
│   ├── table11_community_cohesion.csv
│   └── table12_community_function.csv
├── centrality_metrics.csv
├── community_assignments.csv
├── bridging_developers.csv
├── graph_edges.csv
├── structural_metrics.csv
├── pagerank.csv
├── integrated_graph.gexf
├── graph_with_communities.gexf
├── graph_with_pagerank.gexf
├── graph1_comments.gexf
├── graph2_closes.gexf
├── graph3_reviews.gexf
└── RELATORIO_COMPLETO.md
```

## Visualização no Gephi

Os arquivos `.gexf` podem ser abertos no Gephi para visualização interativa:

1. Baixe o Gephi: https://gephi.org/
2. Abra o Gephi
3. File → Open → Selecione `output/graph_with_communities.gexf`
4. Use os atributos (PageRank, Community) para colorir e dimensionar nós
5. Aplique layout Force Atlas 2 para melhor visualização

## Comandos Rápidos (Resumo)

**Windows:**
```bash
# Setup inicial
mvnw.cmd clean compile
cd python && pip install -r requirements.txt && cd ..

# Configurar token no application.yaml

# Executar análise completa
mvnw.cmd exec:java -Dexec.mainClass="br.pucminas.grafos.GrafosApplication"

# Gerar visualizações
cd python
python analysis_visualizer.py
python additional_analysis.py
python generate_report.py
```

**Linux/Mac:**
```bash
# Setup inicial
./mvnw clean compile
cd python && pip install -r requirements.txt && cd ..

# Configurar token no application.yaml

# Executar análise completa
./mvnw exec:java -Dexec.mainClass="br.pucminas.grafos.GrafosApplication"

# Gerar visualizações
cd python
python analysis_visualizer.py
python additional_analysis.py
python generate_report.py
```

## Configurações Avançadas

### Ajustar número de páginas da API

Edite `src/main/java/br/pucminas/grafos/GrafosApplication.java`:

```java
miner.mineIssues(150);        // Padrão: 150 páginas (~3000 issues)
miner.minePullRequests(150);  // Padrão: 150 páginas (~3000 PRs)
```

Reduza os números se quiser execução mais rápida (mas menos dados).

### Mudar repositório analisado

Edite `application.yaml`:

```yaml
github:
  repository: facebook/react    # ou: vuejs/vue, microsoft/vscode, etc
```

### Ajustar parâmetros de algoritmos

Em `src/main/java/br/pucminas/grafos/application/analysis/`:

- **PageRank**: `dampingFactor = 0.85`, `maxIterations = 100`, `tolerance = 0.0001`
- **Louvain**: Executa até modularidade parar de aumentar

## Troubleshooting

### Erro: "401 Unauthorized" ao minerar

**Causa**: Token do GitHub inválido ou sem permissões.

**Solução**:
- Verifique se copiou o token corretamente no `application.yaml`
- Gere novo token com escopos `repo`, `read:org`, `read:user`

### Erro: "Rate limit exceeded"

**Causa**: Ultrapassou 5000 requisições/hora da API do GitHub.

**Solução**:
- Espere 1 hora para reset
- Reduza `maxPages` no código Java
- Aumente delay entre requisições (linha 115 do `GitHubDataMiner.java`)

### Erro: "ModuleNotFoundError" no Python

**Causa**: Dependências não instaladas.

**Solução**:
```bash
cd python
pip install -r requirements.txt
```

### Figuras/tabelas não são geradas

**Causa**: Java não executou ou CSVs não foram criados.

**Solução**:
- Execute primeiro o comando Maven
- Verifique se `output/*.csv` existem
- Rode Python na pasta `python/`

### "FileNotFoundError: interactions.csv"

**Causa**: Caminho relativo errado.

**Solução**:
- Execute scripts Python **de dentro da pasta `python/`**:
  ```bash
  cd python
  python analysis_visualizer.py
  ```

## Performance

Tempos aproximados para repositório `facebook/react`:

- Mineração (API GitHub): ~45 minutos
- Construção de grafos: <1 segundo
- PageRank: ~2 segundos
- Betweenness: ~5 segundos
- Closeness: ~3 segundos
- Louvain: ~1 segundo
- Exportação: ~2 segundos
- Scripts Python (todos): ~30 segundos

**Total: ~50 minutos** (90% é API do GitHub)

Para testes rápidos, use repositórios menores ou reduza `maxPages` para 10-20.

## Documentação Adicional

- **Documentação Técnica**: Ver `DOCUMENTACAO_TECNICA.md` para detalhes de implementação
- **Validação de Algoritmos**: Ver `VALIDACAO_ALGORITMOS.md` para correção teórica
- **Scripts Python**: Ver `python/README.md` para detalhes dos scripts

## Arquitetura

```
grafos-tp/
├── src/main/java/br/pucminas/grafos/
│   ├── core/              # Entidades básicas e estruturas de grafo
│   ├── application/       # Algoritmos de análise
│   ├── infra/            # GitHub API e exportadores
│   └── GrafosApplication.java
├── python/               # Scripts de visualização
│   ├── analysis_visualizer.py
│   ├── additional_analysis.py
│   ├── generate_report.py
│   └── export_latex.py
├── data/                 # Dados brutos minerados
├── output/               # Resultados gerados
└── pom.xml              # Configuração Maven
```

## Licença

Este projeto foi desenvolvido como trabalho acadêmico para a disciplina de Teoria de Grafos da PUC Minas.

## Contato

Para dúvidas ou problemas, consulte a documentação técnica ou abra uma issue no repositório.
