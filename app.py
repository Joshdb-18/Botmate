import aiapi
import config
import json
import openai
import os
import requests

from flask import Flask, render_template, jsonify
from flask import request, flash, logging, url_for, session, redirect
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
# 'mysql://root:root@localhost/auth'
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

        passwd = generate_password_hash(passwd, method='pbkdf2:sha256',
                                        salt_length=8)
        register = User(username=name, password=passwd)
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
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not passw:
            return apology("Must provide password", 403)

        login = User.query.filter_by(username=name).first()
        if login and check_password_hash(login.password, passw):
            session['user_id'] = True
            flash("Welcome!")
            return render_template("chat.html")

        return apology("Invalid username and/or password", 403)

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    """ Chat with Botmate"""
    if request.method == 'POST':
        prompt = request.form['prompt']
        res = {}
        res['answer'] = aiapi.generateChatResponse(prompt)
        save = res['answer']
        id = session["user_id"]
        user = User.query.filter_by(id=id).first()
        chat_history = user.history or ""
        if chat_history is None:
            update = User(
                    history='Input: '+prompt+'\n'
                    + 'Response: '+save+'\n'+'\n')
            db.session.add(update)
            db.session.commit()
        else:
            chat_history += 'Input: ' + prompt + '\n' + 'Response: '
            chat_history += save + "\n" + "\n" + "\n"
            user.history = chat_history
            db.session.commit()
        # res = {}
        # res['answer'] = aiapi.generateChatResponse(prompt)
        return jsonify(res), 200

    return render_template('chat.html', **locals())


@app.route('/image', methods=['GET', 'POST'])
@login_required
def image():
    """ Generate images"""
    if request.method == 'POST':
        api_key = 'unsplash-api-key'
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


@app.route('/history')
@login_required
def history():
    """Shows chat history"""
    message = ""
    user_id = session["user_id"]
    chat = User.query.filter_by(id=user_id).first()
    history = chat.history
    if history:
        return render_template("history.html", message=history.split('\n'))
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
