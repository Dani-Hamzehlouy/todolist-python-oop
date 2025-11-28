"""Adjust project/task ID sequences.

Revision ID: 5f3d9442a6b0
Revises: 0b7d1c5b77e9
Create Date: 2025-11-27 19:22:00.000000
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5f3d9442a6b0"
down_revision: Union[str, Sequence[str], None] = "0b7d1c5b77e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Start project IDs at 1 and task IDs at 100000."""
    op.execute("ALTER SEQUENCE projects_id_seq RESTART WITH 1;")
    op.execute("ALTER SEQUENCE tasks_id_seq RESTART WITH 100000;")


def downgrade() -> None:
    """Restore previous sequence behavior (projects at 10000, tasks at 1)."""
    op.execute("ALTER SEQUENCE projects_id_seq RESTART WITH 10000;")
    op.execute("ALTER SEQUENCE tasks_id_seq RESTART WITH 1;")
