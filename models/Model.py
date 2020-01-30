import configparser
import logging
import os.path
import re
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

class Model:
    STATE=-1
    name="Generic"
    TREE = configparser.ConfigParser()
    SECTIONS=[]
    ANSWERS=[]

    def verifyAnswer(self,answer):
        
        CURRENT_QUESTION=self.TREE[self.SECTIONS[self.STATE]]
        logging.info("verifyAnswer(): Q: "+CURRENT_QUESTION['question'])
        logging.info("verifyAnswer(): A: "+answer)
        # Check if answer match acceptable answers
        if re.match(CURRENT_QUESTION['answer'],answer) is not None:
            ans={ 'answer':answer,
                  'question':CURRENT_QUESTION['question']
                    }
            self.ANSWERS.append(ans)
            # Check if answer is last question in questionary
            if CURRENT_QUESTION['next_question'] == "finish":
                logging.info("verifyAnswer(): This is last question from the list" )
                self.STATE=0
            # Check if answer is CHOISE type    
            elif len(CURRENT_QUESTION['answer'].split("|")) > 1:
                next_q_ind=CURRENT_QUESTION['answer'].split("|").index(answer)
                next_q=CURRENT_QUESTION['next_question'].split("|")[next_q_ind]
                # Is choise not set to last question?
                if next_q != "finish":
                    logging.info("verifyAnswer(): Next section: "+self.SECTIONS[self.STATE]+" --> "+next_q )
                    self.STATE=self.SECTIONS.index(next_q)
                # Is choise set to last question
                elif next_q == "finish":
                    logging.info("verifyAnswer(): Questionary completed. Reached finish." )
                    self.STATE=0
                else:
                    logging.warning("verifyAnswer(): Something went wrong: Q: "+ans['question']+" A:"+ans['answer'])
            else:
                logging.info("verifyAnswer(): Next section: "+self.SECTIONS[self.STATE]+" --> "+self.SECTIONS[self.STATE+1])
                self.STATE += 1
            return True    
        else:
            return None

    def processQuestion(self,answer):
        if self.STATE == -1:
            self.STATE=1
            logging.info("processQuestion(): Initial question "+self.TREE[self.SECTIONS[1]]['question'])
            return(self.TREE[self.SECTIONS[1]]['question'])       
        elif self.STATE >= 0:
            if self.verifyAnswer(answer) is not None:
                if self.STATE==0:
                    return self.TREE['generic']['last_message']
                    
                else:
                    return self.TREE[self.SECTIONS[self.STATE]]['question']
            else:   
                logging.warning("Answer is not correct: "+answer)
                return self.TREE[self.SECTIONS[self.STATE]]['question']
            
    def getMarkup(self):
        try:
            if len(self.TREE[self.SECTIONS[self.STATE]]['answer'].split("|")) > 1 and self.STATE != 0:
                logging.info("getMarkup(): answer: "+self.TREE[self.SECTIONS[self.STATE]]['answer'])
                keyboard=[]
                for key in self.TREE[self.SECTIONS[self.STATE]]['answer'].split("|"):
                    keyboard.append(InlineKeyboardButton(key, callback_data=key))

                return InlineKeyboardMarkup([ keyboard ])
            else:
                return telegram.ReplyKeyboardRemove()
        except:
            return telegram.ReplyKeyboardRemove()

    def getName(self):
        return self.name

    def getAnswers(self):
        str1=""
        for el in self.ANSWERS:
            str1+=el['question']+":"+el['answer']+"\n"

        logging.debug("getAnswers(): Answers list:"+str1)
        return self.ANSWERS
    def getStatus(self):
        return self.STATE

    def loadModel(self):
        self.TREE.read(self.model_config)
        self.SECTIONS=self.TREE.sections()
        logging.info("loadModel(): "+self.name+" ("+self.TREE['generic']['name']+") from file: "+self.model_config)

    def __init__(self, model_name):
        logging.info("Model(): initialization: "+model_name)
        self.name=model_name
        self.model_config=self.name+"_model.ini"

        logging.debug("init(): clear list")
        self.ANSWERS.clear()
        if os.path.isfile(self.model_config):
            self.loadModel()
        else:
            logging.error("init(): Model file "+self.model_config+" doesn't exist.")
            raise Exception("Passed wrong model name: "+self.name)

       
