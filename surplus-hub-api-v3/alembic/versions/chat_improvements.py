"""Chat improvements: add indexes to messages table

Revision ID: chat_improve_001
Revises: sprint4_001
Create Date: 2026-02-14
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'chat_improve_001'
down_revision = 'sprint4_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add indexes to messages table for chat query performance
    op.create_index('ix_messages_chat_room_id', 'messages', ['chat_room_id'])
    op.create_index('ix_messages_sender_id', 'messages', ['sender_id'])
    op.create_index('ix_messages_is_read', 'messages', ['is_read'])


def downgrade() -> None:
    op.drop_index('ix_messages_is_read', table_name='messages')
    op.drop_index('ix_messages_sender_id', table_name='messages')
    op.drop_index('ix_messages_chat_room_id', table_name='messages')
