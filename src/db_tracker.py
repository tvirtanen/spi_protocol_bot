import time

class TrackerDB:
    def __init__(self):
        self.time_ = time.time()
        self.num = 0
        self.names = []
        self.userDict = {'default': 0}
        self.idDict = {'default': 0}
        self.inProgress = 0
        self.alert_time = 60
        self.isInit = 0;
        self.chat_id = 0;
        self.message_chat_id = 0;
        
    def set_time(self, t):
        self.time_ = t
        
    def get_time(self):
        return self.time_

    def upd_user(self, userName, userTime):
        if userName in self.userDict:
            t = self.userDict[userName]
            self.userDict[userName] = userTime
            return  userTime - t
            
        else:
            self.userDict[userName] = userTime
            self.num += 1
            return 0  

    def check_user(self, userName, userTime):
        if userName in self.userDict:
            t = self.userDict[userName]
            return  userTime - t
        else:
            return 0    
        
        
        
class dictTrackerDB:
    def __init__(self):
        #self.chatList[Dict[int, TimeDB]] = {};
        self.chatList = {};