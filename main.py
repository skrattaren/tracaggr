#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import calendar
import datetime
import time

from psycopg2.extras import DictCursor
from flask import Flask, abort, redirect, render_template, session
app = Flask(__name__)

from defaults import *
from utils import dictify, get_tckt_title

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
    today = datetime.date.today()
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
    if today.month == basedate.month and today.year == basedate.year:
        today_day = today.day
    else:
        today_day = None
    del replace_dict
    monthstr = basedate.strftime(DATEFORMAT.replace("%d", "%%"))

    # determine next month/year if they are somewhat special
    next_month = basedate.month + 1
    prev_month = basedate.month - 1
    next_year, prev_year = '', ''

    if basedate.month == 12:
        next_month = 1
        next_year = basedate.year + 1
    elif basedate.month == 1:
        prev_month = 12
        prev_year = basedate.year - 1

    # calculate timestamp boundaries of the month
    clsd_after = calendar.timegm(
                      (basedate.year, basedate.month, 1) + (0,) * 3) * (10**6)
    clsd_before = calendar.timegm(
                      (next_year or basedate.year, next_month, 1) + (0,) * 3
                                 ) * (10**6)

    month_data, month_data_raw, opened, closed = ({}, ) * 4
    for trac in TRACS:
        ## query Trac databases
        # for month data
        cur = trac['conn'].cursor(cursor_factory=DictCursor)
        cur.execute(QUERY_MONTH, (monthstr, ))
        month_data_raw = dictify(cur.fetchall(), 'owner',
                             dict2up=month_data_raw,
                             add_data={'trac': trac['name'],
                                       'base_url': trac['base_url']})
        # query for due_date'less tickets closed on this month
        cur.execute(QUERY_UNSET_DATE, (clsd_after, clsd_before))
        for tckt in cur.fetchall():
            # add ticket to corresponding list of owner's tickets
            owner = tckt['owner']
            # convert timestamp-like ticket.time to `due_date`
            due_date = datetime.date.fromtimestamp(tckt['closed_at'] // (10**6))
            due_date = due_date.strftime(DATEFORMAT)
            user_tckt_list = month_data_raw.get(owner, [])
            user_tckt_list.append({'id': tckt['id'],
                                   'due_date': due_date,
                                   'summary': tckt['summary'],
                                   'time': tckt['time'],
                                   'reporter': tckt['reporter'],
                                   'status': 'closed',
                                   'trac': trac['name'],
                                   'base_url': trac['base_url']})
            month_data_raw['owner'] = user_tckt_list

        # for open tickets
        cur.execute(QUERY_OPEN)
        opened = dictify(cur.fetchall(), 'owner',
                             dict2up=opened,
                             add_data={'trac': trac['name'],
                                       'base_url': trac['base_url']})
        # for recently closed tickets
        week_ago = (time.time() - 604800) * (10**6)   # (7 * 24 * 60 * 60) = 604800
        cur.execute(QUERY_CLSD_WEEK, (week_ago, ))
        closed = dictify(cur.fetchall(), 'owner',
                             dict2up=closed,
                             add_data={'trac': trac['name'],
                                       'base_url': trac['base_url']})

    # total dictification of month data
    for user, tickets in month_data_raw.items():
        for ticket in tickets:
            ##TODO: do it within utils.dictify (pass function in add_data)
            ticket['title'] = get_tckt_title(ticket)
        month_data[user] = dictify(tickets, 'due_date')
        for due_date in month_data[user].keys():
            tickets = month_data[user].pop(due_date)
            month_data[user][due_date] = dictify(tickets, 'trac')

    # a wee bit of simple dictification for opened tickets
    for user, tickets in opened.items():
        for ticket in tickets:
            ##TODO: do it within utils.dictify (pass function in add_data)
            if not ticket['first_due_date']:
                continue
            first_due_date = time.strptime(ticket['first_due_date'], DATEFORMAT)
            first_due_date = datetime.date(first_due_date.tm_year,
                                           first_due_date.tm_mon,
                                           first_due_date.tm_mday)
            delay = today - first_due_date
            if delay.days > 0:
                ticket['delayed_by'] = str(delay.days)
            else:
                ticket['delayed_by'] = ''
        opened[user] = dictify(tickets, 'trac')

    # ...and for closed ones
    for user, tickets in closed.items():
        closed[user] = dictify(tickets, 'trac')

    # create calendars
    calendar.setfirstweekday(calendar.MONDAY)
    cal_year = year
    month, year = (basedate.month, basedate.year)
    context = {
               'devs': DEVLIST,
               'devlist': DEVS,
               'month_data': month_data,
               'next_month': next_month,
               'next_year': next_year,
               'prev_month': prev_month,
               'prev_year': prev_year,
               'calendar': calendar.monthcalendar(year, month),
               'weekhdr': calendar.weekheader(3).split(' '),
               'stylesheet': stylesheet,
               'other_ssheet': other_ssheet,
               'daytmpl': monthstr.replace('%', '%02d'),
               'month_name': calendar.month_name[month],
               'month': month,
               'year': cal_year,
               'today': today_day,
               'opened': opened,
               'closed': closed,
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

