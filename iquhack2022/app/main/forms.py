from flask_wtf import Form
from wtforms.fields import StringField, SubmitField , IntegerField
from wtforms.validators import Required


class LoginForm(Form):
    """Accepts a nickname and a room."""
    name = StringField('Nickname', validators=[Required()])
    submit = SubmitField('Join')
