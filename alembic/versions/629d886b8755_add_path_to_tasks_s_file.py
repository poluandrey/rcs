"""add path to tasks\'s file

Revision ID: 629d886b8755
Revises: 0a447c0cbd26
Create Date: 2024-04-05 11:50:05.494788

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '629d886b8755'
down_revision: Union[str, None] = '0a447c0cbd26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('file', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('task', 'file')
    # ### end Alembic commands ###