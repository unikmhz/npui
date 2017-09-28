"""Initial revision

Revision ID: 7829ac7b5ad0
Revises: 
Create Date: 2017-09-25 14:21:03.278895

"""

# revision identifiers, used by Alembic.
revision = '7829ac7b5ad0'
down_revision = None
branch_labels = ('hosts',)
depends_on = ['98de7f7fe99d', '16be1c0cddd0']

from alembic import op
import sqlalchemy as sa
from sqlalchemy import FetchedValue
from netprofile.db import ddl as npd
from netprofile.db import fields as npf

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hosts_groups',
    sa.Column('hgid', npf.UInt32(), npd.Comment('Host group ID'), nullable=False, default=sa.Sequence('hosts_groups_hgid_seq')),
    sa.Column('name', sa.Unicode(length=255), npd.Comment('Host group name'), nullable=False),
    sa.Column('public', npf.NPBoolean(), npd.Comment('Is host group globally visible?'), server_default=npf.npbool(True), nullable=False),
    sa.Column('startoffset', npf.UInt16(), npd.Comment('IP allocator start offset'), server_default=sa.text('0'), nullable=False),
    sa.Column('endoffset', npf.UInt16(), npd.Comment('IP allocator end offset'), server_default=sa.text('0'), nullable=False),
    sa.Column('startoffset6', npf.UInt64(), npd.Comment('IPv6 allocator start offset'), server_default=sa.text('0'), nullable=False),
    sa.Column('endoffset6', npf.UInt64(), npd.Comment('IPv6 allocator end offset'), server_default=sa.text('0'), nullable=False),
    sa.Column('use_hwaddr', npf.NPBoolean(), npd.Comment('Use unique hardware address check'), server_default=npf.npbool(True), nullable=False),
    sa.Column('use_dhcp', npf.NPBoolean(), npd.Comment('Use DHCP'), server_default=npf.npbool(True), nullable=False),
    sa.Column('use_banning', npf.NPBoolean(), npd.Comment('Use banning system'), server_default=npf.npbool(True), nullable=False),
    sa.PrimaryKeyConstraint('hgid', name=op.f('hosts_groups_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('hosts_groups', 'Host groups')
    op.create_index('hosts_groups_u_hgname', 'hosts_groups', ['name'], unique=True)
    op.create_table('services_types',
    sa.Column('stid', npf.UInt32(), npd.Comment('Service type ID'), nullable=False, default=sa.Sequence('services_types_stid_seq')),
    sa.Column('abbrev', npf.ASCIIString(length=32), npd.Comment('Service type abbreviation'), nullable=False),
    sa.Column('name', sa.Unicode(length=255), npd.Comment('Service type name'), nullable=False),
    sa.Column('proto', npf.DeclEnumType(name='ServiceProtocol', values=['none', 'tcp', 'udp', 'sctp', 'dccp', 'tls']), npd.Comment('Used protocol(s)'), server_default=sa.text("'tcp'"), nullable=False),
    sa.Column('port_start', npf.UInt16(), npd.Comment('Port range start'), nullable=False),
    sa.Column('port_end', npf.UInt16(), npd.Comment('Port range end'), nullable=False),
    sa.Column('alias', npf.ASCIIText(), npd.Comment('List of alternate names'), server_default=sa.text('NULL'), nullable=True),
    sa.PrimaryKeyConstraint('stid', name=op.f('services_types_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('services_types', 'Service types')
    op.create_index('services_types_i_abbrev', 'services_types', ['abbrev'], unique=False)
    op.create_index('services_types_u_service', 'services_types', ['proto', 'abbrev'], unique=True)
    op.create_table('hosts_def',
    sa.Column('hostid', npf.UInt32(), npd.Comment('Host ID'), nullable=False, default=sa.Sequence('hosts_def_hostid_seq')),
    sa.Column('hgid', npf.UInt32(), npd.Comment('Host group ID'), nullable=False),
    sa.Column('entityid', npf.UInt32(), npd.Comment('Entity ID'), nullable=False),
    sa.Column('domainid', npf.UInt32(), npd.Comment('Domain ID'), nullable=False),
    sa.Column('name', sa.Unicode(length=255), npd.Comment('Host Name'), nullable=False),
    sa.Column('aliasid', npf.UInt32(), npd.Comment('Aliased host ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('aliastype', npf.DeclEnumType(name='HostAliasType', values=['SYM', 'NUM']), npd.Comment('Host alias type'), server_default=sa.text("'SYM'"), nullable=False),
    sa.Column('ctime', sa.TIMESTAMP(), npd.Comment('Time of creation'), server_default=FetchedValue(), nullable=True),
    sa.Column('mtime', sa.TIMESTAMP(), npd.Comment('Time of last modification'), server_default=npd.CurrentTimestampDefault(on_update=True), nullable=False),
    sa.Column('cby', npf.UInt32(), npd.Comment('Created by'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('mby', npf.UInt32(), npd.Comment('Last modified by'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('descr', sa.UnicodeText(), npd.Comment('Host description'), server_default=sa.text('NULL'), nullable=True),
    sa.ForeignKeyConstraint(['aliasid'], ['hosts_def.hostid'], name='hosts_def_fk_aliasid', onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['cby'], ['users.uid'], name='hosts_def_fk_cby', onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['domainid'], ['domains_def.domainid'], name='hosts_def_fk_domainid', onupdate='CASCADE'),
    sa.ForeignKeyConstraint(['entityid'], ['entities_def.entityid'], name='hosts_def_fk_entityid', onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['hgid'], ['hosts_groups.hgid'], name='hosts_def_fk_hgid', onupdate='CASCADE'),
    sa.ForeignKeyConstraint(['mby'], ['users.uid'], name='hosts_def_fk_mby', onupdate='CASCADE', ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('hostid', name=op.f('hosts_def_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('hosts_def', 'Hosts')
    op.create_trigger('netprofile_hosts', 'hosts_def', 'before', 'insert', '7829ac7b5ad0')
    op.create_trigger('netprofile_hosts', 'hosts_def', 'before', 'update', '7829ac7b5ad0')
    op.create_trigger('netprofile_hosts', 'hosts_def', 'after', 'insert', '7829ac7b5ad0')
    op.create_trigger('netprofile_hosts', 'hosts_def', 'after', 'update', '7829ac7b5ad0')
    op.create_trigger('netprofile_hosts', 'hosts_def', 'after', 'delete', '7829ac7b5ad0')
    op.create_index('hosts_def_i_aliasid', 'hosts_def', ['aliasid'], unique=False)
    op.create_index('hosts_def_i_cby', 'hosts_def', ['cby'], unique=False)
    op.create_index('hosts_def_i_entityid', 'hosts_def', ['entityid'], unique=False)
    op.create_index('hosts_def_i_hgid', 'hosts_def', ['hgid'], unique=False)
    op.create_index('hosts_def_i_mby', 'hosts_def', ['mby'], unique=False)
    op.create_index('hosts_def_u_hostname', 'hosts_def', ['domainid', 'name'], unique=True)
    op.create_table('domains_hosts',
    sa.Column('dhid', npf.UInt32(), npd.Comment('Domain-host linkage ID'), nullable=False, default=sa.Sequence('domains_hosts_dhid_seq')),
    sa.Column('domainid', npf.UInt32(), npd.Comment('Domain ID'), nullable=False),
    sa.Column('hostid', npf.UInt32(), npd.Comment('Host ID'), nullable=False),
    sa.Column('hltypeid', npf.UInt32(), npd.Comment('Domain-host linkage type'), nullable=False),
    sa.ForeignKeyConstraint(['domainid'], ['domains_def.domainid'], name='domains_hosts_fk_domainid', onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['hltypeid'], ['domains_hltypes.hltypeid'], name='domains_hosts_fk_hltypeid', onupdate='CASCADE'),
    sa.ForeignKeyConstraint(['hostid'], ['hosts_def.hostid'], name='domains_hosts_fk_hostid', onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('dhid', name=op.f('domains_hosts_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('domains_hosts', 'Domains-hosts linkage')
    op.create_index('domains_hosts_i_hltypeid', 'domains_hosts', ['hltypeid'], unique=False)
    op.create_index('domains_hosts_i_hostid', 'domains_hosts', ['hostid'], unique=False)
    op.create_index('domains_hosts_u_dhl', 'domains_hosts', ['domainid', 'hostid', 'hltypeid'], unique=True)
    op.create_table('services_def',
    sa.Column('sid', npf.UInt32(), npd.Comment('Service ID'), nullable=False, default=sa.Sequence('services_def_sid_seq')),
    sa.Column('hostid', npf.UInt32(), npd.Comment('Host ID'), nullable=False),
    sa.Column('stid', npf.UInt32(), npd.Comment('Service type ID'), nullable=False),
    sa.Column('domainid', npf.UInt32(), npd.Comment('Alternate domain ID'), server_default=sa.text('NULL'), nullable=True),
    sa.Column('priority', npf.UInt32(), npd.Comment('Service priority'), server_default=sa.text('0'), nullable=False),
    sa.Column('weight', npf.UInt32(), npd.Comment('Service weight'), server_default=sa.text('0'), nullable=False),
    sa.Column('vis', npf.DeclEnumType(name='ObjectVisibility', values=['B', 'I', 'E']), npd.Comment('Service visibility'), server_default=sa.text("'I'"), nullable=False),
    sa.ForeignKeyConstraint(['domainid'], ['domains_def.domainid'], name='services_def_fk_domainid', onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['hostid'], ['hosts_def.hostid'], name='services_def_fk_hostid', onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['stid'], ['services_types.stid'], name='services_def_fk_stid', onupdate='CASCADE'),
    sa.PrimaryKeyConstraint('sid', name=op.f('services_def_pk')),
    mysql_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.set_table_comment('services_def', 'Services')
    op.create_index('services_def_i_domainid', 'services_def', ['domainid'], unique=False)
    op.create_index('services_def_i_stid', 'services_def', ['stid'], unique=False)
    op.create_index('services_def_u_service', 'services_def', ['hostid', 'stid', 'domainid'], unique=True)
    op.create_function('hosts', npd.SQLFunction('host_create_alias', args=[npd.SQLFunctionArgument('hid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('did', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('aname', sa.Unicode(length=255), 'IN')], returns=None, comment='Make a host alias (CNAME in DNS-speak)', reads_sql=True, writes_sql=True, is_procedure=True, label=None), '7829ac7b5ad0')
    op.create_view('hosts_aliases', {'oracle': 'SELECT hosts_def.hostid AS hostid, hosts_def.hgid AS hgid, hosts_def.entityid AS entityid, hosts_def.domainid AS domainid, hosts_def.name AS name, hosts_def.aliasid AS aliasid, hosts_def.aliastype AS aliastype, hosts_def.ctime AS ctime, hosts_def.mtime AS mtime, hosts_def.cby AS cby, hosts_def.mby AS mby, hosts_def.descr AS descr \nFROM hosts_def \nWHERE hosts_def.aliasid IS NOT NULL', 'postgresql': 'SELECT hosts_def.hostid AS hostid, hosts_def.hgid AS hgid, hosts_def.entityid AS entityid, hosts_def.domainid AS domainid, hosts_def.name AS name, hosts_def.aliasid AS aliasid, hosts_def.aliastype AS aliastype, hosts_def.ctime AS ctime, hosts_def.mtime AS mtime, hosts_def.cby AS cby, hosts_def.mby AS mby, hosts_def.descr AS descr \nFROM hosts_def \nWHERE hosts_def.aliasid IS NOT NULL', 'mssql': 'SELECT hosts_def.hostid AS hostid, hosts_def.hgid AS hgid, hosts_def.entityid AS entityid, hosts_def.domainid AS domainid, hosts_def.name AS name, hosts_def.aliasid AS aliasid, hosts_def.aliastype AS aliastype, hosts_def.ctime AS ctime, hosts_def.mtime AS mtime, hosts_def.cby AS cby, hosts_def.mby AS mby, hosts_def.descr AS descr \nFROM hosts_def \nWHERE hosts_def.aliasid IS NOT NULL', 'mysql': 'SELECT hosts_def.hostid AS hostid, hosts_def.hgid AS hgid, hosts_def.entityid AS entityid, hosts_def.domainid AS domainid, hosts_def.name AS name, hosts_def.aliasid AS aliasid, hosts_def.aliastype AS aliastype, hosts_def.ctime AS ctime, hosts_def.mtime AS mtime, hosts_def.cby AS cby, hosts_def.mby AS mby, hosts_def.descr AS descr \nFROM hosts_def \nWHERE hosts_def.aliasid IS NOT NULL'}, check_option='CASCADED')
    op.create_view('hosts_real', {'oracle': 'SELECT hosts_def.hostid AS hostid, hosts_def.hgid AS hgid, hosts_def.entityid AS entityid, hosts_def.domainid AS domainid, hosts_def.name AS name, NULL AS aliasid, hosts_def.aliastype AS aliastype, hosts_def.ctime AS ctime, hosts_def.mtime AS mtime, hosts_def.cby AS cby, hosts_def.mby AS mby, hosts_def.descr AS descr \nFROM hosts_def \nWHERE hosts_def.aliasid IS NULL', 'postgresql': 'SELECT hosts_def.hostid AS hostid, hosts_def.hgid AS hgid, hosts_def.entityid AS entityid, hosts_def.domainid AS domainid, hosts_def.name AS name, NULL AS aliasid, hosts_def.aliastype AS aliastype, hosts_def.ctime AS ctime, hosts_def.mtime AS mtime, hosts_def.cby AS cby, hosts_def.mby AS mby, hosts_def.descr AS descr \nFROM hosts_def \nWHERE hosts_def.aliasid IS NULL', 'mssql': 'SELECT hosts_def.hostid AS hostid, hosts_def.hgid AS hgid, hosts_def.entityid AS entityid, hosts_def.domainid AS domainid, hosts_def.name AS name, NULL AS aliasid, hosts_def.aliastype AS aliastype, hosts_def.ctime AS ctime, hosts_def.mtime AS mtime, hosts_def.cby AS cby, hosts_def.mby AS mby, hosts_def.descr AS descr \nFROM hosts_def \nWHERE hosts_def.aliasid IS NULL', 'mysql': 'SELECT hosts_def.hostid AS hostid, hosts_def.hgid AS hgid, hosts_def.entityid AS entityid, hosts_def.domainid AS domainid, hosts_def.name AS name, NULL AS aliasid, hosts_def.aliastype AS aliastype, hosts_def.ctime AS ctime, hosts_def.mtime AS mtime, hosts_def.cby AS cby, hosts_def.mby AS mby, hosts_def.descr AS descr \nFROM hosts_def \nWHERE hosts_def.aliasid IS NULL'}, check_option='CASCADED')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_view('hosts_real', {'oracle': 'SELECT hosts_def.hostid AS hostid, hosts_def.hgid AS hgid, hosts_def.entityid AS entityid, hosts_def.domainid AS domainid, hosts_def.name AS name, NULL AS aliasid, hosts_def.aliastype AS aliastype, hosts_def.ctime AS ctime, hosts_def.mtime AS mtime, hosts_def.cby AS cby, hosts_def.mby AS mby, hosts_def.descr AS descr \nFROM hosts_def \nWHERE hosts_def.aliasid IS NULL', 'postgresql': 'SELECT hosts_def.hostid AS hostid, hosts_def.hgid AS hgid, hosts_def.entityid AS entityid, hosts_def.domainid AS domainid, hosts_def.name AS name, NULL AS aliasid, hosts_def.aliastype AS aliastype, hosts_def.ctime AS ctime, hosts_def.mtime AS mtime, hosts_def.cby AS cby, hosts_def.mby AS mby, hosts_def.descr AS descr \nFROM hosts_def \nWHERE hosts_def.aliasid IS NULL', 'mssql': 'SELECT hosts_def.hostid AS hostid, hosts_def.hgid AS hgid, hosts_def.entityid AS entityid, hosts_def.domainid AS domainid, hosts_def.name AS name, NULL AS aliasid, hosts_def.aliastype AS aliastype, hosts_def.ctime AS ctime, hosts_def.mtime AS mtime, hosts_def.cby AS cby, hosts_def.mby AS mby, hosts_def.descr AS descr \nFROM hosts_def \nWHERE hosts_def.aliasid IS NULL', 'mysql': 'SELECT hosts_def.hostid AS hostid, hosts_def.hgid AS hgid, hosts_def.entityid AS entityid, hosts_def.domainid AS domainid, hosts_def.name AS name, NULL AS aliasid, hosts_def.aliastype AS aliastype, hosts_def.ctime AS ctime, hosts_def.mtime AS mtime, hosts_def.cby AS cby, hosts_def.mby AS mby, hosts_def.descr AS descr \nFROM hosts_def \nWHERE hosts_def.aliasid IS NULL'}, check_option='CASCADED')
    op.drop_view('hosts_aliases', {'oracle': 'SELECT hosts_def.hostid AS hostid, hosts_def.hgid AS hgid, hosts_def.entityid AS entityid, hosts_def.domainid AS domainid, hosts_def.name AS name, hosts_def.aliasid AS aliasid, hosts_def.aliastype AS aliastype, hosts_def.ctime AS ctime, hosts_def.mtime AS mtime, hosts_def.cby AS cby, hosts_def.mby AS mby, hosts_def.descr AS descr \nFROM hosts_def \nWHERE hosts_def.aliasid IS NOT NULL', 'postgresql': 'SELECT hosts_def.hostid AS hostid, hosts_def.hgid AS hgid, hosts_def.entityid AS entityid, hosts_def.domainid AS domainid, hosts_def.name AS name, hosts_def.aliasid AS aliasid, hosts_def.aliastype AS aliastype, hosts_def.ctime AS ctime, hosts_def.mtime AS mtime, hosts_def.cby AS cby, hosts_def.mby AS mby, hosts_def.descr AS descr \nFROM hosts_def \nWHERE hosts_def.aliasid IS NOT NULL', 'mssql': 'SELECT hosts_def.hostid AS hostid, hosts_def.hgid AS hgid, hosts_def.entityid AS entityid, hosts_def.domainid AS domainid, hosts_def.name AS name, hosts_def.aliasid AS aliasid, hosts_def.aliastype AS aliastype, hosts_def.ctime AS ctime, hosts_def.mtime AS mtime, hosts_def.cby AS cby, hosts_def.mby AS mby, hosts_def.descr AS descr \nFROM hosts_def \nWHERE hosts_def.aliasid IS NOT NULL', 'mysql': 'SELECT hosts_def.hostid AS hostid, hosts_def.hgid AS hgid, hosts_def.entityid AS entityid, hosts_def.domainid AS domainid, hosts_def.name AS name, hosts_def.aliasid AS aliasid, hosts_def.aliastype AS aliastype, hosts_def.ctime AS ctime, hosts_def.mtime AS mtime, hosts_def.cby AS cby, hosts_def.mby AS mby, hosts_def.descr AS descr \nFROM hosts_def \nWHERE hosts_def.aliasid IS NOT NULL'}, check_option='CASCADED')
    op.drop_function('hosts', npd.SQLFunction('host_create_alias', args=[npd.SQLFunctionArgument('hid', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('did', npf.UInt32(), 'IN'), npd.SQLFunctionArgument('aname', sa.Unicode(length=255), 'IN')], returns=None, comment='Make a host alias (CNAME in DNS-speak)', reads_sql=True, writes_sql=True, is_procedure=True, label=None), '7829ac7b5ad0')
    op.drop_index('services_def_u_service', table_name='services_def')
    op.drop_index('services_def_i_stid', table_name='services_def')
    op.drop_index('services_def_i_domainid', table_name='services_def')
    op.drop_table('services_def')
    op.drop_index('domains_hosts_u_dhl', table_name='domains_hosts')
    op.drop_index('domains_hosts_i_hostid', table_name='domains_hosts')
    op.drop_index('domains_hosts_i_hltypeid', table_name='domains_hosts')
    op.drop_table('domains_hosts')
    op.drop_index('hosts_def_u_hostname', table_name='hosts_def')
    op.drop_index('hosts_def_i_mby', table_name='hosts_def')
    op.drop_index('hosts_def_i_hgid', table_name='hosts_def')
    op.drop_index('hosts_def_i_entityid', table_name='hosts_def')
    op.drop_index('hosts_def_i_cby', table_name='hosts_def')
    op.drop_index('hosts_def_i_aliasid', table_name='hosts_def')
    op.drop_table('hosts_def')
    op.drop_index('services_types_u_service', table_name='services_types')
    op.drop_index('services_types_i_abbrev', table_name='services_types')
    op.drop_table('services_types')
    op.drop_index('hosts_groups_u_hgname', table_name='hosts_groups')
    op.drop_table('hosts_groups')
    # ### end Alembic commands ###
