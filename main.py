#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import calendar
import datetime

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, UNICODE, UNICODEARRAY
from psycopg2.extras import DictCursor

psycopg2.extensions.register_type(UNICODE)
psycopg2.extensions.register_type(UNICODEARRAY)

from flask import Flask, render_template
app = Flask('TracAggr')

from utils import dictify

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

# load local settings
try:
    from settings import TRAC_DATA, DEVS
except ImportError:
    print("Settings not found")

# query to fetch open tickets
QUERY_OPEN = "SELECT id, owner FROM ticket WHERE status!='closed'"
# query to fetch month data
QUERY_MONTH = """SELECT ticket.id, ticket.owner, ticket.summary,
                        ticket_custom.value AS due_date
                FROM ticket INNER JOIN ticket_custom
                ON ticket.id = ticket_custom.ticket
                WHERE ticket_custom.name='due_date' AND
                    ticket_custom.value ILIKE %s"""
# query to fetch tickets close not earlier than a week ago
QUERY_CLSD_WEEK = "SELECT id, owner FROM ticket WHERE status='closed'"

# prepare dictionary of DB connections
TRACS = []
for trac in TRAC_DATA:
    TRACS.append({'name': trac.pop('name'), 'base_url': trac.pop('base_url'),
                  'conn': psycopg2.connect(**trac)})
    TRACS[-1]['conn'].set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    TRACS[-1]['conn'].set_client_encoding('utf-8')

# sort developer list
DEVS.sort(cmp=lambda x,y: cmp(x[0], y[0]))

@app.route("/")
def index():
    ''' Displays calendars and lists of open/recently closed tickets '''
    # prepare search string
    today = datetime.date.today()
    monthstr = today.strftime("%%.%m.%Y")

    month_data, month_data_raw = {}, {}
    for trac in TRACS:
        # query Trac databases
        cur = trac['conn'].cursor(cursor_factory=DictCursor)
        cur.execute(QUERY_MONTH, (monthstr, ))
        month_data_raw = dictify(cur.fetchall(), 'owner',
                             dict2up=month_data_raw,
                             add_data={'trac': trac['name'],
                                       'base_url': trac['base_url']})
    for user, tickets in month_data_raw.items():
        month_data[user] = dictify(tickets, 'due_date')
    # create calendars
    month, year = (today.month, today.year)
    calendar.setfirstweekday(calendar.MONDAY)
    cal = calendar.monthcalendar(year, month)
    return render_template('index.html', devs=DEVS,
                                         month_data=month_data,
                                         calendar=cal,
                                         daytmpl=monthstr.replace('%', '%02d'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
