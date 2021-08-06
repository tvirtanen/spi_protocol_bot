import config
import telebot
import logging
import time
import threading
import sys
import pickle
import db
import db_tracker
from db_tracker import TrackerDB


bot = telebot.TeleBot(config.token)
time_last = (time.process_time())
user_list = db.dictDB()
user_list_old = db.dictDB()
tracker_list = db_tracker.dictTrackerDB()
tracker_list_old = db_tracker.dictTrackerDB()


bot_logger = logging.getLogger('BotLogger')
bot_logger.setLevel(logging.DEBUG) # or whatever
handler = logging.FileHandler('bot.log', 'a', 'utf-8') # or whatever
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s')) # or whatever
bot_logger.addHandler(handler)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
handler.setFormatter(formatter)
bot_logger.addHandler(handler)

def extract_arg(arg):
    return arg.split()[1:]

telebot.apihelper.READ_TIMEOUT = 5

def send_msg(msg_id, text):
    try:
        bot.send_message(msg_id, text)
    except Exception as e:
        logging.info(e)
        send_msg(msg_id, text)
        
@bot.message_handler(content_types=["voice"])
def processing_voice_message(message):
    if (message.chat.id in user_list.chatList):
        if user_list.chatList[message.chat.id].inProgress == 1:
            if not message.from_user.first_name in user_list.chatList[message.chat.id].ignoreList:
                if 'default' in user_list.chatList[message.chat.id].userDict:
                    user_list.chatList[message.chat.id].userDict.pop('default')
                time_last = user_list.chatList[message.chat.id].upd_user(message.from_user.first_name, time.time())
                if time_last == 0:
                    user_list.chatList[message.chat.id].idDict[message.from_user.first_name] = message.from_user.id
                    send_msg(message.chat.id, 'Это первое сообщение от '
                      + str(message.from_user.first_name)
                      + '. Я запомнил')
                    bot_logger.info('First message from ' + str(message.from_user.first_name))
                else:
                    #if(user_list.userDict[message.from_user.first_name] != 2):
                    send_msg(message.chat.id, 'Интервал между сообщениями '
                      + str(message.from_user.first_name)
                      + ' составляет '
                      + time.strftime('%H:%M:%S', time.gmtime(int(time_last))))
                    bot_logger.info('message from '+ str(message.from_user.first_name))
    
                    if time_last > user_list.chatList[message.chat.id].zombieTime:
                        send_msg(message.chat.id, '#alert Интервал между сообщениями '
                          + str(message.from_user.first_name)
                          + ' больше порогового значения'
                          + '. Рекомендовано исключение из чата')
                        bot_logger.info(str(message.from_user.first_name)+' is unreliable')
    
                            #user_list.userDict[message.from_user.first_name] = 2
                            #
                        if (user_list.chatList[message.chat.id].kicking_on):
                            try:
                                bot_logger.error('Trying to kick')
                                bot.kick_chat_member(user_list.chatList[message.chat.id].chat_id, user_list.chatList[message.chat.id].idDict[message.from_user.first_name])
                                user_list.chatList[message.chat.id].idDict.pop(message.from_user.first_name)
                                user_list.chatList[message.chat.id].userDict.pop(message.from_user.first_name)
                            except Exception:
                                bot_logger.error('Can\'t kick')
                    #else:
                    #    send_msg(user_list.chat_id, 'Внимание! '
                    #            + str(message.from_user.first_name)
                    #            + ' ненадежен и уже провалил проверку'
                    #            + '. Рекомендовано исключить его из чата



@bot.message_handler(commands=["game_on"])
def set_ref_time(message):
    if (not message.chat.id in user_list.chatList):
        #user_list.chatList[message.chat.id] = db.dictDB()
        user_list.chatList[message.chat.id] = db.TimeDB()
        user_list.chatList[message.chat.id].inProgress = 1
        send_msg(message.chat.id, '#begin Итак, время пошло. Удачной игры, я за вами наблюдаю!')
        user_list.chatList[message.chat.id].chat_id = message.chat.id
        bot_logger.info("message.chat.id is " + str(message.chat.id))
        bot_logger.info("Start observing")
    else:
        if user_list.chatList[message.chat.id].inProgress == 0:
            user_list.chatList[message.chat.id].inProgress = 1
            send_msg(message.chat.id, '#continue Снова наблюдать!')
            bot_logger.info("message.chat.id is " + str(message.chat.id))
            bot_logger.info("Continue observing")
        else:
            send_msg(message.chat.id, 'Я и так уже наблюдаю!')

#@bot.channel_post_handler(commands=["track_on"])
def set_tracker_time(message):
    if (not message.chat.id in tracker_list.chatList):
        tracker_list.chatList[message.chat.id] = db_tracker.TrackerDB();
        tracker_list.chatList[message.chat.id].inProgress = 1
        send_msg(message.chat.id, '#begin Слежу за трекером')
        send_msg(message.chat.id, "message.chat.id is " + str(message.chat.id))
        tracker_list.chatList[message.chat.id].chat_id = message.chat.id
        bot_logger.info("message.chat.id is " + str(message.chat.id))
        bot_logger.info("Start tracker observing")
    else:
        if tracker_list.chatList[message.chat.id].inProgress == 0:
            tracker_list.chatList[message.chat.id].inProgress = 1
            send_msg(message.chat.id, '#continue Продолжаю следить за трекером')
        else:
            send_msg(message.chat.id, 'Я и так уже слежу за трекером!')  
        
@bot.message_handler(commands=["set_chan_id"])
def set_chat_id(message):
    send_msg(message.chat.id, message.text)
    try:
        #msg_id = int(extract_arg(message.text))
        msg_id = int(message.text[13:])
      
        send_msg(message.chat.id, msg_id)
        
        if (msg_id in tracker_list.chatList):
            if(tracker_list.chatList[msg_id].inProgress == 1):
                tracker_list.chatList[msg_id].message_chat_id = message.chat.id
                send_msg(message.chat.id, '#set_id Теперь сообщения о трекере будут приходить сюда')
                send_msg(tracker_list.chatList[msg_id].chat_id, '#set_id Теперь есть куда сообщать об ошибках')
            else:
                send_msg(message.chat.id, '#set_id Увы, пока никто не следит за трекером')
        else:
            send_msg(message.chat.id, '#set_id Нет такого чата')
    except:
        send_msg(message.chat.id, '#set_id неправильно набран номер')
    
        
@bot.message_handler(commands = ["get_chat_id"])
def get_chat_id(message):
    send_msg(message.chat.id, "message.chat.id is " + str(message.chat.id))
           
#@bot.channel_post_handler(commands=["get_channel_id"])
def get_channel_id(message):
    send_msg(message.chat.id, "Channel ID is " + str(message.chat.id))
        
#@bot.channel_post_handler(commands=["set_alert_time"])
def set_alert_time(message):
    try:
        alert_time = int(message.text[16:])
        tracker_list.chatList[message.chat.id].alert_time = alert_time
        send_msg(message.chat.id, "Трекер поднимет тревогу через " + str(alert_time))
    except:
        send_msg(message.chat.id, "Что-то пошло не так")
                
@bot.message_handler(commands=["auto_kick_on"])
def set_kicking_on(message):
    #name = extract_arg(message.text)
    user_list.chatList[message.chat.id].kicking_on = 1
    send_msg(message.chat.id, 'Автоматическое удаление активировано')
   
    
@bot.message_handler(commands=["auto_kick_off"])
def set_kicking_off(message):
    #name = extract_arg(message.text)
    user_list.chatList[message.chat.id].kicking_on = 0
    send_msg(message.chat.id, 'Автоматическое удаление деактивировано')
    
@bot.message_handler(commands = ["ignore"])
def set_user_to_ignore(message):
    name = extract_arg(message.text)
    user_list.chatList[message.chat.id].ignoreList.append(name[0])
    send_msg(message.chat.id, 'Сообщения от пользователя ' + str(name[0]) + ' будут игнорироваться')
    
#@bot.channel_post_handler(content_types=["text"])
def processing_text_message(message):
    if (message.chat.id in tracker_list.chatList): 
        if (message.chat.id == tracker_list.chatList[message.chat.id].chat_id):
            #send_msg(message.chat.id, message.text)
            if message.text == 'Системы работают исправно':
                send_msg(message.chat.id, "точно-точно")
                if tracker_list.chatList[message.chat.id].inProgress == 1:
                    #if 'default' in tracker_list.userDict:
                    #    tracker_list.userDict.pop('default')
                    #time_last = tracker_list.upd_user(message.from_user.id, time.time())
                    time_last = tracker_list.chatList[message.chat.id].upd_user('default', time.time())
                    if tracker_list.chatList[message.chat.id].isInit == 0:
                        #tracker_list.idDict[message.from_user.first_name] = message.from_user.id
                        send_msg(message.chat.id, 'Это первое сообщение '
                          #+ str(message.from_user.first_name)
                          + '. Я запомнил')
                        bot_logger.info('First message from the tracker')
                        tracker_list.chatList[message.chat.id].isInit = 1

def comrades_checking():
    while True:
        for chatID in user_list.chatList:
            if (user_list.chatList[chatID].num > 0):
                bot_logger.info('comrades checking ')
                #print(threading.get_ident())
                for userName in user_list.chatList[chatID].userDict.keys():
                    if not userName in user_list.chatList[chatID].ignoreList:
                        comrad = bot.get_chat_member(user_list.chatList[chatID].chat_id, user_list.chatList[chatID].idDict[userName])
                        if comrad.status not in ['restricted', 'left', 'kicked']: 
                            time_last = user_list.chatList[chatID].check_user(userName, time.time())
                            
                            #debug
                            print ('time_last: ' + str(time_last))
                            print ('zombie_time: ' + str(user_list.chatList[chatID].zombieTime))
                            #debug
                            
                            #alert each hour after zombieTime
                            if time_last > user_list.chatList[chatID].zombieTime and time.strftime('%M', time.gmtime(int(time_last))) == '00':
                                send_msg(user_list.chatList[chatID].chat_id, '#alert '
                                    + str(userName)
                                    + ' молчит слишком долго: '
                                    + time.strftime(' %H:%M', time.gmtime(int(time_last)))
                                    + '. Рекомендовано исключение из чата')
                                bot_logger.info(str(userName) + ' is unreliable')
                                if (user_list.chatList[chatID].kicking_on):
                                    try:
                                        bot_logger.error('Trying to kick')
                                        bot.kick_chat_member(user_list.chatList[chatID].chat_id, user_list.chatList[chatID].idDict[userName])
                                        user_list.chatList[chatID].idDict.pop(userName)
                                        user_list.chatList[chatID].userDict.pop(userName)
                                    except Exception:
                                        bot_logger.error('Can\'t kick')
                            else:
                                
                                #debug
                                print ('silence_time: ' + str(time_last))
                                print ('threshold_time: ' + str(user_list.chatList[chatID].thresholdTime))
                                #debug
                                
                                
                                #warning each hour after thresholdTime                                           
                                if time_last >= user_list.chatList[chatID].thresholdTime and time.strftime('%M', time.gmtime(int(time_last))) == '00':
                                    st = ('#warning '
                                    + str(userName)
                                    + ' молчит уже'
                                    + time.strftime(' %H:%M', time.gmtime(int(time_last))))
                                    send_msg(user_list.chatList[chatID].chat_id, st)
                                    bot_logger.info(st)
        if (len(user_list.chatList) > 0):
            try:
                with open('user_list.db', 'wb') as f:
                    pickle.dump(user_list, f)
                    bot_logger.info('DB is updated')
            except FileNotFoundError:
                bot_logger.error('Can\'t save database to file')
        #else:
        #    bot_logger.info('there are no comrades for checking')
    
        #threading.Timer(59, comrades_checking).start()
        time.sleep(20)

def tracker_checking():
    for chatID in tracker_list.chatList:
        if (tracker_list.chatList[chatID].isInit == 1):
            bot_logger.info('tracker checking')
            for userName in tracker_list.chatList[chatID].userDict.keys():
                #tracker = bot.get_chat_member(tracker_list.chat_id, tracker_list.idDict[userName])
                #if tracker.status not in ['restricted', 'left', 'kicked']: 
                time_last = tracker_list.chatList[chatID].check_user(userName, time.time())
                if time_last > tracker_list.chatList[chatID].alert_time * 60:
                    send_msg(tracker_list.chatList[chatID].chat_id, '#alert '
                        + '@StanleyKint, @l_casey, @ToivoVirtanen'    
                        + ', проверьте трекер')
                    send_msg(tracker_list.chatList[chatID].message_chat_id, '#alert '
                        + '@StanleyKint, @l_casey, @ToivoVirtanen'    
                        + ', проверьте трекер')
                    bot_logger.info('Tracker is locked')
            try:
                with open('tracker_list.db', 'wb') as f:
                    pickle.dump(tracker_list, f)
                    bot_logger.info('Tracker DB is updated')
            except FileNotFoundError:
                bot_logger.error('Can\'t save tracker DB to file')
        else:
            bot_logger.info('tracking is disabled')

    threading.Timer(60, tracker_checking).start()



def db_restore():
    global user_list

    try:
        with open('user_list.db', 'rb') as f:
            user_list_old = pickle.load(f)
            user_list = user_list_old
            bot_logger.info(str(user_list))
    except FileNotFoundError:
        bot_logger.warning('Users DB not found')

def heartbeat():
    while True:
        print('watching ')
        time.sleep(10)
    #threading.Timer(100, heartbeat()).start()

    
     
if __name__ == '__main__':
    bot_logger.info("Bot is started")
    db_restore()
    tmr_comrades = threading.Thread(target = comrades_checking)
    tmr_comrades.start()
    
    tmr_heartbeat = threading.Thread(target = heartbeat)
    tmr_heartbeat.start()
    #heartbeat();
    
    #comrades_checking()
    #tracker_checking()
    
    while True:
        try:
            #bot.infinity_polling()
            bot.polling(none_stop=True)
        except Exception as e:
            bot_logger.error(e)
            time.sleep(15)
            try:
                tmr_comrades.cancel()
                print ('Comrades checking is disabled')
            except:
                print ('Comrades checking threat crashed. Trying to resume it.')
                #tmr_comrades.terminate()
                del (tmr_comrades)
                tmr_comrades = threading.Thread(target = comrades_checking)
                tmr_comrades.start()
                print ('Comrades checking thread resuming ')
            #del tmr_comrades
            #threading.Timer(9, comrades_checking).start()
            
             


