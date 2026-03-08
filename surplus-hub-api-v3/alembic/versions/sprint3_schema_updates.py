"""Sprint 3: Add likes, reviews tables and materials.likes_count

Revision ID: sprint3_001
Revises: sprint2_001
Create Date: 2026-02-14
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'sprint3_001'
down_revision = 'sprint2_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add likes_count to materials
    op.add_column('materials', sa.Column('likes_count', sa.Integer(), server_default='0'))

    # 2. Create material_likes table
    op.create_table(
        'material_likes',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('material_id', sa.Integer(), sa.ForeignKey('materials.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'material_id', name='uq_material_like'),
    )

    # 3. Create post_likes table
    op.create_table(
        'post_likes',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('post_id', sa.Integer(), sa.ForeignKey('posts.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'post_id', name='uq_post_like'),
    )

    # 4. Create reviews table
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('reviewer_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('target_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('material_id', sa.Integer(), sa.ForeignKey('materials.id'), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='ck_review_rating'),
    )
    op.create_index('ix_reviews_target_user_id', 'reviews', ['target_user_id'])


def downgrade() -> None:
    op.drop_index('ix_reviews_target_user_id', table_name='reviews')
    op.drop_table('reviews')
    op.drop_table('post_likes')
    op.drop_table('material_likes')
    op.drop_column('materials', 'likes_count')
