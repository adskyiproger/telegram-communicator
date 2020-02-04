import telegram
import logging
import logging.handlers
import sys

import configparser
from telegram import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from models.User import User
from models.Model import Model
# Read configuration file
config = configparser.ConfigParser()
config.read('conf/settings.ini')

# Setup logger:
logging.basicConfig(
                format = '[%(asctime)s] [%(levelname)s]: %(message)s',
                level = logging.INFO,
                handlers = [
                    logging.handlers.RotatingFileHandler(
                                        filename = config['DEFAULT']['LOG_FILE'],
                                        maxBytes = (1048576*5),
                                        backupCount = 1,
                                        ),
                    logging.StreamHandler(sys.stdout)
                    ]
                )

# Register token:
TOKEN=config['DEFAULT']['TOKEN']

bot = telegram.Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


lang_keyboard=[]

for key in config.sections():
      lang_keyboard.append(InlineKeyboardButton(key, callback_data=key))

lang_reply_markup=InlineKeyboardMarkup([ lang_keyboard ])

# Dictionary for active users: Store users answers and data
ACTIVE_USERS={}


logging.info("Bot initialized: "+str(bot.get_me()))


def start_reply_markup(user_lang):
    # Create models to categories relation:
    logging.info("start_reply_markup(): Render categories for language: "+user_lang)
    categories=config[user_lang]['categories'].split(",")
    models=config[user_lang]['models'].split(",")
    MODELS=dict(zip(models,categories))

    # Define initial branches:
    keyboard=[]
    for key in config[user_lang]['CATEGORIES'].split(","):
        keyboard.append(InlineKeyboardButton(key, callback_data=key))

    return InlineKeyboardMarkup([ keyboard ])



# processUserResponse(): Call upper datamodel and get answer:
def processUserResponse(update,context,user_msg):
    REPLY_MARKUP=telegram.ReplyKeyboardRemove()
    chat_id=update.effective_chat.id

    # Initiate new user object
    if chat_id not in ACTIVE_USERS:
        ACTIVE_USERS[chat_id]=User(chat_id,update.effective_chat.first_name)

    # Set user language
    if chat_id in ACTIVE_USERS.keys() and user_msg in config.sections() and ACTIVE_USERS[chat_id].getLang() == "DEFAULT":
        ACTIVE_USERS[chat_id].setLang(user_msg)
        
    # Set chat language
    user_lang=ACTIVE_USERS[chat_id].getLang()

    if user_lang == "DEFAULT" and len(config.sections()) > 1:
            REPLY_MARKUP=lang_reply_markup
            print(config.sections())
            MESSAGE=config['DEFAULT']['LANG_MESSAGE']
            REPLY_MARKUP=lang_reply_markup
    # If User questionary is already in process then process user response:
    elif chat_id in ACTIVE_USERS.keys() and ACTIVE_USERS[chat_id].isModel():
        MESSAGE=ACTIVE_USERS[chat_id].getModel().processQuestion(user_msg)
        REPLY_MARKUP=ACTIVE_USERS[chat_id].getModel().getMarkup()
        # If last question in the questionary:
        if ACTIVE_USERS[chat_id].getModel().getStatus() == 0:
             saveAnswers(update,context,ACTIVE_USERS[chat_id].getModel().getAnswers())
             ACTIVE_USERS[chat_id].setModel("NA")
             MESSAGE+=config[user_lang]['BYE_MESSAGE']
    # If User is in list, but have not started questionary:         
    # Initialize Questionary
    elif chat_id in ACTIVE_USERS.keys() and user_msg in config[user_lang]['categories'].split(","):
        ACTIVE_USERS[chat_id].setModel(Model(model_name=config[user_lang]['models'].split(",")[config[user_lang]['categories'].split(",").index(user_msg)],user_lang=user_lang))
        MESSAGE=ACTIVE_USERS[chat_id].getModel().processQuestion(user_msg)

    # Init new user        
    # Show greeting message one more time    
    else:
        REPLY_MARKUP=start_reply_markup(user_lang)
        MESSAGE=config[user_lang]['GREETING_WORD']+" " \
                +ACTIVE_USERS[chat_id].getName()+"! "+config[user_lang]['WELCOME_MESSAGE']

    context.bot.send_message(chat_id=chat_id, text=MESSAGE, parse_mode=telegram.ParseMode.HTML,reply_markup=REPLY_MARKUP)


# Forward Answers to ADMIN_USERs:
def saveAnswers(update,context,answers):
    
    user_lang=ACTIVE_USERS[update.effective_chat.id].getLang()
    user_report=config[user_lang]['REPORT_HEADER']+"\n"
    admin_report=config[user_lang]['ADMIN_REPORT_HEADER'] \
        +" "+str(update.effective_chat.first_name) \
        +" ("+str(update.effective_chat.id)+")\n"
    report=""
    for ii in answers:
        report+="<b>"+ii['question']+"</b> "+ii['answer']+"\n"

    logging.debug("Report sent to used: "+str(update.effective_chat.id))
    
    context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=user_report+report,
            parse_mode=telegram.ParseMode.HTML)

    for ID in config[user_lang]['ADMIN_USER_IDS'].split(","):
        context.bot.send_message(chat_id=int(ID),
                text=admin_report+report,
                parse_mode=telegram.ParseMode.HTML)

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
    context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="I do not want to die, but if you really ask me, I will do that. Bye!!!!")
    updater.stop()

dispatcher.add_handler( CommandHandler('do_suicide', do_suicide) )

# /unknown command processor:
def unknown(update, context):
    context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="Sorry, I didn't understand that command.")

dispatcher.add_handler(MessageHandler(Filters.command, unknown))

# Process Inline Buttons:
def button(update, context):
    user_lang=ACTIVE_USERS[update.effective_chat.id].getLang()
    query = update.callback_query
    query.edit_message_text(
            text=config[user_lang]['SELECTED_OPTION']+" {}"
                   .format(query.data))
    processUserResponse(update, context, query.data)

dispatcher.add_handler(CallbackQueryHandler(button))

# Process Text responses:
def echo(update, context):
    processUserResponse(update, context, update.message.text)

dispatcher.add_handler(MessageHandler(Filters.text, echo))

updater.start_polling()
