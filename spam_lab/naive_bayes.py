"""Multinomial Naive Bayes built explicitly with Counter, not sklearn NB."""
from collections import Counter
import math
import numpy as np


class CounterNaiveBayes:
    def __init__(self, alpha=1.0):
        if alpha <= 0:
            raise ValueError("alpha must be positive")
        self.alpha = alpha
        self.classes_ = np.array(["ham", "spam"])

    def fit(self, texts, labels):
        texts, labels = list(texts), list(labels)
        if len(texts) != len(labels) or set(labels) != set(self.classes_):
            raise ValueError("Training requires matching texts/labels and both ham/spam")
        self.class_counts = Counter(labels)
        self.word_counts = {c: Counter() for c in self.classes_}
        for text, label in zip(texts, labels):
            self.word_counts[label].update(text.split())
        self.vocab = set().union(*(set(c) for c in self.word_counts.values()))
        if not self.vocab:
            raise ValueError("Empty training vocabulary")
        self.totals = {c: sum(counts.values()) for c, counts in self.word_counts.items()}
        self.log_priors = {c: math.log(self.class_counts[c] / len(labels)) for c in self.classes_}
        return self

    def log_scores(self, text):
        counts = Counter(text.split())
        return np.array([
            self.log_priors[c] + sum(
                n * math.log((self.word_counts[c][w] + self.alpha) /
                             (self.totals[c] + self.alpha * len(self.vocab)))
                for w, n in counts.items() if w in self.vocab)
            for c in self.classes_
        ])

    def predict_proba(self, texts):
        scores = np.array([self.log_scores(t) for t in texts])
        scores -= scores.max(axis=1, keepdims=True)
        probs = np.exp(scores)
        return probs / probs.sum(axis=1, keepdims=True)

    def predict(self, texts):
        return self.classes_[self.predict_proba(texts).argmax(axis=1)]

    def explain(self, text):
        terms = []
        for word, count in Counter(text.split()).items():
            if word not in self.vocab:
                continue
            logp = {c: math.log((self.word_counts[c][word] + self.alpha) /
                               (self.totals[c] + self.alpha * len(self.vocab)))
                    for c in self.classes_}
            terms.append({"token": word, "count": count,
                          "spam_log_odds_contribution": count * (logp["spam"] - logp["ham"])})
        return {"log_prior": self.log_priors,
                "log_scores": dict(zip(self.classes_, self.log_scores(text).tolist())),
                "terms": sorted(terms, key=lambda t: abs(t["spam_log_odds_contribution"]), reverse=True),
                "unknown_tokens": sorted(set(text.split()) - self.vocab)}
