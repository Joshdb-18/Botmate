import aiapi
import config
from flask import Flask, render_template, jsonify, request, flash, logging, url_for, session, redirect
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from helpers import apology, login_required
import openai
import os
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config.from_object(config.config['development'])

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# 'mysql://root:root@localhost/auth'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

class User(db.Model):
    """Create User Model which contains id, name, username, email and password"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(256), unique=True)
    history = db.Column(db.String(10000), unique=False)

@app.after_request
def after_request(response):
    """ Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Ensure user enters via POST
    if request.method == "POST":

        name = request.form.get("username")
        passwd = request.form.get("password")
        confirm = request.form.get("confirmation")
        usernameCheck = User.query.filter_by(username=name).first()

        # Ensure username was submitted
        if not name:
            return apology("Must provide a name", 400)

        # Else if username already exists
        elif usernameCheck is not None:
            return apology("Username already exists", 400)

        # Else if password was not submitted
        elif not passwd:
            return apology("Must provide a password", 400)

        # Else if confirmation was not submitted
        elif not confirm:
            return apology("Must confirm Password")

        # Else if password is not the same
        elif passwd != confirm:
            return apology("Password must match", 400)

        register = User(username = name, password = passwd)
        db.session.add(register)
        db.session.commit()

        return redirect(url_for("login"))
    # If user enters via GET
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # checking that user exists
        name = request.form.get("username")
        passw = request.form.get("password")
        if not name:
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not passw:
            return apology("must provide password", 403)

        login = User.query.filter_by(username=name, password=passw).first()
        if login is not None:
            session['user_id'] = True
            return render_template("index.html")


    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route('/chat', methods = ['GET', 'POST'])
@login_required
def chat():
    """ Chat with Botmate"""
    if request.method == 'POST':
        prompt = request.form['prompt']
        his = User(history=prompt)
        db.session.add(his)
        db.session.commit()
        res = {}
        res['answer'] = aiapi.generateChatResponse(prompt)
        return jsonify(res), 200

    return render_template('chat.html', **locals())

@app.route('/image', methods = ['GET', 'POST'])
@login_required
def image():
    """ Generate images"""
    if request.method == 'POST':
        image = ""
        prt = request.form['prompt']
        try:
            response = openai.Image.create(
                    prompt = prt,
                    n=1,
                    size="1024x1024"
                )
            image_url = response['data'][0]['url']
            return image_url, 200
            # return render_template('image.html', image=image_url)
        except openai.error.OpenAIError as e:
            return render_template('image.html', image=e.error)

    return render_template('image.html')

@app.route('/history')
@login_required
def history():
    """Shows chat history"""
    message = ""
    id = session["user_id"]
    chat =  User.query.filter_by(id=id).first()
    history = chat.history
    if history is not None:
        return render_template("history.html", message=history)
    else:
        return render_template("history.html", message="No history found")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session['user_id'] = False

    # Redirect user to login form
    return redirect("/")

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port='5000', debug=True)
