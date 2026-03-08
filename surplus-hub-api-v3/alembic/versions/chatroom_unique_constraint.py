"""Add unique constraint on chat_rooms (material_id, buyer_id, seller_id)

Revision ID: chatroom_uq_001
Revises: ai_pgvector_001
Create Date: 2026-02-22
"""
from alembic import op

revision = 'chatroom_uq_001'
down_revision = 'ai_pgvector_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_chatroom_material_buyer_seller",
        "chat_rooms",
        ["material_id", "buyer_id", "seller_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_chatroom_material_buyer_seller", "chat_rooms", type_="unique")
