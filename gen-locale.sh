#!/bin/sh

for moddef in `ls -1 -d netprofile_*`
do
	cd $moddef
	python setup.py extract_messages
	python setup.py update_catalog
	python setup.py compile_catalog
	cd -
done

