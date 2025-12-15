package br.pucminas.grafos.core.graph;

import br.pucminas.grafos.core.exception.InvalidVertexException;
import br.pucminas.grafos.core.exception.InvalidEdgeException;
import java.util.*;

/**
 * Classe abstrata que define a API comum para grafos direcionados e simples.
 */
public abstract class AbstractGraph {
    protected int numVertices;
    protected int numEdges;
    protected Map<Integer, String> vertexLabels;
    protected Map<Integer, Double> vertexWeights;

    public AbstractGraph(int numVertices) {
        if (numVertices <= 0) {
            throw new IllegalArgumentException("Número de vértices deve ser positivo");
        }
        this.numVertices = numVertices;
        this.numEdges = 0;
        this.vertexLabels = new HashMap<>();
        this.vertexWeights = new HashMap<>();

        for (int i = 0; i < numVertices; i++) {
            vertexWeights.put(i, 0.0);
        }
    }

    public int getVertexCount() {
        return numVertices;
    }

    public int getEdgeCount() {
        return numEdges;
    }

    public abstract boolean hasEdge(int u, int v);

    public abstract void addEdge(int u, int v);

    public abstract void removeEdge(int u, int v);

    public boolean isSucessor(int u, int v) {
        validateVertex(u);
        validateVertex(v);
        return hasEdge(u, v);
    }

    public boolean isPredessor(int u, int v) {
        validateVertex(u);
        validateVertex(v);
        return hasEdge(v, u);
    }

    public boolean isDivergent(int u1, int v1, int u2, int v2) {
        validateVertex(u1);
        validateVertex(v1);
        validateVertex(u2);
        validateVertex(v2);
        return u1 == u2 && v1 != v2 && hasEdge(u1, v1) && hasEdge(u2, v2);
    }

    public boolean isConvergent(int u1, int v1, int u2, int v2) {
        validateVertex(u1);
        validateVertex(v1);
        validateVertex(u2);
        validateVertex(v2);
        return v1 == v2 && u1 != u2 && hasEdge(u1, v1) && hasEdge(u2, v2);
    }

    public boolean isIncident(int u, int v, int x) {
        validateVertex(u);
        validateVertex(v);
        validateVertex(x);
        return hasEdge(u, v) && (u == x || v == x);
    }

    public abstract int getVertexInDegree(int u);

    public abstract int getVertexOutDegree(int u);

    public void setVertexWeight(int v, double w) {
        validateVertex(v);
        vertexWeights.put(v, w);
    }

    public double getVertexWeight(int v) {
        validateVertex(v);
        return vertexWeights.getOrDefault(v, 0.0);
    }

    public abstract void setEdgeWeight(int u, int v, double w);

    public abstract double getEdgeWeight(int u, int v);

    public boolean isConnected() {
        if (numVertices == 0) return true;
        boolean[] visited = new boolean[numVertices];
        dfsUndirected(0, visited);
        for (boolean v : visited) {
            if (!v) return false;
        }
        return true;
    }

    private void dfsUndirected(int v, boolean[] visited) {
        visited[v] = true;
        for (int u = 0; u < numVertices; u++) {
            if (!visited[u] && (hasEdge(v, u) || hasEdge(u, v))) {
                dfsUndirected(u, visited);
            }
        }
    }

    public boolean isEmptyGraph() {
        return numEdges == 0;
    }

    public boolean isCompleteGraph() {
        int maxEdges = numVertices * (numVertices - 1);
        return numEdges == maxEdges;
    }

    public void setVertexLabel(int v, String label) {
        validateVertex(v);
        vertexLabels.put(v, label);
    }

    public String getVertexLabel(int v) {
        validateVertex(v);
        return vertexLabels.getOrDefault(v, "V" + v);
    }

    public abstract List<Integer> getSuccessors(int v);

    public abstract List<Integer> getPredecessors(int v);

    protected void validateVertex(int v) {
        if (v < 0 || v >= numVertices) {
            throw new InvalidVertexException("Vértice " + v + " inválido. Deve estar entre 0 e " + (numVertices - 1));
        }
    }

    protected void validateEdge(int u, int v) {
        validateVertex(u);
        validateVertex(v);
        if (u == v) {
            throw new InvalidEdgeException("Laços não são permitidos em grafos simples");
        }
    }
}