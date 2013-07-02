#!/bin/bash

# The location of the swish-e configuration file
CONFIG_LOCATION=/home/therji/tracmailman-plugin-0.2/swish-e.config

# The location of where the indexes will be put
INDEX_LOCATION=/home/therji

# DO NOT CHANGE THE NAME OF THE INDEX FILES

# Index all the mailman archives, under /var/lib/mailman/public and /var/lib/mailman/private
swish-e -c $CONFIG_LOCATION -f $INDEX_LOCATION/all-index.swish-e

# Index each individual mailman archive in public
for f in $( ls /var/lib/mailman/archives/public ); do
    extension=${f##*.}
    if [ $extension != "mbox" ]
        then swish-e -c $CONFIG_LOCATION -i /var/lib/mailman/archives/public/$f -f $INDEX_LOCATION/$f-index.swish-e
    fi

done

# Index each individual mailman archive in private
for f in $( ls /var/lib/mailman/archives/private ); do
    extension=${f##*.}
    if [ $extension != "mbox" ]
        then swish-e -c $CONFIG_LOCATION -i /var/lib/mailman/archives/private/$f -f $INDEX_LOCATION/$f-index.swish-e
    fi
    
done

