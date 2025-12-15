package br.pucminas.grafos.application.service;

import br.pucminas.grafos.application.analysis.CentralityMetrics;
import br.pucminas.grafos.application.analysis.CommunityDetection;
import br.pucminas.grafos.application.analysis.GraphAnalyzer;
import br.pucminas.grafos.core.domain.User;
import br.pucminas.grafos.core.graph.AbstractGraph;

import java.util.*;

/**
 * Serviço principal de análise de grafos
 */
public class GraphAnalysisService {
    private AbstractGraph graph;
    private Map<String, User> userMap;

    public GraphAnalysisService(AbstractGraph graph, Map<String, User> userMap) {
        this.graph = graph;
        this.userMap = userMap;
    }

    /**
     * Executa análise completa do grafo
     */
    public AnalysisResult performCompleteAnalysis() {
        AnalysisResult result = new AnalysisResult();

        // Análise estrutural
        GraphAnalyzer analyzer = new GraphAnalyzer(graph);
        result.density = analyzer.calculateDensity();
        result.clusteringCoefficient = analyzer.calculateClusteringCoefficient();
        result.diameter = analyzer.calculateDiameter();
        result.averageDistance = analyzer.calculateAverageDistance();
        result.degreeDistribution = analyzer.degreeDistribution();
        result.assortativity = analyzer.calculateAssortativity();

        // Métricas de centralidade
        CentralityMetrics centrality = new CentralityMetrics(graph);
        result.degreeCentrality = centrality.degreeCentrality();
        result.betweennessCentrality = centrality.betweennessCentrality();
        result.closenessCentrality = centrality.closenessCentrality();
        result.pageRank = centrality.pageRank(0.85, 100);

        // Detecção de comunidades
        CommunityDetection communityDetection = new CommunityDetection(graph);
        result.communities = communityDetection.detectCommunities();
        result.numberOfCommunities = communityDetection.getNumberOfCommunities(result.communities);
        result.communityMembers = communityDetection.getCommunityMembers(result.communities);
        result.modularity = communityDetection.calculateModularity(result.communities);
        result.bridgingTies = communityDetection.identifyBridgingTies(result.communities);
        result.bridgingStrength = communityDetection.calculateBridgingStrength(result.communities);

        return result;
    }

    /**
     * Imprime relatório completo
     */
    public void printCompleteReport(AnalysisResult result) {
        System.out.println("\n" + "=".repeat(60));
        System.out.println("  RELATÓRIO DE ANÁLISE DO GRAFO");
        System.out.println("=".repeat(60));

        // Estrutura básica
        System.out.println("\n▶ ESTRUTURA DO GRAFO");
        System.out.println("  Vértices: " + graph.getVertexCount());
        System.out.println("  Arestas: " + graph.getEdgeCount());
        System.out.println("  Densidade: " + String.format("%.4f", result.density));
        System.out.println("  Conexo: " + (graph.isConnected() ? "Sim" : "Não"));

        // Métricas de coesão
        System.out.println("\n▶ MÉTRICAS DE COESÃO");
        System.out.println("  Coeficiente de Aglomeração: " + String.format("%.4f", result.clusteringCoefficient));
        System.out.println("  Diâmetro: " + result.diameter);
        System.out.println("  Distância Média: " + String.format("%.4f", result.averageDistance));
        System.out.println("  Assortatividade: " + String.format("%.4f", result.assortativity));

        // Interpretação da assortatividade
        String assortInterpretation;
        if (result.assortativity > 0.3) {
            assortInterpretation = "Alta (colaboradores influentes se conectam entre si)";
        } else if (result.assortativity < -0.3) {
            assortInterpretation = "Disassortativa (influentes conectam com periféricos)";
        } else {
            assortInterpretation = "Neutra (sem preferência significativa)";
        }
        System.out.println("    └─ Interpretação: " + assortInterpretation);

        // Top usuários por centralidade
        System.out.println("\n▶ TOP 10 USUÁRIOS POR DEGREE CENTRALITY");
        printTopUsers(result.degreeCentrality, 10);

        System.out.println("\n▶ TOP 10 USUÁRIOS POR BETWEENNESS CENTRALITY");
        printTopUsers(result.betweennessCentrality, 10);

        System.out.println("\n▶ TOP 10 USUÁRIOS POR PAGERANK");
        printTopUsers(result.pageRank, 10);

        // Comunidades
        System.out.println("\n▶ DETECÇÃO DE COMUNIDADES");
        System.out.println("  Número de comunidades: " + result.numberOfCommunities);
        System.out.println("  Modularidade (Q): " + String.format("%.4f", result.modularity));

        // Interpretação da modularidade
        String modInterpretation;
        if (result.modularity > 0.7) {
            modInterpretation = "Muito forte (comunidades bem definidas)";
        } else if (result.modularity > 0.3) {
            modInterpretation = "Significativa (estrutura clara de comunidades)";
        } else {
            modInterpretation = "Fraca (comunidades pouco definidas)";
        }
        System.out.println("    └─ Interpretação: " + modInterpretation);

        System.out.println("\n  Distribuição de membros:");
        for (Map.Entry<Integer, List<Integer>> entry : result.communityMembers.entrySet()) {
            System.out.println("    Comunidade " + entry.getKey() + ": " +
                    entry.getValue().size() + " membros");
        }

        // Bridging Ties
        System.out.println("\n▶ BRIDGING TIES (PONTES ENTRE COMUNIDADES)");
        System.out.println("  Total de pontes identificadas: " + result.bridgingTies.size());

        if (!result.bridgingTies.isEmpty()) {
            // Ordena por força de ponte
            List<Map.Entry<Integer, Double>> sortedBridges = new ArrayList<>(result.bridgingStrength.entrySet());
            sortedBridges.sort((a, b) -> Double.compare(b.getValue(), a.getValue()));

            System.out.println("\n  Top 10 desenvolvedores-ponte:");
            int count = 0;
            for (Map.Entry<Integer, Double> entry : sortedBridges) {
                if (!result.bridgingTies.contains(entry.getKey())) continue;

                String username = findUsernameByVertexId(entry.getKey());
                System.out.println(String.format("    %2d. %-20s (força: %.3f)",
                    ++count, username, entry.getValue()));

                if (count >= 10) break;
            }
        }

        System.out.println("\n" + "=".repeat(60));
    }

    /**
     * Imprime top N usuários por uma métrica
     */
    private void printTopUsers(Map<Integer, Double> metric, int n) {
        List<Map.Entry<Integer, Double>> topUsers = CentralityMetrics.getTopN(metric, n);

        int rank = 1;
        for (Map.Entry<Integer, Double> entry : topUsers) {
            int vertexId = entry.getKey();
            double value = entry.getValue();

            String username = findUsernameByVertexId(vertexId);
            System.out.println(String.format("    %2d. %-20s %.6f", rank++, username, value));
        }
    }

    /**
     * Encontra username pelo vertexId
     */
    private String findUsernameByVertexId(int vertexId) {
        for (User user : userMap.values()) {
            if (user.getVertexId() == vertexId) {
                return user.getLogin();
            }
        }
        return "Unknown";
    }

    /**
     * Classe interna para armazenar resultados da análise
     */
    public static class AnalysisResult {
        // Métricas estruturais
        public double density;
        public double clusteringCoefficient;
        public int diameter;
        public double averageDistance;
        public Map<Integer, Integer> degreeDistribution;
        public double assortativity;

        // Métricas de centralidade
        public Map<Integer, Double> degreeCentrality;
        public Map<Integer, Double> betweennessCentrality;
        public Map<Integer, Double> closenessCentrality;
        public Map<Integer, Double> pageRank;

        // Análise de comunidades
        public Map<Integer, Integer> communities;
        public int numberOfCommunities;
        public Map<Integer, List<Integer>> communityMembers;
        public double modularity;
        public List<Integer> bridgingTies;
        public Map<Integer, Double> bridgingStrength;
    }
}