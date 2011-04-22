# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, UNICODE, UNICODEARRAY
from psycopg2.extras import DictCursor

psycopg2.extensions.register_type(UNICODE)
psycopg2.extensions.register_type(UNICODEARRAY)

# Trac databases
TRAC_DATA = (
    {'name': 'Name_1', 'base_url': 'http://example.com/trac',
     'host': 'host1', 'port': 5432,
     'database': 'TracDB', 'user': 'tracuser'},
)

# list of developers
DEVS = (
        ('John Doe', 'johndoe'),
        )

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

# query to fetch open tickets
QUERY_OPEN = "SELECT id, owner FROM ticket WHERE status!='closed'"
# query to fetch month data
QUERY_MONTH = """SELECT ticket.id, ticket.owner, ticket.summary,
                        ticket.status, ticket_custom.value AS due_date
                FROM ticket INNER JOIN ticket_custom
                ON ticket.id = ticket_custom.ticket
                WHERE ticket_custom.name='{0}' AND
                    ticket_custom.value ILIKE %s""".format(DATE_FIELD)

# query to fetch tickets close not earlier than a week ago
QUERY_CLSD_WEEK = "SELECT id, owner FROM ticket WHERE status='closed'"

# prepare dictionary of DB connections
TRACS = []
for trac in TRAC_DATA:
    TRACS.append({'name': trac.pop('name'), 'base_url': trac.pop('base_url'),
                  'conn': psycopg2.connect(**trac)})
    TRACS[-1]['conn'].set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    TRACS[-1]['conn'].set_client_encoding('utf-8')

# remove not to import them
del trac, TRAC_DATA, DATE_FIELD
del ISOLATION_LEVEL_AUTOCOMMIT, UNICODE, UNICODEARRAY, DictCursor

# sort developer list
DEVS.sort(cmp=lambda x,y: cmp(x[0], y[0]))

