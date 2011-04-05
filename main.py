#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extras import DictCursor

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

from flask import Flask, render_template
app = Flask('TracAggr')

# Trac databases
TRAC_DATA = (
    {'name': 'Name_1', 'host': 'host1', 'port': 5432,
     'database': 'TracDB', 'user': 'tracuser'},
)

# list of developers
DEVS = (
        ('John Doe', 'johndoe'),
        )

# load local settings
try:
    from settings import TRAC_DATA, DEVS
except ImportError:
    print("Settings not found")

# query to fetch open tickets
QUERY_OPEN = "SELECT id, owner FROM ticket WHERE status!='closed'"
# query to fetch month data
QUERY_MONTH = """SELECT ticket.id AS ticket,
                ticket.owner, ticket_custom.value AS due_date
                FROM ticket INNER JOIN ticket_custom
                ON ticket.id = ticket_custom.ticket
                WHERE ticket_custom.name='due_date' AND
                    ticket_custom.value ILIKE %s"""
# query to fetch tickets close not earlier than a week ago
QUERY_CLSD_WEEK = "SELECT id, owner FROM ticket WHERE status='closed'"

# prepare dictionary of DB connections
TRACS = []
for trac in TRAC_DATA:
    TRACS.append({'name': trac.pop('name'), 'conn': psycopg2.connect(**trac)})
    TRACS[-1]['conn'].set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# sort developer list
DEVS.sort(cmp=lambda x,y: cmp(x[0], y[0]))

@app.route("/")
def index():
    ''' Displays calendars and lists of open/recently closed tickets '''
    month_data = {}
    # prepare search string
    todaystr = datetime.date.today().strftime("%%-%m-%Y")
    for trac in TRACS:
        # query Trac databases
        cur = trac['conn'].cursor(cursor_factory=DictCursor)
        cur.execute(QUERY_MONTH, (todaystr, ))
        for row in cur.fetchall():
            # append row to one of per-owner lists
            owners_list = month_data.get(row['owner'])
            if owners_list is None:
                month_data[row['owner']] = []
            ticket_data = {'trac': trac['name'],
                           'no': row['ticket'],
                           'due_date': row['due_date']
                           }
            month_data[row['owner']].append(ticket_data)
    return render_template('index.html', month_data=month_data, devs=DEVS)

if __name__ == "__main__":
    app.run(debug=True)
