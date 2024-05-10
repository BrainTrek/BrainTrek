from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from authlib.integrations.flask_client import OAuth
from jinja2 import FileSystemLoader
from flask_pymongo import PyMongo
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
            insertion = users.insert_one({'name': name, 'email': email, 'password': password})
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
        user = users.find_one({'email': email, 'password': password})

        if user:
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

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        selected_option = request.form['quiz_option']
        prompt = f"Create 2 multiple-choice quiz questions and their options and answers based on the topic: '{selected_option}'. Format each question as 'Question X:', provide four multiple-choice options as 'Option A:', 'Option B:', 'Option C:', and 'Option D:', and mark the correct answer with 'Answer:'. Please generate the questions, options, and answers in a clear and consistent format."

        # Send API request to Cohere and get the response
        # Replace 'YOUR_COHERE_API_KEY' with your actual API key
        cohere_client = cohere.Client(api_key="0Rd047SkwTFA2uOiHrSRbvcAZwH55eHLwfKr6YYa")
        response = cohere_client.chat(message=prompt)
        quiz_data = response.text
        print(quiz_data)

        questions = re.findall(r'Question (\d+): (.+?)\n', quiz_data, re.DOTALL)
        options = re.findall(r'Option [A-D]: (.+?)\n', quiz_data, re.DOTALL)
        answers = re.findall(r'Answer: (.+?)\n', quiz_data, re.DOTALL)

        print(questions,options,answers)

        # Create a list of dictionaries for each question
        json_data = []
        for i in range(len(questions)):
            question_dict = {
                "question": questions[i][1].strip(),
                "options": options[i * 4:(i * 4) + 4],
                "answer": answers[i].strip()
            }
            json_data.append(question_dict)

        # Convert the list of dictionaries to JSON
        json_string = json.dumps(json_data, indent=2)
        print(json_string)
    return render_template('quiz.ejs', selected_option=None)


#         for i, question in enumerate(questions, start=1):
#             print(f"Question {i}: {question}")
#             for j, option in enumerate(options[i - 1], start=1):
#                 print(f"{j}. {option}")
#             print(f"Answer: {answers[i - 1]}")
#         # Store the quiz data in the database
#         # quiz_id = str(quizzes.insert_one({'topic': selected_option, 'questions': questions, 'options': options_list, 'answers': answers}).inserted_id)

#         # Render the quiz.ejs template with the quiz data
#         # return render_template('quiz.ejs', selected_option=selected_option, quiz_id=quiz_id, questions=questions, options_list=options_list)

#     return render_template('quiz.ejs', selected_option=None)

# @app.route('/quiz', methods=['POST'])
# def quiz():
#     # Prepare the API request payload
#     payload = {
#         "instructions": "Generate a 10-question quiz on general knowledge, with each question having four multiple-choice options and one correct answer. Number the questions and provide a clear format for each question, option, and correct answer. Also, provide the lists of questions, options, and correct answers separately in the response.",
#         "context": "This is a general knowledge quiz.",
#         "models": ["command"]
#     }

#     # Call the Cohere API
#     headers = {
#         'Authorization': 'api_key 0Rd047SkwTFA2uOiHrSRbvcAZwH55eHLwfKr6YYa',
#     }

#     response = requests.post('https://api.cohere.com/predict', json=payload, headers=headers)

#     # Parse the API response
#     data = response.json()
#     generated_text = data['results'][0]['generated_text']

#     # Split the generated text into lists of questions, options, and correct answers
#     questions = []
#     options = []
#     correct_answers = []

#     for i in range(0, len(generated_text), 5):
#         question_block = generated_text[i:i+5]
#         question = question_block[0].strip()
#         options.append(question_block[1:])
#         questions.append(question)

#         correct_answer_index = question_block[4].find(')') + 1
#         correct_answer = question_block[4][correct_answer_index:].strip()
#         correct_answers.append(correct_answer)

#     # Return the lists of questions, options, and correct answers
#     print(jsonify({"questions": questions, "options": options, "correct_answers": correct_answers}))

@app.route('/quiz/<quiz_id>', methods=['GET', 'POST'])
def quiz_result(quiz_id):
    quiz = quizzes.find_one({'_id': ObjectId(quiz_id)})
    if quiz:
        if request.method == 'POST':
            user_answers = request.form.getlist('user_answer')
            correct_answers = list(quiz['options'].keys())
            correct_count = sum(1 for user_answer in user_answers if user_answer in correct_answers)

            score = int((correct_count / len(correct_answers)) * 100)

            return render_template('quiz_result.html', quiz_data=quiz['questions'], options=quiz['options'], score=score)

    return "Quiz result page for quiz ID: " + quiz_id

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
