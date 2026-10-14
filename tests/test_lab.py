import json
from pathlib import Path
import numpy as np
import pytest

from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from spam_lab.naive_bayes import CounterNaiveBayes
from spam_lab.preprocessing import Normalizer
from spam_lab.inference import Predictor
from backend.main import create_app


def test_nb_matches_reference():
    texts = ["meet home home", "meet dinner", "win free free", "win money"]
    labels = ["ham", "ham", "spam", "spam"]
    own = CounterNaiveBayes().fit(texts, labels)
    vec = CountVectorizer()
    reference = MultinomialNB().fit(vec.fit_transform(texts), labels)
    test = ["free money", "home meet", "unknown", "free " * 10000]
    np.testing.assert_allclose(own.predict_proba(test), reference.predict_proba(vec.transform(test)), atol=1e-12)
    assert "unknown" not in own.vocab


def test_nb_hand_calculation():
    model = CounterNaiveBayes().fit(["home home", "free"], ["ham", "spam"])
    # P(free|ham)=1/4, P(free|spam)=2/3; equal priors -> spam=8/11.
    assert model.predict_proba(["free"])[0, 1] == pytest.approx(8/11)
    np.testing.assert_allclose(model.predict_proba([""])[0], [.5, .5])


def test_normalization():
    norm = Normalizer("both")
    assert norm("Cats were running 123 https://example.org") == "cat be run <number> <url>"
    assert norm(norm("Cats were running")) == norm("Cats were running")


@pytest.fixture
def client():
    if not Path("artifacts/bundle.joblib").exists():
        pytest.skip("Run training before integration tests")
    with create_app("artifacts").test_client() as client:
        yield client


def test_saved_model_and_api(client):
    assert client.get("/health").status_code == 200
    messages = ["WIN free cash now! Call 12345", "See you at dinner tonight", "💫"]
    predictor = Predictor()
    for model in client.get("/models").get_json()["models"]:
        response = client.post("/predict", json={"messages": messages, "model": model, "explain": True})
        assert response.status_code == 200
        results = response.get_json()["predictions"]
        assert results == predictor.predict(messages, model, True)
        for result in results:
            assert sum(result["probabilities"].values()) == pytest.approx(1)
        assert results[-1]["warning"]
    assert client.get("/metrics").status_code == 200


@pytest.mark.parametrize("messages", [[], [" "], ["a"*5001], ["hi"]*101])
def test_invalid_requests(client, messages):
    assert client.post("/predict", json={"messages": messages}).status_code == 422


def test_unknown_model(client):
    assert client.post("/predict", json={"messages": ["hi"], "model": "missing"}).status_code == 400


def test_not_ready():
    with create_app("artifacts/nonexistent-test-directory").test_client() as client:
        assert client.get("/health").status_code == 503
        assert client.post("/predict", json={"messages": ["hi"]}).status_code == 503


def test_split_and_vocabulary(client):
    import pandas as pd
    split = json.loads(Path("artifacts/split.json").read_text())
    frame = pd.read_csv("artifacts/clean_dataset.csv")
    train = frame.iloc[split["train"]].normalized
    test = frame.iloc[split["test"]].normalized
    assert not set(train) & set(test)
    expected = set(" ".join(train).split())
    p = Predictor()
    assert p.bundle["models"]["nb"].vocab == expected
    for name in ["count_lr", "tfidf_lr"]:
        assert set(p.bundle["models"][name].named_steps["vectorizer"].vocabulary_) == expected


def test_neural_api():
    if not Path("artifacts_neural_verified/bundle.joblib").exists():
        pytest.skip("Optional neural model has not been trained")
    with create_app("artifacts_neural_verified").test_client() as client:
        assert "tfidf_dense" in client.get("/models").get_json()["models"]
        response = client.post("/predict", json={"messages": ["Win cash now", "Meet me tonight"], "model": "tfidf_dense"})
        assert response.status_code == 200
        for result in response.get_json()["predictions"]:
            assert sum(result["probabilities"].values()) == pytest.approx(1)


@pytest.mark.parametrize("body", [None, [], {"messages": "hello"}, {"messages": [None]},
                                  {"messages": ["hello"], "model": []},
                                  {"messages": ["hello"], "explain": "yes"}])
def test_flask_validation(client, body):
    assert client.post("/api/predict", json=body).status_code == 422


def test_frontend_and_api_prefix(client):
    import re
    response = client.get("/")
    assert response.status_code == 200
    source = response.get_data(as_text=True)
    for asset in re.findall(r'(?:src|href)="(/assets/[^"]+)"', source):
        assert client.get(asset).status_code == 200
    assert client.get("/api/health").get_json()["backend"] == "flask"
    assert client.get("/api/metrics").get_json() == client.get("/metrics").get_json()
    assert client.get("/api/unknown").status_code == 404
    assert client.get("/assets/../../artifacts/bundle.joblib").status_code == 404
    response = client.post("/api/predict", json={"messages": ["hello"]})
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"


def test_payload_limit(client):
    response = client.post("/api/predict", data='x' * 3_000_001, content_type='application/json')
    assert response.status_code == 413

