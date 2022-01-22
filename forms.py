from flask_wtf import FlaskForm
from wtforms import Form, TextAreaField, validators, StringField, SubmitField, IntegerField, DateField, RadioField
from wtforms.validators import InputRequired
from sqlalchemy import desc, asc

class SettingsForm(FlaskForm):
    fight_duration = IntegerField('Длительность боя, сек', validators=[validators.DataRequired(), validators.number_range(min=1, max=3600)])
    added_time = IntegerField('Дополнительное время, сек', validators=[validators.DataRequired(), validators.number_range(min=1, max=3600)])
    submit = SubmitField('Сохранить')


class CompetitionForm(FlaskForm):
    competition_name_form = StringField('Наименование турнира', validators=[validators.DataRequired()])
    competition_date_start = DateField('Дата начала соревнования', format = '%Y-%m-%d',validators=[validators.DataRequired()])
    competition_date_finish = DateField('Дата завершения соревнования', format = '%Y-%m-%d',validators=[validators.DataRequired()])
    competition_city =  StringField('Город турнира', validators=[validators.DataRequired()])
    submit = SubmitField('Сохранить')

class WeightCategoriesForm(FlaskForm):
    sort_index_form_field = IntegerField('Индекс сортировки', validators=[validators.DataRequired()])
    weight_category_name_form_field = StringField('Наименование категории', validators=[validators.DataRequired()])
    weight_from_form_field = IntegerField('Вес От', validators=[validators.DataRequired()])
    weight_to_form_field = IntegerField('Вес До', validators=[validators.DataRequired()])
    submit = SubmitField('Сохранить')

class ParticipantForm(FlaskForm):
    participant_name_form = StringField('Имя', validators=[validators.DataRequired()])
    participant_last_name_form = StringField('Фамилия', validators=[validators.DataRequired()])
    birthday_form = DateField('Дата рождения', format = '%Y-%m-%d',validators=[validators.DataRequired()])
    avatar_google_code = StringField('Код google для аватарки', validators=[validators.DataRequired()])
    submit = SubmitField('Сохранить')


#class ConstructorFormStep1(FlaskForm):
    #weight_select = RadioField('Label', choices=[('value','description'),('value_two','whatever')])
    #submit = SubmitField('Сохранить')
