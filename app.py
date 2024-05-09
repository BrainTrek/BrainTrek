from flask import Flask, render_template, request, flash, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from pymongo import MongoClient
import cohere
from urllib.parse import urlencode
import json

app = Flask(__name__)

client = MongoClient("mongodb+srv://21pa1a12a5:Svsp9721@cluster0.n3mmdua.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["BrainTrek"]
users = db["users"]

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
    # me = google.get('oauth2/v1/userinfo')
    # user_email = me.data['email']
    # Store user data in MongoDB or perform further actions
    token = oauth.myApp.authorize_access_token()
    session["user"] = token
    return redirect(url_for('main'))

@app.route('/main')
def main():
    # Rest of your main route code here
    return render_template('main.html', session=session.get("user"))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        selected_option = request.form['quiz_option']
        client = cohere.Client(api_key="your_api_key")
        response = client.generate_quiz(prompt=selected_option)
        quiz_data = response.text
        # Store quiz data in MongoDB
        # mongo.db.quizzes.insert_one({'user_id': current_user.id, 'quiz_data': quiz_data})
        # return redirect(url_for('quiz_result', quiz_id=mongo.db.quizzes.inserted_id))
    return render_template('quiz.html')

@app.route('/quiz/<quiz_id>')
def quiz_result(quiz_id):
    # quiz = mongo.db.quizzes.find_one({'_id': ObjectId(quiz_id)})
    # if quiz:
    #     return render_template('quiz_result.html', quiz_data=quiz['quiz_data'])
    # else:
    #     flash('Quiz not found')
    #     return redirect(url_for('index'))
    return "Quiz result page for quiz ID: " + quiz_id

# @app.route('/history')
# def history():
#     user_quizzes = mongo.db.quizzes.find({'user_id': current_user.id})
#     return render_template('history.html', quizzes=user_quizzes)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)