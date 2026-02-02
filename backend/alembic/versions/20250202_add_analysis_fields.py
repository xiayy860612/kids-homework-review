"""add_analysis_fields

Revision ID: 20250202001
Revises: 20250123001
Create Date: 2025-02-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250202001'
down_revision: Union[str, Sequence[str], None] = '20250123001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'wrong_questions',
        sa.Column('analysis_status', sa.String(length=20), nullable=False, server_default='pending')
    )
    op.add_column(
        'wrong_questions',
        sa.Column('analysis_result', sa.Text(), nullable=True)
    )
    op.add_column(
        'wrong_questions',
        sa.Column('analysis_error', sa.Text(), nullable=True)
    )
    op.add_column(
        'wrong_questions',
        sa.Column('analyzed_at', sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('wrong_questions', 'analyzed_at')
    op.drop_column('wrong_questions', 'analysis_error')
    op.drop_column('wrong_questions', 'analysis_result')
    op.drop_column('wrong_questions', 'analysis_status')
