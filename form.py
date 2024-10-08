from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, SelectField, PasswordField, BooleanField, RadioField
from wtforms.validators import DataRequired, Email, length,  Regexp

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
    param1 = BooleanField("Возбуждение уголовного дела.")
    param2 = BooleanField("Запрос видеофиксации задеражания.")
    param3 = BooleanField("Запрос перснональных данных.")
    param4 = BooleanField("Запрет на смену перснональных данных.")
    param5 = BooleanField("Запрет на увольнение, перевод в другую фракцию.")
    param6 = BooleanField("Запрет на ведении службы на время расследования.")
    case = StringField(validators=[DataRequired(), length(min=1, max=5)],render_kw={"placeholder": "Введите номер дел"})
    submit = SubmitField(label='отправить', validators=[DataRequired()])
    arrest_time = StringField(validators=[Regexp(r'^\d{4}/\d{1,2}/\d{1,2}/\d{1,2}/\d{1,2}$', message="Формат: Год/День/Час/Минута")],
                               render_kw={"placeholder": "Год/День/Час/Минута"})
