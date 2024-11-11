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
def is_send_allowed(wait_seconds=30):
    """Проверяет, прошло ли достаточно времени с последней отправки и возвращает оставшееся время."""
    last_sent_time = session.get('last_sent_time')
    
    if last_sent_time:
        last_sent_time = datetime.strptime(last_sent_time, '%Y-%m-%d %H:%M:%S')
        remaining_time = (last_sent_time + timedelta(seconds=wait_seconds)) - datetime.now()
        
        if remaining_time.total_seconds() > 0:
            # Вычисляем оставшиеся секунды и выводим сообщение
            seconds_left = int(remaining_time.total_seconds())
            flash(f"Пожалуйста, подождите {seconds_left} секунд перед повторной отправкой.")
            return False

    # Обновляем временную метку, если отправка разрешена
    session['last_sent_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return True

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
    # Устанавливаем шрифт для подписи
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
    color = '#142c77'  # Синий
  elif organ == 'LSCSD':
    color = '#9F4C0F'  # Коричневый
  elif organ == 'SANG':
    color = '#166c0e'  # Зеленый
  elif organ == 'FIB':
    color = '#000000' # черный
  elif organ == 'EMS':
    color = '#a21726' # красный
  elif organ == 'WN':
    color = '#a21726' # красный
  elif organ == 'GOV':
    color = '#CCAC00' # желтый
    
  return color

def read_ranks(filename):
  with open(filename, 'r', encoding='utf-8') as f:
    data = json.load(f)
  return data

def get_rank_info(ranks, organization, rank_level):
  rank_info = None
  if organization in ranks:
    for rank_data in ranks[organization]:
      for level, name in rank_data.items():
        if level.strip("[]") == rank_level:
          rank_info = name.strip()
          break
  return rank_info

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
  print("отправленно")
  redis_client.publish('new_resolution', json.dumps(message))

def send_to_bot_changepass(code, discord_id):
    message = {
        'code': code,
        'discord_id': discord_id
    }
    redis_client.publish('changepass_channel', json.dumps(message))

# создание блюпринта
main = Blueprint('main', __name__)

def check_user_action(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      from __init__ import Users
      if current_user.is_authenticated:
          user = Users.query.get(current_user.id)
          if user and user.action == 'Dismissal':
              logout_user()
              return redirect(url_for('main.index'))
      return f(*args, **kwargs)
    return decorated_function
  
def user_permission_moderation(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from __init__ import Users
        if not current_user.is_authenticated:
            flash('Необходимо войти для доступа к этой странице.')
            return redirect(url_for('main.auth'))

        user = Users.query.get(current_user.id)
        uid = request.args.get('uid')
        rankuser_value = int(user.rankuser) if user.rankuser.isdigit() else 0

        if user.organ == 'GOV' and rankuser_value >= 11 and rankuser_value != 12:
            send_to_bot_permission_none(False)
            return f(*args, **kwargs)

        send_to_bot_permission_none(True)
        flash('У вас нет доступа к модерации постановлений!')
        return redirect(url_for('main.index'))

    return decorated_function
CLIENT_ID = '63202ab8a29f3f1'
def upload_image_to_imgur(image):
    import requests
    headers = {
        'Authorization': f'Client-ID {CLIENT_ID}'
    }
    api_url = 'https://api.imgur.com/3/upload'
    
    response = requests.post(api_url, headers=headers, files={'image': image})
    
    if response.status_code == 200:
        data = response.json()
        return data['data']['link']
    else:
        return None
# главная страница
@main.route('/', methods=['POST', 'GET'])
def index():
  from __init__ import PermissionUsers, Users, db, News
  from form import Formnews
  import time
  form = Formnews()
  city_hallnews = News.query.filter_by(typenews="cityhall").all()
  leadernews = News.query.filter_by(typenews="leaders").all()
  weazelnewsn = News.query.filter_by(typenews="weazel").all()
  has_access = False
  if current_user.is_authenticated:
    cancrnews = current_user.permissions[0]
    if cancrnews:
       has_access = cancrnews is not None
  if 'zagolovok' in request.form:
    last_request_time = session.get('last_request_time', 0)
    current_time = time.time()
    if current_time - last_request_time < 60:
      return jsonify(message=f'Подождите некоторое время до отправки следующей новости!'), 400
    session['last_request_time'] = current_time
    name = form.zagolovok.data
    desc = form.desc.data
    news_type = form.type_news.data
    userperm = current_user.permissions[0]
    user = Users.query.filter_by(static=current_user.static).first()
    if not userperm.create_news:
      return jsonify(message='Отказано в доступе!'), 403
    if news_type == "leaders" and not userperm.admin:
      return jsonify(message='Вы не администратор!'), 400
        
    if news_type == "weazel" and user.organ != "WN":
      return jsonify(message='Вы не сотрудник WN!'), 400
    file = form.img.data
    if file:
      imgur_link = upload_image_to_imgur(file)
      new_new = News(typenews=news_type, created_by=user.nikname, headernews=name, textnews=desc, picture=imgur_link)
    else:
      new_new = News(typenews=news_type, created_by=user.nikname, headernews=name, textnews=desc)
    db.session.add(new_new)
    db.session.commit()
    return jsonify(message='Успешно!'), 200
  if request.method == 'POST':
    data = request.get_json()
    news_id = data.get('id')
    if news_id:
      if not current_user.permissions[0].create_news:
        return jsonify(message='Отказано в доступе!'), 403
      news_item = db.session.query(News).filter_by(id=news_id).first()
      db.session.delete(news_item)
      db.session.commit()
      send_to_bot_log_dump(f'Новость {news_item.typenews} с ID {news_id} удалена', f"Заголовок {news_item.headernews}\nНовость {news_item.textnews}\nКартинка {news_item.picture}\nСоздано {news_item.created_by}\nУдалил {current_user.static}")
      return jsonify(redirect_url=url_for('main.index')), 200
    
  return render_template('index.html', city_hallnews=city_hallnews, leadernews=leadernews, weazelnewsn=weazelnewsn, has_access=has_access, form=form)

@main.route('/iskapplications', methods=['POST', 'GET'])
def iskapplications():
  from __init__ import iskdis, isksup, PermissionUsers, Users, db
  supreme = isksup.query.all()
  district = iskdis.query.all()
  authent = False
  if current_user.is_authenticated:
    authent = True
  if request.method == "POST":
    created = request.form.get('created')
    if not created:
      created = current_user.nikname
    isnt = request.form.get('isnt')
    defenda = request.form.get('defenda')
    descri = request.form.get('descri')
    phonen = request.form.get('phonen')
    cardn = request.form.get('cardn')
    claims = request.form.getlist('claims[]')
    defenda_list = [name.strip() for name in defenda.split(',')] if defenda else []
    if isnt == "district":
      isk = iskdis(discription=descri, claims=claims, phone=phonen, cardn=cardn, created=created, defendant=defenda_list, createdds="1234")
      db.session.add(isk)
      db.session.commit()
    return redirect(url_for('main.iskapplications'))
  return render_template('applic.html', district=district, supreme=supreme, authent=authent)
   
@main.route('/isk', methods=['POST', 'GET'])
def isk():
  from __init__ import iskdis, isksup, PermissionUsers, Users, db, repltoisks
  import time
  id = request.args.get('id')
  type = request.args.get('type')
  status = None
  def othermem(self):
        if self.otherme:
          return '\n'.join([f"{key}: {value}" for key, value in self.otherme.items()])
  if request.method == "POST":
    typeopr = request.form.get("typeopr")
    if typeopr == "prinatie":
      iskuid = session.get('iskuid')
      ids = session.get('id')
      iskt = session.get('type')
      print(f'{ids}{iskt}')
      motivirovka = request.form.get('motivirovkat')
      investigation = request.form.get('investigation')
      print(f'{iskuid} {motivirovka} {investigation}')
      if motivirovka:
        text = {
        "motivirovka": motivirovka,
        "investigation": investigation
        }
      else:
        text = {
        "investigation": investigation
        }
      replto = repltoisks(uid=iskuid, author=current_user.nikname, replyik=text, type_document="acceptisk")
      db.session.add(replto)
      db.session.commit()
      if iskt == "district":
        isktype = iskdis
      elif iskt == "supreme":
        isktype = isksup
      db.session.query(isktype).filter_by(uid=iskuid).update({
        "judge": current_user.nikname
      })
      return redirect(url_for('main.isk', id=ids, type=iskt))
    elif typeopr == "otkaz":
      iskuid = session.get('iskuid')
      ids = session.get('id')
      iskt = session.get('type')
      motivirovka = request.form.get('motivirovkat')
      text = {
         "motivirovka": motivirovka
      }
      replto = repltoisks(uid=iskuid, author=current_user.nikname, replyik=text, type_document="otkazisk")
      db.session.add(replto)
      db.session.commit()
      if iskt == "district":
        isktype = iskdis
      elif iskt == "supreme":
        isktype = isksup
      db.session.query(isktype).filter_by(uid=iskuid).update({
        "judge": current_user.nikname,
        "is_archived": True
      })
      return redirect(url_for('main.isk', id=ids, type=iskt))
    elif typeopr == "prokdelo":
      iskuid = session.get('iskuid')
      ids = session.get('id')
      iskt = session.get('type')
      text = {
        "prok": current_user.nikname
      }
      replto = repltoisks(uid=iskuid, author=current_user.nikname, replyik=text, type_document="prokdelo")
      db.session.add(replto)
      db.session.commit()
      if iskt == "district":
        isktype = iskdis
      elif iskt == "supreme":
        isktype = isksup
      db.session.query(isktype).filter_by(uid=iskuid).update({
        "prosecutor": current_user.nikname
      })
      return redirect(url_for('main.isk', id=ids, type=iskt))
    elif typeopr == "svidetelhod":
      iskuid = session.get('iskuid')
      ids = session.get('id')
      iskt = session.get('type')
      count = db.session.query(repltoisks).filter(repltoisks.type_document == "hodataistvo").count()
      namesvidetela = request.form.get('namesvidetela')
      text = {
        "namesvidetela": namesvidetela,
        "type_hodataistva": "svidetelhod",
        "№_hodataistva": count + 1,
        "accepted": False
      }
      replto = repltoisks(uid=iskuid, author=current_user.nikname, replyik=text, type_document="hodataistvo")
      db.session.add(replto)
      db.session.commit()
       
  if type == "district":
    isk = iskdis.query.filter_by(id=id).first_or_404()
    replies = repltoisks.query.filter_by(uid=isk.uid).all()
    otherme = othermem(isk)
    if current_user.is_authenticated:
      if current_user.nikname == isk.created:
        status = "Created"
      elif current_user.organ == "GOV" and 13 <= int(current_user.rankuser) <= 15:
        status = "Judge"
      elif current_user.organ == "GOV" and int(current_user.rankuser) == 9:
        status = "prosecutor"
      elif current_user.nikname in isk.defendant:
        status = "defendant"
      elif current_user.nikname == isk.lawerc or current_user.nikname == isk.lawerd:
        status = "lawer"
    session['iskuid'] = isk.uid
    session['id'] = id
    session['type'] = type
    return render_template('isk.html', isk=isk, otherme=otherme, status=status, replies=replies)
  elif type == "supreme":
    isk = isksup.query.filter_by(id=id).first_or_404()
    session['iskuid'] = isk.uid
    return render_template('isk.html', isk=isk)
@main.route('/get_news/<int:news_id>', methods=['GET'])
def get_news(news_id):
    from __init__ import news
    news_item = news.query.get_or_404(news_id)
    return jsonify({
        'id': news_item.id,
        'headernews': news_item.headernews,
        'textnews': news_item.textnews,
        'typenews': news_item.typenews,
        'picture': news_item.picture
    })

# Логирование
@main.route('/auth', methods=['POST', 'GET'])
def auth():
  from __init__ import db, Users
  form = FormAuthPush()
  formfp = Formforgetpassword1()
  formfp2 = Formforgetpassword2()

  next_url = request.args.get('next')

  if current_user.is_authenticated:
      return redirect(next_url or url_for('main.profile'))

  if form.validate_on_submit():
    static = Users.query.filter_by(static=form.static.data).first()

    if static:
        if static.action == 'Dismissal':
            logout_user()  # Закрываем сессию логирования
            flash("Отказано в доступе: вы не состоите во фракции.")
            return redirect(url_for('main.auth'))
        
        # Проверяем пароль, если действие не 'Dismissal'
        if check_password_hash(static.password, form.password.data):
            login_user(static)

            next_url = request.args.get('next')
            if next_url:
                return redirect(next_url)
            else:
                  return redirect(url_for('main.profile'))
        else:
              flash("Неверный static или password!")
    else:
          flash("Пользователь не найден!")
    #Забыл пароль(Введите статик)
  if 'staticfp' in request.form:
    def generate_non_repeating_8_digit_number():
      number = [random.randint(1, 9)]
      for _ in range(5):
          number.append(random.choice([d for d in range(10) if d != number[-1]]))
      return int(''.join(map(str, number)))
    from flask import jsonify
    code = generate_non_repeating_8_digit_number()
    staticfp = formfp.staticfp.data
    userfp = Users.query.filter_by(static=staticfp).first()
    if userfp:
      session['codefp'] = code
      session['staticfp'] = staticfp
      send_to_bot_changepass(code, userfp.discordid)
    else:
      return jsonify(message='Пользователь не найден!'), 400
    #Забыл пароль(Введите код)
  if 'codefp' in request.form and 'new_password' in request.form:
    codefp2 = int(formfp2.codefp.data)
    new_password = generate_password_hash(formfp2.new_password.data)
    codefp = session.get('codefp')
    staticfp = session.get('staticfp')
    from flask import jsonify
    if codefp2 == codefp:
      db.session.query(Users).filter_by(static=staticfp).update({
         "password": new_password
      })
      return jsonify(message='Пароль изменен!'), 200
    else:
      session.pop('codefp', None)
      session.pop('staticfp', None)
      return jsonify(redirect_url=url_for('main.index')), 400

  return render_template('auth.html', form=form, formfp=formfp, formfp2=formfp2)

# перенаправление на страницу
@main.after_request
def redirect_login(response):
    if response.status_code == 401:
      if not current_user.is_authenticated:
        return redirect(url_for('main.auth') + '?next=' + request.url)
        
    return response

# Обработка КА функций.
def generate_random_password():
  """Создание пароля"""
  characters = string.ascii_letters + string.digits + string.punctuation
  return ''.join(random.choice(characters) for i in range(10))

def existing_discord_in_multiple_organizations(discord_id, discord_name):
  from __init__ import Users
  """Проверка на 2+ дискорда в Гос. фракции"""
  return (Users.query.filter_by(discordid=discord_id).count() > 1 or 
          Users.query.filter_by(discordname=discord_name).count() > 1)

def send_to_bot_ka(action, static_to, discord_id_from, discord_id_to, curr_rank, prev_rank, nikname_from, nikname_to, reason):
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
      'reason': reason
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

def process_invite_action(user, form, reason, discord_id, static):
  from __init__ import db, ActionUsers
  """Обрабатывает Инвайт если пользователя есть в БД"""
  password = generate_random_password()
  hash_password = generate_password_hash(password)

  try:
    try:
      user.password = hash_password
      user.prev_rank = 0
      user.curr_rank = 1
      user.action = 'Invite'
      user.organ = current_user.organ
      user.nikname = form.nikname.data
      db.session.commit()

    except SQLAlchemyError as e:
      db.session.rollback()
      flash('Произошла ошибка при сохранении данных. Попробуйте снова.', 'error')
      logging.error(f"Ошибка сохранения в базе данных (Users): {str(e)}")
      
    try:
      new_action = ActionUsers(
        discordid = discord_id,
        discordname = user.discordname,
        static = static,
        nikname = form.nikname.data,
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

  except SQLAlchemyError as e:
    db.session.rollback()
    logging.error(f"Ошибка обработки: {str(e)}")     

  else:
    send_to_bot_ka('Invite', static, current_user.discordid, discord_id, user.curr_rank, user.prev_rank, current_user.nikname, form.nikname.data, reason)
    send_to_bot_invite(password, discord_id, static, user.organ)
    flash('Пользователь успешно добавлен!', 'success')
    logging.info('Пользователь был успешно добавлен в бд Users.')

  if int(form.rank.data) > 1:
    process_raise(user, form, reason)
    return redirect(url_for('main.audit'))

def process_new_invite(static, discord_id, discord_name, form, reason):
  from __init__ import db, Users, ActionUsers, PermissionUsers, get_next_id_user, get_next_id_permission
  """Обрабатывает Инвайт если пользователя нет в БД"""
  if existing_discord_in_multiple_organizations(discord_id, discord_name):
    flash('Данный дискорд уже состоит в 2-ух гос. структурах!', 'error')
    return

  password = generate_random_password()
  hash_password = generate_password_hash(password)
  
  try:
    try:
      new_user = Users(
        id=get_next_id_user(),
        discordid=discord_id,
        discordname=discord_name,
        static=static,
        nikname=form.nikname.data,
        action='Invite',
        organ=current_user.organ,
        prev_rank=0,
        curr_rank=1,
        password=hash_password
      )
      db.session.add(new_user)
      db.session.commit()

    except SQLAlchemyError as e:
      db.session.rollback()
      flash('Произошла ошибка при сохранении данных. Попробуйте снова.', 'error')
      logging.error(f"Ошибка сохранения в базе данных (Users): {str(e)}")

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
      
    try:
      new_action = ActionUsers(
        discordid = discord_id,
        discordname = discord_name,
        static = static,
        nikname = form.nikname.data,
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

  except SQLAlchemyError as e:
    db.session.rollback()
    logging.error(f"Ошибка обработки: {str(e)}")

  else:
    send_to_bot_ka('Invite', static, current_user.discordid, discord_id, user.curr_rank, user.prev_rank, current_user.nikname, form.nikname.data, reason)
    send_to_bot_invite(password, discord_id, static, user.organ)
    flash('Пользователь успешно добавлен!', 'success')
    logging.info('Пользователь был успешно добавлен в бд Users.')

  if int(form.rank.data) > 1:
    process_raise(user, form, reason)
    return redirect(url_for('main.audit'))


def process_dismissal(user, form, reason):
  from __init__ import db, ActionUsers
  """Обрабатывает увольнение пользователя."""

  permission_current = current_user.permissions[0]
  permission_user = user.permissions[0]
  if permission_user and (permission_user.admin or permission_user.tech) \
    and permission_current and (not permission_current.admin or not permission_current.tech):
    flash('Вы не можете уволить админа/разработчика.')
    return redirect(url_for('main.audit'))
  
  if current_user.organ != user.organ:
    flash('Вы не можете уволить игрока другой фракции.')   
    return redirect(url_for('main.audit'))
  
  if current_user.curr_rank < user.curr_rank:
    flash('Вы не можете уволить игрока, если вы ниже рангом.')
    return redirect(url_for('main.audit'))
  
  if user.action == 'Dismissal':
    flash('Игрок уже был уволен.')
    return redirect(url_for('main.audit'))

  try:
    try:
      user.action = 'Dismissal'
      user.prev_rank = user.curr_rank
      user.curr_rank = 0
      db.session.commit()
    
    except SQLAlchemyError as e:
      db.session.rollback()
      flash('Произошла ошибка при сохранении данных. Попробуйте снова.', 'error')
      logging.error(f"Ошибка сохранения в базе данных (Users): {str(e)}")

    try:
      permission_user.tech = False
      permission_user.admin = False
      permission_user.lider = False
      permission_user.high_staff = False
      permission_user.creation_doc = False
      db.session.commit()
    
    except SQLAlchemyError as e:
      db.session.rollback()
      logging.error(f"Ошибка сохранения в базе данных (PermissionUsers): {str(e)}")   

    try:
      new_action = ActionUsers(
        discordid = user.discordid,
        discordname = user.discordname,
        static = form.static.data,
        nikname = form.nikname.data,
        action = 'Dismissal',
        curr_rank = user.curr_rank,
        prev_rank = user.prev_rank,
        author_id = current_user.id
      )
      db.session.add(new_action)
      db.session.commit()

    except SQLAlchemyError as e:
      db.session.rollback()
      logging.error(f"Ошибка сохранения в базе данных (ActionUsers): {str(e)}")    

  except SQLAlchemyError as e:
    db.session.rollback()
    logging.error(f"Ошибка обработки: {str(e)}")    

  else:
    send_to_bot_dismissal(user.discordid, user.static, user.organ)
    send_to_bot_ka('Dismissal', form.static.data, current_user.discordid, user.discordid, user.curr_rank, user.prev_rank, current_user.nikname, form.nikname.data, reason)
    flash('Пользователь успешно уволен!', 'success')
    logging.info('Пользователь был успешно обновлен в бд Users.')


def process_raise(user, form, reason):
  from __init__ import db, ActionUsers
  """Обрабатывает повышение пользователя."""
  new_rank = form.rank.data

  permission_current = current_user.permissions[0]
  permission_user = user.permissions[0]
  if permission_user and (permission_user.admin or permission_user.tech) \
    and permission_current and (not permission_current.admin or not permission_current.tech):
    flash('Вы не можете повысить админа/разработчика.')
    return redirect(url_for('main.audit'))
  
  if current_user.organ != user.organ:
    flash('Вы не можете повысить игрока другой фракции.')   
    return redirect(url_for('main.audit'))
  
  if current_user.curr_rank <= user.curr_rank:
    flash('Вы не можете повысить игрока, если вы ниже или таким же рангом.')
    return redirect(url_for('main.audit'))
  
  if user.action == 'Dismissal':
    flash('Игрок не находится во фракции.')
    return redirect(url_for('main.audit'))
  
  if user.curr_rank >= int(new_rank):
    flash('Вы не можете повысить на текущий/ниже ранг')
    return redirect(url_for('main.audit'))

  try:
    try:
      user.action = 'Raising'
      user.prev_rank = user.curr_rank
      user.curr_rank = new_rank
      db.session.commit()

    except SQLAlchemyError as e:
      db.session.rollback()
      flash('Произошла ошибка при сохранении данных. Попробуйте снова.', 'error')
      logging.error(f"Ошибка сохранения в базе данных (Users): {str(e)}")
    
    try:
      new_action = ActionUsers(
        discordid = user.discordid,
        discordname = user.discordname,
        static = form.static.data,
        nikname = form.nikname.data,
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

  except SQLAlchemyError as e:
    db.session.rollback()
    logging.error(f"Ошибка обработки: {str(e)}")    
 
  else:
    send_to_bot_ka('Raising', form.static.data, current_user.discordid, user.discordid, user.curr_rank, user.prev_rank, current_user.nikname, form.nikname.data, reason)
    flash('Пользователь успешно повышен!', 'success')
    logging.info('Пользователь был успешно обновлен в бд Users.')


def process_demotion(user, form, reason):
  from __init__ import db, ActionUsers
  """Обрабатывает понижение пользователя."""
  new_rank = form.rank.data

  permission_current = current_user.permissions[0]
  permission_user = user.permissions[0]
  if permission_user and (permission_user.admin or permission_user.tech) \
    and permission_current and (not permission_current.admin or not permission_current.tech):
    flash('Вы не можете понизить админа/разработчика.')
    return redirect(url_for('main.audit'))
  
  if current_user.organ != user.organ:
    flash('Вы не можете понизить игрока другой фракции.')   
    return redirect(url_for('main.audit'))
  
  if current_user.curr_rank <= user.curr_rank:
    flash('Вы не можете понизить игрока, если вы ниже или таким же рангом.')
    return redirect(url_for('main.audit'))
  
  if user.action == 'Dismissal':
    flash('Игрок не находится во фракции.')
    return redirect(url_for('main.audit'))
  
  if user.curr_rank <= int(new_rank):
    flash('Вы не можете понизить на текущий/выше ранг')
    return redirect(url_for('main.audit'))
  
  try:
    try:
      user.action = 'Demotion'
      user.prev_rank = user.curr_rank
      user.curr_rank = new_rank
      db.session.commit()
    
    except SQLAlchemyError as e:
      db.session.rollback()
      flash('Произошла ошибка при сохранении данных. Попробуйте снова.', 'error')
      logging.error(f"Ошибка сохранения в базе данных (Users): {str(e)}")
    
    try:
      new_action = ActionUsers(
        discordid = user.discordid,
        discordname = user.discordname,
        static = form.static.data,
        nikname = form.nikname.data,
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

  except SQLAlchemyError as e:
    db.session.rollback()
    logging.error(f"Ошибка обработки: {str(e)}")  

  else:
    send_to_bot_ka('Demotion', form.static.data, current_user.discordid, user.discordid, user.curr_rank, user.prev_rank, current_user.nikname, form.nikname.data, reason)
    flash('Пользователь успешно понизили!', 'success')
    logging.info('Пользователь был успешно обновлен в бд Users.')

  if user.curr_rank == 0:
    process_dismissal(user, form, reason)
    return redirect(url_for('main.audit'))


# Кадровый аудит
@main.route('/audit', methods=['POST', 'GET'])
@check_user_action
@login_required
def audit():
  from __init__ import db, Users
  form = FormAuditPush()  
  
  permission = current_user.permissions[0]
  if not (permission.high_staff or permission.lider or permission.admin or permission.tech):
    flash("Доступ запрещен, отсутствуют права.")
    return redirect(url_for('main.profile'))
  
  action_users = current_user.action_log

  organ = current_user.organ
  nikname = current_user.nikname
  color = color_organ(organ)

  if form.validate_on_submit():
    static = form.static.data
    action = form.action.data
    discord_name = form.discordName.data
    discord_id = form.discordID.data
    reason = form.reason.data

    user = Users.query.filter_by(static=static).first()
    if static == current_user.static:
      flash('Нельзя проводить действия над собой')
      return redirect(url_for('main.audit'))

    if action == 'Invite':
      if user and user.action == 'Dismissal':
          process_invite_action(user, form, reason, discord_id, static)
      elif user is None:
          process_new_invite(static, discord_id, discord_name, form, reason)
      else:
          flash('Такой статик уже имеется во госс. фракции!')
          return redirect(url_for('main.audit'))

    else:
      if not user or user.action == 'Dismissal':
        flash('Такого статика не существует во фракции!')
        return redirect(url_for('main.audit'))
      
      if action == 'Dismissal':
        process_dismissal(user, form, reason)
      elif action == 'Raising':
        process_raise(user, form, reason)
      elif action == 'Demotion':
        process_demotion(user, form, reason)

    return redirect(url_for('main.audit'))
  return render_template('ka.html', form=form, organ=organ, color=color, nikname=nikname, action_users=action_users, current_user=current_user)

# выход с профиля 
@main.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
  logout_user()
  return redirect(url_for('main.index'))

# профиль
@main.route('/profile', methods=['GET', 'POST'])
@check_user_action
@login_required
def profile():
  from __init__ import Users, db
  from flask import jsonify
  nickname = current_user.nikname
  organ = current_user.organ
  rank = current_user.curr_rank
  color = color_organ(organ)
  form = Formchangepassword()
  if 'oldpass' in request.form and 'newpass' in request.form:
    usercp = db.session.query(Users).filter_by(nikname=nickname, organ=organ).first()
    old_password = form.oldpass.data
    new_password = form.newpass.data
    if old_password == new_password:
      return jsonify(message='Новый пароль не может быть старым!'), 400
    stored_password_hash = usercp.password
    if check_password_hash(stored_password_hash, old_password):
      new_password_hash = generate_password_hash(new_password)
      db.session.query(Users).filter_by(nikname=nickname, organ=organ).update({
          "password": new_password_hash
        })
      db.session.commit()
      #send_to_bot_changepass(new_password, usercp.discordid, usercp.static)
      return jsonify(message='Пароль успешно изменен!'), 200
    else:
       return jsonify(message='Вы ввели неверный старый пароль!'), 400
  pass
  filename = "./python/name-ranks.json"
  ranks = read_ranks(filename)
  rank_name = get_rank_info(ranks, organ, rank)
  YW = current_user.YW
  SW = current_user.SW
      
  return render_template('profile.html', nickname=nickname, organ=organ, rank=rank, rank_name=rank_name, color=color, YW=YW, SW=SW, form=form)

@main.route('/doc')
def doc():
  if not current_user.is_authenticated:
    flash('Вам необходимо находиться в государственной структуре и быть залогированным на сайте, чтобы создавать документации!')
    return render_template('doc.html', is_permission=False, is_authenticated=False)

  perm_user = current_user.permissions[0]
  if not perm_user: 
    flash('У вас отстутсвуют права для создания документации!')
    return render_template('doc.html', is_permission=False, is_authenticated=True)
  if not (perm_user.creation_doc or perm_user.lider or perm_user.tech): 
    flash('У вас отстутсвуют права для создания документации!')
    return render_template('doc.html', is_permission=False, is_authenticated=True)

  from form import FormCreateDoc, FormCreateResolution, FormCreateOrder

  form = FormCreateDoc()
  formResolution = FormCreateResolution()
  formOrder = FormCreateOrder()
  
  nickname = current_user.nikname
  organ = current_user.organ
  color = color_organ(organ)

  return render_template('doc.html', is_permission=True, is_authenticated=True, form=form, formResolution=formResolution, formOrder=formOrder, nickname=nickname, organ=organ, color=color)
  
@main.route('/create_doc',  methods=['POST', 'GET'])
def create_doc():
  from __init__ import Users, PDFDocument, ResolutionTheUser, OrderTheUser, db, ResolutionNumberCounter
  from form import FormCreateDoc, FormCreateResolution, FormCreateOrder
  form = FormCreateDoc()
  formResolution = FormCreateResolution()
  formOrder = FormCreateOrder()

  if not is_send_allowed():
    return redirect(url_for('main.doc'))

  if not current_user.is_authenticated:
    flash('Для создания постановления требуется войти в аккаунт!')
    return redirect(url_for('main.doc'))

  perm_user = current_user.permissions[0]
  rankuser_value = current_user.curr_rank
  if not (current_user.organ == 'GOV' and (rankuser_value == 10 or rankuser_value == 11 or rankuser_value >= 18)):
    flash('Для создания постановлений требуется уровень доступа, прокурор!')
    return redirect(url_for('main.doc'))
    
  elif not (perm_user.creation_doc or perm_user.admin or perm_user.tech):
    flash('Для создания постановлений требуется разрешение!')
    return redirect(url_for('main.doc'))
    
  if request.method == 'POST':
    custom_button_pressed = formResolution.custom_button_pressed.data
    print(custom_button_pressed)
    typeDoc = form.type_doc.data
    nickname = form.nickname.data
    static = form.static.data

    if static == '':
      flash('Неверный формат. Поле статик не может быть пустым!')
      return redirect(url_for('main.doc'))
 
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
            flash("Неверный формат. Неверно заполнены пункты в ордере.")
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

      # Получение номера документа
      record = ResolutionNumberCounter.increment(db.session)
      new_resolution_number = increment_number_with_leading_zeros(record)
      draw_text(pdf, 150, 200, f"Дата: {datetime.now().strftime('%d.%m.%Y')}")
      draw_text(pdf, 30, 200, f"Doc. No: {new_resolution_number}")
      
      # Стартовая координата y
      y = 190

      # Динамическое заполнение по типу ордера
      if formOrder.type_order.data == 'AS' or formOrder.type_order.data == 'Arrest and Search':
        create_order_header(pdf, "UNITED STATES DEPARTMENT OF JUSTICE", "прокуратура штата Сан-Андреас", 'Arrest and Search')
        str_typeOrder = 'Arrest and Search'
        offwork = formOrder.param4.data
        time = formOrder.param3.data
        articlesAccusation = formOrder.param1.data
        termImprisonment = formOrder.param2.data

        if not all([offwork, time, articlesAccusation, termImprisonment]):
           flash('Неверный формат. Вы заполнили не все поля')
           return redirect(url_for('main.doc'))

        details = [
            "1. Цель. Проведение процедуры законного задержания гражданина штата Сан-Андреас, "
            f"{nickname if nickname != '' else ''}, с номером паспорта {static}, с последующим заключением в Федеральной "
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

      elif formOrder.type_order.data == 'RI' or formOrder.type_order.data == 'Removal of Immunity':
        create_order_header(pdf, "UNITED STATES DEPARTMENT OF JUSTICE", "прокуратура штата Сан-Андреас", 'Removal of Immunity')
        str_typeOrder = 'Removal of Immunity'
        applicationNum = formOrder.application_num.data
        degreeRI = formOrder.degree_ri.data
        time = formOrder.param3.data

        if not all([applicationNum, degreeRI, time]):
          flash('Неверный формат. Вы заполнили не все поля')
          return redirect(url_for('main.doc'))
        
        document_string = applicationNum
        basis_type, basis_number = get_basis_for_immunity_removal(document_string)

        if not basis_type or not basis_number:
          return redirect(url_for('main.doc'))

        if basis_type == "Иск":
          basis_text = f"исковым заявлением № {basis_number}"
        else:
          basis_text = f"заявлением в прокуратуру № {basis_number}"
      
        if degreeRI == 'частично':
          details = [
              f"1. Цель. Частичное снятие статуса неприкосновенности у гражданина {nickname if nickname != '' else ''}, паспортные "
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
              f"1. Цель. Полное снятие статуса неприкосновенности с гражданина {nickname if nickname != '' else ''}, паспортные данные "
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
          flash("Неверный формат. Такой степени снятия неприкосновености не существует, проверьте правописание")
          return redirect(url_for('main.doc'))
        
        y = add_order_details(pdf, details, y * mm)
      
      elif formOrder.type_order.data == 'AR' or formOrder.type_order.data == 'Access To Raid':
        create_order_header(pdf, "UNITED STATES DEPARTMENT OF JUSTICE", "прокуратура штата Сан-Андреас", 'Access To Raid')
        str_typeOrder = 'Access To Raid'
        nameCrimeOrgam = formOrder.name_organ_for_order.data
        adreasCrimeOrgan = formOrder.adreas_organ_for_order.data
        offwork = formOrder.param4.data
        time = formOrder.param3.data
        articlesAccusation = formOrder.param1.data

        if not all([nameCrimeOrgam, adreasCrimeOrgan, offwork, time, articlesAccusation, static]):
           flash('Неверный формат. Вы заполнили не все поля')
           return redirect(url_for('main.doc'))
        
        details = [
          "1. Цель: Прекращение преступной деятельности граждан, выявление и задержание лиц, "
          "нарушающих законодательство штата Сан-Андреас.", 

          f"2. Пояснение к цели: Разрешено проведение рейда на территории {nameCrimeOrgam} "
          f"расположенного по адресу: Сан-Андреас, {adreasCrimeOrgan}. Цель мероприятия, провести "
          "обыск сотрудников и транспортных средств, находящихся на прилегающей территории, а "
          "также осуществить задержание и допрос предполагаемого владельца автомастерской, "
          f"{nickname if nickname != '' else ''} с паспортными данными {static}.",
        
          f"Основания для ордера: Ордер выдан на основании делопроизводства {offwork}, при "
          "наличии следующих нарушений в соответствии с Уголовным кодексом штата Сан-Андреас:                              "
          f"{articlesAccusation}", 

          f"Срок действия ордера: Ордер действителен {time} всех указанных целей и задач."
        ]
        y = add_order_details(pdf, details, y * mm)

      elif formOrder.type_order.data == 'SA' or formOrder.type_order.data == 'Search Access':
        create_order_header(pdf, "UNITED STATES DEPARTMENT OF JUSTICE", "прокуратура штата Сан-Андреас", 'Search Access')
        str_typeOrder = 'Search Access'
        adreasSuspect = formOrder.adreas_suspect.data
        carBrand = formOrder.car_brand.data
        articlesAccusation = formOrder.param1.data
        time = formOrder.param3.data

        if not all([adreasSuspect, carBrand, articlesAccusation, time]):
          flash('Неверный формат. Вы заполнили не все поля')
          return redirect(url_for('main.doc'))
        
        details = [
          "1. Цель: Проведение обыска имущества и транспортных средств, связанных с подозреваемыми в"
          "преступной деятельности, в целях сбора доказательств и пресечения правонарушений.", 

          "2. Пояснение к цели: Разрешено проведение обыска на территории объектов, находящихся в собственности или в "
          f"распоряжении подозреваемого, {nickname if nickname != '' else ''} с паспортными данными {static}, "
          "включая все здания, помещения, транспортные средства и прилегающую территорию. "
          f"Объекты, подлежащие обыску, включают: адрес(a) жилого(ых) помещения(ий) {adreasSuspect} "
          f"марска т\с: {carBrand}", 
          
          "3. Основания для обыска: Обыск проводится, в соответсивии с подозрениями в совершение " 
          f"правонарушений по статьям: {articlesAccusation}", 

          f"4. Настоящий ордер действителен {time} обысковых мероприятий и сбора доказательств, необходимых для "
          "достижения целей расследования."
        ]
        y = add_order_details(pdf, details, y * mm)
      
      elif formOrder.type_order.data == 'FW' or formOrder.type_order.data == 'Federal Wanted':
        create_order_header(pdf, "UNITED STATES DEPARTMENT OF JUSTICE", "прокуратура штата Сан-Андреас", 'Federal Wanted')
        str_typeOrder = 'Federal Wanted'
        articlesAccusation = formOrder.param1.data
        time = formOrder.param3.data
        offwork = formOrder.param4.data

        if not all([articlesAccusation, time, offwork]):
          flash('Неверный формат. Вы заполнили не все поля')
          return redirect(url_for('main.doc'))
        
        details = [
          f"1. Цель: Объявление в розыск и задержание гражданина {nickname if nickname != '' else ''} с паспортынми данными {static}, "
          f"подозреваемого в совершении преступлений, с целью пресечения его противоправной деятельности и "
          "обеспечения его явки для проведения следственных и процессуальных действий.",

          "2. Пояснение к цели: Данный ордер выдается для организации оперативно-розыскных мероприятий "
          f"c целью установления местонахождения гражданина {nickname if nickname != '' else ''}, с паспортынми данными {static} "
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
        flash('Такого ордера не существует, проверьте правильность написания!')
        return redirect(url_for('main.doc'))

      # Сохранение и запись PDF
      pdf.showPage()
      pdf.save()
      buffer.seek(0)

      uid = ''.join([str(random.randint(0, 9)) for _ in range(26)])
      file_path = os.path.join('static', 'uploads', f'{uid}.pdf')
      with open(file_path, 'wb') as f:
        f.write(buffer.getvalue())

      # Создание и сохранение документа в базе данных
      # Создание и добавление записи в PDFDocument
      pdf_document = PDFDocument(
        author_id=current_user.id,
        uid=uid,
        content=file_path
      )
      db.session.add(pdf_document)
      db.session.commit() 

      send_to_bot_new_resolution(
          uid=uid, 
          nickname=current_user.nikname, 
          static=current_user.static, 
          discordid=current_user.discordid, 
          status='moder', 
          number_resolution=new_resolution_number
      )

      user = Users.query.filter_by(static=static).first()
      new_order = OrderTheUser(
          current_uid=uid,  
          author_id=current_user.id,
          nickname_accused=nickname,
          static_accused=static,
          discord_accused=user.discordid if user else None,
          type_order=str_typeOrder,
          time=formOrder.param3.data if formOrder.param3.data != '' else None,
          articlesAccusation=formOrder.param1.data if formOrder.param1.data != '' else None,
          termImprisonment=formOrder.param2.data if formOrder.param2.data != '' else None,
          offWork=formOrder.param4.data if formOrder.param4.data != '' else None,
      )

      db.session.add(new_order)
      db.session.commit()
    
    elif typeDoc == 'Resolution' and custom_button_pressed == 'false':
      if not any([formResolution.param1.data, formResolution.param2.data, formResolution.param3.data, formResolution.param4.data, formResolution.param5.data, formResolution.param6.data]):
        flash('При создании постановленмя должен быть выбран хотя бы один пунк!')
        return redirect(url_for('main.doc'))
      
      user = Users.query.filter_by(static=static).first()

      def generate_resolution_pdf(formResolution, user, current_user, static, nickname):
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

        record = ResolutionNumberCounter.increment(db.session)
        new_resolution_number = increment_number_with_leading_zeros(record)
        draw_text(pdf, 150, 200, f"Дата: {datetime.now().strftime('%d.%m.%Y')}")
        draw_text(pdf, 30, 200, f"Doc. No: {new_resolution_number}")

        draw_text(pdf, 15, 190, f"Я, {current_user.nikname}, являюсь Прокурором штата San Andreas, пользуясь правами, данными мне Конституцией")
        draw_text(pdf, 15, 185, "и законодательством штата San Andreas, а также иными нормативно-правовыми актами,")
        draw_text(pdf, 15, 180, "в связи с необходимостью обеспечения законности и правопорядка в рамках своих полномочий,")
        draw_text(pdf, 80, 170, "ПОСТАНОВЛЯЮ:")

        y = 160
        num = 1
        if formResolution.param1.data:
          text = (f"{num}. Возбудить уголовное дело в отношении {'сотрудника ' + user.organ if user else 'гражданина'} "
                  f"{nickname if nickname != '' else ''}, с номером паспортные данные {static}. Присвоить делу идентификатор {formResolution.case.data} и принять его к производству прокуратурой штата.")
          y = draw_multiline_text(pdf, text, 15, y)
          y -= 5
          num += 1

        if formResolution.param2.data:
          text = (f"{num}. Обязать {'сотрудника ' + user.organ if user else 'гражданина'} {nickname if nickname != '' else ''}, с номером паспортные данные {static}, "
                  f"в течение 24 часов предоставить на почту Прокурора {current_user.nikname} ({current_user.discordname}@gov.sa) видеозапись процессуальных действий, проведённых в отношении {formResolution.param2_nickname.data}, время провдение ареста {formResolution.arrest_time.data}. "
                  f"Запись должна содержать момент ареста {formResolution.arrest_time.data} и фиксировать предполагаемое нарушение.")
          y = draw_multiline_text(pdf, text, 15, y)
          y -= 5
          num += 1

        if formResolution.param3.data:
          text = (f"{num}. Предоставить личное дело {'сотрудника ' + user.organ if user else 'гражданина'} {nickname if nickname != '' else ''}, "
                  f"с номером паспортные данные {static}, включающее электронную почту, должность. Срок предоставления информации — 24 часа.")
          y = draw_multiline_text(pdf, text, 15, y)
          y -= 5
          num += 1

        if formResolution.param4.data:
          text = f"{num}. Ввести запрет на смену персональных данных {'сотрудника ' + user.organ if user else 'гражданина'} {nickname if nickname != '' else ''}, с номером паспортные данные {static}."
          y = draw_multiline_text(pdf, text, 15, y)
          y -= 5
          num += 1

        if formResolution.param5.data and user and user.action != 'Dismissal':
          text = (f"{num}. Ввести запрет на увольнение сотрудника {user.organ} {nickname if nickname != '' else ''} с номером паспортные данные {static} "
                  f"и на перевод в другие государственные структуры на период расследования по делу с идентификатором {formResolution.case.data}.")
          y = draw_multiline_text(pdf, text, 15, y)
          y -= 5
          num += 1

        if formResolution.param6.data and user and user.action != 'Dismissal':
          text = f"{num}. Временно отстранить сотрудника {user.organ} {nickname}, с номером паспортные данные {static}, от исполнения служебных обязанностей на время расследования по делу с идентификатором {formResolution.case.data}."
          y = draw_multiline_text(pdf, text, 15, y)
          y -= 5
          num += 1

        sing_font_path = os.path.join('static', 'fonts', 'Updock-Regular.ttf') 
        pdfmetrics.registerFont(TTFont('Updock', sing_font_path))

        # Генерация подписи
        generate_signature(pdf, y, current_user, 'resolution', page=1)
        y -= 5

        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        
        # Saving PDF and database operations here
        return buffer, new_resolution_number

      # Usage in main logic
      buffer, num_resolution = generate_resolution_pdf(formResolution, user, current_user, static, nickname)
      
      uid = ''.join([str(random.randint(0, 9)) for _ in range(26)])
      session['uid'] = uid
      
      file_path = os.path.join('static', 'uploads', f'{uid}.pdf')
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
        initiation_case=formResolution.param1.data,
        provide_video=formResolution.param2.data,
        provide_personal_file=formResolution.param3.data,
        changing_personal_data=formResolution.param4.data,
        dismissal_employee=formResolution.param5.data,
        temporarily_suspend=formResolution.param6.data,
        victim_nickname=formResolution.param2_nickname.data if formResolution.param2_nickname.data != '' else '', 
        time_arrest=formResolution.arrest_time.data if formResolution.arrest_time.data != '' else '',
        number_case=formResolution.case.data if formResolution.case.data != '' else ''
        )
        
      db.session.add(new_resolution)
      db.session.commit()

    elif typeDoc == 'Resolution' and custom_button_pressed:
      custom_text_fields = [request.form[key] for key in request.form if key.startswith('custom_text_')]
      print(custom_text_fields)

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
        flash('Должно быть заполнено хотя бы одно кастомное поле.')
        return redirect(url_for('main.doc'))
      
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

      record = ResolutionNumberCounter.increment(db.session)
      new_resolution_number = increment_number_with_leading_zeros(record)
      draw_text(pdf, 150, 200, f"Дата: {datetime.now().strftime('%d.%m.%Y')}")
      draw_text(pdf, 30, 200, f"Doc. No: {new_resolution_number}")

      draw_text(pdf, 15, 190, f"Я, {current_user.nikname}, являюсь Прокурором штата San Andreas, пользуясь правами, данными мне Конституцией")
      draw_text(pdf, 15, 185, "и законодательством штата San Andreas, а также иными нормативно-правовыми актами,")
      draw_text(pdf, 15, 180, "в связи с необходимостью обеспечения законности и правопорядка в рамках своих полномочий,")
      draw_text(pdf, 80, 170, "ПОСТАНОВЛЯЮ:")

      y, last_page = add_order_details(pdf, custom_text_fields, 160 * mm)
      generate_signature(pdf, y, current_user, 'resolution', page=last_page)

      pdf.showPage()
      pdf.save()
      buffer.seek(0)

      uid = ''.join([str(random.randint(0, 9)) for _ in range(26)])
      session['uid'] = uid
      
      file_path = os.path.join('static', 'uploads', f'{uid}.pdf')
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
        custom_fields=custom_fields_json
      )
      db.session.add(resolution)
      db.session.commit()

      status = 'moder'
      send_to_bot_new_resolution(uid=uid, nickname=current_user.nikname, static=current_user.static, discordid=current_user.discordid, status=status, number_resolution=new_resolution_number)
    
    else:
      flash('Неверный формат. Вы должны выбрать какой нибуть тип документации!')
      return redirect(url_for('main.doc'))
    
  return redirect(url_for('main.doc'))

@main.route('/resolution', methods=['POST', 'GET'])
def resolution():
    from __init__ import PDFDocument, ResolutionTheUser, OrderTheUser, Users, CustomResolutionTheUser, db
    from form import FormModerationResolution

    # Получаем UID и проверяем наличие /moderation
    uid = request.args.get('uid')
    if not uid:
      return "No UID provided", 400

    uid_parts = uid.split('/')
    base_uid = uid_parts[0]
    is_moderation_link = len(uid_parts) > 1 and uid_parts[1] == 'moderation'

    # Получаем PDF и проверяем его наличие
    pdf_doc = PDFDocument.query.filter_by(uid=base_uid).first()
    if not pdf_doc or not os.path.exists(pdf_doc.content):
      text_error = "PDF not found or invalid UID"
      return render_template('api/404.html', text_error=text_error)

    # Получаем записи для модерации и проверяем их
    moder_resolution = ResolutionTheUser.query.filter_by(current_uid=base_uid).first()
    moder_order = OrderTheUser.query.filter_by(current_uid=base_uid).first()
    moder_custom_resolution = CustomResolutionTheUser.query.filter_by(current_uid=base_uid).first()
    if not moder_resolution and not moder_order and not moder_custom_resolution:
      return "Moderation records not found", 404

    form = FormModerationResolution()

    # Проверка на статус модерации
    if moder_order and moder_order.is_modertation:
      return render_template('preview_resolution.html', pdf_path=pdf_doc.content, uid=uid)

    if moder_resolution and moder_resolution.is_modertation:
      return render_template('preview_resolution.html', pdf_path=pdf_doc.content, uid=uid)
    
    if moder_custom_resolution and moder_custom_resolution.is_modertation:
       return render_template('preview_resolution.html', pdf_path=pdf_doc.content, uid=uid)

    if is_moderation_link:
        if not current_user.is_authenticated:
          flash('Для модерации постановлений требуется войти в аккаунт!')
          send_to_bot_permission_none(True)
          return redirect(url_for('main.index'))

        if not current_user:
          flash('User not found!')
          return redirect(url_for('main.index'))

        rankuser_value = current_user.curr_rank

        def handle_moderation(moder_obj, min_rank, is_order, is_resolution, template_name):
            if current_user.organ == 'GOV' and min_rank <= rankuser_value != 12:
                send_to_bot_permission_none(False)

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

            flash('У вас отсутствуют права на модерацию постановлений!')
            send_to_bot_permission_none(True)
            return redirect(url_for('main.index'))

        if moder_resolution and rankuser_value >= 11:
          return handle_moderation(moder_resolution, 11, is_order=False, is_resolution=True, template_name='temporary_page.html')
        elif moder_order and rankuser_value >= 18:
          return handle_moderation(moder_order, 18, is_order=True, is_resolution=False, template_name='temporary_page.html')
        elif moder_custom_resolution and rankuser_value >= 11:
           return handle_moderation(moder_custom_resolution, 11, is_order=False, is_resolution=True, template_name='temporary_page.html')

    # Если is_moderation=False, и отсутствует доступ к /moderation
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
        
        pdf_doc = PDFDocument.query.filter_by(user_static=current_user.static, uid=uid).first()

        if not pdf_doc:
          flash('Вы не можете редактировать это постановление!')
          return redirect(url_for('main.index')) 
      
        return f(*args, **kwargs)

    return decorated_function

@main.route('/edit_doc')
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
def edit_resolution():
  from __init__ import ResolutionTheUser, Users, db
  from form import FormEditResolution
  
  uid = request.args.get('uid')
  
  form = FormEditResolution()
  if request.method == 'POST':
    if not is_send_allowed():
      return redirect(url_for('main.doc'))

    doc = ResolutionTheUser.query.filter_by(uid=uid).first()
    nickname_victim = form.param1.data
    nickname_accused = form.param2.data
    static_accused = form.param3.data
    time_arrest = form.param4.data
    del_item = form.param5.data
    del_item_list = [int(x) for x in del_item.replace(',', ' ').split() if x.isdigit()]

    selected_static_accused = static_accused if static_accused != '' else doc.static_accused
    selected_nickname_accused = nickname_accused if nickname_accused != '' else doc.nickname_accused
    selected_nickname_victim = nickname_victim if nickname_victim != '' else doc.victim_nickname
    selected_time_arrest = time_arrest if time_arrest != '' else doc.time_arrest

    user = Users.query.filter_by(static=selected_static_accused)

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
    draw_text(pdf, 30, 200, f"Doc. No: {doc.number_resolution if doc else ''}")

    # Основной текст постановления
    draw_text(pdf, 15, 190, f"Я, {current_user.nikname}, являюсь Прокурором штата San Andreas, пользуясь правами,")
    draw_text(pdf, 15, 185, "данными мне Конституцией и законодательством штата San Andreas, а также иными нормативно-правовыми актами,")
    draw_text(pdf, 15, 180, "в связи с необходимостью обеспечения законности и правопорядка в рамках своих полномочий,")
    draw_text(pdf, 80, 175, "ПОСТАНОВЛЯЮ:")

    y = 170
    num = 1

    if doc.param_limit1 and 1 not in del_item_list:
      text = (f"{num}. Возбудить уголовное дело в отношении {'сотрудника ' + user.organ if user else 'гражданина'} "
              f"{selected_nickname_accused}, с номером паспортные данные {selected_static_accused}. Присвоить делу идентификатор {doc.number_case} и принять его к производству прокуратурой штата.")
      y = draw_multiline_text(pdf, text, 15, y)
      y -= 5
      num += 1

    if doc.param_limit2 and 2 not in del_item_list:
      text = (f"{num}. Обязать {'сотрудника ' + user.organ if user else 'гражданина'} {selected_nickname_accused}, с номером паспортные данные {selected_static_accused}, "
              f"в течение 24 часов предоставить на почту Прокурора {current_user.nikname} ({current_user.discordname}@gov.sa) видеозапись процессуальных действий, проведённых в отношении {selected_nickname_victim}, время провдение ареста {selected_time_arrest}. "
              f"Запись должна содержать момент ареста и фиксировать предполагаемое нарушение.")
      y = draw_multiline_text(pdf, text, 15, y)
      y -= 5
      num += 1

    if doc.param_limit3 and 3 not in del_item_list:
      text = (f"{num}. Предоставить личное дело {'сотрудника ' + user.organ if user else 'гражданина'} {selected_nickname_accused}, "
              f"с номером паспортные данные {selected_static_accused}, включающее электронную почту, должность. Срок предоставления информации — 24 часа.")
      y = draw_multiline_text(pdf, text, 15, y)
      y -= 5
      num += 1

    if doc.param_limit4 and 4 not in del_item_list:
      text = f"{num}. Ввести запрет на смену персональных данных {'сотрудника ' + user.organ if user else 'гражданина'} {selected_nickname_accused}, с номером паспортные данные {selected_static_accused}."
      y = draw_multiline_text(pdf, text, 15, y)
      y -= 5
      num += 1

    if doc.param_limit5 and user and user.action != 'Dismissal' and 5 not in del_item_list:
      text = (f"{num}. Ввести запрет на увольнение сотрудника {user.organ} {selected_nickname_accused} с номером паспортные данные {selected_static_accused} "
              f"и на перевод в другие государственные структуры на период расследования по делу с идентификатором {doc.number_case}.")
      y = draw_multiline_text(pdf, text, 15, y)
      y -= 5
      num += 1

    if doc.param_limit6 and user and user.action != 'Dismissal' and 6 not in del_item_list:
      text = f"{num}. Временно отстранить сотрудника {user.organ} {selected_nickname_accused}, с номером паспортные данные {selected_static_accused}, от исполнения служебных обязанностей на время расследования по делу с идентификатором {doc.number_case}."
      y = draw_multiline_text(pdf, text, 15, y)
      y -= 5
      num += 1
    
    generate_signature(pdf, y, current_user, 'resolution')
    y -= 5

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    status = 'edit'
    send_to_bot_new_resolution(uid=uid, nickname=current_user.nikname, static=current_user.static, discordid=current_user.discordid, status=status, number_resolution=doc.number_resolution)
    
    doc.nickname_accused = selected_nickname_accused
    doc.static_accused = selected_static_accused
    doc.discord_accused = user.discordid if user else None
    doc.initiation_case=None if 1 not in del_item_list else doc.initiation_case
    doc.provide_video=None if 2 not in del_item_list else doc.provide_video
    doc.provide_personal_file=None if 3 not in del_item_list else doc.provide_personal_file
    doc.changing_personal_data=None if 4 not in del_item_list else doc.changing_personal_data
    doc.dismissal_employee=None if 5 not in del_item_list else doc.dismissal_employee
    doc.temporarily_suspend=None if 6 not in del_item_list else doc.temporarily_suspend
    doc.victim_nickname=nickname_victim
    doc.time_arrest=selected_time_arrest

    db.session.commit()
    
    return redirect(url_for('main.index'))

@main.route('/get_prosecution_office_content')
def get_prosecution_office_content():
  from __init__ import ResolutionTheUser
  is_visibily_attoney = True

  action_users = ResolutionTheUser.query.filter_by(is_modertation=True).all()
  
  return render_template(
    'main/main-doc-attomey.html', 
    is_visibily_attoney=is_visibily_attoney, 
    action_users=action_users)
