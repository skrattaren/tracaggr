#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

from flask import Flask, render_template
app = Flask('TracAggr')

TRAC_DATA = (
    {'name': 'Name_1', 'host': 'host1', 'port': 5432,
     'database': 'TracDB', 'user': 'tracuser'},
)

try:
    from settings import TRAC_DATA
except ImportError:
    print("Settings not found")

QUERY = "SELECT id, owner FROM ticket WHERE status!='closed'"

# prepare dictionary of DB connections
TRACS = []
for trac in TRAC_DATA:
    TRACS.append({'name': trac.pop('name'), 'conn': psycopg2.connect(**trac)})
    TRACS[-1]['conn'].set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

@app.route("/")
def index():
    result = {}
    for trac in TRACS:
        cur = trac['conn'].cursor()
        cur.execute(QUERY)
        result[trac['name']] = cur.fetchall()
    return render_template('index.html', data=result)

if __name__ == "__main__":
    app.run(debug=True)
