import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import config
import datetime
import database

bot = telebot.TeleBot(config.TOKEN)


# Start


@bot.message_handler(commands=['start'])
def cmdStart(msg):
    bot.delete_message(msg.chat.id, msg.id)

    bot.send_message(msg.chat.id, f'Здравствуйте, я телеграм бот для поиска менторов курсов "Geeks"')

    menu(msg)


# Task


# 0 - id, 1 - contant, 2 - name, 3 - month, 4 - problem, 5 - format
userInfo = []
mentorsForTask = []
tasks = []


@bot.message_handler(commands=['task'])
def cmdTask(msg):

    bot.delete_message(msg.chat.id, msg.id)

    msgIteration = 0

    try:
        while True:
            if userInfo[msgIteration][0] == id:
                break
            else:
                msgIteration += 1
    except Exception:
        pass

    username = msg.chat.username
    if username is not None:
        username = f'@{username}'
    userInfo.append([msg.chat.id, username, 'name', 'month', 'problem', 'format'])
    bot.send_message(msg.chat.id, 'Для поиска ментора необходимо заполнить заявку на помощь\n'
                                  'Для заполнения просто отвечайте на вопросы')
    taskStart(msg)


def taskStart(msg):
    bot.send_message(msg.chat.id, 'Ваше имя:\n')

    bot.register_next_step_handler(msg, taskName)


def taskName(msg):
    saveInfo(msg.text, 2, msg.chat.id)

    bot.send_message(msg.chat.id, 'Ваш месяц обучения в курсах Geeks', reply_markup=monthButtons())
    bot.register_next_step_handler(msg, taskMonth)


def taskMonth(msg):
    filter = [
        '1',
        '2',
        '3',
        '4',
        '5'
    ]
    if str(msg.text).lower() in filter:
        saveInfo(msg.text, 3, msg.chat.id)

        bot.send_message(msg.chat.id, 'Кратко опишите вашу проблему\n')
        bot.register_next_step_handler(msg, taskProblem)
    else:
        bot.send_message(msg.chat.id, 'Ошибка\n'
                                      'Вы ввели неправильные данные\n'
                                      'Повторно введите данные\n\n'
                                      'Ваш месяц обучения в курсах Geeks', reply_markup=monthButtons())
        bot.register_next_step_handler(msg, taskMonth)


def taskProblem(msg):
    saveInfo(msg.text, 4, msg.chat.id)
    bot.send_message(msg.chat.id, 'В каком формате вам нужна помощь?\n'
                                  'Онлайн - Ментор вам поможет через интернет\n'
                                  'Оффлайн - Ментор вам поможет в офисе Geeks', reply_markup=formatButtons())
    bot.register_next_step_handler(msg, taskFormat)


def taskFormat(msg):
    filter = [
        'онлайн',
        'оффлайн'
    ]

    if str(msg.text).lower() in filter:
        saveInfo(msg.text, 5, msg.chat.id)

        if userInfo[getIteration(msg.chat.id)][1] is None:
            bot.send_message(msg.chat.id, 'Ваш номер телефона\n'
                                          'Номер телефона берется для того, чтобы ментор с вами связался\n'
                                          'Пример: "+996*********"')
            bot.register_next_step_handler(msg, taskContact)
        else:
            bot.send_message(msg.chat.id, 'Подтвердите отправку заявки', reply_markup=confirmButtons())
            bot.register_next_step_handler(msg, confirmTask)
    else:
        bot.send_message(msg.chat.id, 'Ошибка\n'
                                      'Вы ввели неправильные данные\n'
                                      'Повторно введите данные\n\n'
                                      'В каком формате вам нужна помощь?\n'
                                      'Онлайн - Ментор вам поможет через интернет\n'
                                      'Оффлайн - Ментор вам поможет в офисе Geeks', reply_markup=formatButtons())
        bot.register_next_step_handler(msg, taskFormat)


def taskContact(msg):
    phoneNum = str(msg.text).lower().replace(' ', '')
    if len(phoneNum.replace('+996', '')) == 9:
        saveInfo(msg.text, 1, msg.chat.id)
        bot.send_message(msg.chat.id, 'Подтвердите отправку заявки', reply_markup=confirmButtons())
        bot.register_next_step_handler(msg, confirmTask)

    else:
        bot.send_message(msg.chat.id, 'Ошибка\n'
                                      'Вы ввели неправильные данные\n'
                                      'Повторно введите данные\n\n'
                                      'Ваш номер телефона\n'
                                      'Номер телефона берется для того, чтобы ментор с вами связался\n'
                                      'Пример: "+996*********"')

        bot.register_next_step_handler(msg, taskContact)


def confirmTask(msg):
    if msg.text == 'Отправить':
        taskEnd(msg)
    elif msg.text == 'Отменить заявку':
        bot.send_message(msg.chat.id, 'Отправка заявки отменена')
        menu(msg)
    else:
        bot.send_message(msg.chat.id, 'Ошибка, повторите попытку', reply_markup=confirmButtons())
        bot.register_next_step_handler(msg, confirmTask)


def taskEnd(msg):
    sendTask(msg)
    bot.send_message(msg.chat.id, 'Спасибо за заполнение заявки, в течении 10 минут с вами свяжется ментор\n\n'
                                  'Чем могу вам помочь?\n'
                                  '/task - Вызвать ментора\n', reply_markup=menuButtons())
    deleteInfo(msg.chat.id)


def sendTask(msg):
    infoIteration = getIteration(msg.chat.id)
    month = userInfo[infoIteration][3]
    mentorMessage = f'Время отправки: {str(datetime.datetime.now()).split(".")[0]}\n' \
                    f'Контакты: {userInfo[infoIteration][1]}\n' \
                    f'Имя: {userInfo[infoIteration][2]}\n' \
                    f'Месяц обучения: {userInfo[infoIteration][3]}\n' \
                    f'Проблемы: {userInfo[infoIteration][4]}\n' \
                    f'Формат: {userInfo[infoIteration][5]}\n'

    if mentorsForTask:
        status = 1
        for el in mentorsForTask:
            menMonth = database.getMenMonth(str(el[0]))
            if int(menMonth) > int(month):
                if userInfo[infoIteration][5] == el[1]:
                    status = 0
                    bot.send_message(el[0], mentorMessage)
                    mentorsForTask.remove(el)
        if status:
            tasks.append([mentorMessage, month, userInfo[infoIteration][5]])
    else:
        tasks.append([mentorMessage, month, userInfo[infoIteration][5]])


def saveInfo(info, index, id):
    infoIteration = 0
    while True:
        if userInfo[infoIteration][0] == id:
            userInfo[infoIteration][index] = str(info)
            break
        else:
            infoIteration += 1


def deleteInfo(id):
    infoIteration = getIteration(id)
    userInfo.pop(infoIteration)


def getIteration(id):
    infoIteration = 0
    while True:
        if userInfo[infoIteration][0] == id:
            break
        else:
            infoIteration += 1
    return infoIteration


def confirmButtons():
    markup = ReplyKeyboardMarkup()
    markup.row_width = 2
    markup.one_time_keyboard = True
    markup.resize_keyboard = True
    markup.add(KeyboardButton('Отправить'),
               KeyboardButton('Отменить заявку'),)
    return markup


def monthButtons():
    markup = ReplyKeyboardMarkup()
    markup.row_width = 5
    markup.one_time_keyboard = True
    markup.resize_keyboard = True
    markup.add(KeyboardButton('1'),
               KeyboardButton('2'),
               KeyboardButton('3'),
               KeyboardButton('4'),
               KeyboardButton('5'))
    return markup


def formatButtons():
    markup = ReplyKeyboardMarkup()
    markup.row_width = 2
    markup.one_time_keyboard = True
    markup.resize_keyboard = True
    markup.add(KeyboardButton('Онлайн'),
               KeyboardButton('Оффлайн'))
    return markup


# Menu

def menu(msg):
    bot.send_message(msg.chat.id, '/task - Обратится к ментору\n', reply_markup=menuButtons())


def menuButtons():
    markup = ReplyKeyboardMarkup()
    markup.row_width = 1
    markup.one_time_keyboard = True
    markup.resize_keyboard = True
    markup.add(KeyboardButton('/task'))
    return markup


# Admin

@bot.message_handler(commands=['admin'])
def adminCmd(msg):
    if msg.chat.id in config.MENTORID:
        bot.send_message(msg.chat.id, 'Админ панель управления', reply_markup=adminButtons())
        bot.register_next_step_handler(msg, adminMenu)
    else:
        bot.delete_message(msg.chat.id, msg.id)
        bot.send_message(msg.chat.id, 'You have not permission')


def adminMenu(msg):
    if msg.text == 'Менторы':
        bot.send_message(msg.chat.id, 'Комманды', reply_markup=adminMenComButtons())
        bot.register_next_step_handler(msg, adminMen)
    elif msg.text == 'Кандидаты':
        bot.send_message(msg.chat.id, 'Комманды', reply_markup=adminCanComButtons())
        bot.register_next_step_handler(msg, adminCan)
    elif msg.text == 'Мониторинг':
        taskInfo = ''
        mentorsOnline = ''
        for el in tasks:
            taskInfo += f'Месяц обучения {el[1]}, Формат: {el[2]}\n'
        for el in mentorsForTask:
            mentorFullInfo = database.getFullMentorInfo(str(el[0]))
            mentorsOnline += f'Имя: {mentorFullInfo[0]} | Формат: {el[1]} | Месяц: {mentorFullInfo[2]}\n'
        if mentorsOnline == '':
            mentorsOnline = "В данный момент нет менторов в сети"
        bot.send_message(msg.chat.id, f'В данный момент {len(tasks)} тасков ждут подходящих себе менторов\n'
                                      f'{taskInfo}\n\n'
                                      f'Менторы которые находятся в сети:\n'
                                      f'{mentorsOnline}')
        return adminCmd(msg)
    elif msg.text == 'Exit':
        pass
    else:
        bot.send_message(msg.chat.id, 'Ошибка', reply_markup=adminButtons())
        bot.register_next_step_handler(msg, adminMenu)


def adminMen(msg):
    if msg.text == 'Удалить':
        bot.send_message(msg.chat.id, 'Менторы:', reply_markup=adminMenButtons())
        bot.register_next_step_handler(msg, deleteMen)
    elif msg.text == 'Обновить месяц':
        bot.send_message(msg.chat.id, 'Менторы:', reply_markup=adminMenButtons())
        bot.register_next_step_handler(msg, updateMen)
    elif msg.text == 'Cancel':
        return adminCmd(msg)
    else:
        bot.send_message(msg.chat.id, 'Ошибка', reply_markup=adminMenComButtons())
        bot.register_next_step_handler(msg, adminMen)


def deleteMen(msg):
    if msg.text == 'Cancel':
        return adminCmd(msg)
    name = msg.text[0:len(msg.text) - 2]
    database.deleteMenInfo(name)
    bot.send_message(msg.chat.id, f'{name} был удалён из менторов')
    return adminCmd(msg)


def updateMen(msg):
    if msg.text == 'Cancel':
        return adminCmd(msg)
    name = msg.text[0:len(msg.text) - 2]
    database.updateMenInfo(name)
    bot.send_message(msg.chat.id, f'{name} месяц был обновлен')
    return adminCmd(msg)


def adminCan(msg):
    if msg.text == 'Принять':
        bot.send_message(msg.chat.id, 'Кандидаты', reply_markup=adminCanButtons())
        bot.register_next_step_handler(msg, acceptCan)
    elif msg.text == 'Отклонить':
        bot.send_message(msg.chat.id, 'Кандидаты', reply_markup=adminCanButtons())
        bot.register_next_step_handler(msg, declineCan)
    elif msg.text == 'Cancel':
        return adminCmd(msg)
    else:
        bot.send_message(msg.chat.id, 'Ошибка', reply_markup=adminCanComButtons())
        bot.register_next_step_handler(msg, adminCan)


def acceptCan(msg):
    if msg.text == 'Cancel':
        return adminCmd(msg)
    name = msg.text[0:len(msg.text) - 2]
    candidate = database.getCandidate(name)
    database.deleteCanInfo(name)
    database.insertMenInfo(candidate[0], candidate[1], candidate[2])
    bot.send_message(msg.chat.id, f'{name} был принят')
    return adminCmd(msg)


def declineCan(msg):
    if msg.text == 'Cancel':
        return adminCmd(msg)
    name = msg.text[0:len(msg.text) - 2]
    database.deleteCanInfo(name)
    bot.send_message(msg.chat.id, f'{name} был отклонён')
    return adminCmd(msg)


def adminButtons():
    markup = ReplyKeyboardMarkup()
    markup.row_width = 2
    markup.one_time_keyboard = True
    markup.resize_keyboard = True
    markup.add(KeyboardButton('Менторы'),
               KeyboardButton('Кандидаты'),
               KeyboardButton('Мониторинг'),
               KeyboardButton('Exit'))
    return markup


def adminMenComButtons():
    markup = ReplyKeyboardMarkup()
    markup.row_width = 2
    markup.one_time_keyboard = True
    markup.resize_keyboard = True
    markup.add(KeyboardButton('Удалить'),
               KeyboardButton('Обновить месяц'),
               KeyboardButton('Cancel'),)
    return markup


def adminCanComButtons():
    markup = ReplyKeyboardMarkup()
    markup.row_width = 2
    markup.one_time_keyboard = True
    markup.resize_keyboard = True
    markup.add(KeyboardButton('Принять'),
               KeyboardButton('Отклонить'),
               KeyboardButton('Cancel'),)
    return markup


def adminCanButtons():
    candidates = database.getCanInfo()
    markup = ReplyKeyboardMarkup()
    markup.row_width = 5
    markup.one_time_keyboard = True
    markup.resize_keyboard = True
    for el in candidates:
        markup.add(KeyboardButton(f'{el[0]} {el[2]}'))
    markup.add(KeyboardButton('Cancel'))
    return markup


def adminMenButtons():
    mentors = database.getMenInfo()
    markup = ReplyKeyboardMarkup()
    markup.row_width = 5
    markup.one_time_keyboard = True
    markup.resize_keyboard = True
    for el in mentors:
        markup.add(KeyboardButton(f'{el[0]} {el[2]}'))
    markup.add(KeyboardButton('Cancel'))
    return markup


# candidate
candidate = []


@bot.message_handler(commands=['candidate'])
def candidateCmd(msg):
    bot.delete_message(msg.chat.id, msg.id)
    status = 1
    candidates = database.getCanInfo()
    mentors = database.getMenInfo()
    txt = ''
    if candidates:
        for el in candidates:
            if str(msg.chat.id) == el[1]:
                status = 0
                txt = 'кандидатом'

    if mentors:
        for el in mentors:
            if str(msg.chat.id) == el[1]:
                status = 0
                txt = 'ментором'

    if status:
        candidate.append(['name', msg.chat.id, 'month'])

        bot.send_message(msg.chat.id, 'Пример: "AzatSun", без ковычек\nВаше полное имя')
        bot.register_next_step_handler(msg, candidateGetName)
    else:
        bot.send_message(msg.chat.id, f'Вы уже являетесь {txt}')


def candidateGetName(msg):
    bot.send_message(msg.chat.id, 'От 1 до 6\nПример: "4"\n6 - Выпускник\nВаш месяц обучения')
    candidate[getCanIteration(msg)][0] = msg.text
    bot.register_next_step_handler(msg, candidateGetMonth)


def candidateGetMonth(msg):
    if msg.text in ['1', '2', '3', '4', '5', '6']:
        bot.send_message(msg.chat.id, 'Ожидайте решение Старшего ментора')
        candidate[getCanIteration(msg)][2] = msg.text
        iteration = getCanIteration(msg)
        database.insertCanInfo(candidate[iteration][0], candidate[iteration][1], candidate[iteration][2])
    else:
        bot.send_message(msg.chat.id, 'От 1 до 6\nПример: "4"\nВаш месяц обучения')
        candidateGetMonth(msg)


def getCanIteration(msg):
    candidateIteration = 0
    while True:
        if candidate[candidateIteration][1] == msg.chat.id:
            break
        else:
            candidateIteration += 1
    return candidateIteration


@bot.message_handler(commands=['mentor'])
def mentorCmd(msg):
    bot.delete_message(msg.chat.id, msg.id)
    status = 0
    mentors = database.getMenInfo()
    for el in mentors:
        if str(msg.chat.id) == el[1]:
            status = 1

    if status:
        bot.send_message(msg.chat.id, 'Панель управления', reply_markup=mentorMenuButtons())
        bot.register_next_step_handler(msg, mentorMenu)
    else:
        bot.send_message(msg.chat.id, 'You dont have permission')


def mentorMenu(msg):
    if msg.text == 'Получить таск':
        mentorGetTask(msg)
    elif msg.text == 'Очистить таски':
        mentorClearTask(msg)
    elif msg.text == 'Exit':
        pass


def mentorClearTask(msg):
    for el in mentorsForTask:
        if el[0] == msg.chat.id:
            mentorsForTask.remove(el)
    for el in mentorsForTask:
        if el[0] == msg.chat.id:
            mentorsForTask.remove(el)


def mentorGetTask(msg):
    bot.send_message(msg.chat.id, 'В каком формате вы хотите получить таск', reply_markup=mentorFormatButtons())
    bot.register_next_step_handler(msg, mentorFormat)


def mentorFormat(msg):
    if msg.text in ['Онлайн', 'Оффлайн']:
        status = 1
        if tasks:
            menMonth = database.getMenMonth(str(msg.chat.id))
            for el in tasks:
                if int(menMonth) > int(el[1]):
                    if msg.text == el[2]:
                        bot.send_message(msg.chat.id, el[0])
                        tasks.remove(el)
                        status = 0
                        break
            if status:
                if [msg.chat.id, msg.text] not in mentorsForTask:
                    mentorsForTask.append([msg.chat.id, msg.text])
                    bot.send_message(msg.chat.id, 'Ожидайте подходящий для вас таск')
                else:
                    bot.send_message(msg.chat.id, 'Вы уже в очереди для получения таска')

        else:
            if [msg.chat.id, msg.text] not in mentorsForTask:
                mentorsForTask.append([msg.chat.id, msg.text])
                bot.send_message(msg.chat.id, 'Ожидайте подходящий для вас таск')
            else:
                bot.send_message(msg.chat.id, 'Вы уже в очереди для получения таска')
    else:
        bot.send_message(msg.chat.id, 'error')
        mentorGetTask(msg)


def mentorMenuButtons():
    markup = ReplyKeyboardMarkup()
    markup.row_width = 2
    markup.one_time_keyboard = True
    markup.resize_keyboard = True
    markup.add(KeyboardButton('Получить таск'),
               KeyboardButton('Очистить таски'),
               KeyboardButton('Exit'), )
    return markup


def mentorFormatButtons():
    markup = ReplyKeyboardMarkup()
    markup.row_width = 2
    markup.one_time_keyboard = True
    markup.resize_keyboard = True
    markup.add(KeyboardButton('Онлайн'),
               KeyboardButton('Оффлайн'),
               KeyboardButton('Exit'), )
    return markup


@bot.message_handler(commands=['check'])
def check():
    print(tasks)
    print(mentorsForTask)


@bot.message_handler(content_types=['text'])
def deleteNewMessage(msg):
    bot.delete_message(msg.chat.id, msg.id)


if __name__ == '__main__':
    bot.polling(non_stop=True)
