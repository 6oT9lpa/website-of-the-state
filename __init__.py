from flask import Flask
from sqlalchemy import DateTime, func
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from datetime import datetime
import logging

from main import main

from flask import render_template, redirect, url_for, request, flash, Blueprint, session, send_file, make_response, jsonify, abort
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash
from form import FormAuditPush, FormAuthPush, Formchangepassword, Formforgetpassword1, Formforgetpassword2
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from textwrap import wrap
from PyPDF2 import PdfReader, PdfWriter
import random, string, redis, json, os, re, shutil, logging, json
from logging import handlers


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = '9QKKakkd0.api1ii2kkalofmqlo31miqmmfkTBo9lMaTbIIIJluxa'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
app.config['JSON_AS_ASCII'] = True
app.config['WTF_CSRF_ENABLED'] = True 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Qwerty123!@localhost:3306/db_majestic'
app.config['DEBUG'] = False
app.register_blueprint(main)

db = SQLAlchemy(app)
login_manager = LoginManager(app)

def get_next_id_user():
    last_id = db.session.query(func.max(Users.id)).scalar()
    return (last_id or 0) + 1

def get_next_id_permission():
    last_id = db.session.query(func.max(PermissionUsers.id)).scalar()
    return (last_id or 0) + 1

class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    discordid = db.Column(db.BigInteger, nullable=False)
    discordname = db.Column(db.String(45), nullable=False)
    static = db.Column(db.Integer, nullable=False, unique=True)
    nikname = db.Column(db.String(45), nullable=False)
    action = db.Column(db.String(20), nullable=False)
    prev_rank = db.Column(db.Integer, nullable=False)
    curr_rank = db.Column(db.Integer, nullable=False)
    organ = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    permissions = db.relationship('PermissionUsers', back_populates='user')
    custom_resolution = db.relationship('CustomResolutionTheUser', back_populates='user')
    resolution = db.relationship('ResolutionTheUser', back_populates='user')
    create_document = db.relationship('PDFDocument', back_populates='user')
    action_log = db.relationship('ActionUsers', back_populates='user')
    order = db.relationship('OrderTheUser', back_populates='user')

class PermissionUsers(db.Model, UserMixin):
    __tablename__ = 'permission'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    tech = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)
    lider = db.Column(db.Boolean, default=False)
    high_staff = db.Column(db.Boolean, default=False)
    creation_doc = db.Column(db.Boolean, default=False)

    user = db.relationship('Users', back_populates='permissions')

class ActionUsers(db.Model, UserMixin):
    __tablename__ = 'action_user' 
    
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    discordid = db.Column(db.BigInteger, nullable=False)
    discordname = db.Column(db.String(45), nullable=False)
    static = db.Column(db.Integer, nullable=False)
    nikname = db.Column(db.String(45), nullable=False)
    action = db.Column(db.String(20), nullable=False)
    prev_rank = db.Column(db.Integer, nullable=False)
    curr_rank = db.Column(db.Integer, nullable=False)
    timespan = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('Users', back_populates='action_log')

class PDFDocument(db.Model, UserMixin):
    __tablename__ = 'pdf_document'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    uid = db.Column(db.Integer, unique=True, nullable=False)
    content = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    custom_resolution = db.relationship('CustomResolutionTheUser', back_populates='current_document')
    resolution = db.relationship('ResolutionTheUser', back_populates='current_document')
    user = db.relationship('Users', back_populates='create_document')
    order = db.relationship('OrderTheUser', back_populates='current_document')

class ResolutionNumberCounter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_number = db.Column(db.Integer, default=1, nullable=False)

    @classmethod
    def increment(cls, session):
        counter = session.query(cls).first()
        if not counter:
            counter = cls(current_number=1)
            session.add(counter)
            session.commit()
            logging.info("Initialized current_number with 1")
        else:
            counter.current_number += 1
            session.commit()
            logging.info(f"Incremented current_number to {counter.current_number}")
        return counter.current_number

class CustomResolutionTheUser(db.Model):
    __tablename__ = 'customer_resolution'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    current_uid = db.Column(db.Integer, db.ForeignKey('pdf_document.uid'), nullable=False)

    custom_fields = db.Column(db.JSON)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    is_modertation = db.Column(db.Boolean, default=False)

    user = db.relationship('Users', back_populates='custom_resolution')
    current_document = db.relationship('PDFDocument', back_populates='custom_resolution')
    
class ResolutionTheUser(db.Model):
    __tablename__ = 'resolution'

    id = db.Column(db.Integer, primary_key=True)
    current_uid = db.Column(db.Integer, db.ForeignKey('pdf_document.uid'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    nickname_accused = db.Column(db.String(52), default='Гражданин')
    static_accused = db.Column(db.String(7))
    discord_accused = db.Column(db.String(20))

    initiation_case = db.Column(db.Boolean, default=False)
    number_case = db.Column(db.String(20))
    provide_video = db.Column(db.Boolean, default=False)
    victim_nickname = db.Column(db.String(52))
    time_arrest = db.Column(db.String(52))
    provide_personal_file = db.Column(db.Boolean, default=False)
    changing_personal_data = db.Column(db.Boolean, default=False)
    dismissal_employee = db.Column(db.Boolean, default=False)
    temporarily_suspend = db.Column(db.Boolean, default=False)

    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    is_modertation = db.Column(db.Boolean, default=False)

    user = db.relationship('Users', back_populates='resolution')
    current_document = db.relationship('PDFDocument', back_populates='resolution')

class OrderTheUser(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    current_uid = db.Column(db.Integer, db.ForeignKey('pdf_document.uid'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
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
    
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    is_modertation = db.Column(db.Boolean, default=False)

    current_document = db.relationship('PDFDocument', back_populates='order')
    user = db.relationship('Users', back_populates='order')

class News(db.Model):
    __tablename__ = 'news'
    
    id = db.Column(db.Integer, primary_key=True)
    typenews = db.Column(db.String(10), nullable=False)
    created_by = db.Column(db.String(45), nullable=False)
    headernews = db.Column(db.String(100), nullable=False)
    textnews = db.Column(db.Text, nullable=False)
    
# Создание таблиц базы данных
with app.app_context():
    db.create_all()
    
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(10))
    print(password)
    
    hash_password = generate_password_hash(password)
    new_user = Users(
        id = get_next_id(),
        discordid="762514681209946122",
        discordname="6ot9lpa",
        static="77857",
        nikname="6ot9lpa",
        action="Invite",
        prev_rank="0",
        curr_rank="21",
        organ="GOV",
        password=hash_password
    )
    db.session.add(new_user)
    db.session.commit()

    user = Users.query.filter_by(static=77857).first()
    permission_entry = PermissionUsers(
        author_id=user.id,
        tech=True, 
        admin=True,
        lider=True,
        high_staff=False,
        creation_doc=True
    )
    db.session.add(permission_entry)
    db.session.commit()
    """

# Функция загрузки пользователя
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)
