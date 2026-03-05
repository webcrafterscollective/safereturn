"""Add admin sticker packs, QR claim metadata, and user admin role."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260305_03"
down_revision: str | None = "20260305_02"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Create admin/pack tables and extend users/stickers for claim lifecycle."""
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_users_is_admin", "users", ["is_admin"], unique=False)

    op.create_table(
        "sticker_packs",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("pack_code", sa.String(length=64), nullable=False),
        sa.Column("total_stickers", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column(
            "created_by_user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "assigned_user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_sticker_packs_pack_code", "sticker_packs", ["pack_code"], unique=True)
    op.create_index("ix_sticker_packs_status", "sticker_packs", ["status"], unique=False)
    op.create_index(
        "ix_sticker_packs_created_by_user_id", "sticker_packs", ["created_by_user_id"], unique=False
    )
    op.create_index(
        "ix_sticker_packs_assigned_user_id", "sticker_packs", ["assigned_user_id"], unique=False
    )

    op.add_column(
        "qr_stickers",
        sa.Column(
            "pack_id",
            sa.String(length=36),
            sa.ForeignKey("sticker_packs.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "qr_stickers",
        sa.Column("assigned_once", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "qr_stickers",
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "qr_stickers",
        sa.Column("invalidated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column("qr_stickers", sa.Column("replaced_by_code", sa.String(length=64), nullable=True))
    op.alter_column(
        "qr_stickers",
        "owner_user_id",
        existing_type=sa.String(length=36),
        nullable=True,
    )
    op.create_index("ix_qr_stickers_pack_id", "qr_stickers", ["pack_id"], unique=False)


def downgrade() -> None:
    """Drop admin/pack schema additions."""
    op.drop_index("ix_qr_stickers_pack_id", table_name="qr_stickers")
    op.alter_column(
        "qr_stickers",
        "owner_user_id",
        existing_type=sa.String(length=36),
        nullable=False,
    )
    op.drop_column("qr_stickers", "replaced_by_code")
    op.drop_column("qr_stickers", "invalidated_at")
    op.drop_column("qr_stickers", "claimed_at")
    op.drop_column("qr_stickers", "assigned_once")
    op.drop_column("qr_stickers", "pack_id")

    op.drop_index("ix_sticker_packs_assigned_user_id", table_name="sticker_packs")
    op.drop_index("ix_sticker_packs_created_by_user_id", table_name="sticker_packs")
    op.drop_index("ix_sticker_packs_status", table_name="sticker_packs")
    op.drop_index("ix_sticker_packs_pack_code", table_name="sticker_packs")
    op.drop_table("sticker_packs")

    op.drop_index("ix_users_is_admin", table_name="users")
    op.drop_column("users", "is_admin")
