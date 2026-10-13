"""add ticket assignment

Revision ID: c8338381ca94
Revises: fd1bcec9c6e2
Create Date: 2026-10-13 22:49:15.288166

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c8338381ca94"
down_revision: Union[str, Sequence[str], None] = "fd1bcec9c6e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "tickets",
        sa.Column(
            "assignee_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        op.f("ix_tickets_assignee_id"),
        "tickets",
        ["assignee_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_tickets_assignee_id_users",
        "tickets",
        "users",
        ["assignee_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_tickets_assignee_id_users",
        "tickets",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_tickets_assignee_id"),
        table_name="tickets",
    )

    op.drop_column(
        "tickets",
        "assignee_id",
    )