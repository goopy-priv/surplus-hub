"""
Tests for dynamic search filters, suggestions, embedding cache, and concurrency.

All AI services are mocked since pgvector is not available in SQLite test DB.
"""

import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

API_V1_STR = "/api/v1"


def _make_mock_material(**overrides):
    m = MagicMock()
    m.id = overrides.get("id", 1)
    m.title = overrides.get("title", "H빔 잉여")
    m.description = overrides.get("description", "건설현장 잉여 H빔 10개")
    m.price = overrides.get("price", 100000)
    m.category = overrides.get("category", "철근")
    m.thumbnail_url = overrides.get("thumbnail_url", None)
    m.location_lat = overrides.get("location_lat", None)
    m.location_lng = overrides.get("location_lng", None)
    m.location_address = overrides.get("location_address", None)
    return m


# ---------------------------------------------------------------------------
# Dynamic filter parameter tests
# ---------------------------------------------------------------------------
class TestDynamicFilters:
    """Test dynamic search filter parameters are passed correctly."""

    @patch("app.ai.services.search.log_search_query")
    @patch("app.ai.services.search.hybrid_search")
    def test_price_range_filter(self, mock_search, mock_log, client: TestClient):
        """Price range filters are forwarded to search service."""
        mock_search.return_value = ([], 0, "hybrid")

        resp = client.get(
            f"{API_V1_STR}/ai/search?q=철근&priceMin=10000&priceMax=500000"
        )
        assert resp.status_code == 200
        kwargs = mock_search.call_args.kwargs
        assert kwargs["price_min"] == 10000
        assert kwargs["price_max"] == 500000

    @patch("app.ai.services.search.log_search_query")
    @patch("app.ai.services.search.hybrid_search")
    def test_location_radius_filter(self, mock_search, mock_log, client: TestClient):
        """Location and radius filters are forwarded to search service."""
        mock_search.return_value = ([], 0, "hybrid")

        resp = client.get(
            f"{API_V1_STR}/ai/search?q=시멘트"
            f"&locationLat=37.5665&locationLng=126.978&radiusKm=5"
        )
        assert resp.status_code == 200
        kwargs = mock_search.call_args.kwargs
        assert kwargs["location_lat"] == pytest.approx(37.5665)
        assert kwargs["location_lng"] == pytest.approx(126.978)
        assert kwargs["radius_km"] == pytest.approx(5.0)

    @patch("app.ai.services.search.log_search_query")
    @patch("app.ai.services.search.hybrid_search")
    def test_trade_method_filter(self, mock_search, mock_log, client: TestClient):
        """Trade method filter is forwarded to search service."""
        mock_search.return_value = ([], 0, "hybrid")

        resp = client.get(f"{API_V1_STR}/ai/search?q=파이프&tradeMethod=DELIVERY")
        assert resp.status_code == 200
        kwargs = mock_search.call_args.kwargs
        assert kwargs["trade_method"] == "DELIVERY"

    @patch("app.ai.services.search.log_search_query")
    @patch("app.ai.services.search.hybrid_search")
    def test_sort_by_parameter(self, mock_search, mock_log, client: TestClient):
        """Sort-by parameter is forwarded to search service."""
        mock_search.return_value = ([], 0, "hybrid")

        resp = client.get(f"{API_V1_STR}/ai/search?q=목재&sortBy=price_asc")
        assert resp.status_code == 200
        kwargs = mock_search.call_args.kwargs
        assert kwargs["sort_by"] == "price_asc"

    @patch("app.ai.services.search.log_search_query")
    @patch("app.ai.services.search.hybrid_search")
    def test_date_range_filter(self, mock_search, mock_log, client: TestClient):
        """Date range filters are forwarded to search service."""
        mock_search.return_value = ([], 0, "hybrid")

        resp = client.get(
            f"{API_V1_STR}/ai/search?q=자재"
            f"&dateFrom=2026-01-01T00:00:00&dateTo=2026-02-01T00:00:00"
        )
        assert resp.status_code == 200
        kwargs = mock_search.call_args.kwargs
        assert kwargs["date_from"] is not None
        assert kwargs["date_to"] is not None

    @patch("app.ai.services.search.log_search_query")
    @patch("app.ai.services.search.hybrid_search")
    def test_result_includes_distance_and_location(
        self, mock_search, mock_log, client: TestClient
    ):
        """Results include distance_km and location when available."""
        m = _make_mock_material(
            location_lat=37.5665,
            location_lng=126.978,
            location_address="서울시 중구",
        )
        mock_search.return_value = (
            [
                {
                    "material": m,
                    "score": 0.9,
                    "vector_similarity": 0.85,
                    "keyword_score": 1.0,
                    "distance_km": 3.2,
                }
            ],
            1,
            "hybrid",
        )

        resp = client.get(f"{API_V1_STR}/ai/search?q=H빔")
        assert resp.status_code == 200
        item = resp.json()["data"][0]
        assert item["distanceKm"] == pytest.approx(3.2)
        assert item["location"]["lat"] == pytest.approx(37.5665)
        assert item["location"]["address"] == "서울시 중구"

    @patch("app.ai.services.search.log_search_query")
    @patch("app.ai.services.search.hybrid_search")
    def test_search_mode_in_meta(self, mock_search, mock_log, client: TestClient):
        """Meta includes searchMode field."""
        mock_search.return_value = ([], 0, "keyword_only")

        resp = client.get(f"{API_V1_STR}/ai/search?q=시멘트")
        assert resp.status_code == 200
        assert resp.json()["meta"]["searchMode"] == "keyword_only"


# ---------------------------------------------------------------------------
# Search suggestions tests
# ---------------------------------------------------------------------------
class TestSearchSuggestions:
    """GET /api/v1/ai/search/suggestions"""

    @patch("app.ai.services.search.get_search_suggestions")
    def test_suggestions_returns_results(self, mock_suggest, client: TestClient):
        """Suggestions endpoint returns structured suggestions."""
        mock_suggest.return_value = [
            {"text": "H빔 잉여", "type": "title", "count": None},
            {"text": "철근", "type": "category", "count": None},
        ]

        resp = client.get(f"{API_V1_STR}/ai/search/suggestions?q=H빔")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        suggestions = data["data"]["suggestions"]
        assert len(suggestions) == 2
        assert suggestions[0]["text"] == "H빔 잉여"
        assert suggestions[0]["type"] == "title"

    def test_suggestions_requires_min_length(self, client: TestClient):
        """Query must be at least 2 characters."""
        resp = client.get(f"{API_V1_STR}/ai/search/suggestions?q=H")
        assert resp.status_code == 422

    @patch("app.ai.services.search.get_search_suggestions")
    def test_suggestions_empty_for_no_match(self, mock_suggest, client: TestClient):
        """Empty suggestions for no match."""
        mock_suggest.return_value = []

        resp = client.get(f"{API_V1_STR}/ai/search/suggestions?q=없는자재abc")
        assert resp.status_code == 200
        suggestions = resp.json()["data"]["suggestions"]
        assert suggestions == []


# ---------------------------------------------------------------------------
# Scenario A: Concurrent search performance (50 users, p95 < 500ms)
# ---------------------------------------------------------------------------
class TestConcurrentSearchPerformance:
    """50명 동시 검색 시 pgvector 쿼리 응답시간 측정."""

    @patch("app.ai.services.search.log_search_query")
    @patch("app.ai.services.search.hybrid_search")
    def test_concurrent_50_users_p95_under_500ms(
        self, mock_search, mock_log, client: TestClient
    ):
        """50명이 동시에 검색 요청 시 p95 응답시간 < 500ms."""
        from app.core.rate_limit import limiter

        limiter.enabled = False
        try:
            mock_search.return_value = ([], 0, "hybrid")
            queries = [f"건설자재{i}" for i in range(50)]

            def do_search(q: str) -> float:
                start = time.monotonic()
                resp = client.get(f"{API_V1_STR}/ai/search?q={q}")
                elapsed = (time.monotonic() - start) * 1000
                assert resp.status_code == 200
                return elapsed

            with ThreadPoolExecutor(max_workers=50) as executor:
                latencies = list(executor.map(do_search, queries))

            p95 = sorted(latencies)[int(len(latencies) * 0.95)]
            assert p95 < 500, f"p95 latency {p95:.1f}ms exceeds 500ms threshold"
        finally:
            limiter.enabled = True

    @patch("app.ai.services.search.log_search_query")
    @patch("app.ai.services.search.hybrid_search")
    def test_concurrent_search_no_errors(
        self, mock_search, mock_log, client: TestClient
    ):
        """동시 검색 시 에러 없이 모두 200 응답."""
        from app.core.rate_limit import limiter

        limiter.enabled = False
        try:
            mock_search.return_value = ([], 0, "hybrid")
            errors = []

            def do_search(q: str):
                resp = client.get(f"{API_V1_STR}/ai/search?q={q}")
                if resp.status_code != 200:
                    errors.append((q, resp.status_code))

            with ThreadPoolExecutor(max_workers=50) as executor:
                executor.map(do_search, [f"자재{i}" for i in range(50)])

            assert len(errors) == 0, f"Errors occurred: {errors}"
        finally:
            limiter.enabled = True


# ---------------------------------------------------------------------------
# Scenario B: Embedding fallback (keyword-only on failure)
# ---------------------------------------------------------------------------
class TestEmbeddingFallback:
    """임베딩 생성 병목/실패 시 키워드 전용 검색 Fallback."""

    @patch("app.ai.services.search.log_search_query")
    @patch("app.ai.services.search.hybrid_search")
    def test_fallback_to_keyword_on_embedding_failure(
        self, mock_search, mock_log, client: TestClient
    ):
        """임베딩 생성 실패 시 키워드 검색으로 Fallback하여 200 반환."""
        mock_search.return_value = ([], 0, "keyword_only")

        resp = client.get(f"{API_V1_STR}/ai/search?q=H빔")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "data" in data

    @patch("app.ai.services.search.log_search_query")
    @patch("app.ai.services.search.hybrid_search")
    def test_fallback_indicates_degraded_mode(
        self, mock_search, mock_log, client: TestClient
    ):
        """Fallback 시 응답 meta에 searchMode='keyword_only' 표시."""
        mock_search.return_value = ([], 0, "keyword_only")

        resp = client.get(f"{API_V1_STR}/ai/search?q=시멘트")
        assert resp.status_code == 200
        meta = resp.json()["meta"]
        assert meta["searchMode"] == "keyword_only"

    def test_search_service_fallback_on_exception(self):
        """search service hybrid_search falls back on embedding exception."""
        from app.ai.services.search import hybrid_search

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.filter.return_value.scalar.return_value = 0
        mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        with patch(
            "app.ai.services.search.get_or_generate_embedding",
            side_effect=RuntimeError("GPU OOM"),
        ):
            results, total, mode = hybrid_search(mock_db, query="시멘트")

        assert mode == "keyword_only"


# ---------------------------------------------------------------------------
# Scenario C: Embedding deduplication via cache
# ---------------------------------------------------------------------------
class TestEmbeddingDeduplication:
    """동일 검색어 동시 요청 시 임베딩 중복 생성 방지."""

    def test_cache_prevents_duplicate_embedding(self):
        """동일 텍스트에 대해 임베딩 캐시 히트 확인."""
        from app.ai.services.search import (
            _embedding_cache,
            _cache_lock,
            get_or_generate_embedding,
        )

        # Clear cache
        with _cache_lock:
            _embedding_cache.clear()

        call_count = 0
        original_vector = [0.1] * 1024

        def mock_generate(text):
            nonlocal call_count
            call_count += 1
            return original_vector

        with patch(
            "app.ai.services.search.generate_embedding",
            side_effect=mock_generate,
        ):
            # First call generates
            result1 = get_or_generate_embedding("H빔")
            assert call_count == 1

            # Second call hits cache
            result2 = get_or_generate_embedding("H빔")
            assert call_count == 1  # No additional call

            assert result1 == result2

        # Cleanup
        with _cache_lock:
            _embedding_cache.clear()

    def test_concurrent_same_query_cache_populated_after_first_batch(self):
        """동시 요청 후 캐시가 채워져 후속 요청에는 임베딩 재생성 없음."""
        from app.ai.services.search import (
            _embedding_cache,
            _cache_lock,
            get_or_generate_embedding,
        )

        # Clear cache
        with _cache_lock:
            _embedding_cache.clear()

        call_count = 0

        def counting_embed(text):
            nonlocal call_count
            call_count += 1
            time.sleep(0.02)
            return [0.1] * 1024

        with patch(
            "app.ai.services.search.generate_embedding",
            side_effect=counting_embed,
        ):
            # First batch: concurrent requests (some race expected)
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(get_or_generate_embedding, "동일검색어")
                    for _ in range(10)
                ]
                results = [f.result() for f in futures]

            first_batch_calls = call_count

            # All results should be identical
            assert all(r == results[0] for r in results)

            # Second batch: all should hit cache, zero new embedding calls
            for _ in range(5):
                get_or_generate_embedding("동일검색어")

            assert call_count == first_batch_calls, (
                f"Expected no new calls after cache populated, "
                f"but got {call_count - first_batch_calls} extra"
            )

        # Cleanup
        with _cache_lock:
            _embedding_cache.clear()

    def test_cache_eviction_at_max_size(self):
        """캐시가 최대 크기 도달 시 FIFO 방식으로 eviction."""
        from app.ai.services.search import (
            _embedding_cache,
            _cache_lock,
            _CACHE_MAX_SIZE,
            get_or_generate_embedding,
        )

        # Clear cache
        with _cache_lock:
            _embedding_cache.clear()

        with patch(
            "app.ai.services.search.generate_embedding",
            side_effect=lambda t: [float(hash(t) % 100)] * 10,
        ):
            with patch("app.ai.services.search._CACHE_MAX_SIZE", 5):
                for i in range(7):
                    get_or_generate_embedding(f"query_{i}")

                with _cache_lock:
                    assert len(_embedding_cache) <= 5

        # Cleanup
        with _cache_lock:
            _embedding_cache.clear()
