#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import calendar
import datetime

from psycopg2.extras import DictCursor
from flask import Flask, abort, redirect, render_template, session
app = Flask(__name__)

from defaults import *
from utils import dictify

def other_colour(colour):
    return 'dark' if colour == 'light' else 'light'

@app.route("/")
@app.route('/<int:month>/')
@app.route('/<int:month>/<int:year>/')
def index(month=None, year=None):
    ''' Displays calendars and lists of open/recently closed tickets '''
    stylesheet = session.get('css', 'light')
    other_ssheet = other_colour(stylesheet)
    # prepare search string, with today as default
    basedate = datetime.date.today()
    replace_dict = {'day': 1}
    if month is not None:
        replace_dict['month'] = month
    if year is not None:
        replace_dict['year'] = year
    try:
        basedate = basedate.replace(**replace_dict)
    except ValueError:
        #TODO: prettify 404, add info
        abort(404)
    del replace_dict
    monthstr = basedate.strftime("%%.%m.%Y")

    month_data, month_data_raw = {}, {}
    for trac in TRACS:
        ## query Trac databases
        # for month data
        cur = trac['conn'].cursor(cursor_factory=DictCursor)
        cur.execute(QUERY_MONTH, (monthstr, ))
        month_data_raw = dictify(cur.fetchall(), 'owner',
                             dict2up=month_data_raw,
                             add_data={'trac': trac['name'],
                                       'base_url': trac['base_url']})
        # for open tickets
        cur.execute(QUERY_OPEN)
        opened = dictify(cur.fetchall(), 'owner',
                             add_data={'trac': trac['name'],
                                       'base_url': trac['base_url']})
    # total dictification of month data
    for user, tickets in month_data_raw.items():
        month_data[user] = dictify(tickets, 'due_date')
        for due_date in month_data[user].keys():
            tickets = month_data[user].pop(due_date)
            month_data[user][due_date] = dictify(tickets, 'trac')
    # a wee bit of simple dictification for opened tickets
    for user, tickets in opened.items():
        opened[user] = dictify(tickets, 'trac')

    # create calendars
    calendar.setfirstweekday(calendar.MONDAY)
    cal_year = year
    month, year = (basedate.month, basedate.year)
    context = {
               'devs': DEVS,
               'month_data': month_data,
               'calendar': calendar.monthcalendar(year, month),
               'weekhdr': calendar.weekheader(3).split(' '),
               'stylesheet': stylesheet,
               'other_ssheet': other_ssheet,
               'daytmpl': monthstr.replace('%', '%02d'),
               'month_name': calendar.month_name[month],
               'month': month,
               'year': cal_year,
               'opened': opened,
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

