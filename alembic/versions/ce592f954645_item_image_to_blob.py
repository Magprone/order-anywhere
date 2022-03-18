"""Item image to BLOB

Revision ID: ce592f954645
Revises: 1c06259f16bd
Create Date: 2022-03-12 21:54:21.017789

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce592f954645'
down_revision = '1c06259f16bd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('menu_items', 'item_image')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###