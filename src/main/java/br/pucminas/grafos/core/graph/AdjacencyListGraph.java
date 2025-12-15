package br.pucminas.grafos.core.graph;

import java.util.*;

public class AdjacencyListGraph extends AbstractGraph {
    private List<Map<Integer, Double>> adjacencyList;

    public AdjacencyListGraph(int numVertices) {
        super(numVertices);
        this.adjacencyList = new ArrayList<>(numVertices);
        for (int i = 0; i < numVertices; i++) {
            adjacencyList.add(new HashMap<>());
        }
    }

    @Override
    public boolean hasEdge(int u, int v) {
        validateVertex(u);
        validateVertex(v);
        return adjacencyList.get(u).containsKey(v);
    }

    @Override
    public void addEdge(int u, int v) {
        validateEdge(u, v);
        if (!hasEdge(u, v)) {
            adjacencyList.get(u).put(v, 0.0);
            numEdges++;
        }
    }

    @Override
    public void removeEdge(int u, int v) {
        validateEdge(u, v);
        if (hasEdge(u, v)) {
            adjacencyList.get(u).remove(v);
            numEdges--;
        }
    }

    @Override
    public int getVertexInDegree(int u) {
        validateVertex(u);
        int degree = 0;
        for (int i = 0; i < numVertices; i++) {
            if (adjacencyList.get(i).containsKey(u)) {
                degree++;
            }
        }
        return degree;
    }

    @Override
    public int getVertexOutDegree(int u) {
        validateVertex(u);
        return adjacencyList.get(u).size();
    }

    @Override
    public void setEdgeWeight(int u, int v, double w) {
        validateEdge(u, v);
        if (!hasEdge(u, v)) {
            addEdge(u, v);
        }
        adjacencyList.get(u).put(v, w);
    }

    @Override
    public double getEdgeWeight(int u, int v) {
        validateEdge(u, v);
        if (!hasEdge(u, v)) {
            return 0.0;
        }
        return adjacencyList.get(u).get(v);
    }

    @Override
    public List<Integer> getSuccessors(int v) {
        validateVertex(v);
        return new ArrayList<>(adjacencyList.get(v).keySet());
    }

    @Override
    public List<Integer> getPredecessors(int v) {
        validateVertex(v);
        List<Integer> predecessors = new ArrayList<>();
        for (int i = 0; i < numVertices; i++) {
            if (adjacencyList.get(i).containsKey(v)) {
                predecessors.add(i);
            }
        }
        return predecessors;
    }

    public List<Map<Integer, Double>> getAdjacencyList() {
        return adjacencyList;
    }
}