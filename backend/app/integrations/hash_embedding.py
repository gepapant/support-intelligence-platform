import hashlib
import math
import re

from app.domain.embedding import EMBEDDING_DIMENSIONS


class HashEmbeddingProvider:
    model_name = "hash-embedding-dev-v2"
    dimensions = EMBEDDING_DIMENSIONS

    def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return [self._embed_text(text) for text in texts]

    def _embed_text(
        self,
        text: str,
    ) -> list[float]:
        vector = [0.0 for _ in range(self.dimensions)]

        normalized = text.lower()

        words = re.findall(
            r"\w+",
            normalized,
            flags=re.UNICODE,
        )

        features = list(words)

        for word in words:
            if len(word) >= 3:
                features.extend(
                    word[index : index + 3] for index in range(len(word) - 2)
                )

        for feature in features:
            digest = hashlib.sha256(feature.encode("utf-8")).digest()

            index = (
                int.from_bytes(
                    digest[:4],
                    byteorder="big",
                )
                % self.dimensions
            )

            vector[index] += 1.0

        magnitude = math.sqrt(sum(value * value for value in vector))

        if magnitude == 0:
            return vector

        return [value / magnitude for value in vector]
