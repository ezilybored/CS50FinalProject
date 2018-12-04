#import os
#import requests

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
#from flask_socketio import SocketIO, emit
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

# helpers.py
from helpers import login_required

# Configure application
app = Flask(__name__)
# Configures Socket I/
#app.config['SECRET_KEY'] = 'secret!'
#socketio = SocketIO(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
# Flask prefers the use of cookies normally
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database set as adventure.db
db = SQL("sqlite:///adventure.db")

"""This section of code relates to the user registration and login/out processes"""

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            return render_template("error.html")

        password = request.form.get("password")
        get_newuser = request.form.get("username")
        get_dob = request.form.get("dob")
        get_email = request.form.get("email")
        get_twitter = request.form.get("twitter")

        print("Date = ", get_dob)

        # Checks to see if the username already exists
        check = db.execute("SELECT * FROM users WHERE username = :username",
                          username=get_newuser)
        if check:
            return render_template("error.html", error = "Username already exists")

        insert = db.execute("INSERT INTO users (username, password, twitter, email, date_of_birth) VALUES (:username, :password, :twitter, :email, :date_of_birth)",
                            username=get_newuser,
                            # This generates the hash of the inputted password
                            password=generate_password_hash(request.form.get("password")),
                            twitter=get_twitter,
                            email=get_email,
                            date_of_birth=get_dob)

        if not insert:
            return render_template("error.html", error = "Failed user entry")

        session["user_id"] = insert

        db.execute("UPDATE users SET date_of_registration = currentdate WHERE userid = :userid",
                    userid=session["user_id"])

        session["admin"] = db.execute("SELECT * FROM users WHERE userid = :userid AND admin = :admin",
                           userid=session["user_id"],
                           admin="true")

        if not session["admin"]:
            return redirect("/")

    else:
        return render_template("register.html")


@app.route("/regcheck", methods=["GET", "POST"])
def regcheck():
    """Allows the site to check whether a particular username has been taken yet"""

    username = request.form.get("username")
    print(username)
    user = db.execute("SELECT username FROM users WHERE username = :username",
                          username=username)
    if not user:
        t = jsonify({"success": True})
        return t
    else:
        f = jsonify({"success": False})
        return f


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()

    if request.method == "POST":
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct using check_password_hash from werkzeug.security
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return render_template("error.html", error = "username or password are incorrect")

        session["user_id"] = rows[0]["userid"]

        session["admin"] = db.execute("SELECT * FROM users WHERE userid = :userid AND admin = :admin",
                           userid=session["user_id"],
                           admin="true")

        if not session["admin"]:
            return redirect("/")

        else:
            return redirect("/admin")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    session.clear()

    return redirect("/")


"""This section of code relates to the users pages"""


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    """The main home page of the website"""

    db.execute("UPDATE posts SET current_date = current_date")
    topost = db.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 1")

    current = datetime.strptime(topost[0]["current_date"], '%Y-%m-%d')
    postdate = datetime.strptime(topost[0]["date_of_post"], '%Y-%m-%d')
    daydifference = 7 - (current - postdate).days

    if not session["admin"]:
        topost = db.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 1")
        selected = db.execute("SELECT selected FROM choices WHERE userid = :userid AND date = :date",
                                userid=session["user_id"],
                                date=topost[0]["date_of_post"])

        if request.method == "POST":
            if not selected and request.form.get("selection") == 'A':
                db.execute("INSERT INTO choices (userid, choice, date, selected, choiceText) VALUES (:userid, :choice, :date, :selected, :choiceText)",
                            userid=session["user_id"],
                            choice="A",
                            date=topost[0]["date_of_post"],
                            selected="true",
                            choiceText=topost[0]["optionA"])
                print("A")
            elif not selected and request.form.get("selection") == 'B':
                db.execute("INSERT INTO choices (userid, choice, date, selected, choiceText) VALUES (:userid, :choice, :date, :selected, :choiceText)",
                            userid=session["user_id"],
                            choice="B",
                            date=topost[0]["date_of_post"],
                            selected="true",
                            choiceText=topost[0]["optionB"])
                print("B")
            elif not selected and request.form.get("selection") == 'C':
                db.execute("INSERT INTO choices (userid, choice, date, selected, choiceText) VALUES (:userid, :choice, :date, :selected, :choiceText)",
                            userid=session["user_id"],
                            choice="C",
                            date=topost[0]["date_of_post"],
                            selected="true",
                            choiceText=topost[0]["optionC"])
                print("C")
            elif not selected and request.form.get("selection") == 'D':
                db.execute("INSERT INTO choices (userid, choice, date, selected, choiceText) VALUES (:userid, :choice, :date, :selected, :choiceText)",
                            userid=session["user_id"],
                            choice="D",
                            date=topost[0]["date_of_post"],
                            selected="true",
                            choiceText=topost[0]["optionD"])
                print("D")

        return render_template("index.html", text=topost)

    else:
        return render_template("index.html")


@app.route("/archive", methods=["GET", "POST"])
@login_required
def archive():
    """A history of all previous posts, essentially the story from week 1"""

    db.execute("UPDATE posts SET current_date = current_date")
    allposts = db.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 2")
    return render_template("archive.html", posts=allposts[1:2])


@app.route("/choices")
@login_required
def choices():
    """Shows the choices made by the user"""

    choicesmade = db.execute("SELECT * FROM choices WHERE userid = :userid",
                                userid=session["user_id"])

    if len(choicesmade) > 10:
        return render_template("choices.html", choices=choicesmade[0:11])
    else:
        return render_template("choices.html", choices=choicesmade)


@app.route("/votecheck", methods=["POST"])
@login_required
def votecheck():
    """Allows the site to check if the user has posted yet this week via an AJAX request"""

    topost = db.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 1")
    selected = db.execute("SELECT selected FROM choices WHERE userid = :userid AND date = :date",
                            userid=session["user_id"],
                            date=topost[0]["date_of_post"])

    if not selected:
        t = jsonify({"success": True})
        return t
    else:
        f = jsonify({"success": False})
        return f


"""This section of code relates to the admin pages"""


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    """The admin home screen that shows a running tally of the totals for each post selection for the week"""

    topost = db.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 1")

    optionA = len(db.execute("SELECT * FROM CHOICES WHERE choice=:choice", choice = "A"))
    print(optionA)
    optionB = len(db.execute("SELECT * FROM CHOICES WHERE choice=:choice", choice = "B"))
    print(optionB)
    optionC = len(db.execute("SELECT * FROM CHOICES WHERE choice=:choice", choice = "C"))
    print(optionC)
    optionD = len(db.execute("SELECT * FROM CHOICES WHERE choice=:choice", choice = "D"))
    print(optionD)

    return render_template("admin.html", A=optionA, B=optionB, C=optionC, D=optionD, text=topost)


@app.route("/users", methods=["GET", "POST"])
@login_required
def users():
    """A list of all registered users for the admin"""

    if not session["admin"]:
        return render_template("error.html", error = ("This should only be visible to an admin"))
    else:
        userslist = db.execute("SELECT * FROM users ORDER BY userid ASC LIMIT 10")
        finalid = userslist[len(userslist)-1]["userid"]
        print(finalid)

        if len(userslist) > 10:
            return render_template("users.html", users=userslist[0:10], finalid=finalid)
        else:
            return render_template("users.html", users=userslist, finalid=finalid)


@app.route("/changeUser", methods=["GET", "POST"])
@login_required
def changeUser():

    if request.form.get("Next"):
        nextusers = db.execute("SELECT * FROM users WHERE userid > :postid ORDER BY userid ASC LIMIT 10", postid=(int(request.form.get("Next"))))

        if not nextusers:
            return render_template("error.html", error = ("You have gone too far. There are no more users"))

        else:
            finalid = nextusers[len(nextusers)-1]["userid"]
            return render_template("users.html", users=nextusers, finalid=finalid)


    if request.form.get("Previous"):
        modulation = int(request.form.get("Previous")) % 10
        prevusers = db.execute("SELECT * FROM users WHERE userid > :postid ORDER BY userid ASC LIMIT 10", postid=(int(request.form.get("Previous")))-10-modulation)
        finalid = prevusers[len(prevusers)-1]["userid"]

        if not prevusers:
            return render_template("error.html", error = ("You have gone too far. There are no more users"))

        else:
            return render_template("users.html", users=prevusers, finalid=finalid)


@app.route("/newpost", methods=["GET", "POST"])
@login_required
def newpost():
    """Where the admin can create new posts"""
    anyposts = db.execute("SELECT * FROM posts")

    if not anyposts:
        if request.method == "POST":
                newpost = request.form.get("newpost")
                optionA = request.form.get("optionA")
                optionB = request.form.get("optionB")
                optionC = request.form.get("optionC")
                optionD = request.form.get("optionD")

                db.execute("INSERT INTO posts (post, optionA, optionB, optionC, optionD) VALUES (:post, :optionA, :optionB, :optionC, :optionD)",
                                post=newpost,
                                optionA=optionA,
                                optionB=optionB,
                                optionC=optionC,
                                optionD=optionD)

                db.execute("UPDATE posts SET date_of_post = current_date WHERE post = :post",
                            post=newpost)

                return render_template("newpost.html")
        else:
            return render_template("newpost.html")

    else:
        db.execute("UPDATE posts SET current_date = current_date")
        topost = db.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 1")
        current = datetime.strptime(topost[0]["current_date"], '%Y-%m-%d')
        postdate = datetime.strptime(topost[0]["date_of_post"], '%Y-%m-%d')
        daydifference = (current - postdate).days

        if request.method == "POST":
            if daydifference > 7:
                newpost = request.form.get("newpost")
                optionA = request.form.get("optionA")
                optionB = request.form.get("optionB")
                optionC = request.form.get("optionC")
                optionD = request.form.get("optionD")

                db.execute("INSERT INTO posts (post, optionA, optionB, optionC, optionD) VALUES (:post, :optionA, :optionB, :optionC, :optionD)",
                                post=newpost,
                                optionA=optionA,
                                optionB=optionB,
                                optionC=optionC,
                                optionD=optionD)

                db.execute("UPDATE posts SET date_of_post = current_date WHERE post = :post",
                            post=newpost)

                return render_template("newpost.html")

            else:
                return render_template("error.html", error = ("You have already posted this week, try again in " + str(daydifference) + " days"))

        return render_template("newpost.html")


@app.route("/editpost", methods=["GET", "POST"])
@login_required
def editpost():
    """Allows the admin to edit any posts that may have errors"""

    return render_template("editpost.html")


@app.route("/retrieveposts", methods=["POST"])
@login_required
def retrieveposts():
    """Retrieves a previous post so that the admin can make any edits required"""

    date = request.form.get("date")
    print(date)
    posts = db.execute("SELECT post, id FROM posts WHERE date_of_post = :date_of_post",
                            date_of_post=date)

    if not posts:
        t = jsonify({"success": False})
        return t
    else:
        topost = posts[0]['post']
        postid = posts[0]['id']
        print(topost)
        print(postid)
        f = jsonify({"success": True, "post": topost, "postid": postid})
        print(f)
        return f


@app.route("/updateposts", methods=["POST"])
@login_required
def updateposts():
    """Updates the saved posts with any changes made by the admin"""

    if request.method == "POST":
        updatepost = request.form.get("postedit")
        postid = request.form.get("postid")

        print(updatepost)
        print(postid)

        toupdate = db.execute("UPDATE posts SET post = :post WHERE id = :postid",
                                post=updatepost,
                                postid=postid)

    return render_template("editpost.html")


@app.route("/changePost", methods=["GET", "POST"])
@login_required
def changePost():

    if request.form.get("Previous"):
        prevpost = db.execute("SELECT * FROM posts WHERE id=:postid", postid=(int(request.form.get("Previous"))-1))

        if not prevpost:
            return render_template("error.html", error = ("You have gone too far. There is no more story"))

        else:
            return render_template("archive.html", posts=prevpost)

    if request.form.get("Next"):
        nextpost = db.execute("SELECT * FROM posts WHERE id=:postid", postid=(int(request.form.get("Next"))+1))

        if not nextpost:
            return render_template("error.html", error = ("You have gone too far. There is no more story"))

        else:
            return render_template("archive.html", posts=nextpost)

