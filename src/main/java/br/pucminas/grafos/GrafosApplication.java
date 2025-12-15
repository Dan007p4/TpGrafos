package br.pucminas.grafos;

import org.springframework.boot.autoconfigure.SpringBootApplication;
import br.pucminas.grafos.application.service.GraphAnalysisService;
import br.pucminas.grafos.application.service.GraphBuildService;
import br.pucminas.grafos.infra.export.CSVExporter;
import br.pucminas.grafos.infra.export.GephiExporter;
import br.pucminas.grafos.infra.github.GitHubDataMiner;
import br.pucminas.grafos.core.enums.InteractionType;
import br.pucminas.grafos.core.graph.AbstractGraph;

import java.io.File;
import java.util.Arrays;
import java.util.Scanner;

@SpringBootApplication
public class GrafosApplication {

    public static void main(String[] args) {

        Scanner scanner = new Scanner(System.in);

        System.out.println("\n" + "=".repeat(60));
        System.out.println("  ANÁLISE DE COLABORAÇÃO EM REPOSITÓRIOS GITHUB");
        System.out.println("  Teoria de Grafos - PUC Minas");
        System.out.println("=".repeat(60));

        // Configurações
        String owner = "EvolutionAPI";
        String repo = "evolution-api";

        System.out.print("\nDigite seu token do GitHub (ou Enter para pular): ");
        String token = scanner.nextLine().trim();

        System.out.print("Páginas de issues para minerar (recomendado: 5-10): ");
        int issuePages = scanner.nextInt();

        System.out.print("Páginas de PRs para minerar (recomendado: 5-10): ");
        int prPages = scanner.nextInt();

        // Cria diretórios de saída
        new File("data").mkdirs();
        new File("output").mkdirs();

        // ETAPA 1: Mineração de Dados
        System.out.println("\n" + "=".repeat(60));
        System.out.println("  ETAPA 1: MINERAÇÃO DE DADOS");
        System.out.println("=".repeat(60));

        GitHubDataMiner miner = new GitHubDataMiner(token, owner, repo);
        miner.mineIssues(issuePages);
        miner.minePullRequests(prPages);
        miner.printStatistics();

        try {
            CSVExporter.exportInteractions(miner.getInteractions(), "data/interactions.csv");
        } catch (Exception e) {
            System.err.println("Erro ao exportar interações: " + e.getMessage());
        }

        // ETAPA 2: Construção dos Grafos
        System.out.println("\n" + "=".repeat(60));
        System.out.println("  ETAPA 2: CONSTRUÇÃO DOS GRAFOS");
        System.out.println("=".repeat(60));

        // Grafo Integrado: Todas as interações com pesos
        AbstractGraph integratedGraph = GraphBuildService.buildIntegratedGraph(
                miner.getInteractions(), miner.getUserMap());
        System.out.println("✓ Grafo integrado criado (com pesos)");

        // Grafo 1: Comentários em issues ou pull requests
        // Conforme enunciado: agrupa COMMENT_ISSUE + COMMENT_PR
        AbstractGraph commentGraph = GraphBuildService.buildGraphByTypes(
                miner.getInteractions(), miner.getUserMap(),
                Arrays.asList(InteractionType.COMMENT_ISSUE, InteractionType.COMMENT_PR));
        System.out.println("✓ Grafo 1 - Comentários (issues + PRs) criado");

        // Grafo 2: Fechamento de issues por outro usuário
        // Conforme enunciado: apenas ISSUE_CLOSE
        AbstractGraph closeGraph = GraphBuildService.buildGraphByType(
                miner.getInteractions(), miner.getUserMap(), InteractionType.ISSUE_CLOSE);
        System.out.println("✓ Grafo 2 - Fechamento de issues criado");

        // Grafo 3: Revisões/aprovações/merges de pull requests
        // Conforme enunciado: agrupa PR_REVIEW + PR_APPROVAL + PR_MERGE
        AbstractGraph reviewGraph = GraphBuildService.buildGraphByTypes(
                miner.getInteractions(), miner.getUserMap(),
                Arrays.asList(InteractionType.PR_REVIEW, InteractionType.PR_APPROVAL, InteractionType.PR_MERGE));
        System.out.println("✓ Grafo 3 - Reviews/Aprovações/Merges criado");

        // ETAPA 3: Análise do Grafo
        System.out.println("\n" + "=".repeat(60));
        System.out.println("  ETAPA 3: ANÁLISE DO GRAFO");
        System.out.println("=".repeat(60));

        GraphAnalysisService analysisService = new GraphAnalysisService(
                integratedGraph, miner.getUserMap());

        System.out.println("\nExecutando análise completa...");
        GraphAnalysisService.AnalysisResult result = analysisService.performCompleteAnalysis();
        analysisService.printCompleteReport(result);

        // ETAPA 4: Exportação
        System.out.println("\n" + "=".repeat(60));
        System.out.println("  ETAPA 4: EXPORTAÇÃO");
        System.out.println("=".repeat(60));

        try {
            // Exporta grafo integrado (GEXF)
            GephiExporter.exportToGEXF(integratedGraph, "output/integrated_graph.gexf");
            GephiExporter.exportToGEXF(integratedGraph, "output/graph_with_pagerank.gexf",
                    result.pageRank, "PageRank");
            GephiExporter.exportToGEXF(integratedGraph, "output/graph_with_communities.gexf",
                    result.communities);

            // Exporta os 3 grafos separados conforme enunciado (GEXF)
            GephiExporter.exportToGEXF(commentGraph, "output/graph1_comments.gexf");
            GephiExporter.exportToGEXF(closeGraph, "output/graph2_closes.gexf");
            GephiExporter.exportToGEXF(reviewGraph, "output/graph3_reviews.gexf");

            // CSV - Grafos e métricas básicas
            CSVExporter.exportEdges(integratedGraph, "output/graph_edges.csv");
            CSVExporter.exportMetrics(integratedGraph, result.pageRank,
                    "PageRank", "output/pagerank.csv");

            // CSV - Todas as centralidades combinadas
            CSVExporter.exportAllCentralities(
                    result.degreeCentrality,
                    result.betweennessCentrality,
                    result.closenessCentrality,
                    result.pageRank,
                    integratedGraph,
                    "output/centrality_metrics.csv"
            );

            // CSV - Comunidades
            CSVExporter.exportCommunities(
                    result.communities,
                    integratedGraph,
                    "output/community_assignments.csv"
            );

            // CSV - Bridging Developers
            CSVExporter.exportBridgingDevelopers(
                    result.bridgingTies,
                    result.bridgingStrength,
                    result.communities,
                    integratedGraph,
                    "output/bridging_developers.csv"
            );

            // CSV - Métricas estruturais (resumo)
            CSVExporter.exportStructuralMetrics(
                    result,
                    integratedGraph,
                    "output/structural_metrics.csv"
            );

            System.out.println("\n✓ Todos os arquivos exportados com sucesso!");
        } catch (Exception e) {
            System.err.println("✗ Erro ao exportar: " + e.getMessage());
            e.printStackTrace();
        }

        System.out.println("\n" + "=".repeat(60));
        System.out.println("  ANÁLISE CONCLUÍDA");
        System.out.println("=".repeat(60));
        System.out.println("\nArquivos gerados:");
        System.out.println("  • data/interactions.csv");
        System.out.println("\n  Grafos GEXF (Gephi):");
        System.out.println("    • output/integrated_graph.gexf");
        System.out.println("    • output/graph_with_pagerank.gexf");
        System.out.println("    • output/graph_with_communities.gexf");
        System.out.println("    • output/graph1_comments.gexf");
        System.out.println("    • output/graph2_closes.gexf");
        System.out.println("    • output/graph3_reviews.gexf");
        System.out.println("\n  Dados CSV (Análise):");
        System.out.println("    • output/graph_edges.csv");
        System.out.println("    • output/centrality_metrics.csv");
        System.out.println("    • output/community_assignments.csv");
        System.out.println("    • output/bridging_developers.csv");
        System.out.println("    • output/structural_metrics.csv");
        System.out.println("    • output/pagerank.csv");
        System.out.println("\n  Para visualizar os dados:");
        System.out.println("    1. Abra os arquivos .gexf no Gephi");
        System.out.println("    2. Execute os scripts Python para gerar figuras e tabelas");

        scanner.close();
    }
}


