"""add task runner settings

Revision ID: 1ebd65a0652d
Revises: f5b798981514
Create Date: 2026-10-09 22:01:56.560085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ebd65a0652d'
down_revision: Union[str, Sequence[str], None] = 'f5b798981514'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'tasks',
        sa.Column(
            'entrypoint',
            sa.String(length=100),
            nullable=True,
        ),
    )
    op.add_column(
        'tasks',
        sa.Column(
            'time_limit_ms',
            sa.Integer(),
            nullable=False,
            server_default='2000',
        ),
    )
    op.add_column(
        'tasks',
        sa.Column(
            'memory_limit_mb',
            sa.Integer(),
            nullable=False,
            server_default='128',
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('tasks', 'memory_limit_mb')
    op.drop_column('tasks', 'time_limit_ms')
    op.drop_column('tasks', 'entrypoint')