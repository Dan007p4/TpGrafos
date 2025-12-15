package br.pucminas.grafos.infra.github;
import br.pucminas.grafos.core.domain.*;
import br.pucminas.grafos.core.enums.InteractionType;
import org.json.JSONObject;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * Minerador de dados do GitHub
 */
public class GitHubDataMiner {
    private GitHubAPI api;
    private String owner;
    private String repo;
    private Map<String, User> userMap;
    private List<Interaction> interactions;
    private int userIdCounter = 0;

    public GitHubDataMiner(String token, String owner, String repo) {
        this.api = new GitHubAPI(token);
        this.owner = owner;
        this.repo = repo;
        this.userMap = new HashMap<>();
        this.interactions = new ArrayList<>();
    }

    /**
     * Obtém ou cria um usuário
     */
    private User getOrCreateUser(JSONObject userJson) {
        if (userJson == null || userJson.isNull("login")) {
            return null;
        }

        String login = userJson.getString("login");

        if (!userMap.containsKey(login)) {
            int id = userJson.optInt("id", userIdCounter++);
            String name = userJson.optString("name", login);
            User user = new User(id, login, name);
            user.setVertexId(userMap.size());
            userMap.put(login, user);
        }

        return userMap.get(login);
    }

    /**
     * Minera dados de issues
     */
    public void mineIssues(int maxPages) {
        System.out.println("\n=== Minerando Issues ===");

        try {
            List<JSONObject> issues = api.getIssues(owner, repo, maxPages);
            System.out.println("Total de issues coletadas: " + issues.size());

            int processed = 0;
            for (JSONObject issue : issues) {
                if (issue.has("pull_request")) {
                    continue;
                }

                int issueNumber = issue.getInt("number");
                User issueAuthor = getOrCreateUser(issue.getJSONObject("user"));

                if (issueAuthor == null) continue;

                try {
                    List<JSONObject> comments = api.getIssueComments(owner, repo, issueNumber);

                    for (JSONObject comment : comments) {
                        User commenter = getOrCreateUser(comment.getJSONObject("user"));

                        if (commenter != null && !commenter.equals(issueAuthor)) {
                            String timestamp = comment.getString("created_at");
                            LocalDateTime dateTime = parseGitHubTimestamp(timestamp);

                            Interaction interaction = new Interaction(
                                    commenter,
                                    issueAuthor,
                                    InteractionType.COMMENT_ISSUE,
                                    dateTime,
                                    "issue-" + issueNumber
                            );
                            interactions.add(interaction);
                        }
                    }

                    if (issue.has("closed_by") && !issue.isNull("closed_by")) {
                        User closer = getOrCreateUser(issue.getJSONObject("closed_by"));

                        if (closer != null && !closer.equals(issueAuthor)) {
                            String timestamp = issue.optString("closed_at", "");
                            LocalDateTime dateTime = parseGitHubTimestamp(timestamp);

                            Interaction interaction = new Interaction(
                                    closer,
                                    issueAuthor,
                                    InteractionType.ISSUE_CLOSE,
                                    dateTime,
                                    "issue-" + issueNumber
                            );
                            interactions.add(interaction);
                        }
                    }

                    processed++;
                    if (processed % 10 == 0) {
                        System.out.println("Processadas " + processed + " issues...");
                    }

                    Thread.sleep(200);

                } catch (Exception e) {
                    System.err.println("Erro ao processar issue #" + issueNumber + ": " + e.getMessage());
                }
            }

            System.out.println("Issues mineradas com sucesso!");

        } catch (Exception e) {
            System.err.println("Erro ao minerar issues: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Minera dados de pull requests
     */
    public void minePullRequests(int maxPages) {
        System.out.println("\n=== Minerando Pull Requests ===");

        try {
            List<JSONObject> prs = api.getPullRequests(owner, repo, maxPages);
            System.out.println("Total de PRs coletados: " + prs.size());

            int processed = 0;
            for (JSONObject pr : prs) {
                int prNumber = pr.getInt("number");
                User prAuthor = getOrCreateUser(pr.getJSONObject("user"));

                if (prAuthor == null) continue;

                try {
                    List<JSONObject> comments = api.getPullRequestComments(owner, repo, prNumber);

                    for (JSONObject comment : comments) {
                        User commenter = getOrCreateUser(comment.getJSONObject("user"));

                        if (commenter != null && !commenter.equals(prAuthor)) {
                            String timestamp = comment.getString("created_at");
                            LocalDateTime dateTime = parseGitHubTimestamp(timestamp);

                            Interaction interaction = new Interaction(
                                    commenter,
                                    prAuthor,
                                    InteractionType.COMMENT_PR,
                                    dateTime,
                                    "pr-" + prNumber
                            );
                            interactions.add(interaction);
                        }
                    }

                    List<JSONObject> reviews = api.getPullRequestReviews(owner, repo, prNumber);

                    for (JSONObject review : reviews) {
                        User reviewer = getOrCreateUser(review.getJSONObject("user"));

                        if (reviewer != null && !reviewer.equals(prAuthor)) {
                            String state = review.getString("state");
                            String timestamp = review.getString("submitted_at");
                            LocalDateTime dateTime = parseGitHubTimestamp(timestamp);

                            InteractionType type = InteractionType.PR_REVIEW;
                            if ("APPROVED".equals(state)) {
                                type = InteractionType.PR_APPROVAL;
                            }

                            Interaction interaction = new Interaction(
                                    reviewer,
                                    prAuthor,
                                    type,
                                    dateTime,
                                    "pr-" + prNumber
                            );
                            interactions.add(interaction);
                        }
                    }

                    if (pr.has("merged_by") && !pr.isNull("merged_by")) {
                        User merger = getOrCreateUser(pr.getJSONObject("merged_by"));

                        if (merger != null && !merger.equals(prAuthor)) {
                            String timestamp = pr.optString("merged_at", "");
                            LocalDateTime dateTime = parseGitHubTimestamp(timestamp);

                            Interaction interaction = new Interaction(
                                    merger,
                                    prAuthor,
                                    InteractionType.PR_MERGE,
                                    dateTime,
                                    "pr-" + prNumber
                            );
                            interactions.add(interaction);
                        }
                    }

                    processed++;
                    if (processed % 10 == 0) {
                        System.out.println("Processados " + processed + " PRs...");
                    }

                    Thread.sleep(200);

                } catch (Exception e) {
                    System.err.println("Erro ao processar PR #" + prNumber + ": " + e.getMessage());
                }
            }

            System.out.println("Pull requests minerados com sucesso!");

        } catch (Exception e) {
            System.err.println("Erro ao minerar pull requests: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Parse de timestamp do GitHub
     */
    private LocalDateTime parseGitHubTimestamp(String timestamp) {
        if (timestamp == null || timestamp.isEmpty()) {
            return LocalDateTime.now();
        }

        try {
            DateTimeFormatter formatter = DateTimeFormatter.ISO_DATE_TIME;
            return LocalDateTime.parse(timestamp, formatter);
        } catch (Exception e) {
            return LocalDateTime.now();
        }
    }

    /**
     * Imprime estatísticas da mineração
     */
    public void printStatistics() {
        System.out.println("\n=== Estatísticas da Mineração ===");
        System.out.println("Total de usuários: " + userMap.size());
        System.out.println("Total de interações: " + interactions.size());

        Map<InteractionType, Integer> typeCount = new HashMap<>();
        for (Interaction interaction : interactions) {
            typeCount.put(interaction.getType(),
                    typeCount.getOrDefault(interaction.getType(), 0) + 1);
        }

        System.out.println("\nInterações por tipo:");
        for (Map.Entry<InteractionType, Integer> entry : typeCount.entrySet()) {
            System.out.println("  " + entry.getKey().getDescription() + ": " + entry.getValue());
        }
    }

    public Map<String, User> getUserMap() {
        return userMap;
    }

    public List<Interaction> getInteractions() {
        return interactions;
    }
}