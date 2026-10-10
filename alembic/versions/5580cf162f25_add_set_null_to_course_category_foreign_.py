"""add set null to course category foreign keys

Revision ID: 5580cf162f25
Revises: 9a3926baf1c3
Create Date: 2026-10-10 11:17:09.199158

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5580cf162f25'
down_revision: Union[str, Sequence[str], None] = '9a3926baf1c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "courses_category_id_fkey",
        "courses",
        type_="foreignkey",
    )
    op.drop_constraint(
        "courses_subcategory_id_fkey",
        "courses",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "courses_subcategory_id_fkey",
        "courses",
        "course_subcategories",
        ["subcategory_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "courses_category_id_fkey",
        "courses",
        "course_categories",
        ["category_id"],
        ["id"],
        ondelete="SET NULL",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_constraint(
        "courses_subcategory_id_fkey",
        "courses",
        type_="foreignkey",
    )
    op.drop_constraint(
        "courses_category_id_fkey",
        "courses",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "courses_subcategory_id_fkey",
        "courses",
        "course_subcategories",
        ["subcategory_id"],
        ["id"],
    )
    op.create_foreign_key(
        "courses_category_id_fkey",
        "courses",
        "course_categories",
        ["category_id"],
        ["id"],
    )
