package br.pucminas.grafos.application.service;

import br.pucminas.grafos.core.domain.*;
import br.pucminas.grafos.core.enums.InteractionType;
import br.pucminas.grafos.core.graph.AbstractGraph;
import br.pucminas.grafos.core.graph.AdjacencyListGraph;

import java.util.*;

public class GraphBuildService {

    // Constrói grafo filtrando um tipo específico de interação
    public static AbstractGraph buildGraphByType(List<Interaction> interactions,
                                                 Map<String, User> userMap,
                                                 InteractionType type) {
        List<Interaction> filteredInteractions = new ArrayList<>();

        for (Interaction interaction : interactions) {
            if (interaction.getType() == type) {
                filteredInteractions.add(interaction);
            }
        }

        return buildGraph(filteredInteractions, userMap, false);
    }

    // Constrói grafo filtrando múltiplos tipos de interação
    public static AbstractGraph buildGraphByTypes(List<Interaction> interactions,
                                                  Map<String, User> userMap,
                                                  List<InteractionType> types) {
        List<Interaction> filteredInteractions = new ArrayList<>();

        for (Interaction interaction : interactions) {
            if (types.contains(interaction.getType())) {
                filteredInteractions.add(interaction);
            }
        }

        return buildGraph(filteredInteractions, userMap, false);
    }

    // Constrói grafo integrado com pesos
    public static AbstractGraph buildIntegratedGraph(List<Interaction> interactions,
                                                     Map<String, User> userMap) {
        return buildGraph(interactions, userMap, true);
    }

    private static AbstractGraph buildGraph(List<Interaction> interactionsList,
                                            Map<String, User> userMap,
                                            boolean weighted) {
        int numUsers = userMap.size();
        AbstractGraph graph = new AdjacencyListGraph(numUsers);

        for (User user : userMap.values()) {
            graph.setVertexLabel(user.getVertexId(), user.getLogin());
        }

        Map<String, Double> edgeWeightMap = new HashMap<>();

        for (Interaction interaction : interactionsList) {
            int sourceId = interaction.getSource().getVertexId();
            int targetId = interaction.getTarget().getVertexId();
            String edgeKey = sourceId + "-" + targetId;

            if (weighted) {
                double currentWeight = edgeWeightMap.getOrDefault(edgeKey, 0.0);
                edgeWeightMap.put(edgeKey, currentWeight + interaction.getWeight());
            } else {
                edgeWeightMap.put(edgeKey, edgeWeightMap.getOrDefault(edgeKey, 0.0) + 1.0);
            }
        }

        for (Map.Entry<String, Double> entry : edgeWeightMap.entrySet()) {
            String[] parts = entry.getKey().split("-");
            int source = Integer.parseInt(parts[0]);
            int target = Integer.parseInt(parts[1]);
            double weight = entry.getValue();

            graph.addEdge(source, target);
            graph.setEdgeWeight(source, target, weight);
        }

        return graph;
    }
}