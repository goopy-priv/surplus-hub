"""Add search_logs table

Revision ID: search_logs_001
Revises: chatroom_uq_001
Create Date: 2026-02-22
"""
from alembic import op
import sqlalchemy as sa

revision = 'search_logs_001'
down_revision = 'chatroom_uq_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'search_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('query', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('results_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_search_logs_query', 'search_logs', ['query'])


def downgrade() -> None:
    op.drop_index('ix_search_logs_query', table_name='search_logs')
    op.drop_table('search_logs')
