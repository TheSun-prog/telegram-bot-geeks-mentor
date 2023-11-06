import telebot
import config

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def start(msg):
    bot.register_next_step_handler(msg, cont(msg, 123, 'asd'))


def cont(msg, id, task):
    print(msg.text, id, task)


bot.polling(none_stop=True)
