from database import User, Message, Image, Text, Indicator
from sqlalchemy import update
from sqlalchemy.sql.expression import insert

def save_user_info(session, telegram_id, first_name, last_name, username):
    user = User(first_name=first_name,
                last_name=last_name,
                username=username,
                telegram_id=telegram_id)
    session.add(user)
    session.commit()


def save_message_info(session, content_type, date, message):
    user = None
    for i in session.query(User.id):
        user = i
    saved_message = Message(user=user,
                            content_type=content_type,
                            date=date)
    if content_type == "Text":
        save_text_info(session,
                       message.json['text'],
                       message.json['entities'][0]['length'],
                       message.json['entities'][0]['type'])
    elif 'caption' in message.json:
        save_text_info(session,
                       message.json['caption'],
                       len(message.json['caption']),
                       "caption")
    session.add(saved_message)
    session.commit()


def save_photo_info(session, full_size, width, height, file_id):
    message = None
    for i in session.query(Message.id):
        message = i
    image = Image(message_id=message,
                  full_size=full_size,
                  width=width,
                  height=height,
                  file_id=file_id)
    session.add(image)
    session.commit()


def save_text_info(session, content, length, type):
    message = None
    for i in session.query(Message.id):
        message = i
    text = Text(message_id=message,
                content=content,
                length=length,
                type=type)
    session.add(text)
    session.commit()


def save_indicators_info(session, meters):
    name = None
    date = None
    for i, j in session.query(Message.date, Text.content):
        date, name = i, j

    indicator = Indicator(id=None,
                          name=name,
                          date=date,
                          meter_numbers=meters)
    session.add(indicator)
    session.commit()


def print_indicators(session):
    result_name = []
    result_date = []
    result_meter = []
    for name, date, meter_numbers in session.query(Indicator.name, Indicator.date, Indicator.meter_numbers):
        result_name.append(name)
        result_date.append(date)
        result_meter.append(meter_numbers)
    return result_name, result_date, result_meter


def print_selected_indicators(session, input_name):
    result_name = []
    result_date = []
    result_meter = []
    for name, date, meter_numbers in session.query(Indicator).filter(Indicator.name.like(input_name)).all():
        result_name.append(name)
        result_date.append(date)
        result_meter.append(meter_numbers)
    return result_name, result_date, result_meter


def change_indicators_name(session, new_name, old_name):
    id_old_name = None
    old_date = None
    old_meters = None
    for id, date, meter_numbers in session.query(Indicator.id, Indicator.date, Indicator.meter_numbers).filter(Indicator.name==old_name):
        id_old_name, old_date, old_meters = id, date, meter_numbers
    #Indicator.update().where(Indicator.c.id == id_old_name).values(name=new_name)
    indicator = Indicator(id=id_old_name, name=new_name, date=old_date, meter_numbers=old_meters)
    indicator.update(session)


def change_indicators_value(session, new_value, name_meter):
    id_name = None
    current_name = None
    current_date = None
    for id, date, name in session.query(Indicator.id, Indicator.date, Indicator.name).filter(Indicator.name == name_meter):
        id_name, current_date, current_name = id, date, name

    indicator = Indicator(id=id_name, name=current_name, date=current_date, meter_numbers=new_value)
    indicator.update(session)