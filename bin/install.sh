#!/bin/sh

if [ $# -lt 1 ]; then
	echo "Usage: $0 <installdir>"
	echo " for example: $0 /usr"
	exit 1
fi

PREFIX=$1
FINAL_PREFIX=${PREFIX}

if [ $# -gt 1 ]; then
	FINAL_PREFIX=$2
fi

cd `dirname $0`/..
# install submin-admin
install -g root -o root -m 755 bin/submin-admin.py ${PREFIX}/bin/submin-admin
# fix path
sed -ie "s@_SUBMIN_LIB_DIR_@${FINAL_PREFIX}/share/submin/lib@" ${PREFIX}/bin/submin-admin

SHARE=${PREFIX}/share/submin
mkdir -p ${SHARE}
cp -r www lib ${SHARE}
chown root:root ${SHARE}/www/submin.py
chmod 755 ${SHARE}/www/submin.py
find ${SHARE} -type d -name .svn -exec rm -rf \{} \; -prune
