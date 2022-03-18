"""name to title

Revision ID: 515c7c610eef
Revises: a6f18077351d
Create Date: 2022-03-12 23:43:11.731042

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '515c7c610eef'
down_revision = 'a6f18077351d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('restaurants', sa.Column('profile_image', sa.LargeBinary(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('restaurants', 'profile_image')
    # ### end Alembic commands ###