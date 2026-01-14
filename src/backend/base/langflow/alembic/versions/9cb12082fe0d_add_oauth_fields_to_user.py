"""add_oauth_fields_to_user

Revision ID: 9cb12082fe0d
Revises: 182e5471b900
Create Date: 2026-01-14 17:38:19.142518

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.engine.reflection import Inspector
from langflow.utils import migration


# revision identifiers, used by Alembic.
revision: str = '9cb12082fe0d'
down_revision: Union[str, None] = '182e5471b900'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    table_name = "user"
    
    # Check if columns already exist
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    
    # Add oauth_provider column
    if "oauth_provider" not in columns:
        op.add_column(
            table_name,
            sa.Column("oauth_provider", sa.String(), nullable=True),
        )
    
    # Add oauth_id column with index
    if "oauth_id" not in columns:
        op.add_column(
            table_name,
            sa.Column("oauth_id", sa.String(), nullable=True),
        )
        op.create_index(
            "ix_user_oauth_id",
            table_name,
            ["oauth_id"],
            unique=False,
        )
    
    # Add wallet_address column with index
    if "wallet_address" not in columns:
        op.add_column(
            table_name,
            sa.Column("wallet_address", sa.String(), nullable=True),
        )
        op.create_index(
            "ix_user_wallet_address",
            table_name,
            ["wallet_address"],
            unique=False,
        )


def downgrade() -> None:
    conn = op.get_bind()
    table_name = "user"
    
    # Drop indexes first
    try:
        op.drop_index("ix_user_wallet_address", table_name=table_name)
    except Exception:
        pass
    
    try:
        op.drop_index("ix_user_oauth_id", table_name=table_name)
    except Exception:
        pass
    
    # Drop columns
    try:
        op.drop_column(table_name, "wallet_address")
    except Exception:
        pass
    
    try:
        op.drop_column(table_name, "oauth_id")
    except Exception:
        pass
    
    try:
        op.drop_column(table_name, "oauth_provider")
    except Exception:
        pass
