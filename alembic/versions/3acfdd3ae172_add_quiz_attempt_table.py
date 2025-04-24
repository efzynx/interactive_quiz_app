"""Add quiz_attempt table

Revision ID: 3acfdd3ae172
Revises: 4b51bda4e654
Create Date: 2025-04-24 17:59:12.463454

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3acfdd3ae172'
down_revision: Union[str, None] = '4b51bda4e654'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
