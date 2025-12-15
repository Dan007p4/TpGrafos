package br.pucminas.grafos.core.graph;
import java.util.*;

public class AdjacencyMatrixGraph extends AbstractGraph {
    private boolean[][] adjacencyMatrix;
    private double[][] edgeWeights;

    public AdjacencyMatrixGraph(int numVertices) {
        super(numVertices);
        this.adjacencyMatrix = new boolean[numVertices][numVertices];
        this.edgeWeights = new double[numVertices][numVertices];

        for (int i = 0; i < numVertices; i++) {
            Arrays.fill(edgeWeights[i], 0.0);
        }
    }

    @Override
    public boolean hasEdge(int u, int v) {
        validateVertex(u);
        validateVertex(v);
        return adjacencyMatrix[u][v];
    }

    @Override
    public void addEdge(int u, int v) {
        validateEdge(u, v);
        if (!adjacencyMatrix[u][v]) {
            adjacencyMatrix[u][v] = true;
            numEdges++;
        }
    }

    @Override
    public void removeEdge(int u, int v) {
        validateEdge(u, v);
        if (adjacencyMatrix[u][v]) {
            adjacencyMatrix[u][v] = false;
            edgeWeights[u][v] = 0.0;
            numEdges--;
        }
    }

    @Override
    public int getVertexInDegree(int u) {
        validateVertex(u);
        int degree = 0;
        for (int i = 0; i < numVertices; i++) {
            if (adjacencyMatrix[i][u]) {
                degree++;
            }
        }
        return degree;
    }

    @Override
    public int getVertexOutDegree(int u) {
        validateVertex(u);
        int degree = 0;
        for (int i = 0; i < numVertices; i++) {
            if (adjacencyMatrix[u][i]) {
                degree++;
            }
        }
        return degree;
    }

    @Override
    public void setEdgeWeight(int u, int v, double w) {
        validateEdge(u, v);
        if (!hasEdge(u, v)) {
            addEdge(u, v);
        }
        edgeWeights[u][v] = w;
    }

    @Override
    public double getEdgeWeight(int u, int v) {
        validateEdge(u, v);
        if (!hasEdge(u, v)) {
            return 0.0;
        }
        return edgeWeights[u][v];
    }

    @Override
    public List<Integer> getSuccessors(int v) {
        validateVertex(v);
        List<Integer> successors = new ArrayList<>();
        for (int i = 0; i < numVertices; i++) {
            if (adjacencyMatrix[v][i]) {
                successors.add(i);
            }
        }
        return successors;
    }

    @Override
    public List<Integer> getPredecessors(int v) {
        validateVertex(v);
        List<Integer> predecessors = new ArrayList<>();
        for (int i = 0; i < numVertices; i++) {
            if (adjacencyMatrix[i][v]) {
                predecessors.add(i);
            }
        }
        return predecessors;
    }

    public boolean[][] getAdjacencyMatrix() {
        return adjacencyMatrix;
    }
}