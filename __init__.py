from flask import Flask
from sqlalchemy import DateTime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager

from main import main

# настройка сервера Flask
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = '9QKKakkd0.api1ii2kkalofmqlo31miqmmfkTBo9lMaTbIIIJluxa'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Qwerty123!@localhost:3306/db_majestic'
app.register_blueprint(main)

# получение достпука к бд через SQLAlchemy, также создание login manager
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# создание бд Users
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    discordid = db.Column(db.String(18), nullable=False)
    discordname = db.Column(db.String(45), nullable=False)
    static = db.Column(db.String(6), nullable=False, unique=True)
    nikname = db.Column(db.String(45), nullable=False)
    action = db.Column(db.String(20), nullable=False)
    prevrank = db.Column(db.String(3), nullable=False)
    rankuser = db.Column(db.String(3), nullable=False)
    organ = db.Column(db.String(10), nullable=False)
    timespan = db.Column(DateTime, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# создание бд Action Users
class ActionUsers(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    discordid = db.Column(db.String(18), nullable=False)
    discordname = db.Column(db.String(45), nullable=False)
    static = db.Column(db.String(6), nullable=False)
    staticof = db.Column(db.String(6), nullable=False)
    nikname = db.Column(db.String(45), nullable=False)
    actionof = db.Column(db.String(20), nullable=False)
    prevrankof = db.Column(db.String(3), nullable=False)
    currrankof = db.Column(db.String(3), nullable=False)
    timespan = db.Column(DateTime, nullable=False)

# создание бдешек
with app.app_context():
    db.create_all()

# получение user_id залогированного пользователя    
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)