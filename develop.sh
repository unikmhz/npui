#!/bin/sh
# Use this script to quickly install required dependencies
# and register module directories with distutils.
# WARNING: Use inside an activated virtualenv only!

NPMOD_DEFAULT="netprofile \
	netprofile_core \
	netprofile_documents \
	netprofile_geo \
	netprofile_dialup \
	netprofile_domains \
	netprofile_entities \
	netprofile_hosts \
	netprofile_networks \
	netprofile_ipaddresses \
	netprofile_rates \
	netprofile_tickets \
	netprofile_stashes \
	netprofile_access \
	netprofile_sessions \
	netprofile_paidservices \
	netprofile_xop"

pip install --upgrade \
	python-dateutil \
	icalendar \
	phpserialize \
	dogpile.cache \
	repoze.tm2 \
	SQLAlchemy \
	zope.sqlalchemy \
	transaction \
	waitress \
	pyramid \
	pyramid_mako \
	pyramid_rpc \
	pyramid_debugtoolbar \
	pyramid_redis_sessions \
	pyramid_mailer \
	cliff \
	Babel \
	lingua \
	lxml \
	tornado \
	sockjs-tornado \
	tornado-redis \
	cracklib

for mod in $NPMOD_DEFAULT
do
	pip install -e $mod
done

