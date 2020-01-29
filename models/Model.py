import configparser
import logging
import os.path
import re
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

class Model:
    state=-1
    status=-1
    name="Generic"
    #script_path=SCRIPT_PATH
    TREE = configparser.ConfigParser()
    SECTIONS=[]
    ANSWERS=[]
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

    def verifyAnswer(self,answer):
        logging.info("Question: "+self.TREE[self.SECTIONS[self.state]]['question'])
        logging.info("Answer: "+answer)
        if re.match(self.TREE[self.SECTIONS[self.state]]['answer'],answer) is not None:
            ans={ 'answer':answer,
                  'question':self.TREE[self.SECTIONS[self.state]]['question']
                    }
            self.ANSWERS.append(ans)
            if self.TREE[self.SECTIONS[self.state]]['next_question'] == "finish":
                logging.info("This is last question from the list" )
                self.state=0
            elif len(self.TREE[self.SECTIONS[self.state]]['answer'].split("|")) > 1:
                a=self.TREE[self.SECTIONS[self.state]]['answer'].split("|")
                next_ind=a.index(answer)
                q=self.TREE[self.SECTIONS[self.state]]['next_question'].split("|")[next_ind]
                #state=self.SECTIONS.index(q)
                if q != "finish":
                    q=self.TREE[self.SECTIONS[self.state]]['next_question'].split("|")[next_ind]
                #state=self.SECTIONS.index(q)
                    logging.info("Question tree identified: "+self.SECTIONS[self.state]+" --> "+self.SECTIONS[self.state] )
                    self.state=self.SECTIONS.index(q)
                else:
                    logging.info("this is last question from the list" )
                    self.state=0
            else:
                logging.info("Doing increment.")
                self.state += 1
            return True    
        else:
            return None

    def processQuestion(self,answer):
        if self.state == -1:
            self.state=1
            logging.info("Question: "+self.TREE[self.SECTIONS[1]]['question'])
            return(self.TREE[self.SECTIONS[1]]['question'])       
        elif self.state >= 0:
            if self.verifyAnswer(answer) is not None:
                if self.state==0:
                    return self.TREE['generic']['last_message']
                    
                else:
                    return self.TREE[self.SECTIONS[self.state]]['question']
            else:   
                logging.info("Answer is not correct: "+answer)
                return self.TREE[self.SECTIONS[self.state]]['question']
            
    def getMarkup(self):
        try:
            logging.info("getMarkup(): answer: "+self.TREE[self.SECTIONS[self.state]]['answer'])
            if len(self.TREE[self.SECTIONS[self.state]]['answer'].split("|")) > 1 and self.state != 0:
                #custom_keyboard = [ self.TREE[self.SECTIONS[self.state]]['answer'].split("|")  ]
                #reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
                keyboard=[]
                for key in self.TREE[self.SECTIONS[self.state]]['answer'].split("|"):
                    keyboard.append(InlineKeyboardButton(key, callback_data=key))
                reply_markup=InlineKeyboardMarkup([ keyboard ])

                return reply_markup
            else:
                return telegram.ReplyKeyboardRemove()
        except:
            return telegram.ReplyKeyboardRemove()

    def getName(self):
        return self.name

    def getAnswers(self):
        return self.ANSWERS
    def getStatus(self):
        return self.state
    def loadModel(self):
        self.TREE.read(self.model_config)
        self.SECTIONS=self.TREE.sections()
        logging.info("Model "+self.name+" ("+self.TREE['generic']['name']+") from file: "+self.model_config)

    def __init__(self, model_name):
        logging.info("initialization")
        self.name=model_name
        self.model_config=self.name+"_model.ini"
        if os.path.isfile(self.model_config):
            self.loadModel()
        else:
            logging.error("Model file "+self.model_config+" doesn't exist.")
            raise Exception("Passed wrong model name: "+self.name)

       
