from flask import Flask
from sqlalchemy import DateTime, and_
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from datetime import datetime

from main import main

# настройка сервера Flask
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = '9QKKakkd0.api1ii2kkalofmqlo31miqmmfkTBo9lMaTbIIIJluxa'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['JSON_AS_ASCII'] = True
app.config['WTF_CSRF_ENABLED'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Qwerty123!@localhost:3306/db_majestic'
app.register_blueprint(main)

# получение достпука к бд через SQLAlchemy, также создание login manager
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# создание бд Users
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    discordid = db.Column(db.String(20), nullable=False, index=True)
    discordname = db.Column(db.String(45), nullable=False)
    static = db.Column(db.String(6), nullable=False, unique=True, index=True)
    nikname = db.Column(db.String(45), nullable=False)
    action = db.Column(db.String(20), nullable=False)
    prevrank = db.Column(db.String(3), nullable=False)
    rankuser = db.Column(db.String(3), nullable=False)
    organ = db.Column(db.String(10), nullable=False)
    timespan = db.Column(DateTime, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    create_document = db.relationship('PDFDocument', back_populates='user', foreign_keys='PDFDocument.user_static')
    permissions = db.relationship('PermissionUsers', back_populates='user', foreign_keys='PermissionUsers.user_static')

# создание бд Action Users
class ActionUsers(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    discordid = db.Column(db.String(20), nullable=False)
    discordname = db.Column(db.String(45), nullable=False)
    static = db.Column(db.String(6), nullable=False, unique=True)
    staticof = db.Column(db.String(6), nullable=False)
    nikname = db.Column(db.String(45), nullable=False)
    actionof = db.Column(db.String(20), nullable=False)
    prevrankof = db.Column(db.String(3), nullable=False)
    currrankof = db.Column(db.String(3), nullable=False)
    timespan = db.Column(DateTime, nullable=False)
    
class PermissionUsers(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_static = db.Column(db.String(6), db.ForeignKey('users.static'), nullable=False, unique=True)
    user_discordid = db.Column(db.String(20), db.ForeignKey('users.discordid'), nullable=False)
    tech = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)
    lider = db.Column(db.Boolean, default=False)
    high_staff = db.Column(db.Boolean, default=False)
    creation_doc = db.Column(db.Boolean, default=False)
    user = db.relationship('Users', back_populates='permissions', foreign_keys=[user_static])
    
class PDFDocument(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_static = db.Column(db.String(6), db.ForeignKey('users.static'), nullable=False)
    user_discordid = db.Column(db.String(32), db.ForeignKey('users.discordid'), nullable=False)
    uid = db.Column(db.String(26), unique=True, nullable=False)
    content = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    user = db.relationship('Users', back_populates='create_document', foreign_keys=[user_static])
    
class PublicDocumentAndNotificationsResolution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(26), unique=True, nullable=False)
    
    nickname_attorney = db.Column(db.String(52), nullable=False)
    static_attorney = db.Column(db.String(7), nullable=False)
    discord_attorney = db.Column(db.String(20),  nullable=False)
    
    nickname_accused = db.Column(db.String(52), default='Гражданин')
    static_accused = db.Column(db.String(7))
    discord_accused = db.Column(db.String(20))

    param_limit1 = db.Column(db.Boolean, default=False)
    param_limit2 = db.Column(db.Boolean, default=False)
    param_limit3 = db.Column(db.Boolean, default=False)
    param_limit4 = db.Column(db.Boolean, default=False)
    param_limit5 = db.Column(db.Boolean, default=False)
    param_limit6 = db.Column(db.Boolean, default=False)
    
    param_limit1_case = db.Column(db.String(20))
    param_limit2_nickmane = db.Column(db.String(52))
    param_limit2_time = db.Column(db.String(52))
    number_resolution = db.Column(db.String(4), default='0001')
    
    is_modertation = db.Column(db.Boolean, default=False)

class PublicDocumentAndNotificationsOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(26), unique=True, nullable=False)
    
    nickname_attorney = db.Column(db.String(52), nullable=False)
    static_attorney = db.Column(db.String(7), nullable=False)
    discord_attorney = db.Column(db.String(20),  nullable=False)
    
    nickname_accused = db.Column(db.String(52), default='Гражданин')
    static_accused = db.Column(db.String(7))
    discord_accused = db.Column(db.String(20))

    nameCrimeOrgan = db.Column(db.String(60), default='null')
    adreasCrimeOrgan = db.Column(db.String(60), default='null')
    offWork = db.Column(db.String(60), default='null')
    termImprisonment = db.Column(db.String(60), default='null')
    articlesAccusation = db.Column(db.String(60), default='null')
    time = db.Column(db.String(60), default='null')
    
    type_order = db.Column(db.String(20), nullable=False)
    number_order = db.Column(db.String(4), default='0001')
    
    is_modertation = db.Column(db.Boolean, default=False)
    
# создание бдешек
with app.app_context():
    db.create_all()
    
# получение user_id залогированного пользователя    
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)