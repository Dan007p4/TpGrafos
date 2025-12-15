package br.pucminas.grafos.core.enums;

public enum InteractionType {
    COMMENT_ISSUE(2.0, "Comentário em Issue"),
    COMMENT_PR(2.0, "Comentário em Pull Request"),
    ISSUE_OPENED(3.0, "Abertura de Issue comentada"),
    PR_REVIEW(4.0, "Revisão de Pull Request"),
    PR_APPROVAL(4.0, "Aprovação de Pull Request"),
    PR_MERGE(5.0, "Merge de Pull Request"),
    ISSUE_CLOSE(3.0, "Fechamento de Issue");

    private final double weight;
    private final String description;

    InteractionType(double weight, String description) {
        this.weight = weight;
        this.description = description;
    }

    public double getWeight() {
        return weight;
    }

    public String getDescription() {
        return description;
    }
}