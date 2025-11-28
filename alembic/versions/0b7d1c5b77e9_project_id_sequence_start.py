"""Set project ID sequence to start at 10000.

Revision ID: 0b7d1c5b77e9
Revises: e2a42e9d9be8
Create Date: 2025-11-27 18:45:00.000000
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0b7d1c5b77e9"
down_revision: Union[str, Sequence[str], None] = "e2a42e9d9be8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ensure new project IDs start at 10000."""
    op.execute("ALTER SEQUENCE projects_id_seq RESTART WITH 10000;")


def downgrade() -> None:
    """Revert project ID sequence to default starting value."""
    op.execute("ALTER SEQUENCE projects_id_seq RESTART WITH 1;")
