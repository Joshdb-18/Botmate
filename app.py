import aiapi
import config
import os
import requests
import re

from datetime import datetime
from flask import Flask, render_template, jsonify
from flask import request, flash, url_for, session, redirect
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from googleapiclient.discovery import build
from helpers import apology, login_required
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config.from_object(config.config['development'])

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


class User(db.Model):
    """
    Create User Model which contains id, name,
    username, email and password
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(80), unique=True)
    username = db.Column(db.String(80), unique=False)
    password = db.Column(db.String(256), unique=True)
    history = db.relationship('History', backref='user', lazy=True)


class History(db.Model):
    """ Create History Model which is a one
    to many relationship
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    prompt = db.Column(db.String(10000), nullable=False)
    response = db.Column(db.String(10000), nullable=False)


@app.after_request
def after_request(response):
    """ Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():

    # Clear any current session before redirect
    session['user_id'] = False

    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Ensure user enters via POST
    if request.method == "POST":

        email = request.form.get("email")
        name = request.form.get("username")
        passwd = request.form.get("password")
        confirm = request.form.get("confirmation")
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        emailCheck = User.query.filter_by(email=email).first()

        # Ensure email was submitted
        if not email:
            return apology("Must provide an email", 400)

        # Ensure the email is valid
        elif re.match(pattern, email) is None:
            return apology("Invalid email", 400)

        # Ensure username is submitted
        elif not name:
            return apology("Must provide a name", 400)

        # Else if username already exists
        elif emailCheck is not None:
            return apology("Email already exists", 400)

        # Else if password was not submitted
        elif not passwd:
            return apology("Must provide a password", 400)

        # Else if confirmation was not submitted
        elif not confirm:
            return apology("Must confirm Password")

        # Else if password is not the same
        elif passwd != confirm:
            return apology("Password must match", 400)

        passwd = generate_password_hash(passwd, method='pbkdf2:sha256',
                                        salt_length=8)
        user = User(email=email, username=name, password=passwd)
        db.session.add(user)
        db.session.commit()

        # If the user was successfully created, store their ID in the session
        session['user_id'] = user.id

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
        email = request.form.get("email")
        passw = request.form.get("password")
        if not email:
            return apology("Must provide email", 403)

        # Ensure password was submitted
        elif not passw:
            return apology("Must provide password", 403)

        login = User.query.filter_by(email=email).first()
        if login and check_password_hash(login.password, passw):
            session['user_id'] = login.id
            return redirect(url_for('chat'))

        return apology("Invalid username and/or password", 403)

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    """ Chat with Botmate"""

    # Get the current logged in user
    user_id = session.get('user_id')

    # Get the id of the user in the history model
    history = History.query.filter_by(user_id=user_id).all()

    if request.method == 'POST':
        prompt = request.form['prompt']
        res = {}
        res['answer'] = aiapi.generateChatResponse(prompt)
        response = res['answer']
        if history:
            last_history = history[-1]
            if last_history.response != response:
                new_history = History(
                        user_id=user_id,
                        date=datetime.utcnow(),
                        prompt=prompt,
                        response=response)
                db.session.add(new_history)
                db.session.commit()
        else:
            new_history = History(
                    user_id=user_id,
                    date=datetime.utcnow(),
                    prompt=prompt,
                    response=response)
            db.session.add(new_history)
            db.session.commit()

        return jsonify(res), 200

    return render_template('chat.html')


@app.route('/image', methods=['GET', 'POST'])
@login_required
def image():
    """ Generate images"""
    if request.method == 'POST':
        api_key = 'api-key'
        url = 'https://api.unsplash.com/search/photos'
        prompt = request.form.get("prompt")
        headers = {'Authorization': f'Client-ID {api_key}'}
        params = {'query': f'{prompt}', 'per_page': 10000}

        response = requests.get(url, headers=headers, params=params)
        results = response.json()['results']
        photo_urls = [result['urls']['regular'] for result in results]

        return render_template('image.html', photo_urls=photo_urls)

    return render_template('image.html')


@app.route("/video", methods=["GET", "POST"])
@login_required
def video():
    """ Generate videos"""
    if request.method == "POST":
        query = request.form.get("query")
        api_key = 'api-key'
        youtube = build('youtube', 'v3', developerKey=api_key)
        search_request = youtube.search().list(
            q=query,
            type='video',
            part='id,snippet',
            maxResults=1000
        )
        response = search_request.execute()
        videos = response['items']
        return render_template('video.html', videos=videos)

    return render_template('video.html')


@app.route('/history/<int:user_id>')
@login_required
def history(user_id):
    """Shows chat history"""
    user = User.query.get(user_id)
    history = user.history
    if history:
        messages = []
        for h in history:
            messages.append({
                'date': h.date.strftime("%Y-%m-%d %H:%M:%S"),
                'prompt': h.prompt,
                'response': h.response.replace('<br>', " ")
                })
        return render_template("history.html", messages=messages, user=user)
    else:
        return render_template("history.html", messages="No history found",
                               user=user)


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
