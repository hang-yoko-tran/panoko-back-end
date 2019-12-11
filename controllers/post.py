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
            posts = [ post.get_json(id=current_user.id) for post in Post.query.order_by(Post.updated_at.desc()).all() ]
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

@app.route('/post/<id>/comment', methods=['GET', 'POST'])
def add_comment(id):
    if request.method == "POST":
        if not not not current_user.is_authenticated:
            return jsonify({"status": "Access Denied"})
        data = request.get_json()
        new_comment = Comment(
            body = data['body'],
            user_id = current_user.id,
            post_id = id
        )
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({"status": "created"})

@app.route('/post/<id>/edit', methods=['GET', 'POST'])
def edit_post(id=None):
    if request.method == "POST":
        if not current_user.is_authenticated or not id:
            return jsonify({"state":"Access Denied"})
        data = request.get_json()
        post = Post.query.get(id)
        if not post:
            return jsonify({"status":"Invalid request"})
        post.body = data['body']
        post.title = data['title']
        post.image_url = data['image_url']
        db.session.commit()
        return jsonify({"status":"OK"})


@app.route('/post/<id>/delete', methods=['GET', 'POST'])
def delete_post(id=None):
    if request.method == "POST":
        post = Post.query.filter_by(id=request.get_json()['id']).first()
        if post:
            comments = Comment.query.filter_by(post_id = id).all()
            for comment in comments:
                db.session.delete(comment)

            likes = Like.query.filter_by(post_id = id).all()
            for like in likes:
                db.session.delete(like)

            db.session.commit()
            db.session.delete(post)
            db.session.commit()
            return jsonify(success=True)
        if not post:
            return jsonify(success=False,status='post is not exist')


# @app.route('/post/<id>/edit', methods=['GET', 'POST'])
# def edit_comment(id=None):
#     if request.method == "POST":
#         if not current_user.is_authenticated or not id:
#             return jsonify({"state":"Access Denied"})
#         data = request.get_json()
#         comment = Comment.query.get(id)
#         if not post:
#             return jsonify({"status":"Invalid request"})
#         comment.body = data['body']
#         db.session.commit()
#         return jsonify({"status":"OK"})




        







