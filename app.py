import os
import sys

from helpers import login_required, apology
import logging
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_kafka import FlaskKafka
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from threading import Event
# import signal
import pyodbc
import pysftp
import pandas as pd

server = 'hk-mc-fc-data.database.windows.net'
database = 'hk-mc-fc-data-training'
username = 'server-admin'
password = 'Pa$$w0rd'
cxnx = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cxnx.cursor()

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.debug = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

INTERRUPT_EVENT = Event()

# def get_kafka_producer():
#     return Producer({'sasl.mechanisms':'PLAIN',
#                      'request.timeout.ms': 20000,
#                      'bootstrap.servers':'pkc-epwny.eastus.azure.confluent.cloud:9092',
#                      'retry.backoff.ms':500,
#                      'sasl.username':'IHO7XVPCJCCBZAYX',
#                      'sasl.password':'UAwjmSIn5xuAL7HZmBjU4NGt0nLfXbyjtlVA7imgCdGBYFkog5kw0gc4e5MYmiUE',
#                      'security.protocol':'SASL_SSL'})

logging.basicConfig(level=logging.DEBUG)

# Create a Kafka Producer
# producer=get_kafka_producer()

# client = FlaskKafka(INTERRUPT_EVENT,
#                  bootstrap_servers=",".join(["localhost:9092"]),
#                  group_id="consumer-grp-id"
#                  )

# # update this
# @client.handle('customers')
# def test_topic_handler(msg):
#     print("consumed {} from test-topic".format(msg))

# def listen_kill_server():
#     signal.signal(signal.SIGTERM, client.interrupted_process)
#     signal.signal(signal.SIGINT, client.interrupted_process)
#     signal.signal(signal.SIGQUIT, client.interrupted_process)
#     signal.signal(signal.SIGHUP, client.interrupted_process)
# run the app.

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

        Name = request.form.get("Name")
        startdate = request.form.get("startdate")
        dob = request.form.get("dob")
        email = request.form.get("email")
        gender = request.form.get("gender")
        premium = request.form.get("premium")
        policytype = request.form.get("policytype")

        # If no symbols are inputted
        if not Name or not startdate or not dob or not email or not gender or not premium or not policytype:
            return apology("Missing field")

      #  Query the users database for the users, product database for the policy
        users = cursor.execute("SELECT * FROM fwd_poc.products WHERE name=Name")
        policyP = cursor.execute("SELECT * FROM fwd_poc.products WHERE id = :id", id=id)
       # Error check for search result
        if not users:
            apology("Invalid user information")
        if not policyP:
            apology("Invalid policy information")

        typ = policyP[0]["Type"]
        inputtype = users[0]["policytype"]

       # Update stream with the new buyer information
        results = cursor.api_client.inserts_stream("my_stream_name", users=users, use_http2=True)
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

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = cursor.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"), use_http2=True)

        # Ensure username exists and password is correct
        if len(rows) != 1:
            return apology("invalid username and/or password", 403)

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
        new_username = str(request.form.get("username"))
        password = str(request.form.get("password"))
        confirmation = str(request.form.get("confirmation"))

        # Validate submission; ensure username was submitted
        if not new_username:
            return apology("Invalid username")

        if not password or not confirmation:
            return apology("Invalid password")

        if password != confirmation:
            return apology("Passwords don't match")

         # Add user to database
        try:
            id = cursor.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
                            request.form.get("username"),
                            (request.form.get("password")))
        except ValueError:
            return apology("username taken")

        # Log user in
        session["user_id"] = id

        # Let user know they're registered
        flash("Registered!")

        # Insert the new login information from register into the users table
        rows = cursor.api_client.inserts_stream("my_stream_name", password, new_username, session["user_id"])
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
