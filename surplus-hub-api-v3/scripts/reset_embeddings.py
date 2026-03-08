"""Reset all embedding vectors after switching AI_PROVIDER.

Usage:
    python -m scripts.reset_embeddings

Embeddings are model-specific and not compatible across providers.
Run this script after changing AI_PROVIDER, then restart the server
to re-generate embeddings on demand.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from app.db.session import SessionLocal


def main():
    db = SessionLocal()
    try:
        result = db.execute(
            text("UPDATE materials SET embedding_vector = NULL WHERE embedding_vector IS NOT NULL")
        )
        db.commit()
        print(f"Reset {result.rowcount} embedding vectors.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
