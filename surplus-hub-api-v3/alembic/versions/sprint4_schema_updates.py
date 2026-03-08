"""Sprint 4: Add events, transactions, subscriptions, material review columns

Revision ID: sprint4_001
Revises: sprint3_001
Create Date: 2026-02-14
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'sprint4_001'
down_revision = 'sprint3_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('event_type', sa.String(), server_default='general'),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 2. Add admin review columns to materials
    op.add_column('materials', sa.Column('reviewed_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True))
    op.add_column('materials', sa.Column('review_note', sa.Text(), nullable=True))
    op.add_column('materials', sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True))

    # 3. Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('material_id', sa.Integer(), sa.ForeignKey('materials.id'), nullable=False),
        sa.Column('seller_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('buyer_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), server_default='PENDING'),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )

    # 4. Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('plan', sa.String(), server_default='free'),
        sa.Column('status', sa.String(), server_default='active'),
        sa.Column('iap_receipt_id', sa.String(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_subscriptions_user_id', 'subscriptions', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_subscriptions_user_id', table_name='subscriptions')
    op.drop_table('subscriptions')
    op.drop_table('transactions')
    op.drop_column('materials', 'reviewed_at')
    op.drop_column('materials', 'review_note')
    op.drop_column('materials', 'reviewed_by')
    op.drop_table('events')
