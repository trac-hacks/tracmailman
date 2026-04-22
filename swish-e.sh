#!/bin/bash
#
# Licensed under a 3-clause BSD style license - see LICENSE.rst
#
function usage() {
    local execName=$(/usr/bin/basename $0)
    (
        echo "${execName} [-c CONFIG] [-f INDEX] [-h] [-i MAIL] [-t] [-v]"
        echo ""
        echo "Run the swish-e indexer on a set of mail archives."
        echo ""
        echo "    -c CONFIG Configuration file for the swish-e executable."
        echo "    -f INDEX  Write index files to INDEX."
        echo "    -h        Print help and exit."
        echo "    -i MAIL   Location of the mailmain archive files."
        echo "    -t        Test mode. Do not run commands. Implies -v."
        echo "    -v        Verbose mode. Print extra information."
        echo ""
        echo "Note: options, e.g. -i, are chosen to match the swish-e executable."
    ) >&2
}
#
# Configuration setup.
#
config_file=/home/trac/desi/mailman_indices/swish-e.config
# The location of where the indexes will be put (should be the same as
# search_index_path in trac.ini).
index_path=/home/trac/desi/mailman_indices
# The location of the archive files (should be the same as mail_archive_path
# in trac.ini).
mail_path=/home/mailman/archives
verbose=/usr/bin/false
test=/usr/bin/false
while getopts c:f:hi:tv argname; do
    case ${argname} in
        c) config_file=${OPTARG} ;;
        f) index_path=${OPTARG} ;;
        h) usage; exit 0 ;;
        i) mail_path=${OPTARG} ;;
        t) test=/usr/bin/true; verbose=/usr/bin/true ;;
        v) verbose=/usr/bin/true ;;
        *) usage; exit 1 ;;
    esac
done
#
# DO NOT CHANGE THE NAME OF THE INDEX FILES
#
# Index all the mailman archives.
#
${verbose} && echo "swish-e -c ${config_file} -f ${index_path}/all-index.swish-e" >&2
${test}    || swish-e -c ${config_file} -f ${index_path}/all-index.swish-e
#
# Index each individual mailman archive in public and private.
#
for p in public private; do
    for f in $( /usr/bin/ls ${mail_path}/${p} ); do
        extension=${f##*.}
        if [[ "${extension}" != "mbox" ]]; then
            ${verbose} && echo "swish-e -c ${config_file} -i ${mail_path}/${p}/${f} -f ${index_path}/${f}-index.swish-e" >&2
            ${test}    || swish-e -c ${config_file} -i ${mail_path}/${p}/${f} -f ${index_path}/${f}-index.swish-e
        fi
    done
done
