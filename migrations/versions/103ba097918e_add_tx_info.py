"""add tx_info

Revision ID: 103ba097918e
Revises: 0341fcd398cf
Create Date: 2023-09-07 18:28:32.458790

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "103ba097918e"
down_revision: Union[str, None] = "0341fcd398cf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("transaction", sa.Column("task_id", sa.UUID(), nullable=True))
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    # generate random uuid for migration
    op.execute("UPDATE transaction SET task_id = uuid_generate_v4()")
    op.alter_column("transaction", "task_id", nullable=False)
    op.add_column("transaction", sa.Column("exc", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("transaction", "exc")
    op.drop_column("transaction", "task_id")
