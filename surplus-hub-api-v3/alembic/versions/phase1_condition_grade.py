"""Add condition_grade to materials

Revision ID: phase1_001
Revises: de88dda64b34
Create Date: 2026-03-26

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'phase1_001'
down_revision = 'de88dda64b34'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('materials', sa.Column('condition_grade', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('materials', 'condition_grade')
