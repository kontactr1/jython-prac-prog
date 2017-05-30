from flask import Flask
from __init__ import app
from wiki_info import *
from flask import url_for


@app.route("/")
def home_page():
    return """<html>
                <head>
                    <title>My new page</title>
                </head>
                <body>
                    <h1>Welcome to my page</h1>
                    <a href='""" + url_for("page_re") + """'>enter to vanity url </a>
                </body>
              </html>"""


@app.route("/page_re")
def page_re():
    return "Enter data in url"

@app.route("/page_re/<title>")
def create_vanity_url(title):
    return url_carw(title)
