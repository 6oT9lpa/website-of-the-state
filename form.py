from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, SelectField, PasswordField, BooleanField, RadioField
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
    nickname = StringField(validators=[DataRequired(), length(min=3, max=45)], render_kw={"placeholder": "Введите ник"})
    static = StringField(validators=[DataRequired(), length(min=1, max=6)], render_kw={"placeholder": "Введите статик"})
    type_doc = RadioField('Тип документа', choices=[
        ('Order', 'Ордер'),
        ('Resolution', 'Постановление'),
        ('Agenda', 'Повестка'),
    ], validators=[DataRequired()]
    )
    submit = SubmitField(label='отправить', validators=[DataRequired()], render_kw={'id': 'FormBtn'})
    
class FormCreateResolution(FormCreateDoc):   
    param1 = BooleanField("Возбуждение уголовного дела.")
    param2 = BooleanField("Запрос видеофиксации задеражания.")
    param3 = BooleanField("Запрос перснональных данных.")
    param4 = BooleanField("Запрет на смену перснональных данных.")
    param5 = BooleanField("Запрет на увольнение, перевод в другую фракцию.")
    param6 = BooleanField("Запрет на ведении службы на время расследования.")  
    case = StringField(render_kw={"placeholder": "Введите номер дела"})
    arrest_time = StringField(render_kw={"placeholder": "Год.Месяц.День Час:Минута"})
    
    
class FormCreateOrder(FormCreateDoc):
    param1 = StringField("Статьи Обвинения.", validators=[
    DataRequired(),
  ], render_kw={"placeholder": "Введите статьи", "id": "param1"})
    param2 = StringField("Срок заключения.", render_kw={"placeholder": "Введите срок ареста", "id": "param2"})
    param3 = StringField("Срок исполения.", render_kw={"placeholder": "Введите срок", "id": "param3"})
    param4 = StringField("Номер дела.", render_kw={"placeholder": "Введите номер дела", "id": "param4"})    

    
class FormCreateAgenda(FormCreateDoc):
    param5 = StringField("Куда явится по повестке.", render_kw={"placeholder": "Введите место", "id": "param5"})
    param6 = StringField("В какой время явится.", render_kw={"placeholder": "Введите время", "id": "param6"})
    param7 = StringField("С какой целью.", render_kw={"placeholder": "Введите цель", "id": "param7"})

