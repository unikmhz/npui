"""Initial revision

Revision ID: 7ec1022dcbee
Revises: 
Create Date: 2017-09-25 14:10:36.676182

"""

# revision identifiers, used by Alembic.
revision = '7ec1022dcbee'
down_revision = None
branch_labels = ('dialup',)
depends_on = '033d52604eac'

from alembic import op
import sqlalchemy as sa
from sqlalchemy import FetchedValue
from netprofile.db import ddl as npd
from netprofile.db import fields as npf

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ippool_def',
    sa.Column('poolid', npf.UInt32(), npd.Comment('IP address pool ID'), nullable=False, default=sa.Sequence('ippool_def_poolid_seq')),
    sa.Column('name', sa.Unicode(length=255), npd.Comment('IP address pool name'), nullable=False),
    sa.Column('ip6prefix', npf.IPv6Address(length=16), npd.Comment('IPv6 prefix'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('ip6plen', npf.UInt8(), npd.Comment('IPv6 prefix length'), nullable=False),
    sa.Column('descr', sa.UnicodeText(), npd.Comment('IP address pool description'), server_default=sa.text('NULL'), nullable=True),
    sa.PrimaryKeyConstraint('poolid', name=op.f('ippool_def_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('ippool_def', 'IP address pools')
    op.create_index('ippool_def_u_name', 'ippool_def', ['name'], unique=True)
    op.create_table('nas_def',
    sa.Column('nasid', npf.UInt32(), npd.Comment('Network access server ID'), nullable=False, default=sa.Sequence('nas_def_nasid_seq')),
    sa.Column('idstr', npf.ASCIIString(length=255), npd.Comment('Network access server identification string'), nullable=False),
    sa.Column('descr', sa.UnicodeText(), npd.Comment('Network access server description'), server_default=sa.text('NULL'), nullable=True),
    sa.PrimaryKeyConstraint('nasid', name=op.f('nas_def_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('nas_def', 'Network access servers')
    op.create_index('nas_def_i_idstr', 'nas_def', ['idstr'], unique=False)
    op.create_table('nas_pools',
    sa.Column('npid', npf.UInt32(), npd.Comment('NAS IP pool ID'), nullable=False, default=sa.Sequence('nas_pools_npid_seq')),
    sa.Column('nasid', npf.UInt32(), npd.Comment('Network access server ID'), nullable=False),
    sa.Column('poolid', npf.UInt32(), npd.Comment('IP address pool ID'), nullable=False),
    sa.ForeignKeyConstraint(['nasid'], ['nas_def.nasid'], name='nas_pools_fk_nasid', onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['poolid'], ['ippool_def.poolid'], name='nas_pools_fk_poolid', onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('npid', name=op.f('nas_pools_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('nas_pools', 'NAS IP pools')
    op.create_index('nas_pools_i_poolid', 'nas_pools', ['poolid'], unique=False)
    op.create_index('nas_pools_u_linkage', 'nas_pools', ['nasid', 'poolid'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('nas_pools_u_linkage', table_name='nas_pools')
    op.drop_index('nas_pools_i_poolid', table_name='nas_pools')
    op.drop_table('nas_pools')
    op.drop_index('nas_def_i_idstr', table_name='nas_def')
    op.drop_table('nas_def')
    op.drop_index('ippool_def_u_name', table_name='ippool_def')
    op.drop_table('ippool_def')
    # ### end Alembic commands ###

