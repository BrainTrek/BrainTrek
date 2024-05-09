from flask import Flask,render_template, request, flash, url_for, redirect, session
from flask_pymongo import PyMongo
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import base64
import cohere

app = Flask(__name__)
app.secret_key = 'prajnesh@2310'
# app.config['MONGO_URI'] = 'mongodb+srv://21pa1a12a5:Svsp9721@cluster0.nsdecj7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
myclient = MongoClient("mongodb+srv://21pa1a12a5:Svsp9721@cluster0.nsdecj7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
# mongo = PyMongo(app)
# login_manager = LoginManager()
# login_manager.init_app(app)

# class User(UserMixin):
#     def __init__(self, id, email):
#         self.id = id
#         self.email = email

# @login_manager.user_loader
# def load_user(user_id):
#     user = mongo.db.users.find_one({'_id': user_id})
#     if user:
#         return User(id=user['_id'], email=user['email'])
#     return None

@app.route('/')
def index():
    return render_template('lander.html')

brainTrekdb = myclient["BrainTrek"]
users = brainTrekdb["users"]

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        print(name,email,password)
        if password == confirm_password:
            new_user = {'name': name, 'email': email, 'password': password}
            print(new_user)
            insertion = users.insert_one(new_user)
            flash('Account created successfully')
            return redirect(url_for('signin'))
        flash('Passwords do not match')
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users.find_one({'email': email, 'password': password})
        if user:
            # user_obj = User(id=user['_id'], email=user['email'])
            # login_user(user_obj)
            return redirect(url_for('main'))
        flash('Invalid email or password')
    return render_template('signin.html')

@app.route('/main')
# @login_required
def main():
    return render_template('main.html')

@app.route('/quiz', methods=['GET', 'POST'])
# @login_required
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

# @app.route('/quiz/<quiz_id>')
# @login_required
# def quiz_result(quiz_id):
#     quiz = mongo.db.quizzes.find_one({'_id': quiz_id})
#     return render_template('quiz_result.html', quiz_data=quiz['quiz_data'])

# @app.route('/history')
# @login_required
# def history():
#     user_quizzes = mongo.db.quizzes.find({'user_id': current_user.id})
#     return render_template('history.html', quizzes=user_quizzes)

@app.route('/logout')
# @login_required
def logout():
    # logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)