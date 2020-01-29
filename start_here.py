import telegram
import logging
import configparser
from telegram import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from models.User import User
from models.Model import Model
# adskyiproger token:
TOKEN='1047778864:AAHhfMlfhTKtCIwleg9rB-gRmjbmlmpXvdA'

bot = telegram.Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Read configuration file
config = configparser.ConfigParser()
config.read('settings.ini')
categories=config['DEFAULT']['categories'].split(",")
models=config['DEFAULT']['models'].split(",")
MODELS=dict(zip(models,categories))
keyboard=[]
for key in config['DEFAULT']['CATEGORIES'].split(","):
      keyboard.append(InlineKeyboardButton(key, callback_data=key))
      start_reply_markup=InlineKeyboardMarkup([ keyboard ])

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

def button(update, context):
    chat_id=update.effective_chat.id
    query = update.callback_query

    if chat_id in ACTIVE_USERS.keys() and ACTIVE_USERS[chat_id].isModel():
        MODEL=ACTIVE_USERS[chat_id].getModel()
        MESSAGE=ACTIVE_USERS[chat_id].getModel().processQuestion(query.data)
        REPLY_MARKUP=ACTIVE_USERS[chat_id].getModel().getMarkup()
        if ACTIVE_USERS[chat_id].getModel().getStatus() == 0:
             logging.info(ACTIVE_USERS[chat_id].getModel().getAnswers())
             #MESSAGE=ACTIVE_USERS[chat_id].getModel().getAnswers()
             ACTIVE_USERS[chat_id].setModel("NA")
             MESSAGE+=config['DEFAULT']['BYE_MESSAGE']
    elif chat_id in ACTIVE_USERS.keys():
        if query.data in categories:
            model=models[categories.index(query.data)]
            ACTIVE_USERS[chat_id].setModel(Model(model))
            MESSAGE=ACTIVE_USERS[chat_id].getModel().processQuestion(query.data)
            REPLY_MARKUP=ACTIVE_USERS[chat_id].getModel().getMarkup()
        else:
            MESSAGE=config['DEFAULT']['GREETING_WORD']+" "+ACTIVE_USERS[chat_id].getName()+"! "+config['DEFAULT']['WELCOME_MESSAGE']
            REPLY_MARKUP=start_reply_markup
    else:
        ACTIVE_USERS[chat_id]=User(chat_id,update.effective_chat.first_name)
        MESSAGE=config['DEFAULT']['GREETING_WORD']+" "+ACTIVE_USERS[chat_id].getName()+"! "+config['DEFAULT']['WELCOME_MESSAGE']
        REPLY_MARKUP=start_reply_markup
    query.edit_message_text(text=config['DEFAULT']['SELECTED_OPTION']+" {}".format(query.data))
    context.bot.send_message(chat_id=chat_id, text=MESSAGE, parse_mode=telegram.ParseMode.HTML,reply_markup=REPLY_MARKUP)
     

dispatcher.add_handler(CallbackQueryHandler(button))

# Bot commands:
# /start
def start(update, context):
    chat_id=update.effective_chat.id
    logging.info(update.effective_chat)
    print(reply_markup)
    context.bot.send_message(chat_id=chat_id,
                 text=config['DEFAULT']['CATEGORY_MENU_HEADER'],
                 reply_markup=reply_markup)

    ACTIVE_USERS[chat_id]=User(chat_id,update.effective_chat.first_name)
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
    REPLY_MARKUP=telegram.ReplyKeyboardRemove()
    
    if chat_id in ACTIVE_USERS.keys() and ACTIVE_USERS[chat_id].isModel():
        MODEL=ACTIVE_USERS[chat_id].getModel()
        MESSAGE=MODEL.processQuestion(update.message.text)
        REPLY_MARKUP=ACTIVE_USERS[chat_id].getModel().getMarkup()
        if ACTIVE_USERS[chat_id].getModel().getStatus() == 0:
             logging.info(ACTIVE_USERS[chat_id].getModel().getAnswers())
             #MESSAGE=ACTIVE_USERS[chat_id].getModel().getAnswers()
             ACTIVE_USERS[chat_id].setModel("NA")
             MESSAGE+=config['DEFAULT']['BYE_MESSAGE']
    elif chat_id in ACTIVE_USERS.keys():
        if update.message.text in categories:
            model=models[categories.index(update.message.text)]
            ACTIVE_USERS[chat_id].setModel(Model(model))
            MESSAGE=ACTIVE_USERS[chat_id].getModel().processQuestion(update.message.text)
        else:
            MESSAGE=config['DEFAULT']['GREETING_WORD']+" "+ACTIVE_USERS[chat_id].getName()+"! "+config['DEFAULT']['WELCOME_MESSAGE']
            REPLY_MARKUP=start_reply_markup
    else:
        ACTIVE_USERS[chat_id]=User(chat_id,update.effective_chat.first_name)
        MESSAGE=config['DEFAULT']['GREETING_WORD']+" "+ACTIVE_USERS[chat_id].getName()+"! "+config['DEFAULT']['WELCOME_MESSAGE']
        REPLY_MARKUP=start_reply_markup

    context.bot.send_message(chat_id=chat_id, text=MESSAGE, parse_mode=telegram.ParseMode.HTML,reply_markup=REPLY_MARKUP)

echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)

# small class 
def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)





updater.start_polling()
