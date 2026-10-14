"""Owns model lifecycle and serializes access to shared NLP/model state."""
import logging
from threading import Lock
from spam_lab.inference import Predictor


class PredictionService:
    def __init__(self, directory):
        self.predictor = None
        self.lock = Lock()
        try:
            self.predictor = Predictor(directory)
        except Exception:
            logging.exception("Model loading failed. Check MODEL_DIR and NLTK resources.")

    @property
    def ready(self):
        return self.predictor is not None

    @property
    def models(self):
        return list(self.predictor.bundle["models"])

    @property
    def report(self):
        return self.predictor.report

    def predict(self, messages, model, explain):
        with self.lock:
            return self.predictor.predict(messages, model, explain)
