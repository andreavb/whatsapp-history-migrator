"""
Migrates history when contact's number receives a 9 (ANATEL new rules)
"""

#!/usr/bin/python


import sqlite3
import sys


def individual_conditions(contact):
    """
    Check if individual contact matches conditions to be changed

    @param string contact contact id
    @return bool if contact matches conditions
    """

    # general condition: contact is from SP state
    condition = contact.startswith("551") or contact.startswith("552")
    # condition_i1: contact hasn't been migrated yet
    condition_i1 = len(contact) == 27
    # condition_i2: contact is individual, not group
    condition_i2 = "@s.whatsapp.net" in contact
    # concatenates individual conditions
    conditions = condition and condition_i1 and condition_i2

    return conditions
    # individual_conditions()


def group_conditions(contact):
    """
    Check if group contact matches conditions to be changed

    @param string contact contact id
    @return bool if contact matches conditions
    """

    # general condition: contact is from SP state
    condition = contact.startswith("551")
    # condition_g1: contact hasn't been migrated yet
    condition_g1 = len(contact) == 28
    # condition_g2: contact is individual, not group
    condition_g2 = "@g.us" in contact
    # concatenate group conditions
    conditions = condition and condition_g1 and condition_g2

    return conditions
    # group_conditions()


def change_contacts(connection, table):
    """
    @param table either messages or chat_list
    """

    cursor = connection.execute("select key_remote_jid from %s" % table)
    for row in cursor:

        contact = row[0]

        # conditions for migration match: profit!
        if individual_conditions(contact) or group_conditions(contact):
            # put the 9 in the correct position
            newcontact = contact[:4] + '9' + contact[4:]
            print "Updating contact ID: %s is now %s" % (contact, newcontact)
            # update contact

            try:
                update_query = "update %s set key_remote_jid='%s' where " \
                       "key_remote_jid='%s'" % (table, newcontact, contact)
                connection.execute(update_query)
                connection.commit()
            # column key_remote_jid must be unique in chat_list table
            except sqlite3.IntegrityError:
                if table == "chat_list":
                    delete_query = "delete from %s where key_remote_jid='%s'" \
                        % (table, contact)
                    connection.execute(delete_query)
                    connection.commit()
                    update_query = "update %s set key_remote_jid='%s' where " \
                           "key_remote_jid='%s'" % (table, newcontact, contact)
                    connection.execute(update_query)

    print "Total number of rows updated: %d" % connection.total_changes
    # change_contacts()


# verify sanity
if len(sys.argv) < 2:
    print "Usage: %s <file>" % (sys.argv[0])
    sys.exit(1)
DATABASE = sys.argv[1]

# open db connection
CONN = sqlite3.connect(DATABASE)
# update db
for data in ("messages", "chat_list"):
    change_contacts(CONN, data)
# close db connection
CONN.close()
