import telegram
import logging
import configparser
from telegram import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters
from models.User import User
# adskyiproger token:
TOKEN='1047778864:AAHhfMlfhTKtCIwleg9rB-gRmjbmlmpXvdA'

bot = telegram.Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Read configuration file
config = configparser.ConfigParser()
config.read('settings.ini')


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

ACTIVE_USERS={}

print(bot.get_me())

def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu

# Bot commands:
# /start
def start(update, context):
    chat_id=update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text='<b>bold</b> <i>italic</i> <a href="http://google.com">link</a>.', 
                 parse_mode=telegram.ParseMode.HTML)
    logging.info(update.effective_chat)
    custom_keyboard = [ config['DEFAULT']['CATEGORIES'].split(",") ]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    print(reply_markup)
    #reply_markup = telegram.InlineKeyboardMarkup(build_menu(custom_keyboard, n_cols=2 ))
    #print(custom_keyboard + "=" + config['DEFAULT']['CATEGORIES'])
    context.bot.send_message(chat_id=chat_id,
                 text=config['DEFAULT']['CATEGORY_MENU_HEADER'],
                 reply_markup=reply_markup)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

# /do_suicide
def do_suicide(update,context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I do not want to die, but if you really ask me, I will do that. Bye!!!!")
    updater.stop()

stop_handler = CommandHandler('do_suicide', do_suicide)
dispatcher.add_handler(stop_handler)


# echo: This is main handler, but all Logic is hidden behind the Model class
def echo(update, context):
    
    chat_id=update.effective_chat.id
    
    if chat_id in ACTIVE_USERS.keys():
        MESSAGE="Welcome back "+ACTIVE_USERS[chat_id].name
        if ACTIVE_USERS[chat_id].isModel():
            MODEL=ACTIVE_USERS[chat_id].getModel()
            MESSAGE=MODEL.getMessage()   
        else:
            try:
                print(update.message.text)
                MODEL=Model(update.message.text)
            except:
                print("Unknown Model")


    else:
        MESSAGE="Please write '/start' in chat window to begin dialog"
        ACTIVE_USERS[chat_id]=User(chat_id,update.effective_chat.first_name)

    reply_markup = telegram.ReplyKeyboardRemove()
    context.bot.send_message(chat_id=chat_id, text="I'm back.", reply_markup=reply_markup)
    print(ACTIVE_USERS[chat_id].name)
    context.bot.send_message(chat_id=chat_id, text=MESSAGE)

echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)

# small class 
def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)





updater.start_polling()
