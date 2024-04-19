import abc
import logging
import time

from babyvec.abstract_embedding_store import AbstractEmbeddingStore
from babyvec.models import Embedding


class AbstractEmbedder(abc.ABC):
    def __init__(
            self,
            *,
            store: AbstractEmbeddingStore,
    ):
        self.store = store
        return


    @abc.abstractmethod
    def _compute_embeddings(self, texts: list[str]) -> list[Embedding]:
        return

    def get_embeddings(self, texts: list[str]) -> list[Embedding]:
        cached = [
            self.store.get(text)
            for text in texts
        ]
        to_compute = {
            text: i
            for i, text in enumerate(texts) if cached[i] is None
        }
        logging.debug("found %d cached embeddings", len(cached) - len(to_compute))
        to_compute_uniq = list(set(to_compute.keys()))
        t0 = time.time()
        new_embeddings = self._compute_embeddings(to_compute_uniq)
        t1 = time.time()
        logging.debug(
            "computed %d embeddings in %d s",
            len(to_compute_uniq),
            round(t1 - t0, 2)
        )
        for text, embed in zip(to_compute_uniq, new_embeddings):
            self.store.put(text, embed)
            cached[to_compute[text]] = embed
        t2 = time.time()
        logging.debug(
            "stored %d embeddings in %d s",
            len(to_compute_uniq),
            round(t2 - t1, 2)
        )
        return cached
