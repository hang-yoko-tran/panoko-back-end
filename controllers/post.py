from flask import Blueprint, request, url_for, render_template, flash, redirect, jsonify
from app.models import User, Token, Post
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


@app.route('/posts/<id>', methods=['POST', 'GET'])
def single_post(id):
    action = request.args.get('action')
    post = Post.query.get(id)
    post.view_count += 1
    db.session.commit()
    # comments = Comment.query.filter_by(post_id=id).all()
    if not post:
        flash('Post not found', 'warning')
        return redirect(url_for('root'))
    post.author = User.query.get(post.user_id)
    if request.method == "POST":
        if post.user_id != current_user.id:
            flash('not allow to do this', 'danger')
            return redirect(url_for('root'))
        if action == 'delete':
            db.session.delete(post)
            db.session.commit()
            return redirect(url_for('root'))
        elif action == 'update':
            post.body = request.form['body']
            db.session.commit()
            return redirect(url_for('single_post', id=id))
        elif action == 'edit':
            return render_template('views/single_post.html', post=post, action=action)
    if not action:
        action = 'view' 

    for comment in comments:
        # import code; code.interact(local=dict(globals(), **locals()))
        comment.user_name = User.query.get(comment.user_id).name
    return render_template('views/single_post.html', post=post, action=action, comments=comments)




