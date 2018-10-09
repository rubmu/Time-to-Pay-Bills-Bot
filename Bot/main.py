import urllib.request
from datetime import datetime
from random import randint

import decorator
import telebot

from database import engine
from database_utils import save_user_info,\
    save_message_info, save_photo_info, \
    save_indicators_info, print_indicators, change_indicators_name, change_indicators_value

from Recognition import recognition
from sqlalchemy.orm import sessionmaker

bot = telebot.TeleBot("")
LINK_TO_FOLDER = "https://api.telegram.org/file/bot/"
Session = sessionmaker(bind=engine)
session = Session()

EMOJI_REACTION = "😱😡🤯😤😫😎🤪☺️"

@decorator.decorator
def error_logs(func, *args, **kwargs):
    result = None
    try:
        result = func(*args, **kwargs)
    except Exception as some_error:
        print(some_error.__repr__())
    return result


@error_logs
def process_photo_message(message):
    file_id = message.photo[-1].file_id
    file = bot.get_file(file_id)
    bot.reply_to(message, "Ваше фото обрабатывается. Подождите совсем немного!")

    local_filename = urllib.request.urlretrieve(LINK_TO_FOLDER + file.file_path,
                                                "../Recognition/saved_photo/img" + str(randint(1, 100)) + ".png")

    result_recognition = recognition.detect(local_filename[0])
    text_message = "Записаны показания счетчика «%s»: " \
                   "потребление %s, дата %s" % (message.caption,
                                                result_recognition,
                                                datetime.utcfromtimestamp(int(message.date)).strftime("%d/%m/%y"))

    save_indicators_info(session, result_recognition)
    bot.reply_to(message, text_message)


@bot.message_handler(content_types=['photo'])
def photo(message):
    print(message)
    save_message_info(session,
                      "Photo",
                      datetime.utcfromtimestamp(int(message.date)).strftime("%d/%m/%y %H:%M:%S"),
                      message)
    save_photo_info(session,
                    message.json['photo'][0]['file_size'],
                    message.json['photo'][0]['width'],
                    message.json['photo'][0]['height'],
                    message.json['photo'][0]['file_id'])
    process_photo_message(message)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    save_user_info(session,
                   message.from_user.id,
                   message.from_user.first_name,
                   message.from_user.last_name,
                   message.from_user.username)

    save_message_info(session,
                      "Text",
                      datetime.utcfromtimestamp(int(message.date)).strftime("%d/%m/%y %H:%M:%S"),
                      message)

    bot.reply_to(message, "Привет! Я телеграм-бот, который позволяет сохранять показания всех ваших счётчиков! 💾"
                          " Просто пришлите мне название счётчика и фотографию самого счётчика! 📸")


@bot.message_handler(commands=['stat_all'])
def stat_all(message):
    save_message_info(session,
                      "Text",
                      datetime.utcfromtimestamp(int(message.date)).strftime("%d/%m/%y %H:%M:%S"),
                      message)

    result = print_indicators(session)
    output_string = ""
    for i in range(len(result[0])):
        output_string += "🔸Счётчик «%s». \n\t 🕰 Дата и время заполнения: %s \n\t %s Показания счётчика: %s" %\
                         (str(result[0][i]), str(result[1][i]), str(EMOJI_REACTION[randint(0, 7)]), str(result[2][i]))
        output_string += "\n\n"
    bot.reply_to(message, output_string)


@bot.message_handler(commands=['change_name'])
def change_name(message):
    save_message_info(session,
                      "Text",
                      datetime.utcfromtimestamp(int(message.date)).strftime("%d/%m/%y %H:%M:%S"),
                      message)
    input_message = message.json['text'].split()
    old_name, new_name = input_message[1], input_message[2]
    change_indicators_name(session, str(new_name), str(old_name))
    bot.reply_to(message, "Готово!")


@bot.message_handler(commands=['help'])
def send_welcome(message):
    save_message_info(session,
                      "Text",
                      datetime.utcfromtimestamp(int(message.date)).strftime("%d/%m/%y %H:%M:%S"),
                      message)
    bot.reply_to(message, "У тебя какие-то трудности? Давай помогу! Доступные пока команды:\n /start "
                          "\n /test \n /stat_all \n /change_name и новое название счётчика \n"
                          " /correct_indi и правильное значение показателей счётчика")


@bot.message_handler(commands=['correct_indi'])
def correct_indicators(message):
    save_message_info(session,
                      "Text",
                      datetime.utcfromtimestamp(int(message.date)).strftime("%d/%m/%y %H:%M:%S"),
                      message)
    input_message = message.json['text'].split()
    new_value, name_meter = input_message[1], input_message[2]
    change_indicators_value(session, str(new_value), str(name_meter))
    bot.reply_to(message, "Готово!")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.polling()
