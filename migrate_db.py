"""
Migrates history when contact's number receives a 9 (ANATEL new rules)
"""

#!/usr/bin/python


import sqlite3
import sys


# verify sanity
if len(sys.argv) < 2:
    print "Usage: %s <file>" % (sys.argv[0])
    sys.exit(1)
DATABASE = sys.argv[1]

# connect to db
CONN = sqlite3.connect(DATABASE)

# process contacts in history
CURSOR = CONN.execute("select key_remote_jid from messages")
for row in CURSOR:
    contact = row[0]

    # general condition
    # condition: contact is from SP state
    condition = contact.startswith("551")

    # conditions for individual contact
    # condition_i1: contact hasn't been migrated yet
    condition_i1 = len(contact) == 27
    # condition_i2: contact is individual, not group
    condition_i2 = "@s.whatsapp.net" in contact
    # concatenates individual conditions
    individual_conditions = condition and condition_i1 and condition_i2

    # conditions for group contact
    # condition_g1: contact hasn't been migrated yet
    condition_g1 = len(contact) == 28
    # condition_g2: contact is individual, not group
    condition_g2 = "@g.us" in contact
    # concatenate group conditions
    group_conditions = condition and condition_g1 and condition_g2

    # conditions for migration match: profit!
    if individual_conditions or group_conditions:
        # put the 9 in the correct position
        newcontact = contact[:4] + '9' + contact[4:]
        print "Updating contact ID: %s is now %s" % (contact, newcontact)
        # update contact
        update_query = "update messages set key_remote_jid='%s' where " \
                       "key_remote_jid='%s'" % (newcontact, contact)
        CONN.execute(update_query)
        CONN.commit()

print "Total number of rows updated: %d" % CONN.total_changes
CONN.close()
