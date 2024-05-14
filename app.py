from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from authlib.integrations.flask_client import OAuth
from jinja2 import FileSystemLoader
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from pymongo import MongoClient
import requests
import re
import cohere
from cohere import Client
from urllib.parse import urlencode
import json

app = Flask(__name__)

app.jinja_loader = FileSystemLoader(searchpath=['views', 'templates'])

app.jinja_env.filters['enumerate'] = enumerate

bcrypt = Bcrypt(app)

client = MongoClient("mongodb+srv://21pa1a12a5:Svsp9721@cluster0.n3mmdua.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["BrainTrek"]
users = db["users"]
quizzes = db["quizzes"]

appConf = {
    "OAUTH2_CLIENT_ID": "800948137796-11mkomvfo2gpqb55bl130td54j8sf2f6.apps.googleusercontent.com",
    "OAUTH2_CLIENT_SECRET": "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",
    "OAUTH2_META_URL": "https://accounts.google.com/.well-known/openid-configuration",
    "FLASK_SECRET": "prajnesh@2310",
    "FLASK_PORT": 5000
}

app.secret_key = appConf.get("FLASK_SECRET")

# Google OAuth configuration
oauth = OAuth(app)
oauth.register("myApp",
               client_id=appConf.get("OAUTH2_CLIENT_ID"),
               client_secret=appConf.get("OAUTH2_CLIENT_SECRET"),
               server_metadata_url=appConf.get("OAUTH2_META_URL"),
               client_kwargs={
                   "scope": "openid email profile",
               }
               )

@app.route('/')
def index():
    return render_template('lander.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        if password == confirm_password:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            insertion = users.insert_one({'name': name, 'email': email, 'password': hashed_password})
            flash('Account created successfully')
            return redirect(url_for('index'))
        else:
            flash('Passwords do not match')
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users.find_one({'email': email})

        if user and bcrypt.check_password_hash(user['password'], password):
            # Successful sign-in
            return redirect(url_for('main'))
        else:
            flash('Invalid email or password')
    return render_template('signin.html')

@app.route('/signin/google')
def signin_google():
    callback = url_for('authorized_google', next=request.args.get('next') or request.referrer or None, _external=True)
    return oauth.myApp.authorize_redirect(redirect_uri=url_for("authorized_google", _external=True))

@app.route('/authorized/google')
def authorized_google():
    token = oauth.myApp.authorize_access_token()
    session["user"] = token
    return redirect(url_for('main'))

@app.route('/main')
def main():
    return render_template('main.html', session=session.get("user"))

@app.route('/GKquiz', methods=['GET', 'POST'])
def gkquiz():
    if request.method == 'POST':
        selected_standard = request.form['standard']
        prompt = f"Create 25 multiple-choice general knowledge quiz questions and their options and answers for a student of standard {selected_standard}th standard students and that questions doesn't be generated for a question on images like what is the output of the code or like that also note that don't generate same set of questions repeatedly for consecutive times. Format each question as 'Question X:', provide four multiple-choice options as 'Option A:', 'Option B:', 'Option C:', and 'Option D:', and mark the correct answer with 'Answer:'. Please generate the questions, options, and answers in a clear and consistent format."

        # Send API request to Cohere and get the response
        cohere_client = cohere.Client(api_key="0Rd047SkwTFA2uOiHrSRbvcAZwH55eHLwfKr6YYa")
        response = cohere_client.chat(message=prompt)
        quiz_data_text = response.text
        questions = []
        current_question = {}

        lines = quiz_data_text.strip().split('\n')
        for line in lines:
            if line.startswith("Question"):
                if current_question:
                    questions.append(current_question)
                    current_question = {}
                current_question["Question"] = line.split(":")[1].strip()
                current_question["Options"] = {}
            elif line.startswith("Option"):
                option, text = line.split(":", 1)
                current_question["Options"][option.strip()] = text.strip()
            elif line.startswith("Answer"):
                current_question["Answer"] = line.split(":")[1].strip()

        if current_question:
            questions.append(current_question)

        return render_template("quiz.html", obj=questions)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        selected_option = request.form['quiz_option']
        prompt = f"Create 25 multiple-choice quiz questions and their options and answers based on the topic: '{selected_option}' and that questions doesn't be generated for a question on images like what is the output of the code or like that also note that don't generate same set of questions repeatedly for consecutive times and Make sure to generate all the questions and their options with answers correctly and they have to be visible. Format each question as 'Question X:', provide four multiple-choice options as 'Option A:', 'Option B:', 'Option C:', and 'Option D:', and mark the correct answer with 'Answer:'. Please generate the questions, options, and answers in a clear and consistent format."

        # Send API request to Cohere and get the response
        # Replace 'YOUR_COHERE_API_KEY' with your actual API key
        cohere_client = cohere.Client(api_key="0Rd047SkwTFA2uOiHrSRbvcAZwH55eHLwfKr6YYa")
        response = cohere_client.chat(message=prompt)
        # print(response)
        quiz_data_text = response.text
        questions = []
        current_question = {}

        lines = quiz_data_text.strip().split('\n')
        # print(lines)
        for line in lines:
            if line.startswith("Question"):
                if current_question:
                    questions.append(current_question)
                    current_question = {}
                current_question["Question"] = line.split(":")[1].strip()
                current_question["Options"] = {}
                # print(current_question,"qn")
            elif line.startswith("Option"):
                option, text = line.split(":", 1)
                current_question["Options"][option.strip()] = text.strip()
                # print(current_question,"options")
            elif line.startswith("Answer"):
                current_question["Answer"] = line.split(":")[1].strip()

        if current_question:
            questions.append(current_question)

        return render_template("quiz.html",obj=questions)
    
@app.route('/Topicquiz', methods=['GET', 'POST'])
def Topicquiz():
    if request.method == 'POST':
        entered_topic = request.form['topic']
        prompt = f"Create 25 multiple-choice quiz questions and their options and answers based on the topic: '{entered_topic}' and that questions doesn't be generated for a question on images like what is the output of the code or like that. Format each question as 'Question X:', provide four multiple-choice options as 'Option A:', 'Option B:', 'Option C:', and 'Option D:', and mark the correct answer with 'Answer:'. Please generate the questions, options, and answers in a clear and consistent format."

        # Send API request to Cohere and get the response
        # Replace 'YOUR_COHERE_API_KEY' with your actual API key
        cohere_client = cohere.Client(api_key="0Rd047SkwTFA2uOiHrSRbvcAZwH55eHLwfKr6YYa")
        response = cohere_client.chat(message=prompt)
        # print(response)
        quiz_data_text = response.text
        questions = []
        current_question = {}

        lines = quiz_data_text.strip().split('\n')
        # print(lines)
        for line in lines:
            if line.startswith("Question"):
                if current_question:
                    questions.append(current_question)
                    current_question = {}
                current_question["Question"] = line.split(":")[1].strip()
                current_question["Options"] = {}
                # print(current_question,"qn")
            elif line.startswith("Option"):
                option, text = line.split(":", 1)
                current_question["Options"][option.strip()] = text.strip()
                # print(current_question,"options")
            elif line.startswith("Answer"):
                current_question["Answer"] = line.split(":")[1].strip()

        if current_question:
            questions.append(current_question)

        return render_template("quiz.html",obj=questions)    

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
