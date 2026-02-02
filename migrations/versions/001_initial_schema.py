"""Initial database schema.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-01-31
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=True),
        sa.Column('is_premium', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Create chapter_progress table
    op.create_table(
        'chapter_progress',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chapter_id', sa.String(10), nullable=False),
        sa.Column('status', sa.String(20), default='not_started', nullable=False),
        sa.Column('time_spent_minutes', sa.Integer(), default=0, nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.UniqueConstraint('user_id', 'chapter_id', name='uq_user_chapter')
    )
    op.create_index('ix_chapter_progress_user_id', 'chapter_progress', ['user_id'])
    op.create_index('ix_chapter_progress_chapter_id', 'chapter_progress', ['chapter_id'])

    # Create quiz_attempts table
    op.create_table(
        'quiz_attempts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quiz_id', sa.String(20), nullable=False),
        sa.Column('chapter_id', sa.String(10), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.Column('answers', postgresql.JSONB(), nullable=False),
        sa.Column('attempted_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
    )
    op.create_index('ix_quiz_attempts_user_id', 'quiz_attempts', ['user_id'])
    op.create_index('ix_quiz_attempts_quiz_id', 'quiz_attempts', ['quiz_id'])
    op.create_index('ix_quiz_attempts_chapter_id', 'quiz_attempts', ['chapter_id'])

    # Create daily_activities table
    op.create_table(
        'daily_activities',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('activity_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('actions_count', sa.Integer(), default=1, nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.UniqueConstraint('user_id', 'activity_date', name='uq_user_date')
    )
    op.create_index('ix_daily_activities_user_id', 'daily_activities', ['user_id'])
    op.create_index('ix_daily_activities_activity_date', 'daily_activities', ['activity_date'])


def downgrade() -> None:
    op.drop_table('daily_activities')
    op.drop_table('quiz_attempts')
    op.drop_table('chapter_progress')
    op.drop_table('users')
