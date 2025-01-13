from flask import Flask
from sqlalchemy import DateTime, func, Enum
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
import logging, uuid, os
from cryptography.fernet import Fernet  # type: ignore
from datetime import timedelta
import pytz

from limiter import limiter
from main import main

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = '9QKKakkd0.api1ii2kkalofmqlo31miqmmfkTBo9lMaTbIIIJluxa'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['WTF_CSRF_ENABLED'] = True
app.config['DEBUG'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Qwerty123!@localhost:3306/db_majestic'
app.config['FERNET_KEY'] = b'RZP6DxiYrL_hz7fX1IN0v4YAtfMwwz5Gp53JRVvLw6M='
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)

app.config['UPLOAD_FOLDER'] = 'static/uploads/images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

cipher = Fernet(app.config['FERNET_KEY'])
limiter.init_app(app)
app.register_blueprint(main)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
moscow_tz = pytz.timezone('Europe/Moscow')

def generate_uid():
    return str(uuid.uuid4()).replace("-", "")[:16]

def get_next_id_user():
    last_id_user = db.session.query(func.max(Users.id)).scalar()
    last_id_guest = db.session.query(func.max(guestUsers.id)).scalar()

    if not last_id_user:
        return (last_id_guest or 0) + 1
    
    if not last_id_guest:
        return (last_id_user or 0) + 1

    if last_id_user > last_id_guest:
        return (last_id_user or 0) + 1

    return (last_id_guest or 0) + 1

def get_next_num_resolution():
    last_custom = db.session.query(func.max(CustomResolutionTheUser.current_number)).scalar()
    last_resolution = db.session.query(func.max(ResolutionTheUser.current_number)).scalar()

    if not last_custom:
        return (last_resolution or 0) + 1
    
    if not last_resolution:
        return (last_custom or 0) + 1

    if last_custom > last_resolution:
        return (last_custom or 0) + 1

    return (last_resolution or 0) + 1
    
def get_next_num_order():
    last_order = db.session.query(func.max(OrderTheUser.current_number)).scalar()
    return (last_order or 0) + 1

def get_next_id_permission():
    last_id = db.session.query(func.max(PermissionUsers.id)).scalar()
    return (last_id or 0) + 1

def get_next_id_isk():
    last_id = db.session.query(func.max(claimsStatement.id)).scalar()
    return (last_id or 0) + 1

class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    user_type = db.Column(db.String(10), default='user')

    id = db.Column(db.Integer, primary_key=True)
    discordid = db.Column(db.BigInteger, nullable=False)
    discordname = db.Column(db.String(45), nullable=False)
    static = db.Column(db.Integer, nullable=False, unique=True)
    nikname = db.Column(db.String(45), nullable=False)
    action = db.Column(db.String(20), nullable=False)
    prev_rank = db.Column(db.Integer, nullable=False)
    curr_rank = db.Column(db.Integer, nullable=False)
    organ = db.Column(db.String(10), nullable=False)
    YW = db.Column(db.Integer, nullable=False, default=0)
    SW = db.Column(db.Integer, nullable=False, default=0)
    password = db.Column(db.String(255), nullable=False)
    url_image = db.Column(db.String(255), nullable=True)

    @property
    def is_guest(self):
        return False

    permissions = db.relationship('PermissionUsers', back_populates='user')
    custom_resolution = db.relationship('CustomResolutionTheUser', back_populates='user')
    resolution = db.relationship('ResolutionTheUser', back_populates='user')
    create_document = db.relationship('PDFDocument', back_populates='user')
    action_log = db.relationship('ActionUsers', back_populates='user')
    order = db.relationship('OrderTheUser', back_populates='user')
    news = db.relationship('News', back_populates='user')


class guestUsers(db.Model, UserMixin):
    __tablename__ = 'guest_users'

    user_type = db.Column(db.String(10), default='guest')

    id = db.Column(db.Integer, primary_key=True, default=get_next_id_user)
    discord_id = db.Column(db.BigInteger, nullable=False)
    static = db.Column(db.Integer, nullable=False, unique=True)
    nickname = db.Column(db.String(45), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    url_image = db.Column(db.String(255), nullable=True)

    @property
    def is_guest(self):
        return True

    permissions = db.relationship('PermissionUsers', back_populates='guest_user')     

class PermissionUsers(db.Model, UserMixin):
    __tablename__ = 'permission'

    id = db.Column(db.Integer, primary_key=True, default=get_next_id_permission)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest_users.id'), unique=True)

    tech = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)
    lider = db.Column(db.Boolean, default=False)
    dep_lider = db.Column(db.Boolean, default=False)
    high_staff = db.Column(db.Boolean, default=False)
    creation_doc = db.Column(db.Boolean, default=False)
    create_news = db.Column(db.Boolean, default=False)
    judge = db.Column(db.Boolean, default=False)
    lawyer = db.Column(db.Boolean, default=False)
    prosecutor = db.Column(db.Boolean, default=False)

    user = db.relationship('Users', back_populates='permissions')
    guest_user = db.relationship('guestUsers', back_populates='permissions')

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
    timespan = db.Column(db.DateTime, default=lambda: datetime.now(moscow_tz))

    user = db.relationship('Users', back_populates='action_log')

class PDFDocument(db.Model, UserMixin):
    __tablename__ = 'pdf_document'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    uid = db.Column(db.String(26), unique=True, nullable=False)
    content = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(moscow_tz))

    custom_resolution = db.relationship('CustomResolutionTheUser', back_populates='current_document')
    resolution = db.relationship('ResolutionTheUser', back_populates='current_document')
    user = db.relationship('Users', back_populates='create_document')
    order = db.relationship('OrderTheUser', back_populates='current_document')


class CustomResolutionTheUser(db.Model):
    __tablename__ = 'customer_resolution'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    current_uid = db.Column(db.String(26), db.ForeignKey('pdf_document.uid'), nullable=False)
    current_number = db.Column(db.Integer)

    custom_fields = db.Column(db.JSON)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(moscow_tz))
    is_modertation = db.Column(db.Boolean, default=False)

    user = db.relationship('Users', back_populates='custom_resolution')
    current_document = db.relationship('PDFDocument', back_populates='custom_resolution')
    
class ResolutionTheUser(db.Model):
    __tablename__ = 'resolution'

    id = db.Column(db.Integer, primary_key=True)
    current_uid = db.Column(db.String(26), db.ForeignKey('pdf_document.uid'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    current_number = db.Column(db.Integer)

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

    date_created = db.Column(db.DateTime, default=lambda: datetime.now(moscow_tz))
    is_modertation = db.Column(db.Boolean, default=False)

    user = db.relationship('Users', back_populates='resolution')
    current_document = db.relationship('PDFDocument', back_populates='resolution')


class OrderTheUser(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    current_uid = db.Column(db.String(26), db.ForeignKey('pdf_document.uid'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    current_number = db.Column(db.Integer)

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

    date_created = db.Column(db.DateTime, default=lambda: datetime.now(moscow_tz))
    is_modertation = db.Column(db.Boolean, default=False)

    current_document = db.relationship('PDFDocument', back_populates='order')
    user = db.relationship('Users', back_populates='order')


class News(db.Model):
    __tablename__ = 'news'
    
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type_news = db.Column(Enum('admin-news', 'govenor-news', 'weazel-news', name='news_type'), nullable=False)
    
    heading = db.Column(db.String(100), nullable=False)
    brief_content = db.Column(db.Text, nullable=False)
    full_content = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(255))
    timespan = db.Column(db.DateTime, default=lambda: datetime.now(moscow_tz))
    
    user = db.relationship('Users', back_populates='news')
    
class claimsStatement(db.Model):
    __tablename__ = 'court_claims'

    id = db.Column(db.Integer, primary_key=True, default=get_next_id_isk)
    uid = db.Column(db.String(16), unique=True, default=generate_uid)
    create_at = db.Column(db.DateTime, default=lambda: datetime.now(moscow_tz))
    date_court_session = db.Column(db.DateTime, nullable=True)
    criminal_case = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)

    reply = db.relationship('repltoisks', back_populates='current_claim')
    district_court = db.relationship('iskdis', back_populates='current_claim', foreign_keys='iskdis.current_uid') 
    supreme_court = db.relationship('isksup', back_populates='current_claim', foreign_keys='isksup.current_uid')  
    court_order = db.relationship('courtOrder', back_populates='current_claim')


class iskdis(db.Model):
    __tablename__ = 'district_court'

    id = db.Column(db.Integer, primary_key=True)
    current_uid = db.Column(db.String(16), db.ForeignKey('court_claims.uid'), unique=True)
    judge = db.Column(db.Integer)
    discription = db.Column(db.Text, nullable=True)
    claims = db.Column(db.PickleType, nullable=True)
    phone = db.Column(db.String(12), nullable=True)
    cardn = db.Column(db.String(15), nullable=True)
    created = db.Column(db.Integer, nullable=False)
    defendant = db.Column(db.PickleType)
    prosecutor = db.Column(db.Integer)
    lawerc = db.Column(db.String(45))
    lawerd = db.Column(db.String(45))
    otherme = db.Column(db.PickleType, nullable=True)
    status = db.Column(db.String(15), default='Waitting')
    evidence = db.Column(db.PickleType, nullable=True)
    
    type_criminal = db.Column(db.Boolean, default=False)
    link_case = db.Column(db.String(256), nullable=True)
    date_case = db.Column(db.String(256), nullable=True)

    current_claim = db.relationship('claimsStatement', back_populates='district_court')


class isksup(db.Model):
    __tablename__ = 'supreme_court'

    id = db.Column(db.Integer, primary_key=True)
    current_uid = db.Column(db.String(16), db.ForeignKey('court_claims.uid'), unique=True)
    judge = db.Column(db.Integer)
    discription = db.Column(db.Text, nullable=True)
    claims = db.Column(db.PickleType, nullable=True)
    phone = db.Column(db.String(12), nullable=True)
    cardn = db.Column(db.String(15), nullable=True)
    created = db.Column(db.Integer, nullable=False)
    defendant = db.Column(db.PickleType)
    prosecutor = db.Column(db.Integer)
    lawerc = db.Column(db.String(45))
    lawerd = db.Column(db.String(45))
    otherme = db.Column(db.PickleType, nullable=True)
    status = db.Column(db.String(15), default='Waitting')
    evidence = db.Column(db.PickleType, nullable=True)
    
    type_criminal = db.Column(db.Boolean, default=False)
    link_case = db.Column(db.String(256), nullable=True)
    date_case = db.Column(db.String(256), nullable=True)

    current_claim = db.relationship('claimsStatement', back_populates='supreme_court')


class repltoisks(db.Model):
    __tablename__ = 'replto_claims'

    id = db.Column(db.Integer, primary_key=True)
    current_uid = db.Column(db.String(16), db.ForeignKey('court_claims.uid'), nullable=False)
    author_id = db.Column(db.String(45), nullable=False)

    replyik = db.Column(db.PickleType, nullable=False)
    moderation = db.Column(db.Boolean, default=False)
    type_doc = db.Column(db.String(45), nullable=False)

    timespan = db.Column(db.DateTime, default=lambda: datetime.now(moscow_tz))

    current_claim = db.relationship('claimsStatement', back_populates='reply')

class courtOrder(db.Model):
    __tablename__ = 'court_order'

    id = db.Column(db.Integer, primary_key=True)
    current_uid = db.Column(db.String(16), db.ForeignKey('court_claims.uid'), nullable=False)
    author_id = db.Column(db.String(6), nullable=False)

    findings = db.Column(db.PickleType, nullable=False)
    consideration = db.Column(db.PickleType, nullable=False)
    ruling = db.Column(db.PickleType, nullable=False)
    other = db.Column(db.String(256), nullable=True)

    type_doc = db.Column(db.String(45), nullable=False)

    timespan = db.Column(db.DateTime, default=lambda: datetime.now(moscow_tz))

    current_claim = db.relationship('claimsStatement', back_populates='court_order')

class courtPrecedents(db.Model):
    __tablename__ = 'court_precedents'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.String(6), nullable=False)
    
    number_complaint = db.Column(db.String(256), nullable=False)
    date_complaint = db.Column(db.DateTime, nullable=False)
    link = db.Column(db.String(256), nullable=False)
    author = db.Column(db.String(256), nullable=False)
    findings = db.Column(db.PickleType, nullable=False)
    court = db.Column(db.String(256), nullable=False)
    
    timespan = db.Column(db.DateTime, default=lambda: datetime.now(moscow_tz))
    
class permissionRoles(db.Model):
    __tablename__ = 'permission_roles'
    id = db.Column(db.Integer, primary_key=True)

    fraction = db.Column(db.String(45), nullable=False)
    position_rank = db.Column(db.Integer, nullable=False)
    roles = db.Column(db.PickleType, nullable=False)
    
# Создание таблиц базы данных
with app.app_context():
    db.create_all()
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(10))
    print(password)
    
    hash_password = generate_password_hash(password)
    new_user = Users(
        id = get_next_id_user(),
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

@login_manager.user_loader
def load_user(user_id):
    user = Users.query.get(user_id) 
    if user and user.action != 'Dismissal':
        return user

    guest = guestUsers.query.get(user_id)
    if guest:
        return guest

    return None
