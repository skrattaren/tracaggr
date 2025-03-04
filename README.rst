====================================
TracAggregator documentation
====================================

:Author: Nikolaj Sjujskij (Николай Шуйский)

Description
-----------

TracAggregator is a simple Flask webapp inspired by WikiTicketCalendarMacro_.
It "aggregates" multiple Trac_ environments (only PostgreSQL_-powered
at the moment), displaying neat calendars for each developer with tickets
bound to days.

Thanks to Maria Osipenko (Мария Осипенко) for CSS work

The work is released under the GPLv3 license (see ``LICENSE`` file).

.. _WikiTicketCalendarMacro: http://trac-hacks.org/wiki/WikiTicketCalendarMacro
.. _Trac: http://trac.edgewall.com/
.. _PostgreSQL: http://www.postgresql.org/

Requirements
------------

* Python_ >= 2.6
* Flask_ >= 0.6
* Psycopg2_

.. _Python: http://python.org/
.. _Flask: http://flask.pocoo.org/
.. _Psycopg2: http://initd.org/psycopg/

Quickstart
----------
1. Create ``settings.py`` for storing your settings. Use ``unicode_literals``
2. Define ``TRAC_DATA, DEVS, SECRET_KEY`` (obligatory) and ``DEBUG_HOST``,
   ``DATEFORMAT``, ``DATE_FIELD`` (optional) variables there.
   See ``defaults.py`` file for syntax and samples
3. Tickets are expected to have custom field ``due_date`` with date in format
   "``%d.%m.%Y``" there (DateFieldPlugin_ suggested; see 2 for tuning)
4. Run
   ``$ python main.py``
5. Deploy with uWSGI_/mod_wsgi_

.. _DateFieldPlugin: http://trac-hacks.org/wiki/DateFieldPlugin
.. _uWSGI: http://projects.unbit.it/uwsgi/
.. _mod_wsgi: http://code.google.com/p/modwsgi/

