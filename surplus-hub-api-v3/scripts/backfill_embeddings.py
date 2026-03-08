"""Backfill embeddings for existing materials.

Usage:
    python -m scripts.backfill_embeddings
"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai.clients.embeddings import (
    build_search_text,
    generate_embeddings_batch,
)
from app.db.session import SessionLocal
from app.models.material import Material

BATCH_SIZE = 32


def main():
    db = SessionLocal()
    try:
        total = db.query(Material).filter(Material.embedding_vector.is_(None)).count()
        print(f"Materials without embeddings: {total}")

        if total == 0:
            print("Nothing to backfill.")
            return

        processed = 0
        offset = 0

        while offset < total:
            materials = (
                db.query(Material)
                .filter(Material.embedding_vector.is_(None))
                .order_by(Material.id)
                .offset(0)  # always 0 since we update in place
                .limit(BATCH_SIZE)
                .all()
            )

            if not materials:
                break

            texts = [
                build_search_text(
                    title=m.title,
                    description=m.description,
                    category=m.category,
                )
                for m in materials
            ]

            embeddings = generate_embeddings_batch(texts, batch_size=BATCH_SIZE)

            for m, emb in zip(materials, embeddings):
                m.embedding_vector = emb

            db.commit()
            processed += len(materials)
            print(f"  Processed {processed}/{total} materials")

        print(f"Done! {processed} materials backfilled.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
