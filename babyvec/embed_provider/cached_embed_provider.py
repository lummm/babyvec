import abc
import logging
import time
from typing import cast

from babyvec.computer.abstract_embedding_computer import AbstractEmbeddingComputer
from babyvec.embed_provider.abstract_embed_provider import AbstractEmbedProvider
from babyvec.models import CorpusFragment, EmbedComputeOptions, Embedding
from babyvec.store.abstract_embedding_store import AbstractEmbeddingStore


class CachedEmbedProvider(AbstractEmbedProvider):
    def __init__(
        self,
        *,
        computer: AbstractEmbeddingComputer,
        store: AbstractEmbeddingStore | None = None,
    ):
        self.store = store
        self.computer = computer
        return

    def get_embeddings(self, texts: list[str]) -> list[Embedding]:
        cache_hits: list[Embedding | None]
        if self.store:
            cache_hits = [self.store.get(text) for text in texts]
        else:
            cache_hits = [None] * len(texts)
            pass

        to_compute = {text: i for i, text in enumerate(texts) if cache_hits[i] is None}

        logging.debug("found %d cached embeddings", len(cache_hits) - len(to_compute))

        if not to_compute:
            return cast(list[Embedding], cache_hits)

        to_compute_uniq = list(set(to_compute.keys()))

        t0 = time.time()
        new_embeddings = self.computer.compute_embeddings(to_compute_uniq)

        t1 = time.time()
        logging.debug(
            "computed %d embeddings in %f s", len(to_compute_uniq), round(t1 - t0, 2)
        )

        for text, embed in zip(to_compute_uniq, new_embeddings):
            if self.store:
                self.store.put(text=text, embedding=embed)
            cache_hits[to_compute[text]] = embed
            pass

        if self.store:
            t2 = time.time()
            logging.debug(
                "stored %d embeddings in %f s", len(to_compute_uniq), round(t2 - t1, 2)
            )
            pass
        return cast(list[Embedding], cache_hits)
