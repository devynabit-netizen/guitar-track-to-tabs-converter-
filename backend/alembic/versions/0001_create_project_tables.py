"""create project and tab version tables

Revision ID: 0001_create_project_tables
Revises:
Create Date: 2026-03-01 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_create_project_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("audio_path", sa.String(length=512), nullable=False),
        sa.Column("tuning", sa.JSON(), nullable=False),
        sa.Column("tempo_bpm", sa.Float(), nullable=False, server_default="120.0"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="queued"),
        sa.Column("progress", sa.Float(), nullable=False, server_default="0.2"),
        sa.Column("current_phase", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("error_message", sa.String(length=1024), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "tab_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("notes_raw", sa.JSON(), nullable=False),
        sa.Column("notes_mapped", sa.JSON(), nullable=False),
        sa.Column("tab_ascii", sa.String(), nullable=False, server_default=""),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("tab_versions")
    op.drop_table("projects")
