"""Item image to BLOB

Revision ID: c0234ecb1899
Revises: ce592f954645
Create Date: 2022-03-12 22:00:15.507574

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0234ecb1899'
down_revision = 'ce592f954645'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('menu_items', sa.Column('item_image', sa.LargeBinary(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('menu_items', 'item_image')
    # ### end Alembic commands ###
