"""empty message

Revision ID: f21d9c63d8df
Revises: ab0cc4d44cfc
Create Date: 2019-12-09 16:19:52.115392

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f21d9c63d8df'
down_revision = 'ab0cc4d44cfc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('likes', sa.Column('id', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('likes', 'id')
    # ### end Alembic commands ###
