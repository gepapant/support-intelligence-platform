from typing import Protocol


class EmbeddingProviderError(Exception):
    pass


class EmbeddingProvider(Protocol):
    model_name: str
    dimensions: int

    def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]: ...
