"""Add core recovery tables for items, stickers, sessions, and relay messages."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260305_02"
down_revision: str | None = "20260305_01"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Create recovery-domain persistence tables and indexes."""
    op.create_table(
        "items",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column(
            "owner_user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("is_lost", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_items_owner_user_id", "items", ["owner_user_id"], unique=False)
    op.create_index("ix_items_is_lost", "items", ["is_lost"], unique=False)

    op.create_table(
        "qr_stickers",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column(
            "owner_user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "item_id",
            sa.String(length=36),
            sa.ForeignKey("items.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_qr_stickers_code", "qr_stickers", ["code"], unique=True)
    op.create_index("ix_qr_stickers_owner_user_id", "qr_stickers", ["owner_user_id"], unique=False)
    op.create_index("ix_qr_stickers_item_id", "qr_stickers", ["item_id"], unique=False)
    op.create_index("ix_qr_stickers_status", "qr_stickers", ["status"], unique=False)

    op.create_table(
        "lost_item_reports",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column(
            "item_id",
            sa.String(length=36),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "owner_user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("last_known_location", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_lost_item_reports_item_id", "lost_item_reports", ["item_id"], unique=False)
    op.create_index(
        "ix_lost_item_reports_owner_user_id",
        "lost_item_reports",
        ["owner_user_id"],
        unique=False,
    )
    op.create_index("ix_lost_item_reports_status", "lost_item_reports", ["status"], unique=False)

    op.create_table(
        "finder_sessions",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column(
            "sticker_id",
            sa.String(length=36),
            sa.ForeignKey("qr_stickers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("public_token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finder_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_finder_sessions_sticker_id", "finder_sessions", ["sticker_id"], unique=False
    )
    op.create_index(
        "ix_finder_sessions_public_token_hash",
        "finder_sessions",
        ["public_token_hash"],
        unique=True,
    )
    op.create_index(
        "ix_finder_sessions_expires_at", "finder_sessions", ["expires_at"], unique=False
    )

    op.create_table(
        "anonymous_messages",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column(
            "finder_session_id",
            sa.String(length=36),
            sa.ForeignKey("finder_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sender_role", sa.String(length=16), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_anonymous_messages_finder_session_id",
        "anonymous_messages",
        ["finder_session_id"],
        unique=False,
    )
    op.create_index(
        "ix_anonymous_messages_sender_role", "anonymous_messages", ["sender_role"], unique=False
    )
    op.create_index(
        "ix_anonymous_messages_created_at", "anonymous_messages", ["created_at"], unique=False
    )


def downgrade() -> None:
    """Drop recovery tables in reverse dependency order."""
    op.drop_index("ix_anonymous_messages_created_at", table_name="anonymous_messages")
    op.drop_index("ix_anonymous_messages_sender_role", table_name="anonymous_messages")
    op.drop_index("ix_anonymous_messages_finder_session_id", table_name="anonymous_messages")
    op.drop_table("anonymous_messages")

    op.drop_index("ix_finder_sessions_expires_at", table_name="finder_sessions")
    op.drop_index("ix_finder_sessions_public_token_hash", table_name="finder_sessions")
    op.drop_index("ix_finder_sessions_sticker_id", table_name="finder_sessions")
    op.drop_table("finder_sessions")

    op.drop_index("ix_lost_item_reports_status", table_name="lost_item_reports")
    op.drop_index("ix_lost_item_reports_owner_user_id", table_name="lost_item_reports")
    op.drop_index("ix_lost_item_reports_item_id", table_name="lost_item_reports")
    op.drop_table("lost_item_reports")

    op.drop_index("ix_qr_stickers_status", table_name="qr_stickers")
    op.drop_index("ix_qr_stickers_item_id", table_name="qr_stickers")
    op.drop_index("ix_qr_stickers_owner_user_id", table_name="qr_stickers")
    op.drop_index("ix_qr_stickers_code", table_name="qr_stickers")
    op.drop_table("qr_stickers")

    op.drop_index("ix_items_is_lost", table_name="items")
    op.drop_index("ix_items_owner_user_id", table_name="items")
    op.drop_table("items")
