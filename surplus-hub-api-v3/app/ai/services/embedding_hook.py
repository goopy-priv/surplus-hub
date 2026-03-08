"""Hook to auto-generate embeddings when materials are created/updated."""

import logging

from sqlalchemy.orm import Session

from app.ai.clients.embeddings import build_search_text, generate_embedding
from app.models.material import Material

logger = logging.getLogger(__name__)


def update_material_embedding(db: Session, material: Material) -> bool:
    """Generate and store embedding for a material. Returns True on success.

    Wrapped in try/except so failures never break the main flow.
    """
    try:
        search_text = build_search_text(
            title=material.title,
            description=material.description,
            category=material.category,
        )
        embedding = generate_embedding(search_text)
        material.embedding_vector = embedding
        db.add(material)
        db.commit()
        db.refresh(material)
        logger.info("Updated embedding for material %d", material.id)
        return True
    except Exception:
        logger.exception("Failed to update embedding for material %d", material.id)
        db.rollback()
        return False


def update_material_embedding_background(material_id: int) -> bool:
    """Generate and store embedding in a background task with its own DB session.

    This function creates and manages its own DB session so it can safely
    run outside the request lifecycle (e.g., in FastAPI BackgroundTasks).
    """
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        material = db.get(Material, material_id)
        if material is None:
            logger.warning("Background embedding: material %d not found", material_id)
            return False

        search_text = build_search_text(
            title=material.title,
            description=material.description,
            category=material.category,
        )
        embedding = generate_embedding(search_text)
        material.embedding_vector = embedding
        db.add(material)
        db.commit()
        logger.info("Background embedding updated for material %d", material_id)
        return True
    except Exception:
        logger.exception("Background embedding failed for material %d", material_id)
        db.rollback()
        return False
    finally:
        db.close()
