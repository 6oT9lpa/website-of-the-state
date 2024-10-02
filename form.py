from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, Email, length

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
    discordID = StringField(validators=[DataRequired(), length(min=18, max=18)],render_kw={"placeholder": "Введите дс id"})
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