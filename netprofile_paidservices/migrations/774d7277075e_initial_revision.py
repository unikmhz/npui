"""Initial revision

Revision ID: 774d7277075e
Revises: 
Create Date: 2017-09-25 16:11:47.558219

"""

# revision identifiers, used by Alembic.
revision = '774d7277075e'
down_revision = None
branch_labels = ('paidservices',)
depends_on = 'b32a4bf96447'

from alembic import op
import sqlalchemy as sa
from sqlalchemy import FetchedValue
from netprofile.db import ddl as npd
from netprofile.db import fields as npf

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('paid_types',
    sa.Column('paidid', npf.UInt32(), npd.Comment('Paid service ID'), nullable=False, default=sa.Sequence('paid_types_paidid_seq')),
    sa.Column('name', sa.Unicode(length=255), npd.Comment('Paid service name'), nullable=False),
    sa.Column('isum', npf.Money(precision=20, scale=8), npd.Comment('Initial payment sum'), server_default=sa.text('0'), nullable=False),
    sa.Column('qsum', npf.Money(precision=20, scale=8), npd.Comment('Quota sum'), server_default=sa.text('0'), nullable=False),
    sa.Column('qp_type', npf.DeclEnumType(name='PaidServiceQPType', values=['I', 'L', 'O']), npd.Comment('Quota period type'), server_default=sa.text("'I'"), nullable=False),
    sa.Column('qp_order', npf.UInt8(), npd.Comment('Pay order for linked services'), server_default=sa.text('0'), nullable=False),
    sa.Column('sp_amount', npf.UInt16(), npd.Comment('Number of skipped periods'), server_default=sa.text('0'), nullable=False),
    sa.Column('qp_amount', npf.UInt16(), npd.Comment('Quota period amount'), server_default=sa.text('1'), nullable=False),
    sa.Column('qp_unit', npf.DeclEnumType(name='QuotaPeriodUnit', values=['a_hour', 'a_day', 'a_week', 'a_month', 'a_year', 'c_hour', 'c_day', 'c_month', 'c_year', 'f_hour', 'f_day', 'f_week', 'f_month', 'f_year']), npd.Comment('Quota period unit'), server_default=sa.text("'c_month'"), nullable=False),
    sa.Column('cb_before', npf.ASCIIString(length=255), npd.Comment('Callback before charging'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('cb_success', npf.ASCIIString(length=255), npd.Comment('Callback on success'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('cb_failure', npf.ASCIIString(length=255), npd.Comment('Callback on failure'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('cb_ratemod', npf.ASCIIString(length=255), npd.Comment('Callback on linked rate'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('descr', sa.UnicodeText(), npd.Comment('Paid service description'), server_default=sa.text('NULL'), nullable=True),
    sa.PrimaryKeyConstraint('paidid', name=op.f('paid_types_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('paid_types', 'Paid service types')
    op.create_index('paid_types_i_qp_type', 'paid_types', ['qp_type'], unique=False)
    op.create_index('paid_types_u_name', 'paid_types', ['name'], unique=True)
    op.create_table('paid_def',
    sa.Column('epid', npf.UInt32(), npd.Comment('Paid service mapping ID'), nullable=False, default=sa.Sequence('paid_def_epid_seq')),
    sa.Column('entityid', npf.UInt32(), npd.Comment('Entity ID'), nullable=False),
    sa.Column('aeid', npf.UInt32(), npd.Comment('Access entity ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('hostid', npf.UInt32(), npd.Comment('Host ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('stashid', npf.UInt32(), npd.Comment('Used stash ID'), nullable=False),
    sa.Column('paidid', npf.UInt32(), npd.Comment('Type ID'), nullable=False),
    sa.Column('active', npf.NPBoolean(), npd.Comment('Is service active'), server_default=npf.npbool(True), nullable=False),
    sa.Column('qpend', sa.TIMESTAMP(), npd.Comment('End of quota period'), server_default=FetchedValue(), nullable=True),
    sa.Column('descr', sa.UnicodeText(), npd.Comment('Description'), server_default=sa.text('NULL'), nullable=True),
    sa.ForeignKeyConstraint(['aeid'], ['entities_access.entityid'], name='paid_def_fk_aeid', onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['entityid'], ['entities_def.entityid'], name='paid_def_fk_entityid', onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['hostid'], ['hosts_def.hostid'], name='paid_def_fk_hostid', onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['paidid'], ['paid_types.paidid'], name='paid_def_fk_paidid', onupdate='CASCADE'),
    sa.ForeignKeyConstraint(['stashid'], ['stashes_def.stashid'], name='paid_def_fk_stashid', onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('epid', name=op.f('paid_def_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('paid_def', 'Paid service mappings')
    op.create_trigger('netprofile_paidservices', 'paid_def', 'before', 'insert', '774d7277075e')
    op.create_trigger('netprofile_paidservices', 'paid_def', 'before', 'update', '774d7277075e')
    op.create_trigger('netprofile_paidservices', 'paid_def', 'after', 'insert', '774d7277075e')
    op.create_trigger('netprofile_paidservices', 'paid_def', 'after', 'update', '774d7277075e')
    op.create_trigger('netprofile_paidservices', 'paid_def', 'after', 'delete', '774d7277075e')
    op.create_index('paid_def_i_active', 'paid_def', ['active'], unique=False)
    op.create_index('paid_def_i_aeid', 'paid_def', ['aeid'], unique=False)
    op.create_index('paid_def_i_entityid', 'paid_def', ['entityid'], unique=False)
    op.create_index('paid_def_i_hostid', 'paid_def', ['hostid'], unique=False)
    op.create_index('paid_def_i_paidid', 'paid_def', ['paidid'], unique=False)
    op.create_index('paid_def_i_qpend', 'paid_def', ['qpend'], unique=False)
    op.create_index('paid_def_i_stashid', 'paid_def', ['stashid'], unique=False)
    op.create_function('paidservices', npd.SQLFunction('acct_pcheck', args=[npd.SQLFunctionArgument('aeid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('ts', sa.DateTime(), 'IN'), npd.SQLFunctionArgument('rate_type', npf.DeclEnumType(name='RateType', values=['prepaid', 'prepaid_cont', 'postpaid', 'free']), 'IN'), npd.SQLFunctionArgument('isok', npf.NPBoolean(), 'INOUT'), npd.SQLFunctionArgument('user_stashid', npf.UInt32(), 'INOUT'), npd.SQLFunctionArgument('user_qpend', sa.DateTime(), 'INOUT'), npd.SQLFunctionArgument('stash_amount', npf.Money(precision=20, scale=8), 'INOUT'), npd.SQLFunctionArgument('stash_credit', npf.Money(precision=20, scale=8), 'INOUT'), npd.SQLFunctionArgument('xcurrid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('xrate', npf.Money(precision=20, scale=8), 'IN'), npd.SQLFunctionArgument('pay', npf.Money(precision=20, scale=8), 'IN')], returns=None, comment='Run linked paid service checks', reads_sql=True, writes_sql=True, is_procedure=True, label='aapfunc'), '774d7277075e')
    op.create_function('paidservices', npd.SQLFunction('ps_poll', args=[npd.SQLFunctionArgument('ts', sa.DateTime(), 'IN')], returns=None, comment='Poll paid services', reads_sql=True, writes_sql=True, is_procedure=True, label=None), '774d7277075e')
    op.create_function('paidservices', npd.SQLFunction('ps_execute', args=[npd.SQLFunctionArgument('xepid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('ts', sa.DateTime(), 'IN')], returns=None, comment='Execute paid service handler', reads_sql=True, writes_sql=True, is_procedure=True, label='psefunc'), '774d7277075e')
    op.create_function('paidservices', npd.SQLFunction('ps_callback', args=[npd.SQLFunctionArgument('cbname', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('xepid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('ts', sa.DateTime(), 'IN'), npd.SQLFunctionArgument('ps_aeid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('ps_hostid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('ps_paidid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('ps_entityid', npf.UInt32(), 'INOUT'), npd.SQLFunctionArgument('ps_stashid', npf.UInt32(), 'INOUT'), npd.SQLFunctionArgument('ps_qpend', sa.DateTime(), 'INOUT'), npd.SQLFunctionArgument('pay', npf.Money(precision=20, scale=8), 'INOUT')], returns=None, comment='Callback helper for paid services', reads_sql=True, writes_sql=True, is_procedure=True, label=None), '774d7277075e')
    op.create_event('paidservices', npd.SQLEvent('ev_ps_poll', sched_unit='minute', sched_interval=15, starts=None, preserve=True, enabled=True, comment='Poll for independent paid services'), '774d7277075e')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_event('paidservices', npd.SQLEvent('ev_ps_poll', sched_unit='minute', sched_interval=15, starts=None, preserve=True, enabled=True, comment='Poll for independent paid services'), '774d7277075e')
    op.drop_function('paidservices', npd.SQLFunction('ps_callback', args=[npd.SQLFunctionArgument('cbname', sa.Unicode(length=255), 'IN'), npd.SQLFunctionArgument('xepid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('ts', sa.DateTime(), 'IN'), npd.SQLFunctionArgument('ps_aeid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('ps_hostid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('ps_paidid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('ps_entityid', npf.UInt32(), 'INOUT'), npd.SQLFunctionArgument('ps_stashid', npf.UInt32(), 'INOUT'), npd.SQLFunctionArgument('ps_qpend', sa.DateTime(), 'INOUT'), npd.SQLFunctionArgument('pay', npf.Money(precision=20, scale=8), 'INOUT')], returns=None, comment='Callback helper for paid services', reads_sql=True, writes_sql=True, is_procedure=True, label=None), '774d7277075e')
    op.drop_function('paidservices', npd.SQLFunction('ps_execute', args=[npd.SQLFunctionArgument('xepid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('ts', sa.DateTime(), 'IN')], returns=None, comment='Execute paid service handler', reads_sql=True, writes_sql=True, is_procedure=True, label='psefunc'), '774d7277075e')
    op.drop_function('paidservices', npd.SQLFunction('ps_poll', args=[npd.SQLFunctionArgument('ts', sa.DateTime(), 'IN')], returns=None, comment='Poll paid services', reads_sql=True, writes_sql=True, is_procedure=True, label=None), '774d7277075e')
    op.drop_function('paidservices', npd.SQLFunction('acct_pcheck', args=[npd.SQLFunctionArgument('aeid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('ts', sa.DateTime(), 'IN'), npd.SQLFunctionArgument('rate_type', npf.DeclEnumType(name='RateType', values=['prepaid', 'prepaid_cont', 'postpaid', 'free']), 'IN'), npd.SQLFunctionArgument('isok', npf.NPBoolean(), 'INOUT'), npd.SQLFunctionArgument('user_stashid', npf.UInt32(), 'INOUT'), npd.SQLFunctionArgument('user_qpend', sa.DateTime(), 'INOUT'), npd.SQLFunctionArgument('stash_amount', npf.Money(precision=20, scale=8), 'INOUT'), npd.SQLFunctionArgument('stash_credit', npf.Money(precision=20, scale=8), 'INOUT'), npd.SQLFunctionArgument('xcurrid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('xrate', npf.Money(precision=20, scale=8), 'IN'), npd.SQLFunctionArgument('pay', npf.Money(precision=20, scale=8), 'IN')], returns=None, comment='Run linked paid service checks', reads_sql=True, writes_sql=True, is_procedure=True, label='aapfunc'), '774d7277075e')
    op.drop_index('paid_def_i_stashid', table_name='paid_def')
    op.drop_index('paid_def_i_qpend', table_name='paid_def')
    op.drop_index('paid_def_i_paidid', table_name='paid_def')
    op.drop_index('paid_def_i_hostid', table_name='paid_def')
    op.drop_index('paid_def_i_entityid', table_name='paid_def')
    op.drop_index('paid_def_i_aeid', table_name='paid_def')
    op.drop_index('paid_def_i_active', table_name='paid_def')
    op.drop_table('paid_def')
    op.drop_index('paid_types_u_name', table_name='paid_types')
    op.drop_index('paid_types_i_qp_type', table_name='paid_types')
    op.drop_table('paid_types')
    # ### end Alembic commands ###
