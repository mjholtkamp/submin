#!/bin/sh
#
# Install files in the proper directories. Not shown in usage, but 
# if you provide two arguments it will install in the first prefix,
# but changes files because they will be ultimately installed in the
# second prefix. This is implemented so that files can be installed in
# a temporary directory used for packaging (i.e. debian package), but
# are ultimately installed in another.
#
# If any second argument is given, it will force install

if [ $# -lt 1 ]; then
	echo "Usage: $0 <installdir>"
	echo " for example: $0 /usr"
	exit 1
fi

PREFIX=$1
FINAL_PREFIX=${PREFIX}
SHARE=${PREFIX}/share/submin
SUBMIN_ADMIN=${PREFIX}/bin/submin-admin

if [ $# -gt 1 ]; then
	FINAL_PREFIX=$2
	FORCE=1
fi

if [ -e ${SHARE} ] || [ -e ${SUBMIN_ADMIN} ] && [ "${FORCE}" != "1" ]; then
	echo "Found previous installation at ${PREFIX}"
	echo "To overwrite use: $0 ${PREFIX} --force"
	exit 1
fi

cd `dirname $0`/..
# install submin-admin
install -g root -o root -m 755 bin/submin-admin.py ${SUBMIN_ADMIN}
# fix path
sed -i -e "s@_SUBMIN_LIB_DIR_@${FINAL_PREFIX}/share/submin/lib@" ${PREFIX}/bin/submin-admin

rm -rf "${SHARE}"
mkdir -p ${SHARE}
cp -r www lib templates ${SHARE}
chown root:root ${SHARE}/www/submin.cgi
chmod 755 ${SHARE}/www/submin.cgi
find ${SHARE} -type d -name .svn -exec rm -rf \{} \; -prune
