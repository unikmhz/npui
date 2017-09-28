"""Initial revision

Revision ID: a026b610c23c
Revises: 
Create Date: 2017-09-25 16:02:05.833826

"""

# revision identifiers, used by Alembic.
revision = 'a026b610c23c'
down_revision = None
branch_labels = ('sessions',)
depends_on = 'b32a4bf96447'

from alembic import op
import sqlalchemy as sa
from sqlalchemy import FetchedValue
from netprofile.db import ddl as npd
from netprofile.db import fields as npf

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sessions_def',
    sa.Column('sessid', npf.UInt64(), npd.Comment('Session ID'), nullable=False, default=sa.Sequence('sessions_def_sessid_seq')),
    sa.Column('name', npf.ASCIIString(length=255), npd.Comment('Session name'), nullable=False),
    sa.Column('stationid', npf.UInt32(), npd.Comment('Station ID'), server_default=sa.text('1'), nullable=False),
    sa.Column('entityid', npf.UInt32(), npd.Comment('Access entity ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('ipaddrid', npf.UInt32(), npd.Comment('IPv4 address ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('ip6addrid', npf.UInt64(), npd.Comment('IPv6 address ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('destid', npf.UInt32(), npd.Comment('Accounting destination ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('nasid', npf.UInt32(), npd.Comment('Network access server ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('csid', npf.ASCIIString(length=255), npd.Comment('Calling station ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('called', npf.ASCIIString(length=255), npd.Comment('Called station ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('startts', sa.TIMESTAMP(), npd.Comment('Session start time'), nullable=True),
    sa.Column('updatets', sa.TIMESTAMP(), npd.Comment('Accounting update time'), nullable=True),
    sa.Column('ut_ingress', npf.Traffic(precision=16, scale=0), npd.Comment('Used ingress traffic'), server_default=sa.text('0'), nullable=False),
    sa.Column('ut_egress', npf.Traffic(precision=16, scale=0), npd.Comment('Used egress traffic'), server_default=sa.text('0'), nullable=False),
    sa.Column('pol_ingress', npf.ASCIIString(length=255), npd.Comment('Ingress traffic policy'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('pol_egress', npf.ASCIIString(length=255), npd.Comment('Egress traffic policy'), server_default=sa.text('NULL'), nullable=True),
    sa.ForeignKeyConstraint(['destid'], ['dest_def.destid'], name='sessions_def_fk_destid', onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['entityid'], ['entities_access.entityid'], name='sessions_def_fk_entityid', onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['ip6addrid'], ['ip6addr_def.ip6addrid'], name='sessions_def_fk_ip6addrid', onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['ipaddrid'], ['ipaddr_def.ipaddrid'], name='sessions_def_fk_ipaddrid', onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['nasid'], ['nas_def.nasid'], name='sessions_def_fk_nasid', onupdate='CASCADE', ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('sessid', name=op.f('sessions_def_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('sessions_def', 'Access sessions')
    op.create_trigger('netprofile_sessions', 'sessions_def', 'before', 'delete', 'a026b610c23c')
    op.create_trigger('netprofile_sessions', 'sessions_def', 'after', 'delete', 'a026b610c23c')
    op.create_index('sessions_def_i_destid', 'sessions_def', ['destid'], unique=False)
    op.create_index('sessions_def_i_entityid', 'sessions_def', ['entityid'], unique=False)
    op.create_index('sessions_def_i_ip6addrid', 'sessions_def', ['ip6addrid'], unique=False)
    op.create_index('sessions_def_i_ipaddrid', 'sessions_def', ['ipaddrid'], unique=False)
    op.create_index('sessions_def_i_nasid', 'sessions_def', ['nasid'], unique=False)
    op.create_index('sessions_def_i_updatets', 'sessions_def', ['updatets'], unique=False)
    op.create_index('sessions_def_u_session', 'sessions_def', ['stationid', 'name'], unique=True)
    op.create_table('sessions_history',
    sa.Column('sessid', npf.UInt64(), npd.Comment('Session ID'), nullable=False, default=sa.Sequence('sessions_history_sessid_seq')),
    sa.Column('name', npf.ASCIIString(length=255), npd.Comment('Session name'), nullable=False),
    sa.Column('stationid', npf.UInt32(), npd.Comment('Station ID'), nullable=False),
    sa.Column('entityid', npf.UInt32(), npd.Comment('Access entity ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('ipaddrid', npf.UInt32(), npd.Comment('IPv4 address ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('ip6addrid', npf.UInt64(), npd.Comment('IPv6 address ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('destid', npf.UInt32(), npd.Comment('Accounting destination ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('nasid', npf.UInt32(), npd.Comment('Network access server ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('csid', npf.ASCIIString(length=255), npd.Comment('Calling station ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('called', npf.ASCIIString(length=255), npd.Comment('Called station ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('startts', sa.TIMESTAMP(), npd.Comment('Session start time'), nullable=True),
    sa.Column('endts', sa.TIMESTAMP(), npd.Comment('Session end time'), nullable=True),
    sa.Column('ut_ingress', npf.Traffic(precision=16, scale=0), npd.Comment('Used ingress traffic'), server_default=sa.text('0'), nullable=False),
    sa.Column('ut_egress', npf.Traffic(precision=16, scale=0), npd.Comment('Used egress traffic'), server_default=sa.text('0'), nullable=False),
    sa.Column('pol_ingress', npf.ASCIIString(length=255), npd.Comment('Ingress traffic policy'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('pol_egress', npf.ASCIIString(length=255), npd.Comment('Egress traffic policy'), server_default=sa.text('NULL'), nullable=True),
    sa.ForeignKeyConstraint(['destid'], ['dest_def.destid'], name='sessions_history_fk_destid', onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['entityid'], ['entities_access.entityid'], name='sessions_history_fk_entityid', onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['ip6addrid'], ['ip6addr_def.ip6addrid'], name='sessions_history_fk_ip6addrid', onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['ipaddrid'], ['ipaddr_def.ipaddrid'], name='sessions_history_fk_ipaddrid', onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['nasid'], ['nas_def.nasid'], name='sessions_history_fk_nasid', onupdate='CASCADE', ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('sessid', name=op.f('sessions_history_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('sessions_history', 'Log of closed sessions')
    op.create_index('sessions_history_i_destid', 'sessions_history', ['destid'], unique=False)
    op.create_index('sessions_history_i_endts', 'sessions_history', ['endts'], unique=False)
    op.create_index('sessions_history_i_entityid', 'sessions_history', ['entityid'], unique=False)
    op.create_index('sessions_history_i_ip6addrid', 'sessions_history', ['ip6addrid'], unique=False)
    op.create_index('sessions_history_i_ipaddrid', 'sessions_history', ['ipaddrid'], unique=False)
    op.create_index('sessions_history_i_nasid', 'sessions_history', ['nasid'], unique=False)
    op.create_function('sessions', npd.SQLFunction('acct_close_session', args=[npd.SQLFunctionArgument('sid', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('stid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('ts', sa.DateTime(), 'IN')], returns=None, comment='Close specified session', reads_sql=True, writes_sql=True, is_procedure=True, label=None), 'a026b610c23c')
    op.create_function('sessions', npd.SQLFunction('acct_alloc_ip', args=[npd.SQLFunctionArgument('nid', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('ename', sa.Unicode(length=255), 'IN')], returns=None, comment='Allocate session IPv4 address', reads_sql=True, writes_sql=True, is_procedure=True, label=None), 'a026b610c23c')
    op.create_function('sessions', npd.SQLFunction('acct_open_session', args=[npd.SQLFunctionArgument('sid', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('stid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('name', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('fip', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('fip6', npf.UInt64(), 'IN'), npd.SQLFunctionArgument('xnasid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('ts', sa.DateTime(), 'IN'), npd.SQLFunctionArgument('csid', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('called', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('pol_in', npf.ASCIIString(length=255), 'IN'), npd.SQLFunctionArgument('pol_eg', npf.ASCIIString(length=255), 'IN')], returns=None, comment='Open new session', reads_sql=True, writes_sql=True, is_procedure=True, label='aosfunc'), 'a026b610c23c')
    op.create_function('sessions', npd.SQLFunction('acct_alloc_ipv6', args=[npd.SQLFunctionArgument('nid', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('ename', sa.Unicode(length=255), 'IN')], returns=None, comment='Allocate session IPv6 address', reads_sql=True, writes_sql=True, is_procedure=True, label=None), 'a026b610c23c')
    op.create_function('sessions', npd.SQLFunction('acct_authz_session', args=[npd.SQLFunctionArgument('name', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('r_porttype', npf.Int32(), 'IN'), npd.SQLFunctionArgument('r_servicetype', npf.Int32(), 'IN'), npd.SQLFunctionArgument('r_frproto', npf.Int32(), 'IN'), npd.SQLFunctionArgument('r_tuntype', npf.Int32(), 'IN'), npd.SQLFunctionArgument('r_tunmedium', npf.Int32(), 'IN')], returns=None, comment='Get authorized account info with session estabilishment', reads_sql=True, writes_sql=True, is_procedure=True, label='authzfunc'), 'a026b610c23c')
    op.create_function('sessions', npd.SQLFunction('acct_add_session', args=[npd.SQLFunctionArgument('sid', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('stid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('username', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('tin', npf.Traffic(precision=16, scale=0), 'IN'), npd.SQLFunctionArgument('teg', npf.Traffic(precision=16, scale=0), 'IN'), npd.SQLFunctionArgument('ts', sa.DateTime(), 'IN')], returns=None, comment='Add accounting information for opened session', reads_sql=True, writes_sql=True, is_procedure=True, label='aasfunc'), 'a026b610c23c')
    op.create_event('sessions', npd.SQLEvent('ev_sessions_clear_stale', sched_unit='minute', sched_interval=2, starts=None, preserve=True, enabled=True, comment='Clear open but stale sessions'), 'a026b610c23c')
    op.create_event('sessions', npd.SQLEvent('ev_ipaddr_clear_stale', sched_unit='minute', sched_interval=91, starts=None, preserve=True, enabled=False, comment='Clear stale in-use IP addresses'), 'a026b610c23c')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_event('sessions', npd.SQLEvent('ev_ipaddr_clear_stale', sched_unit='minute', sched_interval=91, starts=None, preserve=True, enabled=False, comment='Clear stale in-use IP addresses'), 'a026b610c23c')
    op.drop_event('sessions', npd.SQLEvent('ev_sessions_clear_stale', sched_unit='minute', sched_interval=2, starts=None, preserve=True, enabled=True, comment='Clear open but stale sessions'), 'a026b610c23c')
    op.drop_function('sessions', npd.SQLFunction('acct_add_session', args=[npd.SQLFunctionArgument('sid', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('stid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('username', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('tin', npf.Traffic(precision=16, scale=0), 'IN'), npd.SQLFunctionArgument('teg', npf.Traffic(precision=16, scale=0), 'IN'), npd.SQLFunctionArgument('ts', sa.DateTime(), 'IN')], returns=None, comment='Add accounting information for opened session', reads_sql=True, writes_sql=True, is_procedure=True, label='aasfunc'), 'a026b610c23c')
    op.drop_function('sessions', npd.SQLFunction('acct_authz_session', args=[npd.SQLFunctionArgument('name', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('r_porttype', npf.Int32(), 'IN'), npd.SQLFunctionArgument('r_servicetype', npf.Int32(), 'IN'), npd.SQLFunctionArgument('r_frproto', npf.Int32(), 'IN'), npd.SQLFunctionArgument('r_tuntype', npf.Int32(), 'IN'), npd.SQLFunctionArgument('r_tunmedium', npf.Int32(), 'IN')], returns=None, comment='Get authorized account info with session estabilishment', reads_sql=True, writes_sql=True, is_procedure=True, label='authzfunc'), 'a026b610c23c')
    op.drop_function('sessions', npd.SQLFunction('acct_alloc_ipv6', args=[npd.SQLFunctionArgument('nid', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('ename', sa.Unicode(length=255), 'IN')], returns=None, comment='Allocate session IPv6 address', reads_sql=True, writes_sql=True, is_procedure=True, label=None), 'a026b610c23c')
    op.drop_function('sessions', npd.SQLFunction('acct_open_session', args=[npd.SQLFunctionArgument('sid', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('stid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('name', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('fip', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('fip6', npf.UInt64(), 'IN'), npd.SQLFunctionArgument('xnasid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('ts', sa.DateTime(), 'IN'), npd.SQLFunctionArgument('csid', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('called', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('pol_in', npf.ASCIIString(length=255), 'IN'), npd.SQLFunctionArgument('pol_eg', npf.ASCIIString(length=255), 'IN')], returns=None, comment='Open new session', reads_sql=True, writes_sql=True, is_procedure=True, label='aosfunc'), 'a026b610c23c')
    op.drop_function('sessions', npd.SQLFunction('acct_alloc_ip', args=[npd.SQLFunctionArgument('nid', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('ename', sa.Unicode(length=255), 'IN')], returns=None, comment='Allocate session IPv4 address', reads_sql=True, writes_sql=True, is_procedure=True, label=None), 'a026b610c23c')
    op.drop_function('sessions', npd.SQLFunction('acct_close_session', args=[npd.SQLFunctionArgument('sid', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('stid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('ts', sa.DateTime(), 'IN')], returns=None, comment='Close specified session', reads_sql=True, writes_sql=True, is_procedure=True, label=None), 'a026b610c23c')
    op.drop_index('sessions_history_i_nasid', table_name='sessions_history')
    op.drop_index('sessions_history_i_ipaddrid', table_name='sessions_history')
    op.drop_index('sessions_history_i_ip6addrid', table_name='sessions_history')
    op.drop_index('sessions_history_i_entityid', table_name='sessions_history')
    op.drop_index('sessions_history_i_endts', table_name='sessions_history')
    op.drop_index('sessions_history_i_destid', table_name='sessions_history')
    op.drop_table('sessions_history')
    op.drop_index('sessions_def_u_session', table_name='sessions_def')
    op.drop_index('sessions_def_i_updatets', table_name='sessions_def')
    op.drop_index('sessions_def_i_nasid', table_name='sessions_def')
    op.drop_index('sessions_def_i_ipaddrid', table_name='sessions_def')
    op.drop_index('sessions_def_i_ip6addrid', table_name='sessions_def')
    op.drop_index('sessions_def_i_entityid', table_name='sessions_def')
    op.drop_index('sessions_def_i_destid', table_name='sessions_def')
    op.drop_table('sessions_def')
    # ### end Alembic commands ###
