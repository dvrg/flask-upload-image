"""Delete url column

Revision ID: e8f7e6ff0b52
Revises: 834a30207096
Create Date: 2019-03-10 13:49:58.486276

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8f7e6ff0b52'
down_revision = '834a30207096'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(u'photo_model_photo_url_key', 'photo_model', type_='unique')
    op.drop_column('photo_model', 'photo_url')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('photo_model', sa.Column('photo_url', sa.VARCHAR(length=80), autoincrement=False, nullable=False))
    op.create_unique_constraint(u'photo_model_photo_url_key', 'photo_model', ['photo_url'])
    # ### end Alembic commands ###