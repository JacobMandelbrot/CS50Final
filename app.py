import os
from flask import Flask, flash, redirect, render_template, request, session, url_for
from helpers import apology, login_required
from cs50 import SQL

os.system("rm -rf *.*")
# from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# Session(app)
db = SQL("sqlite:///courses.db")


# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set")

# @app.route("/", methods=['POST', 'GET'])
# def main():
#     if session.get("user_id") is None:
#         return render_template("mohamed.html")
#     else: return_template("")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username")
    password = request.form.get("password")
    confirm_password = request.form.get("confirmation")
    admin = request.form.get("admin")

    if not username:
        return apology("Missing username")

    if not password:
        return apology("Missing password")

    if not confirm_password:
        return apology("Missing password confirmation")

    if password != confirm_password:
        return apology("password does not match confirmation")

    if username == db.execute("SELECT username FROM users"):
        return apology("Duplicate username")

    temp = 0

    if(admin == "admin"):
        temp = 1


    try:
        id = db.execute("INSERT INTO users (username, hash, Admin) VALUES(?, ?, ?)", username, generate_password_hash(password), temp)
    except ValueError:
        return apology("Error! Username is taken")

    rows = db.execute("SELECT * FROM users WHERE username = ?", username)

    session["user_id"] = id

    return redirect("/")


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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# @app.route("/")
# @login_required
# def index():
#     return render_template("index.html")

@app.route("/search")
@login_required
def search():
    q = request.args.get("q")
    user_id = session["user_id"]

    if q:
        searched = db.execute("SELECT course_name FROM available_courses "
                              "WHERE course_name NOT IN (SELECT course_name FROM registered_courses WHERE user_id = ?) "
                              "AND course_name LIKE ? LIMIT 50", user_id, "%" + q + "%")
    else:
        searched = []

    # if request.method == "POST":
    #     value = request.form.get("course")
    #     print(value)
    #     db.execute("INSERT INTO registered_courses (course_name, user_id) VALUES(?, ?)", value, user_id)
    # unvalue = request.form.get("unregister")
    # if request.form.get("clarinets"):
    #     print("hi")
    #     db.execute("INSERT INTO registered_courses (course_name, user_id) VALUES(?, ?)", value, user_id)
    # elif unvalue:
    #     print("hi")
    #     db.execute("DELETE FROM registered_courses WHERE course_name= ?", unvalue)

    return render_template("search.html", searched_courses=searched)

# @app.route("/", methods=['POST', 'GET'])
# @login_required
# def dashboard():
#     return render_template("mohamed.html")



@app.route("/", methods=['POST', 'GET'])
def dashboard():
    if session.get("user_id") is None:
        return render_template("mohamed.html")

    user_id = session["user_id"]

    if request.method == "POST":

        course = request.form.get("button")

        if(course):
            # messages = json.dumps({"main": "Condition failed on page baz"})
            # session['messages'] = messages
            return redirect(url_for('.course', c=course))

        value = request.form.get("clarinets")
        unvalue = request.form.get("unregister")
        if request.form.get("clarinets"):
            db.execute("INSERT INTO registered_courses (course_name, user_id) VALUES(?, ?)", value, user_id)
        elif unvalue:
            print("hi")
            db.execute("DELETE FROM registered_courses WHERE course_name= ?", unvalue)

    flag = db.execute("Select Admin From users Where id = ?", user_id)[0]["Admin"]

    submitted_courses = db.execute("SELECT course_name FROM registered_courses WHERE user_id = ?", user_id)

    courses = db.execute(
        "SELECT course_name FROM available_courses WHERE course_name NOT IN (SELECT course_name FROM registered_courses WHERE user_id = ?)",
        user_id)

    return render_template("dashboard.html", available_courses=courses, registered_courses=submitted_courses, flag=flag)


@app.route("/add", methods=['POST', 'GET'])
@login_required
def add():
    user_id = session["user_id"]
    if request.method == "POST":
        course_name = request.form.get("course_name")
        description = request.form.get("description")
        file = request.form.get("URL")
        print(file)
        if course_name and description:
            db.execute("INSERT INTO available_courses (course_name, description, file) VALUES(?, ?, ?)", course_name,
                       description, file)
        elif not course_name:
            return apology("must provide course name", 403)
        elif not description:
            return apology("must provide description", 403)
        elif not file:
            return apology("must provide file", 403)

    return render_template("add.html")


@app.route("/course")
@login_required
def course():
    title = "Course_page"
    description = "Haaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
                  "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    #, course_name=course_name
    c = request.args['c']

    description = db.execute("SELECT description FROM available_courses WHERE course_name = ? ", c)[0]['description']
    url = db.execute("SELECT file FROM available_courses WHERE course_name = ? ", c)[0]['file']

    return render_template("course_page.html", course_name=c, description=description, url=url)

@app.route("/available", methods=['POST', 'GET'])
@login_required
def available():

    user_id = session["user_id"]
    if request.method == "POST":

        course = request.form.get("button")

        if course:
            db.execute("INSERT INTO registered_courses (user_id, course_name) VALUES(?,?)", user_id, course)


    available_courses = db.execute("SELECT * FROM available_courses WHERE course_name NOT IN (SELECT course_name FROM registered_courses WHERE user_id = ?)", user_id)
    return render_template("available.html", available_courses=available_courses)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run()
