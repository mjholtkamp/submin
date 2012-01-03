#!/bin/sh

BASEDIR=`pwd`/`dirname $0`/../../
if [ -z "${PYTHONPATH}" ]; then
	export PYTHONPATH=${BASEDIR}/packages
else
	export PYTHONPATH=${BASEDIR}/packages:${PYTHONPATH}
fi
${BASEDIR}/bin/submin2-admin $*
