import configparser
import logging
import os.path
import re
class Model:
    state=-1
    name="Generic"
    #script_path=SCRIPT_PATH
    TREE = configparser.ConfigParser()
    SECTIONS=[]
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

    def verifyAnswer(self,answer):
        if re.match(self.TREE[self.SECTIONS[self.state]]['answer'],answer) is not None:
            logging.info("Previous question: "+self.TREE[self.SECTIONS[self.state]]['question'])
            logging.info("Accepted answer: "+self.TREE[self.SECTIONS[self.state]]['question'])
            if self.TREE[self.SECTIONS[self.state]]['next_question'] == "finish":
                logging.info("This is last question from the list" )
                self.state=0
            elif len(self.TREE[self.SECTIONS[self.state]]['answer'].split("|")) > 1:
                a=self.TREE[self.SECTIONS[self.state]]['answer'].split("|")
                next_ind=a.index(answer)
                q=self.TREE[self.SECTIONS[self.state]]['next_question'].split("|")[next_ind]
                if q != "finish":
                    logging.info("Question tree identified: "+self.SECTIONS[self.state]+" --> "+self.SECTIONS[next_ind] )
                    self.state=self.SECTIONS.index(q)
                else:
                    logging.info("Question tree identified: "+self.SECTIONS[self.state]+" --> "+self.SECTIONS[next_ind] )
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
                    return "END"
                else:
                    return self.TREE[self.SECTIONS[self.state]]['question']
            else:   
                logging.info("Answer is not correct: "+answer)
                return self.TREE[self.SECTIONS[self.state]]['question']
            
    def getState(self):
        return self.state

    def getName(self):
        return self.name

    def getMessage(self):
        message=self.message
        return message

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

       
