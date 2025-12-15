package br.pucminas.grafos.application.analysis;

import br.pucminas.grafos.core.graph.AbstractGraph;
import java.util.*;

/**
 * Detecção de comunidades
 */
public class CommunityDetection {
    private AbstractGraph graph;

    public CommunityDetection(AbstractGraph graph) {
        this.graph = graph;
    }

    public Map<Integer, Integer> detectCommunities() {
        int n = graph.getVertexCount();
        Map<Integer, Integer> communities = new HashMap<>();

        for (int v = 0; v < n; v++) {
            communities.put(v, v);
        }

        boolean improved = true;
        int iterations = 0;
        int maxIterations = 100;

        while (improved && iterations < maxIterations) {
            improved = false;
            iterations++;

            for (int v = 0; v < n; v++) {
                int bestCommunity = communities.get(v);
                double bestModularityGain = 0.0;

                Set<Integer> neighborCommunities = new HashSet<>();
                for (int u : graph.getSuccessors(v)) {
                    neighborCommunities.add(communities.get(u));
                }
                for (int u : graph.getPredecessors(v)) {
                    neighborCommunities.add(communities.get(u));
                }

                for (int community : neighborCommunities) {
                    if (community != communities.get(v)) {
                        double gain = calculateModularityGain(v, community, communities);
                        if (gain > bestModularityGain) {
                            bestModularityGain = gain;
                            bestCommunity = community;
                            improved = true;
                        }
                    }
                }

                communities.put(v, bestCommunity);
            }
        }

        return normalizeCommunities(communities);
    }

    /**
     * Calcula o ganho de modularidade ao mover um vértice para uma comunidade alvo.
     *
     * Implementa a fórmula de Blondel et al. (2008):
     * ΔQ = [Σin + ki,in / 2m - (Σtot + ki)² / (2m)²] - [Σin / 2m - (Σtot / 2m)² - (ki / 2m)²]
     *
     * Simplificando:
     * ΔQ = [ki,in / 2m - (Σtot × ki) / (2m)²]
     *
     * @param vertex Vértice a ser movido
     * @param targetCommunity Comunidade alvo
     * @param communities Mapa atual de comunidades
     * @return Ganho de modularidade (positivo = melhoria, negativo = piora)
     */
    private double calculateModularityGain(int vertex, int targetCommunity, Map<Integer, Integer> communities) {
        int m = graph.getEdgeCount();
        if (m == 0) return 0.0;

        double twoM = 2.0 * m;

        // ki = grau total do vértice (in + out para grafos direcionados)
        int ki = graph.getVertexInDegree(vertex) + graph.getVertexOutDegree(vertex);

        // ki,in = número de arestas do vértice para a comunidade alvo
        int ki_in = 0;

        // Conta arestas de saída para a comunidade alvo
        for (int successor : graph.getSuccessors(vertex)) {
            if (communities.get(successor) == targetCommunity) {
                ki_in++;
            }
        }

        // Conta arestas de entrada da comunidade alvo
        for (int predecessor : graph.getPredecessors(vertex)) {
            if (communities.get(predecessor) == targetCommunity) {
                ki_in++;
            }
        }

        // Σtot = soma total dos graus de todos os vértices na comunidade alvo
        int sigmaTot = 0;
        int n = graph.getVertexCount();

        for (int v = 0; v < n; v++) {
            if (communities.get(v) == targetCommunity) {
                sigmaTot += graph.getVertexInDegree(v) + graph.getVertexOutDegree(v);
            }
        }

        // Calcula ΔQ usando a fórmula simplificada
        // ΔQ = ki,in / 2m - (Σtot × ki) / (2m)²
        double deltaQ = (ki_in / twoM) - ((sigmaTot * ki) / (twoM * twoM));

        return deltaQ;
    }

    private Map<Integer, Integer> normalizeCommunities(Map<Integer, Integer> communities) {
        Map<Integer, Integer> normalized = new HashMap<>();
        Map<Integer, Integer> communityMapping = new HashMap<>();
        int nextId = 0;

        for (Map.Entry<Integer, Integer> entry : communities.entrySet()) {
            int oldCommunity = entry.getValue();
            if (!communityMapping.containsKey(oldCommunity)) {
                communityMapping.put(oldCommunity, nextId++);
            }
            normalized.put(entry.getKey(), communityMapping.get(oldCommunity));
        }

        return normalized;
    }

    public int getNumberOfCommunities(Map<Integer, Integer> communities) {
        return new HashSet<>(communities.values()).size();
    }

    public Map<Integer, List<Integer>> getCommunityMembers(Map<Integer, Integer> communities) {
        Map<Integer, List<Integer>> members = new HashMap<>();

        for (Map.Entry<Integer, Integer> entry : communities.entrySet()) {
            int vertex = entry.getKey();
            int community = entry.getValue();
            members.computeIfAbsent(community, k -> new ArrayList<>()).add(vertex);
        }

        return members;
    }

    /**
     * Identifica "bridging ties" - vértices que conectam diferentes comunidades.
     *
     * Bridging ties são colaboradores que atuam como pontes entre comunidades,
     * conectando grupos que de outra forma estariam isolados. Esses vértices
     * são cruciais para a coesão da rede e fluxo de informação entre grupos.
     *
     * Um vértice é considerado uma ponte se:
     * 1. Possui conexões com pelo menos 2 comunidades diferentes
     * 2. Tem uma proporção significativa de conexões inter-comunidades
     *
     * @param communities Mapa de vértice -> comunidade
     * @return Lista de vértices que atuam como pontes entre comunidades
     */
    public List<Integer> identifyBridgingTies(Map<Integer, Integer> communities) {
        List<Integer> bridges = new ArrayList<>();
        int n = graph.getVertexCount();

        for (int v = 0; v < n; v++) {
            // Identifica a comunidade do vértice atual
            int vCommunity = communities.getOrDefault(v, -1);
            if (vCommunity == -1) continue;

            // Conta conexões com outras comunidades
            Set<Integer> connectedCommunities = new HashSet<>();
            int totalConnections = 0;
            int interCommunityConnections = 0;

            // Analisa sucessores (saída)
            for (int successor : graph.getSuccessors(v)) {
                totalConnections++;
                int successorCommunity = communities.getOrDefault(successor, -1);

                if (successorCommunity != vCommunity && successorCommunity != -1) {
                    connectedCommunities.add(successorCommunity);
                    interCommunityConnections++;
                }
            }

            // Analisa predecessores (entrada)
            for (int predecessor : graph.getPredecessors(v)) {
                totalConnections++;
                int predecessorCommunity = communities.getOrDefault(predecessor, -1);

                if (predecessorCommunity != vCommunity && predecessorCommunity != -1) {
                    connectedCommunities.add(predecessorCommunity);
                    interCommunityConnections++;
                }
            }

            // Critérios para ser considerado uma ponte:
            // 1. Conecta com pelo menos 2 comunidades diferentes
            // 2. Pelo menos 30% das conexões são inter-comunidades
            if (connectedCommunities.size() >= 2 && totalConnections > 0) {
                double interCommunityRatio = (double) interCommunityConnections / totalConnections;
                if (interCommunityRatio >= 0.3) {
                    bridges.add(v);
                }
            }
        }

        return bridges;
    }

    /**
     * Calcula a "força de ponte" (bridging strength) de cada vértice.
     *
     * A força de ponte quantifica o quão importante é um vértice para
     * conectar diferentes comunidades. É calculada como:
     * - Número de comunidades diferentes conectadas
     * - Multiplicado pela proporção de conexões inter-comunidades
     *
     * @param communities Mapa de vértice -> comunidade
     * @return Mapa de vértice -> força de ponte (quanto maior, mais importante)
     */
    public Map<Integer, Double> calculateBridgingStrength(Map<Integer, Integer> communities) {
        Map<Integer, Double> bridgingStrength = new HashMap<>();
        int n = graph.getVertexCount();

        for (int v = 0; v < n; v++) {
            int vCommunity = communities.getOrDefault(v, -1);
            if (vCommunity == -1) {
                bridgingStrength.put(v, 0.0);
                continue;
            }

            // Conta conexões únicas com outras comunidades
            Set<Integer> connectedCommunities = new HashSet<>();
            int totalConnections = 0;
            int interCommunityConnections = 0;

            // Sucessores
            for (int successor : graph.getSuccessors(v)) {
                totalConnections++;
                int successorCommunity = communities.getOrDefault(successor, -1);
                if (successorCommunity != vCommunity && successorCommunity != -1) {
                    connectedCommunities.add(successorCommunity);
                    interCommunityConnections++;
                }
            }

            // Predecessores
            for (int predecessor : graph.getPredecessors(v)) {
                totalConnections++;
                int predecessorCommunity = communities.getOrDefault(predecessor, -1);
                if (predecessorCommunity != vCommunity && predecessorCommunity != -1) {
                    connectedCommunities.add(predecessorCommunity);
                    interCommunityConnections++;
                }
            }

            // Calcula força de ponte
            double strength = 0.0;
            if (totalConnections > 0) {
                double interRatio = (double) interCommunityConnections / totalConnections;
                strength = connectedCommunities.size() * interRatio;
            }

            bridgingStrength.put(v, strength);
        }

        return bridgingStrength;
    }

    /**
     * Calcula a modularidade da rede baseada nas comunidades detectadas.
     *
     * A modularidade (Q) mede a qualidade da divisão da rede em comunidades.
     * Varia de -1 a 1, onde:
     * - Q > 0.3: Estrutura de comunidades significativa
     * - Q > 0.7: Estrutura muito forte
     * - Q < 0.3: Estrutura fraca ou inexistente
     *
     * Fórmula de Newman-Girvan:
     * Q = (1/2m) * Σ[A_ij - (k_i * k_j)/(2m)] * δ(c_i, c_j)
     *
     * onde:
     * - m = número de arestas
     * - A_ij = 1 se existe aresta entre i e j, 0 caso contrário
     * - k_i, k_j = graus dos vértices i e j
     * - δ(c_i, c_j) = 1 se i e j estão na mesma comunidade, 0 caso contrário
     *
     * @param communities Mapa de vértice -> comunidade
     * @return Valor de modularidade Q
     */
    public double calculateModularity(Map<Integer, Integer> communities) {
        int n = graph.getVertexCount();
        int m = graph.getEdgeCount();

        if (m == 0) return 0.0;

        double twoM = 2.0 * m;
        double Q = 0.0;

        // Calcula graus de todos os vértices
        int[] degrees = new int[n];
        for (int v = 0; v < n; v++) {
            degrees[v] = graph.getVertexInDegree(v) + graph.getVertexOutDegree(v);
        }

        // Para cada par de vértices
        for (int i = 0; i < n; i++) {
            int communityI = communities.getOrDefault(i, -1);
            if (communityI == -1) continue;

            for (int j = 0; j < n; j++) {
                int communityJ = communities.getOrDefault(j, -1);
                if (communityJ == -1) continue;

                // δ(c_i, c_j): 1 se mesma comunidade, 0 caso contrário
                if (communityI != communityJ) continue;

                // A_ij: 1 se existe aresta, 0 caso contrário
                int A_ij = graph.hasEdge(i, j) ? 1 : 0;

                // k_i * k_j / (2m)
                double expected = (degrees[i] * degrees[j]) / twoM;

                // Acumula: A_ij - expected
                Q += (A_ij - expected);
            }
        }

        // Normaliza por 2m
        Q /= twoM;

        return Q;
    }
}