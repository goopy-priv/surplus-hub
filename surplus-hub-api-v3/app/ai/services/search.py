"""Hybrid semantic search service (keyword + vector)."""

import hashlib
import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy import case, func, text
from sqlalchemy.orm import Session

from app.ai.clients.embeddings import build_search_text, generate_embedding
from app.models.material import Material

logger = logging.getLogger(__name__)

KEYWORD_WEIGHT = 0.3
VECTOR_WEIGHT = 0.7
MIN_SIMILARITY = 0.3

# ---------------------------------------------------------------------------
# Embedding cache (thread-safe in-memory LRU)
# ---------------------------------------------------------------------------
_embedding_cache: Dict[str, List[float]] = {}
_cache_lock = threading.Lock()
_CACHE_MAX_SIZE = 1000


def get_or_generate_embedding(text_input: str) -> List[float]:
    """Return cached embedding or generate and cache a new one."""
    cache_key = hashlib.md5(text_input.encode()).hexdigest()
    with _cache_lock:
        if cache_key in _embedding_cache:
            return _embedding_cache[cache_key]
    embedding = generate_embedding(text_input)
    with _cache_lock:
        if len(_embedding_cache) >= _CACHE_MAX_SIZE:
            oldest_key = next(iter(_embedding_cache))
            del _embedding_cache[oldest_key]
        _embedding_cache[cache_key] = embedding
    return embedding


# ---------------------------------------------------------------------------
# Haversine distance helper
# ---------------------------------------------------------------------------
def _haversine_distance_expr(lat: float, lng: float):
    """SQLAlchemy expression for haversine distance in km."""
    return (
        6371
        * func.acos(
            func.least(
                1.0,
                func.cos(func.radians(lat))
                * func.cos(func.radians(Material.location_lat))
                * func.cos(func.radians(Material.location_lng) - func.radians(lng))
                + func.sin(func.radians(lat))
                * func.sin(func.radians(Material.location_lat)),
            )
        )
    )


# ---------------------------------------------------------------------------
# Keyword-only fallback search
# ---------------------------------------------------------------------------
def keyword_only_search(
    db: Session,
    query: str,
    page: int = 1,
    limit: int = 20,
    category: Optional[str] = None,
    status: str = "ACTIVE",
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    location_lat: Optional[float] = None,
    location_lng: Optional[float] = None,
    radius_km: Optional[float] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    trade_method: Optional[str] = None,
    sort_by: str = "relevance",
) -> Tuple[List[dict], int, str]:
    """Keyword-only search fallback when embedding generation fails.

    Returns (results, total_count, search_mode).
    """
    base_filter = Material.status == status
    if category:
        base_filter = base_filter & (Material.category == category)
    if price_min is not None:
        base_filter = base_filter & (Material.price >= price_min)
    if price_max is not None:
        base_filter = base_filter & (Material.price <= price_max)
    if trade_method:
        base_filter = base_filter & (Material.trade_method == trade_method)
    if date_from:
        base_filter = base_filter & (Material.created_at >= date_from)
    if date_to:
        base_filter = base_filter & (Material.created_at <= date_to)

    keyword_filter = Material.title.ilike(f"%{query}%") | Material.description.ilike(
        f"%{query}%"
    )

    # Distance filter
    distance_col = None
    if location_lat is not None and location_lng is not None:
        distance_col = _haversine_distance_expr(location_lat, location_lng).label(
            "distance_km"
        )
        base_filter = base_filter & (Material.location_lat.isnot(None))
        base_filter = base_filter & (Material.location_lng.isnot(None))
        if radius_km:
            base_filter = base_filter & (
                _haversine_distance_expr(location_lat, location_lng) <= radius_km
            )

    count_q = (
        db.query(func.count(Material.id)).filter(base_filter).filter(keyword_filter)
    )
    total = count_q.scalar() or 0

    # Build query
    query_cols = [Material]
    if distance_col is not None:
        query_cols.append(distance_col)

    q = db.query(*query_cols).filter(base_filter).filter(keyword_filter)

    # Sorting
    if sort_by == "price_asc":
        q = q.order_by(Material.price.asc())
    elif sort_by == "price_desc":
        q = q.order_by(Material.price.desc())
    elif sort_by == "newest":
        q = q.order_by(Material.created_at.desc())
    else:
        q = q.order_by(Material.created_at.desc())

    offset = (page - 1) * limit
    rows = q.offset(offset).limit(limit).all()

    results = []
    for row in rows:
        if distance_col is not None:
            material, dist = row[0], float(row[1])
        else:
            material = row
            dist = None
        results.append(
            {
                "material": material,
                "score": 1.0,
                "vector_similarity": 0.0,
                "keyword_score": 1.0,
                "distance_km": dist,
            }
        )

    return results, total, "keyword_only"


# ---------------------------------------------------------------------------
# Hybrid search (keyword + vector) with dynamic filters
# ---------------------------------------------------------------------------
def hybrid_search(
    db: Session,
    query: str,
    page: int = 1,
    limit: int = 20,
    category: Optional[str] = None,
    status: str = "ACTIVE",
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    location_lat: Optional[float] = None,
    location_lng: Optional[float] = None,
    radius_km: Optional[float] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    trade_method: Optional[str] = None,
    sort_by: str = "relevance",
) -> Tuple[List[dict], int, str]:
    """Hybrid search combining keyword matching and vector similarity.

    Returns (results, total_count, search_mode) where each result is a dict with
    'material', 'score', 'vector_similarity', 'keyword_score', and 'distance_km' keys.
    search_mode is 'hybrid' or 'keyword_only'.
    """
    try:
        query_embedding = get_or_generate_embedding(query)
    except Exception:
        logger.warning("Embedding generation failed, falling back to keyword search")
        return keyword_only_search(
            db,
            query,
            page=page,
            limit=limit,
            category=category,
            status=status,
            price_min=price_min,
            price_max=price_max,
            location_lat=location_lat,
            location_lng=location_lng,
            radius_km=radius_km,
            date_from=date_from,
            date_to=date_to,
            trade_method=trade_method,
            sort_by=sort_by,
        )

    # Build base query filtering
    base_filter = Material.status == status
    if category:
        base_filter = base_filter & (Material.category == category)
    if price_min is not None:
        base_filter = base_filter & (Material.price >= price_min)
    if price_max is not None:
        base_filter = base_filter & (Material.price <= price_max)
    if trade_method:
        base_filter = base_filter & (Material.trade_method == trade_method)
    if date_from:
        base_filter = base_filter & (Material.created_at >= date_from)
    if date_to:
        base_filter = base_filter & (Material.created_at <= date_to)

    # Only search materials that have embeddings
    base_filter = base_filter & (Material.embedding_vector.isnot(None))

    # Distance filter
    distance_col = None
    if location_lat is not None and location_lng is not None:
        distance_col = _haversine_distance_expr(location_lat, location_lng).label(
            "distance_km"
        )
        base_filter = base_filter & (Material.location_lat.isnot(None))
        base_filter = base_filter & (Material.location_lng.isnot(None))
        if radius_km:
            base_filter = base_filter & (
                _haversine_distance_expr(location_lat, location_lng) <= radius_km
            )

    # Cosine distance via pgvector <=> operator (lower = more similar)
    cosine_distance = Material.embedding_vector.cosine_distance(query_embedding)
    vector_similarity = (1 - cosine_distance).label("vector_similarity")

    # Keyword score: simple ILIKE match on title/description
    keyword_score = case(
        (
            Material.title.ilike(f"%{query}%")
            | Material.description.ilike(f"%{query}%"),
            1.0,
        ),
        else_=0.0,
    ).label("keyword_score")

    # Hybrid score
    hybrid_score = (
        KEYWORD_WEIGHT * keyword_score + VECTOR_WEIGHT * vector_similarity
    ).label("hybrid_score")

    # Count query
    count_q = (
        db.query(func.count(Material.id))
        .filter(base_filter)
        .filter((1 - cosine_distance) >= MIN_SIMILARITY)
    )
    total = count_q.scalar() or 0

    # Main query columns
    query_cols = [Material, hybrid_score, vector_similarity, keyword_score]
    if distance_col is not None:
        query_cols.append(distance_col)

    q = (
        db.query(*query_cols)
        .filter(base_filter)
        .filter((1 - cosine_distance) >= MIN_SIMILARITY)
    )

    # Sorting
    if sort_by == "price_asc":
        q = q.order_by(Material.price.asc())
    elif sort_by == "price_desc":
        q = q.order_by(Material.price.desc())
    elif sort_by == "newest":
        q = q.order_by(Material.created_at.desc())
    elif sort_by == "distance" and distance_col is not None:
        q = q.order_by(distance_col.asc())
    else:
        q = q.order_by(hybrid_score.desc())

    offset = (page - 1) * limit
    rows = q.offset(offset).limit(limit).all()

    results = []
    for row in rows:
        if distance_col is not None:
            material, h_score, v_sim, k_score, dist = (
                row[0],
                float(row[1]),
                float(row[2]),
                float(row[3]),
                float(row[4]),
            )
        else:
            material, h_score, v_sim, k_score = (
                row[0],
                float(row[1]),
                float(row[2]),
                float(row[3]),
            )
            dist = None
        results.append(
            {
                "material": material,
                "score": h_score,
                "vector_similarity": v_sim,
                "keyword_score": k_score,
                "distance_km": dist,
            }
        )

    return results, total, "hybrid"


def vector_search_only(
    db: Session,
    query: str,
    limit: int = 10,
    status: str = "ACTIVE",
) -> List[Tuple[Material, float]]:
    """Pure vector similarity search. Returns (Material, similarity) pairs."""
    try:
        query_embedding = get_or_generate_embedding(query)
    except Exception:
        logger.exception("Failed to generate query embedding")
        return []

    cosine_distance = Material.embedding_vector.cosine_distance(query_embedding)
    similarity = (1 - cosine_distance).label("similarity")

    rows = (
        db.query(Material, similarity)
        .filter(Material.status == status)
        .filter(Material.embedding_vector.isnot(None))
        .filter((1 - cosine_distance) >= MIN_SIMILARITY)
        .order_by(cosine_distance)
        .limit(limit)
        .all()
    )

    return [(row[0], float(row[1])) for row in rows]


def find_similar_materials(
    db: Session,
    material_id: int,
    limit: int = 5,
) -> List[Tuple[Material, float]]:
    """Find materials similar to a given material."""
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material or material.embedding_vector is None:
        return []

    cosine_distance = Material.embedding_vector.cosine_distance(
        material.embedding_vector
    )
    similarity = (1 - cosine_distance).label("similarity")

    rows = (
        db.query(Material, similarity)
        .filter(Material.id != material_id)
        .filter(Material.status == "ACTIVE")
        .filter(Material.embedding_vector.isnot(None))
        .filter((1 - cosine_distance) >= MIN_SIMILARITY)
        .order_by(cosine_distance)
        .limit(limit)
        .all()
    )

    return [(row[0], float(row[1])) for row in rows]


# ---------------------------------------------------------------------------
# Search suggestions
# ---------------------------------------------------------------------------
def get_search_suggestions(
    db: Session,
    query: str,
    limit: int = 5,
) -> List[dict]:
    """Return search suggestions based on title prefix, categories, and popular queries."""
    suggestions = []

    if len(query) < 2:
        return suggestions

    # 1. Title prefix matches
    title_matches = (
        db.query(Material.title)
        .filter(Material.status == "ACTIVE")
        .filter(Material.title.ilike(f"%{query}%"))
        .distinct()
        .limit(limit)
        .all()
    )
    for row in title_matches:
        suggestions.append({"text": row[0], "type": "title", "count": None})

    # 2. Category matches
    cat_matches = (
        db.query(Material.category)
        .filter(Material.category.isnot(None))
        .filter(Material.category.ilike(f"%{query}%"))
        .distinct()
        .limit(3)
        .all()
    )
    for row in cat_matches:
        suggestions.append({"text": row[0], "type": "category", "count": None})

    # 3. Popular queries from search_logs
    try:
        from app.models.search_log import SearchLog

        popular = (
            db.query(SearchLog.query, func.count(SearchLog.id).label("cnt"))
            .filter(SearchLog.query.ilike(f"%{query}%"))
            .group_by(SearchLog.query)
            .order_by(func.count(SearchLog.id).desc())
            .limit(3)
            .all()
        )
        for row in popular:
            suggestions.append({"text": row[0], "type": "popular", "count": row[1]})
    except Exception:
        pass

    # Deduplicate by text, keep first occurrence
    seen = set()
    unique = []
    for s in suggestions:
        if s["text"] not in seen:
            seen.add(s["text"])
            unique.append(s)
    return unique[:limit]


def log_search_query(
    db: Session,
    query: str,
    results_count: int,
    user_id: Optional[int] = None,
) -> None:
    """Log a search query for analytics and suggestions."""
    try:
        from app.models.search_log import SearchLog

        log = SearchLog(query=query, user_id=user_id, results_count=results_count)
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()
        logger.debug("Failed to log search query", exc_info=True)
