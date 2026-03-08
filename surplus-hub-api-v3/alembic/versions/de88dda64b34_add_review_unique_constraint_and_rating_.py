"""add_review_unique_constraint_and_rating_check

Revision ID: de88dda64b34
Revises: search_logs_001
Create Date: 2026-02-28 13:21:13.168332

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'de88dda64b34'
down_revision = 'search_logs_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint('uq_review_per_material', 'reviews', ['reviewer_id', 'material_id'])
    # ck_review_rating already exists in the DB (added via model __table_args__)
    # Idempotent: only add if missing
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE reviews ADD CONSTRAINT ck_review_rating CHECK (rating >= 1 AND rating <= 5);
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE reviews DROP CONSTRAINT IF EXISTS ck_review_rating")
    op.drop_constraint('uq_review_per_material', 'reviews', type_='unique')
