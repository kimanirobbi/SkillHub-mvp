from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class JobForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(), Length(min=5, max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=1000)])
    profession = SelectField('Profession', choices=[
        ('plumber', 'Plumber'),
        ('electrician', 'Electrician'),
        ('carpenter', 'Carpenter'),
        ('cleaner', 'Cleaner'),
        ('mason', 'Mason'),
        ('painter', 'Painter'),
        ('welder', 'Welder'),
        ('mechanic', 'Mechanic'),
        ('technician', 'Technician'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Post Job')