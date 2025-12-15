package br.pucminas.grafos.application.analysis;

import br.pucminas.grafos.core.graph.AbstractGraph;
import java.util.*;

/**
 * Analisador de propriedades estruturais do grafo
 */
public class GraphAnalyzer {
    private AbstractGraph graph;

    public GraphAnalyzer(AbstractGraph graph) {
        this.graph = graph;
    }

    public double calculateDensity() {
        int n = graph.getVertexCount();
        int m = graph.getEdgeCount();
        if (n <= 1) return 0.0;
        int maxEdges = n * (n - 1);
        return (double) m / maxEdges;
    }

    public double calculateClusteringCoefficient() {
        int n = graph.getVertexCount();
        double totalCoefficient = 0.0;
        int validNodes = 0;

        for (int v = 0; v < n; v++) {
            double localCoef = calculateLocalClusteringCoefficient(v);
            if (localCoef >= 0) {
                totalCoefficient += localCoef;
                validNodes++;
            }
        }

        return validNodes > 0 ? totalCoefficient / validNodes : 0.0;
    }

    public double calculateLocalClusteringCoefficient(int v) {
        List<Integer> neighbors = getNeighbors(v);
        int k = neighbors.size();

        if (k < 2) return 0.0;

        int connections = 0;
        for (int i = 0; i < neighbors.size(); i++) {
            for (int j = i + 1; j < neighbors.size(); j++) {
                int u = neighbors.get(i);
                int w = neighbors.get(j);

                if (graph.hasEdge(u, w) || graph.hasEdge(w, u)) {
                    connections++;
                }
            }
        }

        int maxConnections = k * (k - 1) / 2;
        return (double) connections / maxConnections;
    }

    private List<Integer> getNeighbors(int v) {
        Set<Integer> neighbors = new HashSet<>();
        neighbors.addAll(graph.getSuccessors(v));
        neighbors.addAll(graph.getPredecessors(v));
        return new ArrayList<>(neighbors);
    }

    public Map<Integer, Integer> degreeDistribution() {
        Map<Integer, Integer> distribution = new HashMap<>();
        int n = graph.getVertexCount();

        for (int v = 0; v < n; v++) {
            int degree = graph.getVertexInDegree(v) + graph.getVertexOutDegree(v);
            distribution.put(degree, distribution.getOrDefault(degree, 0) + 1);
        }

        return distribution;
    }

    public int calculateDiameter() {
        int n = graph.getVertexCount();
        int diameter = 0;

        for (int v = 0; v < n; v++) {
            int[] distances = bfsDistances(v);
            for (int d : distances) {
                if (d != Integer.MAX_VALUE && d > diameter) {
                    diameter = d;
                }
            }
        }

        return diameter;
    }

    public double calculateAverageDistance() {
        int n = graph.getVertexCount();
        int totalDistance = 0;
        int count = 0;

        for (int v = 0; v < n; v++) {
            int[] distances = bfsDistances(v);
            for (int d : distances) {
                if (d > 0 && d != Integer.MAX_VALUE) {
                    totalDistance += d;
                    count++;
                }
            }
        }

        return count > 0 ? (double) totalDistance / count : 0.0;
    }

    /**
     * Calcula a assortatividade da rede (assortativity coefficient).
     *
     * A assortatividade mede a tendência de nós com características similares
     * se conectarem entre si. No caso de redes, medimos se nós com graus
     * similares tendem a se conectar.
     *
     * Fórmula: Correlação de Pearson entre os graus dos vértices conectados
     *
     * Valores:
     *  r > 0: Rede assortativa (nós com muitas conexões se conectam entre si)
     *  r ≈ 0: Rede neutra (conexões independentes do grau)
     *  r < 0: Rede disassortativa (nós com muitas conexões se conectam com nós de poucas conexões)
     *
     * Referência: Newman, M.E.J. (2002). "Assortative mixing in networks"
     *
     * @return Coeficiente de assortatividade entre -1 e 1
     */
    public double calculateAssortativity() {
        int n = graph.getVertexCount();
        int m = graph.getEdgeCount();

        if (m == 0) return 0.0;

        // Coleta graus de todos os vértices
        int[] degrees = new int[n];
        for (int v = 0; v < n; v++) {
            degrees[v] = graph.getVertexInDegree(v) + graph.getVertexOutDegree(v);
        }

        // Calcula somatórios necessários para a correlação de Pearson
        // Para cada aresta (i,j), consideramos o par de graus (k_i, k_j)
        double sumJK = 0.0;    // Soma de j*k para cada aresta
        double sumJ = 0.0;     // Soma de j para cada aresta
        double sumK = 0.0;     // Suma de k para cada aresta
        double sumJ2 = 0.0;    // Suma de j² para cada aresta
        double sumK2 = 0.0;    // Suma de k² para cada aresta
        int edgeCount = 0;

        // Para cada aresta, acumula os produtos e somas dos graus
        for (int i = 0; i < n; i++) {
            List<Integer> successors = graph.getSuccessors(i);

            for (int j : successors) {
                int degreeI = degrees[i];
                int degreeJ = degrees[j];

                sumJK += degreeI * degreeJ;
                sumJ += degreeI;
                sumK += degreeJ;
                sumJ2 += degreeI * degreeI;
                sumK2 += degreeJ * degreeJ;
                edgeCount++;
            }
        }

        if (edgeCount == 0) return 0.0;

        // Calcula a correlação de Pearson
        // r = [M * Σ(jk) - Σ(j) * Σ(k)] / sqrt([M * Σ(j²) - (Σ(j))²] * [M * Σ(k²) - (Σ(k))²])
        double numerator = edgeCount * sumJK - sumJ * sumK;
        double denomJ = edgeCount * sumJ2 - sumJ * sumJ;
        double denomK = edgeCount * sumK2 - sumK * sumK;

        // Evita divisão por zero
        if (denomJ <= 0 || denomK <= 0) return 0.0;

        double denominator = Math.sqrt(denomJ * denomK);

        if (denominator == 0) return 0.0;

        return numerator / denominator;
    }

    private int[] bfsDistances(int source) {
        int n = graph.getVertexCount();
        int[] distances = new int[n];
        Arrays.fill(distances, Integer.MAX_VALUE);
        distances[source] = 0;

        Queue<Integer> queue = new LinkedList<>();
        queue.offer(source);

        while (!queue.isEmpty()) {
            int v = queue.poll();
            for (int u : graph.getSuccessors(v)) {
                if (distances[u] == Integer.MAX_VALUE) {
                    distances[u] = distances[v] + 1;
                    queue.offer(u);
                }
            }
        }

        return distances;
    }
}