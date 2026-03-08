"""Environment-based embedding provider with thread-safe singleton pattern.

Supports three providers:
- LocalEmbeddingProvider: sentence-transformers/BAAI/bge-m3 (APP_ENV=local)
- OpenAIEmbeddingProvider: OpenAI text-embedding-3-small (APP_ENV=dev/stage/prod)
- VertexEmbeddingProvider: Gemini embedding via Vertex AI (AI_PROVIDER=vertex)
"""

import logging
import threading
from typing import List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

_provider = None
_provider_lock = threading.Lock()


class LocalEmbeddingProvider:
    """sentence-transformers based local embedding provider."""

    def __init__(self):
        self._model = None
        self._lock = threading.Lock()

    def _load_model(self):
        if self._model is None:
            with self._lock:
                if self._model is None:
                    from sentence_transformers import SentenceTransformer

                    logger.info("Loading local embedding model: %s", settings.EMBEDDING_MODEL_NAME)
                    self._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
                    logger.info("Local embedding model loaded successfully")
        return self._model

    def generate(self, text: str) -> List[float]:
        model = self._load_model()
        vector = model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    def generate_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        model = self._load_model()
        vectors = model.encode(texts, batch_size=batch_size, normalize_embeddings=True)
        return [v.tolist() for v in vectors]


class OpenAIEmbeddingProvider:
    """OpenAI API based embedding provider."""

    def __init__(self):
        self._client = None
        self._lock = threading.Lock()

    def _get_client(self):
        if self._client is None:
            with self._lock:
                if self._client is None:
                    import openai

                    if not settings.OPENAI_API_KEY:
                        raise ValueError(
                            f"OPENAI_API_KEY is required when APP_ENV={settings.APP_ENV}. "
                            "Set it in .env or environment variables."
                        )
                    self._client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                    logger.info(
                        "OpenAI embedding client initialized (model=%s, dim=%d)",
                        settings.OPENAI_EMBEDDING_MODEL,
                        settings.EMBEDDING_DIMENSION,
                    )
        return self._client

    def _call_api(self, input_data, dimensions: int):
        """Single API call with retry logic."""
        from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
        import openai

        client = self._get_client()

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((openai.RateLimitError, openai.APITimeoutError, openai.APIConnectionError)),
        )
        def _do_call():
            return client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=input_data,
                dimensions=dimensions,
            )

        return _do_call()

    def generate(self, text: str) -> List[float]:
        response = self._call_api(text, dimensions=settings.EMBEDDING_DIMENSION)
        return response.data[0].embedding

    def generate_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        all_embeddings: List[List[float]] = []
        for i in range(0, len(texts), batch_size):
            chunk = texts[i : i + batch_size]
            response = self._call_api(chunk, dimensions=settings.EMBEDDING_DIMENSION)
            sorted_data = sorted(response.data, key=lambda x: x.index)
            all_embeddings.extend([d.embedding for d in sorted_data])
        return all_embeddings


class VertexEmbeddingProvider:
    """Gemini embedding via Vertex AI."""

    VERTEX_EMBEDDING_MODEL = "gemini-embedding-001"

    def __init__(self):
        self._client = None
        self._lock = threading.Lock()

    def _get_client(self):
        if self._client is None:
            with self._lock:
                if self._client is None:
                    from google import genai
                    self._client = genai.Client(
                        vertexai=True,
                        project=settings.GOOGLE_CLOUD_PROJECT,
                        location=settings.GOOGLE_CLOUD_LOCATION,
                    )
                    logger.info(
                        "Vertex AI embedding client initialized (model=%s, dim=%d)",
                        self.VERTEX_EMBEDDING_MODEL,
                        settings.EMBEDDING_DIMENSION,
                    )
        return self._client

    def generate(self, text: str) -> List[float]:
        from google.genai import types
        client = self._get_client()
        result = client.models.embed_content(
            model=self.VERTEX_EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=settings.EMBEDDING_DIMENSION,
            ),
        )
        return list(result.embeddings[0].values)

    def generate_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        from google.genai import types
        client = self._get_client()
        all_embeddings: List[List[float]] = []
        for i in range(0, len(texts), batch_size):
            chunk = texts[i : i + batch_size]
            result = client.models.embed_content(
                model=self.VERTEX_EMBEDDING_MODEL,
                contents=chunk,
                config=types.EmbedContentConfig(
                    output_dimensionality=settings.EMBEDDING_DIMENSION,
                ),
            )
            all_embeddings.extend([list(e.values) for e in result.embeddings])
        return all_embeddings


def _get_provider():
    """Return the singleton embedding provider based on AI_PROVIDER / APP_ENV."""
    global _provider
    if _provider is None:
        with _provider_lock:
            if _provider is None:
                if settings.use_vertex:
                    _provider = VertexEmbeddingProvider()
                elif settings.use_local_embedding:
                    _provider = LocalEmbeddingProvider()
                else:
                    _provider = OpenAIEmbeddingProvider()
                logger.info(
                    "Embedding provider: %s (AI_PROVIDER=%s, APP_ENV=%s)",
                    type(_provider).__name__,
                    settings.AI_PROVIDER,
                    settings.APP_ENV,
                )
    return _provider


def _get_model():
    """Backward-compatible warm-up. Called from main.py startup."""
    provider = _get_provider()
    if isinstance(provider, LocalEmbeddingProvider):
        provider._load_model()
    return provider


def build_search_text(
    title: str,
    description: Optional[str] = None,
    category: Optional[str] = None,
) -> str:
    """Combine material fields into a single text for embedding."""
    parts = [title]
    if category:
        parts.append(f"카테고리: {category}")
    if description:
        parts.append(description[:500])
    return " ".join(parts)


def generate_embedding(text: str) -> List[float]:
    """Generate a single embedding vector."""
    return _get_provider().generate(text)


def generate_embeddings_batch(
    texts: List[str], batch_size: int = 32
) -> List[List[float]]:
    """Generate embeddings for a batch of texts."""
    return _get_provider().generate_batch(texts, batch_size)
