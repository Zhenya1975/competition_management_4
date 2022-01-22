import os
from flask import Flask, render_template, request, flash, abort, redirect, url_for, json
from flask_socketio import SocketIO, emit
from flask_bootstrap import Bootstrap
from forms import SettingsForm, CompetitionForm, WeightCategoriesForm, ParticipantForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy import desc, asc
from flask_migrate import Migrate
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
#app.secret_key = os.environ.get('SECRET')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fights.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)
bootstrap = Bootstrap(app)




"""Модель для весовых категорий"""
class WeightcategoriesDB(db.Model):
    weight_cat_id = db.Column(db.Integer, primary_key=True)
    sort_index = db.Column(db.Integer)
    weight_category_name = db.Column(db.String)
    weight_category_start = db.Column(db.Integer)
    weight_category_finish = db.Column(db.Integer)
    registrations = db.relationship('RegistrationDB', backref='weight_categories')
    fights = db.relationship('FightsDB', backref = 'weight_category_backref')



"""Модель для регистрации"""
class RegistrationDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitionsDB.competition_id'))
    fighter_id = db.Column(db.Integer, db.ForeignKey('fightersDB.fighter_id'))
    fighter_registration_weight = db.Column(db.Integer)
    fighter_registration_age = db.Column(db.Integer)
    weight_cat_id = db.Column(db.Integer, db.ForeignKey('weightcategoriesDB.weight_cat_id'))
    age_cat_id = db.Column(db.Integer, db.ForeignKey('agecategoriesDB.id'))
    finish_round_id = db.Column(db.Integer, db.ForeignKey('roundsDB.id'))


"""Модель для кругов"""
class RoundsDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    round_name = db.Column(db.String)
    sort_index = db.Column(db.Integer)
    fights = db.relationship('FightsDB', backref = 'roundNo')
    finished_regs = db.relationship('RegistrationDB', backref = 'roundNo')

"""Модель для возрастных категорий"""
class AgecategoriesDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sort_index = db.Column(db.Integer)
    age_category_name = db.Column(db.String)
    age_category_start = db.Column(db.Integer)
    age_category_finish = db.Column(db.Integer)
    registrations = db.relationship('RegistrationDB', backref='age_categories')
    fights = db.relationship('FightsDB', backref = 'age_category_backref')



"""Model for Settings."""
class SettingsDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Fight_duration_DB_Field = db.Column(db.Integer)
    Added_time_DB_Field = db.Column(db.Integer)

"""Модель для соревнований"""
class CompetitionsDB(db.Model):
    competition_id = db.Column(db.Integer, primary_key=True)
    competition_name = db.Column(db.String)
    competition_date_start = db.Column(db.Date, default=datetime.utcnow)
    competition_date_finish = db.Column(db.Date, default=datetime.utcnow)
    competition_city = db.Column(db.String)
    competition_fights = db.relationship('FightsDB', backref='competition', lazy='dynamic')
    registrations = db.relationship('RegistrationDB', backref='competition')



"""Model for fighters."""
class FightersDB(db.Model):
    fighter_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    last_name = db.Column(db.String)
    fighter_image = db.Column(db.String)
    fighter_image_id = db.Column(db.String)
    birthday = db.Column(db.Date, default=datetime.utcnow)
    active_status = db.Column(db.Integer)
    red_fighter = db.relationship('FightsDB', backref='red_fighter', foreign_keys="[FightsDB.red_fighter_id]")
    blue_fighter = db.relationship('FightsDB', backref='blue_fighter', foreign_keys="[FightsDB.blue_fighter_id]")
    registrations = db.relationship('RegistrationDB', backref = 'fighter')

"""Model for fights"""
class FightsDB(db.Model):
    fight_id = db.Column(db.Integer, primary_key=True)
    round_number = db.Column(db.Integer, db.ForeignKey('roundsDB.id')) # номер круга, в котором проводится бой. Текст ,потому что есть полуфинал и финал
    weight_category = db.Column(db.Integer, db.ForeignKey('weightcategoriesDB.weight_cat_id')) # весовая категория, в которой проводится бой
    age_category = db.Column(db.Integer, db.ForeignKey('agecategoriesDB.id'))  # возрастная категория, в которой проводится бой
    red_fighter_id = db.Column(db.Integer, db.ForeignKey('fightersDB.fighter_id')) # id красного бойца
    blue_fighter_id = db.Column(db.Integer, db.ForeignKey('fightersDB.fighter_id')) # id синего бойца
    #fight_status = db.Column(db.String)  # статус боя Запланирован, Завершен
    fight_status = db.Column(db.Boolean, default=False) # False = Запланирован. True - завершен
    red_fighter_score = db.Column(db.Integer) # счет красного бойца
    blue_fighter_score = db.Column(db.Integer) # счет синего бойца
    won_id = db.Column(db.Integer) # результат боя Кто выиграл. Например. ID победителя
    loose_id = db.Column(db.Integer) #  id бойца. который проиграл
    draw_status = db.Column(db.Boolean) # если ничья, то True
    competition_id = db.Column(db.Integer, db.ForeignKey('competitionsDB.competition_id'))
    fight_result = db.Column(db.String)

db.create_all()
SQLALCHEMY_TRACK_MODIFICATIONS = False


"""Возрастные категории"""
age_category_1 = AgecategoriesDB(id=1, sort_index=500, age_category_name= ' от 0 до 12 лет включительно', age_category_start=0, age_category_finish=12)
age_category_2 = AgecategoriesDB(id=2, sort_index=600, age_category_name= 'от 13 до 15 лет включительно', age_category_start=13, age_category_finish=15)
age_category_3 = AgecategoriesDB(id=3, sort_index=700, age_category_name= 'старше 16 лет включительно', age_category_start=16, age_category_finish=1800)
db.session.add(age_category_1)
db.session.add(age_category_2)
db.session.add(age_category_3)


"""Круги"""
round_1 = RoundsDB(id=1, sort_index=500, round_name='круг 1')
round_2 = RoundsDB(id=2, sort_index=600, round_name='круг 2')
round_3 = RoundsDB(id=3, sort_index=700, round_name='круг 3')
round_4 = RoundsDB(id=4, sort_index=800, round_name='круг 4')
round_semifinal = RoundsDB(id=5, sort_index=900, round_name='полуфинал')
round_34 = RoundsDB(id=6, sort_index=1000, round_name='за 3 и 4 место')
round_final = RoundsDB(id=7, sort_index=1100, round_name='финал за 1 и 2 место')
db.session.add(round_1)
db.session.add(round_2)
db.session.add(round_3)
db.session.add(round_4)
db.session.add(round_semifinal)
db.session.add(round_34)
db.session.add(round_final)


"""Весовые категории"""
w_category_1 = WeightcategoriesDB(weight_cat_id = 1, sort_index = 500, weight_category_name = 'до 36 кг включительно', weight_category_start = 0, weight_category_finish = 36)
w_category_2 = WeightcategoriesDB(weight_cat_id = 2, sort_index = 600, weight_category_name = 'от 37 до 48 кг включительно', weight_category_start = 37, weight_category_finish = 48)
w_category_3 = WeightcategoriesDB(weight_cat_id = 3, sort_index = 700, weight_category_name = 'от 49 до 72 кг включительно', weight_category_start = 49, weight_category_finish = 72)
w_category_4 = WeightcategoriesDB(weight_cat_id = 4, sort_index = 800, weight_category_name = 'свыше 73 кг включительно', weight_category_start = 73, weight_category_finish = 1000)
db.session.add(w_category_1)
db.session.add(w_category_2)
db.session.add(w_category_3)
db.session.add(w_category_4)


"""Соревнования"""
competition_one = CompetitionsDB(competition_id = 1, competition_name = "Первенство Москвы по каратэ.")
db.session.add(competition_one)

try:
   db.session.commit()
except Exception as e:
    #print(e)
    db.session.rollback()


# import fighters csv
def import_fighters_csv():
    with open('fighters.csv', encoding='utf8') as csvfile:
        fighters_csv_list = csv.reader(csvfile)
        for row in fighters_csv_list:
            new_fighter = FightersDB(active_status=1, name = row[0], last_name=row[1], fighter_image = row[6], fighter_image_id=row[5],birthday=date(int(row[7]),int(row[8]),int(row[9])))
            db.session.add(new_fighter)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
    return "yep"
#import_fighters_csv()

# import fighters csv
def import_regs_csv():
    with open('fighters - registration_csv.csv', encoding='utf8') as csvfile:
        regs_csv_list = csv.reader(csvfile)
        for row in regs_csv_list:
            new_registration = RegistrationDB(competition_id=int(row[0]), fighter_id=int(row[1]), fighter_registration_weight=int(row[2]), fighter_registration_age=int(row[3]), weight_cat_id=int(row[4]), age_cat_id=int(row[5]))

            db.session.add(new_registration)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
    return "yep"
#import_regs_csv()

"""Настройки боя"""
settings_default = SettingsDB(Fight_duration_DB_Field=60, Added_time_DB_Field=20)
# Мы создаем запись в таблице настроеке, если эта запись еще не была создана
check_record = SettingsDB.query.get('1')
if check_record == None:
    db.session.add(settings_default)
    try:
       db.session.commit()
    except Exception as e:
       db.session.rollback()



socketio = SocketIO(app, cors_allowed_origins='*')



# values['slider1'] and values['slider2'] store the current value of the sliders
# This is done to prevent data loss on page reload by client.

# создаем переменную, которая равна строке из таблицы настроек. В нашем случае это строка с ID =1
settings_row = SettingsDB.query.get("1")


values = {
    'slider1': 25,
    'slider2': 0,
    'default_duration_DB_value': settings_row.Fight_duration_DB_Field,
    'fight_duration_server_value': settings_row.Fight_duration_DB_Field,
    'added_time_server_value': settings_row.Added_time_DB_Field,
    'left_fighter_score': 0,
    'right_fighter_score': 0,
    'competition_name': '',
    'current_fight_id':0,
    'weight_category_name':'',
    'age_category_name':'',
    'roundno':'',
    'red_pic': ''
}


# Handler for default flask route
# Using jinja template to render html along with slider value as input
@app.route('/')
def index():
    return render_template('home.html')

# участники - бойцы, зарегистрированные в системе
@app.route('/participants')
def participants():
    participants = FightersDB.query.all()
    return render_template('participants.html', participants = participants)

# participant view
@app.route('/participants/<int:participant_id>', methods=["POST", "GET"])
def participant_view(participant_id):
    participant = FightersDB.query.get(participant_id)
    form = ParticipantForm()
    if form.validate_on_submit():
        flash('Изменения сохранены')
        participant.name = form.participant_name_form.data
        participant.last_name = form.participant_last_name_form.data
        participant.birthday = form.birthday_form.data
        participant.fighter_image_id = form.avatar_google_code.data
        participant.fighter_image = "https://drive.google.com/uc?id=" + participant.fighter_image_id
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
        return render_template('participant.html', participant = participant, form=form)
    return render_template('participant.html', participant = participant, form=form)



# Competitions list
@app.route('/competitions')
def competitions():
    competitions_data = CompetitionsDB.query.all()
    return render_template('competitions.html', competitions_data = competitions_data)

# Удаление боя из конструктора
@app.route('/competitions/<int:comp_id>/constructor/step2/weightcat/<int:weight_cat_id>/agecat/<int:age_cat_id>/roundno/<int:round_no>/fight_id/<int:fight_id>/fight_delete')
def delete_fight(comp_id, weight_cat_id, age_cat_id, round_no, fight_id):
    fight_to_delete = FightsDB.query.get(fight_id)
    if fight_to_delete is None:
        abort(404, description="No Fight was Found with the given ID")
    if fight_to_delete.fight_status == False:
        db.session.delete(fight_to_delete)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
    else:
        return "Нет запланированного боя с указанным ID"
    return redirect(url_for('fight_constructor_step2', comp_id = comp_id, weight_cat_id = weight_cat_id, age_cat_id = age_cat_id, round_no = round_no))



# Обработчик формы выбора бойцов в конструкторе
@app.route('/competitions/<int:comp_id>/constructor/step2/weightcat/<int:weight_cat_id>/agecat/<int:age_cat_id>/roundno/<int:round_no>/fighters_selected', methods= ['GET', 'POST'])
def constractor_fighters_are_selected(comp_id, weight_cat_id, age_cat_id, round_no):
    if request.method == 'POST':
        # Получаем список getlist из формы. Мы получаем по факту два значения айдишников бойцов, которыпе выбраны в форме
        selected_fighters = request.form.getlist('fighters_from_regs')
        # Проверяем, что список не пустой
        if len(selected_fighters) >0:
            # Присваиваем красному бойцу айдишник первого
            red_fighter_id = selected_fighters[0]
            # и присваиваем синему бойцу айдишник второго
            blue_fighter_id = selected_fighters[1]
            # Сохздаем новый бой с новыми бойцами
            new_fight = FightsDB(round_number = round_no, weight_category = weight_cat_id, age_category = age_cat_id, red_fighter_id = red_fighter_id, blue_fighter_id = blue_fighter_id, fight_status = False, red_fighter_score = 0, blue_fighter_score = 0, competition_id = comp_id)
            db.session.add(new_fight)
            try:
                db.session.commit()
            except Exception as e:
                print(e)
                db.session.rollback()
            # Сейчас нас надо перенаправиться на оригинальную вьюху,передав ей все параметры
            return redirect(url_for('fight_constructor_step2', comp_id = comp_id, weight_cat_id = weight_cat_id, age_cat_id = age_cat_id, round_no = round_no))
    return "Не удалось создать бой"


# Конструктор поединков Шаг 2. Создание боев
@app.route('/competitions/<int:comp_id>/constructor/step2/weightcat/<int:weight_cat_id>/agecat/<int:age_cat_id>/roundno/<int:round_no>')
def fight_constructor_step2(comp_id, weight_cat_id, age_cat_id, round_no):

    competition_data = CompetitionsDB.query.get(comp_id)
    weight_category_data = WeightcategoriesDB.query.get(weight_cat_id)
    age_category_data = AgecategoriesDB.query.get(age_cat_id)
    round_data = RoundsDB.query.get(round_no)
    reg_list_for_constructor = RegistrationDB.query.filter_by(competition_id = comp_id, weight_cat_id = weight_cat_id, age_cat_id = age_cat_id).all()
    fights_data = FightsDB.query.filter_by(competition_id=comp_id, round_number=round_no, weight_category=weight_cat_id, age_category=age_cat_id).all()
    fights_data_qty = FightsDB.query.filter_by(competition_id=comp_id, round_number=round_no, weight_category=weight_cat_id, age_category=age_cat_id).count()
    fights_data_in_all_rounds = FightsDB.query.filter_by(competition_id=comp_id, weight_category=weight_cat_id, age_category=age_cat_id).all()
    # создаем список уникальных айдишников раундов из списока боев в fights_data_in_all_rounds
    round_list = []
    for fight in fights_data_in_all_rounds:
        if fight.round_number not in round_list:
            round_list.append(fight.round_number)

    # cоздаем словарь для таблицы История. Ключем будет круг. Значением будеит список данных
    # Итерируемся по раундам
    round_history = {}
    for round in round_list:
        fight_data = {} # в этот словарь будем записывать данные боев внутри раунда
        list_of_fights_in_round = []  # список боев в раунде
        for fight in FightsDB.query.filter_by(competition_id=comp_id, round_number = round, weight_category=weight_cat_id, age_category=age_cat_id).all(): # итерируемся по боям внутри раунда

            fight_data["fight_id"] = fight.fight_id
            fight_data["red_fighter_name"] = fight.red_fighter.name
            fight_data["red_fighter_last_name"] = fight.red_fighter.last_name
            fight_data["blue_fighter_name"] = fight.blue_fighter.name
            fight_data["blue_fighter_last_name"] = fight.blue_fighter.last_name
            fight_data["fight_result"] = fight.fight_result
            list_of_fights_in_round.append(fight_data)
            fight_data = {}
        round_data_history = RoundsDB.query.get(round)
        round_history[round_data_history.round_name] = list_of_fights_in_round

    # Нужно создать словарь. И итерироваться по словарю, а не по запросу из базы
    fighters_in_left_column = {}
    list_of_selected_fighters = []
    for reg in reg_list_for_constructor: #  итерируемся по регистрациям
        parameters ={}

        if fights_data_qty>0: # проверяем, есть ли бои в нашей выборке
            for fight in fights_data:
                #  если бои есть, то мы проверяем есть ли среди боев бойцы из регистрации
                # Если есть, то присваиваем статус, что бой с этой регистрацией уже существует
                if reg.fighter_id == fight.red_fighter_id or reg.fighter_id == fight.blue_fighter_id:
                    parameters['name'] = reg.fighter.name
                    parameters['last_name'] = reg.fighter.last_name
                    parameters['fight_is_exist'] = True
                    list_of_selected_fighters.append(reg.fighter_id)
                    break
                else:
                    parameters['name'] = reg.fighter.name
                    parameters['last_name'] = reg.fighter.last_name
                    parameters['fight_is_exist'] = False
        else:
            parameters['name'] = reg.fighter.name
            parameters['last_name'] = reg.fighter.last_name
            parameters['fight_is_exist'] = False
        # проверяем не вылетел ли боец
        if reg.finish_round_id:
            parameters["finished_in_round"] = reg.finish_round_id
            parameters["finished_round_name"] = RoundsDB.query.get(reg.finish_round_id).round_name
        else:
            parameters["finished_in_round"] = 0
        fighters_in_left_column[reg.id] = parameters
    print(fighters_in_left_column)
    return render_template('fightconstructorstep2.html',
                           round_history = round_history,
                           list_of_selected_fighters = list_of_selected_fighters,
                           fighters_in_left_column = fighters_in_left_column,
                           fights_data = fights_data,
                           competition_data  = competition_data,
                           weight_category_data = weight_category_data,
                           age_category_data = age_category_data,
                           round_data = round_data,
                           reg_list_for_constructor = reg_list_for_constructor)



# Конструктор поединков. Выбор параметров. constructor view
@app.route('/competitions/<int:comp_id>/constructor', methods= ['GET', 'POST'])
def fight_constructor(comp_id):
    competition_data = CompetitionsDB.query.get(comp_id)
    weight_categories = WeightcategoriesDB.query.order_by(asc(WeightcategoriesDB.sort_index)).all()
    age_categories = AgecategoriesDB.query.order_by(asc(AgecategoriesDB.sort_index)).all()
    rounds = RoundsDB.query.order_by(asc(RoundsDB.sort_index)).all()

    registrations = RegistrationDB.query.filter_by(competition_id=comp_id).all()
    # Получаем список id возрастных категорий из регистраций
    age_cats_in_reg = [] # список возрастных категорий в регистрациях
    for reg in registrations:
        if reg.age_cat_id not in age_cats_in_reg:
            age_cats_in_reg.append(reg.age_cat_id)
    age_cats_in_reg.sort()
    # Получаем словарь наименований возрастных категорий из регистраций
    age_cat_data = {}
    for age_cat in age_categories:
        if age_cat.id in age_cats_in_reg:
            age_cat_names = {}
            age_cat_names["age_cat_id"] = age_cat.id
            age_cat_names["age_cat_name"] = age_cat.age_category_name
            age_cat_data[age_cat.id] = age_cat_names

    # Получаем список id весовых категорий из регистраций
    weight_cats_in_reg = []  # список возрастных категорий в регистрациях
    for reg in registrations:
        if reg.weight_cat_id not in weight_cats_in_reg:
            weight_cats_in_reg.append(reg.weight_cat_id)
    weight_cats_in_reg.sort()

    # Получаем словарь наименований весовых категорий из регистраций
    weight_cat_data = {}
    for weight_cat in weight_categories:
        if weight_cat.weight_cat_id in weight_cats_in_reg:
            weight_cat_names = {}
            weight_cat_names["weight_cat_id"] = weight_cat.weight_cat_id
            weight_cat_names["weight_cat_name"] = weight_cat.weight_category_name
            weight_cat_data[weight_cat.weight_cat_id] = weight_cat_names

    # Считаем количество зарегистрированных участников
    weight_cat_data_im_age_categories = {} # данные в весовых категориях записываются в возрастные категории
    #print("age_cat_data ", age_cat_data)
    #print("weight_cat_data ", weight_cat_data)
    age_weight_data = {}
    age_data = {}
    for age_cat_id, age_cat in age_cat_data.items():
        age_weight_data = {}
        weight_fighter_data = {}
        for weight_cat_id, weight_cat in weight_cat_data.items():
            age_cat_weight_cat_data = {}  # количество зарегистрированных бойцов в весовой категории
            regs_in_age_and_weight_cat = RegistrationDB.query.filter_by(age_cat_id=age_cat_id, weight_cat_id = weight_cat_id).count()
            age_cat_weight_cat_data["weight_cat_id"] = weight_cat_id
            age_cat_weight_cat_data["weight_cat_name"] = WeightcategoriesDB.query.get(weight_cat_id).weight_category_name
            age_cat_weight_cat_data["fighters_qty_in_weight_cat"] = regs_in_age_and_weight_cat

            # сначала получаем выборку из боев с фильтрами
            fights_in_age_and_weight = FightsDB.query.filter_by(age_category = age_cat_id, weight_category = weight_cat_id).all()
            # получаем список с id кругв, из боев в данном возрасте и весе
            list_of_rounds_in_age_in_weight = []
            for fight in fights_in_age_and_weight:
                if fight.round_number not in list_of_rounds_in_age_in_weight:
                    list_of_rounds_in_age_in_weight.append(fight.round_number)
            age_weight_rounds_aggregate_data = {}
            for round_id in list_of_rounds_in_age_in_weight:
                age_weight_rounds_data = {}
                age_weight_rounds_data["round_id"] = round_id
                age_weight_rounds_data["round_name"] = RoundsDB.query.get(round_id).round_name
                number_of_planned_fights = FightsDB.query.filter_by(age_category = age_cat_id, weight_category = weight_cat_id, round_number = round_id).count()
                number_of_finished_fights = FightsDB.query.filter_by(age_category = age_cat_id, weight_category = weight_cat_id, round_number = round_id, fight_status = 1).count()
                if number_of_planned_fights == number_of_finished_fights:
                    age_weight_rounds_data["round_status"] = "Завершен"
                elif number_of_planned_fights > number_of_finished_fights:
                    age_weight_rounds_data["round_status"] = "Не завершен"
                age_weight_rounds_data["planned_fights_qty"] = number_of_planned_fights
                age_weight_rounds_data["finished_fights_qty"] = number_of_finished_fights
                age_weight_rounds_aggregate_data[round_id] = age_weight_rounds_data
            age_cat_weight_cat_data["rounds_data"] = age_weight_rounds_aggregate_data

            weight_fighter_data[weight_cat_id] = age_cat_weight_cat_data

        age_weight_data["age_id"] = age_cat_id
        age_weight_data["age_cat_name"] = AgecategoriesDB.query.get(age_cat_id).age_category_name
        age_weight_data["age_weight_data"] = weight_fighter_data
        #print("age_weight_data ", age_weight_data)
        age_data[age_cat_id] = age_weight_data



    if request.method == 'POST':
        comp_id = competition_data.competition_id
        weight_cat = request.form.get('weight_cats_radio')
        age_cat = request.form.get('age_cat_radio')
        round_no = request.form.get('round_radio')
        if weight_cat and age_cat and round_no:
            return redirect(url_for('fight_constructor_step2', comp_id = comp_id, weight_cat_id = weight_cat, age_cat_id = age_cat, round_no = round_no))
        else:
            flash('Необходимо выбрать возрастную категорию, весовую категорию и круг')
            return render_template('fightconstructor.html', age_data=age_data, competition_data=competition_data,
                                   age_cat_data=age_cat_data, rounds=rounds, weight_cat_data=weight_cat_data)
    return render_template('fightconstructor.html', age_data = age_data, competition_data=competition_data, age_cat_data = age_cat_data, rounds = rounds, weight_cat_data = weight_cat_data)



# список боев
@app.route('/competitions/<int:comp_id>/fights')
def competition_fights_view(comp_id):
    competition_data = CompetitionsDB.query.get(comp_id)
    fights_in_competition = competition_data.competition_fights.all()
    return render_template('fights.html', fights_in_competition = fights_in_competition, competition_data = competition_data)

# создание весовой категории
@app.route('/weightcatgory/new', methods=["POST", "GET"])
def weight_category_new():
    form = WeightCategoriesForm()
    if form.validate_on_submit():
        flash('Изменения сохранены')
        new_weight_category = WeightcategoriesDB(sort_index = form.sort_index_form_field.data, weight_category_name = form.weight_category_name_form_field.data, weight_category_start = form.weight_from_form_field.data, weight_category_finish = form.weight_to_form_field.data)
        db.session.add(new_weight_category)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
        return render_template('newweightcategory.html')
    return render_template('newweightcategory.html', form = form)

# редактирование весовых категорий view
@app.route('/weightcatgory/<int:id>', methods=["POST", "GET"])
def weight_category_edit(id):
    weight_category_data = WeightcategoriesDB.query.get(id)
    form = WeightCategoriesForm()
    if form.validate_on_submit():
        flash('Изменения сохранены')
        weight_category_data.weight_category_name = form.weight_category_name_form_field.data
        weight_category_data.sort_index = form.sort_index_form_field.data
        weight_category_data.weight_category_start = form.weight_from_form_field.data
        weight_category_data.weight_category_finish = form.weight_to_form_field.data
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
        return render_template('weightcategoryedit.html', form = form, weight_category_data = weight_category_data)
    return render_template('weightcategoryedit.html', form=form, weight_category_data=weight_category_data)

# registration list
@app.route('/competitions/<int:competition_id>/registrations')
def registration(competition_id):
    competition_data = CompetitionsDB.query.get(competition_id)
    regs = RegistrationDB.query.all()
    return render_template('registration.html', competition_data = competition_data, regs = regs)


# new registration form
@app.route('/competitions/<int:competition_id>/registrations/new', methods=["POST", "GET"])
def registration_new(competition_id):
    competition_data = CompetitionsDB.query.get(competition_id)
    fighters = FightersDB.query.all()
    regs = RegistrationDB.query.all() # запрос всех регистраций
    fighters_status = {}  # Статус бойца - это словарь. Ключ словаря - id бойца.
    for fighter in fighters:
        # надо понять что такое general_status': fighter.active_status
        fighters_status[fighter.fighter_id] = {'general_status': fighter.active_status, 'reg_status': 0, 'fighter_name': fighter.name, 'fighter_last_name': fighter.last_name}
        for reg in regs:
            if fighter.fighter_id == reg.fighter.fighter_id:
                fighters_status[fighter.fighter_id] = {'general_status':fighter.active_status, 'reg_status': 1, 'fighter_name':fighter.name, 'fighter_last_name': fighter.last_name}



    if request.method == 'POST':
        selected_fighter = request.form.get('fighter_pick')
        new_registration = RegistrationDB(fighter_id = int(selected_fighter), competition_id = competition_id)
        db.session.add(new_registration)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
        last_record = RegistrationDB.query.order_by(desc(RegistrationDB.id)).first()
        id_of_last_record = last_record.id
        registered_fighter = RegistrationDB.query.get(id_of_last_record)
        return redirect(url_for('registration_view', competition_id = competition_id, registration_id = id_of_last_record))

    return render_template('regnewform.html', regs = regs, competition_data = competition_data, fighters = fighters, fighters_status = fighters_status)

# registration delete
@app.route('/competitions/<int:competition_id>/registrations/delete/<int:registration_id>')
def delete_registration(competition_id, registration_id):
    competition_data = CompetitionsDB.query.get(competition_id)
    registration_data = RegistrationDB.query.get(registration_id)
    if registration_data is None:
        abort(404, description="No Reg was Found with the given ID")
    db.session.delete(registration_data)
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
    return redirect(url_for('registration', competition_id=competition_data.competition_id))


# registration view
@app.route('/competitions/<int:competition_id>/registrations/<int:registration_id>', methods=["POST", "GET"])
def registration_view(competition_id, registration_id):
    competition_data = CompetitionsDB.query.get(competition_id)
    fighters = FightersDB.query.all()
    reg = RegistrationDB.query.get(registration_id)
    weight_categories_number_of_records = WeightcategoriesDB.query.count()
    age_categories_number_of_records = AgecategoriesDB.query.count()
    x = competition_data.competition_date_start - reg.fighter.birthday
    y = int(x.days / 365.25)
    reg.fighter_registration_age = y
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()

    # записываем id соотвествующей возрастной категории бойца
    for i in range(1, age_categories_number_of_records + 1):

        if y <= AgecategoriesDB.query.get(i).age_category_finish and y >= AgecategoriesDB.query.get(i).age_category_start:
            reg.age_cat_id = i
            try:
                db.session.commit()
            except Exception as e:
                print(e)
            db.session.rollback()



    if request.method == 'POST':
        flash('Изменения сохранены')
        # записываем значение веса бойца
        reg.fighter_registration_weight = request.form.get('weight_field')
        try:
            db.session.commit()
        except Exception as e:
            print(e)
        db.session.rollback()


        # записываем id соотвествующей весовой категории бойца
        for i in range(1, weight_categories_number_of_records + 1):
            if reg.fighter_registration_weight <= WeightcategoriesDB.query.get(
                    i).weight_category_finish and reg.fighter_registration_weight >= WeightcategoriesDB.query.get(
                    i).weight_category_start:

                reg.weight_cat_id = i
                try:
                    db.session.commit()
                except Exception as e:
                    print(e)
                db.session.rollback()


        return render_template('registrationform.html', competition_data=competition_data, reg=reg, fighters=fighters, age = y)
    return render_template('registrationform.html', competition_data=competition_data, reg=reg, fighters = fighters, age= y)

# competition view
@app.route('/competitions/<int:competition_id>', methods=["POST", "GET"])
def competition_view(competition_id):
    competition_data = CompetitionsDB.query.get(competition_id)
    form = CompetitionForm()
    if form.validate_on_submit():
        competition_data.competition_name = form.competition_name_form.data
        competition_data.competition_date_start = form.competition_date_start.data
        competition_data.competition_date_finish = form.competition_date_finish.data
        competition_data.competition_city = form.competition_city.data
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()


        return render_template('competition.html', competition_data=competition_data, form=form)
    return render_template('competition.html', competition_data = competition_data, form=form)


# Завершение боя
@app.route('/competitions/<int:comp_id>/fights/<int:fight_id>', methods=["POST", "GET"])
def fight_finished(comp_id, fight_id):
    fight = FightsDB.query.get(fight_id)
    competition = CompetitionsDB.query.get(comp_id)
    red_fighter_registration = RegistrationDB.query.filter_by(competition_id=comp_id, fighter_id=fight.red_fighter_id).all()
    blue_fighter_registration = RegistrationDB.query.filter_by(competition_id=comp_id, fighter_id=fight.blue_fighter_id).all()

    if request.method == 'POST':
        fight_rusult = request.form.get('fightresult')
        fight.fight_status = 'Завершен'
        fight.red_fighter_score = values['left_fighter_score']
        fight.blue_fighter_score = values['right_fighter_score']
        if fight_rusult == 'winner_red':
            fight.won_id = fight.red_fighter_id
            fight.loose_id = fight.blue_fighter_id
            fight.draw_status = False
            fight.fight_status = True # Завершен
            fight.fight_result = 'Победил ' + fight.red_fighter.name + ' ' + fight.red_fighter.last_name
            blue_fighter_finished_round_id = request.form.get('fighter_finished')
            blue_fighter_registration[0].finish_round_id = blue_fighter_finished_round_id

        elif fight_rusult == 'winner_blue':
            fight.won_id = fight.blue_fighter_id
            fight.loose_id = fight.red_fighter_id
            fight.draw_status = False
            fight.fight_status = True  # Завершен
            fight.fight_result = 'Победил ' + fight.blue_fighter.name + ' ' + fight.blue_fighter.last_name
            red_fighter_finished_round_id = request.form.get('fighter_finished')
            red_fighter_registration[0].finish_round_id = red_fighter_finished_round_id
        else:
            fight.won_id = 0
            fight.loose_id = 0
            fight.draw_status = True
            fight.fight_status = True  # Завершен
            fight.fight_result = 'Ничья'
        try:
            db.session.commit()
        except Exception as e:
            print(e)
        db.session.rollback()
        values['left_fighter_score'] = 0
        values['right_fighter_score'] = 0
        return redirect (url_for('fights', comp_id = competition.competition_id))

#  выбор вьюхи для разного типа боя - завершенного или запланированного
@app.route('/competitions/<int:comp_id>/weightcat/<int:weight_cat_id>/agecat/<int:age_cat_id>/roundno/<int:round_no>/fights/<int:fight_id>')
def select_fight_status(comp_id, weight_cat_id, age_cat_id, round_no, fight_id):
    competition = CompetitionsDB.query.get(comp_id)
    weightcat = WeightcategoriesDB.query.get(weight_cat_id)
    agecat = AgecategoriesDB.query.get(age_cat_id)
    round = RoundsDB.query.get(round_no)
    fight = FightsDB.query.get(fight_id)
    if fight.fight_status:
        return redirect (url_for('closed_fight', comp_id = competition.competition_id, weight_cat_id = weightcat.weight_cat_id, age_cat_id = agecat.id,  round_no = round.id, fight_id = fight.fight_id))
    else:
        return redirect (url_for('fight', comp_id = competition.competition_id, weight_cat_id = weightcat.weight_cat_id, age_cat_id = agecat.id,  round_no = round.id, fight_id = fight.fight_id))



# карточка завершенного боя
@app.route('/competitions/<int:comp_id>/weightcat/<int:weight_cat_id>/agecat/<int:age_cat_id>/roundno/<int:round_no>/fights/<int:fight_id>/closed')
def closed_fight(comp_id, weight_cat_id, age_cat_id, round_no, fight_id):
    competition = CompetitionsDB.query.get(comp_id)
    weightcat = WeightcategoriesDB.query.get(weight_cat_id)
    agecat = AgecategoriesDB.query.get(age_cat_id)
    round = RoundsDB.query.get(round_no)
    fight = FightsDB.query.get(fight_id)
    #if fight is None:
    #    abort(404, description="Не найдено боев с указанным ID")
    #elif fight.fight_status:
    return render_template('closed_fight.html', competition = competition, weightcat = weightcat, agecat = agecat, round = round, fight = fight)
    #else:
    #    abort(404, description="Не найдено завершенного боя с указанным ID")

# Карточка боя
@app.route('/competitions/<int:comp_id>/weightcat/<int:weight_cat_id>/agecat/<int:age_cat_id>/roundno/<int:round_no>/fights/<int:fight_id>/open')
def fight(comp_id, weight_cat_id, age_cat_id, round_no, fight_id):
    competition = CompetitionsDB.query.get(comp_id)
    weightcat = WeightcategoriesDB.query.get(weight_cat_id)
    agecat = AgecategoriesDB.query.get(age_cat_id)
    round = RoundsDB.query.get(round_no)
    fight = FightsDB.query.get(fight_id)
    values['current_fight_id'] = fight_id
    closed_fights_in_competition = FightsDB.query.filter_by(competition_id = comp_id, fight_status = 1).all() # Получили все завершенные бои в соревновании
    red_fighter_history = {}
    for closed_fight in closed_fights_in_competition:
        red_fighter_fight_result = {} # результаты боев, в которых участвовал красный боец
        if closed_fight.fight_id != fight_id:
            if fight.red_fighter_id == closed_fight.red_fighter_id:
                red_fighter_fight_result["round"] = closed_fight.roundNo.round_name
                red_fighter_fight_result["partner"] = "Соперник: " + closed_fight.blue_fighter.name + " " + closed_fight.blue_fighter.last_name
                red_fighter_fight_result["result"] = closed_fight.fight_result
                red_fighter_history[closed_fight.roundNo.round_name] = red_fighter_fight_result
            elif fight.red_fighter_id == closed_fight.blue_fighter_id:
                red_fighter_fight_result["round"] = closed_fight.roundNo.round_name
                red_fighter_fight_result["partner"] = "Соперник: " + closed_fight.red_fighter.name + " " + closed_fight.red_fighter.last_name
                red_fighter_fight_result["result"] = closed_fight.fight_result
                red_fighter_history[closed_fight.roundNo.round_name] = red_fighter_fight_result
            else:
                continue

    blue_fighter_history = {}
    for closed_fight in closed_fights_in_competition:
        blue_fighter_fight_result = {}  # результаты боев, в которых участвовал красный боец
        if closed_fight.fight_id != fight_id:
            if fight.blue_fighter_id == closed_fight.blue_fighter_id:
                blue_fighter_fight_result["round"] = closed_fight.roundNo.round_name
                blue_fighter_fight_result["partner"] = "Соперник: " + closed_fight.red_fighter.name + " " + closed_fight.red_fighter.last_name
                blue_fighter_fight_result["result"] = closed_fight.fight_result
                blue_fighter_history[closed_fight.roundNo.round_name] = blue_fighter_fight_result
            elif fight.blue_fighter_id == closed_fight.red_fighter_id:
                blue_fighter_fight_result["round"] = closed_fight.roundNo.round_name
                blue_fighter_fight_result["partner"] = "Соперник: " + closed_fight.blue_fighter.name + " " + closed_fight.blue_fighter.last_name
                blue_fighter_fight_result["result"] = closed_fight.fight_result
                blue_fighter_history[closed_fight.roundNo.round_name] = blue_fighter_fight_result
            else:
                continue

    return render_template('referee.html',
                           closed_fights_in_competition = closed_fights_in_competition,
                           blue_fighter_history = blue_fighter_history,
                           red_fighter_history =  red_fighter_history,
                           competition = competition,
                           weightcat = weightcat,
                           agecat = agecat,
                           round = round,
                           fight = fight,
                           **values)

# Visitor view
@app.route('/visitor')
def visitor():
    fight_id = values['current_fight_id']
    fight = FightsDB.query.get(fight_id)

    return render_template('visitor.html', **values, fight = fight)

@app.route('/competitions/<int:comp_id>/fights')
def fights(comp_id):
    competition = CompetitionsDB.query.get(comp_id)
    fights = FightsDB.query.all()
    return render_template('fights.html', **values, fights = fights, competition = competition)

@app.route('/test')
def test():
    test_value = "Это значение, приехавшее с сервера"
    return render_template('test.html', test_value = 2)
@app.route('/test2')
def test2():
    return render_template('test2.html')

# Handler for a message received over 'connect' channel
@socketio.on('connect')
def test_connect():
    emit('after connect', {'data': 'Lets dance'})


# при получении сообщения от клиента мы апдейтим значения переменных
# emit отправляет сообщение чероз канал 'update value'
#@socketio.on('Slider value changed')
#def value_changed(message):
#    values[message['who']] = message['data']
#    emit('update value', message, broadcast=True)


@socketio.on('Timer value changed')
def timer_value_changed(timer_message):
    values['fight_duration_server_value'] = timer_message['timer_sent']
    emit('update_timer_value', timer_message, broadcast=True)


@socketio.on('Fight_data')
def fight_data_func(message):
    values['competition_name'] = message['competition_name']
    values['weight_category_name'] = message['weight_category_name']
    values['age_category_name'] = message['age_category_name']
    values['roundno'] = message['roundno']
    values['red_pic'] = message['red_pic']
    values['blue_pic'] = message['blue_pic']
    emit('update_competition_name', message, broadcast=True)


@socketio.on('Score value changed')
def left_fighter_score_added_func(message):
    values['left_fighter_score'] = message['left_fighter_score']
    #values['right_fighter_score'] = message['right_fighter_score']
    print("values['left_fighter_score'] ",values['left_fighter_score'])
    emit('update_left_fighter_score', message, broadcast=True)

@socketio.on('Right score value changed')
def right_fighter_score_func(message):
    values['right_fighter_score'] = message['right_fighter_score']
    emit('update_right_fighter_score', message, broadcast=True)



# Settings view
@app.route("/settings", methods=["GET", "POST"])
def settings_form():
    """Standard `contact` form."""
    form = SettingsForm()
    form_weight_categories = WeightCategoriesForm()
    w_categories = WeightcategoriesDB.query.order_by(asc(WeightcategoriesDB.sort_index)).all()
    age_categories = AgecategoriesDB.query.order_by(asc(AgecategoriesDB.sort_index)).all()
    if form.validate_on_submit():
        flash('Изменения сохранены')
        values['default_duration_DB_value'] = form.fight_duration.data
        values['added_time_server_value'] = form.added_time.data
        # Записываем изменнения в базу, в таблицу настроек
        # создаем переменную, которая равна строке из таблицы настроек. В нашем случае это строка с ID =1
        settings_row = SettingsDB.query.get("1")
        settings_row.Fight_duration_DB_Field = form.fight_duration.data
        settings_row.Added_time_DB_Field = form.added_time.data
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
        #finally:db.session.close()

        return render_template("settings.html",form=form, **values, w_categories = w_categories, form_weight_categories = form_weight_categories, age_categories = age_categories)
    return render_template("settings.html", form=form, **values, w_categories = w_categories, form_weight_categories = form_weight_categories, age_categories = age_categories)



if __name__ == "__main__":
    #socketio.run(app)
    app.run()
