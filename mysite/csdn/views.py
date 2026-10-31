from django.http import HttpResponse
# from rest_framework.response import Response
# from rest_framework import status
from django.http import JsonResponse
import os
import requests
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
from mysite.projectpaths import web_dir_of, find_top_marker, TOP_CSDN
import siteconfig   # 站点统一配置（mysite/site_config.json，修改即时生效）
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
    return i.replace(":", "_").replace("-问号-", "？").replace("_问号_", "？").replace("_感叹号_", "！").replace("-感叹号-", "！").\
              replace("小于", "<").replace("大于", ">").replace("_逗号_", "，").replace("-逗号-", "，").\
              replace("_空格_", " ").replace("-空格-", " ").replace("_冒号_", "：").replace("-冒号-", "：").\
              replace("_顿号_", "、").replace("-顿号-", "、")

allfile = {}
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
            currentpage = int(siteconfig.get('default_currentpage'))
        try:
            pagesize = int(req["pagesize"])
        except:
            pagesize = int(siteconfig.get('default_pagesize_csdn'))
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
        allfile.pop(basepath, None)
    collect = []
    search = search.split(" ")
    while '' in search:
        search.remove("")
    # 当前查看者的账号（用于计算点赞/收藏高亮）；未登录按 '#' 处理，不参与个性化
    maillogin = req['mail'] if ('mail' in req.keys() and len(req['mail'])!=1) else '#'
    cache = allfile.get(basepath)
    # 缓存只存「中性全量列表」；带搜索词时必须实时构建（搜索结果不入缓存，见下方存储条件）
    if cache is not None and len(search)==0:
        result_ret = cache[(currentpage-1) * pagesize : currentpage * pagesize]
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
        # 点赞/收藏高亮是查看者个人状态：对本页条目浅拷贝后按请求者重算，
        # 防止高亮状态随首个查看者的身份固化进缓存、泄漏给其他查看者
        if maillogin != '#':
            ret = [dict(x, click=(maillogin in x['upvote']), clickshoucang=(maillogin in x['kshoucang'])) for x in ret]
        return JsonResponse({"collect":ret, "length":len(cache)}, safe = False)

    # jsonfile = os.path.join(addpath, 'article', 'idtranslate.json')
    # with open(jsonfile, 'r', encoding='utf-8') as obj:
    #     jsonfp = json.loads(obj)
    # alldate = []
    TOPTOP = []
    # 目录结构不完整的用户（如数据迁移/目录被删）访问文篇页时，目录可能不存在，直接 listdir 会 500
    os.makedirs(basepath, exist_ok=True)
    for i in os.listdir(basepath):
        nth = os.path.join(basepath, i)
        if not os.path.isdir(nth):
            continue
        if '20'==i[:2] or '21' == i[:2]:
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
            modifyTime = int(os.path.basename(markdownpth).replace("_markdown.md", "").replace(" ", "").replace("_", "").replace("-", "").replace(":", ""))
            # modifyTime = int(datetime.fromtimestamp(modifyTime).isoformat()[:19].replace("T", " ").replace(" ", "").replace(":", "").replace("-", ""))
        else:
            modifyTime = int(date.replace(" ", "").replace(":", "").replace("-", ""))
        upvotecomment = os.path.join(nth, 'upvote_comment.json')
        if not os.path.exists(upvotecomment):
            # 用 open 创建空文件，避免 os.system 每次 fork 子进程（热点循环里开销很大）
            open(upvotecomment, 'a').close()
        upvote = []
        comment = []
        kshoucang = []
        click = False
        clickshoucang = False
        if len(markdownpth) > 0:
            with open(markdownpth, 'r', encoding = 'utf-8') as obj:
                markdown = obj.read().strip()
        else:
            markdownpth = os.path.join(nth, 'markdown.md')
            with open(markdownpth, 'w', encoding = 'utf-8') as obj:
                obj.write(markdown)
        # with open(file, 'w', encoding='utf-8') as obj:upvote_comment
        #     json.dump(Setting_Formel, obj, indent=2, ensure_ascii=False)
        tails = markdownpth.split(os.sep)[-1]
        # 原子创建锁；锁对象永不 pop，否则并发下其他线程会 KeyError 或重建第二把锁
        sem = kseamutex.setdefault(tails, Semaphore(value=1))
        sem.acquire()
        try:
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
                    # 点赞/收藏高亮不入缓存：构建时一律中性 False，返回前按查看者重算（见函数末尾）
        finally:
            sem.release()
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
        inlist = False
        if len(search)==0:
            collect.append({"date":date.replace("_", ":"), "title": title, "markdown": markdown[:200], \
                            "path":markdownpth, "upvote":upvote, 'comment':comment, 'click':click, \
                            'clickshoucang':clickshoucang, 'kshoucang':kshoucang, "modifyTime":modifyTime, 'isTop':False})
            inlist = True
        else:
            for j in search:
                if j in markdown or j in i or j.replace(":", "_") in i:
                    collect.append({"date":date.replace("_", ":"), "title": title, "markdown": markdown[:200], \
                                    "path":markdownpth, "upvote":upvote, 'comment':comment, 'click':click, \
                                    'clickshoucang':clickshoucang, 'kshoucang':kshoucang, "modifyTime":modifyTime, 'isTop':False})
                    inlist = True
                    break

        if inlist == True:
            topPath = find_top_marker(nth, TOP_CSDN)
            if os.path.exists(topPath):
                topTime = os.path.getmtime(topPath)
                collect.pop()
                inserted = False
                for itop in range(len(TOPTOP)):
                    if TOPTOP[itop]['topTime'] < topTime:
                        TOPTOP.insert(itop, {"date":date.replace("_", ":"), "title": title, "markdown": markdown[:200], \
                                "path":markdownpth, "upvote":upvote, 'comment':comment, 'click':click, \
                                'clickshoucang':clickshoucang, 'kshoucang':kshoucang, "modifyTime":modifyTime,
                                'isTop':True, "topTime":os.path.getmtime(topPath)})
                        inserted = True
                        break
                if inserted==False:
                    TOPTOP.append({"date":date.replace("_", ":"), "title": title, "markdown": markdown[:200], \
                                "path":markdownpth, "upvote":upvote, 'comment':comment, 'click':click, \
                                'clickshoucang':clickshoucang, 'kshoucang':kshoucang, "modifyTime":modifyTime,
                                'isTop':True, "topTime":os.path.getmtime(topPath)})

    collect = sorted(collect.__iter__(), key = lambda x:x['modifyTime'], reverse=True)
    collect = TOPTOP + collect

    # 只缓存「无搜索词且未排除leetcode」的中性全量列表；搜索/过滤结果属于当前请求，存进去会被当成全量复用
    if len(search)==0 and checke==True:
        allfile[basepath] = collect
    ret = collect[(currentpage-1) * pagesize : currentpage * pagesize]
    # 点赞/收藏高亮按当前查看者重算（dict 浅拷贝，避免改到缓存里的条目）
    if maillogin != '#':
        ret = [dict(x, click=(maillogin in x['upvote']), clickshoucang=(maillogin in x['kshoucang'])) for x in ret]
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
    _domain = siteconfig.get('site_domain')
    if not notify_guanliyuan:
        if not modify:
            msg.set_content(f'注册需要的验证数字串：{number}\n\n\n{_domain}')
            msg['Subject'] = f"{siteconfig.get('site_name')}注册验证数字串"
        else:
            msg.set_content(f'修改密钥需要的验证数字串：{number}\n\n\n{_domain}')
            msg['Subject'] = f"{siteconfig.get('site_name')}修改密钥数字串"
    if notify_guanliyuan:
        msg.set_content(notify_guanliyuan[1])
        msg['Subject'] = f"{siteconfig.get('site_name')}{notify_guanliyuan[0]}"
    msg['From'] = siteconfig.get('smtp_user')
    msg['To'] = mail
    # smtplib.SMTP()
    smpt = smtplib.SMTP_SSL(siteconfig.get('smtp_host'), port=int(siteconfig.get('smtp_port')))
    # smpt.connect("smtp.qq.com", port=465)
    try:
        smpt.login(user=siteconfig.get('smtp_user'), password=siteconfig.get('smtp_password'))
    except:
        return "999999"
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
    if number=='999999':
        return JsonResponse({"number":3})
    elif number[0]=='-':
        return JsonResponse({"number":0})
    addpa = os.path.abspath(__file__ + "/../../")
    yonghu = os.path.join(addpa, "..", "article", 'register.txt')
    sendmutex.acquire()
    with open(yonghu, 'a+', encoding='utf-8') as obj:
        obj.write(str(time.time() + timezone) + f'<》!=$)(=$@{mail}<》!=$)(=$@{number}\n')
    sendmutex.release()
    return JsonResponse({"number":1}, safe = False)

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
            if len(i) < 2:
                # 空行/脏行跳过，防 member.txt 尾部空行导致全站检查 500
                continue
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
  }
]
# 个人卡片/左侧卡片配置槽位总数（前后端一致，前端 mainpage.vue SETTING_SLOTS_MAX 同步）
SETTING_SLOTS_MAX = 60
LeftSetting_Formel += [
  {"introduction": "", "link": "", "color": "#000000", "button1": "", "button2": "", "button3": "", "n": i}
  for i in range(8, SETTING_SLOTS_MAX + 1)
]
Setting_Formel = [
        {"introduction":"姓名", "link":"", "link_describe":"邹九", 'other_describe':"", "button":"", 'n':1},
        {"introduction":"邮箱", "link":"", "link_describe":"1069679911@qq.com", 'other_describe':"", "button":"", 'n':2},
        {"introduction":"攀拓PAT", "link":"https://github.com/ZouJiu1/PAT", "link_describe":"github.com/ZouJiu1/PAT", 'other_describe':"甲级/乙级基本都刷完了", "button":"PAT证书", 'n':3},
        {"introduction":"Leetcode主页", "link":"https://leetcode.cn/u/shiheyingzhe/", "link_describe":"leetcode.cn/u/shiheyingzhe/", 'other_describe':"刷完了406道题目", "button":"", 'n':4},
        {"introduction":"Kaggle主页", "link":"https://www.kaggle.com/shiheyingzhe", "link_describe":"www.kaggle.com/shiheyingzhe", 'other_describe':"", "button":"", 'n':5},
      ]
Setting_Formel += [
        {"introduction":"", "link":"", "link_describe":"", 'other_describe':"", "button":"", 'n':i}
        for i in range(6, SETTING_SLOTS_MAX + 1)
      ]

memmute = Semaphore(value=1)  # 占位，在下方 regmute 定义处统一为同一把锁
ffmute = Semaphore(value=1)
fleftmute = Semaphore(value=1)
def _atomic_write_member(member, text):
    """member.txt 原子写：先写同目录临时文件，再用 os.replace 原子替换。

    直接 open('w') 会先截断原文件，截断到写完之间存在窗口期，
    全站不加锁的读者（getusername/check_logined/userlist 等）会读到半截文件，
    导致并发下认证随机失败甚至 500（压测实测复现）。
    os.replace 在同一文件系统上是原子操作，读者要么看到旧完整内容，要么看到新完整内容。
    """
    tmp = member + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fp:
        fp.write(text)
        fp.flush()
        os.fsync(fp.fileno())
    os.replace(tmp, member)

def _atomic_write_json(path, data):
    """json 配置文件原子写（setting/f.json、set_left/fleft.json、imgbook/fbook.json）。

    直接 open('w') 会先截断原文件，无锁读者（GetSetting/mainpagedataget）在截断到
    写完之间会读到半截 json 抛 500；os.replace 保证读者要么看到旧完整内容，要么新完整内容。
    """
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fp:
        json.dump(data, fp, indent=2, ensure_ascii=False)
        fp.flush()
        os.fsync(fp.fileno())
    os.replace(tmp, path)

def _clean_field(val, maxlen):
    """表单字段统一转 str 并截断到上限，防超大 payload 滥用磁盘；None 按空串处理"""
    return str(val if val is not None else '')[:maxlen]

def writeYonghu(password, member, email, nickname):
    global Setting_Formel, LeftSetting_Formel, memmute, ffmute, fleftmute, fbookmute
    # 新用户密码直接存加盐格式；登录输入仍是前端 sha256 值，见 salted_from_value
    ret = salted_from_value(genpassword(password))

    memmute.acquire()
    # 昵称/邮箱消毒：剔除 member.txt 分隔符与换行，防止注册内容破坏行结构
    nickname = str(nickname).replace(MEMBER_SEP, "").replace("\n", " ").replace("\r", " ")
    email = str(email).replace(MEMBER_SEP, "").replace("\n", " ").replace("\r", " ")
    with open(member, 'a+', encoding='utf-8') as fp:
        # 上一账号行若无尾换行，直接 append 会粘行：新账号不可登录，
        # 且上一行的密码列/qx 被拼接破坏。append 前先补齐换行。
        fp.seek(0, os.SEEK_END)
        size = fp.tell()
        if size > 0:
            fp.seek(size - 1)
            if fp.read(1) != "\n":
                fp.write("\n")
        fp.write(f"{ret}<》!=$)(=$@{email}<》!=$)(=$@{nickname}<》!=$)(=$@1\n")
    memmute.release()

    prepa = os.path.abspath(__file__ + "/../../../")
    # 全邮箱直接作为 people/ 目录名与身份标识（register 入口已做邮箱格式校验防穿越）
    ml = email
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
    for i in range(1, SETTING_SLOTS_MAX + 1):
        nth = os.path.join(setting, str(i))
        os.makedirs(nth, exist_ok=True)
    for i in range(1, SETTING_SLOTS_MAX + 1):
        nth1 = os.path.join(set_left, str(i), '1')
        nth2 = os.path.join(set_left, str(i), '2')
        nth3 = os.path.join(set_left, str(i), '3')
        os.makedirs(nth1, exist_ok=True)
        os.makedirs(nth2, exist_ok=True)
        os.makedirs(nth3, exist_ok=True)

    file = os.path.join(setting, 'f.json')

    if not os.path.exists(file):
        # 统一原子写（tmp+os.replace），避免注册瞬间被并发读接口读到半截 JSON
        ffmute.acquire()
        try:
            _atomic_write_json(file, Setting_Formel)
        finally:
            ffmute.release()

    file = os.path.join(set_left, 'fleft.json')
    if not os.path.exists(file):
        fleftmute.acquire()
        try:
            _atomic_write_json(file, LeftSetting_Formel)
        finally:
            fleftmute.release()

    # 书架空文件"出生即完整"：读书架/加书接口不再依赖懒初始化兜底
    fbook = os.path.join(imgbook, 'fbook.json')
    if not os.path.exists(fbook):
        fbookmute.acquire()
        try:
            _atomic_write_json(fbook, [])
        finally:
            fbookmute.release()

    # 访客统计文件预建（文件名/初值取 siteconfig，改配置即时生效）；
    # 缺失时读接口虽有兜底，注册时建好可避免首次计数从兜底路径走
    travelfile = os.path.join(prepa, 'people', ml, str(siteconfig.get('traveler_filename')))
    if not os.path.exists(travelfile):
        try:
            with open(travelfile, 'w', encoding='utf-8') as obj:
                obj.write(str(int(siteconfig.get('traveler_default_init'))))
        except Exception:
            pass

    try:
        shutil.copyfile(os.path.join(prepa, 'article', "2寸.jpg"), os.path.join(touxiang, '2寸.jpg'))
    except Exception:
        # 默认头像缺失/不可读时不能让整个注册失败——读接口有二次兜底恢复
        pass

regmute = Semaphore(value=1)
memmute = regmute  # 三锁合一：member.txt 全站唯一写锁，writeYonghu/register/admin_*/NicknameSetting 共用，防止跨函数并发读改写竞态
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
                if len(i) < 2:
                    # 空行/脏行原样保留，不参与改写
                    allkl.append(ll)
                    continue
                if i[1]==email:
                    # 忘记密码重置必须存加盐格式（与注册/登录一致）。
                    # 旧代码存裸 sha256（已弃用格式），verify_member_password 一律
                    # 返回 False，导致重置后的账号永远无法登录
                    i[0] = salted_from_value(genpassword(password))
                    ll = '<》!=$)(=$@'.join(i) + '\n'
                allkl.append(ll)
        regmute.acquire()
        _atomic_write_member(member, "".join(allkl))
        regmute.release()
        return JsonResponse({"ret":100}, safe = False)

    # 用户名（邮箱 @ 前缀）至少 7 个字符：getusername 会把短名按匿名访客处理，
    # 短用户名注册后将永远无法登录，这里在注册入口直接拒绝（阈值统一配置在 site_config.json）
    _min_prefix = int(siteconfig.get('min_username_prefix_length'))
    if len(email.split("@")[0]) < _min_prefix:
        return JsonResponse({"ret":-6, "msg":f"用户名（@前的部分）至少需要{_min_prefix}个字符"}, safe = False)

    # 全邮箱将直接作为身份标识与 people/ 目录名，注册入口必须校验格式，
    # 拒绝 ../、member.txt 分隔符等危险字符（目录穿越/行结构破坏）
    if not regular.fullmatch(r'[A-Za-z0-9._+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z0-9\-]+', email):
        return JsonResponse({"ret":-6, "msg": "邮箱格式不合法"}, safe = False)

    with open(yonghu, 'r', encoding='utf-8') as obj:
        for i in obj.readlines():
            i = i.strip()
            i = i.split("<》!=$)(=$@")
            if len(i) < 2:
                # 空行/脏行跳过
                continue
            if email==i[1]:
                dif = time.time() + timezone - float(i[0])
                if dif >= int(siteconfig.get('verify_code_ttl_seconds')):
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

import hmac

# 密码只存加盐格式：sha256s$<salt>$<digest>，digest = sha256(salt + 前端 sha256 值)。
# 登录输入恒为前端算好的 sha256 值。旧格式（裸 sha256）已彻底弃用：
# member.txt 中非 sha256s$ 开头的行一律校验失败（旧用户需重新注册）。
SALT_PREFIX = "sha256s$"

def salted_from_value(value):
    """把旧式密码值（前端传来的 sha256 十六进制）转为加盐存储格式。"""
    salt = hashlib.sha256(os.urandom(32)).hexdigest()[:32]
    digest = hashlib.sha256((salt + value).encode('utf-8')).hexdigest()
    return SALT_PREFIX + salt + "$" + digest

def verify_member_password(stored, value):
    """校验 member.txt 第一字段 stored（必须为加盐格式）与前端传来的 sha256 值 value 是否匹配。
    旧格式（裸 sha256）已弃用，一律校验失败。"""
    if not stored.startswith(SALT_PREFIX):
        return False
    try:
        _, salt, digest = stored.split("$", 2)
    except ValueError:
        return False
    calc = hashlib.sha256((salt + value).encode('utf-8')).hexdigest()
    return hmac.compare_digest(calc, digest)

def checklogin(password, username, member):
    # 前端登录传输 sha256 密文，这里不做二次哈希，直接按加盐格式校验
    # key = bytes(password, encoding='utf-8')
    # sha = hashlib.sha256()
    # sha.update(key)
    # ret = sha.hexdigest()
    ret = password
    with open(member, 'r', encoding='utf-8') as fp:
        for i in fp.readlines():
            i = i.strip().split("<》!=$)(=$@")
            if len(i) < 2:
                # 空行/脏行跳过，防登录全挂
                continue
            # 支持三种登录名：完整邮箱 / 昵称 / 邮箱前缀（@ 前的用户名）。
            # 输入带 @ 时按完整邮箱精确匹配，避免前缀歧义误登
            prefix = i[1].split("@")[0] if "@" in i[1] else i[1]
            if ("@" not in username and prefix == username
                    or i[1] == username or i[2] == username) and verify_member_password(i[0], ret):
                # 登录成功统一返回完整邮箱；全站身份/存储/路径均以完整邮箱为准
                return True, ret, i[1], i[2], int(i[-1])
    return False, 0, 0, 0, -1

def login(request):
    req = json.loads(request.body)
    infor = req["LoginForm"]
    password = infor['password']
    username = infor['username']
    addpa = os.path.abspath(__file__ + "/../../")
    member = os.path.join(addpa, "..", "article", 'member.txt')
    ret, passw, ml, usern, quanxian = checklogin(password, username, member)
    if ret:
        return JsonResponse({"ret":ret,'password':passw, 'mail':ml, 'username':usern, 'quanxian':quanxian}, safe = False)
    else:
        return JsonResponse({"ret":ret}, safe=False)

MEMBER_SEP = "<》!=$)(=$@"

# 三级权限（权限值共 3 个）：
#   超级管理员：可管理所有用户，包含普通管理员
#   普通管理员：可管理所有普通用户，但看不到/动不了超级管理员
#   普通用户  ：只能管理自己的内容
# 站长权限：999999999，不参与三级权限体系；
#   仅按权限值识别站长（member.txt 权限列=999999999），与邮箱/昵称无关；
#   任何管理员（含超级管理员）都不能删除/降权/重置站长账号，
#   且该值不在 VALID_QUANXIAN 内，无法通过接口授予，只能手工维护。
SUPER_ADMIN_QUANXIAN = 1000000
ADMIN_QUANXIAN = 100
NORMAL_QUANXIAN = 1
OWNER_QUANXIAN = 999999999
VALID_QUANXIAN = (NORMAL_QUANXIAN, ADMIN_QUANXIAN, SUPER_ADMIN_QUANXIAN)

def is_admin(quanxian):
    """是否为管理员（站长、超级管理员或普通管理员）。
    站长（999999999）视为最高管理员：_member_level 鉴权、管理接口均依赖此判断。"""
    try:
        return int(quanxian) in (OWNER_QUANXIAN, ADMIN_QUANXIAN, SUPER_ADMIN_QUANXIAN)
    except (ValueError, TypeError):
        return False

def is_super_admin(quanxian):
    """是否为超级管理员。"""
    try:
        return int(quanxian) == SUPER_ADMIN_QUANXIAN
    except (ValueError, TypeError):
        return False

def is_owner(quanxian):
    """是否为站长（仅按权限值 999999999 识别）。"""
    try:
        return int(quanxian) == OWNER_QUANXIAN
    except (ValueError, TypeError):
        return False

def _member_level(req):
    """返回请求方账号的权限值；不是管理员返回 0。"""
    mail = req.get('mail', '')
    password = req.get('password', '')
    if not mail or not password:
        return 0
    _, parsed = _read_members(_member_file())
    for parts in parsed:
        ml = parts[1]
        if ml == mail and verify_member_password(parts[0], password):
            try:
                qx = int(parts[-1])
            except (ValueError, TypeError):
                return 0
            return qx if is_admin(qx) else 0
    return 0

def _target_level(target):
    """查询目标账号的权限值；不存在返回 None。"""
    if not target:
        return None
    _, parsed = _read_members(_member_file())
    for parts in parsed:
        ml = parts[1]
        if ml == target or parts[1] == target:
            try:
                return int(parts[-1])
            except (ValueError, TypeError):
                return NORMAL_QUANXIAN
    return None

def _member_file():
    addpa = os.path.abspath(__file__ + "/../../")
    return os.path.join(addpa, "..", "article", 'member.txt')

def _read_members(member):
    """读取 member.txt，返回 (原始行列表, 解析后的字段列表)。"""
    lines, parsed = [], []
    if not os.path.exists(member):
        return lines, parsed
    with open(member, 'r', encoding='utf-8') as fp:
        for i in fp.readlines():
            i = i.strip()
            if not i:
                continue
            parts = i.split(MEMBER_SEP)
            if len(parts) < 4:
                continue
            lines.append(i)
            parsed.append(parts)
    return lines, parsed

def _require_admin(req):
    """校验请求方是否为管理员（超级管理员或普通管理员）。cookie 中的 password 为 sha256 后的值。"""
    return _member_level(req) > 0

@csrf_exempt
def userlist(request):
    """公开接口：列出所有用户的用户名与昵称，供"其他用户"之间互相跳转。

    不返回邮箱、密码、权限等敏感信息。
    """
    _, parsed = _read_members(_member_file())
    prepa = os.path.abspath(__file__ + "/../../../")
    users = []
    for parts in parsed:
        ml = parts[1]
        users.append({
            "mail": ml,
            "nickname": parts[2] or ml,
            "hasdata": os.path.isdir(os.path.join(prepa, 'people', ml)),
        })
    users.sort(key=lambda x: x["mail"])
    return JsonResponse({"ret": 1, "users": users}, safe=False)

@csrf_exempt
def admin_userlist(request):
    """管理员获取注册用户列表（不含密码散列）。

    超级管理员能看到全部用户；普通管理员看不到超级管理员。
    """
    try:
        req = json.loads(request.body)
    except Exception:
        req = request.GET.dict()
    my_level = _member_level(req)
    if my_level == 0:
        return JsonResponse({"ret": -100, "users": []}, safe=False)
    member = _member_file()
    _, parsed = _read_members(member)
    users = []
    prepa = os.path.abspath(__file__ + "/../../../")
    for parts in parsed:
        ml = parts[1]
        try:
            qx = int(parts[-1])
        except (ValueError, TypeError):
            qx = NORMAL_QUANXIAN
        # 普通管理员看不到超级管理员
        if is_super_admin(qx) and not is_super_admin(my_level):
            continue
        userdir = os.path.join(prepa, 'people', ml)
        users.append({
            "mail": ml,
            "truemail": parts[1],
            "nickname": parts[2],
            "quanxian": qx,
            "is_admin": is_admin(qx),
            "is_super": is_super_admin(qx),
            "is_owner": is_owner(qx),
            "hasdata": os.path.isdir(userdir),
        })
    return JsonResponse({"ret": 1, "users": users, "my_level": my_level}, safe=False)

@csrf_exempt
def admin_createuser(request):
    """管理员新建用户（仅站长/超级管理员）：直接写入 member.txt 并初始化用户目录。

    必须给出邮箱（登录账号）、用户名（昵称）、密码；邮箱格式与用户名最小长度
    复用注册入口同规则校验；密码落库为加盐格式（与注册/重置一致）。
    普通管理员无权新建。
    """
    try:
        req = json.loads(request.body)
    except Exception:
        return JsonResponse({"ret": -100}, safe=False)
    my_level = _member_level(req)
    if not (is_owner(my_level) or is_super_admin(my_level)):
        return JsonResponse({"ret": -100}, safe=False)
    email = str(req.get('email', '') or '').strip()
    nickname = str(req.get('nickname', '') or '').strip()
    # 新用户密码用独立键 newpass：req['password'] 是请求方管理员的登录凭据（_member_level 用），
    # 两者不能共用一个键，否则前端 authData 的凭据被新用户密码覆盖、管理员鉴权永远失败
    password = str(req.get('newpass', '') or '')
    if not email or not nickname or not password:
        return JsonResponse({"ret": -1, "msg": "邮箱、用户名、密码都必须填写"}, safe=False)
    # 与注册入口同规则：邮箱格式（防目录穿越/member.txt 行结构破坏）
    if not regular.fullmatch(r'[A-Za-z0-9._+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z0-9\-]+', email):
        return JsonResponse({"ret": -2, "msg": "邮箱格式不合法"}, safe=False)
    # 用户名（@ 前缀）最小长度：短名会被短名守卫按匿名处理，永远无法登录
    _min_prefix = int(siteconfig.get('min_username_prefix_length'))
    if len(email.split("@")[0]) < _min_prefix:
        return JsonResponse({"ret": -3, "msg": f"用户名（@前的部分）至少需要{_min_prefix}个字符"}, safe=False)
    member = _member_file()
    # 查重与注册同模式（锁外读）；writeYonghu 内部自持 memmute 写入，
    # 这里不可再持同一把非重入锁调用它，否则死锁
    if not checkYonghu(email, member):
        return JsonResponse({"ret": -4, "msg": "该邮箱已被注册"}, safe=False)
    writeYonghu(password, member, email, nickname)
    return JsonResponse({"ret": 1}, safe=False)

@csrf_exempt
def admin_resetpass(request):
    """管理员重置指定用户密码。普通管理员不能重置超级管理员。"""
    try:
        req = json.loads(request.body)
    except Exception:
        # 空 body / 非法 JSON：按未授权处理，而不是 500
        return JsonResponse({"ret": -100}, safe=False)
    my_level = _member_level(req)
    if my_level == 0:
        return JsonResponse({"ret": -100}, safe=False)
    target = req.get('target', '')
    newpass = str(req.get('newpass', '') or '')
    # 与前端提示一致：至少 6 位且必须同时包含数字和字母
    if not target or len(newpass) < 6 or \
            not (regular.search(r'[A-Za-z]', newpass) and regular.search(r'\d', newpass)):
        return JsonResponse({"ret": -1}, safe=False)
    tlevel = _target_level(target)
    if tlevel is None:
        return JsonResponse({"ret": -2}, safe=False)
    # 站长账号（权限 999999999）受保护：任何管理员都不能重置其密码（防止接管）
    if is_owner(tlevel):
        return JsonResponse({"ret": -6}, safe=False)
    if is_super_admin(tlevel) and not is_super_admin(my_level):
        return JsonResponse({"ret": -3}, safe=False)  # 普通管理员不能重置超级管理员
    member = _member_file()
    found = False
    # 读-改-写全程持锁，防止读到 open('w') 截断瞬间产生空快照后被写回
    regmute.acquire()
    try:
        lines, parsed = _read_members(member)
        out = []
        for line, parts in zip(lines, parsed):
            ml = parts[1]
            if ml == target or parts[1] == target:
                parts[0] = salted_from_value(genpassword(newpass))
                line = MEMBER_SEP.join(parts)
                found = True
            out.append(line + '\n')
        _atomic_write_member(member, "".join(out))
    finally:
        regmute.release()
    return JsonResponse({"ret": 1 if found else -2}, safe=False)

@csrf_exempt
def admin_setquanxian(request):
    """管理员修改指定用户权限（仅三个合法权限值）。

    规则：
      - 不能修改自己的权限（避免自己把自己锁死）
      - 普通管理员不能修改超级管理员的权限
      - 只有超级管理员能把他人设为超级管理员
    """
    try:
        req = json.loads(request.body)
    except Exception:
        # 空 body / 非法 JSON：按未授权处理，而不是 500
        return JsonResponse({"ret": -100}, safe=False)
    my_level = _member_level(req)
    if my_level == 0:
        return JsonResponse({"ret": -100}, safe=False)
    target = req.get('target', '')
    try:
        quanxian = int(req.get('quanxian', NORMAL_QUANXIAN))
    except (ValueError, TypeError):
        return JsonResponse({"ret": -1}, safe=False)
    if quanxian not in VALID_QUANXIAN:
        return JsonResponse({"ret": -1}, safe=False)
    # 不允许管理员修改自己的权限，避免误操作导致自己失去管理员身份
    selfmail = req.get('mail', '')
    if target and (target == selfmail or target == req.get('truemail', '')):
        return JsonResponse({"ret": -4}, safe=False)
    tlevel = _target_level(target)
    if tlevel is None:
        return JsonResponse({"ret": -2}, safe=False)
    # 站长账号（权限 999999999）受保护：任何管理员都不能修改其权限
    # （防止先把站长降权成普通用户、再删除的绕过路径）
    if is_owner(tlevel):
        return JsonResponse({"ret": -6}, safe=False)
    if is_super_admin(tlevel) and not is_super_admin(my_level):
        return JsonResponse({"ret": -3}, safe=False)  # 普通管理员动不了超级管理员
    if is_super_admin(quanxian) and not is_super_admin(my_level):
        return JsonResponse({"ret": -3}, safe=False)  # 只有超级管理员能授予超级管理员
    member = _member_file()
    found = False
    # 读-改-写全程持锁，防止读到 open('w') 截断瞬间产生空快照后被写回
    regmute.acquire()
    try:
        lines, parsed = _read_members(member)
        out = []
        for line, parts in zip(lines, parsed):
            ml = parts[1]
            if ml == target or parts[1] == target:
                parts[-1] = str(quanxian)
                line = MEMBER_SEP.join(parts)
                found = True
            out.append(line + '\n')
        _atomic_write_member(member, "".join(out))
    finally:
        regmute.release()
    return JsonResponse({"ret": 1 if found else -2}, safe=False)

@csrf_exempt
def admin_deleteuser(request):
    """管理员删除用户：member.txt 移除记录，people/<mail> 目录移动到 article/deleted_users 备份。

    超级管理员可删除任意用户（含普通管理员）；普通管理员只能删除普通用户。
    """
    try:
        req = json.loads(request.body)
    except Exception:
        # 空 body / 非法 JSON：按未授权处理，而不是 500
        return JsonResponse({"ret": -100}, safe=False)
    my_level = _member_level(req)
    if my_level == 0:
        return JsonResponse({"ret": -100}, safe=False)
    target = str(req.get('target', '') or '')
    if not target:
        return JsonResponse({"ret": -1}, safe=False)
    # 纵深防御：target 将参与 people/<target> 目录拼接与 shutil.move，
    # 禁止路径分隔符/上级引用（正常应被 _target_level 的精确匹配挡住，这里双保险）
    if '/' in target or '\\' in target or '..' in target:
        return JsonResponse({"ret": -1}, safe=False)
    # 与前端 canManage 一致：不允许删除自己（避免误操作把自己从系统中删掉）
    if target == req.get('mail', ''):
        return JsonResponse({"ret": -5}, safe=False)
    tlevel = _target_level(target)
    if tlevel is None:
        return JsonResponse({"ret": -2}, safe=False)
    # 站长账号（权限 999999999）受保护：超级管理员和普通管理员都不能删除
    if is_owner(tlevel):
        return JsonResponse({"ret": -6}, safe=False)
    if is_admin(tlevel) and not is_super_admin(my_level):
        return JsonResponse({"ret": -3}, safe=False)  # 普通管理员不能删除管理员
    member = _member_file()
    found = False
    # 读-改-写全程持锁，防止读到 open('w') 截断瞬间产生空快照后被写回
    regmute.acquire()
    try:
        lines, parsed = _read_members(member)
        keep_lines = []
        for line, parts in zip(lines, parsed):
            ml = parts[1]
            if ml == target or parts[1] == target:
                found = True
                continue
            keep_lines.append(line)
        if not found:
            return JsonResponse({"ret": -2}, safe=False)  # finally 统一释放锁
        _atomic_write_member(member, "".join(l + '\n' for l in keep_lines))
    finally:
        regmute.release()
    prepa = os.path.abspath(__file__ + "/../../../")
    userdir = os.path.join(prepa, 'people', target)
    if os.path.isdir(userdir):
        backup = os.path.join(prepa, 'article', 'deleted_users')
        os.makedirs(backup, exist_ok=True)
        postDate = datetime.fromtimestamp(time.time() + timezone).isoformat()[:19].replace(":", "_")
        shutil.move(userdir, os.path.join(backup, f"{postDate}_{target}"))
    return JsonResponse({"ret": 1}, safe=False)

NOTICE_FILE = 'notices.json'
_notice_mutex = Semaphore(value=1)

def _notice_display_max():
    """通知显示/存储上限（配置项 notice_display_max，缺省回退 200）。"""
    try:
        return max(1, int(siteconfig.get('notice_display_max')))
    except (TypeError, ValueError):
        return 200

def _notice_path(mail):
    prepa = os.path.abspath(__file__ + "/../../../")
    return os.path.join(prepa, 'people', mail, NOTICE_FILE)

def _read_notices(mail):
    """读取某用户的通知列表（按时间倒序）。"""
    p = _notice_path(mail)
    if not os.path.exists(p):
        return []
    try:
        with open(p, 'r', encoding='utf-8') as obj:
            data = json.load(obj)
        if not isinstance(data, list):
            return []
    except Exception:
        return []
    data.sort(key=lambda x: str(x.get('time', '')), reverse=True)
    return data

@csrf_exempt
def send_notice(request):
    """管理员发送通知。

    targets 为空表示通知全部用户；也可以指定一个或多个用户名。
    普通管理员不能通知超级管理员。
    """
    try:
        req = json.loads(request.body)
    except Exception:
        req = request.POST.dict()
    my_level = _member_level(req)
    if my_level == 0:
        return JsonResponse({"ret": -100}, safe=False)
    content = str(req.get('content', '') or '').strip()
    if not content:
        return JsonResponse({"ret": -1}, safe=False)
    if len(content) > 2000:
        content = content[:2000]
    targets = req.get('targets') or []
    if isinstance(targets, str):
        targets = [targets]
    if not isinstance(targets, list):
        targets = []

    _, parsed = _read_members(_member_file())
    all_mails, allowed = [], []
    for parts in parsed:
        ml = parts[1]
        all_mails.append(ml)
        try:
            qx = int(parts[-1])
        except (ValueError, TypeError):
            qx = NORMAL_QUANXIAN
        # 普通管理员不能给超级管理员发通知
        if is_super_admin(qx) and not is_super_admin(my_level):
            continue
        allowed.append(ml)

    if targets:
        sendto = [t for t in targets if t in allowed]
    else:
        sendto = allowed
    if not sendto:
        return JsonResponse({"ret": -2}, safe=False)

    sender = str(req.get('mail', ''))
    # 带毫秒，保证同一秒内多条通知也能正确倒序
    now = datetime.fromtimestamp(time.time() + timezone).isoformat()[:23].replace("T", " ")
    sent = 0
    _notice_mutex.acquire()
    try:
        for ml in sendto:
            p = _notice_path(ml)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            data = []
            if os.path.exists(p):
                try:
                    with open(p, 'r', encoding='utf-8') as obj:
                        data = json.load(obj)
                    if not isinstance(data, list):
                        data = []
                except Exception:
                    data = []
            data.append({"time": now, "from": sender, "content": content})
            data = data[-_notice_display_max():]
            # tmp + os.replace 原子写：读取方（前端拉通知）无锁，
            # 直接 open('w') 的截断窗口会让并发读取拿到半截 JSON
            tmp = p + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as obj:
                json.dump(data, obj, indent=2, ensure_ascii=False)
            os.replace(tmp, p)
            sent += 1
    finally:
        _notice_mutex.release()
    return JsonResponse({"ret": 1, "sent": sent, "targets": sendto}, safe=False)

@csrf_exempt
def get_notice(request):
    """当前登录用户获取自己的通知（时间倒序）。"""
    try:
        req = json.loads(request.body)
    except Exception:
        req = request.POST.dict()
    mail = str(req.get('mail', '') or '')
    password = str(req.get('password', '') or '')
    if not mail or not check_logined(mail, password):
        return JsonResponse({"ret": -100, "notices": []}, safe=False)
    # 按配置项 notice_display_max 只返回最近 N 条（时间倒序），max 供前端提示文案使用
    notices = _read_notices(mail)[:_notice_display_max()]
    return JsonResponse({"ret": 1, "notices": notices, "max": _notice_display_max()}, safe=False)

@csrf_exempt
def clear_notice(request):
    """当前登录用户清空自己的通知。"""
    try:
        req = json.loads(request.body)
    except Exception:
        req = request.POST.dict()
    mail = str(req.get('mail', '') or '')
    password = str(req.get('password', '') or '')
    if not mail or not check_logined(mail, password):
        return JsonResponse({"ret": -100}, safe=False)
    # notice_clear_temporary=true 时清空是临时的：只影响当前页面显示，不删磁盘数据，
    # 刷新页面/新开标签后通知继续展示；false 时保持原持久清空行为
    temporary = str(siteconfig.get('notice_clear_temporary')).strip().lower() in ('1', 'true', 'yes', 'on')
    if temporary:
        return JsonResponse({"ret": 1, "temporary": True}, safe=False)
    p = _notice_path(mail)
    _notice_mutex.acquire()
    try:
        if os.path.exists(p):
            with open(p, 'w', encoding='utf-8') as obj:
                json.dump([], obj)
    finally:
        _notice_mutex.release()
    return JsonResponse({"ret": 1}, safe=False)

def check_logined(mailaddr, password):
    addpa = os.path.abspath(__file__ + "/../../")
    member = os.path.join(addpa, "..", "article", 'member.txt')
    usern = ""
    with open(member, 'r', encoding='utf-8') as fp:
        for i in fp.readlines():
            i = i.strip().split("<》!=$)(=$@")
            if len(i) < 2:
                # 空行/脏行跳过，防登录校验 500
                continue
            mail = i[1]
            # 全邮箱精确匹配；历史脏行（无 @）密码列也不会匹配，直接按原样比较即可
            if mail==mailaddr and verify_member_password(i[0], password):
                return True
    return False

def check_identity(request, req, admin_bypass=False):
    """
    统一身份认证封装（供发布/修改/删除等写接口复用，替代各接口重复的三段式认证代码）：
      1) renzheng      —— 发布密钥校验
      2) getusername   —— 登录态与页面归属（ret: 0 匿名 / 1 本人页面 / 2 他人页面）
      3) check_logined —— member.txt 账号密码校验

    参数:
      request      : Django HttpRequest
      req          : 请求参数 dict（request.POST.dict() 或 json.loads(request.body)）
      admin_bypass : True 时管理员（quanxian==ADMIN_QUANXIAN）免密通过，
                     用于管理员修改/删除他人内容的接口

    返回 dict:
      passed  : bool  综合认证是否通过；False 时调用方应直接返回 ret:-100
      logined : bool  账号密码是否校验通过（可用于定位保存目录等后续逻辑）
      keyok   : bool  发布密钥是否有效
      get     : dict  getusername 的完整返回（mail/urlmail/quanxian/ret），
                       供调用方继续做"普通用户只能操作自己内容"的归属校验
    """
    try:
        rzret = json.loads(renzheng(request).content)
        keyok = not rzret.get('ret', True)
        get = json.loads(getusername(request).content)
        quanxian = get.get('quanxian', -1)
        logined = ('mail' in req.keys() and 'password' in req.keys()
                   and check_logined(req['mail'], req['password']))
    except Exception:
        return {"passed": False, "logined": False, "keyok": False,
                "get": {"ret": 0, "quanxian": -1, "mail": "", "urlmail": ""}}
    passed = (admin_bypass and quanxian == ADMIN_QUANXIAN) or (logined and keyok)
    return {"passed": passed, "logined": logined, "keyok": keyok, "get": get}

# 路由中不代表用户名的模块前缀，解析 urlmail 时需要跳过
_URL_MODULE_PREFIX = {
    "think", "csdn", "book", "zhihu", "video", "travel",
    "commonuse", "everydayimg", "admin", "people", "article",
    "markdown_detail", "post_article", "detail",
}

def findurlmail(urlrul:str):
    """从页面 URL 中解析出 urlmail（路由里代表用户的那一段）。

    前端各页面都直接上报 document.URL，因此需要同时兼容两种路由形态：
      1) history 模式：https://host/think/homepage
      2) hash 模式   ：https://host/#/think/homepage
    并跳过模块前缀（think/csdn/admin/markdown_detail...），返回用户段。
    解析失败一律返回空串，由调用方按匿名处理，避免异常导致 500。
    """
    if not urlrul:
        return ""
    # 去掉 scheme://
    idx = urlrul.find("://")
    rest = urlrul[idx + 3:] if idx >= 0 else urlrul
    # 去掉 host（可能带端口）
    slash = rest.find("/")
    path = rest[slash:] if slash >= 0 else ""
    # 去掉 query，hash 之后的内容才是 hash 路由的真实路径
    path = path.split("?")[0]
    if "#" in path:
        path = path.split("#", 1)[1]
    segs = [s for s in path.split("/") if s]
    while segs and segs[0].lower() in _URL_MODULE_PREFIX:
        segs.pop(0)
    return segs[0] if segs else ""

# @csrf_exempt
# 跨用户共享的全局变量 —— 已全部移除，改为 per-urlmail 独立存储
# StatisticTravelerCount 每个用户从磁盘 TravelerStatistics.txt 独立读取
# allTraveler 下面模块级 dict 已改为嵌套 {urlmail: {ip: timestamp}} 隔离

def getusername(request):
    if isinstance(request.POST.dict(), dict) and len(request.POST.dict())!=0:
        req = request.POST.dict()
    else:
        try:
            req = json.loads(request.body)
        except Exception:
            # 空 body / 非法 JSON 按匿名兜底：全站大量接口依赖本函数，异常会连带 500
            req = {}
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
    if urlmail=='zj' or len(urlmail)<=int(siteconfig.get('short_name_guard_max_length')):
        getStatisticTravelerCount(request, urlmail)
        return JsonResponse({"ret":0, 'mail':None, 'username':None, 'urlmail':urlmail, 'quanxian':-1, 'truemail':-1}, safe = False)
    quanxian = -1
    nickname = ""
    with open(member, 'r', encoding='utf-8') as fp:
        fpline = [i.strip() for i in fp.readlines()]
        findmember = False
        for i in fpline:
            i = i.split("<》!=$)(=$@")
            if len(i) < 2:
                # 空行/脏行跳过，防 member.txt 尾部空行导致全站登录态判断 500
                continue
            mail = i[1]
            if "@" not in mail:
                # 全邮箱匹配：脏行（无 @）跳过，防后续逻辑异常
                continue
            if mail==mailaddr:
                quanxian = int(i[-1])
                nickname = i[2]
            if mail==mailaddr and verify_member_password(i[0], password):
                usern = i[2]
                findmember = True
                # 自己页面判定：优先用解析出的 urlmail（兼容 hash 路由），
                # 再兜底原来的子串判断
                if urlmail == mail or mail in req['url']:
                    getStatisticTravelerCount(request, urlmail)
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
                        if len(ij) < 2:
                            # 空行/脏行跳过
                            continue
                        mll = ij[1]
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
                        getStatisticTravelerCount(request, urlmail)
                        return JsonResponse({"ret":2, 'mail':mailaddr, 'username':usern, \
                                             'urlmail':urlmail, 'quanxian':quanxian, 'truemail':mail, 'nickname':nickname},\
                                            safe = False)
        if not findmember:
            for i in fpline:
                i = i.split("<》!=$)(=$@")
                if len(i) < 2:
                    # 空行/脏行跳过
                    continue
                ml = i[1]
                if urlmail==ml:
                    quanxian = int(i[-1])
                    nickname = i[2]
                    getStatisticTravelerCount(request, urlmail)
                    return JsonResponse({"ret":3, 'mail':mailaddr, 'username':nickname, \
                                             'urlmail':urlmail, 'quanxian':-1, 'truemail':None, 'nickname':nickname},\
                                            safe = False)
    getStatisticTravelerCount(request, urlmail)
    return JsonResponse({"ret":0, 'mail':None, 'username':None, \
                         'urlmail':urlmail, 'quanxian':-1, 'truemail':-1, 'nickname':nickname}, safe = False)

# https://docs.djangoproject.com/zh-hans/5.1/ref/csrf/
@csrf_exempt
def postArticle(request):
    global allfile, path
    basepath = deepcopy(path)
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    req = json.loads(request.body)
    markdown = req["textarea"]
    # 容量限制：超长内容直接拒绝，防止一条请求经多层正则渲染拖死 worker 或撑爆磁盘
    if len(markdown) > 5 * 1024 * 1024:
        return JsonResponse({"ret": -2, "msg": "文章内容过大（超过5MB）"}, safe=False)
    # original = deepcopy(markdown)

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
        if "%" in savename:
            savename = savename.replace("%", "")

        # if "mail" in req.keys():
        #     if check_logined(req['mail'], req['password']):
        #         basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
        auth = check_identity(request, req)
        get = auth['get']
        if not auth['passed']:
            return JsonResponse( { "ret" : -100} , safe = False)
        basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
        if f"{get['mail']}" not in req['url']:
            return JsonResponse( { "ret" : -100} , safe = False)

        dirp = basepath
        # 管理员编辑他人/公共文章时，保存到原文章所在目录，而不是管理员自己的目录
        try:
            if is_admin(get.get('quanxian')) and len(filepath) > 0 and os.path.exists(filepath):
                origindir = os.path.dirname(filepath)
                # 安全：管理员代写也只允许落在 people/ 或 article/ 内，防路径穿越写任意位置
                realdir = os.path.realpath(origindir)
                root = os.path.realpath(os.path.abspath(__file__ + "/../../../"))
                allowed_roots = [os.path.join(root, 'people') + os.sep, os.path.join(root, 'article') + os.sep]
                if os.path.isdir(origindir) and any(realdir.startswith(a) for a in allowed_roots):
                    dirp = origindir
        except Exception:
            pass
        if 'zhihu' in filepath:
            dirp = dirp.replace("csdn_spider", "zhihu_spider")
        # 只失效受影响目录的文章列表缓存（index() 以文章根目录为键），不再清空全用户缓存
        allfile.pop(dirp, None)
        savepath = os.path.join(dirp, postDate + "_" + title)
        if len(dirname) > 0:
            for i in os.listdir(dirp):
                if dirname == i: # or (len(title) > 0 and title in i):
                    savepath = os.path.join(dirp, i)
                    break
        if not os.path.exists(savepath):
            # 递归创建，兼容新用户首次发布（上层目录可能还不存在）
            os.makedirs(savepath, exist_ok=True)
        savefile = os.path.join(savepath, savename)
        # if title not in markdown[:100]:
        #     markdown = f"# {title}\n\n" + markdown 
        if len(markdown)==0:
            markdown = "# no content\n\n# no content\n\n# no content\n\n"
        try:
            nextline_index = markdown.index("\n")
        except:
            markdown = "-----------------------------\n\n" + markdown
            
        imglink = regular.findall(r'\!\[image.png\]\((.*)\)', markdown)
        if len(imglink) > 0:
            img = imglink[0]
            imglink = imglink[0].split('\"')
            if len(imglink) > 0:
                imglink = imglink[0]
        
                imgname = imglink.split("/")[-1]
                if 'https' in imglink:
                    response = requests.get(imglink, timeout=30)
                    if response.status_code==200 and "leetcode" in imglink:
                        markdown = markdown.replace(img, imgname);
                        with open(os.path.join(savepath, imgname), 'wb') as obj:
                            obj.write(response.content)

        with open(savefile, 'w') as obj:
            obj.write(markdown)
        create = os.path.join(savepath, 'create.txt')
        if not os.path.exists(create):
            with open(create, 'w') as obj:
                obj.write(postDate + "\n")
        with open(create, 'a+') as obj:
            obj.write(postDate + "\n")
        if new_Title:
            # 安全：dirname 来自客户端，改名目标必须由「dirp 下真实存在的目录项 + 新标题」
            # 推导，且最终路径收容在 dirp 内，防止目录名携带 ../ 造成路径穿越改名
            rename_to = ""
            for i in os.listdir(dirp):
                if dirname == i:
                    prefix = i[:20-3] if 'zhihu' in filepath else i[:23]
                    rename_to = os.path.join(dirp, prefix + newtitle)
                    break
            if rename_to and os.path.realpath(rename_to).startswith(os.path.realpath(dirp) + os.sep):
                os.rename(savepath, rename_to)
                # 目录已改名，同步修正返回给前端的文件路径，否则前端拿到旧路径后续点赞/收藏/传图全部失效
                savefile = os.path.join(rename_to, savename)

    if len(filepath) > 0:
        webdir = web_dir_of(filepath)

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

    markdown = markdown2.markdown(markdown, extras=["tables", "admonitions", "breaks"])
    
    if len(filepath) > 0:
        markdown = markdown.replace('''<img src=\"''',\
            '''<img crossorigin=\"use-credentials\" loading=\"eager\" class=\"preview_img\"''' + \
            '''src=\"''' + webdir + os.sep)
        
        def keepLeetcodeImage(text):
            inp = text[0]
            if "https" in inp and "leetcode" in inp:
                return inp.replace('''<img crossorigin=\"use-credentials\" loading=\"eager\" class=\"preview_img\"''' + \
            '''src=\"''' + webdir + os.sep, '''<img src=\"''')
            else:
                return inp
        
        markdown = regular.sub(r'<img crossorigin=.*/?>', keepLeetcodeImage, markdown)
        
    def keepLeetcodeImagePreview(text):
        inp = text[0]
        return inp.replace('''<img ''', '''<img width=\"100%\"''')
        
    markdown = regular.sub(r'<img .*/?>', keepLeetcodeImagePreview, markdown)

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

def _backup_deleted(src, dstdir):
    """把被管理员删除的内容备份到 administer/<urlmail>/ 目录，供管理员审查恢复。
    不再使用 os.system("sudo cp ...")：既不安全（路径可注入），无 sudo 权限时还会静默失败。"""
    try:
        if not src or not os.path.exists(src):
            return
        base = os.path.basename(str(src).rstrip(os.sep))
        dst = os.path.join(dstdir, base)
        if os.path.exists(dst):
            postDate = datetime.fromtimestamp(time.time() + timezone).isoformat()[:19].replace(":", "_")
            dst = os.path.join(dstdir, postDate + "_" + base)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
        else:
            shutil.copytree(src, dst)
    except Exception as e:
        print("backup deleted content error: ", e)

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
                    if len(i) > 0 and i[-1]==os.sep:
                        i = i[:-1]
                    _backup_deleted(i, urlmaildir)
                dir = '\n'.join(dir)
            else:
                if len(dir) > 0 and dir[-1]==os.sep:
                    dir = dir[:-1]
                _backup_deleted(dir, urlmaildir)
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

    auth = check_identity(request, req, admin_bypass=True)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    realdir = os.path.realpath(currentpage)  # realpath 归一化后校验归属，防 ../ 穿越删除他人文章目录
    # 所有身份（含管理员）都只允许删除项目 people/ 或 article/ 下的目录，防误删与被入侵后任意删
    root = os.path.realpath(os.path.abspath(__file__ + "/../../../"))
    allowed_roots = [os.path.join(root, 'people') + os.sep, os.path.join(root, 'article') + os.sep]
    if not any(realdir.startswith(a) for a in allowed_roots):
        return JsonResponse( { "ret" : -100} , safe = False)
    if not is_admin(get['quanxian']) and (f"/people/{get['mail']}/" not in realdir or '.md' not in tail):
        return JsonResponse( { "ret" : -100} , safe = False)
    try:
        # 只失效受影响目录的文章列表缓存（键为文章根目录），不再清空全用户缓存
        allfile.pop(currentpage, None)
        allfile.pop(os.path.dirname(currentpage), None)
        if is_admin(get['quanxian']) and get['mail']!=get['urlmail']:
            notify_administer(currentpage, get['truemail'], get['mail'], get['urlmail'], False)
        elif is_admin(get['quanxian']) and get['mail']==get['urlmail']:
            notify_administer(currentpage, get['truemail'], get['mail'], get['urlmail'], True)
        shutil.rmtree(currentpage)
        return JsonResponse( { "done" : currentpage , 'ret':True} , safe = False)
    except:
        return JsonResponse( { "done" : currentpage , 'ret':0} , safe = False)

def editArticle(request):
    re = request.GET.dict()
    currentpage = re["path"]
    # 安全校验：只允许读取站内文章 markdown 文件（people/ 或 article/ 下的 .md），
    # 防止任意路径读取导致 member.txt 等敏感文件泄露
    real = os.path.realpath(currentpage) if currentpage else ""
    root = os.path.realpath(os.path.abspath(__file__ + "/../../../"))
    allowed_roots = [os.path.join(root, 'people') + os.sep, os.path.join(root, 'article') + os.sep]
    if not real.endswith('.md') or not any(real.startswith(a) for a in allowed_roots):
        return JsonResponse( { "ret" : -100 } , safe = False)
    dirname = currentpage.split(os.sep)[-2]
    postDate = datetime.fromtimestamp(time.time() +timezone).isoformat()[:19].replace(":", "_")
    postDate = postDate.replace("T", " ")
    if '20'==dirname[:2] or '21' == dirname[:2]:
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
    else:
        tail = ""
    return tail

# https://docs.djangoproject.com/zh-hans/5.1/topics/http/file-uploads/
def handle_uploaded_file(f, savename):
    with open(savename, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)
        # destination.write(f)

def replacewithjpg(path, quality = 60, max_side = 1920):
    """图片统一转 JPG 并压缩：质量 quality；最长边超过 max_side 时等比缩小。
    手机原图动辄 5-10MB，压缩+缩小后约几百 KB，控制服务器磁盘占用。"""
    tails = (path[-6:]).lower()
    if '.jpg' in tails or '.png' in tails or \
       '.jpeg' in tails or 'bmp' in tails or \
       '.gif' in tails:
        # 兜底：图片数据损坏/无法解码时保留原文件直接返回，上传不应 500
        try:
            nowpath = path.replace("." + path[-6:].split(".")[-1], '.jpg')
            img = Image.open(path).convert("RGB")
            # 超大图等比缩小（最长边限制），LANCZOS 缩放质量较好
            try:
                w, h = img.size
                if max_side > 0 and max(w, h) > max_side:
                    scale = max_side / float(max(w, h))
                    img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
            except Exception:
                pass
            nam = nowpath.split(os.sep)[-1]
            try:
                os.remove(path)
            except:
                pass
            img.save(nowpath, quality = quality)
            return nam, nowpath
        except Exception:
            return path.split(os.sep)[-1], path

@csrf_exempt
def uploadImg(request):
    global path
    # body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    req = request.POST.dict()
    # https://docs.djangoproject.com/zh-hans/5.1/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile
    uploadImageName = request.FILES['file'].name
    tail = getTail(uploadImageName)
    # 安全：仅允许图片扩展名上传，防止 .html/.svg 等可执行内容落到静态目录形成存储型 XSS
    if not tail:
        return JsonResponse({ "ret" : -1, "msg" : "仅支持上传图片（jpg/jpeg/png/bmp/gif）" }, safe=False)
    # 安全：剥离路径成分，防文件名携带 ../ 逃逸保存目录
    uploadImageName = os.path.basename(uploadImageName)
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
    # 安全：先完成身份认证，再进行任何文件系统访问（os.listdir/os.path.exists），
    # 防止未认证用户借「目录是否存在/同名文件是否触发改名」的差异探测任意路径
    auth = check_identity(request, req)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    if f"{get['mail']}" not in str(req.get('url', '')):
        return JsonResponse( { "ret" : -100} , safe = False)
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
        # 兜底：path 指向的文章目录可能已被改名/删除，直接 listdir 会 500；此时跳过重名检测走新建目录即可
        if not os.path.isdir(dirpath):
            dirpath = ""
        if dirpath:
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
    # 认证已前置完成（见函数开头），此处只负责确定保存根目录
    basepath = deepcopy(path)
    basepath = basepath.replace("/article/", f"/people/{get['mail']}/")

    dirp = basepath
    postDa = datetime.fromtimestamp(time.time() +timezone).isoformat()[:19].replace(":", "_")
    postDate = postDa.replace("T", "_空格_").replace(":", "_")

    # 管理员编辑他人/公共文章配图时，保存到原文章所在目录，而不是管理员自己的目录
    try:
        if is_admin(get.get('quanxian')) and len(mdpath) > 0 and os.path.exists(mdpath):
            origindir = os.path.dirname(mdpath)
            # 安全：管理员代存配图也只允许落在 people/ 或 article/ 内
            realdir = os.path.realpath(origindir)
            root = os.path.realpath(os.path.abspath(__file__ + "/../../../"))
            allowed_roots = [os.path.join(root, 'people') + os.sep, os.path.join(root, 'article') + os.sep]
            if os.path.isdir(origindir) and any(realdir.startswith(a) for a in allowed_roots):
                dirp = origindir
    except Exception:
        pass

    if 'zhihu' in mdpath:
        postDate = postDa.replace("T", "_").replace(":", "_")[:-2]
        dirp = dirp.replace("csdn_spider", "zhihu_spider")
    
    savepath = os.path.join(dirp, postDate + "_" + title)
    if len(dirname) > 0:
        for i in os.listdir(dirp):
            if dirname == i: # or (len(old_title) > 0 and old_title in i):
                savepath = os.path.join(dirp, i)
    if not os.path.exists(savepath):
        # 递归创建，兼容新用户首次上传（上层目录可能还不存在）
        os.makedirs(savepath, exist_ok=True)

    dirlast = savepath.split(os.sep)[-1]
    
    uploadname = uploadImageName # str(number) + tail
    imgpath = os.path.join(savepath, uploadname)
    handle_uploaded_file(request.FILES['file'], imgpath)

    uploadname, nowpath = replacewithjpg(imgpath)

    lastpath = savepath
    if new_Title:
        title = newtitle
        # 安全：同 postArticle，改名目标必须由 dirp 下真实存在的目录项推导并收容在 dirp 内
        rename_to = ""
        for i in os.listdir(dirp):
            if dirname == i:
                prefix = i[:20-3] if 'zhihu' in mdpath else i[:23]
                rename_to = os.path.join(dirp, prefix + newtitle)
                break
        if rename_to and os.path.realpath(rename_to).startswith(os.path.realpath(dirp) + os.sep):
            os.rename(savepath, rename_to)
        if rename_to:
            lastpath = rename_to
            dirlast = os.path.basename(rename_to)

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
    try:
        # 日志封顶：超过 10MB 轮转为 .old，防止 article/clickpage.txt 无限增长
        try:
            if os.path.exists(ckf) and os.path.getsize(ckf) > 10 * 1024 * 1024:
                os.replace(ckf, ckf + '.old')
        except Exception:
            pass
        with open(ckf, 'a+', encoding='utf-8') as obj:
            obj.write(postDate + ',' + ip_address + ',' + type + '\n')
    finally:
        clicktxt.release()

def clickpage(request):
    global addpath
    rep = request.GET.dict()
    # type 缺参兜底 + 消毒限长：只保留字母数字下划线，防任意字符串写入 clickpage.txt
    type = regular.sub(r'[^0-9A-Za-z_-]', '', str(rep.get('type', 'unknown')))[:32] or 'unknown'
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
    
    # 快速失败：写失败只丢弃本次点击统计，不再 sleep(30)×100 次重试占住 worker
    try:
        write_click(ckf, postDate, ip_address, type)
    except Exception:
        pass
    return HttpResponse(",")

def GetSetting(request):
    global path, Setting_Formel, LeftSetting_Formel, ffmute, fleftmute
    # 空 body / 非法 JSON 按匿名读兜底，避免 500
    try:
        req = json.loads(request.body)
        if not isinstance(req, dict):
            req = {}
    except Exception:
        req = {}
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
            try:
                _atomic_write_json(file, Setting_Formel)
            finally:
                ffmute.release()
            for i in range(1, SETTING_SLOTS_MAX + 1):
                nth = os.path.join(basepath, 'setting', str(i))
                os.makedirs(nth, exist_ok=True)

        try:
            with open(file, 'r', encoding='utf-8') as obj:
                jfile = json.load(obj)
        except Exception:
            # f.json 损坏/非列表时回退默认模板并原子重写，避免读接口 500
            jfile = deepcopy(Setting_Formel)
            ffmute.acquire()
            try:
                _atomic_write_json(file, jfile)
            finally:
                ffmute.release()
        if not isinstance(jfile, list):
            jfile = deepcopy(Setting_Formel)
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
            try:
                _atomic_write_json(file, LeftSetting_Formel)
            finally:
                fleftmute.release()
            for i in range(1, SETTING_SLOTS_MAX + 1):
                nth1 = os.path.join(basepath, 'set_left', str(i), '1')
                nth2 = os.path.join(basepath, 'set_left', str(i), '2')
                nth3 = os.path.join(basepath, 'set_left', str(i), '3')
                os.makedirs(nth1, exist_ok=True)
                os.makedirs(nth2, exist_ok=True)
                os.makedirs(nth3, exist_ok=True)
        try:
            with open(file, 'r', encoding='utf-8') as obj:
                jfile = json.load(obj)
        except Exception:
            # fleft.json 损坏/非列表时回退默认模板并原子重写，避免读接口 500
            jfile = deepcopy(LeftSetting_Formel)
            fleftmute.acquire()
            try:
                _atomic_write_json(file, jfile)
            finally:
                fleftmute.release()
        if not isinstance(jfile, list):
            jfile = deepcopy(LeftSetting_Formel)
    return JsonResponse( { "jfile" : jfile} , safe = False)

fbookmute = Semaphore(value=1)
def mainpagedataget(request):
    global path, Setting_Formel, LeftSetting_Formel, ffmute, fleftmute, fbookmute
    # 空 body / 非法 JSON 按匿名读兜底，避免 500
    try:
        req = json.loads(request.body)
        if not isinstance(req, dict):
            req = {}
    except Exception:
        req = {}
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
            os.makedirs(kkk, exist_ok=True)
        if not os.path.exists(inpath):
            kk = []
            fbookmute.acquire()
            try:
                _atomic_write_json(inpath, kk)
            finally:
                fbookmute.release()
        else:
            try:
                with open(inpath, 'r', encoding='utf-8') as obj:
                    kk = json.load(obj)
            except Exception:
                # fbook.json 损坏时按空书架兜底，避免 500
                kk = []
        if not isinstance(kk, list):
            kk = []

        # 过滤参数在循环外归一一次：书架扩容到 30000 本后，逐本重复解析参数的开销不可接受
        sval = str(req.get('search', ''))
        words = [w for w in sval.lower().split(" ") if w] if sval else []
        try:
            cbv = int(req.get('checkboxval', 2))
        except (TypeError, ValueError):
            cbv = 2
        if cbv not in (0, 1):
            cbv = 2

        # 单次遍历完成搜索+筛选，只收集条目引用不做任何 IO（listdir 留到分页后只做当前页）
        matched = []
        for i in kk:
            if not isinstance(i, dict) or i.get('name', "") == "":
                continue
            if words:
                # 4 字段拼接后一次 lower 代替「每搜索词 × 每字段」4 次 lower
                hay = " ".join((str(i.get(f, '')) for f in ('name', 'github', 'readdate', 'ratio'))).lower()
                hit = False
                for ir in words:
                    if ir in hay:
                        hit = True
                        break
                if not hit:
                    continue
            if cbv != 2:
                # finished 兼容 True/False/1/0/"1"；异常值按未看完处理，避免 int() 500
                fin = i.get('finished', False)
                fin = fin is True or fin == 1 or fin == '1'
                if cbv != int(fin):
                    continue
            matched.append(i)

        # 分页：请求带 currentpage>=1 时只对当前页做封面 listdir（30000 本全量会做 3 万次 listdir）
        # 页码超出有效范围时钳制到最后一页，删除清空末页后前端无需二次请求
        try:
            bookpage = int(req.get('currentpage', 0))
        except (TypeError, ValueError):
            bookpage = 0
        if bookpage >= 1:
            try:
                bookps = int(req.get('pagesize', 0))
            except (TypeError, ValueError):
                bookps = 0
            if bookps < 1:
                bookps = int(siteconfig.get('book_default_pagesize'))
            bookps = min(bookps, int(siteconfig.get('book_max_pagesize')))
            npages = max(1, (len(matched) + bookps - 1) // bookps)
            if bookpage > npages:
                bookpage = npages
            start = (bookpage - 1) * bookps
            page_items = matched[start:start + bookps]
        else:
            # 兼容旧调用（未带分页参数）：维持全量返回
            start = 0
            page_items = matched

        for offset, i in enumerate(page_items):
            nval = str(i.get('n', ''))
            setting = os.path.join(basepath, 'imgbook', nval) if nval else ''
            # 无封面书可能没有 imgbook/<n> 图片目录，缺目录时按无图兜底，避免 listdir 500
            im = [ijk for ijk in (os.listdir(setting) if nval and os.path.isdir(setting) else []) if '.jpg' in ijk.lower()]
            if len(im) > 0:
                setting = os.path.join(basepath, 'imgbook', nval, im[0])
                if 'people' in setting:
                    imgurl = '/people' + setting.split("people")[-1]
                else:
                    imgurl = '/article' + setting.split("article")[-1]
                i['img'] = imgurl
            else:
                i['img'] = '/article/logobeian.png'
            i['imglist'] = [i['img']]
            if i.get('readdate', '') != '':
                i['ratio'] = i['readdate'] + ", " + i.get('ratio', '')
            i['website'] = r'https://s.taobao.com/search?_input_charset=utf-8&commend=all&ie=utf8&initiative_id=tbindexz_20170306&localImgKey=&page=1&q=' + str(i.get('name',''))
            # number 为匹配结果里的全局序号（跨页连续），分页后仍从 1 连续编号
            i['number'] = str(start + offset + 1)
            jfile.append(i)
        return JsonResponse( { "jfile" : jfile, "length" : len(matched), "page" : bookpage if bookpage >= 1 else 1 } , safe = False)
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
            try:
                _atomic_write_json(file, Setting_Formel)
            finally:
                ffmute.release()
        # 60 槽位图片目录幂等补建：老用户的 f.json 已存在时上面初始化块不会走，
        # 目录只停留在旧版 1..10，槽位 11..60 的图片将无处存放（幂等，开销为 60 次 exists）
        for i in range(1, SETTING_SLOTS_MAX + 1):
            nth = os.path.join(basepath, 'setting', str(i))
            os.makedirs(nth, exist_ok=True)
        delete = []
        try:
            with open(file, 'r', encoding='utf-8') as obj:
                jfile = json.load(obj)
        except Exception:
            # f.json 损坏/非列表时回退默认模板并原子重写，避免读接口 500
            jfile = deepcopy(Setting_Formel)
            ffmute.acquire()
            try:
                _atomic_write_json(file, jfile)
            finally:
                ffmute.release()
        if not isinstance(jfile, list):
            jfile = deepcopy(Setting_Formel)
        for j in range(len(jfile)):
                if not isinstance(jfile[j], dict):
                    # 非 dict 条目归一为空 dict，走后面的删除过滤，避免 AttributeError 500
                    jfile[j] = {}
                # 旧格式/手工写坏的数据缺键时 .get 兜底，避免 KeyError 500
                jfile[j]['introduction'] = str(jfile[j].get('introduction', ''))
                jfile[j]['link'] = str(jfile[j].get('link', ''))
                jfile[j]['link_describe'] = str(jfile[j].get('link_describe', ''))
                jfile[j]['other_describe'] = str(jfile[j].get('other_describe', ''))
                jfile[j]['button'] = str(jfile[j].get('button', ''))
                jfile[j]['n'] = jfile[j].get('n', '')
                if jfile[j]['introduction']=="" or str(jfile[j]['n'])=="":
                    # 缺 introduction/n 的条目无法渲染与定位图片目录，按删除过滤
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
            try:
                prepa = os.path.abspath(__file__ + "/../../../")
                shutil.copyfile(os.path.join(prepa, 'article', "2寸.jpg"), os.path.join(setting, '2寸.jpg'))
            except Exception:
                pass
        imgs = os.listdir(setting)
        if len(imgs)==0:
            # 头像目录意外为空（默认头像复制失败/被误删）时重放一次，防 listdir()[0] IndexError 500
            try:
                prepa = os.path.abspath(__file__ + "/../../../")
                shutil.copyfile(os.path.join(prepa, 'article', "2寸.jpg"), os.path.join(setting, '2寸.jpg'))
            except Exception:
                pass
            imgs = os.listdir(setting)
        if len(imgs)==0:
            # 仍为空（目录不可写等极端情况）时退回全站默认头像，保证响应结构不变
            ll.append('/article/2寸.jpg')
        else:
            f1 = imgs[0]
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
            try:
                _atomic_write_json(file, LeftSetting_Formel)
            finally:
                fleftmute.release()
        # 60 槽位 ×3 子按钮图片目录幂等补建（同 setting 分支：老用户旧文件不触发初始化块）
        for i in range(1, SETTING_SLOTS_MAX + 1):
            nth1 = os.path.join(basepath, 'set_left', str(i), '1')
            nth2 = os.path.join(basepath, 'set_left', str(i), '2')
            nth3 = os.path.join(basepath, 'set_left', str(i), '3')
            os.makedirs(nth1, exist_ok=True)
            os.makedirs(nth2, exist_ok=True)
            os.makedirs(nth3, exist_ok=True)
        delete = []
        try:
            with open(file, 'r', encoding='utf-8') as obj:
                jfile = json.load(obj)
        except Exception:
            # fleft.json 损坏/非列表时回退默认模板并原子重写，避免读接口 500
            jfile = deepcopy(LeftSetting_Formel)
            fleftmute.acquire()
            try:
                _atomic_write_json(file, jfile)
            finally:
                fleftmute.release()
        if not isinstance(jfile, list):
            jfile = deepcopy(LeftSetting_Formel)
        for j in range(len(jfile)):
                if not isinstance(jfile[j], dict):
                    # 非 dict 条目归一为空 dict，走后面的删除过滤，避免 AttributeError 500
                    jfile[j] = {}
                # 旧格式/手工写坏的数据缺键时 .get 兜底，避免 KeyError 500
                jfile[j]['introduction'] = str(jfile[j].get('introduction', ''))
                jfile[j]['link'] = str(jfile[j].get('link', ''))
                jfile[j]['color'] = str(jfile[j].get('color', '#000000')) or '#000000'
                jfile[j]['button1'] = str(jfile[j].get('button1', ''))
                jfile[j]['button2'] = str(jfile[j].get('button2', ''))
                jfile[j]['button3'] = str(jfile[j].get('button3', ''))
                jfile[j]['n'] = jfile[j].get('n', '')
                if jfile[j]['introduction']=="" or str(jfile[j]['n'])=="":
                    # 缺 introduction/n 的条目无法渲染与定位图片目录，按删除过滤
                    delete.append(jfile[j])
                else:
                    # 左侧卡片 style 与按钮缺省兜底，避免前端渲染异常
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
    if 'file' not in request.FILES:
        # 未携带文件字段时返回业务错误而非 MultiValueDictKeyError 500
        return JsonResponse( { "ret" : -105, "msg": "缺少上传文件" } , safe = False)
    uploadImageName = request.FILES['file'].name.replace(" ", "_")
    tail = getTail(uploadImageName)
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    auth = check_identity(request, req)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
    if f"{get['mail']}" not in req.get('url', ''):
        return JsonResponse( { "ret" : -100} , safe = False)

    # 路径消毒：n/index 直接参与 os.path.join，只允许数字（set_left 的 n 形如 "3_1"），
    # 防止 "../" 目录穿越写到任意路径（含 clickcard 分支 listdir+remove 清空穿越目录的破坏面）
    for k in ('n', 'index'):
        if k in req.keys():
            req[k] = regular.sub(r'[^0-9_]', '', str(req[k])) if k == 'n' else regular.sub(r'[^0-9]', '', str(req[k]))
            if req[k] == '':
                req.pop(k)

    setting = None
    if 'n' in req.keys():
        setting = os.path.join(basepath, 'setting', req['n'])
    if 'index' in req.keys():
        if 'n' not in req.keys():
            return JsonResponse( { "ret" : -101, "msg": "set_left 上传缺少 n 参数"} , safe = False)
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
            kk = []
            if os.path.exists(inpath):
                try:
                    with open(inpath, 'r', encoding='utf-8') as obj:
                        kk = json.load(obj)
                except Exception:
                    kk = []
            if not isinstance(kk, list):
                kk = []
            # n 统一按 int 提取；历史脏数据（如字符串 "1"）转不了 int 时跳过，防混型 sort() TypeError
            kkey = []
            for ijk in kk:
                if isinstance(ijk, dict):
                    try:
                        kkey.append(int(ijk.get('n', 0)))
                    except (TypeError, ValueError):
                        continue
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
            if 'n' not in req.keys():
                # n 全为非法字符被消毒段剔除时缺失，直接返回业务错误而非 KeyError 500
                return JsonResponse( { "ret" : -104, "msg": "改封面缺少 n 参数"} , safe = False)
            # n 已消毒为纯数字；统一转 int，避免与 addbook 写入的 int n 混型
            maxmax = int(req['n'])
        setting = os.path.join(setting, str(maxmax))
        if not os.path.exists(setting):
            os.makedirs(setting, exist_ok=True)
        for i in os.listdir(setting):
            os.remove(os.path.join(setting, i))

    if setting is None:
        # 既无 person/ImgbookUpload 也无 n/index 参数时无法确定上传目标目录
        return JsonResponse( { "ret" : -102, "msg": "缺少上传目标参数"} , safe = False)
    if not os.path.exists(setting):
        os.makedirs(setting)
    # https://docs.djangoproject.com/zh-hans/5.1/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile
    # uploadType = request.FILES['file'].content_type

    imgpath = os.path.join(setting, uploadImageName)
    handle_uploaded_file(request.FILES['file'], imgpath)

    try:
        uploadImageName, nowpath = replacewithjpg(imgpath)
    except Exception:
        # 非图片/损坏文件：清理残件并返回业务错误，避免 500
        try:
            os.remove(imgpath)
        except OSError:
            pass
        return JsonResponse( { "ret" : -103, "msg": "上传文件不是有效图片"} , safe = False)

    if 'ImgbookUpload' in req.keys():
        inpath = os.path.join(basepath, 'imgbook', 'fbook.json')
        find = -9
        kk = []
        if os.path.exists(inpath):
            try:
                with open(inpath, 'r', encoding='utf-8') as obj:
                    kk = json.load(obj)
            except Exception:
                kk = []
        if not isinstance(kk, list):
            kk = []
        if 'clickcard' in req.keys():
            # 改封面（修改对话框重传）：按 n 原位更新对应条目的 img；
            # 旧行为每次都追加无名槽位，导致 fbook.json 堆积垃圾条目
            for i in range(len(kk)):
                if isinstance(kk[i], dict) and str(kk[i].get('n', '')) == str(maxmax):
                    kk[i]['img'] = uploadImageName
                    find = 9
                    break
        if find < 0:
            # 封面暂存槽位同样受书架容量上限约束，防止绕过 addbook 刷出超限条目
            if len(kk) < int(siteconfig.get('book_max_items')):
                kk.append({"github": "", "img": uploadImageName, "name": "", \
                           "ratio": "", "n": maxmax, "readdate": "", 'finished':False, 'author':""})
        fbookmute.acquire()
        try:
            _atomic_write_json(inpath, kk)
        finally:
            fbookmute.release()

    if 'person' in req.keys() and len(os.listdir(setting)) > 1 and len(xiang)!=0:
        os.remove(os.path.join(setting, xiang))

    return JsonResponse( { "ret" : True} , safe = False)

membermutex = regmute  # member.txt 全站唯一写锁：memmute/regmute/membermutex 三名同锁，防止跨函数并发读改写竞态
def NicknameSetting(request):
    global path, membermutex
    # 空 body / 非法 JSON 按未授权兜底，避免 500
    try:
        req = json.loads(request.body)
        if not isinstance(req, dict):
            req = {}
    except Exception:
        req = {}
    # 昵称消毒：剔除 member.txt 分隔符与换行，防止昵称注入破坏 member.txt 行结构；并限长防滥用
    if 'modifiednickname' in req.keys():
        req["modifiednickname"] = str(req["modifiednickname"]).replace(MEMBER_SEP, "").replace("\n", " ").replace("\r", " ")[:int(siteconfig.get('nickname_max_len'))]

    # req = request.POST.dict()
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    auth = check_identity(request, req)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
    if f"{get['mail']}" not in req.get('url', ''):
        return JsonResponse( { "ret" : -100} , safe = False)

    if (auth['passed'] or not auth['keyok']) and 'modifiednickname' in req.keys() and len(req["modifiednickname"])!=0:
        addpa = os.path.abspath(__file__ + "/../../")
        member = os.path.join(addpa, "..", "article", 'member.txt')

        cll = []
        passwd = req.get('password', '')

        prepa = os.path.abspath(__file__ + "/../../../")
        oldpassword = os.path.join(prepa, 'article', 'oldpassword')
        if not os.path.exists(oldpassword):
            os.makedirs(oldpassword)
        # 读-改-写全程持锁：open('w') 截断瞬间其他线程可能读到空文件并写回空（曾导致 member.txt 被清空）
        membermutex.acquire()
        try:
            postDate = datetime.fromtimestamp(time.time() +timezone).isoformat()[:19].replace(":", "_")
            shutil.copyfile(member, os.path.join(oldpassword, postDate + '_member.txt'))

            with open(member, 'r', encoding='utf-8') as fp:
                for line in fp.readlines():
                    cll.append(line)
                    i = line.strip().split("<》!=$)(=$@")
                    if len(i) < 3:
                        # 空行/脏行（字段不足 3）跳过，防 IndexError 破坏 member.txt 写回
                        continue
                    ml = i[1]
                    if (auth['passed'] and ml==get['urlmail'] and verify_member_password(i[0], passwd)) or \
                        (not auth['keyok'] and get['urlmail']==ml):
                        i[2] = req["modifiednickname"]
                        i = "<》!=$)(=$@".join(i) + '\n'
                        cll.pop()
                        cll.append(i)
            _atomic_write_member(member, ''.join(cll))
        finally:
            membermutex.release()
    return JsonResponse( { "ret" : True} , safe = False)

def FormsubmitSetting(request):
    global path, membermutex, ffmute, fleftmute, fbookmute
    # 空 body / 非法 JSON 按未授权兜底，避免 500
    try:
        req = json.loads(request.body)
        if not isinstance(req, dict):
            req = {}
    except Exception:
        return JsonResponse( { "ret" : -100} , safe = False)

    # req = request.POST.dict()
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    auth = check_identity(request, req)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
    if f"{get['mail']}" not in req.get('url', ''):
        return JsonResponse( { "ret" : -100} , safe = False)
    # 新用户首次保存配置时 people/<mail>/ 及其子目录可能不存在，直接写 json 会 FileNotFoundError(500)
    for sub in ('', 'setting', 'imgbook', 'set_left'):
        os.makedirs(os.path.join(basepath, sub) if sub else basepath, exist_ok=True)

    # 书架/卡片字段统一长度上限（siteconfig 可调），防超大 payload 滥用磁盘
    book_max = int(siteconfig.get('book_max_field_len'))
    setting_max = int(siteconfig.get('setting_max_field_len'))

    if 'delete' in req.keys():
        inpath = os.path.join(basepath, 'imgbook', 'fbook.json')
        kk = []
        if os.path.exists(inpath):
            try:
                with open(inpath, 'r', encoding='utf-8') as obj:
                    kk = json.load(obj)
            except Exception:
                kk = []
        if not isinstance(kk, list):
            kk = []
        if 'n' in req.keys():
            for i in range(len(kk)):
                if isinstance(kk[i], dict) and str(kk[i].get('n', '')) == str(req['n']):
                    # n 来自服务端数据也消毒为纯数字，防脏数据拼接出穿越路径 rmtree 误删
                    nclean = regular.sub(r'[^0-9]', '', str(kk[i].get('n', '')))
                    inp = os.path.join(basepath, 'imgbook', nclean) if nclean else ''
                    if inp and os.path.isdir(inp):
                        shutil.rmtree(inp)
                    kk.remove(kk[i])
                    break
        fbookmute.acquire()
        try:
            _atomic_write_json(inpath, kk)
        finally:
            fbookmute.release()
        return JsonResponse( { "ret" : True} , safe = False)

    SettingForm = req.get('SettingForm')
    if not isinstance(SettingForm, list):
        # 缺失/非列表的 SettingForm 兜底为空列表，避免 KeyError/TypeError 500
        SettingForm = []
    SettingForm = [sf for sf in SettingForm if isinstance(sf, dict)][:int(siteconfig.get('setting_max_items'))]
    if 'Left' not in req.keys() and 'addbook' not in req.keys() and 'clickcard' not in req.keys():
        for sf in SettingForm:
            for fk in ('introduction', 'link', 'link_describe', 'other_describe', 'button'):
                sf[fk] = _clean_field(sf.get(fk, ''), setting_max)
            if '/$删除$/' in sf['introduction']:
                sf['introduction'] = ""
                sf['link'] = ""
                sf['link_describe'] = ""
                sf['other_describe'] = ""
                sf['button'] = ""
                setting = os.path.join(basepath, 'setting', regular.sub(r'[^0-9]', '', str(sf.get('n', ''))))
                if os.path.isdir(setting):   # 目录缺失时跳过清理，避免 listdir 500
                    for i in os.listdir(setting):
                        os.remove(os.path.join(setting, i))
        file = os.path.join(basepath, 'setting', 'f.json')
        ffmute.acquire()
        try:
            _atomic_write_json(file, SettingForm)
        finally:
            ffmute.release()
        # 保存后按条目即时补建槽位图片目录（幂等），前端"传图→保存"任意时序下目录都存在
        for sf in SettingForm:
            nclean = regular.sub(r'[^0-9]', '', str(sf.get('n', '')))
            if nclean:
                os.makedirs(os.path.join(basepath, 'setting', nclean), exist_ok=True)
    elif 'clickcard' in req.keys():
        inpath = os.path.join(basepath, 'imgbook', 'fbook.json')
        kk = []
        if os.path.exists(inpath):
            try:
                with open(inpath, 'r', encoding='utf-8') as obj:
                    kk = json.load(obj)
            except Exception:
                kk = []
        if not isinstance(kk, list):
            kk = []
        for i in range(len(kk)):
                if isinstance(kk[i], dict) and str(kk[i].get('n', '')) == str(req.get('n', '')):
                    # n 来自服务端数据也消毒为纯数字，防脏数据拼接出穿越路径
                    nclean = regular.sub(r'[^0-9]', '', str(kk[i].get('n', '')))
                    inp = os.path.join(basepath, 'imgbook', nclean) if nclean else ''
                    olt = os.listdir(inp) if inp and os.path.isdir(inp) else []
                    if len(olt) > 0:
                        kk[i]['img'] = olt[0]
                    # 字段 .get 兜底 + 限长，缺键不再 KeyError 500
                    kk[i]['github'] = _clean_field(req.get('github', ''), book_max)
                    kk[i]['name'] = _clean_field(req.get('name', ''), book_max)
                    kk[i]['readdate'] = _clean_field(req.get('readdate', ''), book_max)
                    kk[i]['ratio'] = _clean_field(req.get('ratio', ''), book_max)
                    kk[i]['finished'] = bool(req.get('finished'))
                    kk[i]['author'] = _clean_field(req.get('author', ''), book_max)
                    break
        fbookmute.acquire()
        try:
            _atomic_write_json(inpath, kk)
        finally:
            fbookmute.release()
    elif 'addbook' in req.keys():
        onebook = req.get('addbook')
        if not isinstance(onebook, dict):
            # addbook 缺失/非 dict 时返回业务错误而非 AttributeError 500
            return JsonResponse( { "ret" : -106, "msg": "addbook 参数缺失" } , safe = False)
        # 新用户首次加书时 imgbook/fbook.json 还不存在；书架为空数组时也没有可复用的槽位。
        # 这里统一兜底成"复用第一个空槽位，没有空槽位就追加一条"。
        imgbookdir = os.path.join(basepath, 'imgbook')
        os.makedirs(imgbookdir, exist_ok=True)
        inpath = os.path.join(imgbookdir, 'fbook.json')
        kk = []
        if os.path.exists(inpath):
            try:
                with open(inpath, 'r', encoding='utf-8') as obj:
                    kk = json.load(obj)
            except Exception:
                kk = []
        if not isinstance(kk, list):
            kk = []
        item = {
            "name": _clean_field(onebook.get('name', ''), book_max),
            "github": _clean_field(onebook.get('github', ''), book_max),
            "readdate": _clean_field(onebook.get('readdate', ''), book_max),
            "ratio": _clean_field(onebook.get('ratio', ''), book_max),
            "finished": bool(onebook.get('finished', False)),
            "author": _clean_field(onebook.get('author', ''), book_max),
        }
        reused = False
        for b in kk:
            if isinstance(b, dict) and not b.get('name'):
                # 空槽位可能已有图片目录，保留 img 字段
                b.update(item)
                reused = True
                break
        if not reused:
            # 书架容量上限（siteconfig 可调，默认 30000 本）：满了拒绝新增而非无限追加
            book_cap = int(siteconfig.get('book_max_items'))
            if len(kk) >= book_cap:
                return JsonResponse( { "ret" : -107, "msg": f"书架已满，最多可存 {book_cap} 本" } , safe = False)
            # n 槽位取最大值 +1；历史脏数据 n 非数字时跳过，避免 int() 500
            ns = []
            for b in kk:
                try:
                    ns.append(int(b.get('n', 0)))
                except Exception:
                    pass
            nxt = max(ns + [0]) + 1
            item.update({"n": nxt, "img": ""})
            kk.append(item)
        fbookmute.acquire()
        try:
            _atomic_write_json(inpath, kk)
        finally:
            fbookmute.release()
    else:
        for sf in SettingForm:
            for fk in ('introduction', 'link', 'color', 'button1', 'button2', 'button3'):
                sf[fk] = _clean_field(sf.get(fk, ''), setting_max) or ('#000000' if fk == 'color' else '')
            if '/$删除$/' in sf['introduction']:
                sf['introduction'] = ""
                sf['link'] = ""
                sf['color'] = "#000000"
                sf['button1'] = ""
                sf['button2'] = ""
                sf['button3'] = ""
                for subn in ('1', '2', '3'):   # 子目录缺失时跳过清理，避免 listdir 500
                    setting1 = os.path.join(basepath, 'set_left', regular.sub(r'[^0-9]', '', str(sf.get('n', ''))), subn)
                    if os.path.isdir(setting1):
                        for i in os.listdir(setting1):
                            os.remove(os.path.join(setting1, i))
        file = os.path.join(basepath, 'set_left', 'fleft.json')
        fleftmute.acquire()
        try:
            _atomic_write_json(file, SettingForm)
        finally:
            fleftmute.release()
        # 同主表单分支：保存后即时补建槽位 ×3 子按钮目录
        for sf in SettingForm:
            nclean = regular.sub(r'[^0-9]', '', str(sf.get('n', '')))
            if nclean:
                for subn in ('1', '2', '3'):
                    os.makedirs(os.path.join(basepath, 'set_left', nclean, subn), exist_ok=True)

    return JsonResponse( { "ret" : True} , safe = False)

def placeTopTop(request):
    global allfile
    # req = request.GET.dict()
    req = json.loads(request.body)
    pathkkk = req["path"]
    
    # if '文篇编辑功能展示' in pathkkk:
    #     return JsonResponse( { "ret" : -100} , safe = False)
        # return JsonResponse( { "path" : pathkkk} , safe = False)

    auth = check_identity(request, req)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    if is_admin(get['quanxian']):
        # csdn 置顶的 path 是 .md 文件（不是目录），存在性校验必须用 isfile
        if not os.path.isfile(pathkkk):
            return JsonResponse( { "ret" : -100} , safe = False)
        pass  # 管理员可置顶任何用户的内容
    else:
        realtop = os.path.realpath(pathkkk)  # realpath 防穿越；文件必须存在，避免对已删文章写 TOP.txt 500
        if f"/people/{get['mail']}/" not in realtop or '.md' not in pathkkk or not os.path.isfile(realtop):
            return JsonResponse( { "ret" : -100} , safe = False)

    # dirname = pathkkk.split(os.sep)[-2]
    filename = pathkkk.split(os.sep)[-1]

    # postDa = datetime.fromtimestamp(time.time() +timezone).isoformat()[:19].replace(":", "_")
    # postDate = postDa.replace("T", "_空格_").replace(":", "_")
    
    pathkkkTmp = pathkkk.replace(filename, "TOP.txt")
    with open(pathkkkTmp, 'w', encoding="utf-8") as obj:
        obj.write("")
    # 只失效该文章根目录的列表缓存（置顶标记影响排序），不再清空全用户缓存
    allfile.pop(os.path.dirname(os.path.dirname(pathkkk)), None)
    # 统一命名：清掉历史遗留的另一种命名，避免出现双标记
    legacy = pathkkk.replace(filename, "TOP.text")
    if os.path.exists(legacy):
        os.remove(legacy)
    
    # if 'zhihu' in pathkkk:
    #     postDate = postDa.replace("T", "_").replace(":", "_")[:-2]

    # if '20'==dirname[:2] or '21' == dirname[:2]:
    #     date = dirname[:22]
    # else:
    #     date = postDate
    # if 'zhihu_' in pathkkk:
    #     date = dirname[:16]
    #     date = date[:10] + " " + date[11:]

    # dirpath = pathkkk.replace(filename, "")
    
    # os.rename(dirpath, dirpath.replace(date, postDate))
    # return JsonResponse( { "path" : dirpath.replace(date, postDate + "_") } , safe = False)
    return JsonResponse( { "path" : "" } , safe = False)


def cancelPlaceTopTop(request):
    global allfile
    # req = request.GET.dict()
    req = json.loads(request.body)
    pathkkk = req["path"]
    
    auth = check_identity(request, req)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    if is_admin(get['quanxian']):
        pass  # 管理员可取消置顶任何用户的内容
    else:
        realtop = os.path.realpath(pathkkk)  # realpath 防穿越
        if f"/people/{get['mail']}/" not in realtop or '.md' not in pathkkk:
            return JsonResponse( { "ret" : -100} , safe = False)
    filename = pathkkk.split(os.sep)[-1]

    # 兼容两种历史命名，全部清除
    for name in ("TOP.txt", "TOP.text"):
        p = pathkkk.replace(filename, name)
        if os.path.exists(p):
            os.remove(p)
    # 只失效该文章根目录的列表缓存，不再清空全用户缓存
    allfile.pop(os.path.dirname(os.path.dirname(pathkkk)), None)
    return JsonResponse( { "path" : "" } , safe = False)

# thememutex = Semaphore(value=1)
def themeChange(request):
    global path #, thememutex
    body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    req = json.loads(body)

    # req = request.POST.dict()
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    auth = check_identity(request, req)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
    if f"{get['mail']}" not in req['url']:
        return JsonResponse( { "ret" : -100} , safe = False)

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

allTraveler = {}  # {urlmail: {ip_address: 上次访问时间戳}}，按用户隔离
thememutex = Semaphore(value=1)
# 访客统计阈值统一收敛到 site_config.json（traveler_* 键），修改 JSON 即时生效

def read_traveler_count(urlmail):
    """读取指定用户的访客统计值（TravelerStatistics.txt），缺失或损坏时返回下限"""
    fileTraveler = os.path.abspath(__file__ + "/../../../")
    fileTravelerPath = os.path.join(fileTraveler, 'people', urlmail, siteconfig.get('traveler_filename'))
    _baseline = int(siteconfig.get('traveler_baseline'))
    try:
        with open(fileTravelerPath, 'r', encoding='utf-8') as obj:
            return max(int(obj.read().strip()), _baseline)
    except:
        return _baseline

def getStatisticTravelerCount(request, urlmail):
    # 访客统计按 urlmail 隔离：文件是唯一数据源，不再使用跨用户共享的全局变量
    fileTraveler = os.path.abspath(__file__ + "/../../../")
    fileTravelerPath = os.path.join(fileTraveler, 'people', urlmail, siteconfig.get('traveler_filename'))
    ip_address = request.headers.get('X-Real-Ip') or request.headers.get('X-Forwarded-For')
    if not ip_address:
        # 本地调试/压测时无反向代理头，回退到 REMOTE_ADDR，
        # 否则每个请求都会走写文件分支，高并发下成为瓶颈
        ip_address = request.META.get('REMOTE_ADDR', '')
    thememutex.acquire()
    try:
        if not os.path.exists(fileTravelerPath):
            os.makedirs(os.path.join(fileTraveler, 'people', urlmail), exist_ok=True)
            with open(fileTravelerPath, 'w', encoding='utf-8') as obj:
                obj.write(str(siteconfig.get('traveler_default_init')))
        with open(fileTravelerPath, 'r', encoding='utf-8') as obj:
            try:
                TravelerStatistics = int(obj.read().strip())
            except:
                TravelerStatistics = int(siteconfig.get('traveler_default_init'))
        postDa = int(time.time() + timezone)
        updated = False
        if ip_address:
            visitors = allTraveler.setdefault(urlmail, {})
            # 同一 IP 去重窗口内重复访问同一用户不重复计数（按用户独立去重，窗口见配置 traveler_dedup_window_seconds）
            _dedup_window = int(siteconfig.get('traveler_dedup_window_seconds'))
            if ip_address not in visitors or postDa - visitors[ip_address] > _dedup_window:
                visitors[ip_address] = postDa
                updated = True
            # 清理超过 traveler_cleanup_seconds 未活动的访客记录
            _cleanup = int(siteconfig.get('traveler_cleanup_seconds'))
            for key in [k for k, v in visitors.items() if postDa - v > _cleanup]:
                visitors.pop(key)
        else:
            updated = True
        if updated:
            TravelerStatistics = max(TravelerStatistics + 1, int(siteconfig.get('traveler_baseline')))
            with open(fileTravelerPath, 'w', encoding='utf-8') as obj:
                obj.write(str(TravelerStatistics))
    finally:
        thememutex.release()

@csrf_exempt
def getSiteConfig(request):
    # 前端公开只读配置白名单：仅暴露与浏览器行为相关、无安全敏感的键
    PUBLIC_KEYS = ['cookie_login_days', 'mail_resend_cooldown_seconds',
                   'music_enabled', 'music_api', 'music_server', 'music_type', 'music_id',
                   'music_sources',
                   # 页脚备案信息（公安备案号/版权文字/ICP 备案号/举报邮箱）
                   'footer_gongan_code', 'footer_gongan_text', 'footer_copyright',
                   'footer_icp_text', 'footer_report_email']
    return JsonResponse({k: siteconfig.get(k) for k in PUBLIC_KEYS}, safe=False)

@csrf_exempt
def meting_proxy(request):
    """Meting 协议服务端代理（音乐播放器用）。

    浏览器直连公共 Meting API 会被断连/跨域拦截，改由 Django 服务器端转发，
    目标地址取配置 music_api，参数 server/type/id 可选透传（缺省用配置值）。
    """
    import urllib.parse
    import urllib.request
    base = str(siteconfig.get('music_api')).rstrip('/')
    params = {
        'server': request.GET.get('server') or str(siteconfig.get('music_server')),
        'type': request.GET.get('type') or str(siteconfig.get('music_type')),
        'id': request.GET.get('id') or str(siteconfig.get('music_id')),
    }
    url = f"{base}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    # 公共 Meting API 间歇性断连，重试 3 次提高成功率
    import time
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return HttpResponse(resp.read(), content_type='application/json')
        except Exception:
            time.sleep(1)
    return JsonResponse({"ret": -1, "msg": "音乐接口请求失败"}, status=502)

WIDGET_FILE = 'widget.json'
_widget_mutex = Semaphore(value=1)

def _widget_path(mail):
    prepa = os.path.abspath(__file__ + "/../../../")
    # 安全：mail 来源于请求参数，剥离路径成分确保只会落到 people/<mail>/widget.json
    mail = str(mail).replace('..', '').replace('/', '_').replace('\\', '_')
    return os.path.join(prepa, 'people', mail, WIDGET_FILE)

def _read_widget(mail):
    """读取某用户的看板郎形象配置；文件不存在/损坏返回 None。"""
    p = _widget_path(mail)
    if not os.path.exists(p):
        return None
    try:
        with open(p, 'r', encoding='utf-8') as obj:
            data = json.load(obj)
        return data if isinstance(data, dict) else None
    except Exception:
        return None

@csrf_exempt
def get_widget(request):
    """当前登录用户获取自己的看板郎形象配置。"""
    try:
        req = json.loads(request.body)
    except Exception:
        req = request.POST.dict()
    mail = str(req.get('mail', '') or '')
    password = str(req.get('password', '') or '')
    if not mail or not check_logined(mail, password):
        return JsonResponse({"ret": -100, "widget": None}, safe=False)
    widget = _read_widget(mail)
    return JsonResponse({"ret": 1, "widget": widget}, safe=False)

@csrf_exempt
def set_widget(request):
    """当前登录用户保存自己的看板郎形象配置（如 {"model": "miku"}）。"""
    try:
        req = json.loads(request.body)
    except Exception:
        req = request.POST.dict()
    mail = str(req.get('mail', '') or '')
    password = str(req.get('password', '') or '')
    widget = req.get('widget')
    if not mail or not check_logined(mail, password):
        return JsonResponse({"ret": -100}, safe=False)
    if not isinstance(widget, dict):
        return JsonResponse({"ret": -1, "msg": "widget 必须是对象"}, safe=False)
    # 只保留 model 字段（形象目录名），防止写入意外内容
    widget = {'model': str(widget.get('model', ''))}
    p = _widget_path(mail)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    _widget_mutex.acquire()
    try:
        with open(p, 'w', encoding='utf-8') as obj:
            json.dump(widget, obj, ensure_ascii=False)
    finally:
        _widget_mutex.release()
    return JsonResponse({"ret": 1}, safe=False)


def getThemeColor(request):
    global path
    get = json.loads(getusername(request).content)
    # body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    # req = json.loads(body)

    # 访客数按用户从磁盘读取，不再使用跨用户共享的全局变量
    number = read_traveler_count(get.get('urlmail') or '')
    if str(66 + 9) in str(number):
        kk = str(number)
        kk = kk.replace(str(66 +9), "76")
        number = int(kk)
    if str(30 + 27) in str(number):
        kk = str(number)
        kk = kk.replace(str(30 + 27), "58")
        number = int(kk)
    # kk = deepcopy(path).split(get['urlmail'])
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    # basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    if get['ret'] > 0:
        basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")

    file = os.path.join(basepath, 'themeColor.txt')
    if not os.path.exists(file):
        with open(file, 'w', encoding='utf-8') as obj:
            obj.write('1===0===rgb(136, 187, 250)' + '\n')
            return JsonResponse( { "checked1" : False,  "Themecolor":"rgb(136, 187, 250)", "TravelerStatistics":number} , safe = False)

    with open(file, 'r', encoding='utf-8') as obj:
        ij = obj.read().strip().split("===")
        if (len(ij)==1 and ij[0]=='') or len(ij)==0:
            with open(file, 'w', encoding='utf-8') as obj:
                obj.write('1===0===rgb(136, 187, 250)' + '\n')
                return JsonResponse( { "checked1" : False,  "Themecolor":"rgb(136, 187, 250)", "TravelerStatistics":number} , safe = False)
        if ij[0]=='1':
            ck = bool(int(ij[1]))
            if ck:
                rl = True
            else:
                rl = False
            return JsonResponse( { "checked1" : rl,  "Themecolor":ij[2], 'type':'1', "TravelerStatistics":number} , safe = False)
        else:
            return JsonResponse( { "color1" : ij[1],  "color2":ij[2], "color3":ij[3], 'type':'2', "TravelerStatistics":number} , safe = False)

kshoucangmutex = Semaphore(value=1)
def check_item_path(pathkkk):
    """点赞/评论/收藏的 path 安全校验：必须是站内文章 markdown 文件（.md），
    且位于 people/ 或 article/ 目录内，防止路径遍历在任意目录写 upvote_comment.json"""
    try:
        if not pathkkk.endswith('.md'):
            return False
        real = os.path.realpath(pathkkk)
        if not os.path.isfile(real):
            # 文件必须真实存在（已删除的文章一律拒绝，避免写 upvote_comment.json 时 FileNotFoundError 500）
            return False
        root = os.path.realpath(os.path.abspath(__file__ + "/../../../"))
        allowed = [os.path.join(root, 'people') + os.sep, os.path.join(root, 'article') + os.sep]
        return any(real.startswith(a) for a in allowed)
    except Exception:
        return False

def kshoucang(request):
    global path, kseamutex, kshoucangmutex
    body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    req = json.loads(body)

    # req = request.POST.dict()
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    # kkkpath = deepcopy(basepath)
    auth = check_identity(request, req)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    basepath = basepath.replace("/article/", f"/people/{get['mail']}/")

    # path 校验前置：先确认目标文章合法，再做任何写入，
    # 避免「自己的收藏清单已改、文章侧却校验失败返回 -100」的状态分裂
    pathkkk = req['path']
    if not check_item_path(pathkkk):
        return JsonResponse( { "ret" : -100 } , safe = False)

    filepath = os.path.join(basepath, 'kshoucang.json')
    # 用户从未发布过任何内容时 people/<mail>/ 目录可能不存在，直接写会 FileNotFoundError(500)
    os.makedirs(basepath, exist_ok=True)

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

    tails = pathkkk.split(os.sep)[-1]
    # setdefault 原子创建锁，避免并发下重复创建导致锁失效；
    # 读写合并到同一次加锁，避免丢更新；不再 pop 锁（pop 会让并发等待者拿到已移除的锁对象）
    sem = kseamutex.setdefault(tails, Semaphore(value=1))
    jsonpath = pathkkk.replace(tails, 'upvote_comment.json')

    sem.acquire()
    try:
        # 文件不存在（新内容首次点赞/评论/收藏）时使用默认结构，避免 500
        jsonfile = {"upvote":[], 'comment':[], 'kshoucang':[]}
        try:
            with open(jsonpath, 'r', encoding='utf-8') as obj:
                jsonfile = json.load(obj)
        except:
            pass
        if req['click']:
            jsonfile['kshoucang'].append(req['mail'])
            jsonfile['kshoucang'] = list(set(jsonfile['kshoucang']))
        else:
            try:
                jsonfile['kshoucang'].remove(req['mail'])
            except:
                pass
        with open(jsonpath, 'w', encoding='utf-8') as obj:
            json.dump(jsonfile, obj, indent=2, ensure_ascii=False)
    finally:
        sem.release()
    return JsonResponse( { "ret" : True } , safe = False)

# kcommentmutex = {}
def comment_add(request):
    global path, kseamutex #, kcommentmutex
    body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    req = json.loads(body)

    # req = request.POST.dict()
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    auth = check_identity(request, req)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    basepath = basepath.replace("/article/", f"/people/{get['mail']}/")

    # 评论容量限制：评论会被 index 每次全量加载，不设上限会被单条超大评论拖慢列表接口
    comment_text = str(req.get('comment', ''))
    if len(comment_text.strip()) == 0:
        return JsonResponse( { "ret" : -2, "msg" : "评论内容不能为空" } , safe = False)
    if len(comment_text) > 2000:
        return JsonResponse( { "ret" : -2, "msg" : "评论过长（最多2000字）" } , safe = False)

    pathkkk = req['path']
    if not check_item_path(pathkkk):
        return JsonResponse( { "ret" : -100 } , safe = False)
    tails = pathkkk.split(os.sep)[-1]
    # setdefault 原子创建锁；读写合并到同一次加锁；不再 pop 锁（原因同 kshoucang）
    sem = kseamutex.setdefault(tails, Semaphore(value=1))
    jsonpath = pathkkk.replace(tails, 'upvote_comment.json')

    postDate = datetime.fromtimestamp(time.time() +timezone).isoformat()[:19] #.replace(":", "_")
    postDate = postDate.replace("T", " ")
    sem.acquire()
    try:
        # 文件不存在（新内容首次点赞/评论/收藏）时使用默认结构，避免 500
        jsonfile = {"upvote":[], 'comment':[], 'kshoucang':[]}
        try:
            with open(jsonpath, 'r', encoding='utf-8') as obj:
                jsonfile = json.load(obj)
        except:
            pass
        jsonfile['comment'].append(["http://zoujiu.com.cn/"+req['mail'], comment_text, " - - - "+ postDate, req['mail'], get['nickname']])
        with open(jsonpath, 'w', encoding='utf-8') as obj:
            json.dump(jsonfile, obj, indent=2, ensure_ascii=False)
    finally:
        sem.release()
    return JsonResponse( { "ret" : True } , safe = False)

def upvote_change(request):
    global path, kseamutex
    body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    req = json.loads(body)

    # req = request.POST.dict()
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    auth = check_identity(request, req)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    basepath = basepath.replace("/article/", f"/people/{get['mail']}/")

    pathkkk = req['path']
    if not check_item_path(pathkkk):
        return JsonResponse( { "ret" : -100 } , safe = False)
    tails = pathkkk.split(os.sep)[-1]
    # setdefault 原子创建锁；读写合并到同一次加锁；不再 pop 锁（原因同 kshoucang）
    sem = kseamutex.setdefault(tails, Semaphore(value=1))
    jsonpath = pathkkk.replace(tails, 'upvote_comment.json')

    sem.acquire()
    try:
        # 文件不存在（新内容首次点赞/评论/收藏）时使用默认结构，避免 500
        jsonfile = {"upvote":[], 'comment':[], 'kshoucang':[]}
        try:
            with open(jsonpath, 'r', encoding='utf-8') as obj:
                jsonfile = json.load(obj)
        except:
            pass
        if req['click']:
            jsonfile['upvote'].append(req['mail'])
            jsonfile['upvote'] = list(set(jsonfile['upvote']))
        else:
            try:
                jsonfile['upvote'].remove(req['mail'])
            except:
                pass
        with open(jsonpath, 'w', encoding='utf-8') as obj:
            json.dump(jsonfile, obj, indent=2, ensure_ascii=False)
    finally:
        sem.release()
    return JsonResponse( { "ret" : True } , safe = False)

globaltext = \
r"""
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

# ==================== 草稿箱 ====================
# 草稿按用户隔离存放于 people/<mail>/draft/<id>.json（id 为保存时刻时间戳数字）。
# 鉴权与其他写接口一致：请求携带 mail + password，走 member.txt 校验（check_logined）。
# 防注入：mail 白名单字符校验、draft_id 仅允许纯数字，路径不拼任何未消毒输入。
_draft_mutex = Semaphore(value=1)
DRAFT_MAX_COUNT = 100  # 每用户草稿数上限，防止磁盘滥用
_DRAFT_ID_RE = regular.compile(r'^\d{14,17}$')
_DRAFT_MAIL_RE = regular.compile(r'^[A-Za-z0-9._@-]{1,64}$')

def _draft_dir(mail):
    """草稿目录 people/<mail>/draft/（mail 已通过白名单校验）。"""
    prepa = os.path.abspath(__file__ + "/../../../")
    d = os.path.join(prepa, 'people', mail, 'draft')
    os.makedirs(d, exist_ok=True)
    return d

def _draft_auth(req):
    """草稿接口统一鉴权；通过返回 (mail, '')，失败返回 ('', 原因)。"""
    try:
        mail = str(req.get('mail', ''))
        password = str(req.get('password', ''))
    except Exception:
        return '', '参数错误'
    if not mail or not password:
        return '', '未登录'
    if not _DRAFT_MAIL_RE.match(mail) or '..' in mail:
        return '', '非法账号'
    try:
        if not check_logined(mail, password):
            return '', '登录校验失败'
    except Exception:
        return '', '登录校验失败'
    return mail, ''

def save_draft(request):
    """保存/覆盖草稿。req: {mail, password, title, markdown, draft_id?}。
    draft_id 缺省或非法时新建（时间戳 id）；合法时覆盖原稿（再次编辑保存）。"""
    try:
        req = json.loads(request.body)
    except Exception:
        return JsonResponse({"ret": -100}, safe=False)
    mail, err = _draft_auth(req)
    if err:
        return JsonResponse({"ret": -100, "msg": err}, safe=False)
    title = str(req.get('title', '')).strip()[:200]
    markdown = str(req.get('markdown', ''))
    if len(title) == 0 and len(markdown.strip()) == 0:
        return JsonResponse({"ret": -2, "msg": "标题和内容不能同时为空"}, safe=False)
    if len(markdown) > 2 * 1024 * 1024:
        return JsonResponse({"ret": -2, "msg": "草稿内容过大"}, safe=False)
    draft_id = str(req.get('draft_id', ''))
    now = datetime.fromtimestamp(time.time() + timezone).isoformat()[:19].replace("T", " ")
    new_draft = not _DRAFT_ID_RE.match(draft_id)
    if new_draft:
        draft_id = datetime.fromtimestamp(time.time() + timezone).strftime('%Y%m%d%H%M%S%f')[:17]
    d = _draft_dir(mail)
    _draft_mutex.acquire()
    try:
        if new_draft and len([f for f in os.listdir(d) if f.endswith('.json')]) >= DRAFT_MAX_COUNT:
            return JsonResponse({"ret": -2, "msg": f"草稿已达上限 {DRAFT_MAX_COUNT} 篇，请先删除旧草稿"}, safe=False)
        data = {"id": draft_id, "title": title, "markdown": markdown, "save_time": now}
        # 原子写：先写临时文件再 os.replace，防止并发读到半截 json
        tmp = os.path.join(d, draft_id + '.json.tmp')
        with open(tmp, 'w', encoding='utf-8') as obj:
            json.dump(data, obj, ensure_ascii=False)
        os.replace(tmp, os.path.join(d, draft_id + '.json'))
    finally:
        _draft_mutex.release()
    return JsonResponse({"ret": 1, "draft_id": draft_id, "save_time": now}, safe=False)

def draft_list(request):
    """草稿列表。req: {mail, password}；返回按保存时间倒序的 [{id,title,save_time}]。"""
    try:
        req = json.loads(request.body)
    except Exception:
        return JsonResponse({"ret": -100}, safe=False)
    mail, err = _draft_auth(req)
    if err:
        return JsonResponse({"ret": -100, "msg": err}, safe=False)
    d = _draft_dir(mail)
    drafts = []
    _draft_mutex.acquire()
    try:
        for f in os.listdir(d):
            if not f.endswith('.json'):
                continue
            try:
                with open(os.path.join(d, f), 'r', encoding='utf-8') as obj:
                    data = json.load(obj)
                drafts.append({"id": str(data.get('id', f[:-5])),
                               "title": str(data.get('title', '')),
                               "save_time": str(data.get('save_time', ''))})
            except Exception:
                continue  # 单个损坏文件不影响整个列表
    finally:
        _draft_mutex.release()
    drafts.sort(key=lambda x: x['save_time'], reverse=True)
    return JsonResponse({"ret": 1, "drafts": drafts}, safe=False)

def draft_get(request):
    """读取单篇草稿。req: {mail, password, id}。"""
    try:
        req = json.loads(request.body)
    except Exception:
        return JsonResponse({"ret": -100}, safe=False)
    mail, err = _draft_auth(req)
    if err:
        return JsonResponse({"ret": -100, "msg": err}, safe=False)
    draft_id = str(req.get('id', ''))
    if not _DRAFT_ID_RE.match(draft_id):
        return JsonResponse({"ret": -100, "msg": "非法草稿编号"}, safe=False)
    p = os.path.join(_draft_dir(mail), draft_id + '.json')
    if not os.path.exists(p):
        return JsonResponse({"ret": -2, "msg": "草稿不存在或已删除"}, safe=False)
    try:
        with open(p, 'r', encoding='utf-8') as obj:
            data = json.load(obj)
    except Exception:
        return JsonResponse({"ret": -2, "msg": "草稿文件损坏"}, safe=False)
    return JsonResponse({"ret": 1, "id": data.get('id', draft_id), "title": data.get('title', ''),
                         "markdown": data.get('markdown', ''), "save_time": data.get('save_time', '')}, safe=False)

def draft_delete(request):
    """删除草稿。req: {mail, password, id}。"""
    try:
        req = json.loads(request.body)
    except Exception:
        return JsonResponse({"ret": -100}, safe=False)
    mail, err = _draft_auth(req)
    if err:
        return JsonResponse({"ret": -100, "msg": err}, safe=False)
    draft_id = str(req.get('id', ''))
    if not _DRAFT_ID_RE.match(draft_id):
        return JsonResponse({"ret": -100, "msg": "非法草稿编号"}, safe=False)
    p = os.path.join(_draft_dir(mail), draft_id + '.json')
    _draft_mutex.acquire()
    try:
        if os.path.exists(p):
            os.remove(p)
    finally:
        _draft_mutex.release()
    return JsonResponse({"ret": 1}, safe=False)

if __name__=="__main__":
    md2()
