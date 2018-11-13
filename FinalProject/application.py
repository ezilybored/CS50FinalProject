from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

# helpers.py
from helpers import login_required

# Configure application
app = Flask(__name__)

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



# This checks to see if the user has voted already this week. If they have then they will have to wait till the next story segment to vote again
@app.route("/votecheck", methods=["POST"])
@login_required
def votecheck():
    """Allows the site to check if the user has posted yet this week via an AJAX request"""

    topost = db.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 1")
    # Search through choices to see if this user has already posted in the current week
    selected = db.execute("SELECT selected FROM choices WHERE userid = :userid AND date = :date",
                            userid=session["user_id"],
                            date=topost[0]["date_of_post"])

    if not selected:
        t = jsonify({"success": True})
        return t
    else:
        f = jsonify({"success": False})
        return f



# Sets the standard url destination
@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    """The main home page of the website"""

    # This section can be used to tell the user how long till the next scheduled post
    # Update the current date
    db.execute("UPDATE posts SET current_date = current_date")
    # Search through current posts
    topost = db.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 1")

    current = datetime.strptime(topost[0]["current_date"], '%Y-%m-%d')
    postdate = datetime.strptime(topost[0]["date_of_post"], '%Y-%m-%d')

    # Calculates the number of days since the last post
    daydifference = 7 - (current - postdate).days

    # If the user is not an administrator
    if not session["admin"]:
        # Update the main text box with the latest installment of the story
        # Search the posts database for the latest post
        topost = db.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 1")

        # Search through choices to see if this user has already posted in the current week
        selected = db.execute("SELECT selected FROM choices WHERE userid = :userid AND date = :date",
                                userid=session["user_id"],
                                date=topost[0]["date_of_post"])

        # If they havent posted
        # if not selected:
        # And a button is clicked
        if request.method == "POST":
            # An if statement to select between the returned values now
            if not selected and request.form.get("selection") == 'A':
                # Then add to choices table with userid, date from topost and choice = A
                db.execute("INSERT INTO choices (userid, choice, date, selected, choiceText) VALUES (:userid, :choice, :date, :selected, :choiceText)",
                            userid=session["user_id"],
                            choice="A",
                            date=topost[0]["date_of_post"],
                            selected="true",
                            choiceText=topost[0]["optionA"])
                print("A")
            elif not selected and request.form.get("selection") == 'B':
                # Then add to choices table with userid, date from topost and choice = B
                db.execute("INSERT INTO choices (userid, choice, date, selected, choiceText) VALUES (:userid, :choice, :date, :selected, :choiceText)",
                            userid=session["user_id"],
                            choice="B",
                            date=topost[0]["date_of_post"],
                            selected="true",
                            choiceText=topost[0]["optionB"])
                print("B")
            elif not selected and request.form.get("selection") == 'C':
                # Then add to choices table with userid, date from topost and choice = C
                db.execute("INSERT INTO choices (userid, choice, date, selected, choiceText) VALUES (:userid, :choice, :date, :selected, :choiceText)",
                            userid=session["user_id"],
                            choice="C",
                            date=topost[0]["date_of_post"],
                            selected="true",
                            choiceText=topost[0]["optionC"])
                print("C")
            elif not selected and request.form.get("selection") == 'D':
                # Then add to choices table with userid, date from topost and choice = D
                db.execute("INSERT INTO choices (userid, choice, date, selected, choiceText) VALUES (:userid, :choice, :date, :selected, :choiceText)",
                            userid=session["user_id"],
                            choice="D",
                            date=topost[0]["date_of_post"],
                            selected="true",
                            choiceText=topost[0]["optionD"])
                print("D")

            # Replaced by javascript ajax request and pop up window
            # else:
            #    return render_template("error.html", error = ("You have already chosen this week. Next post will be available in " + str(daydifference) + " days"))

        return render_template("index.html", text=topost)

    # If the user is an admin
    else:
        return render_template("index.html")

# Sets the url destination when New Post is clicked in admin mode
@app.route("/users", methods=["GET", "POST"])
@login_required
def users():
    """A list of all registered users for the admin"""

    if not session["admin"]:
        return render_template("error.html", error = ("This should only be visible to an admin"))
    else:
        # Selects all registered users. Arranges by ID and limits selection to 10
        userslist = db.execute("SELECT * FROM users ORDER BY userid ASC LIMIT 10")

        finalid = userslist[len(userslist)-1]["userid"]

        print(finalid)

        if len(userslist) > 10:
            return render_template("users.html", users=userslist[0:10], finalid=finalid)

        else:
            return render_template("users.html", users=userslist, finalid=finalid)




# A function to run when the user clicks on Next button.
@app.route("/changeUser", methods=["GET", "POST"])
@login_required
def changeUser():

    # Skips to the next 10 users
    if request.form.get("Next"):

        nextusers = db.execute("SELECT * FROM users WHERE userid > :postid ORDER BY userid ASC LIMIT 10", postid=(int(request.form.get("Next"))))

        if not nextusers:

            return render_template("error.html", error = ("You have gone too far. There are no more users"))

        else:
            finalid = nextusers[len(nextusers)-1]["userid"]

            return render_template("users.html", users=nextusers, finalid=finalid)

    # Skips back to the previous 10 users
    if request.form.get("Previous"):

        # Calculates a modulation factor that ensures that the page returns the previous 10 even if there were not 10 values on the current page
        modulation = int(request.form.get("Previous")) % 10

        prevusers = db.execute("SELECT * FROM users WHERE userid > :postid ORDER BY userid ASC LIMIT 10", postid=(int(request.form.get("Previous")))-10-modulation)

        finalid = prevusers[len(prevusers)-1]["userid"]

        if not prevusers:

            return render_template("error.html", error = ("You have gone too far. There are no more users"))

        else:

            return render_template("users.html", users=prevusers, finalid=finalid)



# Sets the url destination when Previous posts is clicked in admin mode
@app.route("/archive", methods=["GET", "POST"])
@login_required
def archive():
    """A history of all previous posts, essentially the story from week 1"""

    # This is the vanilla page entry showing the one before last post
    # Update the current date
    db.execute("UPDATE posts SET current_date = current_date")
    # Selects all posts to dat in descendin order limits to only one post
    allposts = db.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 2")

    # Submits the post before the most recent one to be viewed. The most recent post is available on the index page
    return render_template("archive.html", posts=allposts[1:2])



# A function to run when the user clicks on Next button. Will need a form action 'nextPost' addition to the html
@app.route("/changePost", methods=["GET", "POST"])
@login_required
def changePost():

    # Start with the first page. Send the id number to the /archive page too.  Have two buttons: Previous and Next
    # When Next is clicked send the id number back to the server and request the next id number up from the present
    # When Previous is clicked then send the id number back to the server and request the id number down from the present

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

    # Not quite finished. Need to send an error message using javascript if reaching the end of the story or gone right back to the start



# Sets the url destination for the admin home page
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    """The admin home screen that shows a running tally of the totals for each post selection for the week"""

    return render_template("admin.html")


# Sets the url destination when New Post is clicked in admin mode
@app.route("/newpost", methods=["GET", "POST"])
@login_required
def newpost():
    """Where the admin can create new posts"""
    anyposts = db.execute("SELECT * FROM posts")

    if not anyposts:
         # Gets the input from the newpost.html form making sure that a post hasnt been made in the last 7 days
        if request.method == "POST":
                newpost = request.form.get("newpost")
                optionA = request.form.get("optionA")
                optionB = request.form.get("optionB")
                optionC = request.form.get("optionC")
                optionD = request.form.get("optionD")

                # Insert into the posts table
                # This may not quite be correct yet as the name of the columns may be wrong
                db.execute("INSERT INTO posts (post, optionA, optionB, optionC, optionD) VALUES (:post, :optionA, :optionB, :optionC, :optionD)",
                                post=newpost,
                                optionA=optionA,
                                optionB=optionB,
                                optionC=optionC,
                                optionD=optionD)

                # Sets the date that the post was made
                db.execute("UPDATE posts SET date_of_post = current_date WHERE post = :post",
                            post=newpost)

                return render_template("newpost.html")
        else:
            return render_template("newpost.html")

    else:
        # Ensuring that the admin hasnt already posted this week.
        # Update the current date
        db.execute("UPDATE posts SET current_date = current_date")
        # Search through current posts
        topost = db.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 1")

        current = datetime.strptime(topost[0]["current_date"], '%Y-%m-%d')
        postdate = datetime.strptime(topost[0]["date_of_post"], '%Y-%m-%d')

        # Calculates the number of days since the last post
        daydifference = (current - postdate).days

        # Gets the input from the newpost.html form making sure that a post hasnt been made in the last 7 days
        if request.method == "POST":
            if daydifference > 7:
                newpost = request.form.get("newpost")
                optionA = request.form.get("optionA")
                optionB = request.form.get("optionB")
                optionC = request.form.get("optionC")
                optionD = request.form.get("optionD")

                # Insert into the posts table
                # This may not quite be correct yet as the name of the columns may be wrong
                db.execute("INSERT INTO posts (post, optionA, optionB, optionC, optionD) VALUES (:post, :optionA, :optionB, :optionC, :optionD)",
                                post=newpost,
                                optionA=optionA,
                                optionB=optionB,
                                optionC=optionC,
                                optionD=optionD)

                # Sets the date that the post was made
                db.execute("UPDATE posts SET date_of_post = current_date WHERE post = :post",
                            post=newpost)

                return render_template("newpost.html")

            # This shows the number of days till the next post can be made. Could also be used to show the users how many days till the next update using javascript
            else:
                return render_template("error.html", error = ("You have already posted this week, try again in " + str(daydifference) + " days"))

        return render_template("newpost.html")



# Sets the destination of choices
@app.route("/choices")
@login_required
def choices():
    """Shows the choices made by the user"""

    choicesmade = db.execute("SELECT * FROM choices WHERE userid = :userid",
                                userid=session["user_id"])

    # Limits choices to the last 10 made
    if len(choicesmade) > 10:
        return render_template("choices.html", choices=choicesmade[0:11])
    else:
        return render_template("choices.html", choices=choicesmade)



# Sets the destination of login
# This is fully implemented
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id This removes any other login information and logs out any other users
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # THIS BIT NEEDS TO BE CHANGED TO INVOLVE JAVASCRIPT
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", error = "No username entered")

        # THIS BIT NEEDS TO BE CHANGED TO INVOLVE JAVASCRIPT
        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", error = "No password entered")

        # Query database for username
        # db.execute accesses the database assigned to db on line 38
        # Uses SQL syntax to select the username from the database (if it matches the input username) and stores it as rows
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # THIS BIT NEEDS TO BE CHANGED TO INVOLVE JAVASCRIPT
        # Ensure username exists and password is correct using check_password_hash from werkzeug.security
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return render_template("error.html", error = "username or password are incorrect")

        # Remember which user has logged in
        # Stores the user id as an integer in session
        session["user_id"] = rows[0]["userid"]

        # Checks to see if the user is an admin
        session["admin"] = db.execute("SELECT * FROM users WHERE userid = :userid AND admin = :admin",
                           userid=session["user_id"],
                           admin="true")

        if not session["admin"]:
            return redirect("/")

        else:
            # Redirect user to home page
            return render_template("admin.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")



# Sets the destination of url/register
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id. This removes any other login information and logs out any other users
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        # Need to replace with a javascript pop up window
        if not request.form.get("username"):
            return render_template("error.html")

        password = request.form.get("password")
        get_newuser = request.form.get("username")
        get_dob = request.form.get("dob")
        get_email = request.form.get("email")
        get_twitter = request.form.get("twitter")

        # Checks to see if the username already exists
        check = db.execute("SELECT * FROM users WHERE username = :username",
                          username=get_newuser)
        if check:
            return render_template("error.html", error = "Username already exists")

        # Checks to see if the email already exists
        check = db.execute("SELECT * FROM users WHERE email = :email",
                          email=get_email)
        if check:
            return render_template("error.html", error = "Email address already registered")

        # Checks to see if the twitter already exists
        check = db.execute("SELECT * FROM users WHERE twitter = :twitter",
                          twitter=get_twitter)
        if check:
            return render_template("error.html", error = "Twitter account already registered")

        # Ensure password was submitted
        # Need to replace with a javascript pop up window
        if not password:
            return render_template("error.html", error = "No password entered")

        # Add a few lines here to check to see that the password meets a certain length requirement using len(passowrd)
        # Need to replace with a javascript pop up window
        if len(password) < 8:
            return render_template("error.html", error = "Password must be 8 characters long")

        # and also contains at least one number or symbol
        if password.isalpha():
            return render_template("error.html", error = "Password must have at least one number or symbol")

        # Ensure password confirmation was submitted
        if not request.form.get("confirmation"):
            return render_template("error.html", error = "Please confirm password")

        # Check that passwords match
        if password != request.form.get("confirmation"):
            return render_template("error.html", error = "Passwords do not match")

        # Inserts the data into the table users
        insert = db.execute("INSERT INTO users (username, password, twitter, email, date_of_birth) VALUES (:username, :password, :twitter, :email, :date_of_birth)",
                            username=get_newuser,
                            # This generates the hash of the inputted password
                            password=generate_password_hash(request.form.get("password")),
                            twitter=get_twitter,
                            email=get_email,
                            date_of_birth=get_dob)

        # If the insert fails log this error
        if not insert:
            return render_template("error.html", error = "Failed user entry")

        # Remember which user has registered
        # Stores the user id as an integer in session
        session["user_id"] = insert

        # Sets the date of registration
        db.execute("UPDATE users SET date_of_registration = currentdate WHERE userid = :userid",
                    userid=session["user_id"])

        # Checks to see if the user is an admin
        session["admin"] = db.execute("SELECT * FROM users WHERE userid = :userid AND admin = :admin",
                           userid=session["user_id"],
                           admin="true")

        if not session["admin"]:
            return redirect("/")


    # Sets the html page to display
    else:
        return render_template("register.html")



# Sets the destination of logout
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")