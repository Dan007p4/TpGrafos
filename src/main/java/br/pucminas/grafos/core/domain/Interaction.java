package br.pucminas.grafos.core.domain;

import br.pucminas.grafos.core.enums.InteractionType;

import java.time.LocalDateTime;

public class Interaction {
    private User source;
    private User target;
    private InteractionType type;
    private LocalDateTime timestamp;
    private String context;

    public Interaction(User source, User target, InteractionType type) {
        this.source = source;
        this.target = target;
        this.type = type;
        this.timestamp = LocalDateTime.now();
    }

    public Interaction(User source, User target, InteractionType type, LocalDateTime timestamp, String context) {
        this.source = source;
        this.target = target;
        this.type = type;
        this.timestamp = timestamp;
        this.context = context;
    }

    public User getSource() {
        return source;
    }

    public void setSource(User source) {
        this.source = source;
    }

    public User getTarget() {
        return target;
    }

    public void setTarget(User target) {
        this.target = target;
    }

    public InteractionType getType() {
        return type;
    }

    public void setType(InteractionType type) {
        this.type = type;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }

    public String getContext() {
        return context;
    }

    public void setContext(String context) {
        this.context = context;
    }

    public double getWeight() {
        return type.getWeight();
    }

    @Override
    public String toString() {
        return "Interaction{" +
                "source=" + source.getLogin() +
                ", target=" + target.getLogin() +
                ", type=" + type +
                ", timestamp=" + timestamp +
                ", context='" + context + '\'' +
                '}';
    }
}