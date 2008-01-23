#!/bin/sh

if [ $# -lt 1 ]; then
	echo "Usage: $0 <installdir>"
	echo " for example: $0 /usr"
	exit 1
fi

PREFIX=$1

cd `dirname $0`/..
install -g root -o root -m 755 bin/submin-admin.py ${PREFIX}/bin/submin-admin
SHARE=${PREFIX}/share/submin
mkdir -p ${SHARE}
cp -r www lib ${SHARE}
find ${SHARE} -type d -name .svn -exec rm -rf \{} \; -prune
