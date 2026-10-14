"""Stateless English normalization shared by training and serving."""
import os
import re
import unicodedata
from pathlib import Path

import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer

DATA_DIR = Path(os.environ.get("NLTK_DATA", "nltk_data")).resolve()
nltk.data.path.insert(0, str(DATA_DIR))


def setup_resources():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for resource in ("wordnet", "averaged_perceptron_tagger_eng"):
        if not nltk.download(resource, download_dir=str(DATA_DIR), quiet=True):
            raise RuntimeError(f"Cannot download NLTK resource: {resource}")
    check_resources()


def check_resources():
    try:
        WordNetLemmatizer().lemmatize("cars")
        nltk.pos_tag(["running"])
    except LookupError as exc:
        raise RuntimeError("Run: python -m spam_lab.preprocessing") from exc


class Normalizer:
    def __init__(self, mode="both"):
        if mode not in {"stem", "lemma", "both"}:
            raise ValueError("mode must be stem, lemma or both")
        self.mode = mode
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

    def tokens(self, text):
        text = unicodedata.normalize("NFKC", text).lower()
        text = re.sub(r"https?://\S+|www\.\S+", " <url> ", text)
        text = re.sub(r"\b[\w.+-]+@[\w.-]+\.[a-z]+\b", " <email> ", text)
        text = re.sub(r"\d+(?:[.,]\d+)*", " <number> ", text)
        # Recreate tokenizer: compiled NLTK regex timeout sentinels are not
        # portable through pickle in some NLTK versions.
        tokens = RegexpTokenizer(r"[a-z]+|<url>|<email>|<number>").tokenize(text)
        if self.mode in {"lemma", "both"} and tokens:
            mapping = {"J": "a", "V": "v", "N": "n", "R": "r"}
            tokens = [self.lemmatizer.lemmatize(t, mapping.get(pos[0], "n"))
                      if not t.startswith("<") else t
                      for t, pos in nltk.pos_tag(tokens)]
        if self.mode in {"stem", "both"}:
            tokens = [self.stemmer.stem(t) if not t.startswith("<") else t for t in tokens]
        return tokens

    def __call__(self, text):
        return " ".join(self.tokens(text))


if __name__ == "__main__":
    setup_resources()
