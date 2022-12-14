"""First

Revision ID: bb29b5c5ecb1
Revises: 
Create Date: 2022-07-25 10:45:19.222347

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb29b5c5ecb1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('per_hour_cost', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=1000), nullable=False),
    sa.Column('hardness', sa.Integer(), nullable=False),
    sa.Column('time_create', sa.DateTime(), nullable=True),
    sa.Column('executor', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['executor'], ['users.id'], name='fk_tasks_users_id_executor'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('taskreports',
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.Column('report_id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(length=1000), nullable=False),
    sa.Column('time_create', sa.DateTime(), nullable=True),
    sa.Column('automatically', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name='fk_taskreports_tasks_id_task_id'),
    sa.PrimaryKeyConstraint('report_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('taskreports')
    op.drop_table('tasks')
    op.drop_table('users')
    # ### end Alembic commands ###
