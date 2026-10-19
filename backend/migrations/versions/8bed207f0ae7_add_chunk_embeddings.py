"""add chunk embeddings

Revision ID: 8bed207f0ae7
Revises: 254cbdbeb1d7
Create Date: 2026-10-16 21:54:48.242239

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "8bed207f0ae7"
down_revision: Union[str, Sequence[str], None] = "254cbdbeb1d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "knowledge_chunks",
        sa.Column(
            "embedding",
            Vector(384),
            nullable=True,
        ),
    )
    op.add_column(
        "knowledge_chunks",
        sa.Column(
            "embedding_model",
            sa.String(length=100),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "knowledge_chunks",
        "embedding_model",
    )
    op.drop_column(
        "knowledge_chunks",
        "embedding",
    )
