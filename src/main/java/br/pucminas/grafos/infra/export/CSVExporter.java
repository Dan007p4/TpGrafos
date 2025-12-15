package br.pucminas.grafos.infra.export;

import br.pucminas.grafos.core.domain.Interaction;
import br.pucminas.grafos.core.graph.AbstractGraph;
import br.pucminas.grafos.application.service.GraphAnalysisService;

import java.io.FileWriter;
import java.io.IOException;
import java.util.*;
import java.util.Locale;

public class CSVExporter {

    /**
     * Exporta interações para CSV
     */
    public static void exportInteractions(List<Interaction> interactions, String path) throws IOException {
        FileWriter writer = new FileWriter(path);
        writer.write("Source,Target,Type,Weight,Timestamp,Context\n");

        for (Interaction interaction : interactions) {
            writer.write(String.format("%s,%s,%s,%.1f,%s,%s\n",
                    interaction.getSource().getLogin(),
                    interaction.getTarget().getLogin(),
                    interaction.getType().name(),
                    interaction.getWeight(),
                    interaction.getTimestamp(),
                    interaction.getContext()
            ));
        }

        writer.close();
        System.out.println("✓ Interações exportadas para CSV: " + path);
    }

    /**
     * Exporta arestas do grafo para CSV
     */
    public static void exportEdges(AbstractGraph graph, String path) throws IOException {
        FileWriter writer = new FileWriter(path);
        writer.write("Source,Target,Weight\n");

        for (int u = 0; u < graph.getVertexCount(); u++) {
            for (int v : graph.getSuccessors(u)) {
                double weight = graph.getEdgeWeight(u, v);
                String sourceLabel = graph.getVertexLabel(u);
                String targetLabel = graph.getVertexLabel(v);
                writer.write(sourceLabel + "," + targetLabel + "," + weight + "\n");
            }
        }

        writer.close();
        System.out.println("✓ Arestas exportadas para CSV: " + path);
    }

    /**
     * Exporta métricas de vértices para CSV
     */
    public static void exportMetrics(AbstractGraph graph, Map<Integer, Double> metrics,
                                     String metricName, String path) throws IOException {
        FileWriter writer = new FileWriter(path);
        writer.write("Vertex,Label," + metricName + "\n");

        for (int v = 0; v < graph.getVertexCount(); v++) {
            String label = graph.getVertexLabel(v);
            double value = metrics.getOrDefault(v, 0.0);
            writer.write(v + "," + label + "," + value + "\n");
        }

        writer.close();
        System.out.println("✓ Métricas exportadas para CSV: " + path);
    }

    /**
     * Exporta todas as centralidades combinadas para CSV
     */
    public static void exportAllCentralities(Map<Integer, Double> degreeCentrality,
                                             Map<Integer, Double> betweennessCentrality,
                                             Map<Integer, Double> closenessCentrality,
                                             Map<Integer, Double> pageRank,
                                             AbstractGraph graph,
                                             String path) throws IOException {
        FileWriter writer = new FileWriter(path);
        writer.write("Vertex,Label,DegreeCentrality,BetweennessCentrality,ClosenessCentrality,PageRank\n");

        for (int v = 0; v < graph.getVertexCount(); v++) {
            String label = graph.getVertexLabel(v);
            double degree = degreeCentrality.getOrDefault(v, 0.0);
            double betweenness = betweennessCentrality.getOrDefault(v, 0.0);
            double closeness = closenessCentrality.getOrDefault(v, 0.0);
            double pr = pageRank.getOrDefault(v, 0.0);

            writer.write(String.format(Locale.US, "%d,%s,%.6f,%.6f,%.6f,%.6f\n",
                    v, label, degree, betweenness, closeness, pr));
        }

        writer.close();
        System.out.println("✓ Centralidades exportadas para CSV: " + path);
    }

    /**
     * Exporta comunidades para CSV
     */
    public static void exportCommunities(Map<Integer, Integer> communities,
                                         AbstractGraph graph,
                                         String path) throws IOException {
        FileWriter writer = new FileWriter(path);
        writer.write("Vertex,Label,CommunityID\n");

        for (int v = 0; v < graph.getVertexCount(); v++) {
            String label = graph.getVertexLabel(v);
            int communityId = communities.getOrDefault(v, -1);
            writer.write(v + "," + label + "," + communityId + "\n");
        }

        writer.close();
        System.out.println("✓ Comunidades exportadas para CSV: " + path);
    }

    /**
     * Exporta bridging developers para CSV
     */
    public static void exportBridgingDevelopers(List<Integer> bridgingTies,
                                                Map<Integer, Double> bridgingStrength,
                                                Map<Integer, Integer> communities,
                                                AbstractGraph graph,
                                                String path) throws IOException {
        FileWriter writer = new FileWriter(path);
        writer.write("Vertex,Label,CommunityID,BridgingStrength,ConnectedCommunities\n");

        // Ordena por bridging strength (maior primeiro)
        List<Map.Entry<Integer, Double>> sortedBridges = new ArrayList<>(bridgingStrength.entrySet());
        sortedBridges.sort((a, b) -> Double.compare(b.getValue(), a.getValue()));

        for (Map.Entry<Integer, Double> entry : sortedBridges) {
            int v = entry.getKey();

            // Apenas inclui se for um bridging tie
            if (!bridgingTies.contains(v)) continue;

            String label = graph.getVertexLabel(v);
            int communityId = communities.getOrDefault(v, -1);
            double strength = entry.getValue();

            // Calcula número de comunidades conectadas
            Set<Integer> connectedCommunities = new HashSet<>();
            for (int successor : graph.getSuccessors(v)) {
                int succCommunity = communities.getOrDefault(successor, -1);
                if (succCommunity != communityId && succCommunity != -1) {
                    connectedCommunities.add(succCommunity);
                }
            }
            for (int predecessor : graph.getPredecessors(v)) {
                int predCommunity = communities.getOrDefault(predecessor, -1);
                if (predCommunity != communityId && predCommunity != -1) {
                    connectedCommunities.add(predCommunity);
                }
            }

            writer.write(String.format(Locale.US, "%d,%s,%d,%.6f,%d\n",
                    v, label, communityId, strength, connectedCommunities.size()));
        }

        writer.close();
        System.out.println("✓ Bridging developers exportados para CSV: " + path);
    }

    /**
     * Exporta métricas estruturais (resumo) para CSV
     */
    public static void exportStructuralMetrics(GraphAnalysisService.AnalysisResult result,
                                               AbstractGraph graph,
                                               String path) throws IOException {
        FileWriter writer = new FileWriter(path);
        writer.write("Metric,Value\n");

        writer.write("Vertices," + graph.getVertexCount() + "\n");
        writer.write("Edges," + graph.getEdgeCount() + "\n");
        writer.write(String.format(Locale.US, "Density,%.6f\n", result.density));
        writer.write(String.format(Locale.US, "ClusteringCoefficient,%.6f\n", result.clusteringCoefficient));
        writer.write("Diameter," + result.diameter + "\n");
        writer.write(String.format(Locale.US, "AverageDistance,%.6f\n", result.averageDistance));
        writer.write(String.format(Locale.US, "Assortativity,%.6f\n", result.assortativity));
        writer.write(String.format(Locale.US, "Modularity,%.6f\n", result.modularity));
        writer.write("NumberOfCommunities," + result.numberOfCommunities + "\n");
        writer.write("BridgingTiesCount," + result.bridgingTies.size() + "\n");

        writer.close();
        System.out.println("✓ Métricas estruturais exportadas para CSV: " + path);
    }
}