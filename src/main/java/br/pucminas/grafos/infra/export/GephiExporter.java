package br.pucminas.grafos.infra.export;

import br.pucminas.grafos.core.graph.AbstractGraph;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Map;

/**
 * Exportador para formato GEXF (Gephi)
 */
public class GephiExporter {

    /**
     * Exporta o grafo para formato GEXF
     */
    public static void exportToGEXF(AbstractGraph graph, String path) throws IOException {
        exportToGEXF(graph, path, null, null);
    }

    /**
     * Exporta o grafo para formato GEXF com métricas opcionais
     */
    public static void exportToGEXF(AbstractGraph graph, String path,
                                    Map<Integer, Double> metric, String metricName) throws IOException {
        FileWriter writer = new FileWriter(path);

        writer.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
        writer.write("<gexf xmlns=\"http://www.gexf.net/1.2draft\" version=\"1.2\">\n");
        writer.write("  <meta>\n");
        writer.write("    <creator>GitHub Graph Analyzer - PUC Minas</creator>\n");
        writer.write("    <description>Análise de colaboração em repositório GitHub</description>\n");
        writer.write("  </meta>\n");
        writer.write("  <graph mode=\"static\" defaultedgetype=\"directed\">\n");

        writer.write("    <attributes class=\"node\">\n");
        if (metric != null && metricName != null) {
            writer.write("      <attribute id=\"0\" title=\"" + metricName + "\" type=\"double\"/>\n");
        }
        writer.write("    </attributes>\n");

        writer.write("    <nodes>\n");
        for (int v = 0; v < graph.getVertexCount(); v++) {
            String label = graph.getVertexLabel(v);
            writer.write("      <node id=\"" + v + "\" label=\"" + escapeXml(label) + "\"");

            if (metric != null && metric.containsKey(v)) {
                writer.write(">\n");
                writer.write("        <attvalues>\n");
                writer.write("          <attvalue for=\"0\" value=\"" + metric.get(v) + "\"/>\n");
                writer.write("        </attvalues>\n");
                writer.write("      </node>\n");
            } else {
                writer.write("/>\n");
            }
        }
        writer.write("    </nodes>\n");

        writer.write("    <edges>\n");
        int edgeId = 0;
        for (int u = 0; u < graph.getVertexCount(); u++) {
            for (int v : graph.getSuccessors(u)) {
                double weight = graph.getEdgeWeight(u, v);
                writer.write("      <edge id=\"" + edgeId++ + "\" source=\"" + u +
                        "\" target=\"" + v + "\" weight=\"" + weight + "\"/>\n");
            }
        }
        writer.write("    </edges>\n");

        writer.write("  </graph>\n");
        writer.write("</gexf>\n");

        writer.close();
        System.out.println("✓ Grafo exportado para GEXF: " + path);
    }

    /**
     * Exporta o grafo para formato GEXF com atributo de comunidade
     */
    public static void exportToGEXF(AbstractGraph graph, String path,
                                    Map<Integer, Integer> communities) throws IOException {
        FileWriter writer = new FileWriter(path);

        writer.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
        writer.write("<gexf xmlns=\"http://www.gexf.net/1.2draft\" version=\"1.2\">\n");
        writer.write("  <meta>\n");
        writer.write("    <creator>GitHub Graph Analyzer - PUC Minas</creator>\n");
        writer.write("    <description>Análise de colaboração em repositório GitHub</description>\n");
        writer.write("  </meta>\n");
        writer.write("  <graph mode=\"static\" defaultedgetype=\"directed\">\n");

        writer.write("    <attributes class=\"node\">\n");
        writer.write("      <attribute id=\"0\" title=\"Community\" type=\"integer\"/>\n");
        writer.write("    </attributes>\n");

        writer.write("    <nodes>\n");
        for (int v = 0; v < graph.getVertexCount(); v++) {
            String label = graph.getVertexLabel(v);
            int communityId = communities.getOrDefault(v, -1);

            writer.write("      <node id=\"" + v + "\" label=\"" + escapeXml(label) + "\">\n");
            writer.write("        <attvalues>\n");
            writer.write("          <attvalue for=\"0\" value=\"" + communityId + "\"/>\n");
            writer.write("        </attvalues>\n");
            writer.write("      </node>\n");
        }
        writer.write("    </nodes>\n");

        writer.write("    <edges>\n");
        int edgeId = 0;
        for (int u = 0; u < graph.getVertexCount(); u++) {
            for (int v : graph.getSuccessors(u)) {
                double weight = graph.getEdgeWeight(u, v);
                writer.write("      <edge id=\"" + edgeId++ + "\" source=\"" + u +
                        "\" target=\"" + v + "\" weight=\"" + weight + "\"/>\n");
            }
        }
        writer.write("    </edges>\n");

        writer.write("  </graph>\n");
        writer.write("</gexf>\n");

        writer.close();
        System.out.println("✓ Grafo exportado para GEXF com comunidades: " + path);
    }

    private static String escapeXml(String text) {
        if (text == null) return "";
        return text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\"", "&quot;")
                .replace("'", "&apos;");
    }
}