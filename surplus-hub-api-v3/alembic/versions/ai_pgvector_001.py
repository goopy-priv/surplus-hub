"""AI: pgvector extension + embedding_vector column on materials

Revision ID: ai_pgvector_001
Revises: chat_improve_001
Create Date: 2026-02-21
"""
from alembic import op
import sqlalchemy as sa

revision = 'ai_pgvector_001'
down_revision = 'chat_improve_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # 2. Add embedding_vector column
    op.execute(
        "ALTER TABLE materials ADD COLUMN embedding_vector vector(1024)"
    )

    # 3. Create HNSW index for cosine similarity search
    op.execute(
        "CREATE INDEX idx_materials_embedding_hnsw "
        "ON materials USING hnsw (embedding_vector vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_materials_embedding_hnsw")
    op.drop_column('materials', 'embedding_vector')
    op.execute("DROP EXTENSION IF EXISTS vector")
