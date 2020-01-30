import telegram
import logging
import configparser
from telegram import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from models.User import User
from models.Model import Model
# Read configuration file
config = configparser.ConfigParser()
config.read('settings.ini')

# Setup logger:
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.DEBUG,
                     filename=config['DEFAULT']['LOG_FILE'],
                     filemode='w')


# Register token:
TOKEN=config['DEFAULT']['TOKEN']

bot = telegram.Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Create models to categories relation:
categories=config['DEFAULT']['categories'].split(",")
models=config['DEFAULT']['models'].split(",")
MODELS=dict(zip(models,categories))

# Define initial branches:
keyboard=[]
for key in config['DEFAULT']['CATEGORIES'].split(","):
      keyboard.append(InlineKeyboardButton(key, callback_data=key))
      start_reply_markup=InlineKeyboardMarkup([ keyboard ])


# Dictionary for active users: Store users answers and data
ACTIVE_USERS={}


logging.info("Bot initialized: "+str(bot.get_me()))

# Forward Answers to ADMIN_USERs:
def saveAnswers(update,context,answers):
    user_report=config['DEFAULT']['REPORT_HEADER']+"\n"
    admin_report=config['DEFAULT']['ADMIN_REPORT_HEADER']+" "+str(update.effective_chat.first_name)+"("+str(update.effective_chat.id)+")\n"
    report=""
    for ii in answers:
        report+="<b>"+ii['question']+"</b> "+ii['answer']+"\n"

    logging.debug("Report sent to used: "+str(update.effective_chat.id))
    context.bot.send_message(chat_id=update.effective_chat.id, text=user_report+report, parse_mode=telegram.ParseMode.HTML)
    for ID in config['DEFAULT']['ADMIN_USER_IDS'].split(","):
        context.bot.send_message(chat_id=int(ID), text=admin_report+report, parse_mode=telegram.ParseMode.HTML)

# TBD: this function is not working
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


# Telegram functions implementation:

# Bot commands:
# /do_suicide
def do_suicide(update,context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I do not want to die, but if you really ask me, I will do that. Bye!!!!")
    updater.stop()

dispatcher.add_handler( CommandHandler('do_suicide', do_suicide) )

# /unknown command processor:
def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

dispatcher.add_handler(MessageHandler(Filters.command, unknown))

# Process Inline Buttons:
def button(update, context):
    chat_id=update.effective_chat.id
    query = update.callback_query

    if chat_id in ACTIVE_USERS.keys() and ACTIVE_USERS[chat_id].isModel():
        MODEL=ACTIVE_USERS[chat_id].getModel()
        MESSAGE=ACTIVE_USERS[chat_id].getModel().processQuestion(query.data)
        REPLY_MARKUP=ACTIVE_USERS[chat_id].getModel().getMarkup()
        if ACTIVE_USERS[chat_id].getModel().getStatus() == 0:
             saveAnswers(update,context,ACTIVE_USERS[chat_id].getModel().getAnswers())
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

# Process text responses
def echo(update, context):
    
    chat_id=update.effective_chat.id
    REPLY_MARKUP=telegram.ReplyKeyboardRemove()
    
    if chat_id in ACTIVE_USERS.keys() and ACTIVE_USERS[chat_id].isModel():
        MODEL=ACTIVE_USERS[chat_id].getModel()
        MESSAGE=MODEL.processQuestion(update.message.text)
        REPLY_MARKUP=ACTIVE_USERS[chat_id].getModel().getMarkup()
        if ACTIVE_USERS[chat_id].getModel().getStatus() == 0:
             saveAnswers(update,context,ACTIVE_USERS[chat_id].getModel().getAnswers())
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

dispatcher.add_handler(MessageHandler(Filters.text, echo))

updater.start_polling()
