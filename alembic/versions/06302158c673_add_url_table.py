"""add url table

Revision ID: 06302158c673
Revises: d6f2bb97ceff
Create Date: 2025-03-01 17:16:00.000000

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "06302158c673"
down_revision: Union[str, None] = "d6f2bb97ceff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This migration is skipped as it's trying to create a table that already exists
    # with a different schema. We're using the schema from the previous migration.
    pass


def downgrade() -> None:
    # This downgrade is skipped to avoid dropping the table that should remain
    pass
