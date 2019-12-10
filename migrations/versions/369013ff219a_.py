"""empty message

Revision ID: 369013ff219a
Revises: f21d9c63d8df
Create Date: 2019-12-09 17:11:29.716847

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '369013ff219a'
down_revision = 'f21d9c63d8df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('likes')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('likes',
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('post_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], name='likes_post_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='likes_user_id_fkey'),
    sa.PrimaryKeyConstraint('user_id', 'post_id', name='likes_pkey')
    )
    # ### end Alembic commands ###
