#!/bin/sh

for moddef in `find . -maxdepth 1 -type d -name 'netprofile*'`
do
	cp -a README.rst $moddef/README-NP.rst
	cp -a LICENSE $moddef/LICENSE.txt
done

