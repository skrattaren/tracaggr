#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import calendar
import datetime

from psycopg2.extras import DictCursor
from flask import Flask, redirect, render_template, session
app = Flask(__name__)

from defaults import *
from utils import dictify

def other_colour(colour):
    return 'dark' if colour == 'light' else 'light'

@app.route("/")
def index():
    ''' Displays calendars and lists of open/recently closed tickets '''
    stylesheet = session.get('css', 'light')
    other_ssheet = other_colour(stylesheet)
    # prepare search string
    today = datetime.date.today()
    monthstr = today.strftime(DATEFORMAT.replace('%d', '%%'))

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
        for due_date in month_data[user].keys():
            tickets = month_data[user].pop(due_date)
            month_data[user][due_date] = dictify(tickets, 'trac')

    # create calendars
    month, year = (today.month, today.year)
    calendar.setfirstweekday(calendar.MONDAY)
    context = {
               'devs': DEVS,
               'month_data': month_data,
               'calendar': calendar.monthcalendar(year, month),
               'weekhdr': calendar.weekheader(3).split(' '),
               'stylesheet': stylesheet,
               'other_ssheet': other_ssheet,
               'daytmpl': monthstr.replace('%', '%02d')
               }
    return render_template('index.html', **context)

@app.route("/toggle-css/")
def toggle_css():
    ''' Toggles dark stylesheet to light and vice versa '''
    stylesheet = session.get('css', 'light')
    session['css'] = other_colour(stylesheet)
    session.permanent = True
    return redirect('/')

app.secret_key = SECRET_KEY

if __name__ == "__main__":
    app.run(host=DEBUG_HOST, debug=True)

