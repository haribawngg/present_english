"""Run with python -m spam_lab.train --data data/smsspamcollection.tsv."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from spam_lab.naive_bayes import CounterNaiveBayes
from spam_lab.preprocessing import Normalizer, check_resources


def load_data(path):
    # Accept both this attachment (header + extra columns) and original 2-column SMS data.
    frame = pd.read_csv(path, sep="\t", encoding="utf-8-sig")
    if not {"label", "message"}.issubset(frame.columns):
        frame = pd.read_csv(path, sep="\t", header=None, names=["label", "message"],
                            usecols=[0, 1], encoding="utf-8-sig")
    frame = frame[["label", "message"]].copy()
    original = len(frame)
    frame = frame.dropna()
    frame["label"] = frame.label.str.strip().str.lower()
    frame["message"] = frame.message.str.strip()
    if not frame.label.isin(["ham", "spam"]).all():
        raise ValueError("Dataset contains labels other than ham/spam")
    frame = frame[frame.message.ne("")]
    return frame, original


def evaluate(y_true, y_pred):
    return {"accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, pos_label="spam", zero_division=0),
            "recall": recall_score(y_true, y_pred, pos_label="spam", zero_division=0),
            "f1": f1_score(y_true, y_pred, pos_label="spam", zero_division=0),
            "confusion_matrix": confusion_matrix(y_true, y_pred, labels=["ham", "spam"]).tolist(),
            "classification_report": classification_report(y_true, y_pred, labels=["ham", "spam"],
                                                             output_dict=True, zero_division=0)}


def vectorizer(kind, **kwargs):
    return kind(tokenizer=str.split, token_pattern=None, lowercase=False, **kwargs)


def train(data, output="artifacts", mode="both", seed=42, test_size=0.2, neural=False, epochs=15):
    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1")
    check_resources()
    output = Path(output)
    if (output / "bundle.joblib").exists():
        raise FileExistsError("Output already contains a model; choose a new --output directory")
    output.mkdir(parents=True, exist_ok=True)
    frame, original = load_data(data)
    normalizer = Normalizer(mode)
    frame["normalized"] = frame.message.map(normalizer)
    empty = int(frame.normalized.eq("").sum())
    frame = frame[frame.normalized.ne("")]
    # No learned transform here. Deduplicate normalized messages BEFORE splitting,
    # so spelling/case variants cannot leak across train and test.
    conflicts = frame.groupby("normalized").label.nunique()
    conflict_keys = set(conflicts[conflicts > 1].index)
    conflict_rows = int(frame.normalized.isin(conflict_keys).sum())
    frame = frame[~frame.normalized.isin(conflict_keys)]
    before = len(frame)
    frame = frame.drop_duplicates("normalized").reset_index(drop=True)
    train_ids, test_ids = train_test_split(frame.index, test_size=test_size, random_state=seed, stratify=frame.label)
    x_train, x_test = frame.loc[train_ids, "normalized"], frame.loc[test_ids, "normalized"]
    y_train, y_test = frame.loc[train_ids, "label"], frame.loc[test_ids, "label"]
    models = {"nb": CounterNaiveBayes().fit(x_train, y_train)}
    for name, kind in (("count_lr", CountVectorizer), ("tfidf_lr", TfidfVectorizer)):
        models[name] = Pipeline([("vectorizer", vectorizer(kind)),
                                 ("classifier", LogisticRegression(max_iter=1000, random_state=seed))]).fit(x_train, y_train)
    predictions = {name: model.predict(x_test) for name, model in models.items()}
    metrics = {name: evaluate(y_test, pred) for name, pred in predictions.items()}
    history = None
    if neural:
        import tensorflow as tf
        tf.keras.utils.set_random_seed(seed)
        # Validation comes only from the training partition; test remains untouched.
        xt, xv, yt, yv = train_test_split(x_train, y_train, test_size=0.15, random_state=seed, stratify=y_train)
        vec = vectorizer(TfidfVectorizer, max_features=5000, dtype=np.float32)
        a, b = vec.fit_transform(xt).toarray(), vec.transform(xv).toarray()
        net = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(a.shape[1],)),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(32, activation="relu"),
            tf.keras.layers.Dense(1, activation="sigmoid"),
        ])
        net.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
        fitted = net.fit(a, (yt == "spam").astype(int).to_numpy(),
                         validation_data=(b, (yv == "spam").astype(int).to_numpy()),
                         epochs=epochs, batch_size=32, verbose=2,
                         callbacks=[tf.keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True)])
        predictions["tfidf_dense"] = np.where(net.predict(vec.transform(x_test).toarray(), verbose=0).ravel() >= 0.5, "spam", "ham")
        metrics["tfidf_dense"] = evaluate(y_test, predictions["tfidf_dense"])
        net.save(output / "dense.keras")
        models["tfidf_dense"] = vec
        history = {k: [float(x) for x in v] for k, v in fitted.history.items()}
    metadata = {"created_at": datetime.now(timezone.utc).isoformat(), "seed": seed,
                "normalization": mode, "test_size": test_size, "positive_class": "spam",
                "confusion_matrix_order": ["ham", "spam"], "confusion_matrix_axes": "rows=true, columns=predicted",
                "source_sha256": hashlib.sha256(Path(data).read_bytes()).hexdigest(),
                "original_rows": original, "empty_after_normalization": empty,
                "conflicting_rows_removed": conflict_rows, "duplicates_removed": before - len(frame),
                "clean_rows": len(frame), "train_rows": len(train_ids), "test_rows": len(test_ids),
                "train_distribution": dict(Counter(y_train)), "test_distribution": dict(Counter(y_test)),
                "vocab_size": len(models["nb"].vocab), "default_model": "nb",
                "versions": {p: importlib.metadata.version(p) for p in ["pandas", "numpy", "scikit-learn", "nltk", "joblib"]}}
    if neural:
        metadata["versions"]["tensorflow"] = importlib.metadata.version("tensorflow")
    report = {"metadata": metadata, "models": metrics, "neural_history": history}
    (output / "metrics.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    pd.DataFrame({name: {k: v for k, v in m.items() if k in ["accuracy", "precision", "recall", "f1"]}
                  for name, m in metrics.items()}).T.to_csv(output / "comparison.csv", index_label="model")
    test_results = frame.loc[test_ids].copy()
    for name, pred in predictions.items():
        test_results[name] = pred
    test_results.to_csv(output / "test_predictions.csv", index=False)
    (output / "split.json").write_text(json.dumps({"train": train_ids.tolist(), "test": test_ids.tolist()}), encoding="utf-8")
    frame.to_csv(output / "clean_dataset.csv", index=False)
    nb = models["nb"]
    pd.DataFrame({"token": sorted(nb.vocab), **{c: [nb.word_counts[c][w] for w in sorted(nb.vocab)] for c in nb.classes_}}).to_csv(output / "nb_vocabulary.csv", index=False)
    (output / "nb_example.json").write_text(json.dumps({"message": x_test.iloc[0], **nb.explain(x_test.iloc[0])}, indent=2), encoding="utf-8")
    plot_results(metrics, output)
    joblib.dump({"normalizer": normalizer, "models": models, "metadata": metadata}, output / "bundle.joblib")
    print(pd.read_csv(output / "comparison.csv").to_string(index=False))
    return report


def plot_results(metrics, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, len(metrics), figsize=(5 * len(metrics), 4))
    for ax, (name, scores) in zip(np.atleast_1d(axes), metrics.items()):
        cm = np.array(scores["confusion_matrix"])
        ax.imshow(cm, cmap="Blues")
        ax.set(xticks=[0, 1], yticks=[0, 1], xticklabels=["ham", "spam"], yticklabels=["ham", "spam"],
               xlabel="Predicted", ylabel="True", title=name)
        for (i, j), value in np.ndenumerate(cm):
            ax.text(j, i, str(value), ha="center", va="center", color="white" if value > cm.max()/2 else "black")
    fig.tight_layout()
    fig.savefig(output / "confusion_matrices.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/smsspamcollection.tsv")
    parser.add_argument("--output", default="artifacts")
    parser.add_argument("--mode", choices=["stem", "lemma", "both"], default="both")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--neural", action="store_true")
    parser.add_argument("--epochs", type=int, default=15)
    args = parser.parse_args()
    train(args.data, args.output, args.mode, args.seed, args.test_size, args.neural, args.epochs)
