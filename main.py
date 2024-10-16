from flask import render_template, redirect, url_for, request, flash, Blueprint, session, send_file
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from form import FormAuditPush, FormAuthPush
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
    color = '#008000' # черный
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

def send_to_bot_new_resolution(uid, nickname, static, discrodid):
  message = {
      'uid': uid,
      'nickname': nickname, 
      'static': static, 
      'discrodid': discrodid
  }
  redis_client.publish('new_resolution', json.dumps(message))
  print("Подписка на канал 'new_resolution' выполнена.")

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
        if current_user.is_authenticated and current_user.action == 'Dismissal':
            logout_user()
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
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

  if current_user.is_authenticated:
      return redirect(url_for('main.profile'))

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

  return render_template('auth.html', form=form)

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
  from __init__ import db, Users, ActionUsers
  form = FormAuditPush()  # Assuming you have a FormAuditPush class defined
  
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
            # User found and action is not 'Dismissal'
            timespan = datetime.now()
            
            # Record the action in ActionUsers
            new_action = ActionUsers(
              discordid=current_user.discordid,
              discordname=current_user.discordname,
              static=current_user.static,
              nikname=current_user.nikname,
              timespan=timespan,
              staticof=user.static,
              actionof=action,
              currrankof='0',  # Rank becomes 0
              prevrankof=user.rankuser
            )
            db.session.add(new_action)
            
            # Update the user's status
            user.prevrank = user.rankuser
            user.rankuser = '0'  # Set rank to 0 for dismissal
            user.action = 'Dismissal'
            user.timespan = timespan
            
            # Optionally, send a DM for dismissal notification
            send_to_bot_dismissal(user.discordid, user.static, user.organ)
            
            db.session.commit()
            
            send_to_bot_ka(action, static, user_curr.discordid, discord_id, '0', '1', user_curr.nikname, user.nikname, reason)
            
            flash('Вы успешно уволили', 'success')
            return redirect(url_for('main.audit'))
        
            
          # повышение существующего юзера во фракции
          elif action == 'Raising':
            prev_rank = user.rankuser
            new_rank = form.rank.data
            
            # проверка новый ранг должен быть больше старого
            if new_rank < prev_rank:
              flash('При повышении, новый ранг не может быть меньше старого')
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
            
            if new_rank > prev_rank:
              flash('При понижении, новый ранг не может быть больше старого')
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
  
def logout_user(user):
  logout_user(user)

# профиль
@main.route('/profile')
@check_user_action
@login_required
def profile():
  nickname = current_user.nikname
  organ = current_user.organ
  rank = current_user.rankuser
  color = color_organ(organ)

  filename = "./python/name-ranks.json"
  ranks = read_ranks(filename)
  rank_name = get_rank_info(ranks, organ, rank)
      
  return render_template('profile.html', nickname=nickname, organ=organ, rank=rank, rank_name=rank_name, color=color)

@main.route('/doc')
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
  from __init__ import Users, PDFDocument, db
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

      num = 1
      y = 170  # Начальная координата по Y для списка
      if param1:
          pdf.drawString(15 * mm, y * mm, f"{num}. Возбудить уголовное дело в отношении сотрудника {user.organ} {nickname} с номером")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f"идентификационного знака {static}, присвоить делу идентификатор {case_number}. Принять дело к")
          y -= 5
          pdf.drawString(15 * mm, y * mm, "собственному производству.")
          y -= 10
          num += 1
          
      if param2:
          pdf.drawString(15 * mm, y * mm, f"{num}. Сотруднику {user.organ} {nickname} с номером идентификационного знака {static}, в течении")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f"24-ёх часов надлежит предоставить на почту Прокурора {current_user.nikname} {current_user.discordname}@gov.sa")
          y -= 5
          pdf.drawString(15 * mm, y * mm, "видеофиксацию проведения процессуальных и следственных действий в отношение гражданина")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f"c {arrest_time}, а также иных следственных действий, явившихся предпосылкой произведенного ")
          y -= 5
          pdf.drawString(15 * mm, y * mm, "задержания, включая момент фиксации предполагаемого нарушения.")
          y -= 10
          num += 1
          
      if param3:
          pdf.drawString(15 * mm, y * mm, f"{num}. Предоставить личное дело сотрудника {user.organ} {nickname} с номером")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f"идентификационного знак {static}, включающее в себя: паспортные данные, должность в государственной")
          y -= 5
          pdf.drawString(15 * mm, y * mm, "структуре. Информация должна быть предоставлена в течение 24-х")
          y -= 10
          num += 1
          
      if param4:
          pdf.drawString(15 * mm, y * mm, f"{num}. Запрет на смену персональных данных сотруднику {user.organ} {nickname}")
          y -= 10
          num += 1
      if param5:
          pdf.drawString(15 * mm, y * mm, f"{num}. Сотруднику {user.organ} {nickname} с номером идентификационного знака 58630 запретить")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f"увольнение с государственной организации {user.organ}  и перевод в другие государственные")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f"фракции на момент расследования по делопроизводству с идентификатором {case_number}")
          y -= 10
          num += 1
      if param6:
          pdf.drawString(15 * mm, y * mm, f"{num}. Запрет на ведение службы на время расследования по дулопроизводству с индификаинным")
          y -= 5
          pdf.drawString(15 * mm, y * mm, f"{case_number} сотруднику {user.organ} {nickname} c номером ОПЗ {static}")
          y -= 10
          num += 1

      # Завершаем документ
      pdf.drawString(15 * mm, y * mm, "Настоящее постановление вступает в законную силу с момента его подписания и публикации")
      y -= 5
      pdf.drawString(15 * mm, y * mm, "на портале штата San Andreas.")
      
      # загрузка картинки
      y -= 40
      image_path = os.path.join('static', 'img', 'print.png')
      pdf.drawImage(image_path, 20 * mm, y * mm, width=30 * mm, height=30 * mm)
      
      pdf.showPage()
      pdf.save()
      buffer.seek(0)
      
      curr_user = Users.query.filter_by(static=current_user.static).first()

      # Проверяем, что пользователь найден
      if user:
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
      else:
          flash('Пользователь не найден.')
          return redirect(url_for('main.create_doc'))
        
      send_to_bot_new_resolution(uid=uid, nickname=curr_user.nikname, static=curr_user.static, discrodid=curr_user.discordid)
      
    elif typeDoc == 'Agenda':
      pass
    
  return redirect(url_for('main.doc'))


@main.route('/resolution')
def temporary_page():
    from __init__ import PDFDocument
    uid = request.args.get('uid')

    if not uid:
        return "No UID provided", 400 

    pdf_doc = PDFDocument.query.filter_by(uid=uid).first()
    if pdf_doc:
        if not os.path.exists(pdf_doc.content):
            return "PDF file not found on server", 404
          
        return render_template('temporary_page.html', pdf_path=pdf_doc.content)
    else:
        return "PDF not found or invalid UID", 404


@main.route('/edit_doc', methods=['GET', 'POST'])
def edit_doc():
  from __init__ import PDFDocument, db
  uid = request.args.get('uid')
  if not uid:
      return "No UID provided", 400

  pdf_doc = PDFDocument.query.filter_by(uid=uid).first()
  if not pdf_doc:
      return "PDF not found", 404

  if request.method == 'POST':
      # Получить отредактированные данные из формы
      new_param1 = request.form.get('param1')
      new_param2 = request.form.get('param2')
      # и так далее для всех параметров

      # Создаем новый PDF с обновленными данными
      buffer = BytesIO()
      pdf = canvas.Canvas(buffer, pagesize=A4)
      pdf.setFont("Helvetica", 12)

      # Используем обновленные параметры для создания нового PDF
      pdf.drawString(100, 750, f"Updated param1: {new_param1}")
      pdf.drawString(100, 730, f"Updated param2: {new_param2}")

      # Добавьте сюда код для отображения других параметров

      pdf.showPage()
      pdf.save()
      buffer.seek(0)

      # Сохраняем новый PDF
      new_file_path = os.path.join('uploads', f'{uid}_updated.pdf')
      with open(new_file_path, 'wb') as f:
          f.write(buffer.getvalue())

      # Обновляем запись в базе данных с новым файлом
      pdf_doc.content = new_file_path
      db.session.commit()

      flash('PDF успешно обновлен')
      return redirect(url_for('main.temporary_page', uid=uid))

  # Если метод GET, отобразить форму с текущими данными для редактирования
  return render_template('edit_form.html', document=pdf_doc)