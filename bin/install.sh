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
if [ "`id -u`" == "0" ]; then
	ROOT=1
else
	ROOT=0
fi

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
mkdir -p `dirname ${SUBMIN_ADMIN}`
if [ "$ROOT" == "1" ]; then
	install -g root -o root -m 755 bin/submin-admin.py ${SUBMIN_ADMIN}
else
	install -m 755 bin/submin-admin.py ${SUBMIN_ADMIN}
fi

# fix path
sed -i "" -e "s@_SUBMIN_LIB_DIR_@${FINAL_PREFIX}/share/submin/lib@" ${PREFIX}/bin/submin-admin

rm -rf "${SHARE}"
mkdir -p ${SHARE}/www # make share and share/www
cp -r www/{css,img,js} ${SHARE}/www
cp -r lib templates ${SHARE}
if [ "$ROOT" == "1" ]; then
	install -g root -o root -m 755 www/submin.{ws,c}gi ${SHARE}/www/
else
	install -m 755 www/submin.{ws,c}gi ${SHARE}/www/
fi
find ${SHARE} -type d -name .svn -exec rm -rf \{} \; -prune
