package br.pucminas.grafos.application.analysis;

import br.pucminas.grafos.core.graph.AbstractGraph;
import java.util.*;

/**
 * Cálculo de métricas de centralidade
 */
public class CentralityMetrics {
    private AbstractGraph graph;

    public CentralityMetrics(AbstractGraph graph) {
        this.graph = graph;
    }

    public Map<Integer, Double> degreeCentrality() {
        Map<Integer, Double> centrality = new HashMap<>();
        int n = graph.getVertexCount();

        for (int v = 0; v < n; v++) {
            int inDegree = graph.getVertexInDegree(v);
            int outDegree = graph.getVertexOutDegree(v);
            int totalDegree = inDegree + outDegree;
            double normalizedCentrality = (double) totalDegree / (2.0 * (n - 1));
            centrality.put(v, normalizedCentrality);
        }

        return centrality;
    }

    public Map<Integer, Double> betweennessCentrality() {
        Map<Integer, Double> centrality = new HashMap<>();
        int n = graph.getVertexCount();

        for (int v = 0; v < n; v++) {
            centrality.put(v, 0.0);
        }

        for (int s = 0; s < n; s++) {
            Queue<Integer> queue = new LinkedList<>();
            Stack<Integer> stack = new Stack<>();

            Map<Integer, List<Integer>> predecessors = new HashMap<>();
            Map<Integer, Integer> distance = new HashMap<>();
            Map<Integer, Integer> numPaths = new HashMap<>();

            for (int v = 0; v < n; v++) {
                predecessors.put(v, new ArrayList<>());
                distance.put(v, -1);
                numPaths.put(v, 0);
            }

            distance.put(s, 0);
            numPaths.put(s, 1);
            queue.offer(s);

            while (!queue.isEmpty()) {
                int v = queue.poll();
                stack.push(v);

                for (int w : graph.getSuccessors(v)) {
                    if (distance.get(w) < 0) {
                        distance.put(w, distance.get(v) + 1);
                        queue.offer(w);
                    }

                    if (distance.get(w) == distance.get(v) + 1) {
                        numPaths.put(w, numPaths.get(w) + numPaths.get(v));
                        predecessors.get(w).add(v);
                    }
                }
            }

            Map<Integer, Double> dependency = new HashMap<>();
            for (int v = 0; v < n; v++) {
                dependency.put(v, 0.0);
            }

            while (!stack.isEmpty()) {
                int w = stack.pop();
                for (int v : predecessors.get(w)) {
                    double c = (numPaths.get(v) / (double) numPaths.get(w)) * (1.0 + dependency.get(w));
                    dependency.put(v, dependency.get(v) + c);
                }
                if (w != s) {
                    centrality.put(w, centrality.get(w) + dependency.get(w));
                }
            }
        }

        double normFactor = ((n - 1) * (n - 2));
        if (normFactor > 0) {
            for (int v = 0; v < n; v++) {
                centrality.put(v, centrality.get(v) / normFactor);
            }
        }

        return centrality;
    }

    public Map<Integer, Double> closenessCentrality() {
        Map<Integer, Double> centrality = new HashMap<>();
        int n = graph.getVertexCount();

        for (int v = 0; v < n; v++) {
            int[] distances = bfsDistances(v);
            int reachableCount = 0;
            int totalDistance = 0;

            for (int d : distances) {
                if (d > 0 && d < Integer.MAX_VALUE) {
                    reachableCount++;
                    totalDistance += d;
                }
            }

            if (totalDistance > 0 && reachableCount > 0) {
                double closeness = (double) reachableCount / totalDistance;
                closeness *= (reachableCount / (double) (n - 1));
                centrality.put(v, closeness);
            } else {
                centrality.put(v, 0.0);
            }
        }

        return centrality;
    }

    public Map<Integer, Double> pageRank(double dampingFactor, int maxIterations) {
        int n = graph.getVertexCount();
        Map<Integer, Double> pageRank = new HashMap<>();
        Map<Integer, Double> newPageRank = new HashMap<>();

        double initialValue = 1.0 / n;
        for (int v = 0; v < n; v++) {
            pageRank.put(v, initialValue);
        }

        for (int iter = 0; iter < maxIterations; iter++) {
            for (int v = 0; v < n; v++) {
                double sum = 0.0;
                for (int u : graph.getPredecessors(v)) {
                    int outDegree = graph.getVertexOutDegree(u);
                    if (outDegree > 0) {
                        sum += pageRank.get(u) / outDegree;
                    }
                }
                newPageRank.put(v, (1 - dampingFactor) / n + dampingFactor * sum);
            }
            pageRank = new HashMap<>(newPageRank);
        }

        return pageRank;
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

    public static List<Map.Entry<Integer, Double>> getTopN(Map<Integer, Double> metric, int n) {
        List<Map.Entry<Integer, Double>> sorted = new ArrayList<>(metric.entrySet());
        sorted.sort((a, b) -> Double.compare(b.getValue(), a.getValue()));
        return sorted.subList(0, Math.min(n, sorted.size()));
    }
}