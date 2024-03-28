from flask_sqlalchemy import SQLAlchemy, inspect
from flask_login import UserMixin
from flask import request, current_app as app, make_response, jsonify
from functools import wraps
import jwt
from datetime import datetime
from uuid import uuid4  





db = SQLAlchemy()

class Credentials(db.Model):
    __tablename__ = 'credentials'
    email_id = db.Column(db.String, primary_key=True,
                         nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    last_login = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "user.user_id"), nullable=False, unique=True)
    is_admin = db.Column(db.String, nullable=True,default=None)
    request = db.Column(db.String, nullable=True, default=None)
    owner = db.Column(db.String, nullable=True, default =None)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True,
                        nullable=False, unique=True, autoincrement=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    credential = db.relationship('Credentials', backref='user', uselist=False)



class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    items = db.relationship('Item', backref='category', lazy=True)

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    stock_left = db.Column(db.Integer,nullable= False)
    image_url = db.Column(db.String(200))
    expiration_date = db.Column(db.String , nullable=True)

    def __repr__(self):
        return self.name




def get_item_by_id(item_id):

    item = Item.query.get(item_id)
    return item



class Order(db.Model):
    order_id = db.Column(db.String(150), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(100), nullable=False)
    items_data = db.Column(db.Text, nullable=False)  # JSON data for the order items
    total_price = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)


class Approval(db.Model):
    __tablename__ = 'approvals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)





class Trackers(db.Model):
    __tablename__ = 'trackers'
    track_id = db.Column(db.Integer, primary_key=True,
                         nullable=False, unique=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "user.user_id"), nullable=False)
    track_name = db.Column(db.String, nullable=False)
    track_desc = db.Column(db.String, nullable=False)
    track_type = db.Column(db.String, db.CheckConstraint(
        "track_type in ('num','mcq','time','bool')"), nullable=False)
    options = db.Column(db.String, nullable=False)


class Logs(db.Model):
    __tablename__ = 'logs'
    log_id = db.Column(db.Integer, nullable=False, primary_key=True)
    track_id = db.Column(db.Integer, db.ForeignKey(
        "trackers.track_id"), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    info = db.Column(db.String, nullable=False)


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        print(token)
        if not token:
            return make_response(jsonify({"message": "A valid token is missing!"}), 401)
        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except Exception as e:
            return make_response(jsonify({"message": "Invalid token!"}), 401)
        print("user_id:",data['user_id'])
        return f(data['user_id'], *args, **kwargs)
    
    return decorator
