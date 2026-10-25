"""add knowledge indexing status

Revision ID: eed5cbc73dc0
Revises: 2e1d01856e7d
Create Date: 2026-10-25 19:13:40.779288

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "eed5cbc73dc0"
down_revision: Union[str, Sequence[str], None] = "2e1d01856e7d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "knowledge_articles",
        sa.Column(
            "indexing_status",
            sa.String(length=20),
            server_default="queued",
            nullable=False,
        ),
    )

    op.add_column(
        "knowledge_articles",
        sa.Column(
            "indexing_error",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "knowledge_articles",
        sa.Column(
            "indexed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE knowledge_articles AS article
        SET
            indexing_status = 'ready',
            indexed_at = NOW()
        WHERE EXISTS (
            SELECT 1
            FROM knowledge_chunks AS chunk
            WHERE
                chunk.article_id = article.id
                AND chunk.embedding IS NOT NULL
        )
        """
    )


def downgrade() -> None:
    op.drop_column(
        "knowledge_articles",
        "indexed_at",
    )

    op.drop_column(
        "knowledge_articles",
        "indexing_error",
    )

    op.drop_column(
        "knowledge_articles",
        "indexing_status",
    )
