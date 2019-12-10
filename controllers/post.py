from flask import Blueprint, request, url_for, render_template, flash, redirect, jsonify
from app.models import *
from flask_login import login_required, login_user, logout_user, current_user
from app import db
from itsdangerous import URLSafeTimedSerializer
import requests, json
from app import app


post_blueprint = Blueprint(
    'post_bp', __name__, template_folder='../../templates')

@post_blueprint.route('/', methods=['GET','POST'])
def create_post():
    if request.method == "GET":
        if current_user.is_authenticated:
            posts = [ post.get_json(id=current_user.id) for post in Post.query.all() ]
        else:
            posts = [ post.get_json() for post in Post.query.all() ]
        return jsonify(posts)

    if request.method == 'POST':
        data = request.get_json()
        print(data)
        new_post = Post(title=data['title'],
                        image_url=data['img_url'],
                        body=data['description'],
                        user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        return jsonify({"status": "OK"})


@app.route('/post/<id>', methods=['POST', 'GET'])
def single_post(id):
    if request.method == "GET":
        fucking_post = Post.query.get(int(id))
        return jsonify(fucking_post.get_json())

@app.route('/post/<id>/like', methods=['GET'])
def add_like(id):
    if request.method == "GET":
        fucking_like = Like.query.filter_by(user_id=current_user.id).filter_by(post_id=id).first()
        if not fucking_like:
            Faggot_new_like = Like(user_id=current_user.id, post_id=id)
            db.session.add(Faggot_new_like)
            db.session.commit()
            return jsonify({"status":"OK"})
        db.session.delete(fucking_like)
        db.session.commit()
        return jsonify({"status": "KO"})


# @app.route('/posts/<id>/comments', methods=['POST', 'GET'])
# def create_comment(id):
#     if request.method == 'POST':

#         comment = Comment(user_id=current_user.id, 
#                     post_id=id,
#                     body=request.form['body'],)
#         db.session.add(comment)
#         db.session.commit()
#     return jsonify()




# @app.route('/post/<id>/comment', methods=["GET", "POST"])
# def ThisIsAReallyGoodMethodNameUKnow(id):
#     if request.method == "POST":
#         data = request.get_json()
#         return jsonify()



