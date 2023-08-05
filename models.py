from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    """A model for a simple User in a web app"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, autoincrement=True,
                    primary_key=True)
    username = db.Column(db.String(30), unique=True,
                            nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), unique=True,
                            nullable=False)
    first_name = db.Column(db.String(30),
                            nullable=False)
    last_name = db.Column(db.String(30),
                            nullable=False)
    
    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """Create a new user and store a hashed version of their
        password"""
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, password=hashed_utf8,
                email=email, first_name=first_name, last_name=last_name)
        
    @classmethod
    def authenticate(cls, username, pw):
        """Validate that user exists & password is correct.

        Return user if valid; else return False."""
        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pw):
            return u
        else:
            return False
    
    def __init__(self, **kwargs):
        #Exclude the 'csrf_token' key from the kwargs
        kwargs.pop('csrf_token', None)
        kwargs.pop('confirm', None)
        super().__init__(**kwargs)
        #This won't hinder security, because the token is checked
        #before the Pet object is created

class Feedback(db.Model):
    """A model for storing feedback. Linked to a user"""

    __tablename__ = "feedback_table"
    id = db.Column(db.Integer, autoincrement=True,
                    primary_key=True)
    title = db.Column(db.String(100), nullable=False)

    content = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer,
                          db.ForeignKey('users.id'))
    author = db.relationship("User", backref="posts")