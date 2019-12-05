from flask import Blueprint, request, url_for, render_template, flash, redirect, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from app.models import User, Token
from app import db, login_manager
from itsdangerous import URLSafeTimedSerializer
import requests
from app import app


user_blueprint = Blueprint(
    'user_bp', __name__, template_folder='../../templates')


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


@user_blueprint.route('/get_user')
@login_required
def get_user():
    return jsonify(user={"id":current_user.id, "email":current_user.email})


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.get_json()['email']
        firstname = request.get_json()['firstname']
        lastname = request.get_json()['lastname']
        password = request.get_json()['password']
        check_email = User.query.filter_by(email=email).first()
        if check_email:
            return jsonify({"code": 409})
        else:
            new_user = User(
                email=email, firstname=firstname, lastname=lastname)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"code": 200})
    return redirect('https://localhost:3000/signin')


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.get_json()['email']
        password = request.get_json()['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) :
            login_user(user)
            token = Token()
            token = token.create_token(current_user.id)
            return jsonify({"code" : 200, "user": {"id":current_user.id, "email":current_user.email}, "apiKey": token.uuid})
        return jsonify({"code" : 401})


@user_blueprint.route('/logout')
@login_required
def logout():
    api_key = request.headers.get('Authorization').replace('Token ', '', 1)
    token = Token.query.filter_by(uuid=api_key).first()
    if token:
        db.session.delete(token)
        db.session.commit()
        logout_user()
        return jsonify({"code" : 200})
    return jsonify({"code" : 400})


def send_email(token, email, name):
    url = "https://api.mailgun.net/v3/sandbox1c23cd42dd8b4da093bdfd114f176194.mailgun.org/messages"
    response = requests.post(url,
                             auth=("api", app.config['EMAIL_API']),
                             data={"from": "Hang Yoko <hang.yoko.tran@gmail.com>",
                                   "to": [email],
                                   "subject": "Reset Password",
                                   "text": f"Go to https://localhost:3000/new-password/{token}"})

    print(response)

@user_blueprint.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    # if current_user.is_authenticated:
    #     return redirect(url_for('root'))
    if request.method == 'POST':
        email = request.get_json()['email']
        user = User.query.filter_by(email=email).first()
        if not user:
            # flash('ACCOUTN DOES NOT EXIST', 'danger')
            # return redirect(url_for('user_bp.forgot_password'))
            print("Email not exist!")
            return jsonify({"code": 404})
        s = URLSafeTimedSerializer(app.secret_key)
        token = s.dumps(user.email, salt="UMEO")       
        name = f'{user.firstname} {user.lastname}'
        print("TOKEN:", token)
        print("EMAIL", user.email)
        send_email(token, user.email, name)
       
        return jsonify({"code": 200})
    # return ('user/forgot_password.html')

@user_blueprint.route('/new-password/<token>', methods=['POST'])
def new_password(token):
    print("TOKEN: ", token)
    try:
        s = URLSafeTimedSerializer(app.secret_key)
        email = s.loads(token, salt="UMEO", max_age=3000)
    except:
        print("Invalid token")
        return jsonify({"code": 404})
    
    print("EMAIL", email)
        
    if request.method == "POST":
        if request.get_json()['password'] != request.get_json()['confirm_password']:
            print('Password not match!')
            return jsonify({"code": 400})
        user = User.query.filter_by(email=email).first()
        user.set_password(request.get_json()['password'])
        db.session.commit()
        flash("You have set new password", "successful")
        return jsonify({"code": 200})