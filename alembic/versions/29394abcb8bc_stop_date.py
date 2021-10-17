"""stop date

Revision ID: 29394abcb8bc
Revises: 648c0c21adf1
Create Date: 2021-10-18 00:09:00.035482

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29394abcb8bc'
down_revision = '648c0c21adf1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('consumers', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_consumers_paypal_email'), ['paypal_email'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('consumers', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_consumers_paypal_email'), type_='unique')

    # ### end Alembic commands ###