from __init_app__ import app
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import UserMixin

db=SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"]=config['DATABASE_URI']
db.init_app(app)
app.app_context().push()

class User(db.Model, UserMixin):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(8))
    tfirs = db.relationship('TheftFir', backref='user', order_by='desc(TheftFir.ftime)')

    def get_role(self):
            return self.role

class TheftFir(db.Model):
    __tablename__='theft_fir'
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    ftime=db.Column(db.DateTime, nullable=False)
    username=db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    cname=db.Column(db.String, nullable=False)
    pname=db.Column(db.String, nullable=False)
    address=db.Column(db.String, nullable=False)
    mob=db.Column(db.String, nullable=False)
    email=db.Column(db.String, nullable=False)
    place=db.Column(db.String, nullable=False)
    datetime=db.Column(db.String, nullable=False)
    aname=db.Column(db.String, nullable=False)
    description=db.Column(db.String, nullable=False)
    closed=db.Column(db.Integer, nullable=False)

class Actions(db.Model):
    __tablename__='actions'
    id=db.Column(db.Integer, db.ForeignKey('theft_fir.id'), primary_key=True)
    accepted=db.Column(db.Boolean)
    accepted_timeStamp=db.Column(db.DateTime)
    rejected=db.Column(db.Boolean)
    rejected_timeStamp=db.Column(db.DateTime)
    closed_timeStamp=db.Column(db.DateTime)
    remarks=db.Column(db.String)
