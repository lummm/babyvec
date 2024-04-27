from babyvec.computer.embedding_computer_jina_bert import EmbeddingComputerJinaBert
from babyvec.embed_provider.parallelized_cached_embed_provider import ParallelizedCachedEmbedProvider
from babyvec.index.numpy_faiss_index_factory import NumpyFaissIndexFactory
from babyvec.models import *
from babyvec.store.embedding_store_numpy import EmbeddingStoreNumpy


# 'packaged' providers
class CachedParallelJinaEmbedder(ParallelizedCachedEmbedProvider):
    def __init__(
            self,
            persist_dir: str,
            n_computers: int,
            device: str,
    ):
        store = EmbeddingStoreNumpy(persist_dir=persist_dir)
        super().__init__(
            n_computers=n_computers,
            compute_options=EmbedComputeOptions(
                device=device,
            ),
            computer_type=EmbeddingComputerJinaBert,
            store=store,
        )


def FaissNumpyJinaSemanticDb(
        *,
        persist_dir: str,
        device: str,
):
    """
    MAY NEED TO SET:
      export KMP_DUPLICATE_LIB_OK='True'
    """
    store = EmbeddingStoreNumpy(persist_dir=persist_dir)
    computer = EmbeddingComputerJinaBert(compute_options=EmbedComputeOptions(
        device=device,
    ))

    index_factory = NumpyFaissIndexFactory(
        store=store,
        computer=computer,
    )
    return index_factory.build_index()