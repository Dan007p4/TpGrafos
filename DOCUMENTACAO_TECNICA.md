# Documentação Técnica - Análise de Redes de Colaboração GitHub

## Visão Geral

Este software analisa redes de colaboração em repositórios GitHub. A ideia é simples: pegar interações entre desenvolvedores (comentários, reviews, merges) e transformar isso num grafo onde conseguimos identificar quem são os desenvolvedores mais importantes, como a rede está estruturada, e que tipo de papel cada um desempenha.

O sistema tem duas partes principais:
- **Backend Java**: Faz a mineração dos dados via API do GitHub e calcula todas as métricas de grafo
- **Scripts Python**: Pegam os dados gerados e criam as visualizações e tabelas

## Arquitetura do Sistema

### Estrutura de Pacotes Java

```
br.pucminas.grafos/
├── core/
│   ├── domain/          - Entidades básicas (User, Interaction)
│   ├── enums/           - Tipos de interação
│   ├── exception/       - Exceções customizadas
│   └── graph/           - Implementação da estrutura de grafo
├── application/
│   ├── analysis/        - Algoritmos de análise (PageRank, Betweenness, etc)
│   └── service/         - Lógica de construção e análise dos grafos
├── infra/
│   ├── github/          - Cliente HTTP para API do GitHub
│   └── export/          - Exportadores (CSV, GEXF para Gephi)
└── GrafosApplication    - Ponto de entrada
```

A arquitetura segue o padrão de camadas: Core contém as entidades e estruturas fundamentais, Application tem a lógica de negócio (algoritmos), e Infrastructure cuida de integrações externas (GitHub API, exportação de arquivos).

## Como Funciona a Mineração de Dados

### 1. Conexão com a API do GitHub

A classe `GitHubAPI` faz requisições REST para a API v3 do GitHub. Configuramos o token de autenticação no `application.yaml`:

```yaml
github:
  token: seu_token_aqui
  repository: facebook/react
```

A API do GitHub tem rate limiting (5000 requests/hora com token), então incluímos delays de 200ms entre requisições para não estourar o limite.

### 2. Coleta de Interações

O `GitHubDataMiner` percorre três tipos de artefatos:

**Issues**: Para cada issue, pegamos:
- Comentários: quem comentou na issue de quem
- Fechamentos: quem fechou a issue de quem

**Pull Requests**: Para cada PR, coletamos:
- Comentários: quem comentou no PR de quem
- Reviews: quem revisou o PR de quem
- Aprovações: quando um review é do tipo "APPROVED"
- Merges: quem fez merge do PR de quem

### 3. Filtragem Automática

Durante a mineração, já filtramos algumas coisas:

```java
if (commenter != null && !commenter.equals(issueAuthor)) {
    // Só cria interação se não for auto-interação
    Interaction interaction = new Interaction(
        commenter,
        issueAuthor,
        InteractionType.COMMENT_ISSUE,
        dateTime,
        "issue-" + issueNumber
    );
    interactions.add(interaction);
}
```

Então removemos automaticamente:
- Usuários nulos/inválidos retornados pela API
- Auto-interações (desenvolvedor comentando na própria issue)

**Não removemos**:
- Bots (como dependabot) - ficam no grafo
- Desenvolvedores com poucas interações - todos são incluídos

### 4. Pesos das Interações

Cada tipo de interação tem um peso diferente baseado no esforço/importância:

```java
public enum InteractionType {
    COMMENT_ISSUE(2.0),    // Comentar numa issue
    COMMENT_PR(2.0),       // Comentar num PR
    ISSUE_CLOSE(3.0),      // Fechar uma issue
    PR_REVIEW(4.0),        // Revisar código
    PR_APPROVAL(4.5),      // Aprovar um PR
    PR_MERGE(5.0);         // Fazer merge (maior peso)
}
```

A lógica é: merge é mais importante que review, que é mais importante que comentário.

## Estrutura de Dados - O Grafo

### Implementação da Lista de Adjacência

Escolhemos lista de adjacência em vez de matriz porque o grafo é esparso (densidade ~0.0005). Com 2146 vértices, uma matriz teria 4.6 milhões de posições, mas só temos 2609 arestas.

```java
public class AdjacencyListGraph extends AbstractGraph {
    private List<List<EdgeInfo>> adjList;

    private static class EdgeInfo {
        int target;
        double weight;
    }
}
```

Cada vértice tem uma lista de EdgeInfo apontando para os vizinhos. Isso economiza memória e deixa operações como "percorrer vizinhos de v" muito eficientes.

### Construção dos Grafos

O sistema cria 4 grafos diferentes:

**1. Grafo Integrado (ponderado)**
- Todas as interações juntas
- Peso da aresta = soma dos pesos de todas as interações entre dois desenvolvedores
- Usado para análise geral da rede

**2. Grafo de Comentários (não-ponderado)**
- Só COMMENT_ISSUE + COMMENT_PR
- Peso = 1 (conta se existe aresta, não importa quantas vezes)

**3. Grafo de Fechamentos (não-ponderado)**
- Só ISSUE_CLOSE

**4. Grafo de Reviews (não-ponderado)**
- PR_REVIEW + PR_APPROVAL + PR_MERGE

A diferença entre ponderado e não-ponderado: no integrado, se A comentou 5 vezes em issues de B e fez 2 reviews, a aresta A→B tem peso 5*2.0 + 2*4.0 = 18.0. Nos grafos separados, cada aresta tem peso 1 independente de quantas interações aconteceram.

## Algoritmos Implementados

### PageRank

Implementação do algoritmo original do Google adaptado para grafos direcionados e ponderados.

```java
public static Map<Integer, Double> calculatePageRank(AbstractGraph graph,
                                                      double dampingFactor,
                                                      int maxIterations,
                                                      double tolerance)
```

Como funciona:
1. Inicializa todos os vértices com rank = 1/N
2. A cada iteração, redistribui o rank baseado nas arestas de entrada
3. Fórmula: `PR(v) = (1-d)/N + d * Σ(PR(u)/OutDegree(u))` para cada u que aponta para v
4. Para quando a diferença entre iterações fica menor que tolerance (0.0001)

Nosso PageRank considera pesos: arestas com peso maior transferem mais "importância". Usamos damping factor de 0.85 (padrão) e no máximo 100 iterações.

### Betweenness Centrality

Implementação do algoritmo de Brandes (2001), que é O(nm) em vez de O(n³) da versão naive.

A ideia: para cada par de vértices, calculamos os caminhos mínimos entre eles. Se um vértice v aparece em muitos desses caminhos, ele tem alta betweenness (é uma "ponte" na rede).

```java
public static Map<Integer, Double> calculateBetweenness(AbstractGraph graph)
```

O algoritmo faz:
1. Para cada vértice s:
   - BFS partindo de s para achar todos os caminhos mínimos
   - Conta quantos caminhos passam por cada vértice
2. Normaliza dividindo por (n-1)(n-2)/2

Desenvolvedor com alta betweenness geralmente conecta diferentes partes da rede.

### Closeness Centrality

Mede o quão "próximo" um vértice está de todos os outros.

```java
public static Map<Integer, Double> calculateCloseness(AbstractGraph graph)
```

Para cada vértice v:
1. BFS para calcular distância até todos os outros vértices alcançáveis
2. Closeness = (n-1) / (soma das distâncias)

Se o grafo não é conectado (nosso caso, tem 218 componentes), só consideramos vértices alcançáveis. Vértices isolados ficam com closeness = 0.

### Degree Centrality

O mais simples: quantas arestas o vértice tem.

Como nosso grafo é direcionado, calculamos:
- In-degree: quantas pessoas interagiram com você
- Out-degree: com quantas pessoas você interagiu
- Degree total = in + out

Normalizamos dividindo por (n-1) para ficar entre 0 e 1.

### Detecção de Comunidades (Louvain)

Algoritmo de Blondel et al. (2008) que otimiza a modularidade da rede.

```java
public static Map<Integer, Integer> detectCommunities(AbstractGraph graph)
```

Funciona em duas fases repetidas:
1. **Otimização local**: Para cada vértice, testa mover para a comunidade de cada vizinho. Se aumentar a modularidade, move.
2. **Agregação**: Junta vértices da mesma comunidade num super-vértice e reconstrói o grafo.

Repete até a modularidade parar de aumentar.

Modularidade mede: densidade de arestas dentro de comunidades vs esperado aleatoriamente. Range: [-0.5, 1.0]. Quanto maior, melhor a divisão em comunidades.

### Bridging Ties

Baseado em Guimerà & Amaral (2005). Identifica desenvolvedores que conectam comunidades diferentes.

Para cada vértice v:
1. Conta quantos vizinhos estão em comunidades diferentes da sua
2. Calcula participation coefficient: mede diversidade de comunidades que v conecta

```java
double bridgingStrength = 1.0 - Σ(k_i/k)²
```

onde k_i é número de vizinhos na comunidade i, k é degree total.

Se v só tem vizinhos na própria comunidade: bridgingStrength = 0
Se v distribui conexões igualmente entre comunidades: bridgingStrength próximo de 1

## Classificação de Papéis

Implementamos classificação baseada nas métricas calculadas:

**Core Developers**:
- Degree Centrality > Percentil 75
- PageRank > Percentil 75
- São os "núcleo duro" da rede

**Peripheral Developers**:
- Degree Centrality < Quartil 1
- PageRank < Quartil 1
- Participação marginal

**Connectors**:
- Betweenness Centrality > Percentil 75 OU
- Bridging Strength > 0 (conectam comunidades)
- Fazem a "ponte" entre diferentes partes da rede

**Intermediate**:
- Todos os demais

A classificação é hierárquica: primeiro identificamos Core, depois Peripheral, depois Connector, resto é Intermediate.

## Exportação de Dados

### CSV

Exportamos vários CSVs para análise posterior:

**interactions.csv**: Dados brutos
```
Source,Target,Type,Weight,Timestamp,Context
mmojadad,romariormr,COMMENT_ISSUE,2.0,2025-12-09T23:19:18,issue-2298
```

**centrality_metrics.csv**: Todas as métricas por vértice
```
VertexID,Label,DegreeCentrality,BetweennessCentrality,ClosenessCentrality,PageRank
0,gaearon,0.182934,0.245678,0.523456,0.012345
```

**community_assignments.csv**: Qual comunidade cada vértice pertence
```
VertexID,Label,CommunityID
0,gaearon,1
```

**bridging_developers.csv**: Só os que têm bridging > 0
```
VertexID,Label,BridgingStrength,CommunityID,NumBridgingTies
42,johndoe,0.678,5,15
```

### GEXF (para Gephi)

Exportamos grafos no formato GEXF para visualizar no Gephi:

```xml
<gexf>
  <nodes>
    <node id="0" label="gaearon">
      <attvalues>
        <attvalue for="pagerank" value="0.012345"/>
        <attvalue for="community" value="1"/>
      </attvalues>
    </node>
  </nodes>
  <edges>
    <edge source="0" target="42" weight="18.0"/>
  </edges>
</gexf>
```

Incluímos como atributos dos nós: PageRank, Betweenness, Closeness, Degree, e ID da comunidade.

## Pipeline de Análise Python

### Correção de Dados

O CSV de interações tem um problema: 7 colunas de dados mas só 6 headers. Há uma coluna extra "0" entre Weight e Timestamp.

Solução nos scripts Python:

```python
self.interactions = pd.read_csv(
    'interactions.csv',
    names=['Source', 'Target', 'Type', 'Weight', 'EXTRA', 'Timestamp', 'Context'],
    skiprows=1
)
self.interactions = self.interactions.drop(columns=['EXTRA'])
```

Forçamos leitura com 7 colunas nomeadas e depois removemos a coluna extra.

### Análises Temporais

Agregamos interações por mês:

```python
df['Month'] = pd.to_datetime(df['Timestamp']).dt.to_period('M')
monthly = df.groupby('Month').size()
```

Geramos séries temporais mostrando:
- Evolução de desenvolvedores ativos
- Volume de interações
- Heatmap de atividade (mês × ano)

Usamos decomposição SVD para identificar tendências, mas se não convergir (grafo muito esparso), fazemos média móvel simples.

### Volume de Atividade

Diferente de Degree Centrality (conta conexões únicas), volume conta interações como Source:

```python
activity = interactions.groupby(['Source', 'Type']).size()
```

Isso mostra desenvolvedores mais ativos vs mais influentes. Um dev pode ter baixo degree mas alto volume (muitas interações com poucas pessoas).

### Distribuições de Centralidade

Para visualizar as 3 métricas principais juntas, criamos figura com 3 histogramas lado a lado:

```python
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
```

Cada subplot mostra:
- Histograma da distribuição
- Linha de média
- Linha de mediana

Permite comparar visualmente a forma das distribuições (todas têm cauda longa, mas com graus diferentes).

## Métricas Estruturais Globais

Calculadas sobre o grafo integrado:

**Vértices**: Total de desenvolvedores únicos (2146)

**Arestas**: Total de conexões direcionadas (2609)

**Densidade**: Proporção de arestas existentes vs possíveis
```
densidade = arestas / (vértices * (vértices - 1))
```
Nosso grafo tem ~0.0005, ou seja, menos de 0.1% das conexões possíveis existem.

**Coeficiente de Aglomeração**: Mede "amigos dos meus amigos são meus amigos"
```
C(v) = arestas_entre_vizinhos / combinações_possíveis
C_global = média de C(v) para todos os vértices
```
~0.03 indica baixa tendência a formar triângulos.

**Diâmetro**: Maior distância entre qualquer par de vértices alcançáveis (12 saltos)

**Distância Média**: Média de todas as distâncias de caminhos mínimos (~3.45)

**Assortatividade**: Correlação entre degrees de vértices conectados
```
r = -0.18 (negativa)
```
Indica rede dissortativa: hubs tendem a se conectar com vértices de baixo degree.

**Modularidade**: Qualidade da divisão em comunidades (~0.28)

**Número de Componentes Conexos**: 218 (rede fragmentada)

## Fluxo de Execução Completo

1. **Inicialização**
   - Carrega configurações do application.yaml
   - Valida token do GitHub

2. **Mineração**
   ```
   GitHubDataMiner.mineIssues(maxPages)
   GitHubDataMiner.minePullRequests(maxPages)
   ```
   - Para cada página da API
   - Para cada issue/PR
   - Coleta comentários, reviews, etc
   - Filtra auto-interações
   - Armazena em List<Interaction>

3. **Construção dos Grafos**
   ```
   GraphBuildService.buildIntegratedGraph(interactions, userMap)
   GraphBuildService.buildGraphByTypes(interactions, userMap, types)
   ```
   - Cria estrutura de lista de adjacência
   - Acumula pesos das arestas
   - Gera 4 grafos (1 integrado + 3 separados)

4. **Análise**
   ```
   GraphAnalysisService.analyzeGraph(graph)
   ```
   - Calcula PageRank (100 iterações, tol=0.0001)
   - Calcula Betweenness (algoritmo de Brandes)
   - Calcula Closeness (BFS por vértice)
   - Calcula Degree (in/out/total)
   - Detecta comunidades (Louvain)
   - Identifica bridging ties

5. **Exportação**
   ```
   CSVExporter.exportAll(...)
   GephiExporter.exportGraph(...)
   ```
   - Gera CSVs com métricas
   - Gera GEXFs para Gephi
   - Salva em output/

6. **Visualização (Python)**
   ```bash
   python analysis_visualizer.py
   python additional_analysis.py
   ```
   - Lê CSVs gerados
   - Corrige problema da coluna extra
   - Gera 14 figuras + 10 tabelas
   - Salva em output/figures/ e output/tables/

## Detalhes de Implementação

### Por que Lista de Adjacência?

```java
// Matriz: O(n²) espaço, O(1) verificar aresta
double[][] matrix = new double[2146][2146]; // 4.6M posições

// Lista: O(n+m) espaço, O(degree) verificar aresta
List<List<EdgeInfo>> adjList; // 2146 + 2609 = 4755 elementos
```

Com densidade de 0.0005, lista economiza ~99.9% de memória.

### Por que BFS em vez de DFS?

Para caminhos mínimos, BFS garante encontrar o caminho mais curto em grafos não-ponderados. DFS não tem essa garantia.

```java
Queue<Integer> queue = new LinkedList<>();
queue.add(start);
distances[start] = 0;

while (!queue.isEmpty()) {
    int v = queue.poll();
    for (int neighbor : graph.getNeighbors(v)) {
        if (distances[neighbor] == -1) {
            distances[neighbor] = distances[v] + 1;
            queue.add(neighbor);
        }
    }
}
```

### Normalização de Métricas

Todas as centralidades são normalizadas para [0, 1]:

```java
// Degree
normalized = degree / (numVertices - 1)

// Betweenness
normalized = betweenness / ((n-1)*(n-2)/2)

// Closeness
normalized = (n-1) / sumOfDistances
```

Isso permite comparar métricas em escalas diferentes.

### Tratamento de Grafos Desconexos

Closeness em grafos desconexos:

```java
if (reachableNodes == 0) {
    closeness.put(v, 0.0);
} else {
    double avgDistance = totalDistance / reachableNodes;
    closeness.put(v, reachableNodes / avgDistance);
}
```

Só consideramos vértices alcançáveis. Componentes isolados têm closeness = 0.

## Limitações e Decisões de Design

### Não Implementamos

1. **Filtro de bots**: Mantivemos todos os usuários. Podem aparecer dependabot, github-actions, etc.

2. **Filtro de participação mínima**: Todos os desenvolvedores, independente de ter 1 ou 100 interações, estão no grafo.

3. **Agregação temporal na mineração**: Salvamos timestamps mas não agregamos por mês durante a construção. Isso fica para análise posterior em Python.

### Por que Essas Escolhas?

- **Simplicidade**: Filtros adicionam complexidade. Melhor ter dados brutos e filtrar depois se necessário.
- **Reprodutibilidade**: Qualquer um pode rodar e vai ter o mesmo grafo, sem depender de heurísticas de "isso é bot?".
- **Flexibilidade**: Com dados brutos, podemos mudar critérios de análise sem re-minerar.

## Troubleshooting Comum

### "CSV malformado"

O interactions.csv tem 7 colunas mas header com 6. Scripts Python corrigem isso automaticamente. Se você processar o CSV manualmente, lembre de pular a coluna extra entre Weight e Timestamp.

### "SVD did not converge"

Na análise temporal, se o grafo for muito esparso, decomposição SVD pode falhar. Scripts caem para média móvel automaticamente.

### "Rate limit exceeded"

GitHub API limita 5000 req/hora. Se estourar:
- Aumente delay entre requests (linha 115 do GitHubDataMiner)
- Reduza maxPages no main()
- Espere 1 hora para reset

### "No bridging developers found"

Normal em grafos pequenos ou com comunidades muito isoladas. Análise continua normalmente, gera placeholder.

## Performance

Tempos aproximados para repositório facebook/react:

- Mineração: ~45 minutos (150 páginas de issues + 150 de PRs)
- Construção de grafos: <1 segundo
- PageRank: ~2 segundos (100 iterações)
- Betweenness: ~5 segundos (algoritmo de Brandes)
- Closeness: ~3 segundos
- Louvain: ~1 segundo
- Exportação: ~2 segundos
- Scripts Python: ~30 segundos total

**Total: ~50 minutos**, sendo 90% gasto em rede (API do GitHub).

## Referências dos Algoritmos

- **PageRank**: Page et al. (1999) - The PageRank Citation Ranking
- **Betweenness**: Brandes (2001) - A Faster Algorithm for Betweenness Centrality
- **Louvain**: Blondel et al. (2008) - Fast unfolding of communities in large networks
- **Bridging**: Guimerà & Amaral (2005) - Functional cartography of complex metabolic networks
- **Closeness**: Freeman (1978) - Centrality in Social Networks

## Conclusão

O sistema é dividido em responsabilidades claras: Java faz o trabalho pesado (mineração, algoritmos de grafo), Python faz visualização. Os dados fluem via CSVs intermediários, permitindo iterar na visualização sem re-calcular tudo.

A escolha de algoritmos clássicos (PageRank, Brandes, Louvain) garante resultados validados pela literatura. A implementação segue as especificações originais dos papers.

Principais pontos de atenção:
- CSV malformado (scripts Python já lidam)
- Rate limiting da API (delays configurados)
- Grafos desconexos (métricas adaptadas)
- Normalização de métricas (permite comparação)

O código prioriza clareza sobre otimização prematura. Para grafos com milhões de vértices seria necessário otimizar, mas para repositórios típicos do GitHub (2-5k desenvolvedores) a performance é adequada.
