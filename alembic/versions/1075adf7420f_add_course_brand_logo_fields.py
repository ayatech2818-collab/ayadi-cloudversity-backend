"""add course brand logo fields

Revision ID: 1075adf7420f
Revises: a0dab8499767
Create Date: 2026-09-29 09:17:14.485447

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1075adf7420f"
down_revision: Union[str, Sequence[str], None] = "a0dab8499767"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "course_brands",
        sa.Column("logo_url", sa.String(length=500), nullable=True),
    )

    op.add_column(
        "course_brands",
        sa.Column("logo_key", sa.String(length=500), nullable=True),
    )

    op.drop_column(
        "course_brands",
        "logo",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "course_brands",
        sa.Column(
            "logo",
            sa.String(length=500),
            nullable=True,
        ),
    )

    op.drop_column(
        "course_brands",
        "logo_key",
    )

    op.drop_column(
        "course_brands",
        "logo_url",
    )