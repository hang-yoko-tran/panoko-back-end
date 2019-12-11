from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from flask import request
db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__="users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True)
    firstname = db.Column(db.String(256))
    lastname = db.Column(db.String(256))
    image_url = db.Column(db.Text)
    password = db.Column(db.String(256))
    posts = db.relationship("Comment", backref="user", lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_json(self):
        return {
            "id": self.id,
            "email": self.email,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "password": self.password
        }

class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User)


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User)

    def create_token(self, current_user_id ):
        token = Token(user_id=current_user_id, uuid=str(uuid.uuid4().hex))
        db.session.add(token)
        db.session.commit()
        return token

# note
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.String, nullable=False)
    image_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    view_count = db.Column(db.Integer, default=0)
    comments = db.relationship("Comment", backref="post", lazy=True)
    def get_json(self, id=None):
        if not current_user.is_authenticated:
            return {
                "id": self.id,
                "title": self.title,
                "comments": [ comment.get_json() for comment in self.comments ],
                "body": self.body,
                "image_url": self.image_url,
                "view_count": self.view_count,
                "author": User.query.get(self.user_id).get_json(),
                "created_at": self.created_at.strftime("%d-%b-%Y"),
                "isLiked": False
            }
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "comments": [ comment.get_json() for comment in self.comments ],
            "image_url": self.image_url,
            "view_count": self.view_count,
            "author": User.query.get(self.user_id).get_json(),
            "created_at": self.created_at.strftime("%d-%b-%Y"),
            "isLiked": bool(Like.query.filter_by(user_id=current_user.id).filter_by(post_id=self.id).first())
            # "created_at": self.created_at.strftime("%d-%b-%Y (%H:%M:%S.%f)")
        }


class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'),nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def get_json(self):
        return {
            "id": self.id,
            "body": self.body,
            "user_id": self.user_id,
            "post_id": self.post_id,
            "created_at": self.created_at.strftime("%d-%b-%Y"),
            "user": self.user.get_json()
        }


# note

# setup login manager
login_manager = LoginManager()
login_manager.login_view = "facebook.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Token ', '', 1)
        token = Token.query.filter_by(uuid=api_key).first()
        if token:
            return token.user
    return None