import email
import os
import sys
from unicodedata import name
import subprocess
from helpers import login_required, apology
import logging
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from threading import Event
import signal
import pyodbc
import pysftp
import pandas as pd

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
    app.debug = True
    app.run()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
#     consumes the users' data and renders it onto the index page
       # DB CONFIG for index
        server = 'hk-mc-fc-data.database.windows.net'
        database = 'hk-mc-fc-data-training'
        username = 'server_admin'
        password = 'Pa$$w0rd'
        cxnx = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
        cursor = cxnx.cursor()

        sql = f"SELECT * FROM  WHERE email = '{session.get('info')[4]}'"
        myinfo = cursor.execute(sql).fetchone()

        return render_template("index.html", myinfo=myinfo)
    
#     Posting to the database for buying
    if request.method == "POST":
#       consumes and then produces to the next stream
        consumer = os.chmod("/client/producer.py", 644)
        customer = subprocess.call('producer.main()', stdout='/client/getting_started.ini')
        
        flash("Bought!")
        return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    server = 'hk-mc-fc-data.database.windows.net'
    database = 'hk-mc-fc-data-training'
    username = 'server_admin'
    password = 'Pa$$w0rd'
    cxnx = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cursor = cxnx.cursor()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Remember which user has logged in
        email = request.form.get("email")
        #session['email'] = request.form['email_address']

        # Ensure username was submitted
        if not email:
            return apology("must provide email")

        # Query database for username
        sql_query = f"SELECT * FROM dbo.customers WHERE email = '{request.form.get('email')}'"
        rows = cursor.execute(sql_query).fetchall()
        
        if len(rows) != 1:
            return apology("No account found.")

        print(rows)
        session['info'] = rows[0]
        session['user_id'] = rows[0][0]

        cursor.close()
        cxnx.close ()
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
        session['email'] = str(request.form.get("email"))
        gender = request.form.get("gender")
        dob = request.form.get("dob")
        country = request.form.get("country")
        smoking_status = request.form.get("smoking_status")
      
        server = 'hk-mc-fc-data.database.windows.net'
        database = 'hk-mc-fc-data-training'
        username = 'server_admin'
        password = 'Pa$$w0rd'
        cxnx = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        cursor = cxnx.cursor()

        # Validate submission; ensure username was submitted
        if not email:
            return apology("Input email please.")

         # Check if login information is already taken
        try:
            sql3 = f"INSERT INTO dbo.customers (email, name) VALUES(?, ?), email = '{request.form.get('email')}', name = '{request.form.get('name')}'"
            id = cursor.execute(sql3)
            cxnx.commit()
        except ValueError:
            return apology("username taken")

        # Log user in
        session["user_id"] = id

        # Let user know they're registered
        flash("Registered!")

        # Insert the new login information from register into the users table
        sql = f"INSERT INTO dbo.customers (email, name, gender, dob, country, smoking_status) VALUES (?, ?, ?, ?, ?), email = session['email'], name = '{request.form.get('name')}, dob = '{request.form.get('dob')}, gender = '{request.form.get('gender')}, smoking_status = '{request.form.get('smoking_status')}"
        rows = cursor.execute(sql)
    
        # Push to the database
        cxnx.commit()
       
        session["email"] = rows

    # Confirm registration
        return redirect("/")

    else:
        return render_template("register.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)
