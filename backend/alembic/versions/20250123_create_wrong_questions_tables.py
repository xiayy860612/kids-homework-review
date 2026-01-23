"""create_wrong_questions_tables

Revision ID: 20250123001
Revises: 726ef114da2e
Create Date: 2025-01-23

"""
from typing import Sequence, Union
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250123001'
down_revision: Union[str, Sequence[str], None] = '726ef114da2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create subjects table
    op.create_table(
        'subjects',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('is_preset', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create wrong_questions table
    op.create_table(
        'wrong_questions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=False),
        sa.Column('image_base64', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_wrong_questions_user_id_users')),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], name=op.f('fk_wrong_questions_subject_id_subjects'))
    )
    op.create_index('idx_wrong_questions_user_id', 'wrong_questions', ['user_id'])

    # Create wrong_question_tags association table
    op.create_table(
        'wrong_question_tags',
        sa.Column('wrong_question_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('wrong_question_id', 'tag_id'),
        sa.ForeignKeyConstraint(['wrong_question_id'], ['wrong_questions.id'], ondelete='CASCADE', name=op.f('fk_wrong_question_tags_wrong_question_id_wrong_questions')),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE', name=op.f('fk_wrong_question_tags_tag_id_tags'))
    )

    # Seed preset subjects
    now = datetime.now(timezone.utc)
    op.bulk_insert(
        sa.table(
            'subjects',
            sa.column('id', sa.Integer),
            sa.column('name', sa.String),
            sa.column('description', sa.String),
            sa.column('is_active', sa.Boolean),
        ),
        [
            {'id': 1, 'name': '语文', 'description': '语文科目', 'is_active': True},
            {'id': 2, 'name': '数学', 'description': '数学科目', 'is_active': True},
            {'id': 3, 'name': '英语', 'description': '英语科目', 'is_active': True},
            {'id': 4, 'name': '物理', 'description': '物理科目', 'is_active': True},
            {'id': 5, 'name': '化学', 'description': '化学科目', 'is_active': True},
            {'id': 6, 'name': '生物', 'description': '生物科目', 'is_active': True},
            {'id': 7, 'name': '历史', 'description': '历史科目', 'is_active': True},
            {'id': 8, 'name': '地理', 'description': '地理科目', 'is_active': True},
            {'id': 9, 'name': '政治', 'description': '政治科目', 'is_active': True},
        ]
    )

    # Seed preset tags
    op.bulk_insert(
        sa.table(
            'tags',
            sa.column('id', sa.Integer),
            sa.column('name', sa.String),
            sa.column('is_preset', sa.Boolean),
        ),
        [
            {'id': 1, 'name': '计算错误', 'is_preset': True},
            {'id': 2, 'name': '概念不清', 'is_preset': True},
            {'id': 3, 'name': '粗心大意', 'is_preset': True},
            {'id': 4, 'name': '审题错误', 'is_preset': True},
            {'id': 5, 'name': '思路错误', 'is_preset': True},
        ]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('wrong_question_tags')
    op.drop_index('idx_wrong_questions_user_id', table_name='wrong_questions')
    op.drop_table('wrong_questions')
    op.drop_table('tags')
    op.drop_table('subjects')
