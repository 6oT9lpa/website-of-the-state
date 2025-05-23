from flask import render_template, redirect, url_for, request, flash, Blueprint, session, jsonify, abort
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from form import FormAuthPush
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from textwrap import wrap
from PyPDF2 import PdfReader, PdfWriter # type: ignore
import random, string, redis, json, os, re, shutil, logging, json
import base64, random, uuid
import requests

from limiter import limiter

"""
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Создаем обработчик для записи в файл
    handler = handlers.RotatingFileHandler('debug.txt', maxBytes=10*1024*1024, backupCount=5)
    handler.setLevel(logging.DEBUG)

    # Форматирование логов в JSON
    def json_formatter(record):
        log_record = {
            'levelname': record.levelname,
            'message': record.getMessage(),
            'time': record.asctime,
            'name': record.name,
            'filename': record.pathname,
            'line': record.lineno,
        }
        return json.dumps(log_record)

    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

setup_logging()
"""

def givenewmerole(newmerole):
  if newmerole == "svidetel":
    return "Свидетель"
  elif newmerole == "expert":
    return "Эксперт"

def is_send_allowed(wait_seconds=30):
  """Проверяет, прошло ли достаточно времени с последней отправки и возвращает оставшееся время."""
  last_sent_time = session.get('last_sent_time')
  
  if last_sent_time:
    last_sent_time = datetime.strptime(last_sent_time, '%Y-%m-%d %H:%M:%S')
    remaining_time = (last_sent_time + timedelta(seconds=wait_seconds)) - datetime.now()
    
    if remaining_time.total_seconds() > 0:
      seconds_left = int(remaining_time.total_seconds())
      
      flash(f"Пожалуйста, подождите {seconds_left} секунд перед повторной отправкой.")
      return False, seconds_left
    
  # Обновляем временную метку, если отправка разрешена
  session['last_sent_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  return True, 0

def check_isk_status(isk):
  """ Функция для проверки статуса пользователя в контексте иска. """
  status = None 
  
  result = []
  for item in isk.defendant:
    try:
      nickname, static = item.rsplit(' ', 1) 
      if not static.isdigit():
        raise ValueError("Номер должен быть числом.")
      
      result.append({'nickname': nickname.strip(), 'static': int(static)})

    except ValueError as e:
      print(f"Ошибка обработки строки '{item}': {e}")

  if current_user.is_authenticated:
    if any(current_user.static == defenda['static'] for defenda in result):
      status = 'Defenda'
      
    elif current_user.user_type == 'user' and (current_user.id == isk.judge or current_user.permissions[0].judge):
      status = 'Judge'
      
    elif ((isk.prosecutor and current_user.id == isk.prosecutor) or (not isk.prosecutor and current_user.permissions[0].prosecutor)) and current_user.user_type == 'user':
      status = 'Prosecutor'

    elif current_user.static == isk.created:
      status = 'Created'

    elif isk.lawerc and current_user.id == isk.lawerc:
      status = 'Lawerc'

    elif isk.lawerd and current_user.id == isk.lawerd:
      status = 'Lawerd'

  return status

def draw_text(pdf, x, y, text, font="TimesNewRoman", size=12):
  pdf.setFont(font, size)
  pdf.drawString(x * mm, y * mm, text)
      
def draw_multiline_text(pdf, text, x, y, max_width=95, font="TimesNewRoman", size=12):
  pdf.setFont(font, size)
  wrapped_text = wrap(text, width=max_width) 

  for line in wrapped_text:
    pdf.drawString(x * mm, y * mm, line)
    y -= 5

  return y

def generate_signature(pdf, y, current_user, state, page=1):
    
    sing_font_path = os.path.join('static', 'fonts', 'Updock-Regular.ttf') 
    pdfmetrics.registerFont(TTFont('Updock', sing_font_path))
    pdf.setFont("Updock", 32)
    
    # Получаем имя для подписи
    full_name = current_user.nikname
    name_parts = full_name.split()
    first_name = name_parts[0]
    last_name_initial = name_parts[1][0] if len(name_parts) > 1 else ''
    signature = f"{first_name} {last_name_initial}."

    # Рисуем остальные детали, если состояние 'resolution'
    if state == 'resolution':
      pdf.setFont("TimesNewRoman-Bold", 14)
      pdf.drawString(120 * mm, y - 10, "Министерство Юстиций")
      
      pdf.setFont("TimesNewRoman", 12)
      pdf.drawString(115 * mm, y - 20, f"Прокурор {full_name} | {current_user.discordname}@gov.sa")
      
      pdf.setFont("Updock", 32)
      pdf.drawString(130 * mm, y - 45, f"{signature}")
      pdf.setFont("TimesNewRoman", 10)
      
      pdf.drawString(130 * mm, y - 45, "____________________")
      pdf.drawString(140 * mm, y - 55, "(подпись)")
      pdf.drawImage(os.path.join('static', 'img', 'print.png'), 20 * mm, y - 70, width=30 * mm, height=30 * mm)
    

def generate_signature_order(pdf_path, current_user):
    pdf_reader = PdfReader(pdf_path)
    pdf_writer = PdfWriter()

    sing_font_path = os.path.join('static', 'fonts', 'Updock-Regular.ttf') 
    pdfmetrics.registerFont(TTFont('Updock', sing_font_path))
    pdfmetrics.registerFont(TTFont('Times-Roman', os.path.join('static', 'fonts', 'times.ttf')))
    pdfmetrics.registerFont(TTFont('Times-Bold', os.path.join('static', 'fonts', 'timesbd.ttf')))
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)

    full_name = current_user.nikname
    name_parts = full_name.split()
    first_name = name_parts[0]
    last_name_initial = name_parts[1][0] if len(name_parts) > 1 else ''
    signature = f"{first_name} {last_name_initial}."
  
    y = 50 

    can.setFont("Times-Bold", 14)
    can.drawString(120 * mm, y * mm, "Министерство Юстиций")
    y -= 5
    can.setFont("Times-Roman", 12)
    can.drawString(100 * mm, y * mm, f"Генеральный Прокурор {full_name} | {current_user.discordname}@gov.sa")

    y -= 15
    can.setFont("Updock", 32) 
    can.drawString(130 * mm, y * mm, signature)
    can.setFont("Times-Roman", 10)
    y -= 2
    can.drawString(130 * mm, y * mm, "____________________")
    y -= 3
    can.drawString(140 * mm, y * mm, "(подпись)")
    can.drawImage(os.path.join('static', 'img', 'print.png'), 20 * mm, y * mm, width=30 * mm, height=30 * mm)

    can.save()
    packet.seek(0)
    signature_pdf = PdfReader(packet)
    signature_page = signature_pdf.pages[0]

    for page in pdf_reader.pages:
        page.merge_page(signature_page)
        pdf_writer.add_page(page)

    temp_output_path = pdf_path + "_temp.pdf"
    with open(temp_output_path, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)

    shutil.move(temp_output_path, pdf_path)


def increment_number_with_leading_zeros(record):
    num = int(record)
    incremented_num_str = str(num).zfill(4)
    
    return incremented_num_str

def color_organ(organ):
  if organ == 'LSPD':
    color = '#142c77' 
  elif organ == 'LSCSD':
    color = '#9F4C0F' 
  elif organ == 'SANG':
    color = '#166c0e'
  elif organ == 'FIB':
    color = '#6a6969' 
  elif organ == 'EMS':
    color = '#a21726' 
  elif organ == 'WN':
    color = '#a21726' 
  elif organ == 'GOV':
    color = '#CCAC00' 
    
  return color

def read_ranks(filename):
  with open(filename, 'r', encoding='utf-8') as f:
    data = json.load(f)
  return data

def write_ranks(filename):
  with open(filename, 'r+', encoding='utf-8') as f:
    data = json.load(f)
  return data

def get_rank_info(ranks, organization, rank_level):
  rank_info = None
  if organization in ranks:
    for rank_data in ranks[organization]:
      if rank_data['id'] == rank_level:
        return rank_data['name']
  return rank_info

def allowed_file(filename):
    """Проверяет, допустимо ли расширение файла."""
    from __init__ import app
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# подключение redis как обрабочик сообщений
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def send_to_bot_information_resolution(discord_to, discord_from, moderation, reason, uid):
  message = {
      'discord_to': discord_to,
      'discord_from': discord_from,
      'moderation': moderation,
      'reason': reason,
      'uid': uid
  }
  redis_client.publish('information_resolution', json.dumps(message))

def send_to_bot_log_dump(header, text):
  message = {
      'header': header,
      'text': text
  }
  redis_client.publish('log_dump', json.dumps(message))

def send_to_bot_get_dsname(discordid):
  import time
  message = {
    'discordid': discordid
  }
  redis_client.publish('get_dsname', json.dumps(message))
  
  for _ in range(3):  
    response = redis_client.get(f'dsname_response_{discordid}')
    if response:
      return response.decode('utf-8')
    time.sleep(0.5) 
    
  return 'Не определен'

def send_to_bot_permission_none(is_permission):
    message = {'permission_none': is_permission}
    redis_client.publish('user_permission', json.dumps(message))

def send_to_bot_new_resolution(uid, nickname, static, discordid, status, number_resolution):
  message = {
      'uid': uid,
      'nickname': nickname, 
      'static': static, 
      'discordid': discordid,
      'status': status,
      'number_resolution': number_resolution
      
  }
  redis_client.publish('new_resolution', json.dumps(message))

def send_to_bot_changepass(code, discord_id):
    message = {
        'code': code,
        'discord_id': discord_id
    }
    redis_client.publish('changepass_channel', json.dumps(message))

def send_to_bot_notification(text, discord_id, url):
    message = {
        'text': text,
        'discord_id': discord_id,
        'url': url
    }
    redis_client.publish('notificationdm_channel', json.dumps(message))

main = Blueprint('main', __name__)

def check_user_action(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
          if current_user.user_type == 'user' and current_user.action == 'Dismissal':
            logout_user()
            return redirect(url_for('main.index'))

        return f(*args, **kwargs)
    return decorated_function

@limiter.limit("10 per minute")
@main.route('/', methods=['GET'])
def index():
  from __init__ import News, Users
  
  news = News.query.all()
  return render_template('index.html', news=news, Users=Users)

@main.route('/create_news', methods=['POST']) 
@limiter.limit("3 per minute")
def create_news():
  from __init__ import News, db, app

  if current_user.is_authenticated and current_user.user_type != 'user':
    return jsonify({'success': False, 'message': 'Отказано в доступе.'}), 403
  
  data = request.form
  action = data.get('action')
  if not action:
    return jsonify({'success': False, 'message': 'Тип новости не указан.'}), 400

  if action not in ['admin-news', 'govenor-news', 'weazel-news']:
    return jsonify({'success': False, 'message': 'Неизвестный тип новости.'}), 404
  
  if action == 'admin-news':
    if not current_user.permissions[0].admin and not current_user.permissions[0].tech:
      return jsonify({'success': False, 'message': 'Отказано в доступе. Вы не являетесь администратором проекта.'}), 403
  
  if action == 'governor-news':
    if current_user.organ != 'GOV' and current_user.permissions[0].create_news:
      return jsonify({'success': False, 'message': 'Отказано в доступе. Вы не находитесь в гос. стуркрутре Government или у вас отсутсвуют права на создание новостей'}), 403
  
  if action == 'weazel-news':
    if current_user.organ != 'WN' and current_user.permissions[0].create_news:
      return jsonify({'success': False, 'message': 'Отказано в доступе. Вы не находитесь в гос. стуркрутре Weazel News или у вас отсутсвуют права на создание новостей'}), 403

  heading = data.get('heading')
  briefContent = data.get('brief-content')
  fullContent = data.get('full-content')
  file = request.files['file']

  if not all([briefContent, heading, fullContent]):
    return jsonify({'success': False, 'message': 'Все поля обязательны для заполнения.'}), 400
  
  if file:
    if not allowed_file(file.filename):
      return jsonify({'success': False, 'message': 'Недопустимый формат файла'}), 400
    
    file_uid = str(uuid.uuid4()).replace("-", "")[:16]
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{file_uid}.{file_extension}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    file.save(file_path)
    news = News (
      author_id = current_user.id,
      type_news = action,
      heading=heading, 
      brief_content=briefContent, 
      full_content=fullContent, 
      file_path=filename
    )
    db.session.add(news)
    
  else:
    news = News (
      author_id = current_user.id,
      type_news = action,
      heading=heading, 
      brief_content=briefContent, 
      full_content=fullContent
    )
    db.session.add(news)
  db.session.commit()
  
  return jsonify({'success': True, 'message': f'Успешно. { "Новость от Администрации" if action == "admin-news" else ("Новость от Правительства" if action == "govenor-news" else "Новость от Weazel News") } была создана. '}), 200

@main.route('/authentication-guest', methods=['GET'])
@limiter.limit("10 per minute")
def auth_guest():
  from form import GuestForm
  next_url = request.args.get('/')
  if current_user.is_authenticated:
    return redirect(next_url or url_for('main.index'))

  if session.get('nickname') and session.get('static') and session.get('discord') and session.get('password'):
    session['isVerification'] = True
  else:
    session['isVerification'] = False

  form = GuestForm()
  return render_template('auth_guest.html', form=form)

@main.route('/create-guest', methods=['POST', 'GET'])
@limiter.limit("3 per minute")
def create_guest():
  from __init__ import db, guestUsers, Users, cipher
  from form import GuestForm
  if request.method != "POST":
    flash('Вы не можете зайти на данную страницу!', 'error')
    return redirect(url_for('main.auth_guest', next=request.args.get('next')))

  next_url = request.args.get('next')
  if not next_url: 
    next_url = url_for('main.index')
  
  form = GuestForm()
  nickname = form.nickname.data
  static = form.static.data
  discord = form.discord.data
  password = form.password.data
  confirm_password = form.confirm_password.data

  if not all([nickname, static, discord, password]):
    flash('Поля должны быть заполнены!')
    return redirect(url_for('main.auth_guest'))
  
  if not (17 <= len(discord) <= 21):
    flash('Неверный формат. Вы должны вставить свой Discrod ID!')
    return redirect(url_for('main.auth_guest'))
  
  if password != confirm_password:
    flash('Ошибка в валидации Пароля. Пароли не совпадают!')
    return redirect(url_for('main.auth_guest'))
  
  if not (1 <= len(static) <= 7):
    flash('Неверный формат. Вы должны вставить свой static!')
    return redirect(url_for('main.auth_guest'))
  
  guest = guestUsers.query.filter_by(static=static).first()
  if guest:
    flash('Ошибка взаимодействия. Этот static уже зарегистрирован!')
    return redirect(url_for('main.auth_guest'))
  
  hashed_password = generate_password_hash(password)
  session['nickname'] = cipher.encrypt(nickname.encode()).decode()
  session['static'] = cipher.encrypt(str(static).encode()).decode()
  session['discord'] = cipher.encrypt(str(discord).encode()).decode()
  session['password'] = cipher.encrypt(str(hashed_password).encode()).decode()

  def send_verification_code(discord, code):
    message = {
      'discord': discord,
      'code': code
    }
    redis_client.publish('verification_code', json.dumps(message))

  verification_code = random.randint(100000, 999999)
  session['verification_code'] = cipher.encrypt(str(verification_code).encode()).decode()
  send_verification_code(discord, verification_code)

  isVerification = True
  session['isVerification'] = isVerification
  return redirect(url_for('main.auth_guest'))

@main.route('/validate-verificate-code', methods=['POST', 'GET'])
@limiter.limit("3 per minute")
def validate_code():
  from __init__ import cipher, guestUsers, db, PermissionUsers, get_next_id_user

  print(cipher.decrypt(session.get('verification_code').encode()).decode())

  entered_code = request.form.get('verify-code')
  if entered_code and int(entered_code) == int(cipher.decrypt(session.get('verification_code').encode()).decode()):
    nickname = cipher.decrypt(session.get('nickname').encode()).decode()
    static = int(cipher.decrypt(session.get('static').encode()).decode())
    discord = int(cipher.decrypt(session.get('discord').encode()).decode())
    password = cipher.decrypt(session.get('password').encode()).decode()

    try:
      new_guest = guestUsers(
        id=get_next_id_user(),
        nickname=nickname,
        static=static,
        discord_id=discord,
        password=password
      )
      db.session.add(new_guest)
      db.session.commit()
      
      new_permission = PermissionUsers( guest_id = new_guest.id )
      db.session.add(new_permission)
      db.session.commit()

      session.pop('nickname', None)
      session.pop('static', None)
      session.pop('discord', None)
      session.pop('password', None)
      session.pop('verification_code', None)

      isVerification = False
      session['isVerification'] = isVerification

      flash('Пользователь успешно зарегистрирован!')
      return redirect(url_for('main.index'))
  
    except SQLAlchemyError as e:
      db.session.rollback() 
      print(f'Ошибка при регистрации пользователя: {str(e)}')
      isVerification = True
      session['isVerification'] = isVerification
      return redirect(url_for('main.auth_guest'))
    
  else:
    isVerification = True
    session['isVerification'] = isVerification
    flash('Неверный код. Попробуйте снова.', 'error')
    return redirect(url_for('main.auth_guest'))

def format_date(create_at):
  now = datetime.now()
  create_date = datetime.strptime(create_at, '%Y-%m-%d %H:%M:%S')

  if create_date.date() == now.date():
    return f"Сегодня {create_date.strftime('%H:%M')}"
  elif create_date.date() == (now.date() - timedelta(days=1)):
    return f"Вчера {create_date.strftime('%H:%M')}"
  else:
    return create_date.strftime('%Y-%m-%d %H:%M')

@main.route('/get-claim-district-content', methods=['GET'])
@limiter.limit("10 per minute")
def get_claim_district_content():
  from __init__ import iskdis, Users, guestUsers, db, claimsStatement
  count = claimsStatement.query.filter_by(is_archived=True).count()
  now = datetime.now()
  
  considered_claims = claimsStatement.query.filter_by(is_archived=False).all()
  district_data = iskdis.query.filter(iskdis.current_uid.in_([claim.uid for claim in considered_claims])).all()

  return render_template('main/main-state-district.html', 
                         timedelta=timedelta, district=district_data, Users=Users, guestUsers=guestUsers, count=count, now=now)

@main.route('/get-claim-supreme-content', methods=['GET'])
@limiter.limit("10 per minute")
def get_claim_supreme_content():
  from __init__ import isksup, Users, guestUsers, db, claimsStatement
  count = claimsStatement.query.filter_by(is_archived=True).count()
  now = datetime.now()
  
  considered_claims = claimsStatement.query.filter_by(is_archived=False).all()
  district_data = isksup.query.filter(isksup.current_uid.in_([claim.uid for claim in considered_claims])).all()
  
  return render_template('main/main-state-supreme.html', 
                         timedelta=timedelta, district=district_data, Users=Users, guestUsers=guestUsers, count=count, now=now)

@main.route('/create-claim-state', methods=['POST'])
@limiter.limit("3 per minute")
def create_claim():
  from __init__ import iskdis, isksup, db, claimsStatement, Users, guestUsers

  if not current_user.is_authenticated:
    return jsonify({'success': False, 'message': 'Вы не вошли в акаунт!'}), 401

  data = request.get_json()
  
  criminal_case = 'common_complaint'
  if current_user.permissions[0].prosecutor:
    criminal_case = data.get('action')

  if criminal_case == 'common_complaint':
    defendants = data.get('defenda')
    phone_plaintiff = data.get('phone-plaintiff')
    card_plaintiff = data.get('card-plaintiff') 
    claims = data.get('claims')
    description = data.get('description') 
    court_type = data.get('court')
    lower = data.get('lower')

    static = None
    if lower:
      static = lower.split(' ', 2)[2] if len(lower.split()) > 2 else None
  
    if static != None and lower:
      user_lower = Users.query.filter_by(static=static).first()
      guest_lower = guestUsers.query.filter_by(static=static).first()

      if not user_lower and not guest_lower:
        return jsonify({'success': False, 'message': 'Представитель не является частным или государственным адвокатом.'}), 400

      if user_lower:
        if not user_lower.permissions or not user_lower.permissions[0].lawyer:
          return jsonify({'success': False, 'message': 'Представитель не является адвокатом.'}), 400

      if guest_lower and not user_lower:
        if not user_lower.permissions or not guest_lower.permissions[0].lawyer:
          return jsonify({'success': False, 'message': 'Представитель не является частным адвокатом.'}), 400
          
    if not all([phone_plaintiff, card_plaintiff, description]):
      return jsonify({'success': False, 'message': 'Неверный формат. Поля должны быть заполнены'}), 400
    
    defendants=[item for item in defendants if item]
    name_static_pattern = r'^[A-Z][a-z]+ [A-Z][a-z]+ \d{1,7}$'
    faction_static_pattern = r'^(LSPD|LSCSD|FIB|SANG|EMS|WN|GOV) \d{1,7}$'
    for defendant in defendants:
      if not re.match(name_static_pattern, defendant) and not re.match(faction_static_pattern, defendant) and defendant != '':
        return jsonify({"success": False, "message": "Некорректая имя отвечика. Пример: 'Имя Фамилия Статик' или 'Фракция Статик'."}), 400
    
    if not claims:
      return jsonify({'success': False, 'message': 'Неверный формат. Поля должны быть заполнены'}), 400
    
    defendants=[item for item in defendants if item]
    pattern_nick = r'^[A-Z][a-z]+ [A-Z][a-z]+ \d{1,7}$'
    for defendant in defendants:
      if not re.match(pattern_nick, defendant):
        return jsonify({"success": False, "message": "Некорректая имя отвечика. Пример: 'Имя Фамилия Статик'."}), 400
    
    try:
      claim = claimsStatement()
      db.session.add(claim)
      db.session.flush()  

      if court_type == "district":
        district_claim = iskdis(
          current_uid=claim.uid,
          discription=description,
          claims=claims, 
          phone=phone_plaintiff,
          cardn=card_plaintiff,
          created=current_user.static,
          defendant=defendants,
          lawerc= None if static == None else (user_lower.id if user_lower else guest_lower.id)
        )
        db.session.add(district_claim)
      
      elif court_type == "supreme":
        supreme_claim = isksup(
          current_uid=claim.uid,
          discription=description,
          claims=claims, 
          phone=phone_plaintiff,
          cardn=card_plaintiff,
          created=current_user.static,
          defendant=defendants,
          lawerc= None if static == None else (user_lower.id if user_lower else guest_lower.id)
        )
        db.session.add(supreme_claim)

      db.session.commit()
      return jsonify({'success': True, 'message': 'Заявление успешно подано!'}), 200
    
    except Exception as e:
      db.session.rollback()
      print(f'Ошибка {str(e)}')
      return jsonify({'success': False, 'message': 'Ошибка при обработке заявления.'}), 500

  elif criminal_case == 'criminal_case':    
    defendants = data.get('defenda')
    link_case = data.get('criminal_case')
    date_case = data.get('date_investigation')
    court_type = data.get('court')
    
    pattern_link = r"^https:\/\/docs\.google\.com\/document\/.*"
    if not re.match(pattern_link, link_case):
      return jsonify({"success": False, "message": "Некорректная ссылка. Ссылка должна начинаться с https://docs.google.com/"}), 400
    
    pattern_date = r'^\d{2}\.\d{2}\.\d{4}$'
    if not re.match(pattern_date, date_case):
      return jsonify({"success": False, "message": "Некорректаня дата. Пример:'ДД.ММ.ГГГГ'."}), 400

    defendants=[item for item in defendants if item]
    name_static_pattern = r'^[A-Z][a-z]+ [A-Z][a-z]+ \d{1,7}$'
    faction_static_pattern = r'^(LSPD|LSCSD|FIB|SANG|EMS|WN|GOV) \d{1,7}$'
    for defendant in defendants:
      if not re.match(name_static_pattern, defendant) and not re.match(faction_static_pattern, defendant) and defendant != '':
        return jsonify({"success": False, "message": "Некорректая имя отвечика. Пример: 'Имя Фамилия Статик' или 'Фракция Статик'."}), 400
    
    if not all([link_case, date_case]):
      return jsonify({'success': False, 'message': 'Неверный формат. Поля должны быть заполнены'}), 400
    
    try:
      claim = claimsStatement()
      db.session.add(claim)
      db.session.flush()  

      if court_type == "district":
        district_claim = iskdis(
          current_uid=claim.uid,
          created=current_user.static,
          prosecutor=current_user.id,
          defendant=defendants,
          type_criminal=True,
          link_case=link_case,
          date_case=date_case,
          status='CompleteWork'
        )
        db.session.add(district_claim)
      
      elif court_type == 'supreme':
        supreme_claim = isksup(
          current_uid=claim.uid,
          created=current_user.static,
          prosecutor=current_user.id,
          defendant=defendants,
          type_criminal=True,
          link_case=link_case,
          date_case=date_case,
          status='CompleteWork'
        )

        db.session.add(supreme_claim)

      db.session.commit()
      return jsonify({'success': True, 'message': 'Заявление успешно подано!'}), 200
    
    except Exception as e:
      db.session.rollback()
      print(f'Ошибка {str(e)}')
      return jsonify({'success': False, 'message': 'Ошибка при обработке заявления.'}), 500
    
  return jsonify({'success': True, 'message': 'Заявление успешно подано!'}), 200
    
@main.route('/judge_settings', methods=['POST'])
@limiter.limit("3 per minute")
def judge_settings():
  from __init__ import repltoisks, Users, claimsStatement, db

  uid = request.form.get('uid')
  if not uid:
    return jsonify({"success": False, "message": "Данный иск не найден, проверьте его существование!"}), 400
  
  setting = request.form.get('setting')
  if setting == "samootvod":
    isk = claimsStatement.query.filter_by(uid=uid).first()
    if isk.district_court and isk.district_court[0].judge == current_user.id:
      isk.district_court[0].judge = None
    elif isk.supreme_court and isk.supreme_court[0].judge == current_user.id:
      isk.supreme_court[0].judge = None
    else:
      return "Эта ошибка не должна произойти, но если вы её видите напишите в тех. поддержку", 400
    replyik = {
      'judge': current_user.nikname,
      'type_log': 'samootvod'
    }
    new_log = repltoisks(
      current_uid=uid,
      author_id=current_user.id,
      replyik=replyik,
      type_doc='log',
      moderation=True
    )
    db.session.add(new_log)
    
  elif setting == "otvodoth":
    isk = claimsStatement.query.filter_by(uid=uid).first()
    type_otvod = request.form.get('type_otvod')
    name_otvod = request.form.get('name_otvod')
    
    if isk.district_court and isk.district_court[0].judge == current_user.id:
      if type_otvod == "otherme":
        otherme_dict = isk.district_court[0].otherme
        key_to_delete = next((key for key, value in otherme_dict.items() if value == name_otvod), None) 
        if key_to_delete: 
          del otherme_dict[key_to_delete]
      else:
        setattr(isk.district_court[0], type_otvod, None)
        
  elif setting == "privlehenie":
    isk = claimsStatement.query.filter_by(uid=uid).first()
    role = request.form.get('role')
    static = request.form.get('static')
    
    if isk.district_court and isk.district_court[0].judge == current_user.id:
      print(role)
      user = Users.query.filter_by(static=static).first()
      if role == "expert" or role == "svidetel":
        setattr(isk.district_court[0].otherme, role, static)
        
      elif role == "defendant":
        itog = f"{user.nikname} {static}"
        isk.district_court[0].defendant.append(itog)
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(isk.district_court[0], "defendant")
        
      else:
        setattr(isk.district_court[0], role, user.id)
        
  elif setting == "prinatisk":
    isk = claimsStatement.query.filter_by(uid=uid).first()
    status = check_isk_status(isk.district_court[0]) if isk.district_court else check_isk_status(isk.supreme_court[0])
    
    if status == 'Judge':
      if isk.district_court:
        isk.district_court[0].judge = current_user.id
      elif isk.supreme_court:
        isk.supreme_court[0].judge = current_user.id
      else:
        return "Эта ошибка не должна произойти, но если вы её видите напишите в тех. поддержку", 400
      
      replyik = {
        'judge': current_user.nikname,
        'type_log': 'prinatisk'
      }
      new_log = repltoisks(
        current_uid=uid,
        author_id=current_user.id,
        replyik=replyik,
        type_doc='log',
        moderation=True
      )
      db.session.add(new_log)

  try:
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(f'Ошибка {str(e)}')
    return redirect(url_for('main.doc'))
    
  return redirect(url_for('main.claim_state', uid=uid))
      
@main.route('/complaint', methods=['GET'])
@limiter.limit("10 per minute")
def claim_state():
  from __init__ import iskdis, isksup, repltoisks, Users, guestUsers, claimsStatement, courtOrder
  
  uid = request.args.get('uid')
  if not uid:
    return "No UID provided", 400
  
  claim_statement_district = iskdis.query.filter_by(current_uid=uid).first()
  claim_statement_supreme = isksup.query.filter_by(current_uid=uid).first()
  repltoisk = repltoisks.query.filter_by(current_uid=uid).all()

  if not claim_statement_district and not claim_statement_supreme:
    return render_template('api/404.html')

  if claim_statement_district:
    status = check_isk_status(claim_statement_district)
    isk = claim_statement_district

    orders_data = courtOrder.query.filter_by(current_uid=uid).all()
    replo_data = repltoisks.query.filter_by(current_uid=uid).all()

    replies_data = [
    {
        'id-replies': reply.id,
        'current_uid': reply.current_uid,
        'id_reply': reply.author_id,
        'replyik': reply.replyik,
        'moderation': reply.moderation,
        'type_doc': reply.type_doc,
        'timespan': reply.timespan
    } for reply in replo_data ]

    court_orders_data = [
    {
        'id-court': order.id,
        'current_uid': order.current_uid,
        'id_judge': order.author_id,
        'findings': order.findings,
        'consideration': order.consideration,
        'ruling': order.ruling,
        'type_doc': order.type_doc,
        'timespan': order.timespan
    } for order in orders_data ]

    combined_data = sorted(replies_data + court_orders_data, key=lambda x: x['timespan'], reverse=True)

    createat = claimsStatement.query.filter_by(uid=claim_statement_district.current_uid).first()

    create_at_datetime = createat.create_at
    current_date = datetime.now()

    if create_at_datetime.date() == current_date.date():
      display_date = f"Сегодня, {create_at_datetime.strftime('%H:%M')}"
    elif create_at_datetime.date() == (current_date - timedelta(days=1)).date():
      display_date = f"Вчера, {create_at_datetime.strftime('%H:%M')}"
    else:
      display_date = create_at_datetime.strftime('%Y-%m-%d %H:%M')


    return render_template(
      'complaint.html',
      Users=Users,
      guestUsers=guestUsers,
      createat=display_date,
      defendant=isk.defendant,
      status=status,
      combined_data=combined_data,
      repltoisk=repltoisk,
      isk=isk,
      court='district'
    )
  
  elif claim_statement_supreme:
    status = check_isk_status(claim_statement_supreme)
    isk = claim_statement_supreme

    orders_data = courtOrder.query.filter_by(current_uid=uid).all()
    replo_data = repltoisks.query.filter_by(current_uid=uid).all()

    replies_data = [
    {
        'id-replies': reply.id,
        'current_uid': reply.current_uid,
        'author_id': reply.author_id,
        'replyik': reply.replyik,
        'moderation': reply.moderation,
        'type_doc': reply.type_doc,
        'timespan': reply.timespan
    } for reply in replo_data ]

    court_orders_data = [
    {
        'id-court': order.id,
        'current_uid': order.current_uid,
        'id_judge': order.author_id,
        'findings': order.findings,
        'consideration': order.consideration,
        'ruling': order.ruling,
        'type_doc': order.type_doc,
        'timespan': order.timespan
    } for order in orders_data ]

    combined_data = sorted(replies_data + court_orders_data, key=lambda x: x['timespan'], reverse=True)

    createat = claimsStatement.query.filter_by(uid=claim_statement_supreme.current_uid).first()

    create_at_datetime = createat.create_at
    current_date = datetime.now()

    if create_at_datetime.date() == current_date.date():
      display_date = f"Сегодня, {create_at_datetime.strftime('%H:%M')}"
    elif create_at_datetime.date() == (current_date - timedelta(days=1)).date():
      display_date = f"Вчера, {create_at_datetime.strftime('%H:%M')}"
    else:
      display_date = create_at_datetime.strftime('%Y-%m-%d %H:%M')


    return render_template(
      'complaint.html',
      Users=Users,
      guestUsers=guestUsers,
      createat=display_date,
      defendant=isk.defendant,
      claims=isk.claims,
      status=status,
      combined_data=combined_data,
      repltoisk=repltoisk,
      isk=isk,
      court='supreme'
      )
  else:
    flash('Данный иск удален или поврежден!')
    return redirect(url_for('main.doc'))
  
@main.route('/add_link_court', methods=['POST'])
@limiter.limit("3 per minute")
def addlink():
  from __init__ import iskdis, isksup, db
  
  data = request.get_json()
  uid = data.get('uid')
  if not uid:
    return jsonify({"success": False, "message": "Данный иск не найден, проверьте его существование!"}), 400

  if iskdis.query.filter_by(current_uid=uid).first():
    isk = iskdis.query.filter_by(current_uid=uid).first()
  elif isksup.query.filter_by(current_uid=uid).first():
    isk = isksup.query.filter_by(current_uid=uid).first()
  else:
    return jsonify({"success": False, "message": "Данный иск не найден, проверьте его существование!"}), 500
  
  paymentProof = data.get('paymentProof', '')
  evidences =  data.get('evidence', [])
  print(evidences)
  
  YOUTUBE_REGEX = r'^(https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/(watch\?v=[\w-]+|.+)$'
  RUTUBE_REGEX = r'^(https?:\/\/)?(www\.)?rutube\.ru\/video\/[a-zA-Z0-9]+\/?$'
  YAPIX_REGEX = r'^(https?:\/\/)?(www\.)?yapix\.ru\/video\/[a-zA-Z0-9]+\/?$'
  IMGUR_REGEX = r'^(https?:\/\/)?(www\.)?imgur\.com\/[a-zA-Z0-9]+\/?$'
  
  if paymentProof and not (
    re.match(YAPIX_REGEX, paymentProof) or 
    re.match(IMGUR_REGEX, paymentProof)):
    return jsonify({"success": False, "message": "Введите корректную ссылку для оплаты гос пошлины (Yapix или Imgur)"}), 400
  
  for evidence in evidences:
    if evidence:
      if not (
        re.match(YOUTUBE_REGEX, evidence) or 
        re.match(RUTUBE_REGEX, evidence) or 
        re.match(YAPIX_REGEX, evidence) or 
        re.match(IMGUR_REGEX, evidence)):
        return jsonify({"success": False, "message": "Введите корректную ссылку YouTube, Rutube, Yapix или Imgur для доказательств"}), 400
  
  link_evedence = {}
  try:
    evidences = [evidence for evidence in evidences if evidence and (isinstance(evidence, dict) and evidence or isinstance(evidence, str) and evidence.strip())]
    link_evedence = {
      'paymentProof': paymentProof,
      'evidences': evidences
    }
    isk.evidence = link_evedence
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    return jsonify({"success": False, "message": "Попробуйте позже!"}), 500

  return jsonify({"success": True, "message": "Доказательства бли прикрепленны!"}), 200


@main.route('/create_petition', methods=['POST'])
@limiter.limit("3 per minute")
def createPettion():
  from __init__ import repltoisks, db
  
  data = request.get_json()
  uid = data.get('uid')
  if not uid:
    return jsonify({"success": False, "message": "Данный иск не найден, проверьте его существование!"}), 400

  type_pettion = data.get('action')
  findings = data.get('findings')
  nickname = data.get('nickname')
  static = data.get('static')

  replyik = {}

  count = repltoisks.query.filter_by(current_uid=uid, type_doc='pettion').count()
  if type_pettion == 'svidetel':
    if nickname == '' or static == '':
      return jsonify({"success": False, "message": "Nickname и static не могут быть пустыми при выборе 'Свидетель'"}), 400
    
    replyik = {
      "creater": current_user.id,
      "№-pettion": count + 1,
      "type": 'svidetel',
      "nickname": nickname if nickname != '' else None,
      "static": static if static != '' else None,
      "findings": findings
    }

  elif type_pettion == 'expert':
    if nickname == '' or static == '':
      return jsonify({"success": False, "message": "Nickname и static не могут быть пустыми при выборе 'Эксперт'"}), 400
    
    replyik = {
      "creater": current_user.id,
      "№-pettion": count + 1,
      "type": 'expert',
      "nickname": nickname if nickname != '' else None,
      "static": static if static != '' else None,
      "findings": findings
    }

  elif type_pettion == 'otvod':
    if nickname == '' or static == '':
      return jsonify({"success": False, "message": "Nickname и static не могут быть пустыми при выборе 'Отвод'"}), 400
    
    replyik = {
      "creater": current_user.id,
      "№-pettion": count + 1,
      "type": 'otvod',
      "nickname": nickname if nickname != '' else None,
      "static": static if static != '' else None,
      "findings": findings
    }

  elif type_pettion == 'freeform':
    replyik = {
      "creater": current_user.id,
      "№-pettion": count + 1,
      "type": 'freeform',
      "nickname": nickname if nickname != '' else None,
      "static": static if static != '' else None,
      "findings": findings
    }

  else:
    return jsonify({"success": False, "message": "Вы должны выбрать тип ходатайства"}), 400

  try: 
    new_pettion = repltoisks(
      current_uid=uid,
      author_id=current_user.id,
      replyik=replyik,
      type_doc='pettion'
    )

    db.session.add(new_pettion)
    db.session.commit()
    return jsonify({"success": True, "message": f"Вы успешно подали ходатайство!"}), 200

  except SQLAlchemyError as e:
    logging.error(f'Ошибка в бд repltoisks: {e}') 
    return jsonify({"success": False, "message": "Попробуйте позже!"}), 500
  

@main.route('/create_prosecutor', methods=['POST'])
@limiter.limit("3 per minute")
def createProsecutor():
  from __init__ import repltoisks, db, iskdis, isksup

  data = request.get_json()
  uid = data.get('uid')
  if not uid:
    return jsonify({"success": False, "message": "Данный иск не найден, проверьте его существование!"}), 400
  
  if current_user.user_type != 'user' and not current_user.permissions[0].prosecutor:
    return jsonify({"success": False, "message": "У вас недостаточно прав для выполнения этого действия."}), 403

  type_document = data.get('type_document')
  if type_document == "complete_delo":
    
    delo = data.get('delo')
    pattern = r"^https:\/\/docs\.google\.com\/document\/.*"
    if not re.match(pattern, delo):
      return jsonify({"success": False, "message": "Некорректная ссылка. Ссылка должна начинаться с https://docs.google.com/"}), 400
    
    type_delo = data.get('type_delo')
    if all([delo, type_delo]):
      return jsonify({"success": False, "message": "Все поля должны быть заполнены!"}), 400

  replyik = {}
  if type_document == 'start_investigation':
    now = datetime.now()
    replyik = {
      "type": 'start_investigation',
      "id_prosecutor": current_user.id,
      "date": now.strftime("%Y.%m.%d %H:%M")
    }
    claim_statement_district = iskdis.query.filter_by(current_uid=uid).first()
    claim_statement_supreme = isksup.query.filter_by(current_uid=uid).first()
    
    if claim_statement_district:
      claim_statement_district.prosecutor = current_user.id
      
    elif claim_statement_supreme:
      claim_statement_supreme.prosecutor = current_user.id

  elif type_document == 'complete_delo':
    now = datetime.now()
    replyik = {
      "type": 'complete_delo',
      "date": now.strftime("%Y.%m.%d %H:%M"),
      "delo": delo,
      "id_prosecutor": current_user.id,
      "type_delo": type_delo
    }

  else:
    return jsonify({"success": False, "message": "Данное действие недоступно!"}), 400

  try: 
    new_procdoc = repltoisks(
      current_uid=uid,
      author_id=current_user.id,
      replyik=replyik,
      moderation=True,
      type_doc='start_investigation' if type_document == 'start_investigation' else 'complete_delo'
    )

    if type_document == 'complete_delo':
      district = iskdis.query.filter_by(current_uid=uid).first()
      district.status = 'CompleteWork'

    db.session.add(new_procdoc)
    db.session.commit()
    return jsonify({"success": True, "message": "Успешно было отправленно!"}), 200

  except SQLAlchemyError as e:
    db.session.rollback()
    logging.error(f'Ошибка в бд repltoisks: {e}') 
    return jsonify({"success": False, "message": "Проблема создания документа, попробуйте позже!"}), 404

@main.route('/create_court_pettion', methods=['POST'])
@limiter.limit("3 per minute")
def courtPettion():
  from __init__ import db, repltoisks, iskdis, courtOrder

  data = request.get_json()
  uid = data.get('uid')
  if not uid:
    return jsonify({"success": False, "message": "Данный иск не найден, проверьте его существование!"}), 400
  
  action = data.get('action')
  pettion = data.get('petition')
  ruling = data.get('decision')
  findings = data.get('findings')
  consideration = data.get('consideration') 

  if not all([findings, consideration, action, pettion]):
    return jsonify({"success": False, "message": "Все поля должны быть заполнены!"}), 400
  
  entries = repltoisks.query.filter_by(current_uid=uid).all()
  entry = None
  id_entry = None

  for e in entries:
    if '№-pettion' in e.replyik and e.replyik['№-pettion'] == int(pettion):
      id_entry = e.id
      entry = e.replyik['№-pettion']

  if not entry: 
    return jsonify({"success": False, "message": f"Такого ходатайства {pettion} не существует!"}), 400
  
  replo = repltoisks.query.filter_by(id=id_entry).first()
  if action == 'false-petition':
    try:
      new_order = courtOrder(
        author_id = current_user.id,
        current_uid = uid,
        findings = findings,
        ruling = ruling, 
        consideration = consideration,
        type_doc = 'court_order'
      )

      replo.moderation = True

      db.session.add(new_order)
      db.session.commit()
      return jsonify({"success": True, "message": "Вы успешно отправили определение!"}), 200
    
    except SQLAlchemyError as e:
      db.session.rollback()
      return jsonify({"success": False, "message": "Возникла проблема сохранения, попробуйте позже!"}), 500

  nickname = replo.replyik["nickname"]
  static = replo.replyik["static"]
  isk = iskdis.query.filter_by(current_uid=uid).first()
  if replo.replyik["type"] == 'svidetel':
    try:
      if not isk.otherme:
        isk.otherme = []
      data = {
        "type": 'svidetel',
        "nickname": nickname,
        "static": static
        }
      isk.otherme.append(data)

      new_order = courtOrder(
        author_id = current_user.id,
        current_uid = uid,
        findings = findings,
        ruling = ruling, 
        consideration = consideration,
        type_doc = 'court_order'
      )

      replo.moderation = True

      db.session.add(new_order)
      db.session.commit()

    except SQLAlchemyError as e:
      db.session.rollback()
      return jsonify({"success": False, "message": "Возникла проблема сохранения, попробуйте позже!"}), 500

  elif replo.replyik["type"] == 'expert':
    try:
      if not isk.otherme:
        isk.otherme = []
      data = {
        "type": 'expert',
        "nickname": nickname,
        "static": static
        }
      isk.otherme.append(data)

      new_order = courtOrder(
        author_id = current_user.id,
        current_uid = uid,
        findings = findings,
        ruling = ruling, 
        consideration = consideration,
        type_doc = 'court_order'
      )

      replo.moderation = True

      db.session.add(new_order)
      db.session.commit()

    except SQLAlchemyError as e:
      db.session.rollback()
      return jsonify({"success": False, "message": "Возникла проблема сохранения, попробуйте позже!"}), 500

  elif replo.replyik["type"] == 'otvod':
    new_order = courtOrder(
        author_id = current_user.id,
        current_uid = uid,
        findings = findings,
        ruling = ruling, 
        consideration = consideration,
        type_doc = 'court_order'
      )

    replo.moderation = True

    db.session.add(new_order)
    db.session.commit()

  elif replo.replyik["type"] == 'freeform':
    new_order = courtOrder(
        author_id = current_user.id,
        current_uid = uid,
        findings = findings,
        ruling = ruling, 
        consideration = consideration,
        type_doc = 'court_order'
      )

    replo.moderation = True

    db.session.add(new_order)
    db.session.commit()

  else:
    return jsonify({"success": False, "message": "Возникла проблема сохранения, попробуйте позже!"}), 500
  
  return jsonify({"success": True, "message": "Вы успешно отправили определение!"}), 200

@main.route('/create_court_order', methods=['POST'])
@limiter.limit("3 per minute")
def courtOrder():
    from __init__ import courtOrder, db, iskdis, isksup, claimsStatement
    
    data = request.get_json()
    uid = data.get('uid')
    if not uid:
      return jsonify({"success": False, "message": "Данный иск не найден, проверьте его существование!"}), 400

    if current_user.user_type != 'user' and current_user.permissions[0].judge:
      return jsonify({"success": False, "message": "Вы не можете составлять опредение под иско!"}), 403

    typeOrderCourt = data.get('type_court_order')
    if typeOrderCourt == 'processiong_complaint':
        ruling = data.get('decision')
        print (ruling)
        
        findings = data.get('findings')
        consideration = data.get('consideration') 
        action = data.get('action')

        if not all([findings, consideration, action]):
          return jsonify({"success": False, "message": "Все поля должны быть заполнены!"}), 400

        claimState = claimsStatement.query.filter_by(uid=uid).first()
        complaint = iskdis.query.filter_by(current_uid=uid).first() or isksup.query.filter_by(current_uid=uid).first()
        if not complaint:
          return jsonify({"success": False, "message": "Данный иск не найден, проверьте его существование!"}), 404

        if action == 'accept':
            complaint.status = 'Accepted'
            complaint.judge = current_user.id
        elif action == 'reject':
            complaint.status = 'Rejectioned'
            claimState.is_archived = True
            complaint.judge = current_user.id
        elif action == 'hold':
            complaint.status = 'LeftMoved'
            complaint.judge = current_user.id
        else:
            return jsonify({"success": False, "message": "Ошибка действия над иском!"}), 400

        try:
            new_order = courtOrder(
                current_uid=uid,
                author_id=current_user.id,
                findings=findings,
                consideration=consideration,
                ruling=ruling,
                type_doc='court_order'
            )
            db.session.add(new_order)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"Ошибка сохранения в базе данных: {str(e)}"}), 500

    elif typeOrderCourt == 'appoint_court_session':
        ruling = data.get('decision')
        findings = data.get('findings')
        consideration = data.get('consideration') 
        action = data.get('action')
        time = data.get('time')

        if not all([findings, consideration, action]):
            return jsonify({"success": False, "message": "Все поля должны быть заполнены!"}), 400

        complaint = iskdis.query.filter_by(current_uid=uid).first() or isksup.query.filter_by(current_uid=uid).first()
        claimState = claimsStatement.query.filter_by(uid=uid).first()

        if not complaint or not claimState:
            return jsonify({"success": False, "message": "Исковое заявление не найдено!"}), 404

        if action in ['appoint', 'reassign']:
            try:
                complaint.status = 'CourtHearing'
                date_court_session = datetime.strptime(time, '%d.%m.%Y %H:%M')
                claimState.date_court_session = date_court_session
                db.session.commit()
            except (ValueError, SQLAlchemyError) as e:
                db.session.rollback()
                return jsonify({"success": False, "message": f"Время должно быть в формате 'ДД.ММ.ГГГГ ЧЧ:ММ'."}), 500
        else:
            return jsonify({"success": False, "message": "Произошла ошибка, попробуйте позже!"}), 400

        try:
            new_order = courtOrder(
                current_uid=uid,
                author_id=current_user.id,
                findings=findings,
                consideration=consideration,
                ruling=ruling,
                other=time,
                type_doc='court_order'
            )
            db.session.add(new_order)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"Ошибка сохранения в базе данных: {str(e)}"}), 500

    elif typeOrderCourt == 'decision_court_session':
        ruling = data.get('decision')
        findings = data.get('findings')
        consideration = data.get('consideration')

        if not all([findings, consideration]):
            return jsonify({"success": False, "message": "Все поля должны быть заполнены!"}), 400

        complaint = iskdis.query.filter_by(current_uid=uid).first() or isksup.query.filter_by(current_uid=uid).first()
        claimState = claimsStatement.query.filter_by(uid=uid).first()

        if not complaint or not claimState:
            return jsonify({"success": False, "message": "Исковое заявление не найдено!"}), 404

        if claimState.date_court_session > datetime.now():
            return jsonify({"success": False, "message": "Вы не можете принять решение, пока не прошло время суда!"}), 400

        try:
            complaint.status = 'CompletedTrial'
            claimState.is_archived = True

            new_order = courtOrder(
                current_uid=uid,
                author_id=current_user.id,
                findings=findings,
                consideration=consideration,
                ruling=ruling,
                type_doc='court_order'
            )
            db.session.add(new_order)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"Ошибка сохранения в базе данных: {str(e)}"}), 500

    else:
        return jsonify({"success": False, "message": "Не возможно определить тип действия!"}), 400

    return jsonify({"success": True, "message": "Определение было успешно создано!"}), 200

@main.route('/auth', methods=['POST', 'GET'])
@limiter.limit("10 per minute")
def auth():
  from __init__ import db, Users, guestUsers
  form = FormAuthPush()

  if current_user.is_authenticated:
    next_url = request.args.get('next') or url_for('main.profile')
    return redirect(next_url)

  if form.validate_on_submit():  
    user = Users.query.filter_by(static=form.static.data).first()
    guest = guestUsers.query.filter_by(static=form.static.data).first()

    if user:
      if user.action == 'Dismissal':
        flash("Отказано в доступе: вы не состоите во фракции.")
        return redirect(url_for('main.auth'))

      if check_password_hash(user.password, form.password.data):
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.profile'))
      else:
        flash("Неверный static или password!")
        return redirect(url_for('main.auth'))

    if guest:
        if check_password_hash(guest.password, form.password.data):
          login_user(guest, remember=form.remember_me.data)
          return redirect(url_for('main.profile'))
        else:
          flash("Неверный static или password!")
          return redirect(url_for('main.auth'))

    flash("Пользователь не найден!")
    return redirect(url_for('main.auth'))

  return render_template('auth.html', form=form)

@main.after_request
def redirect_login(response):
    if request.endpoint == 'main.logout':
      return redirect(url_for('main.index'))
    
    if response.status_code == 401:  
      if not current_user.is_authenticated:
        next_url = request.args.get('next')
        if not next_url:
          next_url = url_for('main.index')
        return redirect(url_for('main.auth', next=next_url)) 
    return response

# Обработка КА функций.
def generate_random_password():
  """Создание пароля"""
  characters = string.ascii_letters + string.digits + string.punctuation
  return ''.join(random.choice(characters) for i in range(10))

def existing_discord_in_multiple_organizations(discord_id):
  from __init__ import Users
  """Проверка на 2+ дискорда в Гос. фракции"""
  return (Users.query.filter_by(discordid=discord_id).count() > 1  and Users.query.filter_by(discordid=discord_id).first().action != 'Dismissal')

def send_to_bot_ka(action, static_to, discord_id_from, discord_id_to, curr_rank, prev_rank, nikname_from, nikname_to, reason, fraction):
  """Redis отправка формы КА в discord bot"""
  message = {
      'action': action,
      'discord_id_from': discord_id_from,
      'discord_id_to': discord_id_to,
      'curr_rank': curr_rank,
      'prev_rank': prev_rank,
      'static_to': static_to,
      'nikname_from': nikname_from,
      'nikname_to': nikname_to,
      'reason': reason,
      'fraction': fraction
  }
  redis_client.publish('ka_channel', json.dumps(message))

def send_to_bot_invite(password, discord_id, static, organ):
  message = {
      'password': password,
      'discord_id': discord_id,
      'static': static, 
      'organ': organ
  }
  redis_client.publish('invite_channel', json.dumps(message))

def send_to_bot_dismissal(discord_id, static, organ):
  message = {
      'discord_id': discord_id,
      'static': static,
      'organ': organ
  }
  redis_client.publish('dismissal_channel', json.dumps(message))

def process_ds_avatarka(discord_id):
  message = {
    'discord_id': discord_id
  }
  redis_client.publish('ds_avatarka', json.dumps(message))

from flask import jsonify


def process_invite_action(user, rank, reason, fraction):
    from __init__ import db, ActionUsers
    """Обрабатывает Инвайт если пользователя есть в БД"""
    password = generate_random_password()
    hash_password = generate_password_hash(password)
    
    try:
        user.password = hash_password
        user.prev_rank = 0
        user.curr_rank = 1
        user.action = 'Invite'
        user.organ = fraction
        
        db.session.commit()

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Ошибка сохранения в базе данных (Users): {str(e)}")
        return jsonify({"success": False, "message": "Произошла ошибка при сохранении данных. Попробуйте снова."}), 500

    try:
      new_action = ActionUsers(
        discordid = user.discordid,
        discordname = user.discordname,
        static = user.static,
        nikname = user.nikname,
        action = 'Invite',
        curr_rank = 1,
        prev_rank = 0,
        author_id = current_user.id
      )
      db.session.add(new_action)
      db.session.commit()
      

    except SQLAlchemyError as e:
      db.session.rollback()
      logging.error(f"Ошибка сохранения в базе данных (ActionUsers): {str(e)}")
      return jsonify({"success": False, "message": "Ошибка при сохранении действия пользователя."}), 500

    else:
      send_to_bot_ka('Invite', user.static, current_user.discordid, user.discordid, user.curr_rank, user.prev_rank, current_user.nikname, user.nikname, reason, fraction)
      send_to_bot_invite(password, user.discordid, user.static, user.organ)
      logging.info('Пользователь был успешно добавлен в бд Users.')      
      if int(rank) > 1:
          process_raise(user, rank, reason, fraction)
          return jsonify({"success": True, "message": "Инвайт отправлен, пользователь был повышен."}), 200
      
      return jsonify({"success": True, "message": "Пользователь успешно добавлен!"}), 200

def process_new_invite(static, rank, nickname, discord_id, reason, fraction):
    from __init__ import db, Users, ActionUsers, PermissionUsers, get_next_id_user, get_next_id_permission
    """Обрабатывает Инвайт если пользователя нет в БД"""
    discord_name = send_to_bot_get_dsname(discord_id)
    if existing_discord_in_multiple_organizations(discord_id):
        return jsonify({"success": False, "message": "Данный дискорд уже состоит в 2-ух гос. структурах!"}), 400

    password = generate_random_password()
    hash_password = generate_password_hash(password)

    try:
      try:
        new_user = Users(
          id=get_next_id_user(),
          discordid=discord_id,
          discordname=discord_name,
          static=static,
          nikname=nickname,
          action='Invite',
          organ=fraction,
          prev_rank=0,
          curr_rank=1,
          password=hash_password
        )
        db.session.add(new_user)
        db.session.commit()

      except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Ошибка сохранения в базе данных (Users): {str(e)}")
        return jsonify({"success": False, "message": "Произошла ошибка при сохранении данных. Попробуйте снова."}), 500

      user = Users.query.filter_by(static=static).first()
      try:
        new_permission = PermissionUsers(
            id=get_next_id_permission(),
            author_id=user.id
        )
        db.session.add(new_permission)
        db.session.commit()

      except SQLAlchemyError as e:
          db.session.rollback()
          logging.error(f"Ошибка сохранения в базе данных (PermissionUsers): {str(e)}")
          return jsonify({"success": False, "message": "Ошибка при сохранении прав пользователя."}), 500

      try:
          new_action = ActionUsers(
              discordid = discord_id,
              discordname = discord_name,
              static = static,
              nikname = nickname,
              action = 'Invite',
              curr_rank = 1,
              prev_rank = 0,
              author_id = current_user.id
          )
          db.session.add(new_action)
          db.session.commit()

      except SQLAlchemyError as e:
          db.session.rollback()
          logging.error(f"Ошибка сохранения в базе данных (ActionUsers): {str(e)}")
          return jsonify({"success": False, "message": "Ошибка при сохранении действия пользователя."}), 500
    
    except SQLAlchemyError as e:
      db.session.rollback()
      logging.error(f"Ошибка сохранения: {str(e)}")
      return jsonify({"success": False, "message": "Ошибка при сохранении действия пользователя."}), 500

    else:
        send_to_bot_ka('Invite', static, current_user.discordid, user.discordid, user.curr_rank, user.prev_rank, current_user.nikname, user.nikname, reason, fraction)
        send_to_bot_invite(password, discord_id, static, user.organ)
        logging.info('Пользователь был успешно добавлен в бд Users.')
        if int(rank) > 1:
            process_raise(user, rank, reason, fraction)
            return jsonify({"success": True, "message": "Инвайт отправлен, пользователь был повышен."}), 200
        
        return jsonify({"success": True, "message": "Пользователь успешно добавлен!"}), 200


def process_raise(user, rank, reason, fraction):
    from __init__ import db, ActionUsers, permissionRoles
    """Обрабатывает повышение пользователя."""

    permission_current = current_user.permissions[0]
    permission_user = user.permissions[0]
    if not permission_current.tech or not permission_current.admin:
      if permission_user and (permission_user.admin or permission_user.tech):
        return jsonify({"success": False, "message": "Вы не можете уволить админа/разработчика."}), 403

      if current_user.organ != user.organ:
        return jsonify({"success": False, "message": "Вы не можете уволить игрока другой фракции."}), 403

      if current_user.curr_rank <= user.curr_rank:
        return jsonify({"success": False, "message": "Вы не можете повысить игрока, если вы ниже рангом."}), 403
          
    permissions_roles = permissionRoles.query.filter_by(fraction=fraction).all()
    for permissions_role in permissions_roles:
      if int(permissions_role.position_rank) == int(rank):
        if permissions_role.roles['dep_lider']:
          permission_user.dep_lider = True
        else:
          permission_user.dep_lider = False
          
        if permissions_role.roles['high_staff']:
          permission_user.high_staff = True
        else:
          permission_user.high_staff = False
          
        if permissions_role.roles['judge']:
          permission_user.judge = True
        else:
          permission_user.judge = False
          
        if permissions_role.roles['prosecutor']:
          permission_user.prosecutor = True
        else:
          permission_user.prosecutor = False
          
        if permissions_role.roles['lawyer']:
          permission_user.lawyer = True
        else:
          permission_user.lawyer = False
          
        if permissions_role.roles['news_creation']:
          permission_user.create_news = True
        else:
          permission_user.create_news = False
          
        if permissions_role.roles['documentation_creation']:
          permission_user.creation_doc = True
        else:
          permission_user.creation_doc = False
        
    try:
        user.action = 'Raising'
        user.prev_rank = user.curr_rank
        user.curr_rank = rank
        db.session.commit()

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Ошибка сохранения в базе данных (Users): {str(e)}")
        return jsonify({"success": False, "message": "Произошла ошибка при сохранении данных. Попробуйте снова."}), 500

    try:
        new_action = ActionUsers(
            discordid = user.discordid,
            discordname = user.discordname,
            static = user.static,
            nikname = user.nikname,
            action = 'Raising',
            curr_rank = user.curr_rank,
            prev_rank = user.prev_rank,
            author_id = current_user.id
        )
        db.session.add(new_action)
        db.session.commit()

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Ошибка сохранения в базе данных (ActionUsers): {str(e)}")
        return jsonify({"success": False, "message": "Ошибка при сохранении действия пользователя."}), 500

    else:
        send_to_bot_ka('Raising', user.static, current_user.discordid, user.discordid, user.curr_rank, user.prev_rank, current_user.nikname, user.nikname, reason, fraction)
        logging.info('Пользователь был успешно обновлен в бд Users.')
        return jsonify({"success": True, "message": "Пользователь был повышен!"}), 200


def process_demotion(user, rank, reason, fraction):
    from __init__ import db, ActionUsers, permissionRoles
    """Обрабатывает понижение пользователя."""

    permission_current = current_user.permissions[0]
    permission_user = user.permissions[0]
    if not permission_current.tech or not permission_current.admin:
        if permission_user and (permission_user.admin or permission_user.tech):
            return jsonify({"success": False, "message": "Вы не можете уволить админа/разработчика."}), 403

        if current_user.organ != user.organ:
            return jsonify({"success": False, "message": "Вы не можете уволить игрока другой фракции."}), 403

        if current_user.curr_rank <= user.curr_rank:
            return jsonify({"success": False, "message": "Вы не можете понизить игрока, если вы ниже рангом."}), 403

    permissions_roles = permissionRoles.query.filter_by(fraction=fraction).all()
    for permissions_role in permissions_roles:
      if int(permissions_role.position_rank) == int(rank):
        if permissions_role.roles['dep_lider']:
          permission_user.dep_lider = True
        else:
          permission_user.dep_lider = False
          
        if permissions_role.roles['high_staff']:
          permission_user.high_staff = True
        else:
          permission_user.high_staff = False
          
        if permissions_role.roles['judge']:
          permission_user.judge = True
        else:
          permission_user.judge = False
          
        if permissions_role.roles['prosecutor']:
          permission_user.prosecutor = True
        else:
          permission_user.prosecutor = False
          
        if permissions_role.roles['lawyer']:
          permission_user.lawyer = True
        else:
          permission_user.lawyer = False
          
        if permissions_role.roles['news_creation']:
          permission_user.create_news = True
        else:
          permission_user.create_news = False
          
        if permissions_role.roles['documentation_creation']:
          permission_user.creation_doc = True
        else:
          permission_user.creation_doc = False
    
    try:
        user.action = 'Demotion'
        user.prev_rank = user.curr_rank
        user.curr_rank = rank
        db.session.commit()

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Ошибка сохранения в базе данных (Users): {str(e)}")
        return jsonify({"success": False, "message": "Произошла ошибка при сохранении данных. Попробуйте снова."}), 500

    try:
        new_action = ActionUsers(
            discordid = user.discordid,
            discordname = user.discordname,
            static = user.static,
            nikname = user.nikname,
            action = 'Demotion',
            curr_rank = user.curr_rank,
            prev_rank = user.prev_rank,
            author_id = current_user.id
        )
        db.session.add(new_action)
        db.session.commit()

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Ошибка сохранения в базе данных (ActionUsers): {str(e)}")
        return jsonify({"success": False, "message": "Ошибка при сохранении действия пользователя."}), 500

    else:
        send_to_bot_ka('Demotion', user.static, current_user.discordid, user.discordid, user.curr_rank, user.prev_rank, current_user.nikname, user.nikname, reason, fraction)
        logging.info('Пользователь был успешно обновлен в бд Users.')
        return jsonify({"success": True, "message": "Пользователь был понижен!"}), 200

def process_dismissal(user, reason, fraction):
  from __init__ import db, ActionUsers, Users
  """Обрабатывает увольнение пользователя."""
  
  permission_current = current_user.permissions[0]
  permission_user = user.permissions[0]

  # Проверка прав
  if not permission_current.admin or not permission_current.tech:
    if permission_user and (permission_user.admin or permission_user.tech):
      return jsonify({"success": False, "message": "Вы не можете уволить админа/разработчика."}), 403

    if current_user.organ != user.organ:
      return jsonify({"success": False, "message": "Вы не можете уволить игрока другой фракции."}), 403

    if current_user.curr_rank <= user.curr_rank:
      return jsonify({"success": False, "message": "Вы не можете уволить игрока, если вы ниже рангом."}), 403

  if user.action == 'Dismissal':
    return jsonify({"success": False, "message": "Игрок уже был уволен."}), 400

  try:
    user.action = 'Dismissal'
    user.organ = 'Гражданин'
    user.prev_rank = user.curr_rank
    user.curr_rank = 0

    permission_user.lider = False
    permission_user.dep_lider = False
    permission_user.high_staff = False
    permission_user.creation_doc = False
    permission_user.create_news = False
    permission_user.judge = False
    permission_user.lawyer = False
    permission_user.prosecutor = False

    new_action = ActionUsers(
      discordid=user.discordid,
      discordname=user.discordname,
      static=user.static,
      nikname=user.nikname,
      action='Dismissal',
      curr_rank=user.curr_rank,
      prev_rank=user.prev_rank,
      author_id=current_user.id
    )
    db.session.add(new_action)
    db.session.commit()

    send_to_bot_dismissal(user.discordid, user.static, user.organ)
    send_to_bot_ka('Dismissal', user.static, current_user.discordid, user.discordid, user.curr_rank, user.prev_rank, current_user.nikname, user.nikname, reason, fraction)

    logging.info('Пользователь был успешно уволен.')

  except SQLAlchemyError as e:
    db.session.rollback()
    logging.error(f"Ошибка базы данных: {str(e)}")
    return jsonify({"success": False, "message": "Ошибка базы данных, попробуйте позже."}), 500
  
@main.route('/getPlayerData', methods=['GET'])
@limiter.limit("10 per minute")
@check_user_action
@login_required
def get_player_data():
  from __init__ import Users
  
  static_value = request.args.get('static')
  player = Users.query.filter_by(static=static_value).first()

  if player:
    return jsonify({'success': True, 'discord': player.discordid , 'nickname': player.nikname, 'action': player.action})
  else:
    return jsonify({'success': False})

@main.route('/audit', methods=['POST', 'GET'])
@limiter.limit("20 per minute")
@check_user_action
@login_required
def audit():
  from __init__ import db, Users
  
  permission = current_user.permissions[0]
  if not (permission.high_staff or permission.lider or permission.dep_lider or permission.admin or permission.tech):
    return jsonify({"success": False, "message": "Доступ запрещен, отсутствуют права.", "redirect_url": request.referrer}), 403

  if request.method == 'POST':
    data = request.get_json()
    static = data.get('static')
    nickname = data.get('nickname')
    discord_id = data.get('discord')
    reason = data.get('reason')
    rank_data = data.get('rank')
    dismissal = data.get('dismissal')
    fraction = data.get('fraction', current_user.organ)
    
    filename = "./python/name-ranks.json"
    ranks = read_ranks(filename)

    if fraction not in ranks:
      return jsonify({"success": False, "message": "Неверная фракция."}), 400
    
    rank_id = int(rank_data)
    fraction_ranks = ranks[fraction]
    
    if not any(rank['id'] == rank_id for rank in fraction_ranks):
      return jsonify({"success": False, "message": "Указанный ранг не существует в данной фракции."}), 400
    
    leader_rank = next((rank for rank in fraction_ranks if rank.get("leader")), None)
    if (leader_rank and rank_id == leader_rank["id"]) and not (current_user.permissions[0].admin or current_user.permissions[0].tech):
      return jsonify({"success": False, "message": f"Ошибка: выбранный ранг с ID {rank_id} является рангом лидера {leader_rank['name']}."}), 400
    
    if current_user.discordid == discord_id and not (current_user.permissions[0].admin or current_user.permissions[0].tech):
      return jsonify({"success": False, "message": "Вы не можете выбрать себя."}), 400

    if current_user.curr_rank < int(rank_data) and not (current_user.permissions[0].admin or current_user.permissions[0].tech):
      return jsonify({"success": False, "message": "Ваш текущий ранг выше выбранного. Вы не можете выбрать этот ранг."}), 400
  
    discord_id_regex = r'^\d{17,19}$'
    if not re.match(discord_id_regex, discord_id):
      return jsonify({"success": False, "message": "Discord ID должен быть числовым значением длиной от 17 до 19 символов."}), 400
    
    valid_fractions = ['LSPD', 'LSCSD', 'EMS', 'SANG', 'GOV', 'FIB', 'WN']
    if fraction not in valid_fractions:
      return jsonify({ 'success': False, 'message': "Не неверное название фракции." }), 400

    if static == current_user.static:
      return jsonify({"success": False, "message": "Вы не можете производить действия над собой."}), 400
    
    user = Users.query.filter_by(static=static).first()
    
    nickname_regex = r'^[A-Za-z]+(?:\s[A-Za-z]+)*$'
    if user and not (user.permissions[0].admin or user.permissions[0].tech):
      if not re.match(nickname_regex, nickname):
        return jsonify({"success": False, "message": "Ник должен быть в формате 'Nick Name'"}), 400
    
    if not user:
      process_new_invite(static, rank_data, nickname, discord_id, reason, fraction)
      return jsonify({"success": True, "message": f"Вы успешно приняли игрока."}), 200

    elif user and user.action == 'Dismissal' and dismissal != 'dismissal':
      process_invite_action(user, rank_data, reason, fraction)
      return jsonify({"success": True, "message": f"Вы успешно приняли игрока."}), 200
  
    if fraction != user.organ and user:
      return jsonify({"success": False, "message": "Вы не можете выбрать ранг другой фракции."}), 400

    elif user and dismissal == 'dismissal':
      process_dismissal(user, reason, fraction)
      return jsonify({"success": True, "message": f"Вы успешно уволили {user.nikname} #{user.static}"}), 200

    elif user and user.curr_rank < int(rank_data):
      process_raise(user, rank_data, reason, fraction)
      return jsonify({"success": True, "message": f"Вы успешно повысили {user.nikname} #{user.static}"}), 200

    elif user and user.curr_rank > int(rank_data):
      process_demotion(user, rank_data, reason, fraction)
      return jsonify({"success": True, "message": f"Вы успешно понизили {user.nikname} #{user.static}"}), 200

    return jsonify({"success": False, "message": "Не удалось выполнить действие."}), 400
  
  organ = current_user.organ
  color = color_organ(organ)
  filename = "./python/name-ranks.json"
  ranks = read_ranks(filename)
  return render_template('ka.html', organ=organ, color=color, ranks=ranks)

@main.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
  logout_user()
  return jsonify({
        "success": True,
        "message": f"Вы вышли с аккаунта.",
      }), 200

@main.route('/switch_account/<int:user_id>', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
@login_required
def switch_account(user_id):
    from __init__ import Users

    new_user = Users.query.filter_by(id=user_id, discordid=current_user.discordid).first()
    if new_user:
      logout_user()
      login_user(new_user)
      
      return jsonify({
        "success": True,
        "message": f"Вы переключились на аккаунт {new_user.nikname}.",
        "new_user": {
          "id": new_user.id,
          "nikname": new_user.nikname,
          "discordid": new_user.discordid
        }
      }), 200
    else:
      return jsonify({
        "success": False,
        "message": "Ошибка: аккаунт не найден или недоступен."
      }), 400

@main.route('/profile', methods=['GET'])
@limiter.limit("15 per minute")
@check_user_action
@login_required
def profile():
  from __init__ import Users, guestUsers, ActionUsers
  is_guest = current_user.user_type == 'guest'
  if not is_guest:
    organ = current_user.organ
    rank = current_user.curr_rank
    color = color_organ(organ)
    
    ka_log = ActionUsers.query.filter_by(static=current_user.static).all()
    filename = "./python/name-ranks.json"
    ranks = read_ranks(filename)
    rank_name = get_rank_info(ranks , organ, rank)
    curr_users = Users.query.filter(
            Users.discordid == current_user.discordid,
            Users.id != current_user.id
        ).all()
    return render_template('profile.html', ka_log=ka_log, rank_name=rank_name, color=color, current_user=current_user, is_guest=is_guest, curr_users=curr_users)
  else:
    return render_template('profile.html', current_user=current_user, is_guest=is_guest, guestUsers=guestUsers)
  
def check_perm_changedata():
  if current_user.permissions[0].tech:
    return 5
  elif current_user.permissions[0].admin:
    return 4
  elif current_user.permissions[0].lider:
    return 3
  elif current_user.permissions[0].dep_lider:
    return 2
  elif current_user.permissions[0].high_staff:
    return 1
  
  return 0

@main.route('/getSearchUser', methods=['GET'])
@limiter.limit("15 per minute")
@check_user_action
@login_required
def get_search_data():
    from __init__ import Users
    input_val = request.args.get('inputVal', '').strip()
    filter_val = request.args.get('filterVal', '').strip()

    query = Users.query
    if filter_val == 'nickname':
      query = query.filter(Users.nikname.ilike(f"%{input_val}%"))
    elif filter_val == 'static':
      query = query.filter(Users.static.ilike(f"%{input_val}%"))
    elif filter_val == 'discord':
      query = query.filter(Users.discordname.ilike(f"%{input_val}%"))

    results = query.all()

    filtered_data = [
        {
            "id": user.id,
            "nikname": user.nikname,
            "static": user.static,
            "organ": user.organ,
            "curr_rank": user.curr_rank,
            "discordname": user.discordname
        } for user in results
    ]

    return jsonify({"success": True, "results": filtered_data})

@main.route('/check_permissions', methods=['POST'])
@limiter.limit("10 per minute")
@login_required
def check_permissions():
    permission = current_user.permissions[0]
    if not (permission.lider or permission.dep_lider or permission.admin or permission.tech):
        return jsonify({"success": False, "message": "У вас недостаточно прав для выполнения этого действия."}), 403
    return jsonify({"success": True, "message": "Доступ разрешен."}), 200

@main.route('/database', methods=['GET'])
@limiter.limit("15 per minute")
@check_user_action
@login_required
def database():
  from __init__ import Users, permissionRoles
  perm_level = check_perm_changedata()
  if perm_level == 0:
    return redirect(url_for('main.audit'))
  organ = current_user.organ
  rank = current_user.curr_rank
  users = Users.query.all()
  ranks = read_ranks("./python/name-ranks.json")
  color = color_organ(organ)
  filename = "./python/name-ranks.json"
  ranks = read_ranks(filename)
  rank_name = get_rank_info(ranks, organ, rank)

  roles_permission = permissionRoles.query.all()
  
  groups = {}
  for group_name, rank_items in ranks.items():
    groups[group_name] = rank_items

  return render_template('database.html', roles_permission=roles_permission, rank_name=rank_name, color=color, current_user=current_user, Users=users, ranks=ranks, groups=groups, more_info=False)

DATA_FILE = "./python/name-ranks.json"
def write_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)
        

@main.route('/save_roles', methods=['POST'])
@limiter.limit("3 per minute")
def save_roles():
  from __init__ import permissionRoles, db
  
  if not (current_user.permissions[0].lider or current_user.permissions[0].admin or current_user.permissions[0].tech):
    return jsonify({"success": False, "message": "У вас недостаточно прав для выполнения этого действия."}), 403
  
  data = request.get_json()
  if current_user.permissions[0].lider and current_user.organ != data['fraction'] and not (current_user.permissions[0].admin or current_user.permissions[0].tech):
    return jsonify({"success": False, "message": "Вы не можете изменять данные другой организации!"}), 403
  
  fraction = data.get('fraction')
  roles = data.get('roles', [])
  
  if not fraction or not isinstance(roles, list):
    return jsonify({"success": False, "message": "Отсутствуют необходимые данные для сохранения."}), 400
  
  try:
    for role_data in roles:
      role_id = role_data['id']
      role_permissions = {
        'dep_lider': role_data['dep_lider'],
        'high_staff': role_data['high_staff'],
        'judge': role_data['judge'],
        'prosecutor': role_data['prosecutor'],
        'lawyer': role_data['lawyer'],
        'news_creation': role_data['news_creation'],
        'documentation_creation': role_data['documentation_creation'],
      }

      existing_role = permissionRoles.query.filter_by(fraction=fraction, position_rank=role_id).first()
      if existing_role:
        existing_role.roles = role_permissions
        db.session.add(existing_role)
        
      else:
        new_role = permissionRoles(
          fraction=fraction,
          position_rank=role_data.get('id', 0), 
          roles=role_permissions
        )
        db.session.add(new_role)

    db.session.commit()
    return jsonify({"success": True, "message": "Данные успешно сохранены."}), 200

  except Exception and SQLAlchemyError as e:
    db.session.rollback()
    print(f"Ошибка при сохранении ролей: {e}")
    return jsonify({"success": False, "message": f"Ошибка при сохранении ролей"}), 500
    
    
@main.route('/save_ranks', methods=['POST'])
@limiter.limit("3 per minute")
def save_ranks():
  from __init__ import db, Users
  
  if not (current_user.permissions[0].lider or current_user.permissions[0].admin or current_user.permissions[0].tech):
    return jsonify({"success": False, "message": "У вас недостаточно прав для выполнения этого действия."}), 403
  
  data = request.get_json()
  if current_user.permissions[0].lider and current_user.organ != data['fraction'] and not (current_user.permissions[0].admin or current_user.permissions[0].tech):
    return jsonify({"success": False, "message": "Вы не можете изменять данные другой организации!"}), 403
  
  fraction = data.get('fraction')
  added = data.get('added', [])
  updated = data.get('updated', [])
  deleted = data.get('deleted', [])
  
  if not fraction or not isinstance(added, list) or not isinstance(updated, list) or not isinstance(deleted, list):
      return jsonify({"success": False, "message": "Отсутствуют необходимые данные для сохранения."}), 400
  
  filename = "./python/name-ranks.json"    
  updated_ranks = write_ranks(filename)
  old_ranks = read_ranks(filename)

  try:  
    if len(updated) >= 30:
      return jsonify({"success": False, "message": "Количество рангов не должно превышать 30."}), 400
    
    for rank_data in added:
      for rank in updated_ranks[fraction]:
        if rank['name'] == rank_data['name']:
          return jsonify({"success": False, "message": "Ранг с таким именем уже существует."}), 400
    
    updated_ranks[fraction] = sorted(updated_ranks[fraction], key=lambda x: x['id'], reverse=False)
    
    for rank_data in updated:
      rank_ids = [rank['id'] for rank in updated_ranks[fraction] if rank['name'] == rank_data['name']]
      if rank_ids:
        for rank in updated_ranks[fraction]:
          if rank['id'] in rank_ids and rank['name'] == rank_data['name']:
            rank['id'] = int(rank_data['id']) 
      else:
        new_rank = {
          'id': int(rank_data['id']),
          'name': rank_data['name'],
          'leader': False
        }
        updated_ranks[fraction].append(new_rank)
        
    updated_ranks[fraction] = sorted(updated_ranks[fraction], key=lambda x: x['id'], reverse=True)

    for rank_data in deleted:
      for rank in updated_ranks[fraction]:
        if rank['id'] == int(rank_data['id']) and rank['name'] == rank_data['name']:
          updated_ranks[fraction].remove(rank)
          break
        
      maxid = len(updated_ranks[fraction])
      for rank in updated_ranks[fraction]:
        rank['id'] = maxid
        maxid -= 1
    
    for rank in updated_ranks[fraction]:
      for old_rank in old_ranks[fraction]:
        if old_rank['id'] != rank['id'] and old_rank['name'] == rank['name']:
          users = Users.query.filter(Users.organ == fraction, Users.curr_rank == old_rank['id']).all()
          if users:
            for u in users:
              u.curr_rank = rank['id']
        
        elif old_rank['id'] == rank['id'] and old_rank['name'] != rank['name']:
          users = Users.query.filter(Users.organ == fraction, Users.curr_rank == rank['id']).all()
          if users:
            for u in users:
              u.curr_rank = old_rank['id']
              
    db.session.commit()
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(updated_ranks, f, ensure_ascii=False, indent=4)
    return jsonify({"success": True, "message": "Данные успешно сохранены."}), 200

  except Exception as e:
    db.session.rollback()
    print(f"Ошибка при сохранении рангов: {e}")
    return jsonify({"success": False, "message": "Ошибка при сохранении рангов"}), 500


@main.route('/database_change', methods=['POST'])
@limiter.limit("3 per minute")
@login_required
def database_change():
  from __init__ import Users, db
  perm_level = check_perm_changedata()
  
  if perm_level == 0:
    return jsonify({"success": False, "message": "У вас недостаточно прав для выполнения этого действия!"}), 403
  
  data = request.get_json()
  
  user_id = data.get('user_id')
  user = Users.query.get(user_id)
  admin = data.get('admin')
  lider = data.get('lider')
  dep_lider = data.get('dep_lider')
  prosecutor = data.get('prosecutor')
  high_staff = data.get('high_staff')
  creation_doc = data.get('creation_doc')
  create_news = data.get('create_news')
  lawer = data.get('lawyer')
  judge = data.get('judge')
  discordid = data.get('discordid')
  
  try:
    if perm_level >= 1:
      user.permissions[0].prosecutor = True if prosecutor == 'on' else False
      user.permissions[0].lawyer = True if lawer == 'on' else False
      user.permissions[0].judge = True if judge == 'on' else False 
      
    if perm_level >= 2:
      user.permissions[0].high_staff = True if high_staff == 'on' else False
      
    if perm_level >= 3:
      user.permissions[0].create_news = True if create_news == 'on' else False
      user.permissions[0].creation_doc = True if creation_doc == 'on' else False
      user.permissions[0].dep_lider = True if dep_lider == 'on' else False
      
      dsname = send_to_bot_get_dsname(discordid)
      if dsname == 'Не определен':
        return jsonify({"success": False, "message": "Вы ввели недействительный Discord ID"}), 400
      
      user.discordname = dsname
      user.discordid = discordid
      
    if perm_level >= 4:
      user.permissions[0].lider = True if lider == 'on' else False
      
    if perm_level == 5:
      user.permissions[0].admin = True if admin == 'on' else False
      
    db.session.commit()
    return jsonify({"success": True, "message": "Данные успешно изменены!"}), 200
  
  except Exception and SQLAlchemyError as e:
    print (str(e))
    return jsonify({"success": False, "message": "Произошла ошибка, попробуйте позже!"}), 500


@main.route('/database_getdata', methods=['GET'])
@limiter.limit("10 per minute")
def database_getdata():
  from __init__ import Users, ActionUsers
  perm_change = check_perm_changedata()
  if perm_change == 0:
    return redirect(url_for('main.index'))
  user_id = request.args.get('user_id')
  user = Users.query.get(user_id)
  ka_log = ActionUsers.query.filter_by(static=user.static).all()
  return render_template('database.html', user=user, current_user=current_user, more_info=True, perm_change=perm_change, ka_log=ka_log)


def send_to_bot_change_nickname(new_nickname, old_nickname, static, reason, discordid):
  message = {
      'new_nickname': new_nickname,
      'old_nickname': old_nickname,
      'static': static,
      'reason': reason,
      'discordid': discordid
  }
  redis_client.publish('change_nickname', json.dumps(message))

@main.route('/profile_settings', methods=['POST'])
@limiter.limit("3 per minute")
@login_required
def profile_settings():
  from __init__ import db, app
  try:
    data = request.form
    action = data.get('action')
    if action == 'nickname':
      new_nickname = data.get('new_nickname')
      reason = data.get('reason')
      nickname_regex = r'^[A-Za-z]+(?:\s[A-Za-z]+)*$'
      if not re.match(nickname_regex, new_nickname):
        return jsonify({"success": False, "message": "Ник должен быть в формате 'Nick Name'"}), 400
      
      send_to_bot_change_nickname(new_nickname, current_user.nikname, current_user.static, reason, current_user.discordid)
      return jsonify({"success": True, "message": "Nickname был отправлен на одобрение!"}), 200
        
    elif action == 'discord':
      discord = data.get('new_discordid')
      password = data.get('password-teds')
            
      discord_id_regex = r'^\d{17,19}$'
      if not re.match(discord_id_regex, discord):
        return jsonify({"success": False, "message": "Discord ID должен быть числовым значением длиной от 17 до 19 символов."}), 400
      
      if check_password_hash(current_user.password, password):
        if send_to_bot_get_dsname(discord) != 'Не определен':
          current_user.discordid = discord
          db.session.commit()
          return jsonify({"success": True, "message": "Discord ID был изменен"}), 200
        
        return jsonify({"success": False, "message": "Discord ID не определен, проверьте его правильность!"}), 404
      return jsonify({"success": False, "message": "Вы ввели неверный пароль, проверьте его правильность!"}), 404
    
    elif action == 'password':
      password_old = data.get('password-s')
      password_new = data.get('password-n')
      
      password_check =r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{10,}$'
      
      if not re.match(password_check, password_new):
        return jsonify({"success": False, "message": "Новый пароль должен содержать заглавные и строчные буквы, цифры и специальные символы"}), 400
      
      if check_password_hash(current_user.password, password_old):
        current_user.password = generate_password_hash(password_new)
        db.session.commit()
        return jsonify({"success": True, "message": "Пароль был изменен"}), 200
      return jsonify({"success": False, "message": "Вы ввели неверный пароль, проверьте его правильность!"}), 404
    
    elif action == 'avatar':
      avatar = request.files['avatar']
      if avatar.filename == '':
          return jsonify({'success': False, 'message': 'Файл не выбран'}), 400
      
      if not allowed_file(avatar.filename):
          return jsonify({'success': False, 'message': 'Недопустимый формат файла'}), 400
      
      if current_user.url_image:
        old_avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.url_image)
        if os.path.exists(old_avatar_path):
            os.remove(old_avatar_path)
      
      file_uid = str(uuid.uuid4()).replace("-", "")[:16]
      file_extension = avatar.filename.rsplit('.', 1)[1].lower()
      filename = f"{file_uid}.{file_extension}"
      file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
      
      avatar.save(file_path)
      
      current_user.url_image = filename
      db.session.commit()
      return jsonify({"success": True, "message": "Аватара была изменена"}), 200
    
    else:
      return jsonify({"success": False, "message": "Данное действие не найденно"}), 400
      
  except Exception as e:
    logging.error(f"Ошибка на стороне сервера: {str(e)}")
    return jsonify({"success": False, "message": "Произошла ошибка, попробуйте позже."}), 500

@main.route('/delete-document')
@limiter.limit("1 per minute")
def delete_document():
  from __init__  import PDFDocument, ResolutionTheUser, CustomResolutionTheUser, OrderTheUser, db
  uid = request.args.get('uid')
  
  if not uid:
    return jsonify({"success": False, "message": "Данного документа не существует"}), 400
  
  if not (current_user.permissions[0].dep_lider or current_user.permissions[0].lider or current_user.permissions[0].admin or current_user.permissions[0].tech):
    return jsonify({"success": False, "message": "У вас не прав на данное действие"}), 403
  
  document = PDFDocument.query.filter_by(uid=uid).first()
  resolution = ResolutionTheUser.query.filter_by(current_uid=uid).first()
  resolution_custom = CustomResolutionTheUser.query.filter_by(current_uid=uid).first()
  order = OrderTheUser.query.filter_by(current_uid=uid).first()
  if current_user.url_image:
    file_path = os.path.join('static', 'uploads/documents', f'{uid}.pdf')
    if os.path.exists(file_path):
      os.remove(file_path)

  try:
    if document:
      db.session.delete(document)
      
    if resolution:
      db.session.delete(resolution)
    elif resolution_custom:
      db.session.delete(resolution_custom)
    elif order:
      db.session.delete(order)
      
    db.session.commit()
    return redirect(url_for('main.doc'))
  
  except Exception and SQLAlchemyError as e:
    print (f'Ошибка сохранения {str(e)}')
    db.session.rollback()
    return jsonify({"success": False, "message": "Произошла ошибка, попробуйте позже."}), 500

@main.route('/doc')
@limiter.limit("15 per minute")
def doc():
  if not current_user.is_authenticated:
    message = 'Вам необходимо залогироваться на сайте, дабы воспользоваться данной функцией!', 403
    return render_template('doc.html', is_permission=False, is_authenticated=False, message=message)

  perm_user = current_user.permissions[0]
  if not perm_user or not (perm_user.creation_doc or perm_user.dep_lider or perm_user.lider or perm_user.tech): 
    message = 'У вас отстутсвуют права для использования данной функции!', 403
    return render_template('doc.html', is_permission=False, is_authenticated=True, message=message)
  
  nickname = current_user.nikname
  organ = current_user.organ
  color = color_organ(organ)

  return render_template('doc.html', is_permission=True, is_authenticated=True, nickname=nickname, organ=organ, color=color)

@main.route('/applay-document', methods=['GET'])
def applau_doc():
  return render_template('create_doc.html')

@main.route('/create_doc',  methods=['POST'])
@limiter.limit("2 per minute")
def create_doc():
  from __init__ import Users, PDFDocument, ResolutionTheUser, OrderTheUser, db, get_next_num_resolution, get_next_num_order

  if request.headers.get('X-Auth') != 'True':
    if not current_user.is_authenticated:
      return jsonify({"success": False, "message": "Для создания документации требуется войти в аккаунт."}), 401

    if not current_user.permissions[0].creation_doc and not current_user.permissions[0].lider and not current_user.permissions[0].tech and not current_user.permissions[0].admin:
      return jsonify({"success": False, "message": "У вас не прав для создания документации."}), 403
  
  data = request.get_json()
  
  custom_button_pressed = data.get('custom_button_pressed')
  typeDoc = data.get('type_doc')
  nickname = data.get('nickname')
  static = data.get('static')
  
  if typeDoc == 'Order':
    def create_order_header(pdf, title, subtitle, subtitle2):
      pdf.setFont("TimesNewRoman-Bold", 14)
      pdf.drawString(50 * mm, 235 * mm, title)
      pdf.drawString(70 * mm, 230 * mm, subtitle)
      pdf.setFont("TimesNewRoman-Bold", 16)
      pdf.drawString(80 * mm, 220 * mm, subtitle2)

    def add_order_details(pdf, details, y, max_width=95):
      pdf.setFont("TimesNewRoman", 12)
      line_height = pdf._fontsize + 2 
      subheading_indent = 2 * mm 

      for text in details:
          if text.startswith("4. Особые указания:") or text.startswith("   "):
              current_indent = subheading_indent
          else:
              current_indent = line_height

          wrapped_text = wrap(text, width=max_width) 
          for line in wrapped_text:
              pdf.drawString(15 * mm, y, line)
              y -= line_height
          
          y -= current_indent

      return y
    
    def get_basis_for_immunity_removal(document_string):
      regex = r"^(Иск|Прокуратура)\s№\s*(\d+)$"
      match = re.match(regex, document_string)
      
      if match:
        return match.group(1), match.group(2)
      else:
        return None, None

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    # Установка шрифтов
    font_path = os.path.join('static', 'fonts', 'times.ttf')
    pdfmetrics.registerFont(TTFont('TimesNewRoman', font_path))
    pdfmetrics.registerFont(TTFont('TimesNewRoman-Bold', os.path.join('static', 'fonts', 'timesbd.ttf')))
    pdf.setFont("TimesNewRoman", 12)

    # Заголовок изображения и логотипа
    image_path = os.path.join('static', 'img', 'DepOfJustice.png')
    pdf.drawImage(image_path, 50 * mm, 245 * mm, width=100 * mm, height=50 * mm)

    # Текст разделителя
    separator_path = os.path.join('static', 'img', 'text separator.png')
    pdf.drawImage(separator_path, 10 * mm, 210 * mm, width=190 * mm, height=10 * mm)

    global record
    # Получение номера документа
    record = get_next_num_order()
    new_resolution_number = increment_number_with_leading_zeros(record)
    draw_text(pdf, 150, 200, f"Дата: {datetime.now().strftime('%d.%m.%Y')}")
    draw_text(pdf, 30, 200, f"Doc. No: {new_resolution_number}")
    
    # Стартовая координата y
    y = 190

    typeOrder = data.get('typeOrder')
    
    # Динамическое заполнение по типу ордера
    if typeOrder == 'AS' or typeOrder== 'Arrest and Search':
      create_order_header(pdf, "UNITED STATES DEPARTMENT OF JUSTICE", "прокуратура штата Сан-Андреас", 'Arrest and Search')
      str_typeOrder = 'Arrest and Search'
      offwork = data.get('param4')
      time = data.get('param3')
      articlesAccusation = data.get('param1')
      termImprisonment = data.get('param2')

      if not all([offwork, time, articlesAccusation, termImprisonment, static, nickname]):
        return jsonify({"success": False, "message": "Все поля должны быть заполнены."}), 400
      
      details = [
          "1. Цель. Проведение процедуры законного задержания гражданина штата Сан-Андреас, "
          f"{nickname}, с номером паспорта {static}, с последующим заключением в Федеральной "
          f"тюрьме сроком на {termImprisonment}.", 

          "2. Пояснение к цели. Данный ордер выдан для законного задержания гражданина и его последующего "
          "увольнения с занимаемой государственной должности. После этого осуществляется арест " 
          f"на срок {termImprisonment}.", 

          "3. Основания для авторизации ордера. Гражданин виновен в нарушении следующих положений "
          f"законодательства штата Сан-Андреас: {articlesAccusation}. Дополнительно, к делу прилагается документация с "
          f"номерами производств: {offwork}.",

          f"4. Сроки исполнения. Ордер вступает в силу с момента его публикации и подписания на официальном "
          f"портале штата Сан-Андреас, и остается действительным {time}, указанных в нем целей."
      ]
      y = add_order_details(pdf, details, y * mm)

    elif typeOrder == 'RI' or typeOrder == 'Removal of Immunity':
      create_order_header(pdf, "UNITED STATES DEPARTMENT OF JUSTICE", "прокуратура штата Сан-Андреас", 'Removal of Immunity')
      str_typeOrder = 'Removal of Immunity'
      applicationNum = data.get('applicationNum')
      degreeRI = data.get('degreeRI')
      time = data.get('param3')

      if not all([applicationNum, degreeRI, time, static]):
        return jsonify({"success": False, "message": "Все поля должны быть заполнены."}), 400
      
      basis_type, basis_number = get_basis_for_immunity_removal(applicationNum)

      if not basis_type or not basis_number:
        return jsonify({"success": False, "message": "Неверный формат. Номер заявления должен быть формата, Иск/Прокуртура № XXX"}), 400

      if basis_type == "Иск":
        basis_text = f"исковому заявлению № {basis_number}"
      else:
        basis_text = f"заявлению в прокуратуру № {basis_number}"
    
      if degreeRI == 'частично':
        details = [
            f"1. Цель. Частичное снятие статуса неприкосновенности у гражданина {nickname if nickname != '' else ''}, с номером паспортные "
            f"данные {static}, для проведения следственных действий в рамках прокурорского расследования.", 

            "2. Разрешение. Настоящий ордер предоставляет Прокуратуре штата Сан-Андреас право на осуществление "
            "следственных действий в отношении указанного лица, за исключением задержания и "
            "применения ограничительных мер, связанных с арестом.",

            f"3. Ордер выдан в связи с проведением прокурорской проверки по {basis_text} и расследования "
            "в отношении лица, указанного в пункте 1.",

            f"4. Действие данного ордера оканчивается в месте с завершением прокурорского расследования "
            f"по {basis_text}, либо до его отмены компетентными органами."
        ]

      elif degreeRI == 'полностью':
        details = [
            f"1. Цель. Полное снятие статуса неприкосновенности с гражданина {nickname if nickname != '' else ''}, с номером паспортных данных "
            f"{static}, для задержания и проведения дальнейших процессуальных действий, включая арест.", 

            "2. Разрешение. Настоящий ордер предоставляет право на проведение следственных, процессуальных "
            "и иных необходимых действий, включая задержание и арест указанного лица, с соблюдением "
            "законодательства штата Сан-Андреас.", 

            f"3. Ордер выдан в связи с заявлением № номер заявления, в рамках которого проведение "
            "ареста признано необходимым для обеспечения безопасности и правосудия.", 

            f"4. Настоящий ордер на полное снятие неприкосновенности действует до окончания всех "
            f"процессуальных мероприятий, либо до издания иного распоряжения компетентных органов."
        ]
      
      else:
        return jsonify({"success": False, "message": "Неверный формат. Степень снятия неприкосновености может быть 'полностью' или 'частично'"}), 400
      
      y = add_order_details(pdf, details, y * mm)
    
    elif typeOrder == 'AR' or typeOrder == 'Access To Raid':
      create_order_header(pdf, "UNITED STATES DEPARTMENT OF JUSTICE", "прокуратура штата Сан-Андреас", 'Access To Raid')
      str_typeOrder = 'Access To Raid'
      nameCrimeOrgam = data.get('nameCrimeOrgan')
      adreasCrimeOrgan = data.get('adreasCrimeOrgan')
      offwork = data.get('param4')
      time = data.get('param3')
      articlesAccusation = data.get('param1')

      if not all([nameCrimeOrgam, adreasCrimeOrgan, offwork, time, articlesAccusation]):
        return jsonify({"success": False, "message": "Все поля должны быть заполнены."}), 400
      
      details = [
        "1. Цель: Прекращение преступной деятельности граждан, выявление и задержание лиц, "
        "нарушающих законодательство штата Сан-Андреас.", 

        f"2. Пояснение к цели: Пройти на территорию {nameCrimeOrgam} "
        f"расположенного по адресу: Сан-Андреас, {adreasCrimeOrgan}, совершить рейдовое мероприятие,"
        "произвести обыск членов и транспортных средств на прилегающей территории, а также складских помещений особняка с"
        "конфискацией нелегального имущества.",
      
        f"Основания для ордера: Ордер выдан на основании делопроизводства {offwork}, при "
        "наличии следующих нарушений в соответствии с Уголовным кодексом штата Сан-Андреас:                              "
        f"{articlesAccusation}", 

        f"Срок действия ордера: Ордер действителен {time} всех указанных целей и задач."
      ]
      y = add_order_details(pdf, details, y * mm)

    elif typeOrder == 'SA' or typeOrder == 'Search Access':
      create_order_header(pdf, "UNITED STATES DEPARTMENT OF JUSTICE", "прокуратура штата Сан-Андреас", 'Search Access')
      str_typeOrder = 'Search Access'
      adreasSuspect = data.get('adreasSuspect')
      carBrand = data.get('carBrand')
      articlesAccusation = data.get('param1')
      time = data.get('param3')

      if not all([adreasSuspect, carBrand, articlesAccusation, time, nickname, static]):
        return jsonify({"success": False, "message": "Все поля должны быть заполнены."}), 400
      
      details = [
        "1. Цель: Проведение обыска имущества и транспортных средств, связанных с подозреваемыми в"
        "преступной деятельности, в целях сбора доказательств и пресечения правонарушений.", 

        "2. Пояснение к цели: Разрешено проведение обыска на территории объектов, находящихся в собственности или в "
        f"распоряжении подозреваемого, {nickname} с паспортными данными {static}, "
        "включая все здания, помещения, транспортные средства и прилегающую территорию. "
        f"Объекты, подлежащие обыску, включают: адрес(a) жилого(ых) помещения(ий) {adreasSuspect} "
        f"марска т\с: {carBrand}", 
        
        "3. Основания для обыска: Обыск проводится, в соответсивии с подозрениями в совершение " 
        f"правонарушений по статьям: {articlesAccusation}", 

        f"4. Настоящий ордер действителен {time} обысковых мероприятий и сбора доказательств, необходимых для "
        "достижения целей расследования."
      ]
      y = add_order_details(pdf, details, y * mm)
    
    elif typeOrder == 'FW' or typeOrder == 'Federal Wanted':
      create_order_header(pdf, "UNITED STATES DEPARTMENT OF JUSTICE", "прокуратура штата Сан-Андреас", 'Federal Wanted')
      str_typeOrder = 'Federal Wanted'
      articlesAccusation = data.get('param1')
      time = data.get('param3')
      offwork = data.get('param4')

      if not all([articlesAccusation, time, offwork, nickname, static]):
        return jsonify({"success": False, "message": "Все поля должны быть заполнены."}), 400
      
      details = [
        f"1. Цель: Объявление в розыск и задержание гражданина {nickname} с паспортынми данными {static}, "
        f"подозреваемого в совершении преступлений, с целью пресечения его противоправной деятельности и "
        "обеспечения его явки для проведения следственных и процессуальных действий.",

        "2. Пояснение к цели: Данный ордер выдается для организации оперативно-розыскных мероприятий "
        f"c целью установления местонахождения гражданина {nickname}, с паспортынми данными {static} "
        f"имеются обоснованные подозрения в нарушении законодательства штата Сан-Андреас. Подозреваемый "
        "обвиняется в совершении следующих преступлений согласно Уголовному кодексу штата Сан-Андреас:                " 
        f"{articlesAccusation}.", 

        "3. Основания для объявления в розыск: Ордер на объявление в розыск выдан на основании дела "
        f"{offwork} в связи с наличием подозрений, что указанный гражданин может представлять "
        "опасность для общества или скрываться от следствия.", 

        "4. Особые указания:"
        "Правоохранительным органам штата Сан-Андреас предписывается:",
        
        "   1. Установить место нахождения подозреваемого и при обнаружении произвести задержание в "
        "      рамках полномочий.",
        "   2. При необходимости привлечь дополнительные подразделения для проведения оперативных действий.",
        "   3. Обеспечить сохранность всех потенциальных доказательств, которые могут быть обнаружены "
        "      при задержании подозреваемого.",

        f"5. Ордер на розыск действует {time} подозреваемого или его добровольной явки в "
        "правоохранительные органы."
      ]
      y = add_order_details(pdf, details, y * mm)

    else:
      print("Ошибка. Такого ордера не существуует обратитесь в тех. поддержку")
      return jsonify({"success": False, "message": "Ошибка. Такого ордера не существуует обратитесь в тех. поддержку"}), 404

    # Сохранение и запись PDF
    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    uid = ''.join([str(random.randint(0, 9)) for _ in range(26)])
    file_path = os.path.join('static', 'uploads/documents', f'{uid}.pdf')
    with open(file_path, 'wb') as f:
      f.write(buffer.getvalue())
    
    curr_user = None
    user_id = request.headers.get('X-User-ID')
    if user_id:
      curr_user = Users.query.get(int(user_id))
      
    pdf_document = PDFDocument(
      author_id= curr_user.id if curr_user else current_user.id,
      uid=uid,
      content=file_path
    )
    db.session.add(pdf_document)
    db.session.commit() 

    send_to_bot_new_resolution(
        uid=uid, 
        nickname=curr_user.nikname if curr_user else current_user.nikname, 
        static=curr_user.static if curr_user else current_user.static, 
        discordid=curr_user.discordid if curr_user else current_user.discordid, 
        status='moder', 
        number_resolution=new_resolution_number
    )

    user = Users.query.filter_by(static=static).first()
    new_order = OrderTheUser(
        current_uid=uid,  
        author_id=curr_user.id if curr_user else current_user.id,
        nickname_accused=nickname,
        static_accused=static if static != '' else None,
        discord_accused=user.discordid if user else None,
        type_order=str_typeOrder,
        time=data.get('param3') if data.get('param3') != '' else None,
        articlesAccusation=data.get('param1') if data.get('param1') != '' else None,
        termImprisonment=data.get('param2') if data.get('param2') != '' else None,
        offWork=data.get('param4') if data.get('param4') != '' else None,
        current_number=get_next_num_order()
    )

    db.session.add(new_order)
    db.session.commit()
    return jsonify({"success": True, "message": "Ордер был успешно создан."}), 201
  
  elif typeDoc == 'Resolution' and custom_button_pressed == 'false':
    if not any([data.get('initCase'), data.get('videoRequest'), data.get('personalRequest'), data.get('changePersonal'), data.get('banDismissalandTransfer'), data.get('workBan')]):
      return jsonify({"success": False, "message": "Для создания постановления требуется хотя бы один пункт"}), 400
    
    if not static:
      return jsonify({"success": False, "message": "Для создания постановления требуется указания статика"}), 400
    
    user = Users.query.filter_by(static=static).first()

    def generate_resolution_pdf(user, current_user, static, nickname):
      buffer = BytesIO()
      pdf = canvas.Canvas(buffer, pagesize=A4)
      pdf.setTitle("Постановление")

      pdfmetrics.registerFont(TTFont('TimesNewRoman', os.path.join('static', 'fonts', 'times.ttf')))
      pdfmetrics.registerFont(TTFont('TimesNewRoman-Bold', os.path.join('static', 'fonts', 'timesbd.ttf')))
      
      image_path = os.path.join('static', 'img', 'DepOfJustice.png')
      pdf.drawImage(image_path, 50 * mm, 245 * mm, width=100 * mm, height=50 * mm)
      
      draw_text(pdf, 50, 235, "UNITED STATES DEPARTMENT OF JUSTICE", font="TimesNewRoman-Bold", size=14)
      draw_text(pdf, 70, 230, "прокуратура штата Сан-Андреас", font="TimesNewRoman-Bold", size=14)
      draw_text(pdf, 60, 225, "90001, г. Лос-Сантос, Рокфорд-Хиллз, Карцер-Вей")

      pdf.drawImage(os.path.join('static', 'img', 'text separator.png'), 10 * mm, 210 * mm, width=190 * mm, height=10 * mm)
      global record
      record = get_next_num_resolution()
      new_resolution_number = increment_number_with_leading_zeros(record)
      draw_text(pdf, 150, 200, f"Дата: {datetime.now().strftime('%d.%m.%Y')}")
      draw_text(pdf, 30, 200, f"Doc. No: {new_resolution_number}")

      draw_text(pdf, 15, 190, f"Я, {current_user.nikname}, являюсь Прокурором штата San Andreas, пользуясь правами, данными мне")
      draw_text(pdf, 15, 185, "Конституцией и законодательством штата San Andreas, а также иными нормативно-правовыми актами,")
      draw_text(pdf, 15, 180, "в связи с необходимостью обеспечения законности и правопорядка в рамках своих полномочий,")
      draw_text(pdf, 80, 170, "ПОСТАНОВЛЯЮ:")

      y = 160
      num = 1
      if data.get('initCase'):
        text = (f"{num}. Возбудить уголовное дело в отношении {'сотрудника ' + user.organ if user else 'гражданина'} "
                f"{nickname if nickname != '' else ''}, с номером паспорта {static}. Присвоить делу идентификатор {data.get('numCase')} и принять его к производству прокуратурой штата.")
        y = draw_multiline_text(pdf, text, 15, y)
        y -= 5
        num += 1

      if data.get('videoRequest'):
        text = (f"{num}. Обязать {'сотрудника ' + user.organ if user else 'гражданина'} {nickname if nickname != '' else ''}, с номером паспортных данных {static}, "
                f"в течение 24 часов предоставить на почту Прокурора {current_user.nikname} ({current_user.discordname}@gov.sa) видеозапись процессуальных действий, проведённых в отношении {data.get('victimNickname')}, время провдение ареста {data.get('arrestTime')}. "
                f"Запись должна содержать момент ареста {data.get('arrestTime')} и фиксировать предполагаемое нарушение.")
        y = draw_multiline_text(pdf, text, 15, y)
        y -= 5
        num += 1

      if data.get('personalRequest'):
        text = (f"{num}. Предоставить личное дело {'сотрудника ' + user.organ if user else 'гражданина'} {nickname if nickname != '' else ''}, "
                f"с номером паспортных данных {static}, включающее электронную почту, должность. Срок предоставления информации — 24 часа.")
        y = draw_multiline_text(pdf, text, 15, y)
        y -= 5
        num += 1

      if data.get('changePersonal'):
        text = f"{num}. Ввести запрет на смену персональных данных {'сотрудника ' + user.organ if user else 'гражданина'} {nickname if nickname != '' else ''}, с номером паспортных данных {static}."
        y = draw_multiline_text(pdf, text, 15, y)
        y -= 5
        num += 1

      if data.get('banDismissalandTransfer') and user and user.action != 'Dismissal':
        text = (f"{num}. Ввести запрет на увольнение сотрудника {user.organ} {nickname if nickname != '' else ''} с номером паспортных данных {static} "
                f"и на перевод в другие государственные структуры на период расследования по делу с идентификатором {data.get('numCase')}.")
        y = draw_multiline_text(pdf, text, 15, y)
        y -= 5
        num += 1

      if data.get('workBan') and user and user.action != 'Dismissal':
        text = f"{num}. Временно отстранить сотрудника {user.organ} {nickname}, с номером паспортных данных {static}, от исполнения служебных обязанностей на время расследования по делу с идентификатором {data.get('numCase')}."
        y = draw_multiline_text(pdf, text, 15, y)
        y -= 5
        num += 1

      sing_font_path = os.path.join('static', 'fonts', 'Updock-Regular.ttf') 
      pdfmetrics.registerFont(TTFont('Updock', sing_font_path))

      # Генерация подписи
      y += 20
      generate_signature(pdf, y, current_user, 'resolution', page=1)
      y -= 5

      pdf.showPage()
      pdf.save()
      buffer.seek(0)
      
      # Saving PDF and database operations here
      return buffer, new_resolution_number

    # Usage in main logic
    buffer, num_resolution = generate_resolution_pdf(user, current_user, static, nickname)
    
    uid = ''.join([str(random.randint(0, 9)) for _ in range(26)])
    session['uid'] = uid
    
    file_path = os.path.join('static', 'uploads/documents', f'{uid}.pdf')
    with open(file_path, 'wb') as f:
        f.write(buffer.getvalue())
    
    pdf_document = PDFDocument(
      author_id=current_user.id,
      uid=uid,
      content=file_path
    )
    db.session.add(pdf_document)
    db.session.commit()
    
    status = 'moder'
    send_to_bot_new_resolution(uid=uid, nickname=current_user.nikname, static=current_user.static, discordid=current_user.discordid, status=status, number_resolution=num_resolution)
    
    new_resolution = ResolutionTheUser(
      current_uid=uid, 
      author_id=current_user.id,
      nickname_accused = nickname,
      static_accused = static,
      discord_accused = user.discordid if user else None,
      initiation_case=data.get('initCase') == 'on',
      provide_video=data.get('videoRequest') == 'on',
      provide_personal_file=data.get('personalRequest') == 'on',
      changing_personal_data=data.get('changePersonal') == 'on',
      dismissal_employee=data.get('banDismissalandTransfer')== 'on',
      temporarily_suspend=data.get('workBan') == 'on',
      victim_nickname=data.get('victimNickname') if data.get('victimNickname') != '' else '', 
      time_arrest=data.get('arrestTime') if data.get('arrestTime') != '' else '',
      number_case=data.get('numCase') if data.get('numCase') != '' else '',
      current_number=get_next_num_resolution()
      )
      
    db.session.add(new_resolution)
    db.session.commit()
    return jsonify({"success": True, "message": "Постановление было успешно создано."}), 201

  elif typeDoc == 'Resolution' and custom_button_pressed:
    custom_text_fields = [request.form[key] for key in request.form if key.startswith('custom_text_')]
    def add_order_details(pdf, details, y, max_width=95, line_spacing=12):
      pdf.setFont("TimesNewRoman", 12)  
      last_page = 1
      for text in details:
        wrapped_text = wrap(text, width=max_width) 
        for line in wrapped_text:
            if y < 20 * mm:
                last_page += 1
                pdf.showPage()
                pdf.setFont("TimesNewRoman", 12)
                y = 260 * mm
            
            pdf.drawString(15 * mm, y, line)
            y -= line_spacing 
        y -= line_spacing + 4 
          
      return y, last_page

    if not any(custom_text_fields):
      return jsonify({"success": False, "message": "Для создания кастомного постановления требуется хоя один пункт"}), 400
    
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle("Постановление")

    pdfmetrics.registerFont(TTFont('TimesNewRoman', os.path.join('static', 'fonts', 'times.ttf')))
    pdfmetrics.registerFont(TTFont('TimesNewRoman-Bold', os.path.join('static', 'fonts', 'timesbd.ttf')))

    image_path = os.path.join('static', 'img', 'DepOfJustice.png')
    pdf.drawImage(image_path, 50 * mm, 245 * mm, width=100 * mm, height=50 * mm)

    draw_text(pdf, 50, 235, "UNITED STATES DEPARTMENT OF JUSTICE", font="TimesNewRoman-Bold", size=14)
    draw_text(pdf, 70, 230, "прокуратура штата Сан-Андреас", font="TimesNewRoman-Bold", size=14)
    draw_text(pdf, 60, 225, "90001, г. Лос-Сантос, Рокфорд-Хиллз, Карцер-Вей")

    pdf.drawImage(os.path.join('static', 'img', 'text separator.png'), 10 * mm, 210 * mm, width=190 * mm, height=10 * mm)
    
    record = get_next_num_resolution()
    new_resolution_number = increment_number_with_leading_zeros(record)
    draw_text(pdf, 150, 200, f"Дата: {datetime.now().strftime('%d.%m.%Y')}")
    draw_text(pdf, 30, 200, f"Doc. No: {new_resolution_number}")

    draw_text(pdf, 15, 190, f"Я, {current_user.nikname}, являюсь Прокурором штата San Andreas, пользуясь правами, данными мне")
    draw_text(pdf, 15, 185, "Конституцией и законодательством штата San Andreas, а также иными нормативно-правовыми актами,")
    draw_text(pdf, 15, 180, "в связи с необходимостью обеспечения законности и правопорядка в рамках своих полномочий,")
    draw_text(pdf, 80, 170, "ПОСТАНОВЛЯЮ:")

    y, last_page = add_order_details(pdf, custom_text_fields, 160 * mm)
    generate_signature(pdf, y, current_user, 'resolution', page=last_page)

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    uid = ''.join([str(random.randint(0, 9)) for _ in range(26)])
    session['uid'] = uid
    
    file_path = os.path.join('static', 'uploads/documents', f'{uid}.pdf')
    with open(file_path, 'wb') as f:
      f.write(buffer.getvalue())
    
    pdf_document = PDFDocument(
      author_id=current_user.id,
      uid=uid,
      content=file_path
    )
    db.session.add(pdf_document)
    db.session.commit()
    
    from __init__ import CustomResolutionTheUser
    custom_fields_json = json.dumps(custom_text_fields)
    resolution = CustomResolutionTheUser(
      author_id=current_user.id, 
      current_uid=uid,
      custom_fields=custom_fields_json,
      current_number=get_next_num_resolution()
    )
    db.session.add(resolution)
    db.session.commit()

    status = 'moder'
    send_to_bot_new_resolution(uid=uid, nickname=current_user.nikname, static=current_user.static, discordid=current_user.discordid, status=status, number_resolution=new_resolution_number)
    return jsonify({"success": True, "message": "Кастомное постановление было успешно создано."}), 201
  else:
    print("Ошибка. Такого типа документации не существует.")
    return jsonify({"success": False, "message": "Ошибка. Такого типа документации не существует."}), 404

@main.route('/resolution', methods=['POST', 'GET'])
@limiter.limit("10 per minute")
def resolution():
    from __init__ import PDFDocument, ResolutionTheUser, OrderTheUser, Users, CustomResolutionTheUser, db
    from form import FormModerationResolution

    uid = request.args.get('uid')
    if not uid:
      return "No UID provided", 400

    uid_parts = uid.split('/')
    base_uid = uid_parts[0]
    is_moderation_link = len(uid_parts) > 1 and uid_parts[1] == 'moderation'

    pdf_doc = PDFDocument.query.filter_by(uid=base_uid).first()
    if not pdf_doc or not os.path.exists(pdf_doc.content):
      text_error = "PDF not found or invalid UID"
      return render_template('api/404.html', text_error=text_error)

    moder_resolution = ResolutionTheUser.query.filter_by(current_uid=base_uid).first()
    moder_order = OrderTheUser.query.filter_by(current_uid=base_uid).first()
    moder_custom_resolution = CustomResolutionTheUser.query.filter_by(current_uid=base_uid).first()
    if not moder_resolution and not moder_order and not moder_custom_resolution:
      return "Moderation records not found", 404

    form = FormModerationResolution()

    if moder_order and moder_order.is_modertation:
      return render_template('preview_resolution.html', pdf_path=pdf_doc.content, uid=uid)

    if moder_resolution and moder_resolution.is_modertation:
      return render_template('preview_resolution.html', pdf_path=pdf_doc.content, uid=uid)
    
    if moder_custom_resolution and moder_custom_resolution.is_modertation:
      return render_template('preview_resolution.html', pdf_path=pdf_doc.content, uid=uid)

    if is_moderation_link:
      if not current_user.is_authenticated and current_user.user_type == 'user' and current_user.curr_rank > 11 and current_user.curr_rank != 12:
        flash('Для модерации постановлений требуется войти в аккаунт!')
        send_to_bot_permission_none(True)
        return redirect(url_for('main.index'))

      if not current_user:
        flash('User not found!')
        return redirect(url_for('main.index'))

      rankuser_value = current_user.curr_rank

      def handle_moderation(moder_obj, min_rank, is_order, is_resolution, template_name):
        if current_user.organ == 'GOV' and min_rank <= rankuser_value != 12:
          if form.validate_on_submit():
            moderation = form.success.data
            reason = 'None' if form.success.data else form.reason.data
            user = Users.query.get(moder_obj.author_id)
            send_to_bot_information_resolution(user.discordid, current_user.discordid, moderation, reason, base_uid)

            if form.success.data: 
              if is_order and current_user.organ == 'GOV' and (current_user.curr_rank == 18 or current_user.curr_rank == 21):
                pdf_path = os.path.join(pdf_doc.content)
                generate_signature_order(pdf_path, current_user)
                moder_obj.is_modertation = True
                db.session.commit()

              elif is_resolution:
                moder_obj.is_modertation = True
                db.session.commit()

              else:
                flash('Вы неможе подписывать данные документы!')
                return redirect(url_for('main.doc'))
            else:
              if is_order:
                file_path = os.path.join(pdf_doc.content)
                os.remove(file_path)

                db.session.delete(moder_obj)
                db.session.delete(pdf_doc)
                db.session.commit()
              else:
                moder_obj.is_modertation = False
              db.session.commit()

            return redirect(url_for('main.doc' if form.rejected.data else 'main.resolution', uid=base_uid))
          return render_template(template_name, pdf_path=pdf_doc.content, form=form, uid=uid)
        return redirect(url_for('main.index'))

      if moder_resolution and rankuser_value >= 11:
        send_to_bot_permission_none(False)
        return handle_moderation(moder_resolution, 11, is_order=False, is_resolution=True, template_name='temporary_page.html')
      
      elif moder_order and rankuser_value >= 18:
        send_to_bot_permission_none(False)
        return handle_moderation(moder_order, 18, is_order=True, is_resolution=False, template_name='temporary_page.html')
      
      elif moder_custom_resolution and rankuser_value >= 11:
        send_to_bot_permission_none(False)
        return handle_moderation(moder_custom_resolution, 11, is_order=False, is_resolution=True, template_name='temporary_page.html')

    if not is_moderation_link:
      return redirect(url_for('main.resolution', uid=f"{base_uid}/moderation"))

    return "Unexpected error", 500

def user_is_moder(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from __init__ import PDFDocument
        
        if not current_user.is_authenticated:
            flash('Необходимо войти для доступа к этой странице.')
            return redirect(url_for('main.auth'))

        uid = request.args.get('uid')
        
        if not uid:
            flash('UID не указан.')
            return abort(400)
        
        pdf_doc = PDFDocument.query.filter_by(author_id=current_user.id, uid=uid).first()

        if not pdf_doc:
          flash('Вы не можете редактировать это постановление!')
          return redirect(url_for('main.index')) 
      
        return f(*args, **kwargs)

    return decorated_function

@main.route('/edit_doc')
@limiter.limit("15 per minute")
@user_is_moder
def edit_doc():
  from __init__ import PDFDocument
  from form import FormEditResolution
  
  uid = request.args.get('uid')
  if not uid:
      return "No UID provided", 400

  pdf_doc = PDFDocument.query.filter_by(uid=uid).first()
  if not pdf_doc:
      return "PDF not found", 404 
    
  form = FormEditResolution()
      
  return render_template('edit_doc.html', pdf_path=pdf_doc.content, form=form, uid=uid)


@main.route('/edit_resolution', methods=['GET', 'POST'])
@limiter.limit("2 per minute")
def edit_resolution():
  from __init__ import ResolutionTheUser, Users, db, PDFDocument
  from form import FormEditResolution
  
  uid = request.args.get('uid')
  
  form = FormEditResolution()
  if request.method == 'POST':
    isSend, seconds_left = is_send_allowed()
    if not isSend:
      return redirect(url_for('main.doc'))

    doc = ResolutionTheUser.query.filter_by(current_uid=uid).first()
    nickname_victim = form.param1.data
    nickname_accused = form.param2.data
    static_accused = form.param3.data
    time_arrest = form.param4.data
    del_item = form.param5.data
    del_item_list = [int(x) for x in del_item.replace(',', ' ').split() if x.isdigit()]

    static = static_accused if static_accused != '' else doc.static_accused
    nickname = nickname_accused if nickname_accused != '' else doc.nickname_accused
    nickname_victim = nickname_victim if nickname_victim != '' else doc.victim_nickname
    time_arrest = time_arrest if time_arrest != '' else doc.time_arrest

    user = Users.query.filter_by(static=static).first()

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle("Постановление")

    # Регистрация шрифтов
    pdfmetrics.registerFont(TTFont('TimesNewRoman', os.path.join('static', 'fonts', 'times.ttf')))
    pdfmetrics.registerFont(TTFont('TimesNewRoman-Bold', os.path.join('static', 'fonts', 'timesbd.ttf')))
    
    # Заголовок и логотип
    pdf.drawImage(os.path.join('static', 'img', 'DepOfJustice.png'), 50 * mm, 245 * mm, width=100 * mm, height=50 * mm)
    pdf.setFont("TimesNewRoman-Bold", 14)
    pdf.drawString(50 * mm, 235 * mm, "UNITED STATES DEPARTMENT OF JUSTICE")
    pdf.drawString(70 * mm, 230 * mm, "Прокуратура штата Сан-Андреас")
    pdf.setFont("TimesNewRoman", 12)
    pdf.drawString(60 * mm, 225 * mm, "90001, г. Лос-Сантос, Рокфорд-Хиллз, Карцер-Вей")
    pdf.drawImage(os.path.join('static', 'img', 'text separator.png'), 10 * mm, 210 * mm, width=190 * mm, height=10 * mm)

    # Номер документа и дата
    draw_text(pdf, 150, 200, f"Дата: {datetime.now().strftime('%d.%m.%Y')}")

    # Основной текст постановления
    draw_text(pdf, 15, 190, f"Я, {current_user.nikname}, являюсь Прокурором штата San Andreas, пользуясь правами, данными мне")
    draw_text(pdf, 15, 185, "Конституцией и законодательством штата San Andreas, а также иными нормативно-правовыми актами,")
    draw_text(pdf, 15, 180, "в связи с необходимостью обеспечения законности и правопорядка в рамках своих полномочий,")
    draw_text(pdf, 80, 170, "ПОСТАНОВЛЯЮ:")

    y = 160
    num = 1

    print(doc.initiation_case)
    if doc.initiation_case:
      text = (f"{num}. Возбудить уголовное дело в отношении {'сотрудника ' + user.organ if user else 'гражданина'} "
              f"{nickname if nickname != '' else ''}, с номером паспортных данных {static}. Присвоить делу идентификатор {doc.number_case} и принять его к производству прокуратурой штата.")
      y = draw_multiline_text(pdf, text, 15, y)
      y -= 5
      num += 1

    if doc.provide_video:
      text = (f"{num}. Обязать {'сотрудника ' + user.organ if user else 'гражданина'} {nickname if nickname != '' else ''}, с номером паспортных данных {static}, "
              f"в течение 24 часов предоставить на почту Прокурора {current_user.nikname} ({current_user.discordname}@gov.sa) видеозапись процессуальных действий, проведённых в отношении {nickname_victim}, время провдение ареста {time_arrest}. "
              f"Запись должна содержать момент ареста {time_arrest} и фиксировать предполагаемое нарушение.")
      y = draw_multiline_text(pdf, text, 15, y)
      y -= 5
      num += 1

    if doc.provide_personal_file:
      text = (f"{num}. Предоставить личное дело {'сотрудника ' + user.organ if user else 'гражданина'} {nickname if nickname != '' else ''}, "
              f"с номером паспортных данных {static}, включающее электронную почту, должность. Срок предоставления информации — 24 часа.")
      y = draw_multiline_text(pdf, text, 15, y)
      y -= 5
      num += 1

    if doc.changing_personal_data:
      text = f"{num}. Ввести запрет на смену персональных данных {'сотрудника ' + user.organ if user else 'гражданина'} {nickname if nickname != '' else ''}, с номером паспортных данных {static}."
      y = draw_multiline_text(pdf, text, 15, y)
      y -= 5
      num += 1

    if doc.dismissal_employee and user and user.action != 'Dismissal':
      text = (f"{num}. Ввести запрет на увольнение сотрудника {user.organ} {nickname if nickname != '' else ''} с номером паспортных данных {static} "
              f"и на перевод в другие государственные структуры на период расследования по делу с идентификатором {doc.number_case}.")
      y = draw_multiline_text(pdf, text, 15, y)
      y -= 5
      num += 1

    if doc.temporarily_suspend and user and user.action != 'Dismissal':
      text = f"{num}. Временно отстранить сотрудника {user.organ} {nickname}, с номером паспортных данных {static}, от исполнения служебных обязанностей на время расследования по делу с идентификатором {doc.number_case}."
      y = draw_multiline_text(pdf, text, 15, y)
      y -= 5
      num += 1
    
    generate_signature(pdf, y, current_user, 'resolution')
    y -= 5

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    
    file_path = os.path.join('static', 'uploads/documents', f'{uid}.pdf')
    with open(file_path, 'wb') as f:
      f.write(buffer.getvalue())

    status = 'edit'
    send_to_bot_new_resolution(uid=uid, nickname=current_user.nikname, static=current_user.static, discordid=current_user.discordid, status=status, number_resolution='123')
    
    doc.nickname_accused = nickname
    doc.static_accused = static
    doc.discord_accused = user.discordid if user else None
    doc.initiation_case=None if '1' in del_item_list else doc.initiation_case
    doc.provide_video=None if '2' in del_item_list else doc.provide_video
    doc.provide_personal_file=None if '3' in del_item_list else doc.provide_personal_file
    doc.changing_personal_data=None if '4' in del_item_list else doc.changing_personal_data
    doc.dismissal_employee=None if '5' in del_item_list else doc.dismissal_employee
    doc.temporarily_suspend=None if '6' in del_item_list else doc.temporarily_suspend
    doc.victim_nickname=nickname_victim
    doc.time_arrest=time_arrest

    db.session.commit()
    
    return redirect(url_for('main.index'))

@main.route('/district_court/information=<info_type>')
@limiter.limit("15 per minute")
def district_court_info(info_type):
    from __init__ import iskdis, Users, guestUsers, claimsStatement, courtPrecedents
    now = datetime.now()
    count = 0
    title = ""

    if info_type == 'considered_claims':
      considered_claims = claimsStatement.query.filter_by(is_archived=True).all()
      data = iskdis.query.filter(iskdis.current_uid.in_([claim.uid for claim in considered_claims])).all()
      count = claimsStatement.query.filter_by(is_archived=True).count()
      title = "Рассмотренные исковые заявления"

      return render_template(
      'info_district.html',
      timedelta=timedelta,
      district=data,
      Users=Users,
      guestUsers=guestUsers,
      count=count,
      now=now,
      info_type=info_type,
      title=title
    )

    elif info_type == 'precedents':
      title = "Сборник прецедентов"
      precedents = courtPrecedents.query.all()
      return render_template(
        'info_district.html',
        title=title,
        info_type=info_type,
        precedents=precedents
      )

    elif info_type == 'rules':
      title = "Система обращений"

      return render_template(
        'info_district.html',
        title=title,
        info_type=info_type
      )

@main.route('/create-precedents', methods=['POST'])
@limiter.limit("3 per minute")
def create_precedents():
  from __init__ import courtPrecedents, db
  
  if not current_user.permissions[0].judge:
    return jsonify({"success": False, "message": "У вас нет доступа т.к. вы не судья"}), 403
  
  data = request.get_json()
  complaint = data.get('complaint')
  date = data.get('date')
  author = data.get('author')
  link = data.get('link')
  findings = data.get('findings')
  action = data.get('action')
  date_object = datetime.strptime(date, "%d.%m.%Y %H:%M")
  
  try:
    new_precedent = courtPrecedents(
      author_id=current_user.id, 
      number_complaint=complaint, 
      date_complaint=date_object, 
      author=author, 
      link=link, 
      findings=findings,
      court=action
      )
    db.session.add(new_precedent)
    db.session.commit()

    return jsonify({"success": True, "message": "Прецедент успешно создан"}), 200
  
  except Exception and SQLAlchemyError as e:
    db.session.rollback()
    print(str(e))
    return jsonify({"success": False, "message": "Ошибка при создании прецедента"}), 500
  
@main.route('/get-application-prosecutor-content', methods=['GET'])
@limiter.limit("10 per minute")
def get_application_prosecutor_content():
  from __init__ import petitionProsecutor, Users, guestUsers
  
  now = datetime.now()
  prosecutor = petitionProsecutor.query.filter_by(is_archived=False).all()
  count = petitionProsecutor.query.filter_by(is_archived=True).count()
  
  return render_template('main/main-application-prosecutor.html', count=count, prosecutor=prosecutor, Users=Users, guestUsers=guestUsers, timedelta=timedelta, now=now)

@main.route('/create_petition_prosecutor', methods=['POST'])
@limiter.limit("3 per minute")
def petition_prosecutor():
  from __init__ import petitionProsecutor, db
  
  if not current_user.is_authenticated:
    return jsonify({"success": False, "message": "Вы не авторизованы"}), 401
  
  data = request.get_json()
  defendants = data.get('defendants')
  evidences = data.get('evidence')
  description = data.get('description')
  
  defendants=[item for item in defendants if item]
  name_static_pattern = r'^[A-Z][a-z]+ [A-Z][a-z]+ \d{1,7}$'
  faction_static_pattern = r'^(LSPD|LSCSD|FIB|SANG|EMS|WN|GOV) \d{1,7}$'
  for defendant in defendants:
    if not re.match(name_static_pattern, defendant) and not re.match(faction_static_pattern, defendant) and defendant != '':
      return jsonify({"success": False, "message": "Некорректая имя отвечика. Пример: 'Имя Фамилия Статик' или 'Фракция Статик'."}), 400
    
  youtube_regex = r'^(https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/(watch\?v=[\w-]+|.+)$'
  rutube_regex = r'^(https?:\/\/)?(www\.)?rutube\.ru\/video\/[a-zA-Z0-9]+\/?$'
  yapix_regex = r'^(https?:\/\/)?(www\.)?yapix\.ru\/video\/[a-zA-Z0-9]+\/?$'
  imgur_regex = r'^(https?:\/\/)?(www\.)?imgur\.com\/[a-zA-Z0-9]+\/?$'

  links = evidences.strip().split()
  
  if not all([evidences, description]):
    return jsonify({"success": False, "message": "Все поля должны быть заполнены"}), 404
  
  invalid_links = [link for link in links if not re.match(youtube_regex, link) and 
                                            not re.match(rutube_regex, link) and 
                                            not re.match(yapix_regex, link) and 
                                            not re.match(imgur_regex, link)]
  
  if invalid_links:
    return jsonify({"success": False, "message": "Ссылки не валиды!"}), 404
  
  try:
    new_petition = petitionProsecutor(
      author = current_user.id,
      discription = description,
      defendant = defendants,
      evidence = evidences
    )
    
    db.session.add(new_petition)
    db.session.commit()
    
  except SQLAlchemyError and Exception as e:
    print(f'Возникла проблема {str(e)}')
    db.session.rollback()
    return jsonify({"success": False, "message": "Возникла проблема при создание жалобы в Прокуратуру"}), 500

  return jsonify({"success": True, "message": "Жалоба была успешна создана"}), 201

@main.route('/application-prosecutor', methods=['GET'])
@limiter.limit("15 per minute")
def application_prosecutor():
  from __init__ import petitionProsecutor, Users, guestUsers, replottoPetitionProsecutor
  
  uid = request.args.get('uid')
  if not uid:
    return "No UID provided", 400
  
  application=petitionProsecutor.query.filter_by(uid=uid).first()
  if not application:
    return jsonify({"success": False, "message": "Жалоба не найдена"}), 404 
  
  status = None
  if current_user.id != application.author:
    status = 'author'
  elif current_user.id == application.prosecutor:
    status = 'prosecutor'
  
  replo_data = replottoPetitionProsecutor.query.filter_by(uid=uid).all()
  
  return render_template('petitions-prosecutor.html', replo_data=replo_data, Users=Users, guestUsers=guestUsers, application=application, status=status)

@main.route('/process-complaint-prosecutor', methods=['POST'])
@limiter.limit("2 per minute")
def process_complaint_prosecutor():
  from __init__ import petitionProsecutor, db, replottoPetitionProsecutor, Users, guestUsers
  
  if not current_user.is_authenticated:
    return jsonify({"success": False, "message": "Вы не авторизованы."}), 401
  
  if not current_user.permissions[0].prosecutor:
    return jsonify({"success": False, "message": "У вас нет прав для обработки жалоб в Прокуратуру."}), 403
  
  data = request.get_json()
  uid = data.get('uid')
  
  if not uid:
    return jsonify({"success": False, "message": "UID не был передан, обратитесь в тех. поддержку."}), 400
  
  petition = petitionProsecutor.query.filter_by(uid=uid).first()
  if not petition:
    return jsonify({"success": False, "message": "Жалоба не найдена."}), 404
  
  if petition.prosecutor != None:
    return jsonify({"success": False, "message": "Вы не можете обрабатывать жалобу в Прокурутуру, которую уже была взята в работу."}), 403
  
  action = data.get('action')
  if not action:
    return jsonify({"success": False, "message": "Действие не было передано, обратитесь в тех. поддержку."}), 400
  
  if action == 'accept':
    petition.status = 'Accepted'
    petition.prosecutor = current_user.id
    replik = {
      'action': 'processing_complaint',
      'text': f"""Уважаемый(ая) { Users.query.get(petition.author).nikname if Users.query.get(petition.author) else guestUsers.query.get(petition.author) }, согласно законодательству штата СА, по факту вашего обращения будет проведена 
      прокурорская проверка, направленная на выявление в действиях (бездействиях) проверяемого субъекта нарушений Конституции 
      и действующих на территории Сан-Андреас нормативно-правовых актов, на установление причин и условий, способствующих 
      выявленным нарушениям законности, а также лиц, виновных в совершении выявленных правонарушений."""
    }
    new_writer = replottoPetitionProsecutor(
      author=current_user.id,
      uid=uid,
      replik=replik
    )
    db.session.add(new_writer)
    
  elif action == 'reject':
    petition.status = 'Rejected'
    petition.prosecutor = current_user.id
    petition.is_archived = True
    replik = {
      'action': 'processing_complaint',
      'text': f"Уважаемый { Users.query.get(petition.author).nikname if Users.query.get(petition.author) else guestUsers.query.get(petition.author) }, согласно правилам подачи заявления в Прокуратуру штата, в удовлетворении заявления отказано.",
      'next': f"Для получения дополнительной информации и причины отказа, пожалуйста, обратитесь к Прокурору {current_user.nikname} через его Discord: {current_user.discordname}."
    }
    
    new_writer = replottoPetitionProsecutor(
      author=current_user.id,
      uid=uid,
      replik=replik
    )
    db.session.add(new_writer)
    
  db.session.commit()
  
  return jsonify({"success": True, "message": "Жалоба была успешно обработана"}), 200

def send_bot_order_notification(uid, link, numworked, articles, defendants):
  message = {
      'uid': uid,
      'link': link, 
      'numworked': numworked, 
      'articles': articles,
      'defendants': defendants
      
  }
  redis_client.publish('new_resolution', json.dumps(message))

@main.route('/violations-prosecutor', methods=['POST'])
@limiter.limit('2 per minute')
def violations_prosecutor():
  from __init__ import petitionProsecutor, db, replottoPetitionProsecutor, Users, guestUsers, claimsStatement, iskdis, isksup
  
  if not current_user.is_authenticated:
    return jsonify({"success": False, "message": "Вы не авторизованы."}), 401
  
  if not current_user.permissions[0].prosecutor:
    return jsonify({"success": False, "message": "У вас нет прав для обработки жалоб в Прокуратуру."}), 403
  
  data = request.get_json()
  uid = data.get('uid')
  
  if not uid:
    return jsonify({"success": False, "message": "UID не был передан, обратитесь в тех. поддержку."}), 400
  
  petition = petitionProsecutor.query.filter_by(uid=uid).first()
  if not petition:
    return jsonify({"success": False, "message": "Жалоба не найдена."}), 404
  
  if current_user.id != petition.prosecutor:
    return jsonify({"success": False, "message": "Вы не можете обрабатывать жалобу в Прокурутуру, которую уже была взята в работу."}), 403
  
  action = data.get('action')
  if not action:
    return jsonify({"success": False, "message": "Действие не было передано, обратитесь в тех. поддержку."}), 400
  
  if action == 'no_violations':
    petition.status = 'CompletedWork'
    petition.is_archived = True
    replik = {
      'action': 'completed_complaint',
      'text': f"""Уважаемый(ая) { Users.query.get(petition.author).nikname if Users.query.get(petition.author) else guestUsers.query.get(petition.author) }, согласно законодательству штата СА, по факту вашего обращения была проведена 
      прокурорская проверка, направленная на выявление в действиях (бездействиях) проверяемого субъекта нарушений Конституции и 
      действующих на территории Сан-Андреас нормативно-правовых актов, на установление причин и условий, способствующих 
      выявленным нарушениям законности, а также лиц, виновных в совершении выявленных правонарушений.""",
      'next': f'По результатам проверки не было выявлено никаких нарушений действующего законодательства Штата СА со стороны {", ".join(str(defendant) for defendant in petition.defendant)}, вследствие чего Прокуратура Штата СА закрывает заявление в прокуратуру по причине отсутствия состава преступления.'
    }
    new_writer = replottoPetitionProsecutor(
      author=current_user.id,
      uid=uid,
      replik=replik
    )
    db.session.add(new_writer)
  
  elif action == 'violations_order':
    link = data.get('link')
    numworked = data.get('numworked')
    articles = data.get('articles')
    
    pattern_link = r"^https:\/\/docs\.google\.com\/document\/.*"
    if not re.match(pattern_link, link):
      return jsonify({"success": False, "message": "Некорректная ссылка. Ссылка должна начинаться с https://docs.google.com/"}), 400
    
    petition.status = 'CompletedWork'
    petition.is_archived = True
    replik = {
      'action': 'completed_complaint',
      'text': f"""Уважаемый(ая) { Users.query.get(petition.author).nikname if Users.query.get(petition.author) else guestUsers.query.get(petition.author) }, согласно законодательству штата СА, по факту вашего обращения была проведена 
      прокурорская проверка, направленная на выявление в действиях (бездействиях) проверяемого субъекта нарушений Конституции и 
      действующих на территории Сан-Андреас нормативно-правовых актов, на установление причин и условий, способствующих 
      выявленным нарушениям законности, а также лиц, виновных в совершении выявленных правонарушений.""",
      'next': f'По результатам проверки было выявлено нарушения действующего законодательства Штата СА со стороны {", ".join(str(defendant) for defendant in petition.defendant)}, вследствие чего будет выписан ордер типа AS.'
    }
    new_writer = replottoPetitionProsecutor(
      author=current_user.id,
      uid=uid,
      replik=replik
    )
    db.session.add(new_writer)
    
    headers = {
    "X-User-ID": str(current_user.id),
    "X-Auth": "True"
    }
    
    for item in petition.defendant:
      parts = item.split()
      payload = {
        "type_doc": "Order",
        "static": parts[-1],
        "nickname": " ".join(parts[:-1]),
        "typeOrder": "AS",
        "adreas_suspect": "",
        "param1": f"{articles}",
        "param2": "6 лет",
        "car_brand": "",
        "param3": "до исполения",
        "param4": f"Прокуратура № {numworked}",
        "custom_button_pressed": False
      }
      try:
        response = requests.post(
            f'{request.host_url}create_doc', json=payload, headers=headers
        )
        if response.status_code != 201:
          return jsonify({"success": False, "message": "Ошибка при создании документа."}), 500
        
      except Exception as e:
        return jsonify({"success": False, "message": f"Ошибка соединения с сервером: {str(e)}"}), 500
    
  elif action == 'violations_district_court':
    link = data.get('link')
    numworked = data.get('numworked')
    articles = data.get('articles')
    
    pattern_link = r"^https:\/\/docs\.google\.com\/document\/.*"
    if not re.match(pattern_link, link):
      return jsonify({"success": False, "message": "Некорректная ссылка. Ссылка должна начинаться с https://docs.google.com/"}), 400
    
    petition.status = 'CompletedWork'
    petition.is_archived = True
    replik = {
      'action': 'completed_complaint',
      'text': f"""Уважаемый(ая) { Users.query.get(petition.author).nikname if Users.query.get(petition.author) else guestUsers.query.get(petition.author) }, согласно законодательству штата СА, по факту вашего обращения была проведена 
      прокурорская проверка, направленная на выявление в действиях (бездействиях) проверяемого субъекта нарушений Конституции и 
      действующих на территории Сан-Андреас нормативно-правовых актов, на установление причин и условий, способствующих 
      выявленным нарушениям законности, а также лиц, виновных в совершении выявленных правонарушений.""",
      'next': f'По результатам проверки было выявлено нарушения действующего законодательства Штата СА со стороны {", ".join(str(defendant) for defendant in petition.defendant)}, вследствие чего дело передается в Окружной Суд Штата Сан-Андреас'
    }
    try:
      new_writer = replottoPetitionProsecutor(
        author=current_user.id,
        uid=uid,
        replik=replik
      )
      db.session.add(new_writer)
      
      claim = claimsStatement()
      db.session.add(claim)
      db.session.flush()  

      district_claim = iskdis(
        current_uid=claim.uid,
        created=current_user.static,
        prosecutor=current_user.id,
        defendant=petition.defendant,
        type_criminal=True,
        link_case=link,
        date_case=petition.timespan,
        status='CompleteWork'
      )
      db.session.add(district_claim)
      db.session.commit()
    
    except Exception as e:
      print(f'Ошибка {str(e)}')
      return jsonify({"success": False, "message": "Ошибка создание ответа, попробуйте позже"}), 500
    
  elif action == 'violations_supreme_court':
    link = data.get('link')
    numworked = data.get('numworked')
    articles = data.get('articles')
    
    pattern_link = r"^https:\/\/docs\.google\.com\/document\/.*"
    if not re.match(pattern_link, link):
      return jsonify({"success": False, "message": "Некорректная ссылка. Ссылка должна начинаться с https://docs.google.com/"}), 400
    
    petition.status = 'CompletedWork'
    petition.is_archived = True
    replik = {
      'action': 'completed_complaint',
      'text': f"""Уважаемый(ая) { Users.query.get(petition.author).nikname if Users.query.get(petition.author) else guestUsers.query.get(petition.author) }, согласно законодательству штата СА, по факту вашего обращения была проведена 
      прокурорская проверка, направленная на выявление в действиях (бездействиях) проверяемого субъекта нарушений Конституции и 
      действующих на территории Сан-Андреас нормативно-правовых актов, на установление причин и условий, способствующих 
      выявленным нарушениям законности, а также лиц, виновных в совершении выявленных правонарушений.""",
      'next': f'По результатам проверки было выявлено нарушения действующего законодательства Штата СА со стороны {", ".join(str(defendant) for defendant in petition.defendant)}, вследствие чего дело передается в Верховный Суд Штата Сан-Андреас'
    }
    try:
      new_writer = replottoPetitionProsecutor(
        author=current_user.id,
        uid=uid,
        replik=replik
      )
      db.session.add(new_writer)
      
      claim = claimsStatement()
      db.session.add(claim)
      db.session.flush()  

      supreme_claim = isksup(
        current_uid=claim.uid,
        created=current_user.static,
        prosecutor=current_user.id,
        defendant=petition.defendant,
        type_criminal=True,
        link_case=link,
        date_case=petition.timespan,
        status='CompleteWork'
      )

      db.session.add(supreme_claim)
      db.session.commit()
    
    except Exception as e:
      print(f'Ошибка {str(e)}')
      return jsonify({"success": False, "message": "Ошибка создание ответа, попробуйте позже"}), 500
    
  return jsonify({"success": True, "message": "Решение по жалобе было успешно создано"}), 201

@main.route('/get-documet-prosecutor-content', methods=['GET'])
@limiter.limit("15 per minute")
def get_prosecution_office_content():
  from __init__ import ResolutionTheUser, OrderTheUser, CustomResolutionTheUser
  is_visibily_attoney = True

  resolutions = ResolutionTheUser.query.filter_by(is_modertation=True).all()
  orders = OrderTheUser.query.filter_by(is_modertation=True).all()
  custom_resolutions = CustomResolutionTheUser.query.filter_by(is_modertation=True).all()
  
  all_documents = []
  for res in resolutions:
      all_documents.append({
          'type': 'Постановление',
          'item': res,
          'date_created': res.date_created,
          'number': res.current_number
      })

  for ord in orders:
      all_documents.append({
          'type': 'Ордер',
          'item': ord,
          'date_created': ord.date_created,
          'number': ord.current_number
      })

  for cust_res in custom_resolutions:
      all_documents.append({
          'type': 'Постановление',
          'item': cust_res,
          'date_created': cust_res.date_created,
          'number': cust_res.current_number
      })
      
  sorted_documents = sorted(all_documents, key=lambda x: x['date_created'], reverse=True)
  
  return render_template(
    'main/main-doc-attomey.html', 
    is_visibily_attoney=is_visibily_attoney, sorted_documents=sorted_documents)