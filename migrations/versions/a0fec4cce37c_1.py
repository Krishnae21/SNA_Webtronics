"""1

Revision ID: a0fec4cce37c
Revises: 
Create Date: 2023-07-26 21:51:25.819196

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a0fec4cce37c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "likes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reaction", sa.Integer(), nullable=False),
        sa.Column("reactkey", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reactkey"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("registered", sa.TIMESTAMP(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "post",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("posted_username", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("body", sa.String(), nullable=True),
        sa.Column("posted_at", sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(
            ["posted_username"],
            ["users.username"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("post")
    op.drop_table("users")
    op.drop_table("likes")
    # ### end Alembic commands ###
