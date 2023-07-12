"""8

Revision ID: 92ce188298a9
Revises: 5332a9795df3
Create Date: 2023-07-09 17:19:22.617735

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92ce188298a9'
down_revision = '5332a9795df3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('likes', sa.Column('reactkey', sa.String(), nullable=True))
    op.drop_constraint('likes_reactkey2_key', 'likes', type_='unique')
    op.create_unique_constraint(None, 'likes', ['reactkey'])
    op.drop_column('likes', 'reactkey2')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('likes', sa.Column('reactkey2', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'likes', type_='unique')
    op.create_unique_constraint('likes_reactkey2_key', 'likes', ['reactkey2'])
    op.drop_column('likes', 'reactkey')
    # ### end Alembic commands ###
