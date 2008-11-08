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

rm -rf "${SHARE}"
mkdir -p ${SHARE}/www # make share and share/www
mkdir -p ${SHARE}/bin # make share/bin
cp -r www/{css,img,js} ${SHARE}/www
cp -r lib templates ${SHARE}
if [ "$ROOT" == "1" ]; then
	install -g root -o root -m 755 www/submin.{ws,c}gi ${SHARE}/www/
	install -g root -o root -m 755 bin/{commit-email.pl,post-commit.py} ${SHARE}/bin/
else
	install -m 755 www/submin.{ws,c}gi ${SHARE}/www/
	install -m 755 bin/{commit-email.pl,post-commit.py} ${SHARE}/bin/
fi

# fix hardcoded paths in binaries
## use .bak extension, because OSX and Linux sed versions differ in handling -i
sed -i".bak" -e "s@_SUBMIN_LIB_DIR_@${FINAL_PREFIX}/share/submin/lib@" ${PREFIX}/bin/submin-admin
rm -f ${PREFIX}/bin/submin-admin.bak
sed -i".bak" -e "s@_SUBMIN_SHARE_DIR_@${FINAL_PREFIX}/share/submin/@" ${SHARE}/lib/subminadmin/subminadmin.py
rm -f ${SHARE}/lib/subminadmin/subminadmin.py.bak
sed -i".bak" -e "s@_SUBMIN_LIB_DIR_@${FINAL_PREFIX}/share/submin/lib@" ${SHARE}/bin/post-commit.py
rm -f ${SHARE}/bin/post-commit.py.bak

find ${SHARE} -type d -name .svn -exec rm -rf \{\} \; -prune
find ${SHARE} -type f -name \*.pyc -exec rm -rf \{\} \;