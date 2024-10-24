from flask import render_template, redirect, url_for, request, flash, Blueprint, session, send_file, make_response, jsonify, abort
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from form import FormAuditPush, FormAuthPush, Formchangepassword, Formforgetpassword1, Formforgetpassword2
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import random, string, redis, json, os

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

def send_to_bot_permission_none(is_permission):
    message = {'permission_none': is_permission}
    redis_client.publish('user_permission', json.dumps(message))

def send_to_bot_new_resolution(uid, nickname, static, discordid):
  message = {
      'uid': uid,
      'nickname': nickname, 
      'static': static, 
      'discordid': discordid
  }
  redis_client.publish('new_resolution', json.dumps(message))

def send_to_bot_invite(password, discord_id, static, organ):
    message = {
        'password': password,
        'discord_id': discord_id,
        'static': static, 
        'organ': organ
    }
    redis_client.publish('invite_channel', json.dumps(message))

def send_to_bot_changepass(code, discord_id):
    message = {
        'code': code,
        'discord_id': discord_id
    }
    redis_client.publish('changepass_channel', json.dumps(message))

def send_to_bot_dismissal(discord_id, static, organ):
    message = {
        'discord_id': discord_id,
        'static': static,
        'organ': organ
    }
    redis_client.publish('dismissal_channel', json.dumps(message))

def send_to_bot_ka(action, static_to, discord_id_from, discord_id_to, curr_rank, prev_rank, nikname_from, nikname_to, reason):
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
  
def user_permission(f):
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

# главная страница
@main.route('/')
def index():
  return render_template('index.html')

# Логирование
@main.route('/auth', methods=['POST', 'GET'])
def auth():
  from __init__ import db, Users
  form = FormAuthPush()
  formfp = Formforgetpassword1()
  formfp2 = Formforgetpassword2()

  if current_user.is_authenticated:
      return redirect(url_for('main.profile'))
  #Вход крч
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
      return jsonify(redirect_url=url_for('main.index')), 400

  return render_template('auth.html', form=form, formfp=formfp, formfp2=formfp2)

# перенаправление на страницу
@main.after_request
def redirect_login(response):
    if response.status_code == 401:
        return redirect(url_for('main.auth') + '?next=' + request.url)

    return response


# Кадровый аудит
@main.route('/audit', methods=['POST', 'GET'])
@check_user_action
@login_required
def audit():
  from __init__ import db, Users, ActionUsers, PermissionUsers
  form = FormAuditPush()  
  
  permissionUser = PermissionUsers.query.filter_by(user_static=current_user.static).first()
  if not (permissionUser.high_staff or permissionUser.lider or permissionUser.admin or permissionUser.tech):
    flash("Доступ запрещен, отсутствуют права.")
    return redirect(url_for('main.profile'))

  # получение изменения ка от конкретного юзера
  action_users = []
  action_users = ActionUsers.query.filter_by(static=current_user.static).all()
  userof = ''
  
  if action_users:
    for item in action_users:
      userof = Users.query.filter_by(static=item.staticof).first()

  user_curr = Users.query.filter_by(static=current_user.static).first()     
  if user_curr:
    organ = user_curr.organ
    nikname = user_curr.nikname
    
    color = color_organ(organ)

  # проверка валидации формы
  if form.validate_on_submit():
    static = form.static.data
    action = form.action.data
    discord_name = form.discordName.data
    discord_id = form.discordID.data
    reason = form.reason.data

    user = Users.query.filter_by(static=static).first()
    user_curr = Users.query.filter_by(static=current_user.static).first()
    
    if static == user_curr.static:
      flash('Нельзя проводить действия над собой')
      return redirect(url_for('main.audit'))
    
    # проверка action invite на существование статика, если есть то ошибка
    if action == 'Invite':
      if user and user.action == 'Dismissal':
        timespan = datetime.now()
          
        # получение фракции от юзера который пишет ка
        if user_curr:
          organ_curr = user_curr.organ

        # создание первоначального пароля
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for i in range(10))
        print(password)
        
        # хэшированиие пароля
        hash_password = generate_password_hash(password)
        
        # запись сообщение в redis
        send_to_bot_invite(password, discord_id, static, user.organ)
        
        # изменение существущей строки
        user.password = hash_password
        user.prevrank = '0'
        user.rankuser = '1'
        user.action = 'Invite'
        user.organ = organ_curr
        user.timespan = timespan
        user.nikname = form.nikname.data

        # создание изменения ка
        new_action_curr_user = ActionUsers(discordid=current_user.discordid, discordname=current_user.discordname, static=current_user.static, nikname=current_user.nikname, timespan=timespan, staticof=user.static, actionof=action, currrankof='1', prevrankof='0')
        db.session.add(new_action_curr_user)
        db.session.commit()

        send_to_bot_ka(action, static, user_curr.discordid, discord_id, '1', '0', user_curr.nikname, user.nikname, reason)
        
        flash('Успешно!', 'success')
        return redirect(url_for('main.audit'))
        
      # если в базе отстуствует запись о пользователя
      elif user is None:
        existing_discordID = Users.query.filter_by(discordid=discord_id).all()
        existing_discordName = Users.query.filter_by(discordname=discord_name).all()
        
        # проверка на более двух дс во фракции
        if len(existing_discordName) > 1 or len(existing_discordID) > 1:
          flash('Данный дискорд уже состоит в 2-ух гос. структурах!', 'error')
          return redirect(url_for('main.audit'))
        
        else:
          # создание первоначального пароля
          characters = string.ascii_letters + string.digits + string.punctuation
          password = ''.join(random.choice(characters) for i in range(10))

          timespan = datetime.now()
          hash_password = generate_password_hash(password)
          
          # получение фракции юзера который пишет ка 
          user_curr = Users.query.filter_by(static=current_user.static).first() 
          if user_curr:
            organ_curr = user_curr.organ
            
          # создание нового юзера  
          new_user = Users(discordid=discord_id, discordname=discord_name, static=static, nikname=form.nikname.data, action=action, organ=organ_curr, prevrank='1', rankuser=form.rank.data, timespan=timespan, password=hash_password)

          new_action_curr_user = ActionUsers(discordid=current_user.discordid, discordname=current_user.discordname, static=current_user.static, nikname=current_user.nikname, timespan=timespan, staticof=static, actionof=action, currrankof='1', prevrankof='0')
          
          db.session.add(new_action_curr_user)
          db.session.add(new_user)
          db.session.commit()
          # запись сообщение в redis
          send_to_bot_invite(password, discord_id, static, user_curr.organ)
          
          send_to_bot_ka(action, static, user_curr.discordid, discord_id, '1', '0', user_curr.nikname, form.nikname.data, reason)
          
          flash('Успешно!', 'success')
          return redirect(url_for('main.audit'))
          
      else:
        flash('Такой статик уже имеется во госс. фракции!', 'error')
        return redirect(url_for('main.audit'))
                  
    else:
      # actions (Raising, Demotion, Dismissal) поиск статика на существаония, если нет ошибка
      user = Users.query.filter_by(static=static).first()
      if not user or user.action == 'Dismissal':
          flash('Такого статика не существует во фракции!', 'error')
          return redirect(url_for('main.audit'))
        
      else:
        # увольнение существуещего юзера с фракции
        if action == 'Dismissal':
          timespan = datetime.now()
          
          new_action = ActionUsers(
            discordid=current_user.discordid,
            discordname=current_user.discordname,
            static=current_user.static,
            nikname=current_user.nikname,
            timespan=timespan,
            staticof=user.static,
            actionof=action,
            currrankof='0',
            prevrankof=user.rankuser
          )
          user_perm = PermissionUsers(
            user_static=user.static, 
            user_discordid=user.discordid, 
            tech=False, 
            admin=False, 
            lider=False, 
            high_staff=False, 
            creation_doc = False
          )
          
          db.session.add(user_perm)
          db.session.add(new_action)
          
          user.prevrank = user.rankuser
          user.rankuser = '0' 
          user.action = 'Dismissal'
          user.timespan = timespan

          send_to_bot_dismissal(user.discordid, user.static, user.organ)
          db.session.commit()
          
          send_to_bot_ka(action, static, user_curr.discordid, discord_id, '0', '1', user_curr.nikname, user.nikname, reason)
          
          flash('Вы успешно уволили', 'success')
          return redirect(url_for('main.audit'))
      
          
        # повышение существующего юзера во фракции
        elif action == 'Raising':
          prev_rank = user.rankuser
          new_rank = form.rank.data
          
          if new_rank >= user_curr.rankuser:
            flash('Вы не можете повысить на тот же или выше своего ранга!')
            return redirect(url_for('main.audit'))
          
          if new_rank <= prev_rank:
            flash('При повышении, новый ранг не может быть меньше или равен старому')
            return redirect(url_for('main.audit'))

          timespan = datetime.now()
          new_action_curr_user = ActionUsers(discordid=current_user.discordid, discordname=current_user.discordname, static=current_user.static, nikname=current_user.nikname, timespan=timespan, staticof=static, actionof=action, currrankof=form.rank.data, prevrankof=user.rankuser)
          db.session.add(new_action_curr_user)
          
          # перезапись существущих данных строки 
          user.prevrank = prev_rank
          user.action = action
          user.rankuser = new_rank 
          user.timespan = timespan
          
          db.session.commit() 
          
          send_to_bot_ka(action, static, user_curr.discordid, discord_id, user.rankuser, user.prevrank, user_curr.nikname, user.nikname, reason)
          
          flash('Статик успешно повышен', 'success')
          return redirect(url_for('main.audit'))
        
        # понижение сущесвующего юзера во фракции
        elif action == 'Demotion':
          prev_rank = user.rankuser
          new_rank = form.rank.data
          
          if prev_rank >= user_curr.rankuser:
            flash('Вы не можете понизить ранг выше или равен вашему')
            return redirect(url_for('main.audit'))
          
          if new_rank >= prev_rank:
            flash('При понижении, новый ранг не может быть больше или равен старому')
            return redirect(url_for('main.audit'))
          
          timespan = datetime.now()
          new_action_curr_user = ActionUsers(discordid=current_user.discordid, discordname=current_user.discordname, static=current_user.static, nikname=current_user.nikname, timespan=timespan, staticof=static, actionof=action, currrankof=form.rank.data, prevrankof=user.rankuser)
          db.session.add(new_action_curr_user)
          
          user.action = action
          user.rankuser = new_rank 
          user.prevrank = prev_rank
          user.timespan = timespan
          
          db.session.commit() 
          
          send_to_bot_ka(action, static, user_curr.discordid, discord_id, user.rankuser, user.prevrank, user_curr.nikname, user.nikname, reason)
          
          flash('Статик успешно понижен', 'success')
          return redirect(url_for('main.audit'))
          
    return redirect(url_for('main.audit'))

  return render_template('ka.html', form=form, organ=organ, color=color, nikname=nikname, action_users=action_users,  userof=userof)

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
  rank = current_user.rankuser
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
@main.route('/doc', methods=['GET', 'POST'])
def doc():
  from __init__ import Users
  from form import FormCreateDoc, FormCreateResolution, FormCreateOrder, FormCreateAgenda
  form = FormCreateDoc()
  formResolution = FormCreateResolution()
  formOrder = FormCreateOrder()
  formAgenda = FormCreateAgenda()
  
  if current_user.is_authenticated:
    nickname = current_user.nikname
    organ = current_user.organ
    color = color_organ(organ)

  return render_template('doc.html', form=form, formResolution=formResolution, formOrder=formOrder, formAgenda=formAgenda, nickname=nickname, organ=organ, color=color)

@main.route('/create_doc',  methods=['POST', 'GET'])
def create_doc():
  from __init__ import Users, PDFDocument, PublicDocumentAndNotifications, db
  from form import FormCreateDoc, FormCreateResolution, FormCreateOrder, FormCreateAgenda
  form = FormCreateDoc()
  formResolution = FormCreateResolution()
  formOrder = FormCreateOrder()
  formAgenda = FormCreateAgenda()
  
  if form.validate_on_submit():
    typeDoc = form.type_doc.data
    
    if typeDoc == 'Order':
      pass
    
    elif typeDoc == 'Resolution':
      uid = ''.join([str(random.randint(0, 9)) for _ in range(26)])
      session['uid'] = uid

      nickname = form.nickname.data
      static = form.static.data
      
      user = Users.query.filter_by(static=static).first()
        
      param1 = formResolution.param1.data
      param2 = formResolution.param2.data
      param3 = formResolution.param3.data
      param4 = formResolution.param4.data
      param5 = formResolution.param5.data
      param6 = formResolution.param6.data
      nickname_victim = formResolution.param2_nickname.data
      case_number = formResolution.case.data
      arrest_time = formResolution.arrest_time.data
      
      buffer = BytesIO()
      pdf = canvas.Canvas(buffer, pagesize=A4)
      pdf.setTitle("Постановление")

      # Путь к шрифту
      font_path = os.path.join('static', 'fonts', 'times.ttf')
      pdfmetrics.registerFont(TTFont('TimesNewRoman', font_path))  # Убедитесь, что файл находится в static/fonts
      pdfmetrics.registerFont(TTFont('TimesNewRoman-Bold', os.path.join('static', 'fonts', 'timesbd.ttf')))  # Полужирный шрифт

      # Использование шрифта
      pdf.setFont("TimesNewRoman", 12)
      
      # загрузка картинки
      image_path = os.path.join('static', 'img', 'DepOfJustice.png')
      pdf.drawImage(image_path, 50 * mm, 245 * mm, width=100 * mm, height=50 * mm)
      
      # Рисуем заголовок и основную информацию
      pdf.setFont("TimesNewRoman-Bold", 14)
      pdf.drawString(50 * mm, 235 * mm, "UNITED STATES DEPARTMENT OF JUSTICE")
      pdf.drawString(70 * mm, 230 * mm, "прокуратура штата Сан-Андреас")
      pdf.setFont("TimesNewRoman", 12)
      pdf.drawString(60 * mm, 225 * mm, "90001, г. Лос-Сантос, Рокфорд-Хиллз, Карцер-Вей")
      
      # загрузка картинки
      image_path = os.path.join('static', 'img', 'text separator.png')
      pdf.drawImage(image_path, 10 * mm, 210 * mm, width=190 * mm, height=10 * mm)
      
      pdf.drawString(150 * mm, 200 * mm, f"Дата: {datetime.now().strftime('%d.%m.%Y')}")
      pdf.drawString(30 * mm, 200 * mm, f"Doc. No: {case_number}")

      pdf.setFont("TimesNewRoman-Bold", 14)
     # pdf.drawString(15 * mm, 220 * mm, "ПОСТАНОВЛЕНИЕ")
      pdf.setFont("TimesNewRoman", 12)

      # Рисуем текст постановления
      pdf.drawString(15 * mm, 190 * mm, f"Я, {current_user.nikname}, являюсь Прокурором штата San Andreas пользуясь своими правами, ")
      pdf.drawString(15 * mm, 185 * mm, "данными мне Конституцией и законодательством штата San Andreas.")
      pdf.setFont("TimesNewRoman-Bold", 14)
      pdf.drawString(80 * mm, 175 * mm, "ПОСТАНОВЛЯЮ:")
      pdf.setFont("TimesNewRoman", 12)

      isParam1 = False
      isParam2 = False
      isParam3 = False
      isParam4 = False
      isParam5 = False
      isParam6 = False

      num = 1
      y = 170  # Начальная координата по Y для списка
      if user:
        if param1:
          pdf.drawString(15 * mm, y * mm, f"{num}. Возбудить уголовное дело в отношении сотрудника {user.organ} {nickname} с номером идентификационного знака")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f" {static}, присвоить делу идентификатор {case_number}. Принять дело к собственному производству.")
          y -= 10
          num += 1
          isParam1 = True
            
        if param2:
          pdf.drawString(15 * mm, y * mm, f"{num}. Сотруднику {user.organ} {nickname} с номером идентификационного знака {static}, в течении")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f"24-ёх часов надлежит предоставить на почту Прокурора {current_user.nikname} {current_user.discordname}@gov.sa")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f"видеофиксацию проведения процессуальных и следственных действий в отношение {nickname_victim}")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f"c {arrest_time}, а также иных следственных действий, явившихся предпосылкой произведенного ")
          y -= 5
          pdf.drawString(15 * mm, y * mm, "задержания, включая момент фиксации предполагаемого нарушения.")
          y -= 10
          num += 1
          isParam2 = True
            
        if param3:
          pdf.drawString(15 * mm, y * mm, f"{num}. Предоставить личное дело сотрудника {user.organ} {nickname} с номером")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f"идентификационного знак {static}, включающее в себя: паспортные данные, должность в государственной")
          y -= 5
          pdf.drawString(15 * mm, y * mm, "структуре. Информация должна быть предоставлена в течение 24-х")
          y -= 10
          num += 1
          isParam3 = True
            
        if param4:
          pdf.drawString(15 * mm, y * mm, f"{num}. Запрет на смену персональных данных сотруднику {user.organ} {nickname}")
          y -= 10
          num += 1
          isParam4 = True
            
        if param5:
          pdf.drawString(15 * mm, y * mm, f"{num}. Сотруднику {user.organ} {nickname} с номером идентификационного знака 58630 запретить")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f"увольнение с государственной организации {user.organ}  и перевод в другие государственные")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f"фракции на момент расследования по делопроизводству с идентификатором {case_number}")
          y -= 10
          num += 1
          isParam5 = True
            
        if param6:
          pdf.drawString(15 * mm, y * mm, f"{num}. Запрет на ведение службы на время расследования по делопроизводству с индификаинным")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f"{case_number} сотруднику {user.organ} {nickname} c номером ОПЗ {static}")
          y -= 10
          num += 1
          isParam6 = True
          
      else:
        if param1:
          pdf.drawString(15 * mm, y * mm, f"{num}. Возбудить уголовное дело в отношении сотрудника гражаданина {nickname} с номером идентификационного")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f"знака {static}, присвоить делу идентификатор {case_number}. Принять дело к собственному производству.")
          y -= 10
          num += 1
          isParam1 = True
          
        if param2:
          pdf.drawString(15 * mm, y * mm, f"{num}. Сотруднику гражданина {nickname} с номером идентификационного знака {static}, в течении")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f"24-ёх часов надлежит предоставить на почту Прокурора {current_user.nikname} {current_user.discordname}@gov.sa")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f"видеофиксацию проведения процессуальных и следственных действий в отношение {nickname_victim}")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f"c {arrest_time}, а также иных следственных действий, явившихся предпосылкой произведенного ")
          y -= 5
          pdf.drawString(15 * mm, y * mm, "задержания, включая момент фиксации предполагаемого нарушения.")
          y -= 10
          num += 1
          isParam2 = True
            
        if param3:
          pdf.drawString(15 * mm, y * mm, f"{num}. Предоставить личное дело сотрудника гражданина {nickname} с номером")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f"идентификационного знак {static}, включающее в себя: паспортные данные, должность в государственной")
          y -= 5
          pdf.drawString(15 * mm, y * mm, "структуре. Информация должна быть предоставлена в течение 24-х")
          y -= 10
          num += 1
          isParam3 = True
            
        if param4:
          pdf.drawString(15 * mm, y * mm, f"{num}. Запрет на смену персональных данных сотруднику гражданина {nickname}")
          y -= 10
          num += 1
          isParam4 = True

      # Завершаем документ
      pdf.drawString(15 * mm, y * mm, "Настоящее постановление вступает в законную силу с момента его подписания и публикации")
      y -= 5
      pdf.drawString(15 * mm, y * mm, "на портале штата San Andreas.")
      
      
      sing_font_path = os.path.join('static', 'fonts', 'Updock-Regular.ttf') 
      pdfmetrics.registerFont(TTFont('Updock', sing_font_path))

      # Генерация подписи
      full_name = current_user.nikname
      name_parts = full_name.split()
      first_name = name_parts[0]  # Используем только первое слово в качестве имени
      last_name_initial = name_parts[1][0] if len(name_parts) > 1 else ''  # Если есть фамилия, берем первую букву
      signature = f"{first_name} {last_name_initial}."

      y -= 10
      pdf.setFont("TimesNewRoman-Bold", 14)
      pdf.drawString(120 * mm, y * mm, "Министерство Юстиций")
      y -= 5
      pdf.setFont("TimesNewRoman", 12)
      pdf.drawString(110 * mm, y * mm, f"Прокурор {full_name} | {current_user.discordname}@gov.sa")
      
      y -= 15
      pdf.setFont("Updock", 32)  
      pdf.drawString(130 * mm, y * mm, f"{signature}")
      pdf.setFont("TimesNewRoman", 10)
      y -= 2
      pdf.drawString(130 * mm, y * mm, "____________________")
      y -= 3
      pdf.drawString(140 * mm, y * mm, "(подпись)")

      y -= 5
      # Загрузка изображения печати
      image_path = os.path.join('static', 'img', 'print.png')
      pdf.drawImage(image_path, 20 * mm, y * mm, width=30 * mm, height=30 * mm)
      
      pdf.showPage()
      pdf.save()
      buffer.seek(0)
      
      curr_user = Users.query.filter_by(static=current_user.static).first()

      global file_path
      file_path = os.path.join('static', 'uploads', f'{uid}.pdf')
      with open(file_path, 'wb') as f:
          f.write(buffer.getvalue())
      
      pdf_document = PDFDocument(
          user_static=curr_user.static, 
          user_discordid=curr_user.discordid,
          uid=uid,
          content=file_path,
          created_at=datetime.now()
      )
      db.session.add(pdf_document)
      db.session.commit()
        
      send_to_bot_new_resolution(uid=uid, nickname=curr_user.nikname, static=curr_user.static, discordid=curr_user.discordid)
      
      if not user:
        new_resolution = PublicDocumentAndNotifications(
          uid=uid, 
          nickname_attorney=current_user.nikname,
          static_attorney=current_user.static,
          discord_attorney=current_user.discordid,
          nickname_accused = nickname,
          static_accused = static,
          param_limit1=isParam1,
          param_limit2=isParam2,
          param_limit3=isParam3,
          param_limit4=isParam4,
          param_limit5=isParam5,
          param_limit6=isParam6,
          param_limit2_nickmane=nickname_victim, 
          param_limit2_time=arrest_time
          ) 
      elif user:
        new_resolution = PublicDocumentAndNotifications(
          uid=uid, 
          nickname_attorney=current_user.nikname,
          static_attorney=current_user.static,
          discord_attorney=current_user.discordid,
          nickname_accused = nickname,
          static_accused = static,
          discord_accused = user.discordid,
          param_limit1=isParam1,
          param_limit2=isParam2,
          param_limit3=isParam3,
          param_limit4=isParam4,
          param_limit5=isParam5,
          param_limit6=isParam6,
          param_limit2_nickmane=nickname_victim, 
          param_limit2_time=arrest_time
          )
        
      db.session.add(new_resolution)
      db.session.commit()

    elif typeDoc == 'Agenda':
      pass
    
  return redirect(url_for('main.doc'))

@main.route('/resolution', methods=['POST', 'GET'])
@user_permission
def resolution():
    from __init__ import PDFDocument, PublicDocumentAndNotifications, db
    from form import FormModerationResolution
    uid = request.args.get('uid')

    if not uid:
      return "No UID provided", 400 

    pdf_doc = PDFDocument.query.filter_by(uid=uid).first()
    if pdf_doc:
      if not os.path.exists(pdf_doc.content):
        return "PDF file not found on server", 404
      
      moder = PublicDocumentAndNotifications.query.filter_by(uid=uid).first()
      form = FormModerationResolution()

      if form.success.data:
        moder.is_modertation = True
        
        moderation = True
        reason = 'None'
        send_to_bot_information_resolution(moder.discord_attorney, current_user.discordid, moderation, reason, uid)
        
        db.session.commit()
  
      elif form.rejected.data:
          reason = form.reason.data
          moderation = False
          send_to_bot_information_resolution(moder.discord_attorney, current_user.discordid, moderation, reason, uid)
          
          return redirect(url_for('main.doc'))
      
      if moder.is_modertation:
        flash('Данное постановелние проверенно!')
        return redirect(url_for('main.doc'))
      
      return render_template('temporary_page.html', pdf_path=pdf_doc.content, form=form, uid=uid) 
    else:
      return "PDF not found or invalid UID", 404

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

@main.route('/edit_doc', methods=['GET', 'POST'])
@user_is_moder
def edit_doc():
  from __init__ import PDFDocument, db
  from form import FormEditResolution
  
  uid = request.args.get('uid')
  if not uid:
      return "No UID provided", 400

  pdf_doc = PDFDocument.query.filter_by(uid=uid).first()
  if not pdf_doc:
      return "PDF not found", 404 
  
  form = FormEditResolution()
  
  return render_template('edit_doc.html', pdf_path=pdf_doc.content, form=form)


@main.route('/get_prosecution_office_content')
def get_prosecution_office_content():
  from __init__ import PublicDocumentAndNotifications
  is_visibily_attoney = True

  action_users = PublicDocumentAndNotifications.query.filter_by(is_modertation=True).all()
  
  return render_template(
    'main/main-doc-attomey.html', 
    is_visibily_attoney=is_visibily_attoney, 
    action_users=action_users)
