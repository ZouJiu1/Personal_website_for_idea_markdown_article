import os
import time
import json
import shutil
# from threading import Thread
from datetime import datetime

nowpath = os.path.abspath(__file__ + "/../../")

def getdate():
    postDa = datetime.fromtimestamp(time.time()).isoformat()[:19]
    postDate = postDa.replace("T", " ")
    hour = postDa.split("T")[1][:2]
    return int(hour), postDate

def write():
    global nowpath
    if not nowpath:
        nowpath = os.path.abspath(__file__ + "/../../")
    hour, date = getdate()
    jsonfile = os.path.join(nowpath, 'ip.json')
    
    savepath = os.path.join(nowpath, 'number', 'old')
    if not os.path.exists(savepath):
        os.mkdir(savepath)

    if os.path.exists(jsonfile) and os.path.getsize(jsonfile)!=0:
        shutil.move(jsonfile, os.path.join(savepath, f'ip_{date}.json'))
    with open(jsonfile, 'w', encoding='utf-8') as obj:
        pass

def write_datetime():
    while True:
        time.sleep(3000)
        hour = 0
        # print(nowpath)
        try:
            hour, date = getdate()
        except Exception as el:
            print("getdate: ", el)
            pass
        # print(hour, date)
        if hour == 3:
            try:
                write()
            except Exception as e:
                print('write: ', e)
                pass

if __name__=="__main__":
    write_datetime()
