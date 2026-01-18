"""Add schedule table

Revision ID: add_schedule_table
Revises: 17314130252c
Create Date: 2026-01-19 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_schedule_table"
down_revision: str | None = "17314130252c"  # Latest revision from heads output
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create schedule table."""
    op.create_table(
        "schedule",
        sa.Column("flow_id", sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
        sa.Column("frequency", sa.String(), nullable=False),
        sa.Column("schedule_time", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("day_of_week", sa.Integer(), nullable=True),
        sa.Column("day_of_month", sa.Integer(), nullable=True),
        sa.Column("cron_expression", sa.String(), nullable=True),
        sa.Column("last_run_at", sa.DateTime(), nullable=True),
        sa.Column("next_run_at", sa.DateTime(), nullable=True),
        sa.Column("last_run_status", sa.String(), nullable=True),
        sa.Column("last_run_error", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.types.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["flow_id"], ["flow.id"], name="fk_schedule_flow_id"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name="fk_schedule_user_id"),
        sa.PrimaryKeyConstraint("id", name="pk_schedule"),
        sa.UniqueConstraint("id", name="uq_schedule_id"),
    )
    
    with op.batch_alter_table("schedule", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_schedule_flow_id"), ["flow_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_schedule_user_id"), ["user_id"], unique=False)


def downgrade() -> None:
    """Drop schedule table."""
    with op.batch_alter_table("schedule", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_schedule_user_id"))
        batch_op.drop_index(batch_op.f("ix_schedule_flow_id"))
    
    op.drop_table("schedule")
