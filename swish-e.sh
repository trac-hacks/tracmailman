#!/bin/bash
#
# The location of the swish-e configuration file
#
CONFIG_LOCATION=/home/therji/tracmailman-plugin-0.2/swish-e.config
#
# The location of where the indexes will be put (should be the same as
# search_index_path in trac.ini).
#
search_index_path = /home/trac/desi/mailman_indices
#
# The location of the archive files (should be the same as mail_archive_path
# in trac.ini).
#
mail_archive_path=/var/lib/mailman/archives
#
# DO NOT CHANGE THE NAME OF THE INDEX FILES
#
# Index all the mailman archives, under /var/lib/mailman/public and /var/lib/mailman/private
#
swish-e -c ${CONFIG_LOCATION} -f ${search_index_path}/all-index.swish-e
#
# Index each individual mailman archive in public and private
#
for p in public private; do
    for f in $( /bin/ls ${mail_archive_path}/${p} ); do
        extension=${f##*.}
        if [ "${extension}" != "mbox" ]
            then swish-e -c ${CONFIG_LOCATION} -i ${mail_archive_path}/${p}/${f} -f ${search_index_path}/${f}-index.swish-e
        fi
    done
done
