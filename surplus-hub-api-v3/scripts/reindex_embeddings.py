"""Re-index all material embeddings with the current provider.

Use this script when switching embedding providers (e.g., local -> OpenAI).
The new provider is auto-selected based on the APP_ENV environment variable.

Usage:
    python -m scripts.reindex_embeddings
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.ai.clients.embeddings import (
    build_search_text,
    generate_embeddings_batch,
    _get_provider,
)
from app.db.session import SessionLocal
from app.models.material import Material

BATCH_SIZE = 100


def main():
    provider = _get_provider()
    provider_name = type(provider).__name__
    print(f"APP_ENV={settings.APP_ENV}, Provider={provider_name}")
    print(f"Embedding dimension={settings.EMBEDDING_DIMENSION}")

    db = SessionLocal()
    try:
        total = db.query(Material).count()
        print(f"Total materials to re-index: {total}")

        if total == 0:
            print("No materials found.")
            return

        processed = 0
        offset = 0

        while offset < total:
            materials = (
                db.query(Material)
                .order_by(Material.id)
                .offset(offset)
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

            try:
                embeddings = generate_embeddings_batch(texts, batch_size=BATCH_SIZE)
            except Exception as e:
                print(f"  ERROR at offset {offset}: {e}")
                print(f"  Successfully processed {processed}/{total}. Resume from offset {offset}.")
                db.rollback()
                sys.exit(1)

            for m, emb in zip(materials, embeddings):
                m.embedding_vector = emb

            db.commit()
            processed += len(materials)
            offset += len(materials)
            print(f"  [{processed}/{total}] re-indexed ({processed * 100 // total}%)")

            # Rate limit throttle for OpenAI provider
            if not settings.use_local_embedding:
                time.sleep(0.5)

        print(f"Done! {processed} materials re-indexed with {provider_name}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
