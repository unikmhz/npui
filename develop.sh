#!/bin/sh
# Use this script to quickly install required dependencies
# and register module directories with distutils.
# WARNING: Use inside an activated virtualenv only!

test -z "$VIRTUAL_ENV" && exit 1

NPMOD_DEFAULT="netprofile \
	netprofile_core \
	netprofile_documents \
	netprofile_geo \
	netprofile_dialup \
	netprofile_domains \
	netprofile_entities \
	netprofile_hosts \
	netprofile_devices \
	netprofile_networks \
	netprofile_ipaddresses \
	netprofile_rates \
	netprofile_tickets \
	netprofile_stashes \
	netprofile_access \
	netprofile_sessions \
	netprofile_paidservices \
	netprofile_xop \
	netprofile_confgen"

pip install \
	--upgrade \
	python-dateutil \
	phpserialize \
	dogpile.cache \
	repoze.tm2 \
	SQLAlchemy \
	zope.sqlalchemy \
	transaction \
	waitress \
	pyramid \
	pyramid_mako \
	pyramid_redis_sessions \
	pyramid_rpc \
	pyramid_debugtoolbar \
	pyramid_mailer \
	cliff \
	Babel \
	lingua \
	lxml \
	tornado \
	sockjs-tornado \
	tornado-celery \
	tornado-redis \
	cracklib

# FIXME: maybe remove this, or let the user choose a driver?
pip install \
	--upgrade \
	pymysql

for mod in $NPMOD_DEFAULT
do
	pip install -e $mod
done

