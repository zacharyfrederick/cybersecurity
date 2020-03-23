from app import db
from datetime import datetime
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    tagline = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    salt = db.Column(db.String(100))
    image = db.Column(db.String(200))
    first_name = db.Column(db.String(40))
    last_name = db.Column(db.String(40))

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Chomp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)