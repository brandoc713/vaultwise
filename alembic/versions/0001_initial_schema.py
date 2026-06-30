"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-30
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # The MVP creates tables from SQLAlchemy metadata at startup. This revision
    # anchors Alembic so future schema changes can become migration-driven.
    pass


def downgrade() -> None:
    pass
