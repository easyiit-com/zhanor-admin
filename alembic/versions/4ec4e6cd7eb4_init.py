"""init

Revision ID: 4ec4e6cd7eb4
Revises: b055d7321a62
Create Date: 2024-09-10 11:34:47.085170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ec4e6cd7eb4'
down_revision: Union[str, None] = 'b055d7321a62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('attachment_file', sa.Column('is_image', sa.Enum('0', '1'), server_default='0', nullable=True, comment='Whether the file is an image'))
    op.add_column('attachment_file', sa.Column('thumbnail', sa.String(length=255), nullable=True, comment='Thumbnail Path'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('attachment_file', 'thumbnail')
    op.drop_column('attachment_file', 'is_image')
    # ### end Alembic commands ###
