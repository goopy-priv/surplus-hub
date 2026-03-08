"""Sprint 1: Add user timestamps, material_images order, categories table

Revision ID: sprint1_001
Revises: 75ef6cef2f88
Create Date: 2026-02-14
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'sprint1_001'
down_revision = '75ef6cef2f88'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add timestamps to users table
    op.add_column('users', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()))

    # 2. Add display_order to material_images
    op.add_column('material_images', sa.Column('display_order', sa.Integer(), server_default='0'))

    # 3. Add server_default to materials.updated_at (was nullable without default)
    op.alter_column('materials', 'updated_at', server_default=sa.func.now())

    # 4. Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('icon', sa.String(), nullable=True),
        sa.Column('display_order', sa.Integer(), server_default='0'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
    )
    op.create_index('ix_categories_name', 'categories', ['name'])


def downgrade() -> None:
    op.drop_index('ix_categories_name', table_name='categories')
    op.drop_table('categories')
    op.alter_column('materials', 'updated_at', server_default=None)
    op.drop_column('material_images', 'display_order')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
