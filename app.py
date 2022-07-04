import os
import sys

from helpers import login_required, apology
import logging
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from threading import Event
import signal
import pypyodbc as pyodbc
import pysftp
import pandas as pd

server = 'hk-mc-fc-data.database.windows.net'
database = 'hk-mc-fc-data-training'
username = 'server-admin'
password = 'Pa$$w0rd'
cxnx = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cxnx.cursor()

# Configure application
app = Flask(__name__, template_folder='templates')

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.debug = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

INTERRUPT_EVENT = Event()

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = False
    app.run()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    # Show the policies ordered by latest bought
    if request.method.get == "POST":
        sql = "SELECT * FROM dbo.customers"
        myinfo = pd.read_sql(sql)

    return render_template("index.html", myinfo=myinfo)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy policies"""
    if request.method == "POST":

        # Input desired plan
        name = request.form.get("Name")
        type = request.form.get("Type")
        category = request.form.get("Category")

        # If no symbols are inputted
        if not name or not type or not category:
            return apology("Missing field")

      #  Query the product database for the policies that can be bought
        policyP = cursor.execute("SELECT * FROM fwd_poc.products WHERE type = :type", type=type)
       # Error check for search result
        if not policyP:
            apology("Policy does not exist")

        typ = policyP[0]["Type"]

       # Update stream with the new buyer information
        results = cursor.api_client.inserts_stream("my_stream_name", typ=typ, use_http2=True)

        # FIX ABOVE

        flash("Bought!")
        return redirect("/")

    else:
        return render_template("buy.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        email = request.form.get("email")

        # Ensure username was submitted
        if not email:
            return apology("must provide email", 403)

        # Query database for username
        rows = cursor.execute("SELECT * FROM users WHERE username = email", request.form.get("email"), use_http2=True)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Make sure that the users reached routes via POST
    if request.method == "POST":
        email = str(request.form.get("email"))
        name = str(request.form.get("name"))

        # Validate submission; ensure username was submitted
        if not email:
            return apology("Input email please.")

         # Check if login information is already taken
        try:
            id = cursor.execute("INSERT INTO dbo.customers (email, name) VALUES(?, ?)",
                            request.form.get("email"), request.form.get("email"))
        except ValueError:
            return apology("username taken")

        # Log user in
        session["user_id"] = id

        # Let user know they're registered
        flash("Registered!")

        # Insert the new login information from register into the users table
        rows = cursor.api_client.inserts_stream("my_stream_name", email, name, session["user_id"])
        session["user_id"] = rows

    # Confirm registration
        return redirect("/")

    else:
        return render_template("register.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

cursor.close()
