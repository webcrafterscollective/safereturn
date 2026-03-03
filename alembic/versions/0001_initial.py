"""create initial tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-03-04
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("email_encrypted", sa.String(length=512), nullable=True),
        sa.Column("phone_encrypted", sa.String(length=512), nullable=True),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("phone_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("refresh_token_hash", sa.String(length=128), nullable=True),
    )
    op.create_table(
        "tags",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("public_token", sa.String(length=255), nullable=False, unique=True),
        sa.Column("claim_code", sa.String(length=64), nullable=False, unique=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("owner_id", sa.String(length=64), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "items",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("owner_id", sa.String(length=64), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "tag_id", sa.String(length=64), sa.ForeignKey("tags.id"), nullable=False, unique=True
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "lost_reports",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column(
            "item_id", sa.String(length=64), sa.ForeignKey("items.id"), nullable=False, unique=True
        ),
        sa.Column("is_lost", sa.Boolean(), nullable=False),
        sa.Column("lost_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("found_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "finder_sessions",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("public_token", sa.String(length=255), nullable=False),
        sa.Column("session_token", sa.String(length=255), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "conversations",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("item_id", sa.String(length=64), sa.ForeignKey("items.id"), nullable=False),
        sa.Column("owner_id", sa.String(length=64), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("finder_anon_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "messages",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.String(length=64),
            sa.ForeignKey("conversations.id"),
            nullable=False,
        ),
        sa.Column("sender_type", sa.String(length=16), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "delivery_requests",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.String(length=64),
            sa.ForeignKey("conversations.id"),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("provider_ref", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("actor_type", sa.String(length=32), nullable=False),
        sa.Column("actor_id", sa.String(length=64), nullable=True),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("delivery_requests")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("finder_sessions")
    op.drop_table("lost_reports")
    op.drop_table("items")
    op.drop_table("tags")
    op.drop_table("users")
