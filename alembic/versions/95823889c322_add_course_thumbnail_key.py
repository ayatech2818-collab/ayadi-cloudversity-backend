"""add course thumbnail key

Revision ID: 95823889c322
Revises: 1075adf7420f
Create Date: 2026-09-29 13:29:59.867811

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "95823889c322"
down_revision: Union[str, Sequence[str], None] = "1075adf7420f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "courses",
        sa.Column(
            "thumbnail_key",
            sa.String(length=500),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "courses",
        "thumbnail_key",
    )