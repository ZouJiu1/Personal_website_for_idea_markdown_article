#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import time
import shutil
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from bs4 import BeautifulSoup as fbsp
import requests
import re as regular

timezone = 2 * 2 * 7200
kseamutex = {}

def combine_audio_video():
    path = os.path.abspath(__file__ + "/../../")
    path = os.path.join(path, 'hls')
    kk = []
    mpthree = {}
    mthreeueight = []
    for i in os.listdir(path):
        if '.m3u8' in i:
            mthreeueight.append(os.path.join(path, i))
        if '.ts' in i:
            kk.append(i)
        nth = os.path.join(path, i)
        if os.path.isdir(nth):
            tme = os.path.getmtime(nth)
            mpthree[i] = tme
    mpthree = sorted(mpthree.items(), key = lambda x:x[1], reverse=True)
    if len(mpthree) > 31:
        for i in mpthree[31:]:
            shutil.rmtree(os.path.join(path, i[0]))
    if len(kk)==0:
        return
    kk = sorted(kk.__iter__(), key = lambda k : int(k.split('-')[-1].split('.')[0]))
    dic = {}
    endtimekkk = os.path.getmtime(os.path.join(path, kk[-1]))
    endtimekkkfile = datetime.fromtimestamp(endtimekkk + timezone).isoformat()[:19].replace(":", "_")
    kpath = os.path.join(path, endtimekkkfile)
    if not os.path.exists(kpath):
        os.makedirs(kpath)
    for i in range(24):
        dic[i] = []
    for i in kk:
        ti = os.path.getmtime(os.path.join(path, i))
        tit = datetime.fromtimestamp(ti + timezone).isoformat()[:19].replace(":", "_").split("T")[-1]
        hour = int(tit[:2])
        dic[hour].append(i)
    for i in range(24):
        kk = dic[i]
        if len(kk)==0:
            continue
        kk = kk[:-1]
        fp = open(os.path.join(path, 'fil.txt'), 'w', encoding='utf-8')
        for i in kk:
            fp.write('file \''+i + "\'\n")
        fp.close()
        starttime = os.path.getmtime(os.path.join(path, kk[0]))
        endtime = os.path.getmtime(os.path.join(path, kk[-1]))
        
        starttime = datetime.fromtimestamp(starttime + timezone).isoformat()[:19].replace(":", "_")
        endtime = datetime.fromtimestamp(endtime + timezone).isoformat()[:19].replace(":", "_")

        name = starttime + "_" + endtime + ".mp3"
        
        # ffmpeg -f concat -safe 0 -i fil.txt -vn output.mp3
        # ffmpeg -f concat -safe 0 -i fil.txt  output.mp4
        siz = os.path.getsize(os.path.join(path, kk[0]))
        if siz < 300000:
            os.system(f"cd {kpath} && ffmpeg -f concat -safe 0 -i ../fil.txt -vn {name} -y")
        else:
            os.system(f"cd {kpath} && ffmpeg -f concat -safe 0 -i ../fil.txt {name} -y")
    for i in os.listdir(path):
        if '.ts' in i:
            os.remove(os.path.join(path, i))
    for i in mthreeueight:
        os.remove(i)

def getbingimg():
    path = os.path.abspath(__file__ + "/../../")
    path = os.path.join(path, 'article')
    ret = requests.get(r'https://cn.bing.com', headers= \
                       {"User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0', \
                        "Sec-Ch-Ua-Platform":"macOS"})
    con = ret.content
    parser = fbsp(con, "html.parser")
    meta = parser.find_all("meta")
    description = ""
    for i in meta:
        if 'property' in i.attrs.keys():
            property = i.attrs['property']
            if 'description' in property:
                description = i.attrs['content']
                with open(os.path.join(path, "everydayimg.txt"), 'w', encoding='utf-8') as obj:
                    obj.write(description + '\n')
                break

    findall = parser.find_all("div")
    for i in findall:
        if 'class' in i.attrs.keys():
            lan = i.attrs['class']
            if 'hp_top_cover' in lan:
                style = i.attrs['style']
                imglink = regular.findall(r'url\(\"(.*)\"\)', style)
                try:
                    response = requests.get(imglink[0], timeout=30)
                except:
                    try:
                        response = requests.get(imglink[0], timeout=30)
                    except:
                        break
                if response.status_code==200:
                    savepath = os.path.join(path, "everydayimg.png")
                    with open(savepath, 'wb') as obj:
                        obj.write(response.content)
                return 
    return 

def getdate():
    postDa = datetime.fromtimestamp(time.time() + timezone).isoformat()[:19]
    postDate = postDa.replace("T", " ")
    hour = postDa.split("T")[1][:2]
    return int(hour), postDate.replace(":", "_")

def write_password():
    nowpath = os.path.abspath(__file__ + "/../../../")
    hour, date = getdate()
    jsonfile = os.path.join(nowpath, 'article', 'ip.json')
    
    savepath = os.path.join(nowpath, 'article', 'number', 'old')
    if not os.path.exists(savepath):
        os.makedirs(savepath, exist_ok=True)

    if os.path.exists(jsonfile) and os.path.getsize(jsonfile)!=0:
        shutil.move(jsonfile, os.path.join(savepath, f'ip_{date}.json'))
    with open(jsonfile, 'w', encoding='utf-8') as obj:
        pass

def ontime_apscheduler():
    '''
    https://stackoverflow.com/questions/71058888/zoneinfonotfounderror-no-time-zone-found-with-key-utc
    import zoneinfo
    zoneinfo.available_timezones()
    '''
    trigger_write_password = CronTrigger(hour=3, timezone='Asia/Chongqing')
    trigger_getbingimg = CronTrigger(hour=1, timezone='Asia/Chongqing')
    trigger_combine_audio_video = CronTrigger(hour=9, timezone='Asia/Chongqing')
    # trigger_combine_audio_video = IntervalTrigger(seconds=3)
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        write_password,
        trigger_write_password,
        id="write_password",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        getbingimg,
        trigger_getbingimg,
        id="getbingimg",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        combine_audio_video,
        trigger_combine_audio_video,
        id="combine_audio_video",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.start()

def main():
    ontime_apscheduler()
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    # python manage.py startapp zhihu
    # python manage.py runserver localhost:7009
    # python3 manage.py runserver localhost:7009
    # getbingimg()
    main()
