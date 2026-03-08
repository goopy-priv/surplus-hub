"""Tests for environment-based embedding provider switching."""

from unittest.mock import patch, MagicMock
import pytest


class TestProviderSelection:
    """Test that the correct provider is selected based on APP_ENV."""

    def _reset_provider(self):
        """Reset the singleton provider for each test."""
        import app.ai.clients.embeddings as mod
        mod._provider = None

    def test_local_provider_selected(self):
        self._reset_provider()
        with patch("app.ai.clients.embeddings.settings") as mock_settings:
            mock_settings.use_vertex = False
            mock_settings.use_local_embedding = True
            mock_settings.EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
            mock_settings.APP_ENV = "local"
            mock_settings.AI_PROVIDER = "default"
            from app.ai.clients.embeddings import _get_provider, LocalEmbeddingProvider
            provider = _get_provider()
            assert isinstance(provider, LocalEmbeddingProvider)
        self._reset_provider()

    def test_openai_provider_selected(self):
        self._reset_provider()
        with patch("app.ai.clients.embeddings.settings") as mock_settings:
            mock_settings.use_vertex = False
            mock_settings.use_local_embedding = False
            mock_settings.OPENAI_API_KEY = "sk-test"
            mock_settings.OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
            mock_settings.EMBEDDING_DIMENSION = 1024
            mock_settings.APP_ENV = "dev"
            mock_settings.AI_PROVIDER = "default"
            from app.ai.clients.embeddings import _get_provider, OpenAIEmbeddingProvider
            provider = _get_provider()
            assert isinstance(provider, OpenAIEmbeddingProvider)
        self._reset_provider()


class TestUseLocalEmbeddingProperty:
    """Test settings.use_local_embedding property."""

    def _make_settings_with_env(self, app_env: str, ai_provider: str = "default"):
        """Create a mock settings object with a given APP_ENV."""
        mock = MagicMock()
        mock.APP_ENV = app_env
        mock.AI_PROVIDER = ai_provider
        # Call the real property logic (use_vertex first, then use_local_embedding)
        from app.core.config import Settings
        mock.use_vertex = Settings.use_vertex.fget(mock)
        mock.use_local_embedding = Settings.use_local_embedding.fget(mock)
        return mock

    def test_local_returns_true(self):
        s = self._make_settings_with_env("local")
        assert s.use_local_embedding is True

    def test_dev_returns_false(self):
        s = self._make_settings_with_env("dev")
        assert s.use_local_embedding is False

    def test_prod_returns_false(self):
        s = self._make_settings_with_env("prod")
        assert s.use_local_embedding is False


class TestGenerateEmbeddingDelegation:
    """Test that public functions delegate to the provider."""

    def _reset_provider(self):
        import app.ai.clients.embeddings as mod
        mod._provider = None

    def test_generate_embedding_delegates(self):
        self._reset_provider()
        mock_provider = MagicMock()
        mock_provider.generate.return_value = [0.1] * 1024
        with patch("app.ai.clients.embeddings._get_provider", return_value=mock_provider):
            from app.ai.clients.embeddings import generate_embedding
            result = generate_embedding("test text")
            mock_provider.generate.assert_called_once_with("test text")
            assert len(result) == 1024

    def test_generate_batch_delegates(self):
        self._reset_provider()
        mock_provider = MagicMock()
        mock_provider.generate_batch.return_value = [[0.1] * 1024, [0.2] * 1024]
        with patch("app.ai.clients.embeddings._get_provider", return_value=mock_provider):
            from app.ai.clients.embeddings import generate_embeddings_batch
            result = generate_embeddings_batch(["text1", "text2"])
            mock_provider.generate_batch.assert_called_once_with(["text1", "text2"], 32)
            assert len(result) == 2


class TestOpenAIDimensionParameter:
    """Test that OpenAI calls include dimensions=1024."""

    def test_openai_passes_dimension(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_embedding = MagicMock()
        mock_embedding.embedding = [0.1] * 1024
        mock_response.data = [mock_embedding]
        mock_client.embeddings.create.return_value = mock_response

        with patch("app.ai.clients.embeddings.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "sk-test"
            mock_settings.OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
            mock_settings.EMBEDDING_DIMENSION = 1024

            from app.ai.clients.embeddings import OpenAIEmbeddingProvider
            provider = OpenAIEmbeddingProvider()
            provider._client = mock_client

            result = provider.generate("test")

            mock_client.embeddings.create.assert_called_once_with(
                model="text-embedding-3-small",
                input="test",
                dimensions=1024,
            )
            assert len(result) == 1024


class TestBuildSearchText:
    """Test build_search_text remains unchanged."""

    def test_title_only(self):
        from app.ai.clients.embeddings import build_search_text
        assert build_search_text("H빔") == "H빔"

    def test_with_category(self):
        from app.ai.clients.embeddings import build_search_text
        result = build_search_text("H빔", category="철강")
        assert result == "H빔 카테고리: 철강"

    def test_with_all_fields(self):
        from app.ai.clients.embeddings import build_search_text
        result = build_search_text("H빔", description="좋은 품질", category="철강")
        assert result == "H빔 카테고리: 철강 좋은 품질"
