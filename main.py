#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import Flask, render_template
app = Flask('TracAggr')

@app.route("/")
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
