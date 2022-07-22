import email
import producer

import os
import sys

from numpy import double
from pytz import country_names
import producer
from unicodedata import name
from subprocess import call
from helpers import login_required, apology
import logging
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from threading import Event
import pyodbc


# Configure application
app = Flask(__name__, template_folder='templates')

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.debug = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

premium_structure = "Premium is varied by factors including but not limited to " \
                    "Insured's age, gender, smoking habit, health..."
policy_description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " \
                      "In sed massa sed dui faucibus vestibulum in quis urna. Ut tristique."
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
        # server = 'hk-mc-fc-data.database.windows.net'
        # database = 'hk-mc-fc-data-training'
        # username = 'server_admin'
        # password = 'Pa$$w0rd'
        # cxnx = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
        # cursor = cxnx.cursor()

        # Select customer information to load
        # sql = f"SELECT * FROM dbo.Customer WHERE email = '{session.get('info')[4]}'"

        # myinfo = cursor.execute(sql).fetchone()

        # Close cursor and connection after select query
        # cursor.close()
        # cxnx.close()
        flash("Welcome back!")
        return render_template("index.html")
        # , myinfo=myinfo)
    
#     Posting to the database for buying
    if request.method == "POST":
#       server = 'hk-mc-fc-data.database.windows.net'
        # database = 'hk-mc-fc-data-training'
        # username = 'server_admin'
        # password = 'Pa$$w0rd'
        # cxnx = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
        # cursor = cxnx.cursor()
        # # Insert customer information into KSQLDB 
        # sql= f"INSERT INTO dbo.policydraft (name, term, type, customeremail, premiumpayment,premiumstructure, description, currency, policystatus) VALUES " \
        #      f"('{request.form.get('name')}', '{request.form.get('term')}', '{request.form.get('type')}', '{session.get('info')[4]}', " \
        #      f"'{request.form.get('premiumpayment')}', '{request.form.get('premiumstructure')}', '{request.form.get('desc')}', 'HKD', 'Draft')"
        # # Execute changes
        # results = cursor.execute(sql)
        # # Commit changes to db
        # cxnx.commit()

        # # Close connector to db
        # cursor.close()
        # cxnx.close()
        
        flash("Congratulations! You've bought a new Policy.", category='success')
        return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()
    
    # Set up connection to kSQLDB 
    # server = 'hk-mc-fc-data.database.windows.net'
    # database = 'hk-mc-fc-data-training'
    # username = 'server_admin'
    # password = 'Pa$$w0rd'
    # cxnx = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    # cursor = cxnx.cursor()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Remember which user has logged in
        email = request.form.get("email")
        #session['email'] = request.form['email_address']

        # Ensure username was submitted
        if not email:
            return apology("must provide email")

        j = "john@example.com"
      
        # Check user
        if str(email) == j:
            session['user_id'] = j  
        # Log user in
        session["user_id"] = j
        
        # Query database for email
        # sql_query = f"SELECT * FROM dbo.customers WHERE email = '{request.form.get('email')}'"
        # rows = cursor.execute(sql_query).fetchall()
        
        # If there are 0 or more accounts with the same email address
        # if len(rows) != 1:
        #     return apology("No account found.")

        # Save information in session variable
        # session['info'] = rows[0]
        # session['user_id'] = rows[0][0]

        # cursor.close()
        # cxnx.close ()
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
      
        # server = 'hk-mc-fc-data.database.windows.net'
        # database = 'hk-mc-fc-data-training'
        # username = 'server_admin'
        # password = 'Pa$$w0rd'
        # cxnx = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        # cursor = cxnx.cursor()

        # Validate submission; ensure username was submitted
        if not email:
            return apology("Input email please.")

         # Check if login information is already taken
        # try:
        #     sql3 = f"INSERT INTO dbo.customers (email, name) VALUES(?, ?), email = '{request.form.get('email')}', name = '{request.form.get('name')}'"
        #     id = cursor.execute(sql3)
        #     cxnx.commit()
        # except ValueError:
        #     return apology("username taken")
        

        # Let user know they're registered
        flash("Registered!")

        # Insert the new login information from register into the users table
        # sql = f"INSERT INTO dbo.customers (email, name, gender, dob, country, smoking_status) VALUES (?, ?, ?, ?, ?), email = session['email'], name = '{request.form.get('name')}, dob = '{request.form.get('dob')}, gender = '{request.form.get('gender')}, smoking_status = '{request.form.get('smoking_status')}"
        # rows = cursor.execute(sql)
    
        # # Push to the database
        # cxnx.commit()
       
        # session["email"] = rows

    # Confirm registration
        return redirect("/")

    else:
        return render_template("register.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)
