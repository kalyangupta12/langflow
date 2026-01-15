"""add_email_to_user

Revision ID: 17314130252c
Revises: 9cb12082fe0d
Create Date: 2026-01-14 20:37:54.097895

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.engine.reflection import Inspector
from langflow.utils import migration


# revision identifiers, used by Alembic.
revision: str = '17314130252c'
down_revision: Union[str, None] = '9cb12082fe0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    table_names = inspector.get_table_names()
    
    if "user" in table_names:
        columns = [col["name"] for col in inspector.get_columns("user")]
        
        # Add email column if it doesn't exist
        if "email" not in columns:
            with op.batch_alter_table("user", schema=None) as batch_op:
                batch_op.add_column(sa.Column("email", sa.String(), nullable=True))
                batch_op.create_index("ix_user_email", ["email"], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    table_names = inspector.get_table_names()
    
    if "user" in table_names:
        columns = [col["name"] for col in inspector.get_columns("user")]
        
        if "email" in columns:
            with op.batch_alter_table("user", schema=None) as batch_op:
                batch_op.drop_index("ix_user_email")
                batch_op.drop_column("email")
