from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, SelectField, PasswordField, BooleanField, RadioField, TextAreaField
from wtforms.validators import DataRequired, length,  Regexp, ValidationError

# форма ка
class FormAuditPush(FlaskForm):
    action = SelectField('Действие',choices=[
            ('Raising', 'повышение'),
            ('Demotion', 'понижение'),
            ('Dismissal', 'увольнение'),
            ('Invite', 'принятие'),
        ],
        validators=[DataRequired()],
    )
    discordID = StringField(validators=[DataRequired(), length(min=18, max=20)],render_kw={"placeholder": "Введите дс id"})
    discordName = StringField(validators=[DataRequired(), length(min=3, max=20)], render_kw={"placeholder": "Введите дс имя"})
    static = StringField(validators=[DataRequired(), length(min=1, max=6)], render_kw={"placeholder": "Введите статик"})
    nikname = StringField(validators=[DataRequired(), length(min=3, max=45)], render_kw={"placeholder": "Введите ник"})
    rank = StringField(validators=[DataRequired(), length(min=1, max=3)], render_kw={"placeholder": "Введите ранг"})
    reason = StringField(validators=[DataRequired(), length(max=100)], render_kw={"placeholder": "Введите причину"})
    submit = SubmitField(label='отправить', validators=[DataRequired()])

# форма логирования
class FormAuthPush(FlaskForm):
    static = StringField(validators=[DataRequired(), length(min=1, max=6)], render_kw={"placeholder": "Введите static"})
    password = PasswordField(validators=[DataRequired(), length(min=10, max=40)],render_kw={"placeholder": "Введите password"})
    submit = SubmitField(label='отправить', validators=[DataRequired()])
    
# форма для ОГП создание документа  
class FormCreateDoc(FlaskForm):
    nickname = StringField(render_kw={"placeholder": "Ник обвиняемого"})
    static = StringField(validators=[DataRequired(), length(min=1, max=6)], render_kw={"placeholder": "Статик обвиняемого"})
    type_doc = RadioField('Тип документа', choices=[
        ('Order', 'Ордер'),
        ('Resolution', 'Постановление'),
        ('Agenda', 'Повестка'),
    ], validators=[DataRequired()]
    )
    submit = SubmitField(label='отправить', validators=[DataRequired()], render_kw={'id': 'FormBtn'})
    
class Formchangepassword(FlaskForm):
    oldpass = StringField('Старый Пароль', validators=[DataRequired(), length(min=10, max=45)], render_kw={"placeholder": "Введите старый пароль"})
    newpass = StringField('Новый Пароль', validators=[DataRequired(), length(min=10, max=50)], render_kw={"placeholder": "Введите новый пароль"})
    submit = SubmitField(label='Сменить', validators=[DataRequired()], render_kw={'id': 'FormBtn'})

class Formforgetpassword1(FlaskForm):
    staticfp = StringField( validators=[DataRequired()], render_kw={"placeholder": "Введите static"})
    submitfp = SubmitField(label='Отправить код', validators=[DataRequired()], render_kw={'id': 'FormBtn'})

class Formforgetpassword2(FlaskForm):
    codefp = StringField( validators=[DataRequired()], render_kw={"placeholder": "Введите код"})
    new_password = StringField( validators=[DataRequired(), length(min=10, max=45)], render_kw={"placeholder": "Введите новый пароль"})
    submitfp = SubmitField(label='Сбросить пароль', validators=[DataRequired()], render_kw={'id': 'FormBtn'})

class FormCreateResolution(FormCreateDoc):   
    param1 = BooleanField(label="Возбуждение уголовного дела.")
    param2 = BooleanField(label="Запрос видеофиксации задеражания.")
    param3 = BooleanField(label="Запрос перснональных данных.")
    param4 = BooleanField(label="Запрет на смену перснональных данных.")
    param5 = BooleanField(label="Запрет на увольнение, перевод в другую фракцию.")
    param6 = BooleanField(label="Запрет на ведении службы на время расследования.")  
    
    case = StringField(render_kw={"placeholder": "Введите номер дела."})
    arrest_time = StringField(render_kw={"placeholder": "Время ареста."})
    param2_nickname = StringField(render_kw={"placeholder": "Ник потерпевшего."})
    
    
class FormCreateOrder(FormCreateDoc):
    type_order = StringField(label='Тип ордера', render_kw={"placeholder": "Веведите тип оредра", "id": "typeOrder"})
    param1 = StringField(label="Статьи Обвинения.", render_kw={"placeholder": "Введите статьи", "id": "param1"})
    param2 = StringField(label="Срок заключения.", render_kw={"placeholder": "Введите срок ареста", "id": "param2"})
    param3 = StringField(label="Срок исполения.", render_kw={"placeholder": "Введите срок", "id": "param3"})
    param4 = StringField(label="Номер дела.", render_kw={"placeholder": "Введите номер дела", "id": "param4"})    
    
    application_num = StringField(label="Номер заявления.", render_kw={"placeholder": "Введите номер заявления", "id": "applicationNum"})  
    name_organ_for_order = StringField(label="Название организации", render_kw={"placeholder": "Введите название организации", "id": "nameCrimeOrgan"})  
    adreas_organ_for_order = StringField(label="Адреас организации", render_kw={"placeholder": "Введите адреас организации", "id": "adreasCrimeOrgan"}) 
    adreas_suspect = StringField(label="Адреас проживания", render_kw={"placeholder": "Введите адреас проживания", "id": "adreasSuspect"}) 
    car_brand = StringField(label="Марка авто", render_kw={"placeholder": "Введите марка т\с", "id": "carBrand"}) 
    time_ml = StringField(label="Время ВП", render_kw={"placeholder": "Введите время дейстивя ВП", "id": "timeML"})
    areas_under_ml = StringField(label="Время ВП", render_kw={"placeholder": "Введите время дейстивя ВП", "id": "areasUnderML"})
    degree_ri = StringField(label="Степень снятия неприкоса", render_kw={"placeholder": "Введите степень", "id": "degreeRI"})

    
class FormCreateAgenda(FormCreateDoc):
    param5 = StringField(label="Куда явится по повестке.", render_kw={"placeholder": "Введите место", "id": "param5"})
    param6 = StringField(label="В какой время явится.", render_kw={"placeholder": "Введите время", "id": "param6"})
    param7 = StringField(label="С какой целью.", render_kw={"placeholder": "Введите цель", "id": "param7"})

class FormModerationResolution(FlaskForm):
    success = SubmitField("Одобренно", render_kw={'id': 'success'})
    rejected = SubmitField("Отклоненно", render_kw={'id': 'rejected'})
    reason = StringField("Укажите причину.", render_kw={"placeholder": "Введите причину", "id": "reason"})
    
class FormEditResolution(FlaskForm):
    param1 = StringField(render_kw={"placeholder": "Ник потерпевшего."})
    param2 = StringField(render_kw={"placeholder": "Ник обвиняемого."})
    param3 = StringField(render_kw={"placeholder": "Статик обвиняемого."})
    param4 = StringField(render_kw={"placeholder": "Время ареста."})
    param5 = StringField(render_kw={"placeholder": "Убрать пункт"})
    submit = SubmitField("Сохранить")

class Formnews(FlaskForm):
    zagolovok = StringField("Заголовок", validators=[DataRequired(), length(min=5, max=50)], render_kw={"placeholder": "Введите заголовок"})
    desc = TextAreaField("Новость", render_kw={"placeholder": "Введите новость"})
    type_news = SelectField('Тип новости', choices=[
        ('cityhall', 'Правительство'),
        ('weazel', 'Weazel News'),
        ('leaders', 'Лидер'),
    ], validators=[DataRequired()]
    )
    img = FileField('Изображение', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField(label='отправить', validators=[DataRequired()], render_kw={'id': 'FormBtn'})
