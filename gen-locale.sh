#!/bin/sh

curdir=`pwd`
for moddef in `find . -maxdepth 1 -type d -name 'netprofile*'`
do
	cd $moddef
	python setup.py extract_messages
	python setup.py update_catalog
	python setup.py compile_catalog
	cd $curdir
done

