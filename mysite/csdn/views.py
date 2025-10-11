from django.http import HttpResponse
# from rest_framework.response import Response
# from rest_framework import status
from django.http import JsonResponse
import os
from datetime import datetime
import markdown2
import time
import re as regular
import json
import shutil
import numpy as np
path = os.path.abspath(__file__ + "/../../../article/csdn_spider_selenium/article")
addpath = os.path.abspath(__file__ + "/../../")
mainpath = os.path.abspath(__file__ + "/../../../dist/article")
if os.path.exists(mainpath):
    path = path.replace("/article/", '/dist/article/')
# addpath = addpath.replace("/article/", '/dist/article/')
import sys
sys.path.append(addpath)
sys.path.append(os.path.abspath(__file__ + "/../../"))
from manage import timezone, kseamutex
from markdown_detail.views import remove_code, addback_code, remove_katex, addback_katex
# from commonuse.views import parseTxt
from django.views.decorators.csrf import csrf_exempt
from copy import deepcopy
import json
import hashlib
import smtplib
from email.message import EmailMessage
from PIL import Image
from threading import Semaphore

def rep(i):
    return i.replace(":", "_").replace("_问号_", "？").replace("_感叹号_", "！").replace("-感叹号-", "！").\
              replace("小于", "<").replace("大于", ">").replace("_逗号_", "，").replace("-逗号-", "，").\
              replace("_空格_", " ").replace("-空格-", " ").replace("_冒号_", "：").replace("-冒号-", "：").\
              replace("_顿号_", "、").replace("-顿号-", "、")

allfile = None
pre_page_size = None

def findlatest(pth):
    col = {}
    for j in os.listdir(pth):
        if '.md' in j:
            markdownpth = os.path.join(pth, j)
            mtme = os.path.getmtime(markdownpth)
            col[mtme] = markdownpth
    col = sorted(col.items(), key = lambda x:x[0], reverse = True)
    if len(col)==0:
        return ""
    return col[0][1]

def index(request):
    global allfile, kseamutex, path
    basepath = deepcopy(path)
    # https://docs.djangoproject.com/en/5.1/ref/request-response/#top
    # req = request.GET.dict()
    req = json.loads(request.body)
    try:
        try:
            currentpage = int(req["currentpage"])
        except:
            currentpage = 1
        try:
            pagesize = int(req["pagesize"])
        except:
            pagesize = 6
        search = req["search"]
        reset = int(req["reset"])
        checke = bool(int(req["checke"]))

        get = json.loads(getusername(request).content)
        # basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
        if get['ret'] > 0:
            basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")
        # if "mail" in req.keys():
            # if check_logined(req['mail'], req['password']):
            # basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
    except:
        return HttpResponse("<span style=\"color:#00ffe0;font-weight:600;font-size:30px;\"> \
            请访问然后点击左侧按钮: </span><a style=\"color:#0000ff;font-size:30px;\" \
                href=\"http://zoujiu.com.cn\">http://zoujiu.com.cn</a>")
        # currentpage = 1
        # pagesize = 20
        # search = ""
        # reset = 0
        # checke = True
    postDate = datetime.fromtimestamp(time.time() +timezone).isoformat()[:19].replace(":", "_")
    postDate = postDate.replace("T", " ")

    # reset = 1
    if reset==1:
        allfile = None
    collect = []
    search = search.split(" ")
    while '' in search:
        search.remove("")
    if allfile!=None:
        result_ret = allfile[(currentpage-1) * pagesize : currentpage * pagesize]
        if checke==False:
            ret = []
            for i in range(len(result_ret)):
                if 'leetcode' in result_ret[i]['title'].lower() or \
                    'pat' in result_ret[i]['title'].lower() or 'DP' in result_ret[i]['title']:
                    continue
                else:
                    ret.append(result_ret[i])
        else:
            ret = result_ret
        return JsonResponse({"collect":ret, "length":len(allfile)}, safe = False)

    # jsonfile = os.path.join(addpath, 'article', 'idtranslate.json')
    # with open(jsonfile, 'r', encoding='utf-8') as obj:
    #     jsonfp = json.loads(obj)
    # alldate = []
    for i in os.listdir(basepath):
        nth = os.path.join(basepath, i)
        if not os.path.isdir(nth):
            continue
        if '20'==i[:2]:
            date = rep(i[:22]).replace("_", ":")
            title = rep(i[23:])
        else:
            date = postDate
            title = rep(i)
    #     alldate.append([date, nth, title])
    # alldate = sorted(alldate.__iter__(), key = lambda x:x[0], reverse = True)

        lower_title = title.lower()
        if checke==False and ('leetcode' in lower_title or 'pat' in lower_title or 'DP' in title):
            continue
            
        markdown = "# no content\n# no content\n# no content\n"
        markdownpth = findlatest(nth)
        createFile = os.path.join(nth, "create.txt")
        if os.path.exists(createFile) and os.path.getsize(createFile) > 60 and "20" == i[:2] and int(i[:4]) > 2024 and int(i[4+1:4+3]) > 4:
            modifyTime = os.path.getmtime(markdownpth)
            modifyTime = datetime.fromtimestamp(modifyTime).isoformat()[:19].replace("T", " ")                
        else:
            modifyTime = date
        upvotecomment = os.path.join(nth, 'upvote_comment.json')
        if not os.path.exists(upvotecomment):
            os.system(f"touch \"{upvotecomment}\"")
        upvote = []
        comment = []
        kshoucang = []
        click = False
        clickshoucang = False
        maillogin = '#'
        if 'mail' in req.keys():
            maillogin = req['mail']
        if len(markdownpth) > 0:
            with open(markdownpth, 'r', encoding = 'utf-8') as obj:
                markdown = obj.read().strip()
        else:
            markdownpth = os.path.join(nth, 'markdown.md')
            with open(markdownpth, 'w', encoding = 'utf-8') as obj:
                obj.write(markdown)
        find = False
        marked = -1
        # with open(file, 'w', encoding='utf-8') as obj:upvote_comment
        #     json.dump(Setting_Formel, obj, indent=2, ensure_ascii=False)
        tails = markdownpth.split(os.sep)[-1]
        if tails not in kseamutex.keys():
            kseamutex[tails] = Semaphore(value=1)
        kseamutex[tails].acquire()
        with open(upvotecomment, 'r', encoding='utf-8') as obj:
            try:
                jsonfile = json.load(obj)
            except:
                jsonfile = {"upvote":[], 'comment':[], 'kshoucang':[]}
                with open(upvotecomment, 'w', encoding='utf-8') as obj:
                    json.dump(jsonfile, obj, indent=2, ensure_ascii=False)
            if len(jsonfile)==0:
                pass
            else:
                upvote = jsonfile['upvote']
                comment = jsonfile['comment']
                try:
                    kshoucang = jsonfile['kshoucang']
                except:
                    jsonfile["kshoucang"] = []
                    with open(upvotecomment, 'w', encoding='utf-8') as obj:
                        json.dump(jsonfile, obj, indent=2, ensure_ascii=False)
                for ij in upvote:
                    if len(maillogin)!=1 and maillogin == ij:
                        click = True
                        break
                for ij in kshoucang:
                    if len(maillogin)!=1 and maillogin == ij:
                        clickshoucang = True
                        break
        kseamutex[tails].release()
        kseamutex.pop(tails)
            # for i in obj.readlines():
            #     i = i.strip()
            #     if len(i)==0:
            #         continue
            #     if '#######=[【)]!@#*34fdg12ddsaf[.,,;`,1278943523414547543523dsfadghtrgbuyiiphbg[;[.[,]]].23`af123^1$,./<>>?######' in i:
            #         marked = 1
            #     if marked < 0:
            #         if len(maillogin)!=1 and maillogin in i:
            #             click = True
            #         upvote.append(i)
            #     else:
            #         comment.append(i)
            #     marked += 1
        for j in search:
            if j in markdown or j in i or j.replace(":", "_") in i or  "文篇编辑功能展示" in title or "父母的体检报告出来了，身体毛病挺多的" in title:
                collect.append({"date":date.replace("_", ":"), "title": title, "markdown": markdown[:200], \
                                "path":markdownpth, "upvote":upvote, 'comment':comment, 'click':click, \
                                'clickshoucang':clickshoucang, 'kshoucang':kshoucang, "modifyTime":modifyTime})
                # find = True
                break
        if len(search)==0:
            collect.append({"date":date.replace("_", ":"), "title": title, "markdown": markdown[:200], \
                            "path":markdownpth, "upvote":upvote, 'comment':comment, 'click':click, \
                            'clickshoucang':clickshoucang, 'kshoucang':kshoucang, "modifyTime":modifyTime})

    collect = sorted(collect.__iter__(), key = lambda x:x['modifyTime'], reverse=True)
    tmp = ['a', 'c']
    for i, _ in enumerate(collect):
        if "文篇编辑功能展示" in collect[i]['title']:
            tmp[0] = deepcopy(collect[i])
        if "父母的体检报告出来了，身体毛病挺多的" in collect[i]['title']:
            tmp[1] = deepcopy(collect[i])
    for i in tmp:
        if i in collect:
            collect.remove(i)
    collect = tmp + collect
    if allfile==None:
        allfile = collect
    ret = collect[(currentpage-1) * pagesize : currentpage * pagesize]
    return JsonResponse({"collect":ret, "length":len(collect)}, safe = False)

def getvalidnumber():
    no = str(1 << 2)
    kk = deepcopy(no)
    while no in kk:
        kk = np.random.randint(100000000, 999999999)
        kk = str(kk)
    return kk

def mailsend(mail, modify=False, notify_guanliyuan=None):
    # https://docs.python.org/3.12/library/smtplib.html#module-smtplib
    # https://docs.python.org/3.12/library/email.examples.html#email-examples
    # https://wx.mail.qq.com/list/readtemplate?name=app_intro.html#/agreement/authorizationCode
    msg = EmailMessage()
    number = getvalidnumber()
    if not notify_guanliyuan:
        if not modify:
            msg.set_content(f'注册需要的验证数字串：{number}\n\n\nhttp://zoujiu.com.cn')
            msg['Subject'] = "zoujiu.com.cn注册验证数字串"
        else:
            msg.set_content(f'修改密钥需要的验证数字串：{number}\n\n\nhttp://zoujiu.com.cn')
            msg['Subject'] = "zoujiu.com.cn修改密钥数字串"
    if notify_guanliyuan:
        msg.set_content(notify_guanliyuan[1])
        msg['Subject'] = f"zoujiu.com.cn{notify_guanliyuan[0]}"
    msg['From'] = '1069679911@qq.com'
    msg['To'] = mail
    # smtplib.SMTP()
    smpt = smtplib.SMTP_SSL("smtp.qq.com", port=465)
    # smpt.connect("smtp.qq.com", port=465)
    smpt.login(user="1069679911@qq.com", password='tuftmtivszzgbfcb')
    # smpt.sendmail()
    try:
        smpt.send_message(msg)
    except Exception as e:
        print("register error ", e)
        return '------'
    # smpt.close()
    smpt.quit()
    return number

sendmutex = Semaphore(value=1)
def sendverify(request):
    global sendmutex
    req = request.GET.dict()
    mail = req['mail']

    addpa = os.path.abspath(__file__ + "/../../")
    member = os.path.join(addpa, "..", "article", 'member.txt')
    if 'modify' not in req.keys():
        cret = checkYonghu(mail, member)
        if not cret:
            return JsonResponse({"number":2}, safe = False)

    number = mailsend(mail, 'modify' in req.keys())
    if number[0]=='-':
        return JsonResponse({"number":False})
    addpa = os.path.abspath(__file__ + "/../../")
    yonghu = os.path.join(addpa, "..", "article", 'register.txt')
    sendmutex.acquire()
    with open(yonghu, 'a+', encoding='utf-8') as obj:
        obj.write(str(time.time() + timezone) + f'<》!=$)(=$@{mail}<》!=$)(=$@{number}\n')
    sendmutex.release()
    return JsonResponse({"number":True}, safe = False)

    # https://docs.python.org/3.12/library/smtplib.html#module-smtplib
    # https://docs.python.org/3.12/library/email.examples.html#email-examples
    # https://zhuanlan.zhihu.com/p/24180606
    # https://docs.python.org/3.12/library/email.html#module-email
    # https://wx.mail.qq.com/list/readtemplate?name=app_intro.html#/agreement/authorizationCode

def checkYonghu(email, member):
    if not os.path.exists(member):
        return True
    with open(member, 'r', encoding='utf-8') as fp:
        for i in fp.readlines():
            i = i.strip().split('<》!=$)(=$@')
            if i[1]==email:
                return False
    return True

# LeftSetting_Formel = [
#         {"introduction":"", "link":"", 'color':"#000000", "button1":"", "button2":"", "button3":"", 'n':1},
#         {"introduction":"", "link":"", 'color':"#000000", "button1":"", "button2":"", "button3":"", 'n':2},
#         {"introduction":"", "link":"", 'color':"#000000", "button1":"", "button2":"", "button3":"", 'n':3},
#         {"introduction":"", "link":"", 'color':"#000000", "button1":"", "button2":"", "button3":"", 'n':4},
#         {"introduction":"", "link":"", 'color':"#000000", "button1":"", "button2":"", "button3":"", 'n':5},
#         {"introduction":"", "link":"", 'color':"#000000", "button1":"", "button2":"", "button3":"", 'n':6},
#         {"introduction":"", "link":"", 'color':"#000000", "button1":"", "button2":"", "button3":"", 'n':7},
#         {"introduction":"", "link":"", 'color':"#000000", "button1":"", "button2":"", "button3":"", 'n':8},
#         {"introduction":"", "link":"", 'color':"#000000", "button1":"", "button2":"", "button3":"", 'n':9},
#         {"introduction":"", "link":"", 'color':"#000000", "button1":"", "button2":"", "button3":"", 'n':10},
#       ]
LeftSetting_Formel = [
  {
    "introduction": "GitHub [github.com/ZouJiu1]",
    "link": "https://github.com/ZouJiu1",
    "color": "#ff4500",
    "button1": "",
    "button2": "",
    "button3": "",
    "n": 1
  },
  {
    "introduction": "numpy实现所有前向传播和反向传播的LSTM、RNN，古诗词生成",
    "link": "https://github.com/ZouJiu1/numpy_lstm_RNN",
    "color": "#c7158577",
    "button1": "",
    "button2": "",
    "button3": "",
    "n": 2
  },
  {
    "introduction": "numpy实现所有前向传播和反向传播的Alexnet分类CNN网络来train MNIST，准确率：96.2%",
    "link": "https://github.com/ZouJiu1/CNN_numpy",
    "color": "#ffd700",
    "button1": "",
    "button2": "",
    "button3": "",
    "n": 3
  },
  {
    "introduction": "numpy实现所有前向传播和反向传播的transformer网络，包括VIT、MNIST分类 (准确率：97.2%) 、古诗词生成",
    "link": "https://github.com/ZouJiu1/numpy_transformer",
    "color": "#ff4500",
    "button1": "",
    "button2": "",
    "button3": "",
    "n": 4
  },
  {
    "introduction": "自己写好并且train的Yolov3网络，分类、分割、检测、关节点检测",
    "link": "https://github.com/ZouJiu1/Pytorch_YOLOV3",
    "color": "#00ced1",
    "button1": "检测",
    "button2": "分割",
    "button3": "分割+keypoint",
    "n": 5
  },
  {
    "introduction": "CSDN博客 [zoujiu.blog.csdn.net/]",
    "link": "https://zoujiu.blog.csdn.net/",
    "color": "#c71585",
    "button1": "",
    "button2": "",
    "button3": "",
    "n": 6
  },
  {
    "introduction": "知乎 [www.zhihu.com/people/zoujiu1]",
    "link": "https://www.zhihu.com/people/zoujiu1",
    "color": "#c71585",
    "button1": "",
    "button2": "",
    "button3": "",
    "n": 7
  },
  {
    "introduction": "",
    "link": "",
    "color": "#000000",
    "button1": "",
    "button2": "",
    "button3": "",
    "n": 8
  },
  {
    "introduction": "",
    "link": "",
    "color": "#000000",
    "button1": "",
    "button2": "",
    "button3": "",
    "n": 9
  },
  {
    "introduction": "",
    "link": "",
    "color": "#000000",
    "button1": "",
    "button2": "",
    "button3": "",
    "n": 10
  }
]
Setting_Formel = [
        {"introduction":"姓名", "link":"", "link_describe":"邹九", 'other_describe':"", "button":"", 'n':1},
        {"introduction":"邮箱", "link":"", "link_describe":"1069679911@qq.com", 'other_describe':"", "button":"", 'n':2},
        {"introduction":"攀拓PAT", "link":"https://github.com/ZouJiu1/PAT", "link_describe":"github.com/ZouJiu1/PAT", 'other_describe':"甲级/乙级基本都刷完了", "button":"PAT证书", 'n':3},
        {"introduction":"Leetcode主页", "link":"https://leetcode.cn/u/shiheyingzhe/", "link_describe":"leetcode.cn/u/shiheyingzhe/", 'other_describe':"刷完了406道题目", "button":"", 'n':4},
        {"introduction":"Kaggle主页", "link":"https://www.kaggle.com/shiheyingzhe", "link_describe":"www.kaggle.com/shiheyingzhe", 'other_describe':"", "button":"", 'n':5},
        {"introduction":"", "link":"", "link_describe":"", 'other_describe':"", "button":"", "n":6},
        {"introduction":"", "link":"", "link_describe":"", 'other_describe':"", "button":"", "n":7},
        {"introduction":"", "link":"", "link_describe":"", 'other_describe':"", "button":"", "n":8},
        {"introduction":"", "link":"", "link_describe":"", 'other_describe':"", "button":"", "n":9},
        {"introduction":"", "link":"", "link_describe":"", 'other_describe':"", "button":"", "n":10},
      ]

memmute = Semaphore(value=1)
ffmute = Semaphore(value=1)
fleftmute = Semaphore(value=1)
def writeYonghu(password, member, email, nickname):
    global Setting_Formel, LeftSetting_Formel, memmute, ffmute, fleftmute
    key = bytes(password, encoding='utf-8')
    sha = hashlib.sha256()
    sha.update(key)
    ret = sha.hexdigest()

    memmute.acquire()
    with open(member, 'a+', encoding='utf-8') as fp:
        fp.write(f"{ret}<》!=$)(=$@{email}<》!=$)(=$@{nickname}<》!=$)(=$@1\n")
    memmute.release()

    prepa = os.path.abspath(__file__ + "/../../../")
    id = email.index("@")
    # rpl = str(1 << 2)
    ml = email[:id]#.replace(rpl, "#")
    people = os.path.join(prepa, 'people', ml)
    csdn = os.path.join(prepa, 'people', ml, 'csdn_spider_selenium', 'article')
    think = os.path.join(prepa, 'people', ml, 'zhihu_spider_selenium', 'think')
    travel = os.path.join(prepa, 'people', ml, 'zhihu_spider_selenium', 'travel')
    ideo = os.path.join(prepa, 'people', ml, 'video')
    setting = os.path.join(prepa, 'people', ml, 'setting')
    touxiang = os.path.join(prepa, 'people', ml, 'touxiang')
    set_left = os.path.join(prepa, 'people', ml, 'set_left')
    imgbook = os.path.join(prepa, 'people', ml, 'imgbook')
    # book = os.path.join(prepa, 'people', ml, 'book')
    # main = os.path.join(prepa, 'people', ml, 'main')
    dircol = [csdn, think ,travel, ideo, setting, touxiang, set_left, imgbook]
    for i in dircol:
        os.makedirs(i, exist_ok=True)
    for i in range(1, 11):
        nth = os.path.join(setting, str(i))
        os.makedirs(nth, exist_ok=True)
    for i in range(1, 11):
        nth1 = os.path.join(set_left, str(i), '1')
        nth2 = os.path.join(set_left, str(i), '2')
        nth3 = os.path.join(set_left, str(i), '3')
        os.makedirs(nth1, exist_ok=True)
        os.makedirs(nth2, exist_ok=True)
        os.makedirs(nth3, exist_ok=True)

    file = os.path.join(setting, 'f.json')

    if not os.path.exists(file):
        # SettingForm = []
        # for i in range(1, 11):
        #     SettingForm.append({"introduction":"", "link":"", "link_describe":"", 'other_describe':"", \
        #                         "button":"", 'n':i})
        ffmute.acquire()
        with open(file, 'w', encoding='utf-8') as obj:
            json.dump(Setting_Formel, obj, indent=2, ensure_ascii=False)
        ffmute.release()

    file = os.path.join(set_left, 'fleft.json')
    if not os.path.exists(file):
        # SettingForm = []
        # for i in range(1, 11):
        #     SettingForm.append({"introduction":"", "link":"", "button1":"", 'button2':"", \
        #                         "button2":"", 'n':i})
        fleftmute.acquire()
        with open(file, 'w', encoding='utf-8') as obj:
            json.dump(LeftSetting_Formel, obj, indent=2, ensure_ascii=False)
        fleftmute.release()
    
    shutil.copyfile(os.path.join(prepa, 'article', "2寸.jpg"), os.path.join(touxiang, '2寸.jpg'))

regmute = Semaphore(value=1)
def register(request):
    global regmute
    req = json.loads(request.body)
    infor = req["information"]
    password = infor['pass']
    checkPass = infor['checkPass']
    email = infor['email']
    verifynumber = infor['verifynumber']
    nickname = infor['nickname']
    # origin = infor['origin']
    # if origin!=verifynumber:
    #     return JsonResponse({"ret":0}, safe = False)
    addpa = os.path.abspath(__file__ + "/../../")
    yonghu = os.path.join(addpa, "..", "article", 'register.txt')
    member = os.path.join(addpa, "..", "article", 'member.txt')
    
    # tup = []
    fin = -1
    if 'forget' in req.keys():
        prepa = os.path.abspath(__file__ + "/../../../")
        oldpassword = os.path.join(prepa, 'article', 'oldpassword')
        if not os.path.exists(oldpassword):
            os.makedirs(oldpassword)
        postDate = datetime.fromtimestamp(time.time() +timezone).isoformat()[:19].replace(":", "_")
        shutil.copyfile(member, os.path.join(oldpassword, postDate + '_member.txt'))
        allkl = []
        with open(member, 'r', encoding='utf-8') as obj:
            for i in obj.readlines():
                ll = deepcopy(i)
                i = i.strip()
                i = i.split("<》!=$)(=$@")
                if i[1]==email:
                    key = bytes(password, encoding='utf-8')
                    sha = hashlib.sha256()
                    sha.update(key)
                    ret = sha.hexdigest()
                    i[0] = ret
                    ll = '<》!=$)(=$@'.join(i) + '\n'
                allkl.append(ll)
        regmute.acquire()
        with open(member, 'w', encoding='utf-8') as obj:
            obj.write("".join(allkl))
        regmute.release()
        return JsonResponse({"ret":100}, safe = False)

    with open(yonghu, 'r', encoding='utf-8') as obj:
        for i in obj.readlines():
            i = i.strip()
            i = i.split("<》!=$)(=$@")
            if email==i[1]:
                dif = time.time() + timezone - float(i[0])
                if dif >= 24 * 3600:
                    fin = 1
                    continue
                if str(verifynumber)==i[-1]:
                    chk = checkYonghu(email, member)
                    if chk:
                        writeYonghu(password, member, email, nickname)
                    else:
                        return JsonResponse({"ret": -6}, safe=False)
                    return JsonResponse({"ret":1}, safe = False)
    if fin==1:
        return JsonResponse({"ret":-1}, safe = False)
    else:
        return JsonResponse({"ret":-2}, safe = False)

def genpassword(password):
    key = bytes(password, encoding='utf-8')
    sha = hashlib.sha256()
    sha.update(key)
    ret = sha.hexdigest()
    return ret

def checklogin(password, username, member):
    key = bytes(password, encoding='utf-8')
    sha = hashlib.sha256()
    sha.update(key)
    ret = sha.hexdigest()
    with open(member, 'r', encoding='utf-8') as fp:
        for i in fp.readlines():
            i = i.strip().split("<》!=$)(=$@")
            if (i[1]==username or i[2]==username) and i[0]==ret:
                mail = i[1]
                id = mail.index("@")
                # rpl = str(1 << 2)
                ml = mail[:id] #.replace(rpl, "#")
                return True, ret, ml, i[2]
    return False, 0, 0, 0

def login(request):
    req = json.loads(request.body)
    infor = req["LoginForm"]
    password = infor['password']
    username = infor['username']
    addpa = os.path.abspath(__file__ + "/../../")
    member = os.path.join(addpa, "..", "article", 'member.txt')
    ret, passw, ml, usern = checklogin(password, username, member)
    if ret:
        return JsonResponse({"ret":ret,'password':passw, 'mail':ml, 'username':usern}, safe = False)
    else:
        return JsonResponse({"ret":ret}, safe=False)

def check_logined(mailaddr, password):
    addpa = os.path.abspath(__file__ + "/../../")
    member = os.path.join(addpa, "..", "article", 'member.txt')
    usern = ""
    with open(member, 'r', encoding='utf-8') as fp:
        for i in fp.readlines():
            i = i.strip().split("<》!=$)(=$@")
            mail = i[1]
            id = mail.index("@")
            # rpl = str(1 << 2)
            ml = mail[:id] #.replace(rpl, "#")
            if ml==mailaddr and password==i[0]:
                return True
    return False

def findurlmail(urlrul:str):
    mail = ""
    try:
        # ind = urlrul.index("/zj")
        # return 'zj'
        ind = urlrul.index("/homepage")
        return 'homepage'
    except:
        urlll = urlrul[10:]
        fir = urlll.index("/")
        ur = urlll[fir + 1:]
        try:
            sec = ur.index('/')
        except:
            sec = -1
        try:
            secl = ur.index('#')
        except:
            secl = -1
        if sec < 0:
            sec = ur.__len__()
        if secl < 0:
            secl = ur.__len__()
        sec = min(sec, secl)
        mail = urlrul[fir + 11:11 + sec + fir]
        return mail

# @csrf_exempt
def getusername(request):
    if isinstance(request.POST.dict(), dict) and len(request.POST.dict())!=0:
        req = request.POST.dict()
    else:
        req = json.loads(request.body)
    if 'url' not in req.keys():
        req['url'] = ""
    url = req['url']
    if 'mail' not in req.keys():
        req['mail'] = ''
    if 'password' not in req.keys():
        req['password'] = ""
    mailaddr = req['mail']
    password = req['password']
    addpa = os.path.abspath(__file__ + "/../../")
    member = os.path.join(addpa, "..", "article", 'member.txt')
    usern = ""
    if not os.path.exists(member):
        os.system("touch \"%s\""%member)
    urlmail = findurlmail(req['url'])
    # if urlmail=='zj' or len(urlmail)<=6:
    if urlmail=='zj' or len(urlmail)<=6:
        return JsonResponse({"ret":0, 'mail':None, 'username':None, 'urlmail':urlmail, 'quanxian':-1, 'truemail':-1}, safe = False)
    quanxian = -1
    nickname = ""
    with open(member, 'r', encoding='utf-8') as fp:
        fpline = [i.strip() for i in fp.readlines()]
        findmember = False
        for i in fpline:
            i = i.split("<》!=$)(=$@")
            mail = i[1]
            id = mail.index("@")
            # rpl = str(1 << 2)
            ml = mail[:id]#.replace(rpl, "#")
            if ml==mailaddr:
                quanxian = int(i[-1])
                nickname = i[2]
            if ml==mailaddr and password==i[0]:
                usern = i[2]
                findmember = True
                if ml in req['url']:
                    return JsonResponse({"ret":1, 'mail':mailaddr, 'username':usern, \
                                         'urlmail':urlmail, 'quanxian':quanxian, 'truemail':mail, 'nickname':nickname}, \
                                        safe = False)
                else:
                    findone = False
                    quanxian = -1
                    find1 = False
                    find2 = False
                    for j in fpline:
                        ij = j.split("<》!=$)(=$@")
                        mail = ij[1]
                        id = mail.index("@")
                        mll = mail[:id]
                        if urlmail==mll:
                            usern = ij[2]
                            findone = True
                            find1 = True
                            # break
                        if mll == mailaddr:
                            quanxian = int(ij[-1])
                            find2 = True
                            nickname = i[2]
                        if find1 and find2:
                            break
                    if findone:
                        return JsonResponse({"ret":2, 'mail':mailaddr, 'username':usern, \
                                             'urlmail':urlmail, 'quanxian':quanxian, 'truemail':mail, 'nickname':nickname},\
                                            safe = False)
        if not findmember:
            for i in fpline:
                i = i.split("<》!=$)(=$@")
                mail = i[1]
                id = mail.index("@")
                # rpl = str(1 << 2)
                ml = mail[:id]#.replace(rpl, "#")
                if urlmail==ml:
                    quanxian = int(i[-1])
                    nickname = i[2]
                    return JsonResponse({"ret":3, 'mail':mailaddr, 'username':nickname, \
                                             'urlmail':urlmail, 'quanxian':-1, 'truemail':None, 'nickname':nickname},\
                                            safe = False)
    return JsonResponse({"ret":0, 'mail':None, 'username':None, \
                         'urlmail':urlmail, 'quanxian':-1, 'truemail':-1, 'nickname':nickname}, safe = False)

# https://docs.djangoproject.com/zh-hans/5.1/ref/csrf/
@csrf_exempt
def postArticle(request):
    global allfile, path
    basepath = deepcopy(path)
    allfile = None
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    req = json.loads(request.body)
    markdown = req["textarea"]
    title = req["title"]
    save = bool(req["save"])
    old_title = req["old_title"]
    dirname = req["dirname"]
    filepath = req["path"]
    # 2024-09-14T14:52:52.820554

    postDa = datetime.fromtimestamp(time.time() +timezone).isoformat()[:19].replace(":", "_")
    postDate = postDa.replace("T", "_空格_").replace(":", "_")
    if 'zhihu' in filepath:
        postDate = postDa.replace("T", "_").replace(":", "_")[:-2]
    new_Title = False
    cpy_title = deepcopy(title)
    title = title.replace(":", "_").replace("?", "_问号_"). \
                    replace("/","_").replace("\\","_").replace("\"", "_").\
                    replace("*","_").replace("|", "_").replace("？", "_问号_").replace("！", "_感叹号_").\
                    replace("<", "小于").replace(">", "大于").replace("(", "").\
                    replace(")", "").replace(",", "_逗号_").replace("，", "_逗号_").replace("   ", "_空格_").\
                    replace("  ", "_空格_").replace(" ", "_空格_").replace("：", "_冒号_").replace("\'", "").\
                    replace("\"", "").replace("`", "")
    old_title = old_title.replace(":", "_").replace("?", "_问号_"). \
                    replace("/","_").replace("\\","_").replace("\"", "_").\
                    replace("*","_").replace("|", "_").replace("？", "_问号_").replace("！", "_感叹号_").\
                    replace("<", "小于").replace(">", "大于").replace("(", "").\
                    replace(")", "").replace(",", "_逗号_").replace("，", "_逗号_").replace("   ", "_空格_").\
                    replace("  ", "_空格_").replace(" ", "_空格_").replace("：", "_冒号_").replace("\'", "").\
                    replace("\"", "").replace("`", "")
    if '_' in title:
        title = title.replace("_", "-")
    if os.path.exists(filepath) and old_title != title:
        new_Title = True
    savefile = filepath
    if save:
        if new_Title:
            newtitle = title
            title = old_title
        savename = postDa.replace("T", "_") + "_markdown.md"

        # if "mail" in req.keys():
        #     if check_logined(req['mail'], req['password']):
        #         basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
        rz = renzheng(request)
        rzret = json.loads(rz.content)
        passed = False
        if "mail" in req.keys():
            get = json.loads(getusername(request).content)
            if not rzret['ret'] and 'password' in req.keys() and check_logined(req['mail'], req['password']):
                basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
                passed = True
                if f"{get['mail']}" not in req['url']:
                    return JsonResponse( { "ret" : -100} , safe = False)
            elif get['ret']==2 and not rzret['ret']:
                return JsonResponse( { "ret" : -100} , safe = False)
        if not passed and not rzret['ret']:
            return JsonResponse( { "ret" : -100} , safe = False)
        elif not passed and rzret['ret']:
            get = json.loads(getusername(request).content)
            if get['ret'] > 0:
                basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")

        dirp = basepath
        if 'zhihu' in filepath:
            dirp = dirp.replace("csdn_spider", "zhihu_spider")
        savepath = os.path.join(dirp, postDate + "_" + title)
        if len(dirname) > 0:
            for i in os.listdir(dirp):
                if dirname == i: # or (len(title) > 0 and title in i):
                    savepath = os.path.join(dirp, i)
                    break
        if not os.path.exists(savepath):
            os.mkdir(savepath)
        savefile = os.path.join(savepath, savename)
        # if title not in markdown[:100]:
        #     markdown = f"# {title}\n\n" + markdown 
        if len(markdown)==0:
            markdown = "# no content\n\n# no content\n\n# no content\n\n"
        try:
            nextline_index = markdown.index("\n")
        except:
            markdown = "-----------------------------\n\n" + markdown
        with open(savefile, 'w') as obj:
            obj.write(markdown)
        create = os.path.join(savepath, 'create.txt')
        if not os.path.exists(create):
            with open(create, 'w') as obj:
                obj.write(postDate + "\n")
        with open(create, 'a+') as obj:
            obj.write(postDate + "\n")
        if new_Title:
            dat = dirname[:23] + newtitle 
            if 'zhihu' in filepath:
                dat = dirname[:20-3] + newtitle
            os.rename(savepath, os.path.join(dirp, dat))

    if len(filepath) > 0:
        index = filepath.index("vue-project")
        k = len(filepath) - 1
        while filepath[k]!=os.sep:
            k = k - 1
        if 'dist' in filepath:
            index += 16
        else:
            index += 11

    markdown, collect = remove_code(markdown)
    markdown, collect_katex = remove_katex(markdown)
    choyang = list('《《《》》》》》》《《《？？；；；；；；；；、、、、、、、、）））（（（（（？？？？？】】】【【【ABCDEFGHIJKLMNOPQRSTUVWXYZ'.upper())

    downline = []
    def remove_downline(text):
        inp = text[0]
        rand = np.random.choice(choyang, 100)
        rand = ''.join(rand) + '】】】'
        downline.append([rand, inp])
        return rand
        
    markdown = regular.sub(r' *[\w\d\-\_]*\_[\w\d\-\_]* *', remove_downline, markdown)
    
    if len(filepath) > 0:
        markdown = markdown.replace('''<img src=\"''',\
            '''<img crossorigin=\"use-credentials\" loading=\"eager\" class=\"preview_img\"''' + \
            '''src=\"''' + filepath[index:k] + os.sep)

    markdown = markdown2.markdown(markdown, extras=["tables", "admonitions", "breaks"])
    # markdown = postDate + '\n\n' + markdown
    if 'zhihu' in filepath:
        index = cpy_title.index("_IP_属地")
        cpy_title = cpy_title[:index]
    if cpy_title not in markdown[:100]:
        markdown = f"<h1 style=\"align=center\">{cpy_title}</h1>\n\n" + markdown
    
    markdown = addback_code(markdown, collect)
    markdown = addback_katex(markdown, collect_katex)
    
    markdown = markdown.replace("<p><br></p>", "")
    markdown = markdown.replace("<a", "<a target=\"_blank\" ")
    def replace_weblink(inp):
        text = inp[0]
        id = text.index('</a>')
        text = text[:id+4] +'<br>'+ text[id+4:]
        return text
    def replace_line_delete(md):
        return  "<s>" + md[0][2:-2] + "</s>"
    def replace_warning(md):
        return '<div class=\"warningclass\">' + md[0][11+1:-3] + "</div>"
    markdown = regular.sub(r'''</a>[\n ]*<a''', replace_weblink, markdown)
    markdown = regular.sub(r'''~~.*~~''', replace_line_delete, markdown)
    markdown = regular.sub(r''' *::: warning *\s.*\n:::''', replace_warning, markdown)
    markdown = markdown.replace("$在这里插入图片描述$", "")
    for i in downline:
        markdown = markdown.replace(i[0], i[1])
    # markdown = regular.sub('\n', '<br>', markdown)
    # markdown = regular.sub('(<br> *){2,100}', '<br>', markdown)
    # markdown = regular.sub("<p>.*\s.*\s.*\s.*</p>", subnextline, markdown)
    # kkk = regular.findall('<p>.*\s*.*</p>', markdown)
    markdown = replaceNextLine_br(markdown)
    # markdown = markdown.replace("\n", "<br>")
    return JsonResponse( { "markdown" : markdown, "path" : savefile, 'ret':True} , safe = False)

def subnextline(txt):
    inp = txt[0]
    inp = inp.replace("\n", "<br>")
    return inp

def replaceNextLine_br(md):
    start = -1
    end = -1
    md += '123456789'
    nowlen = len(md)
    addlen = 0
    j = 0
    while j < nowlen + addlen - 1 or addlen!=0:
        addlen = 0
        nowlen = len(md)
        for i in range(j, nowlen, 1):
            if i < end:
                continue
            j = i
            if md[i:i + 3]=="<p>":
                start = 100
            elif md[i:i + 4]=="</p>":
                start = -1
            elif start > 0 and md[i]=='\n':
                md = md[:i] + "<br>" + md[i + 1:]
                end = i + 4
                addlen += 3
    return md[:-9]

def notify_administer(dir, truemail, mail, urlmail, own=True, action='delete'):
    global path
    administer = os.path.abspath(os.path.join(path, '..', '..', '..', 'administer'))
    if not os.path.exists(administer):
        os.makedirs(administer, exist_ok = True)
    urlmaildir = os.path.join(administer, urlmail)
    if not os.path.exists(urlmaildir):
        os.makedirs(urlmaildir, exist_ok = True)
    
    if action=='delete':
        if not own:
            if isinstance(dir, (list)):
                for i in dir:
                    if i[-1]==os.sep:
                        i = i[:-1]
                    os.system(f"sudo cp -rf \"{i}\" \"{urlmaildir}\"")
                dir = '\n'.join(dir)
            else:
                if dir[-1]==os.sep:
                    dir = dir[:-1]
                os.system(f"sudo cp -rf \"{dir}\" \"{urlmaildir}\"")
            #print(99999999999)
            try:
                mailsend('1069679911@qq.com', modify=False, \
                     notify_guanliyuan=['---delete', \
                     f'{mail} delete {urlmail}\n\ncontent: \n{dir}\n\nnowdir: \n{urlmaildir}'])
            #print(999000009999)
                mailsend(truemail, modify=False, \
                     notify_guanliyuan=['---delete', \
                     f'delete {urlmail}\n\ncontent: \n{dir}\n\n can not be recovered'])
            except Exception as e:
                print("delete notify error: ", e)
                pass

def delete_directory(request):
    global allfile
    # re = request.GET.dict()
    req = json.loads(request.body)
    currentpage = req["path"]
    tail = currentpage.split(os.sep)[-1]
    currentpage = currentpage.replace(tail, "")

    rz = renzheng(request)
    rzret = json.loads(rz.content)
    passed = False
    get = {'quanxian': -1}
    if "mail" in req.keys():
        get = json.loads(getusername(request).content)
        if get['quanxian'] < 1000000 and not rzret['ret'] and 'password' in req.keys() and check_logined(req['mail'], req['password']):
            # basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
            passed = True
            if f"/people/{get['mail']}/" not in currentpage or '.md' not in tail:
                return JsonResponse( { "ret" : -100} , safe = False)
        elif  get['quanxian'] < 1000000 and get['ret']==2:
            return JsonResponse( { "ret" : -100} , safe = False)
        elif  get['quanxian'] == 1000000:
            passed = True
    if not passed and not rzret['ret']:
        return JsonResponse( { "ret" : -100} , safe = False)
    # elif not passed and rzret['ret']:
    #     get = json.loads(getusername(request).content)
    #     if get['ret'] > 0:
    #         basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
    try:
        allfile = None
        if get['quanxian'] == 1000000 and get['mail']!=get['urlmail']:
            notify_administer(currentpage, get['truemail'], get['mail'], get['urlmail'], False)
        elif get['quanxian'] == 1000000 and get['mail']==get['urlmail']:
            notify_administer(currentpage, get['truemail'], get['mail'], get['urlmail'], True)
        shutil.rmtree(currentpage)
        return JsonResponse( { "done" : currentpage , 'ret':True} , safe = False)
    except:
        return JsonResponse( { "done" : currentpage , 'ret':0} , safe = False)

def editArticle(request):
    re = request.GET.dict()
    currentpage = re["path"]
    dirname = currentpage.split(os.sep)[-2]
    postDate = datetime.fromtimestamp(time.time() +timezone).isoformat()[:19].replace(":", "_")
    postDate = postDate.replace("T", " ")
    if '20'==dirname[:2]:
        date = rep(dirname[:22]).replace("_", ":")
        title = rep(dirname[23:])
    else:
        date = postDate
        title = rep(dirname)
    if 'zhihu_' in currentpage:
        date = rep(dirname[:16]).replace("_", ":")
        date = date[:10] + " " + date[11:]
        title = rep(dirname[20 - 3:])
    markdown = ""
    if os.path.exists(currentpage):
        with open(currentpage, 'r', encoding = 'utf-8') as obj:
            markdown = obj.read().strip()

    return JsonResponse( { "markdown" : markdown , "title": title, "dirname": dirname} , safe = False)

def getTail(uploadName):
    if '.jpg' in uploadName.lower():
        tail = ".jpg"
    elif '.png' in uploadName.lower():
        tail = ".png"
    elif '.jpeg' in uploadName.lower():
        tail = ".jpeg"
    elif '.bmp' in uploadName.lower():
        tail = ".bmp"
    elif '.gif' in uploadName.lower():
        tail = ".gif"
    return tail

# https://docs.djangoproject.com/zh-hans/5.1/topics/http/file-uploads/
def handle_uploaded_file(f, savename):
    with open(savename, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)
        # destination.write(f)

def replacewithjpg(path, quality = 60):
    tails = (path[-6:]).lower()
    if '.jpg' in tails or '.png' in tails or \
       '.jpeg' in tails or 'bmp' in tails or \
       '.gif' in tails:
        nowpath = path.replace("." + path[-6:].split(".")[-1], '.jpg')
        img = Image.open(path).convert("RGB")
        nam = nowpath.split(os.sep)[-1]
        try:
            os.remove(path)
        except:
            pass
        img.save(nowpath, quality = quality)
        return nam, nowpath

@csrf_exempt
def uploadImg(request):
    global path
    # body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    req = request.POST.dict()
    # https://docs.djangoproject.com/zh-hans/5.1/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile
    uploadImageName = request.FILES['file'].name
    tail = getTail(uploadImageName)
    # https://docs.djangoproject.com/zh-hans/5.1/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile
    # uploadType = request.FILES['file'].content_type
    old_title = req["old_title"]
    title = req["title"]
    mdpath = req["path"]
    dirname = req["dirname"]
    new_Title = False
    title = title.replace(":", "_").replace("?", "_问号_"). \
                    replace("/","_").replace("\\","_").replace("\"", "_").\
                    replace("*","_").replace("|", "_").replace("？", "_问号_").replace("！", "_感叹号_").\
                    replace("<", "小于").replace(">", "大于").replace("(", "").\
                    replace(")", "").replace(",", "_逗号_").replace("，", "_逗号_").replace("   ", "_空格_").\
                    replace("  ", "_空格_").replace(" ", "_空格_").replace("：", "_冒号_").replace("\'", "").\
                    replace("\"", "").replace("`", "")
    old_title = old_title.replace(":", "_").replace("?", "_问号_"). \
                    replace("/","_").replace("\\","_").replace("\"", "_").\
                    replace("*","_").replace("|", "_").replace("？", "_问号_").replace("！", "_感叹号_").\
                    replace("<", "小于").replace(">", "大于").replace("(", "").\
                    replace(")", "").replace(",", "_逗号_").replace("，", "_逗号_").replace("   ", "_空格_").\
                    replace("  ", "_空格_").replace(" ", "_空格_").replace("：", "_冒号_").replace("\'", "").\
                    replace("\"", "").replace("`", "")
    # assert 1==0, (old_title, title)
    if os.path.exists(mdpath) and old_title != title:
        new_Title = True
    if new_Title:
        newtitle = title
        title = old_title
    number = 0
    if len(mdpath) > 0:
        filename = mdpath.split(os.sep)[-1]
        dirpath = mdpath.replace(filename, "")
        imagelist = []
        for i in os.listdir(dirpath):
            if '.jpg' in i or \
               '.png' in i or \
               '.jpeg' in i or \
               '.bmp' in i or \
               '.gif' in i:
                imagelist.append(i)
            if uploadImageName==i:
                uploadImageName = uploadImageName.replace(".", "_.")
                break
        # imagelist.sort()
        # if len(imagelist) > 0:
            # number = int(imagelist[-1].split(".")[0]) + 1
    # assert 1==0, (body, '\n\n', re, number, request.POST, request.FILES, request.FILES['file'], request.FILES['file'].name, request.FILES['file'].content_type, b'jpeg' in body)
    # assert 1==0, (request.body)
    basepath = deepcopy(path)
    # if "mail" in req.keys() and check_logined(req['mail'], req['password']):
    #     basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
    rz = renzheng(request)
    rzret = json.loads(rz.content)
    passed = False
    if "mail" in req.keys():
        get = json.loads(getusername(request).content)
        if not rzret['ret'] and 'password' in req.keys() and check_logined(req['mail'], req['password']):
            basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
            passed = True
            if f"{get['mail']}" not in req['url']:
                return JsonResponse( { "ret" : -100} , safe = False)
        elif get['ret']==2 and not rzret['ret']:
            return JsonResponse( { "ret" : -100} , safe = False)
    if not passed and not rzret['ret']:
        return JsonResponse( { "ret" : -100} , safe = False)
    elif not passed and rzret['ret']:
        get = json.loads(getusername(request).content)
        if get['ret'] > 0:
            basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")

    dirp = basepath
    postDa = datetime.fromtimestamp(time.time() +timezone).isoformat()[:19].replace(":", "_")
    postDate = postDa.replace("T", "_空格_").replace(":", "_")
    
    if 'zhihu' in mdpath:
        postDate = postDa.replace("T", "_").replace(":", "_")[:-2]
        dirp = dirp.replace("csdn_spider", "zhihu_spider")
    
    savepath = os.path.join(dirp, postDate + "_" + title)
    if len(dirname) > 0:
        for i in os.listdir(dirp):
            if dirname == i: # or (len(old_title) > 0 and old_title in i):
                savepath = os.path.join(dirp, i)
    if not os.path.exists(savepath):
        os.mkdir(savepath)

    dirlast = savepath.split(os.sep)[-1]
    
    uploadname = uploadImageName # str(number) + tail
    imgpath = os.path.join(savepath, uploadname)
    handle_uploaded_file(request.FILES['file'], imgpath)

    uploadname, nowpath = replacewithjpg(imgpath)

    lastpath = savepath
    if new_Title:
        title = newtitle
        dat = dirname[:23] + newtitle
        if 'zhihu' in mdpath:
            dat = dirname[:20-3] + newtitle
        lastpath = os.path.join(dirp, dat)
        dirlast = dat
        os.rename(savepath, os.path.join(dirp, dat))

    if len(mdpath) > 0:
        markdown_path = os.path.join(lastpath, filename)
    else:
        markdown_path = os.path.join(lastpath, 'markdown.md')
    
    element_image = f"\n\n<img src=\"{uploadname}\">\n\n"
    return JsonResponse( { "dirname" : dirlast, "path":markdown_path, "uploadname": element_image, 'title':title} , safe = False)

number_renzheng = {}
ipjson = Semaphore(value=1)

def number_check(ip):
    global addpath, ipjson
    limit = 1000000000000
    if not addpath:
        addpath = os.path.abspath(__file__ + "/../../")
    jsonfile = os.path.join(addpath, '..', 'article', 'ip.json')
    jf = {}
    if os.path.exists(jsonfile) and os.path.getsize(jsonfile) != 0:
        with open(jsonfile, 'r', encoding='utf-8') as obj:
            try:
                jf = json.load(obj)
            except:
                jf = {}
                ipjson.acquire()
                with open(jsonfile, 'w', encoding='utf-8') as obj:
                    json.dump(jf, obj, indent=2)
                ipjson.release()
        if ip not in jf.keys():
            jf[ip] = 0
        jf[ip] += 1
        if jf[ip] >= limit:
            return False
        else:
            ipjson.acquire()
            with open(jsonfile, 'w', encoding = 'utf-8') as obj:
                json.dump(jf, obj, indent = 2)
            ipjson.release()
            return True
    else:
        jf[ip] = 1
        ipjson.acquire()
        with open(jsonfile, 'w', encoding = 'utf-8') as obj:
            json.dump(jf, obj, indent = 2)
        ipjson.release()
        return True
    
def keycheck(key):
    key = bytes(key, encoding='utf-8')
    sha = hashlib.sha256()
    sha.update(key)
    ret = sha.hexdigest()
    if ret=='1e0b8a240fb89b60c8dbaeb282d602415a3a743114d0c650c2d87349f809c61d':
        return True
    else:
        return False

def renzheng(request):
    return JsonResponse( { "ret": False} , safe = False)
    global number_renzheng
    # re = request.GET.dict()
    try:
        if isinstance(request.POST.dict(), dict) and len(request.POST.dict())!=0:
            req = request.POST.dict()
        else:
            req = json.loads(request.body)
    except Exception as e:
        return JsonResponse( { "ret": False} , safe = False)
    postkey = req["postkey"]
    '''
    request.headers
    {'Content-Length': '', 'Content-Type': 'text/plain', 'X-Forwarded-For': '36.17.110.86', 
    'X-Forwarded-Proto': 'https', 'X-Forwarded-Host': 'zoujiu.com.cn', 'X-Forwarded-Prefix': '/', 
    'Host': 'zoujiu.com.cn', 'X-Real-Ip': '36.17.110.86', 'Connection': 'close', 
    'Sec-Ch-Ua-Platform': '"Windows"', 'X-Requested-With': 'XMLHttpRequest', 
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0', 
    'Accept': 'application/json, text/plain, */*', 'Sec-Ch-Ua': '"Microsoft Edge";v="129", 
    "Not=A?Brand";v="8", "Chromium";v="129"', 'Dnt': '1', 'Sec-Ch-Ua-Mobile': '?0', 'Sec-Fetch-Site': 'same-origin', 
    'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty', 'Referer': 'https://zoujiu.com.cn/', 'Accept-Encoding': 'gzip, deflate, br, zstd', 
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6'}
    '''
    ip_address = 'notknown'
    if 'X-Real-Ip' in request.headers.keys():
        ip_address = request.headers['X-Real-Ip']
    else:
        if 'X-Forwarded-For' in request.headers.keys():
            ip_address = request.headers['X-Forwarded-For']
    
    if number_check(ip_address) and keycheck(postkey):
        return JsonResponse( { "ret": True} , safe = False)
    else:
        return JsonResponse( { "ret": False} , safe = False)

clicktxt = Semaphore(value=1)
def write_click(ckf, postDate, ip_address, type):
    global clicktxt
    clicktxt.acquire()
    with open(ckf, 'a+', encoding='utf-8') as obj:
        obj.write(postDate + ',' + ip_address + ',' + type + '\n')
    clicktxt.release()

def clickpage(request):
    global addpath
    rep = request.GET.dict()
    type = rep['type']
    postDa = datetime.fromtimestamp(time.time() +timezone).isoformat()[:19].replace(":", "_")
    postDate = postDa.replace("T", " ")
    
    if not addpath:
        addpath = os.path.abspath(__file__ + "/../../")
    ckf = os.path.join(addpath, "..", "article", 'clickpage.txt')

    ip_address = 'notknown'
    if 'X-Real-Ip' in request.headers.keys():
        ip_address = request.headers['X-Real-Ip']
    else:
        if 'X-Forwarded-For' in request.headers.keys():
            ip_address = request.headers['X-Forwarded-For']
    
    for i in range(100):
        try:
            write_click(ckf, postDate, ip_address, type)
            break
        except:
            time.sleep(30)
    return HttpResponse(",")

def GetSetting(request):
    global path, Setting_Formel, LeftSetting_Formel, ffmute, fleftmute
    req = json.loads(request.body)
    if 'mail' not in req.keys():
        req['mail'] = ''
    get = json.loads(getusername(request).content)
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    if get['ret'] > 0:
        basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")
    
    if 'index' not in req.keys():
        file = os.path.join(basepath, 'setting', 'f.json')
        kkk = os.path.join(basepath, 'set_left')
        if not os.path.exists(kkk):
            os.makedirs(kkk)
        if not os.path.exists(file):
            # SettingForm = []
            # for i in range(1, 11):
            #     SettingForm.append({"introduction":"", "link":"", "link_describe":"", 'other_describe':"", \
            #                         "button":"", 'n':i})
            ffmute.acquire()
            with open(file, 'w', encoding='utf-8') as obj:
                json.dump(Setting_Formel, obj, indent=2, ensure_ascii=False)
            ffmute.release()
            for i in range(1, 11):
                nth = os.path.join(basepath, 'setting', str(i))
                os.makedirs(nth, exist_ok=True)
    
        with open(file, 'r', encoding='utf-8') as obj:
            jfile = json.load(obj)
    else:
        file = os.path.join(basepath, 'set_left', 'fleft.json')
        if not os.path.exists(file):
            # SettingForm = []
            # for i in range(1, 11):
            #     SettingForm.append({"introduction":"", "link":"", "button1":"", 'button2':"", \
            #                         "button2":"", 'n':i})
            kkk = os.path.join(basepath, 'set_left')
            if not os.path.exists(kkk):
                os.makedirs(kkk)
            fleftmute.acquire()
            with open(file, 'w', encoding='utf-8') as obj:
                json.dump(LeftSetting_Formel, obj, indent=2, ensure_ascii=False)
            fleftmute.release()
            for i in range(1, 11):
                nth1 = os.path.join(basepath, 'set_left', str(i), '1')
                nth2 = os.path.join(basepath, 'set_left', str(i), '2')
                nth3 = os.path.join(basepath, 'set_left', str(i), '3')
                os.makedirs(nth1, exist_ok=True)
                os.makedirs(nth2, exist_ok=True)
                os.makedirs(nth3, exist_ok=True)
        with open(file, 'r', encoding='utf-8') as obj:
            jfile = json.load(obj)
    return JsonResponse( { "jfile" : jfile} , safe = False)

fbookmute = Semaphore(value=1)
def mainpagedataget(request):
    global path, Setting_Formel, LeftSetting_Formel, ffmute, fleftmute, fbookmute
    req = json.loads(request.body)
    if 'mail' not in req.keys():
        req['mail'] = ''
    get = json.loads(getusername(request).content)
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    if get['ret'] > 0:
        basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")

    ll = []

    if 'imgbook' in req.keys():
        jfile = []
        inpath = os.path.join(basepath, 'imgbook', 'fbook.json')
        kkk = os.path.join(basepath, 'imgbook')
        if not os.path.exists(kkk):
            os.makedirs(kkk)
        # kkkk = os.path.join(basepath, 'imgbook', '1')
        # if not os.path.exists(kkkk):
        #     for i in range(1, 50 - 3, 1):
        #         tp = os.path.join(basepath, 'imgbook', str(i))
        #         if not os.path.exists(tp):
        #             os.makedirs(tp)
        if not os.path.exists(inpath):
            kk = []
            imgbookall = []
            # for i in range(1, 2, 1):
            #     imgbookall.append({
            #     "github": "",
            #     "img": "",
            #     "name": "",
            #     "img": "",
            #     "finished": False,
            #     "author": "",
            #     "n": i,
            #     "readdate": ""
            # },)
            with open(inpath, 'w', encoding='utf-8') as obj:
                json.dump(imgbookall, obj, indent=2, ensure_ascii=False)
        else:
            with open(inpath, 'r', encoding='utf-8') as obj:
                kk = json.load(obj)
        cnt = 1
        for i in kk:
            if i['name']!="":
                found = False
                if 'search' in req.keys() and len(req['search'])!=0:
                    search = req['search'].lower().split(" ")
                    for ir in search:
                        if ir=="":
                            continue
                        if ir in i['github'].lower() or \
                            ir in i['name'].lower() or \
                            ir in i['readdate'].lower() or \
                            ir in i['ratio'].lower():
                                found = True
                                break
                if 'search' in req.keys() and len(req['search'])!=0 and not found:
                    continue
                if 'checkboxval' in req.keys() and req['checkboxval']!=2:
                    if req['checkboxval']!=int(i['finished']):
                        continue

                setting = os.path.join(basepath, 'imgbook', str(i['n']))
                im = [ijk for ijk in os.listdir(setting) if '.jpg' in ijk.lower()]
                if len(im) > 0:
                    setting = os.path.join(basepath, 'imgbook', str(i['n']), im[0])
                    if 'people' in setting:
                        kk = '/people' + setting.split("people")[-1]
                    else:
                        kk = '/article' + setting.split("article")[-1]
                    i['img'] = kk
                else:
                    i['img'] = '/article/logobeian.png'
                i['imglist'] = [i['img']]
                if i['readdate']!='':
                    i['ratio'] = i['readdate'] + ", " + i['ratio']
                i['website'] = r'https://s.taobao.com/search?_input_charset=utf-8&commend=all&ie=utf8&initiative_id=tbindexz_20170306&localImgKey=&page=1&q=' + i['name']
                i['number'] = str(cnt)
                cnt += 1
                jfile.append(i)
        return JsonResponse( { "jfile" : jfile} , safe = False)
    if True:
        file = os.path.join(basepath, 'setting', 'f.json')
        kkk = os.path.join(basepath, 'setting')
        if not os.path.exists(kkk):
            os.makedirs(kkk)
        if not os.path.exists(file):
            # SettingForm = []
            # for i in range(1, 11):
            #     SettingForm.append({"introduction":"", "link":"", "link_describe":"", 'other_describe':"", \
            #                         "button":"", 'n':i})
            ffmute.acquire()
            with open(file, 'w', encoding='utf-8') as obj:
                json.dump(Setting_Formel, obj, indent=2, ensure_ascii=False)
            ffmute.release()
            for i in range(1, 11):
                nth = os.path.join(basepath, 'setting', str(i))
                os.makedirs(nth, exist_ok=True)
        delete = []
        with open(file, 'r', encoding='utf-8') as obj:
            jfile = json.load(obj)
            for j in range(len(jfile)):
                if jfile[j]['introduction']=="":
                    delete.append(jfile[j])
                else:
                    jfile[j]['showbutton'] = True
                    if len(jfile[j]['link_describe'])==0:
                        jfile[j]['link_describe'] = jfile[j]['link']
                        jfile[j]['link'] = '.'
                    if len(jfile[j]['button'])==0:
                        jfile[j]['button'] = '图片'
                    if len(jfile[j]['other_describe'])!=0:
                        jfile[j]['other_describe'] = '，' + jfile[j]['other_describe']
                    setting = os.path.join(basepath, 'setting', str(jfile[j]['n']))
                    if not os.path.exists(setting):
                        os.makedirs(setting)
                    showimg = []
                    if 'people' in setting:
                        kk = '/people' + setting.split("people")[-1]
                    else:
                        kk = '/article' + setting.split("article")[-1]
                    for i in os.listdir(setting):
                        if '.DS_Store' in i:
                            continue
                        if '.jpg' not in i and '.png' not in i and '.JPG' not in i and ".bmp" not in i:
                            continue
                        showimg.append(kk + os.sep + i)
                    jfile[j]['image'] = showimg
                    if len(showimg)==0:
                        jfile[j]['showbutton'] = False
        for de in delete:
            jfile.remove(de)
        ll.append(jfile)
    if True:
        setting = os.path.join(basepath, 'touxiang')
        if not os.path.exists(setting):
            os.makedirs(setting)
            prepa = os.path.abspath(__file__ + "/../../../")
            shutil.copyfile(os.path.join(prepa, 'article', "2寸.jpg"), os.path.join(setting, '2寸.jpg'))
        f1 = os.listdir(setting)[0]
        if 'people' in setting:
            kk = '/people' + setting.split("people")[-1]
        else:
            kk = '/article' + setting.split("article")[-1]
        ll.append(kk + os.sep + f1)
        # return JsonResponse( { "jfile" : os.path.join(kk, f1)} , safe = False)
    # if 'imgbook' in req.keys():
    #     setting = os.path.join(basepath, 'imgbook')
    #     if not os.path.exists(setting):
    #         os.makedirs(setting)
            # for i in range(600):
    if True:
        file = os.path.join(basepath, 'set_left', 'fleft.json')
        kkk = os.path.join(basepath, 'set_left')
        if not os.path.exists(kkk):
            os.makedirs(kkk)
        if not os.path.exists(file):
            # SettingForm = []
            # for i in range(1, 11):
            #     SettingForm.append({"introduction":"", "link":"", "button1":"", 'button2':"", \
            #                         "button2":"", 'n':i})
            fleftmute.acquire()
            with open(file, 'w', encoding='utf-8') as obj:
                json.dump(LeftSetting_Formel, obj, indent=2, ensure_ascii=False)
            fleftmute.release()
            for i in range(1, 11):
                nth1 = os.path.join(basepath, 'set_left', str(i), '1')
                nth2 = os.path.join(basepath, 'set_left', str(i), '2')
                nth3 = os.path.join(basepath, 'set_left', str(i), '3')
                os.makedirs(nth1, exist_ok=True)
                os.makedirs(nth2, exist_ok=True)
                os.makedirs(nth3, exist_ok=True)
        delete = []
        with open(file, 'r', encoding='utf-8') as obj:
            jfile = json.load(obj)
            for j in range(len(jfile)):
                if jfile[j]['introduction']=="":
                    delete.append(jfile[j])
                else:
                    jfile[j]['style'] = f"margin-left:1px;color:{jfile[j]['color']};font-size:16px;"
                    jfile[j]['showfirst'] = True
                    jfile[j]['showsecond'] = True
                    jfile[j]['showthird'] = True
                    if len(jfile[j]['button1'])==0:
                        jfile[j]['button1'] = '图片'
                    if len(jfile[j]['button2'])==0:
                        jfile[j]['button2'] = '图片'
                    if len(jfile[j]['button3'])==0:
                        jfile[j]['button3'] = '图片'
                    setting = os.path.join(basepath, 'set_left', str(jfile[j]['n']), '1')
                    if not os.path.exists(setting):
                        os.makedirs(setting)
                    showimg = []
                    if 'people' in setting:
                        kk = '/people' + setting.split("people")[-1]
                    else:
                        kk = '/article' + setting.split("article")[-1]
                    for i in os.listdir(setting):
                        if '.DS_Store' in i:
                            continue
                        if '.jpg' not in i and '.png' not in i and '.JPG' not in i and ".bmp" not in i:
                            continue
                        showimg.append(kk + os.sep + i)
                    jfile[j]['image1'] = showimg
                    if len(showimg)==0:
                        jfile[j]['showfirst'] = False

                    setting = os.path.join(basepath, 'set_left', str(jfile[j]['n']), '2')
                    if not os.path.exists(setting):
                        os.makedirs(setting)
                    showimg = []
                    if 'people' in setting:
                        kk = '/people' + setting.split("people")[-1]
                    else:
                        kk = '/article' + setting.split("article")[-1]
                    for i in os.listdir(setting):
                        if '.DS_Store' in i:
                            continue
                        if '.jpg' not in i and '.png' not in i and '.JPG' not in i and ".bmp" not in i:
                            continue
                        showimg.append(kk + os.sep + i)
                    jfile[j]['image2'] = showimg
                    if len(showimg)==0:
                        jfile[j]['showsecond'] = False

                    setting = os.path.join(basepath, 'set_left', str(jfile[j]['n']), '3')
                    if not os.path.exists(setting):
                        os.makedirs(setting)
                    showimg = []
                    if 'people' in setting:
                        kk = '/people' + setting.split("people")[-1]
                    else:
                        kk = '/article' + setting.split("article")[-1]
                    for i in os.listdir(setting):
                        if '.DS_Store' in i:
                            continue
                        if '.jpg' not in i and '.png' not in i and '.JPG' not in i and ".bmp" not in i:
                            continue
                        showimg.append(kk + os.sep + i)
                    jfile[j]['image3'] = showimg
                    if len(showimg)==0:
                        jfile[j]['showthird'] = False
        for de in delete:
            jfile.remove(de)
        ll.append(jfile)
    return JsonResponse( { "jfile" : ll} , safe = False)

def mainpageuploadImg(request):
    global path, fbookmute
    # body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    req = request.POST.dict()
    # https://docs.djangoproject.com/zh-hans/5.1/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile
    uploadImageName = request.FILES['file'].name.replace(" ", "_")
    tail = getTail(uploadImageName)
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    rz = renzheng(request)
    rzret = json.loads(rz.content)
    passed = False
    if "mail" in req.keys():
        get = json.loads(getusername(request).content)
        if not rzret['ret'] and 'password' in req.keys() and check_logined(req['mail'], req['password']):
            basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
            passed = True
            if f"{get['mail']}" not in req['url']:
                return JsonResponse( { "ret" : -100} , safe = False)
        elif get['ret']==2 and not rzret['ret']:
            return JsonResponse( { "ret" : -100} , safe = False)
    if not passed and not rzret['ret']:
        return JsonResponse( { "ret" : -100} , safe = False)
    elif not passed and rzret['ret']:
        get = json.loads(getusername(request).content)
        if get['ret'] > 0:
            basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")

    if 'n' in req.keys():
        setting = os.path.join(basepath, 'setting', req['n'])
    if 'index' in req.keys():
        setting = os.path.join(basepath, 'set_left', req['n'].split("_")[0], str(req["index"]))
    
    xiang = ''
    if 'person' in req.keys():
        uploadImageName = 'person' + tail
        setting = os.path.join(basepath, 'touxiang')
        if not os.path.exists(setting):
            os.makedirs(setting, exist_ok=True)
        xiang = os.listdir(setting)
        if len(xiang)!=0:
            xiang = xiang[0]
    
    if 'ImgbookUpload' in req.keys():
        setting = os.path.join(basepath, 'imgbook')
        if not os.path.exists(setting):
            os.makedirs(setting, exist_ok=True)
        maxmax = -9
        le = 10
        if 'clickcard' not in req.keys():
            inpath = os.path.join(basepath, 'imgbook', 'fbook.json')
            with open(inpath, 'r', encoding='utf-8') as obj:
                kk = json.load(obj)
                kkey = [ijk['n'] for ijk in kk]
                kkey.sort()
                lastnum = 0
                if len(kkey)==0:
                    lastnum = 1
                else:
                    lastnum = kkey[-1] + 2
                for ijk in range(lastnum):
                    if ijk not in kkey:
                        maxmax = ijk
                        break
            # kkl = [itt for itt in os.listdir(setting) if os.path.isdir(os.path.join(setting, itt)) and 'all'!=itt]
            # kkl = sorted(kkl.__iter__(), key=lambda x:int(x))
            # for i in kkl:
            #     if i=='all':
            #         continue
            #     # if os.path.isdir(os.path.join(setting, i)):
            #     maxmax = max(maxmax, int(i))
            #     le = len(os.listdir(os.path.join(setting, i)))
            #     if le==0:
            #         break
            # inpath = os.path.join(basepath, 'imgbook', 'fbook.json')
            # maxi = -9
            # if os.path.exists(inpath):
            #     with open(inpath, 'r', encoding='utf-8') as obj:
            #         kk = json.load(obj)
            #         for i in range(len(kk)):
            #             if len(kk[i]['name'])==0:
            #                 maxi = max(maxi, int(kk[i]['n']))
            #                 break
            # if le != 0:
            #     maxmax += 1
            # if maxi > 0:
            #     maxmax = min(maxmax, maxi)
            # if maxmax < 0:
            #     maxmax = 1
        else:
            maxmax = str(req['n'])
        setting = os.path.join(setting, str(maxmax))
        if not os.path.exists(setting):
            os.makedirs(setting, exist_ok=True)
        for i in os.listdir(setting):
            os.remove(os.path.join(setting, i))

    if not os.path.exists(setting):
        os.makedirs(setting)
    # https://docs.djangoproject.com/zh-hans/5.1/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile
    # uploadType = request.FILES['file'].content_type
    
    imgpath = os.path.join(setting, uploadImageName)
    handle_uploaded_file(request.FILES['file'], imgpath)

    uploadImageName, nowpath = replacewithjpg(imgpath)

    if 'ImgbookUpload' in req.keys():
        inpath = os.path.join(basepath, 'imgbook', 'fbook.json')
        find = -9
        kk = []
        if os.path.exists(inpath):
            with open(inpath, 'r', encoding='utf-8') as obj:
                kk = json.load(obj)
                # for i in range(len(kk)):
                #     if str(kk[i]['n'])==str(maxmax):
                #         kk[i]['img'] = uploadImageName
                #         # kk[i]['github'] = ""
                #         # kk[i]['name'] = ""
                #         # kk[i]['readdate'] = ""
                #         # kk[i]['ratio'] = ""
                #         find = 9
                #         break
        if find < 0:
            # kk.append({
            #     "github": "",
            #     "img": uploadImageName,
            #     "name": "",
            #     "img": "",
            #     "finished": False,
            #     "author": "",
            #     "n": maxmax,
            #     "readdate": ""
            # },)
            # find = 9
            kk.append({"github": "", "img": uploadImageName, "name": "", \
                       "ratio": "", "n": maxmax, "readdate": "", 'finished':False, 'author':""})
        fbookmute.acquire()
        with open(inpath, 'w', encoding='utf-8') as obj:
            json.dump(kk, obj, indent=2, ensure_ascii=False)
        fbookmute.release()

    if 'person' in req.keys() and len(os.listdir(setting)) > 1 and len(xiang)!=0:
        os.remove(os.path.join(setting, xiang))

    return JsonResponse( { "ret" : True} , safe = False)

membermutex = Semaphore(value=1)
def NicknameSetting(request):
    global path, membermutex
    body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    req = json.loads(body)

    # req = request.POST.dict()
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    rz = renzheng(request)
    rzret = json.loads(rz.content)
    passed = False
    if "mail" in req.keys():
        get = json.loads(getusername(request).content)
        if not rzret['ret'] and 'password' in req.keys() and check_logined(req['mail'], req['password']):
            basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
            passed = True
            if f"{get['mail']}" not in req['url']:
                return JsonResponse( { "ret" : -100} , safe = False)
        elif get['ret']==2 and not rzret['ret']:
            return JsonResponse( { "ret" : -100} , safe = False)
    if not passed and not rzret['ret']:
        return JsonResponse( { "ret" : -100} , safe = False)
    elif not passed and rzret['ret']:
        get = json.loads(getusername(request).content)
        if get['ret'] > 0:
            basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")

    if (passed or rzret['ret']) and 'modifiednickname' in req.keys() and len(req["modifiednickname"])!=0:
        addpa = os.path.abspath(__file__ + "/../../")
        member = os.path.join(addpa, "..", "article", 'member.txt')
        
        cll = []

        prepa = os.path.abspath(__file__ + "/../../../")
        oldpassword = os.path.join(prepa, 'article', 'oldpassword')
        if not os.path.exists(oldpassword):
            os.makedirs(oldpassword)
        postDate = datetime.fromtimestamp(time.time() +timezone).isoformat()[:19].replace(":", "_")
        shutil.copyfile(member, os.path.join(oldpassword, postDate + '_member.txt'))

        with open(member, 'r', encoding='utf-8') as fp:
            for i in fp.readlines():
                cll.append(i)
                i = i.strip().split("<》!=$)(=$@")
                mail = i[1]
                id = mail.index("@")
                # rpl = str(1 << 2)
                ml = mail[:id] #.replace(rpl, "#")
                if (passed and ml==get['urlmail'] and req['password']==i[0]) or \
                    (rzret['ret'] and get['urlmail']==ml):
                    i[2] = req["modifiednickname"]
                    i = "<》!=$)(=$@".join(i) + '\n'
                    cll.pop()
                    cll.append(i)
        membermutex.acquire()
        with open(member, 'w', encoding='utf-8') as fp:
            fp.write(''.join(cll))
        membermutex.release()
    return JsonResponse( { "ret" : True} , safe = False)

def FormsubmitSetting(request):
    global path, membermutex, ffmute, fleftmute, fbookmute
    body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    req = json.loads(body)

    # req = request.POST.dict()
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    rz = renzheng(request)
    rzret = json.loads(rz.content)
    passed = False
    if "mail" in req.keys():
        get = json.loads(getusername(request).content)
        if not rzret['ret'] and 'password' in req.keys() and check_logined(req['mail'], req['password']):
            basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
            passed = True
            if f"{get['mail']}" not in req['url']:
                return JsonResponse( { "ret" : -100} , safe = False)
        elif get['ret']==2 and not rzret['ret']:
            return JsonResponse( { "ret" : -100} , safe = False)
    if not passed and not rzret['ret']:
        return JsonResponse( { "ret" : -100} , safe = False)
    elif not passed and rzret['ret']:
        get = json.loads(getusername(request).content)
        if get['ret'] > 0:
            basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")

    if 'delete' in req.keys():
        inpath = os.path.join(basepath, 'imgbook', 'fbook.json')
        with open(inpath, 'r', encoding='utf-8') as obj:
            kk = json.load(obj)
            for i in range(len(kk)):
                if str(kk[i]['n'])==str(req['n']):
                    inp = os.path.join(basepath, 'imgbook', str(kk[i]['n']))
                    shutil.rmtree(inp)
                    # for j in os.listdir(inp):
                    #     os.remove(os.path.join(inp, j))
                    # l = kk[i]
                    # l['name'] = ""
                    # l['readdate'] = ""
                    # l['ratio'] = ""
                    # l['img'] = ''
                    # l['github'] = ""
                    # l['finished'] = False
                    # l['author'] = ''
                    kk.remove(kk[i])
                    # kk.append(l)
                    break
        fbookmute.acquire()
        with open(inpath, 'w', encoding='utf-8') as obj:
            json.dump(kk, obj, indent=2, ensure_ascii=False)
        fbookmute.release()
        return JsonResponse( { "ret" : True} , safe = False)

    SettingForm = req['SettingForm']
    if 'Left' not in req.keys() and 'addbook' not in req.keys() and 'clickcard' not in req.keys():
        for j in range(len(SettingForm)):
            if '/$删除$/' in SettingForm[j]['introduction']:
                SettingForm[j]['introduction'] = ""
                SettingForm[j]['link'] = ""
                SettingForm[j]['link_describe'] = ""
                SettingForm[j]['other_describe'] = ""
                SettingForm[j]['button'] = ""
                setting = os.path.join(basepath, 'setting', str(SettingForm[j]['n']))
                for i in os.listdir(setting):
                    os.remove(os.path.join(setting, i))
        file = os.path.join(basepath, 'setting', 'f.json')
        ffmute.acquire()
        with open(file, 'w', encoding='utf-8') as obj:
            json.dump(SettingForm, obj, indent=2, ensure_ascii=False)
        ffmute.release()
    elif 'clickcard' in req.keys():
        inpath = os.path.join(basepath, 'imgbook', 'fbook.json')
        with open(inpath, 'r', encoding='utf-8') as obj:
            kk = json.load(obj)
            for i in range(len(kk)):
                if str(kk[i]['n'])==str(req['n']):
                    inp = os.path.join(basepath, 'imgbook', str(kk[i]['n']))
                    olt = os.listdir(inp)
                    if len(olt) > 0:
                        kk[i]['img'] = olt[0]
                    kk[i]['github'] = req['github']
                    kk[i]['name'] = req['name']
                    kk[i]['readdate'] = req['readdate']
                    kk[i]['ratio'] = req['ratio']
                    kk[i]['finished'] = bool(req['finished'])
                    kk[i]['author'] = req['author']
                    break
        fbookmute.acquire()
        with open(inpath, 'w', encoding='utf-8') as obj:
            json.dump(kk, obj, indent=2, ensure_ascii=False)
        fbookmute.release()
    elif 'addbook' in req.keys():
        onebook = req['addbook']
        inpath = os.path.join(basepath, 'imgbook', 'fbook.json')
        # find = -9
        with open(inpath, 'r', encoding='utf-8') as obj:
            kk = json.load(obj)
            for i in range(len(kk)):
                i = len(kk) - 1
                inp = os.path.join(basepath, 'imgbook', str(kk[i]['n']))
                if kk[i]['name']=="":
                    olt = [ijk for ijk in os.listdir(inp) if '.jpg' in ijk]
                    if len(olt) > 0:
                        kk[i]['img'] = olt[0]
                        kk[i]['github'] = onebook['github']
                        kk[i]['name'] = onebook['name']
                        kk[i]['readdate'] = onebook['readdate']
                        kk[i]['ratio'] = onebook['ratio']
                        kk[i]['finished'] = bool(onebook['finished'])
                        kk[i]['author'] = onebook['author']
                        break
                break
        fbookmute.acquire()
        with open(inpath, 'w', encoding='utf-8') as obj:
            json.dump(kk, obj, indent=2, ensure_ascii=False)
        fbookmute.release()
    else:
        for j in range(len(SettingForm)):
            if '/$删除$/' in SettingForm[j]['introduction']:
                SettingForm[j]['introduction'] = ""
                SettingForm[j]['link'] = ""
                SettingForm[j]['color'] = "#000000"
                SettingForm[j]['button1'] = ""
                SettingForm[j]['button2'] = ""
                SettingForm[j]['button3'] = ""
                setting1 = os.path.join(basepath, 'set_left', str(SettingForm[j]['n']), '1')
                for i in os.listdir(setting1):
                    os.remove(os.path.join(setting1, i))
                setting1 = os.path.join(basepath, 'set_left', str(SettingForm[j]['n']), '2')
                for i in os.listdir(setting1):
                    os.remove(os.path.join(setting1, i))
                setting1 = os.path.join(basepath, 'set_left', str(SettingForm[j]['n']), '3')
                for i in os.listdir(setting1):
                    os.remove(os.path.join(setting1, i))
        file = os.path.join(basepath, 'set_left', 'fleft.json')
        fleftmute.acquire()
        with open(file, 'w', encoding='utf-8') as obj:
            json.dump(SettingForm, obj, indent=2, ensure_ascii=False)
        fleftmute.release()

    return JsonResponse( { "ret" : True} , safe = False)

def placeTopTop(request):
    global allfile
    allfile = None
    # req = request.GET.dict()
    req = json.loads(request.body)
    pathkkk = req["path"]
    
    if '文篇编辑功能展示' in pathkkk:
        return JsonResponse( { "ret" : -100} , safe = False)
        # return JsonResponse( { "path" : pathkkk} , safe = False)

    rz = renzheng(request)
    rzret = json.loads(rz.content)
    passed = False
    if "mail" in req.keys():
        get = json.loads(getusername(request).content)
        if not rzret['ret'] and 'password' in req.keys() and check_logined(req['mail'], req['password']):
            # basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
            passed = True
            if f"/people/{get['mail']}/" not in pathkkk or '.md' not in pathkkk:
                return JsonResponse( { "ret" : -100} , safe = False)
        elif get['ret']==2:
            return JsonResponse( { "ret" : -100} , safe = False)
    if not passed and not rzret['ret']:
        return JsonResponse( { "ret" : -100} , safe = False)
    # elif not passed and rzret['ret']:
    #     get = json.loads(getusername(request).content)
    #     if get['ret'] > 0:
    #         basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")

    dirname = pathkkk.split(os.sep)[-2]
    filename = pathkkk.split(os.sep)[-1]

    postDa = datetime.fromtimestamp(time.time() +timezone).isoformat()[:19].replace(":", "_")
    postDate = postDa.replace("T", "_空格_").replace(":", "_")
    if 'zhihu' in pathkkk:
        postDate = postDa.replace("T", "_").replace(":", "_")[:-2]

    if '20'==dirname[:2]:
        date = dirname[:22]
    else:
        date = postDate
    if 'zhihu_' in pathkkk:
        date = dirname[:16]
        date = date[:10] + " " + date[11:]
        
    dirpath = pathkkk.replace(filename, "")
    
    os.rename(dirpath, dirpath.replace(date, postDate))
    return JsonResponse( { "path" : dirpath.replace(date, postDate + "_") } , safe = False)

# thememutex = Semaphore(value=1)
def themeChange(request):
    global path #, thememutex
    body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    req = json.loads(body)

    # req = request.POST.dict()
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    rz = renzheng(request)
    rzret = json.loads(rz.content)
    passed = False
    if "mail" in req.keys():
        get = json.loads(getusername(request).content)
        if not rzret['ret'] and 'password' in req.keys() and check_logined(req['mail'], req['password']):
            basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
            passed = True
            if f"{get['mail']}" not in req['url']:
                return JsonResponse( { "ret" : -100} , safe = False)
        elif get['ret']==2 and not rzret['ret']:
            return JsonResponse( { "ret" : -100} , safe = False)
    if not passed and not rzret['ret']:
        return JsonResponse( { "ret" : -100} , safe = False)
    elif not passed and rzret['ret']:
        get = json.loads(getusername(request).content)
        if get['ret'] > 0:
            basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")
    
    file = os.path.join(basepath, 'themeColor.txt')
    
    if 'checked1' in req.keys():
        with open(file, 'w', encoding='utf-8') as obj:
            ck = bool(int(req['checked1']))
            if ck:
                rl = '1'
            else:
                rl = '0'
            obj.write( "1===" + rl + '===' + req['Themecolor'] + '\n' )
    else:
        with open(file, 'w', encoding='utf-8') as obj:
            color1 = req['color1']
            color2 = req['color2']
            color3 = req['color3']
            obj.write( "2===" + color1 + '===' + color2 + '===' + color3 + '\n' )
    return JsonResponse( { "ret" : True } , safe = False)

allTraveler = {}
thememutex = Semaphore(value=1)
def getThemeColor(request):
    global path, thememutex, allTraveler
    ip_address = None
    fileTraveler = os.path.abspath(__file__ + "/../../../")
    fileTravelerPath = os.path.join(fileTraveler, 'article', "TravelerStatistics.txt")
    with open(fileTravelerPath, 'r', encoding='utf-8') as obj:
        try:
            TravelerStatistics = int(obj.read().strip())
        except:
            TravelerStatistics = 100
    if 'X-Real-Ip' in request.headers.keys():
        ip_address = request.headers['X-Real-Ip']
    else:
        if 'X-Forwarded-For' in request.headers.keys():
            ip_address = request.headers['X-Forwarded-For']
    if ip_address:
        postDa = int(time.time() + timezone)
        updated = False
        if ip_address not in allTraveler.keys():
            updated = True
        else:
            if postDa - allTraveler[ip_address] > 3600:
                updated = True
        if updated:
            allTraveler[ip_address] = postDa
            TravelerStatistics += 1
            thememutex.acquire()
            with open(fileTravelerPath, 'w', encoding='utf-8') as obj:
                obj.write(str(TravelerStatistics))
            thememutex.release()
        delete = []
        for key, value in allTraveler.items():
            if postDa - value > 3600 * 10:
                delete.append(key)
        for key in delete:
            allTraveler.pop(key)
    # body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    # req = json.loads(body)

    # req = request.POST.dict()
    get = json.loads(getusername(request).content)
    # kk = deepcopy(path).split(get['urlmail'])
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    # basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    if get['ret'] > 0:
        basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")

    file = os.path.join(basepath, 'themeColor.txt')
    if not os.path.exists(file):
        with open(file, 'w', encoding='utf-8') as obj:
            obj.write('1===0===rgb(136, 187, 250)' + '\n')
            return JsonResponse( { "checked1" : False,  "Themecolor":"rgb(136, 187, 250)"} , safe = False)

    with open(file, 'r', encoding='utf-8') as obj:
        ij = obj.read().strip().split("===")
        if (len(ij)==1 and ij[0]=='') or len(ij)==0:
            with open(file, 'w', encoding='utf-8') as obj:
                obj.write('1===0===rgb(136, 187, 250)' + '\n')
                return JsonResponse( { "checked1" : False,  "Themecolor":"rgb(136, 187, 250)"} , safe = False)
        if ij[0]=='1':
            ck = bool(int(ij[1]))
            if ck:
                rl = True
            else:
                rl = False
            return JsonResponse( { "checked1" : rl,  "Themecolor":ij[2], 'type':'1', "TravelerStatistics":TravelerStatistics} , safe = False)
        else:
            return JsonResponse( { "color1" : ij[1],  "color2":ij[2], "color3":ij[3], 'type':'2', "TravelerStatistics":TravelerStatistics} , safe = False)

kshoucangmutex = Semaphore(value=1)
def kshoucang(request):
    global path, kseamutex, kshoucangmutex
    body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    req = json.loads(body)

    # req = request.POST.dict()
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    # kkkpath = deepcopy(basepath)
    if 'postkey' in req.keys():
        rz = renzheng(request)
        rzret = json.loads(rz.content)
    else:
        rzret = {"ret":False}
    passed = False
    if "mail" in req.keys():
        get = json.loads(getusername(request).content)
        if not rzret['ret'] and 'password' in req.keys() and check_logined(req['mail'], req['password']):
            basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
            passed = True
            # if f"{get['mail']}" not in req['url']:
            #     return JsonResponse( { "ret" : -100} , safe = False)
        elif get['ret']==2 and not rzret['ret']:
            return JsonResponse( { "ret" : -100} , safe = False)
    if not passed and not rzret['ret']:
        return JsonResponse( { "ret" : -100} , safe = False)
    elif not passed and rzret['ret']:
        get = json.loads(getusername(request).content)
        if get['ret'] > 0:
            basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")
    
    filepath = os.path.join(basepath, 'kshoucang.json')

    if not os.path.exists(filepath):
        kshoucangmutex.acquire()
        with open(filepath, 'w', encoding='utf-8') as obj:
            json.dump([], obj, indent=2, ensure_ascii=False)
        kshoucangmutex.release()
    kshoucangmutex.acquire()
    with open(filepath, 'r', encoding='utf-8') as obj:
        try:
            kshoucangJson = json.load(obj)
        except:
            kshoucangJson = []
        if req['click']:
            kshoucangJson.append(req['title'] + "===" + f"{req['mail']}#/csdn/markdown_detail/{req['mail']}?plan="+ req['path'])
        else:
            try:
                kshoucangJson.remove(req['title'] + "===" + f"{req['mail']}#/csdn/markdown_detail/{req['mail']}?plan=" + req['path'])
            except:
                pathkkk = req['path']
                tails = pathkkk.split(os.sep)[-1]
                par = pathkkk.replace(tails, "")
                tails = par.split("_")[-1]
                par = par.replace(tails, "")
                for ij in kshoucangJson:
                    if par in ij:
                        kshoucangJson.remove(ij)
                        break
    kshoucangmutex.release()

    kshoucangmutex.acquire()
    with open(filepath, 'w', encoding='utf-8') as obj:
        json.dump(kshoucangJson, obj, indent=2, ensure_ascii=False)
    kshoucangmutex.release()

    pathkkk = req['path']
    tails = pathkkk.split(os.sep)[-1]
    if tails not in kseamutex.keys():
        kseamutex[tails] = Semaphore(value=1)
    # kk = Semaphore(value=1)
    jsonpath = pathkkk.replace(tails, 'upvote_comment.json')
    
        # with open(file, 'w', encoding='utf-8') as obj:
        #     json.dump(Setting_Formel, obj, indent=2, ensure_ascii=False)
    kseamutex[tails].acquire()
    with open(jsonpath, 'r', encoding='utf-8') as obj:
        try:
            jsonfile = json.load(obj)
        except:
            jsonfile = {"upvote":[], 'comment':[], 'kshoucang':[]}
        if req['click']:
            jsonfile['kshoucang'].append(req['mail'])
            jsonfile['kshoucang'] = list(set(jsonfile['kshoucang']))
        else:
            try:
                jsonfile['kshoucang'].remove(req['mail'])
            except:
                pass
    kseamutex[tails].release()

    kseamutex[tails].acquire()
    with open(jsonpath, 'w', encoding='utf-8') as obj:
        json.dump(jsonfile, obj, indent=2, ensure_ascii=False)
    kseamutex[tails].release()
    kseamutex.pop(tails)
    return JsonResponse( { "ret" : True } , safe = False)

# kcommentmutex = {}
def comment_add(request):
    global path, kseamutex #, kcommentmutex
    body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    req = json.loads(body)

    # req = request.POST.dict()
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    if 'postkey' in req.keys():
        rz = renzheng(request)
        rzret = json.loads(rz.content)
    else:
        rzret = { "ret":False }
    passed = False
    if "mail" in req.keys():
        get = json.loads(getusername(request).content)
        if not rzret['ret'] and 'password' in req.keys() and check_logined(req['mail'], req['password']):
            basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
            passed = True
            # if f"{get['mail']}" not in req['url']:
            #     return JsonResponse( { "ret" : -100} , safe = False)
        elif get['ret']==2 and not rzret['ret']:
            return JsonResponse( { "ret" : -100} , safe = False)
    if not passed and not rzret['ret']:
        return JsonResponse( { "ret" : -100} , safe = False)
    elif not passed and rzret['ret']:
        get = json.loads(getusername(request).content)
        if get['ret'] > 0:
            basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")
    
    pathkkk = req['path']
    tails = pathkkk.split(os.sep)[-1]
    if tails not in kseamutex.keys():
        kseamutex[tails] = Semaphore(value=1)
    # kk = Semaphore(value=1)
    jsonpath = pathkkk.replace(tails, 'upvote_comment.json')
    
        # with open(file, 'w', encoding='utf-8') as obj:
        #     json.dump(Setting_Formel, obj, indent=2, ensure_ascii=False)
    postDate = datetime.fromtimestamp(time.time() +timezone).isoformat()[:19] #.replace(":", "_")
    postDate = postDate.replace("T", " ")
    kseamutex[tails].acquire()
    with open(jsonpath, 'r', encoding='utf-8') as obj:
        try:
            jsonfile = json.load(obj)
        except:
            jsonfile = {"upvote":[], 'comment':[], 'kshoucang':[]}
        jsonfile['comment'].append(["http://zoujiu.com.cn/"+req['mail'], req['comment'], " - - - "+ postDate, req['mail'], get['nickname']])
    kseamutex[tails].release()

    kseamutex[tails].acquire()
    with open(jsonpath, 'w', encoding='utf-8') as obj:
        json.dump(jsonfile, obj, indent=2, ensure_ascii=False)
    kseamutex[tails].release()
    kseamutex.pop(tails)
    return JsonResponse( { "ret" : True } , safe = False)

def upvote_change(request):
    global path, kseamutex
    body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    req = json.loads(body)

    # req = request.POST.dict()
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    if 'postkey' in req.keys():
        rz = renzheng(request)
        rzret = json.loads(rz.content)
    else:
        rzret = {"ret":False}
    passed = False
    if "mail" in req.keys():
        get = json.loads(getusername(request).content)
        if not rzret['ret'] and 'password' in req.keys() and check_logined(req['mail'], req['password']):
            basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
            passed = True
            # if f"{get['mail']}" not in req['url']:
            #     return JsonResponse( { "ret" : -100} , safe = False)
        elif get['ret']==2 and not rzret['ret']:
            return JsonResponse( { "ret" : -100} , safe = False)
    if not passed and not rzret['ret']:
        return JsonResponse( { "ret" : -100} , safe = False)
    elif not passed and rzret['ret']:
        get = json.loads(getusername(request).content)
        if get['ret'] > 0:
            basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")
    
    pathkkk = req['path']
    tails = pathkkk.split(os.sep)[-1]
    if tails not in kseamutex.keys():
        kseamutex[tails] = Semaphore(value=1)
    # kk = Semaphore(value=1)
    jsonpath = pathkkk.replace(tails, 'upvote_comment.json')
    
        # with open(file, 'w', encoding='utf-8') as obj:
        #     json.dump(Setting_Formel, obj, indent=2, ensure_ascii=False)
    kseamutex[tails].acquire()
    with open(jsonpath, 'r', encoding='utf-8') as obj:
        try:
            jsonfile = json.load(obj)
        except:
            jsonfile = {"upvote":[], 'comment':[], 'kshoucang':[]}
        if req['click']:
            jsonfile['upvote'].append(req['mail'])
            jsonfile['upvote'] = list(set(jsonfile['upvote']))
        else:
            try:
                jsonfile['upvote'].remove(req['mail'])
            except:
                pass
    kseamutex[tails].release()

    kseamutex[tails].acquire()
    with open(jsonpath, 'w', encoding='utf-8') as obj:
        json.dump(jsonfile, obj, indent=2, ensure_ascii=False)
    kseamutex[tails].release()
    kseamutex.pop(tails)
    return JsonResponse( { "ret" : True } , safe = False)

globaltext = \
"""
同一个段落的
同一个段落的

两个不同的段落

两个不同的段落

### 表格
| Option | Description | row |
| ------ | ----------- | ----- |
| data   | path to data files to supply the data that will be passed into templates. | row |
| engine | engine to be used for processing templates. Handlebars is the default. | row |
| ext    | extension to be used for dest files. | row |


表格向右对齐
| Option | Description | row |
| ------: | -----------: | -----: |
| data   | path to data files to supply the data that will be passed into templates. | row |
| engine | engine to be used for processing templates. Handlebars is the default. | row |
| ext    | extension to be used for dest files. | row |
| ext    | extension to be used for dest files. | row |


### Horizontal 分隔

---------

********

# 一级标题
## 二级标题
### 三级标题

### 数学
$f(x)=f(x_0)+f'(x_0)(x-x_0)+f''(x_0)\\frac{(x-x_0)^2}{2!}+f'''(x_0)\\frac{(x-x_0)^3}{3!}+...+f^{(n)}(x_0)\\frac{(x-x_0)^n}{n!}+O((x-x_0)^n)$

$\\sum_{i=0}^{n}\\frac{f^{(n)}(x_0)}{n!}(x-x_0)^n$

[kalman推导](https://zoujiu.com.cn/#/csdn/markdown_detail/*?plan=/home/admin/vue-project/article/zhihu_spider_selenium/article/2023-08-22_14_00_%E5%8D%A1%E5%B0%94%E6%9B%BC%E6%BB%A4%E6%B3%A2%E6%8E%A8%E5%AF%BC%E5%92%8C%E5%BA%94%E7%94%A8Kalman_%E7%A9%BA%E6%A0%BC_filter_IP_%E5%B1%9E%E5%9C%B0%E4%B8%8A%E6%B5%B7/%E5%8D%A1%E5%B0%94%E6%9B%BC_.md): 

$\\left[\\begin{matrix}x_k\\\\y_k\\\\v_{x-k}\\\\v_{y-k}\\end{matrix}\\right]=\\left[\\begin{matrix}1&0&\\Delta t&0\\\\0&1&0&\\Delta t\\\\0&0&1&0\\\\0&0&0&1\\end{matrix}\\right] \left[\\begin{matrix}x_{k-1}\\\\y_{k-1}\\\\v_{x-(k-1)}\\\\v_{y-(k-1)}\\end{matrix}\\right]+\\left[\\begin{matrix}\\frac{1}{2}\\Delta t^2&0\\\\0&\\frac{1}{2}\\Delta t^2\\\\\Delta t & 0\\\\0 & \Delta t\end{matrix}\\right]\\left[\\begin{matrix}a_x\\\\a_y\\end{matrix}\\right]$

### 强调
**加粗字体**

*倾斜文本*

~~删除线~~

`123456` 和着重 `和着重`

>引用
>引用
引用
引用

引用

### 容器
::: warning
~~容器container~~
:::

网址：[http://zoujiu.com.cn](http://zoujiu.com.cn)

特殊符号$$，表示方式是：$$$$

## 列表

无序

+ 符合`+`, `-`, 或 `*`产生列表
+ 2个空格代表子列表:
  - 符号变化以后强制产生列表:
    * Ac tristique libero volutpat at
    + Facilisis in pretium nisl aliquet
    - Nulla volutpat aliquam velit
+ Very easy!

有序

1. Lorem ipsum dolor sit amet
2. Consectetur adipiscing elit
3. Integer molestie lorem at massa


1. You can use sequential numbers...
1. ...or keep all the numbers as `1.`

用偏置开始的:

9. foo
1. bar

### code
```c++
/*
comment for this code, it is a demo for show.
the second line.
#include<iostream>
class Solution {
public:
    string convert(string s, int numRows) {
        string ret, tmp[numRows];
        int i = 0;
        vector<int> tr;
        int k = tr[0];
        while(i < s.length()) {
*/
#include<iostream>
#include "stdio.h"
#include "stdlib.h" // 注释 #include<iostream> string convert(string s, int numRows)
#include<vector>
#include<string>
#include<unordered_map>
#include<map>
#include<set>

class Solution {// 注释 #include<iostream> string convert(string s, int numRows)
public:
    string convert(string s, int numRows) {
        string ret, tmp[numRows];
        int i = 0;
        vector<int> tr;
        int k = tr[0];
        while(i < s.length()) {
            for(int k = 0; k < numRows && i < s.length(); k++) {
                tmp[k] += s[i++];
            }
            for(int k = numRows-2; k > 0 && i < s.length(); k--) {
                tmp[k] += s[i++];
            }
        }
        for(int k = 0; k < numRows; k++) {
            ret += tmp[k];
        }
        return ret;
    }
};
```

上传图片功能：


<img src="animal.JPG">


```python3 []
# https://github.com/ZouJiu1/KalmanFilter_numpy
import numpy as np
import matplotlib.pyplot as plt

class KalmanFilter(object):
    def __init__(self, dt, u_x, u_y, std_acc, x_std_meas, y_std_meas):
        self.dt = dt
        #x和y方向的加速度
        self.u = np.array([[u_x], [u_y]])
        self.std_acc = std_acc
        #状态转移矩阵，Define the State Transition Matrix A
        self.F = np.array([[1, 0, dt, 0], [0, 1, 0, dt], [0, 0, 1, 0], [0, 0, 0, 1]])
        #外界控制矩阵，加速度，Define the Control Input Matrix B
        self.B = np.array([[(dt**2) * (3/6), 0], [0, (dt**2) * (3/6)], [dt, 0], [0, dt]])
        #误差协方差矩阵，Initial Covariance Matrix
        self.p = np.eye(2*2)
        #状态噪声的方差Q，状态噪声w_k符合均值是0，方差是std_acc的正态分布，Initial Process Noise Covariance
        self.Q = np.array([[((3/6)**2)*np.power(dt, 2*2), 0, (3/6)*np.power(dt, 3), 0], \
                           [0, ((3/6)**2)*np.power(dt, 2*2), 0, (3/6)*np.power(dt, 3)], \
                           [(3/6)*np.power(dt, 3), 0, np.power(dt, 2), 0], \
                           [0, (3/6)*np.power(dt, 3), 0, np.power(dt, 2)]]) * (std_acc**2)
        #观测噪声的方差R，，观测噪声v_k符合均值是0，方差是std_meas的正态分布，Initial Measurement Noise Covariance
        #共两个方向的，x和y方向
        self.R = np.array([[x_std_meas**2, 0], [0, y_std_meas**2]])
        #predict转测量的矩阵，Define Measurement Mapping Matrix
        self.H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]])
        # Intial State
        self.x = np.array([[0], [0], [0], [0]])

        print(self.Q)

    def predict(self):
        self.x = np.dot(self.F, self.x) + np.dot(self.B, self.u)
        self.p = np.dot(self.F, np.dot(self.p, self.F.T)) + self.Q
        return self.x[:2]
        
    def update(self, z):
        S = np.dot(self.H, np.dot(self.p, self.H.T)) + self.R
        K = np.dot(self.p, np.dot(self.H.T, np.linalg.inv(S)))
        self.x = self.x + np.dot(K, z - np.dot(self.H, self.x))
        self.p = np.dot(np.eye(len(self.p)) - np.dot(K, self.H), self.p)
        return self.x[0:2]

def main():
    dt = 0.1
    
    u= 2               # 加速度
    std_acc = 0.6     # 状态噪声的方差Q，状态噪声w_k符合均值是0，方差是std_acc的正态分布
    std_meas = 1.3     # 观测噪声的方差R，，观测噪声v_k符合均值是0，方差是std_meas的正态分布
    
    t = np.arange(0, 100, dt)
    klf = KalmanFilter(dt, u, std_acc, std_meas)
    # real_track = 0.1 * ((t**2) - t)
    real_track = 100 * np.cos(t)

    predictions = []
    measurements = []
    for i in real_track:
        z = klf.H * i + np.random.normal(0, 30)
        predictions.append(klf.predict()[0])
        measurements.append(z.item(0))
        klf.update(z.item(0))

    fig = plt.figure()

    fig.suptitle('Kalman filter for tracking cos', fontsize=20)

    plt.plot(t, measurements, label='Measurements', color='b',linewidth=0.5)

    plt.plot(t, np.array(real_track), label='Real Track', color='m', linewidth=1.5)
    plt.plot(t, np.squeeze(predictions), label='Kalman Filter Prediction', color='r', linewidth=1.5)

    plt.xlabel('Time (s)', fontsize=20)
    plt.ylabel('Position (m)', fontsize=20)
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()
```

### html

```html []
<template>
  <div id='app'>
  <el-container class="layout-container-demo">
    <el-header style="text-align: center; font-size: 200px; color: #00ff00;">
      <div class="toolbar" >
        <span style="text-align:center; margin-right: 100px; margin-top: 10px">邹九的个人页面</span>
        <!-- <el-avatar shape="square" :size="100" src="/animal.JPG" style="align:right; margin-top: 2px" /> -->
        <el-image src="/article/animal.JPG" style="width:3em; margin-top: 0px" />
        <!-- <link rel="icon" href="/animal.JPG"> -->
      </div>
    </el-header>
    <el-container>
      <el-aside style="width:auto;font-size:30px;" id="elaside">
          <el-menu 
          active-text-color="#ffd04b"
          :onclike="click"
          class="el-menu-vertical-demo">
          <el-menu-item 
          id='el-menu-item-1' 
          @click="clickhome"
          >
          <!-- <router-link :to="{ name: 'home' }"> -->
            首页
          <!-- </router-link> -->
          </el-menu-item>

          <el-menu-item 
            @click="clickthink"
            id='el-menu-item-7'
            >
            <!-- <router-link :to="{ name: 'csdn' }"> -->
              片段
            <!-- </router-link> -->
          </el-menu-item>
          <el-menu-item 
            @click="clicktravel"
            id='el-menu-item-7'
            >
            <!-- <router-link :to="{ name: 'csdn' }"> -->
              游客
            <!-- </router-link> -->
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
    <div style="color:#666;padding:3px 0;width:100%;background-color: #f5f5f5;">
      <el-link type="primary" href="https://beian.miit.gov.cn/" style="margin-left:20px;" target="_blank" >
        湘ICP备2024086536号-1
      </el-link>
    </div>
  </el-container>
</div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'app',
  data() {},
  watch: {},
  methods: {
    clickvideo() {
      this.$router.push({ path: '/video', hash: '#video'});
    },
    clicktravel() {
      this.$router.push({ path: '/travel', hash: '#travel'});
    },
  },
}
</script>

<style scoped>
html,body,#app{
  height:100%;
  width:100%;
  margin: 0px;
  padding: 0px;
}
.layout-container-demo{
  height:calc(99vh); /*https://blog.csdn.net/qq_41499782/article/details/102624538*/
}
.layout-container-demo .el-header {
  position: relative;
  background-color: var(--el-color-primary-light-3);
  color: var(--el-text-color-primary);
}
.layout-container-demo .el-aside {
  color: var(--el-text-color-primary);
  background: var(--el-color-primary-light-3);
}
.layout-container-demo .el-menu {
  --el-menu-bg-color: #545c64;
  --el-menu-text-color: #ffffff;
  --el-menu-active-color: #000000;
  border-right: none;
}
.layout-container-demo .el-main {
  padding: 0;
}
.layout-container-demo .el-menu-item:hover { /*https://blog.csdn.net/lannieZ/article/details/124007821*/
  outline: 1 !important;
  color: #6681fa !important;
  background: #eeffff !important;
}
.layout-container-demo .el-menu-item.is-active { /*https://blog.csdn.net/lannieZ/article/details/124007821*/
  color: #6681fa !important;
  background: #ff0000 !important;
}
.layout-container-demo .toolbar{
  color: #ffffff;
}
/*https://developer.mozilla.org/zh-CN/docs/Web/CSS/:active#%E8%A7%84%E8%8C%83*/
a:link {
  /* 未访问链接 */
  color: blue;
}
a:visited {
  /* 已访问链接 */
  color: purple;
}
a:hover {
  /* 用户鼠标悬停 */
  background: #aafaaa;
}
a:active {
  /* 激活链接 */
  color: red;
}

p:active {
  /* 激活段落 */
  background: #eee;
}
</style>
```

### javascript 

```javascript []
import './assets/main.css'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router/routers.js'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const app = createApp(App)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}

app.use(router)
app.use(ElementPlus)
app.mount('#app')

```

### java

```java []
// Source code is decompiled from a .class file using FernFlower decompiler.
package com.horstmann.corejava;

import java.time.LocalDate;

public class Employee {
   private String name;
   private double salary;
   private Double salary;
   private LocalDate hireDay;
   private localDate hireDay;

   public Employee(String var1, double var2, int var4, int var5, int var6) {
      this.name = var1;
      this.salary = var2;
      this.hireDay = LocalDate.of(var4, var5, var6);
   }

   public String getName() {
      return this.name;
   }

   public double getSalary() {
      return this.salary;
   }

   public LocalDate getHireDay() {
      return this.hireDay;
   }

   public void raiseSalary(double var1) {
      double var3 = this.salary * var1 / 100.0;
      this.salary += var3;
   }
}
```

```java []
// Source code is decompiled from a .class file using FernFlower decompiler.
package com.horstmann.corejava;
package draw;
import com.horstmann.corejava.Employee;
import java.io.PrintStream;
import java.awt.*;
import java.awt.geom.*;
import javax.swing.*;

/**
 * @version 1.34 2018-04-10
 * @author Cay Horstmann
 */
public class DrawTest
{
   public static void main(String[] args)
   {
      EventQueue.invokeLater(() ->
         {
            var frame = new DrawFrame();
            frame.setTitle("DrawTest");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setVisible(true);
         });
   }
}

/**
 * A frame that contains a panel with drawings.
 */
class DrawFrame extends JFrame
{
   public DrawFrame()
   {      
      add(new DrawComponent());
      pack();
   }
}

/**
 * A component that displays rectangles and ellipses.
 */
class DrawComponent extends JComponent
{
   private static final int DEFAULT_WIDTH = 400;
   private static final int DEFAULT_HEIGHT = 400;

   public void paintComponent(Graphics g)
   {
      var g2 = (Graphics2D) g;

      // draw a rectangle

      double leftX = 100;
      double topY = 100;
      double width = 200;
      double height = 150;

      var rect = new Rectangle2D.Double(leftX, topY, width, height);
      g2.draw(rect);

      // draw the enclosed ellipse

      var ellipse = new Ellipse2D.Double();
      ellipse.setFrame(rect);
      g2.draw(ellipse);

      // draw a diagonal line

      g2.draw(new Line2D.Double(leftX, topY, leftX + width, topY + height));

      // draw a circle with the same center

      double centerX = rect.getCenterX();
      double centerY = rect.getCenterY();
      double radius = 150;

      var circle = new Ellipse2D.Double();
      circle.setFrameFromCenter(centerX, centerY, centerX + radius, centerY + radius);
      g2.draw(circle);
   }
   
   public Dimension getPreferredSize()
   {
      return new Dimension(DEFAULT_WIDTH, DEFAULT_HEIGHT);
   }
}
```
"""

def getPrimaryText(request):
    global globaltext
    return JsonResponse( { "text": globaltext} , safe = False)

def md2():
    inp = '''
      # title

      ## input

      $\frac{1}{6}$

      * number one
      * number

      **strong**

      > reference
    '''
    k = markdown2.markdown(inp)
    n = 0

if __name__=="__main__":
    md2()
