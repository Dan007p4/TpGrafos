package br.pucminas.grafos.infra.github;

import org.json.JSONArray;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

/**
 * Cliente HTTP para comunicação com a API do GitHub
 */
public class GitHubAPI {
    private static final String GITHUB_API_BASE = "https://api.github.com";
    private final String token;

    public GitHubAPI(String token) {
        this.token = token;
    }

    /**
     * Faz uma requisição GET para a API do GitHub
     */
    private String makeRequest(String endpoint) throws Exception {
        URL url = new URL(GITHUB_API_BASE + endpoint);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();

        conn.setRequestMethod("GET");
        conn.setRequestProperty("Accept", "application/vnd.github.v3+json");

        if (token != null && !token.isEmpty()) {
            conn.setRequestProperty("Authorization", "token " + token);
        }

        int responseCode = conn.getResponseCode();

        if (responseCode == 200) {
            BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            String inputLine;
            StringBuilder response = new StringBuilder();

            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();

            return response.toString();
        } else if (responseCode == 403) {
            throw new Exception("Rate limit excedido. Aguarde ou use um token de autenticação.");
        } else {
            throw new Exception("Erro na requisição: " + responseCode);
        }
    }

    /**
     * Obtém issues de um repositório
     */
    public List<JSONObject> getIssues(String owner, String repo, int maxPages) throws Exception {
        List<JSONObject> allIssues = new ArrayList<>();

        for (int page = 1; page <= maxPages; page++) {
            String endpoint = String.format("/repos/%s/%s/issues?state=all&per_page=100&page=%d",
                    owner, repo, page);
            String response = makeRequest(endpoint);
            JSONArray issues = new JSONArray(response);

            if (issues.isEmpty()) break;

            for (int i = 0; i < issues.length(); i++) {
                allIssues.add(issues.getJSONObject(i));
            }

            System.out.println("Página " + page + " de issues coletada: " + issues.length() + " issues");
            Thread.sleep(500); // Delay para evitar rate limit
        }

        return allIssues;
    }

    /**
     * Obtém comentários de uma issue
     */
    public List<JSONObject> getIssueComments(String owner, String repo, int issueNumber) throws Exception {
        String endpoint = String.format("/repos/%s/%s/issues/%d/comments?per_page=100",
                owner, repo, issueNumber);
        String response = makeRequest(endpoint);
        JSONArray comments = new JSONArray(response);

        List<JSONObject> result = new ArrayList<>();
        for (int i = 0; i < comments.length(); i++) {
            result.add(comments.getJSONObject(i));
        }

        return result;
    }

    /**
     * Obtém pull requests de um repositório
     */
    public List<JSONObject> getPullRequests(String owner, String repo, int maxPages) throws Exception {
        List<JSONObject> allPRs = new ArrayList<>();

        for (int page = 1; page <= maxPages; page++) {
            String endpoint = String.format("/repos/%s/%s/pulls?state=all&per_page=100&page=%d",
                    owner, repo, page);
            String response = makeRequest(endpoint);
            JSONArray prs = new JSONArray(response);

            if (prs.isEmpty()) break;

            for (int i = 0; i < prs.length(); i++) {
                allPRs.add(prs.getJSONObject(i));
            }

            System.out.println("Página " + page + " de PRs coletada: " + prs.length() + " PRs");
            Thread.sleep(500);
        }

        return allPRs;
    }

    /**
     * Obtém reviews de um pull request
     */
    public List<JSONObject> getPullRequestReviews(String owner, String repo, int prNumber) throws Exception {
        String endpoint = String.format("/repos/%s/%s/pulls/%d/reviews?per_page=100",
                owner, repo, prNumber);
        String response = makeRequest(endpoint);
        JSONArray reviews = new JSONArray(response);

        List<JSONObject> result = new ArrayList<>();
        for (int i = 0; i < reviews.length(); i++) {
            result.add(reviews.getJSONObject(i));
        }

        return result;
    }

    /**
     * Obtém comentários de um pull request
     */
    public List<JSONObject> getPullRequestComments(String owner, String repo, int prNumber) throws Exception {
        String endpoint = String.format("/repos/%s/%s/pulls/%d/comments?per_page=100",
                owner, repo, prNumber);
        String response = makeRequest(endpoint);
        JSONArray comments = new JSONArray(response);

        List<JSONObject> result = new ArrayList<>();
        for (int i = 0; i < comments.length(); i++) {
            result.add(comments.getJSONObject(i));
        }

        return result;
    }

    /**
     * Obtém informações do repositório
     */
    public JSONObject getRepositoryInfo(String owner, String repo) throws Exception {
        String endpoint = String.format("/repos/%s/%s", owner, repo);
        String response = makeRequest(endpoint);
        return new JSONObject(response);
    }
}