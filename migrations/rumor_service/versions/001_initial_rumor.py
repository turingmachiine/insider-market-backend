"""initial rumor schema

Revision ID: 001_initial_rumor
Revises:
Create Date: 2026-05-03
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_rumor"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


source_type_enum = postgresql.ENUM(
    "telegram",
    "media",
    "api",
    "manual",
    name="source_type",
    create_type=False,
)
rumor_status_enum = postgresql.ENUM(
    "new",
    "candidate",
    "approved",
    "rejected",
    "archived",
    name="rumor_status",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type
                WHERE typname = 'source_type'
            ) THEN
                CREATE TYPE source_type AS ENUM (
                    'telegram',
                    'media',
                    'api',
                    'manual'
                );
            END IF;
        END
        $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type
                WHERE typname = 'rumor_status'
            ) THEN
                CREATE TYPE rumor_status AS ENUM (
                    'new',
                    'candidate',
                    'approved',
                    'rejected',
                    'archived'
                );
            END IF;
        END
        $$;
        """
    )

    op.create_table(
        "sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source_type", source_type_enum, nullable=False),
        sa.Column("handle", sa.String(length=255), nullable=True),
        sa.Column("url", sa.String(length=500), nullable=True),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_sources_name", "sources", ["name"], unique=True)
    op.create_index("ix_sources_type", "sources", ["source_type"])
    op.create_index("ix_sources_active", "sources", ["is_active"])

    op.create_table(
        "raw_publications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("url", sa.String(length=500), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "collected_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_raw_publications_external",
        "raw_publications",
        ["source_id", "external_id"],
        unique=True,
    )
    op.create_index(
        "ix_raw_publications_published_at",
        "raw_publications",
        ["published_at"],
    )
    op.create_index(
        "ix_raw_publications_source",
        "raw_publications",
        ["source_id"],
    )

    op.create_table(
        "rumors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("raw_publication_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("normalized_text", sa.Text(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("status", rumor_status_enum, nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String(length=100)), nullable=False),
        sa.Column("event_candidate_payload", postgresql.JSONB(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["raw_publication_id"],
            ["raw_publications.id"],
            ondelete="SET NULL",
        ),
    )
    op.create_index("ix_rumors_confidence", "rumors", ["confidence_score"])
    op.create_index("ix_rumors_created_at", "rumors", ["created_at"])
    op.create_index("ix_rumors_publication", "rumors", ["raw_publication_id"])
    op.create_index("ix_rumors_source", "rumors", ["source_id"])
    op.create_index("ix_rumors_status", "rumors", ["status"])


def downgrade() -> None:
    op.drop_index("ix_rumors_status", table_name="rumors")
    op.drop_index("ix_rumors_source", table_name="rumors")
    op.drop_index("ix_rumors_publication", table_name="rumors")
    op.drop_index("ix_rumors_created_at", table_name="rumors")
    op.drop_index("ix_rumors_confidence", table_name="rumors")
    op.drop_table("rumors")
    op.drop_index("ix_raw_publications_source", table_name="raw_publications")
    op.drop_index("ix_raw_publications_published_at", table_name="raw_publications")
    op.drop_index("ix_raw_publications_external", table_name="raw_publications")
    op.drop_table("raw_publications")
    op.drop_index("ix_sources_active", table_name="sources")
    op.drop_index("ix_sources_type", table_name="sources")
    op.drop_index("ix_sources_name", table_name="sources")
    op.drop_table("sources")
    rumor_status_enum.drop(op.get_bind(), checkfirst=True)
    source_type_enum.drop(op.get_bind(), checkfirst=True)
