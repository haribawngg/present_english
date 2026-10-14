import json
from pathlib import Path
import joblib
import numpy as np
from spam_lab.preprocessing import check_resources


class Predictor:
    def __init__(self, directory="artifacts"):
        check_resources()
        self.directory = Path(directory)
        # Load only trusted locally generated artifacts: joblib uses pickle.
        self.bundle = joblib.load(self.directory / "bundle.joblib")
        self.report = json.loads((self.directory / "metrics.json").read_text(encoding="utf-8"))
        self.net = None
        if "tfidf_dense" in self.bundle["models"]:
            import tensorflow as tf
            self.net = tf.keras.models.load_model(self.directory / "dense.keras")

    def predict(self, messages, model="nb", explain=False):
        if model not in self.bundle["models"]:
            raise ValueError(f"Unknown/untrained model: {model}")
        normalized = [self.bundle["normalizer"](text) for text in messages]
        estimator = self.bundle["models"][model]
        if model == "tfidf_dense":
            spam = self.net.predict(estimator.transform(normalized).toarray(), verbose=0).ravel()
            probabilities = np.column_stack([1 - spam, spam])
            vocab = estimator.vocabulary_
        else:
            probabilities = estimator.predict_proba(normalized)
            vocab = estimator.vocab if model == "nb" else estimator.named_steps["vectorizer"].vocabulary_
        results = []
        for original, norm, prob in zip(messages, normalized, probabilities):
            winner = int(np.argmax(prob))
            result = {"message": original, "normalized": norm, "model": model,
                      "label": ["ham", "spam"][winner], "confidence": float(prob[winner]),
                      "probabilities": {"ham": float(prob[0]), "spam": float(prob[1])},
                      "known_token_count": sum(t in vocab for t in norm.split()),
                      "warning": None if any(t in vocab for t in norm.split()) else "No known tokens; prediction uses model baseline."}
            if explain and model == "nb":
                result["explanation"] = estimator.explain(norm)
            results.append(result)
        return results
