
"""add course fields to enquiries

Revision ID: 6c0fcc9e725c
Revises: 65574442fa2d
Create Date: 2026-10-30 11:57:28.413205
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6c0fcc9e725c"
down_revision: Union[str, Sequence[str], None] = "65574442fa2d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "enquiries",
        sa.Column("course_id", sa.UUID(), nullable=True),
    )

    op.add_column(
        "enquiries",
        sa.Column("course_title", sa.String(length=255), nullable=True),
    )

    op.create_index(
        "ix_enquiries_course_id",
        "enquiries",
        ["course_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_enquiries_course_id_courses",
        "enquiries",
        "courses",
        ["course_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_enquiries_course_id_courses",
        "enquiries",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_enquiries_course_id",
        table_name="enquiries",
    )

    op.drop_column("enquiries", "course_title")
    op.drop_column("enquiries", "course_id")
