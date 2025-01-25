from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, SelectField, PasswordField, BooleanField, RadioField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, length, EqualTo

class FormAuthPush(FlaskForm):
    static = StringField(validators=[DataRequired(), length(min=1, max=6)], render_kw={"placeholder": "Введите static"})
    password = PasswordField(validators=[DataRequired(), length(min=10, max=40)],render_kw={"placeholder": "Введите password"})
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField(label='отправить', validators=[DataRequired()])

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

class GuestForm(FlaskForm):
    nickname = StringField('Никнейм', validators=[DataRequired()], render_kw={"placeholder": "Введите ник"})
    static = StringField('Статик', validators=[DataRequired()], render_kw={"placeholder": "Введите статик"})
    discord = StringField('Discord ID', validators=[DataRequired()], render_kw={"placeholder": "Введите discordID"})
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw={"placeholder": "Введите пароль"})
    confirm_password = PasswordField(
        'Повторите пароль',
        validators=[DataRequired(), EqualTo('password', message='Пароли должны совпадать')], render_kw={"placeholder": "Повторите пароль"}
    )
    submit = SubmitField('Отправить')
