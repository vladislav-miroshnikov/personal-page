from flask import Flask, render_template, redirect, url_for, request, session, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import requests
import json
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_url_path='',
            static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '8c6e8548b98042456995b42d1165d63e943cdf8554425452224073287d529d9b8938ea0f01eabed9'
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    vk_id = db.Column(db.String(255), unique=True, nullable=True)
    vk_access_token = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'User: {self.name}\n' \
               f'ID: {self.id}\n' \
               f'VK ID: {self.vk_id}\n' \
               f'Posted time: {self.vk_access_token}\n' \
               f'Time: {self.timestamp}\n' \


# class Posts(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255), nullable=False)
#     question = db.Column(db.String(1023), nullable=False)
#     question_time = db.Column(db.DateTime, default=datetime.utcnow)
#     answer = db.Column(db.String(1023), nullable=True)
#     answer_time = db.Column(db.DateTime, nullable=True)

#     def __repr__(self):
#         return f'Author: {self.name}\n' \
#                f'ID: {self.id}\n' \
#                f'Question: {self.question}\n' \
#                f'Posted time: {self.question_time}\n' \
#                f'Answer: {self.answer}\n' \
#                f'Posted time: {self.answer_time}\n'


@app.route("/")
def main_page():
    if not session.get('user_id') is None:
        # posts = Posts.query.all()
        return render_template("logout_index.html")
    return render_template('login_index.html')


@app.route("/botanic.html")
def botanic():
    return render_template('botanic.html')


@app.route("/navitas.html")
def navitas():
    return render_template('navitas.html')


@app.route("/miniCsharp.html")
def mini_csharp():
    return render_template('miniCsharp.html')


@app.route("/client-server.html")
def client_server():
    return render_template('client-server.html')


@app.route("/logout")
def logout():
    if not session.get('user_id'):
        return redirect(url_for('main_page'))
    session.pop('user_id', None)
    return redirect(url_for('main_page'))


@app.route("/vk_login")
def vk_login():
    code = request.args.get('code')

    if not code:
        return redirect(url_for('main_page'))

    response = requests.get(
        "https://oauth.vk.com/access_token?client_id=7811261&client_secret=Y6MK3wukOPGpjWDD1ODr&redirect_uri=http://127.0.0.1:5000/vk_login&code=" + code)
    vk_access_json = json.loads(response.text)

    if "error" in vk_access_json:
        return redirect(url_for('main_page'))

    vk_id = vk_access_json['user_id']
    access_token = vk_access_json['access_token']

    response = requests.get('https://api.vk.com/method/users.get?user_ids=' + str(
        vk_id) + '&fields=bdate&access_token=' + access_token + '&v=5.130')
    vk_user_json = json.loads(response.text)

    user = Users.query.filter_by(vk_id=vk_id).first()
    if user is None:
        name = vk_user_json['response'][0]['first_name'] + \
            " " + vk_user_json['response'][0]['last_name']
        new_user = Users(name=name, vk_id=vk_id, vk_access_token=access_token)
        try:
            db.session.add(new_user)
            db.session.commit()

        except SQLAlchemyError as err:
            db.session.rollback()
            error = str(err.dict['orig'])

            print(f"ERROR adding user to DB: {error}")

            return redirect(url_for('main_page'))

        user = Users.query.filter_by(vk_id=vk_id).first()

    session['user_id'] = user.id
    return redirect(url_for('main_page'))


# @app.route("/add_question", methods=["POST", "GET"])
# def add_question():
#     if not session.get('user_id'):
#         return redirect(url_for('main_page'))
#     if request.method == "POST":
#         if len(request.form['post']) > 2:
#             user_id = session.get('user_id')
#             user = Users.query.filter_by(id=user_id).first()
#             new_post = Posts(name=user.name, question=request.form['post'])
#             print(new_post.question)
#             try:
#                 db.session.add(new_post)
#                 db.session.commit()
#                 posts = Posts.query.all()
#                 return render_template("logout_index.html", posts=posts)
#             except SQLAlchemyError as err:
#                 db.session.rollback()
#                 error = str(err.dict['orig'])
#                 print(f"ERROR adding question to DB: {error}")
#         else:
#             flash('Cannot be less than 2 characters')


if __name__ == "__main__":
    app.run(debug=True, port=5000)
