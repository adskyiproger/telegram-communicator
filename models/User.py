import logging
class User:

    model="NA"
    model_state=-1

    def __init__(self, uid, name=None):
       self.uid=uid
       self.name=name
       logging.info("User(): initialized: "+str(uid)+" name: "+name)

    def __eq__(self,other):
       if not isinstance(other, User):
           return NotImplemented
       return self.uid == other.uid 

    def isModel(self):
       if self.model != "NA":
           return True
       else:
           return False
    def getName(self):
        return self.name

    def getModel(self):
       return self.model

    def setModel(self,model):
       self.model=model

