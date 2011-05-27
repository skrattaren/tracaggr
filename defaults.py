# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, UNICODE, UNICODEARRAY

psycopg2.extensions.register_type(UNICODE)
psycopg2.extensions.register_type(UNICODEARRAY)

# Trac databases
TRAC_DATA = (
    {'name': 'Name_1', 'base_url': 'http://example.com/trac',
     'host': 'host1', 'port': 5432,
     'database': 'TracDB', 'user': 'tracuser'},
)

# list of developers
DEVS = {
        'johndoe': 'John Doe',
        }

# interface where development/debug server would run
DEBUG_HOST = '127.0.0.1'
# name of field in Trac database where dates are stored
DATE_FIELD = 'due_date'
# format of that filed
DATEFORMAT = '%d.%m.%Y'

# load mandatory settings
try:
    # SECRET_KEY should be `str` or `bytes` when unicode_literals are used
    from settings import TRAC_DATA, DEVS, SECRET_KEY
except ImportError:
    print("Problem importing settings, expect troubles")

# load optional settings
try:
    from settings import *
except ImportError:
    pass

DEVLIST = DEVS.items()
DEVLIST.sort(cmp=lambda x,y: cmp(x[1], y[1]))

# query to fetch month data (with DATE_FIELD set)
QUERY_MONTH = """SELECT ticket.id, ticket.owner, ticket.summary,
                        ticket.reporter, ticket.status, ticket.time,
                        ticket_custom.value AS due_date
                FROM ticket INNER JOIN ticket_custom
                ON ticket.id = ticket_custom.ticket
                WHERE ticket_custom.name='{0}' AND
                    ticket_custom.value ILIKE %s""".format(DATE_FIELD)

# query to fetch tickets closed this month without DATE_FIELD set
QUERY_UNSET_DATE = """SELECT DISTINCT ON (ticket.id)
                            ticket.id, ticket.owner, ticket.time,
                            ticket.summary, ticket.reporter,
                            ticket_change.time AS closed_at
                        FROM ticket INNER JOIN ticket_change
                            ON ticket.id = ticket_change.ticket
                        INNER JOIN ticket_custom
                            ON ticket.id = ticket_custom.ticket
                        WHERE ticket_change.field='status' AND
                            ticket_change.newvalue='closed' AND
                            ticket_custom.name='{0}' AND
                            ticket_custom.value='' AND
                            ticket_change.time>=%s AND
                            ticket_change.time<=%s
                        ORDER BY ticket.id, ticket_change.time DESC;
                    """.format(DATE_FIELD)

# query to fetch open tickets and first due_date ever assigned to them
QUERY_OPEN = """SELECT DISTINCT ON (ticket.id) id, owner, summary, reporter, ticket.time,
                       COALESCE(ticket_change.oldvalue, ticket_custom.value, '')
                                AS first_due_date
                FROM ticket
                    LEFT JOIN ticket_custom ON
                        (ticket.id=ticket_custom.ticket AND
                         ticket_custom.name='{0}')
                    LEFT JOIN ticket_change ON
                        (ticket.id = ticket_change.ticket AND
                         ticket_change.field='{0}' AND
                         ticket_change.oldvalue!='')
                WHERE ticket.status!='closed'
                ORDER BY ticket.id, ticket_change.time ASC
                """.format(DATE_FIELD)
# query to fetch tickets close not earlier than a week ago
QUERY_CLSD_WEEK = """SELECT id, owner, summary,reporter, time FROM ticket
                     WHERE status='closed' AND changetime>%s"""

# prepare list of Tracs with database connections
TRACS = []
for trac in TRAC_DATA:
    TRACS.append({'name': trac.pop('name'), 'base_url': trac.pop('base_url'),
                  'conn': psycopg2.connect(**trac)})
    TRACS[-1]['conn'].set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    TRACS[-1]['conn'].set_client_encoding('utf-8')

# remove not to import them
del trac, TRAC_DATA, DATE_FIELD
del ISOLATION_LEVEL_AUTOCOMMIT, UNICODE, UNICODEARRAY
