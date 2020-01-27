class User:

    model="NA"
    model_state=-1

    def __init__(self, uid, name=None):
       self.uid=uid
       self.name=name

    def __eq__(self,other):
       if not isinstance(other, User):
           return NotImplemented
       return self.uid == other.uid 

    def isModel(self):
       if self.model != "NA":
           return True
       else:
           return False

    def getModel(self):
       return self.model

    def getModelState(self):
       return self.model_state

