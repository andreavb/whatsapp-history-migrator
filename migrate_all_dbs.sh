#!/bin/bash

for cryptfile in `ls *db.crypt`; do
    dbfile=`basename $cryptfile .crypt`
    openssl enc -d -aes-192-ecb -in $cryptfile -out $dbfile -K 346a23652a46392b4d73257c67317e352e3372482177652c
    rm $cryptfile 2>/dev/null
    python migrate_db.py $dbfile
    openssl enc -e -aes-192-ecb -in $dbfile -out $cryptfile -K 346a23652a46392b4d73257c67317e352e3372482177652c
done

exit 0

