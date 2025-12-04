from django.http import HttpResponse
# from rest_framework.response import Response
# from rest_framework import status
from django.http import JsonResponse
import os
from datetime import datetime
import time
from django.views.decorators.csrf import csrf_exempt
import numpy as np
addpath = os.path.abspath(__file__ + "/../../")
import sys
sys.path.append(addpath)
from csdn.views import handle_uploaded_file, replacewithjpg
from csdn.views import check_logined, getusername, renzheng, notify_administer
import markdown2
import re as regular
from copy import deepcopy
import json
from threading import Semaphore
import shutil

sys.path.append(os.path.abspath(__file__ + "/../../"))
from manage import timezone

path = os.path.abspath(__file__ + "/../../../article/zhihu_spider_selenium/think")
mainpath = os.path.abspath(__file__ + "/../../../dist/article")
if os.path.exists(mainpath):
    path = path.replace("/article/", '/dist/article/')

def rep(i):
    return i.replace(":", "_").replace("_问号_", "？").replace("_感叹号_", "！").\
              replace("小于", "<").replace("大于", ">").replace("_逗号_", "，").\
              replace("_空格_", " ").replace("_冒号_", "：").replace("_顿号_", "、")

allfile = None
pre_page_size = None

allmutex = {}
def index(request):
    global allfile, allmutex, path, kseamutexpiaduan
    # https://docs.djangoproject.com/en/5.1/ref/request-response/#top
    # req = request.GET.dict()
    req = json.loads(request.body)
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

    # reset = 1
    if reset==1:
        allfile = None
    basepath = deepcopy(path)

    get = json.loads(getusername(request).content)
    if get['ret'] > 0:
        basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")
    # if "mail" in req.keys():
        # if check_logined(req['mail'], req['password']):
        # basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
    collect = []
    search = search.split(" ")
    while '' in search:
        search.remove("")
    if allfile!=None:
        ret = allfile[(currentpage-1) * pagesize : currentpage * pagesize]
        return JsonResponse({"collect":ret, "length":len(allfile)}, safe = False)
    keep = '素 家 黄色 7元 方便面 骚扰 耳塞 APP 广告 短信 色情 献 血 卡片 书'.split(" ")
    TOPTOP = []
    for i in os.listdir(basepath):
        nth = os.path.join(basepath, i)
        if not os.path.isdir(nth):
            continue
        date = i.replace("_", ":")[:-3]
        markdownpth = ''
        markdown = ""
        imgimg = ''
        imgimgall = []
        allpath = os.listdir(nth)
        allpath = sorted(allpath.__iter__(), key=lambda x:os.path.getmtime(os.path.join(nth, x)))


        upvotecomment = os.path.join(nth, 'upvote_comment.json')
        if not os.path.exists(upvotecomment):
            os.system(f"touch \"{upvotecomment}\"")
        upvote = []
        comment = []
        kshoucang = []
        click = False
        maillogin = '#'
        if 'mail' in req.keys():
            maillogin = req['mail']
        clickshoucang = False
        tails = i
        if tails not in kseamutexpiaduan.keys():
            kseamutexpiaduan[tails] = Semaphore(value=1)
        kseamutexpiaduan[tails].acquire()
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
        kseamutexpiaduan[tails].release()
        kseamutexpiaduan.pop(tails)

        modifytime = 0
        createtime = 0
        for j in allpath:
            if '.txt' in j:
                markdownpth = os.path.join(nth, j)
                # at = os.path.getatime(markdownpth)
                # ct = os.path.getctime(markdownpth)
                modifytime = os.path.getmtime(markdownpth) + timezone
                createtime = datetime.timestamp(datetime.fromisoformat(i.replace("_", ":")))
                with open(markdownpth, 'r', encoding = 'utf-8') as obj:
                    markdown = obj.read().strip()
                markdown = markdown2.markdown(markdown)
                markdown = regular.sub(r'<p>', '<p style=\"margin: 1.4em 0; \
display: block; \
margin-block-start: 1em; \
margin-block-end: 1em; \
margin-inline-start: 0px; \
margin-inline-end: 0px; \
unicode-bidi: isolate; \
word-break: break-word; \
line-height: 1.6; \
font-family: -apple-system,BlinkMacSystemFont,Helvetica Neue,PingFang SC,var(--zFontSansSerif),Microsoft YaHei,Source Han Sans SC,Noto Sans CJK SC,WenQuanYi Micro Hei,sans-serif; \
font-size: 1.1em;\">', markdown)
            if '.jpg' in j.lower() or '.png' in j.lower() or '.gif' in j.lower() or \
                '.bmp' in j.lower() or 'jpeg' in j.lower():
                if 'people' in nth:
                    kk = '/people' + nth.split("people")[-1] + os.sep + j
                else:
                    kk = '/article' + nth.split("article")[-1] + os.sep + j
                imgimg += '<img class=\"el-image__inner el-image__preview think_image\" style=\"object-fit: scale-down;\" @click=\"cardClick\" ' + f' src=\"{kk}\" loading=\"lazy\">' + \
                    f"<span hidden><p hidden @click=\"cardClick\" class=\"hiddenp\">{nth}</p></span>" + \
                            '</img>'
        markdown = "<p @click=\"cardClick\">" + markdown + \
            f"<span hidden><p hidden @click=\"cardClick\" class=\"hiddenp\">{nth}</p>" + \
            "</p></span>"
        if abs(modifytime - createtime) > 3600:
            postDate = datetime.fromtimestamp(modifytime).isoformat()[:19][:-3].replace("T", " ")
            markdown = markdown + f"<span @click=\"cardClick\">------修改时间日期：{postDate}</span>" +\
            f"<span hidden><p hidden @click=\"cardClick\" class=\"hiddenp\">{nth}</p>" + \
            "</p></span>"
        # if len(markdown) + len(imgimg) < 200:
        #     show = markdown + imgimg
        inlist = False
        if len(search)==0:
            inlist = True
            collect.append({"date":date, "markdown": (markdown + "<br>" + imgimg), "imgimg" : imgimg, 'path' : nth, \
                            "upvote":upvote, 'comment':comment, 'click':click, \
                            'clickshoucang':clickshoucang, 'kshoucang':kshoucang, 'isTop':False})
        else:
            for j in search:
                if j in markdown or j in i or j.replace(":", "_") in i:
                    collect.append({"date":date, "markdown": (markdown + "<br>" + imgimg), "imgimg" : imgimg, 'path' : nth, \
                                    "upvote":upvote, 'comment':comment, 'click':click, \
                                    'clickshoucang':clickshoucang, 'kshoucang':kshoucang, 'isTop':False})
                    inlist = True
                    break
        if inlist == True:
            topPath = os.path.join(nth, "TOP.text")
            if os.path.exists(topPath):
                topTime = os.path.getmtime(topPath)
                collect.pop()
                inserted = False
                for itop in range(len(TOPTOP)):
                    if TOPTOP[itop]['topTime'] < topTime:
                        TOPTOP.insert(itop, {"date":date, "markdown": (markdown + "<br>" + imgimg), "imgimg" : imgimg, 'path' : nth, \
                                    "upvote":upvote, 'comment':comment, 'click':click, \
                                    'clickshoucang':clickshoucang, 'kshoucang':kshoucang,
                                    'isTop':True, "topTime":os.path.getmtime(topPath)})
                        inserted = True
                        break
                if inserted==False:
                    TOPTOP.append({"date":date, "markdown": (markdown + "<br>" + imgimg), "imgimg" : imgimg, 'path' : nth, \
                                    "upvote":upvote, 'comment':comment, 'click':click, \
                                    'clickshoucang':clickshoucang, 'kshoucang':kshoucang,
                                    'isTop':True, "topTime":os.path.getmtime(topPath)})
    collect = sorted(collect.__iter__(), key = lambda x:x['date'], reverse=True)
    collect = TOPTOP + collect
    if allfile==None:
        allfile = collect
    ret = collect[(currentpage-1) * pagesize : currentpage * pagesize]
    return JsonResponse({"collect":ret, "length":len(collect)}, safe = False)

    # return Response({
    #         "success": True,
    #         "msg": 'msg',
    #         "results": {
    #             "TOKEN":'token',
    #             "username":'username',
    #         }
    #     }, status=status.HTTP_200_OK)
    # response = HttpResponse(
    #     "Hello, world. You're at the polls index.",
    #     headers={
    #         "Access-Control-Allow-Origin": "*",
    #     },)
    # return response
    # return HttpResponse("Hello, world. You're at the polls index.")
    # return Response("Hello, world. You're at the polls index.", status=status.HTTP_200_OK)
    
def detail(request):
    global allfile, kseamutexpiaduan
    # https://docs.djangoproject.com/en/5.1/ref/request-response/#top
    # req = request.GET.dict()
    # req = request.POST.dict()
    req = json.loads(request.body)
    tailpath = req["path"]
    pathkkk = req["path"]

    # if "mail" in req.keys():
        # if check_logined(req['mail'], req['password']):
        # basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
    markdown = ""
    imgimg = ''
    allpath = os.listdir(tailpath)
    lasttail = tailpath.split(os.sep)[-1].replace("_", ":")
    allpath = sorted(allpath.__iter__(), key=lambda x:os.path.getmtime(os.path.join(tailpath, x)))
    dirname = tailpath.split(os.sep)[-1]
    header = dirname.replace("_", ":")[:-3]
    txtfile = ""
    original = ""
    modifytime = 0
    createtime = 0
    for j in allpath:
        if '.txt' in j:
            txtfile = j
            markdownpth = os.path.join(tailpath, j)
            with open(markdownpth, 'r', encoding = 'utf-8') as obj:
                markdown = obj.read().strip()
                original = deepcopy(markdown)
            modifytime = os.path.getmtime(markdownpth) + timezone

            createtime = datetime.timestamp(datetime.fromisoformat(lasttail))
        if '.jpg' in j.lower() or '.png' in j.lower() or '.gif' in j.lower() or \
                '.bmp' in j.lower() or 'jpeg' in j.lower():
            if 'people' in tailpath:
                kk = '/people' + tailpath.split("people")[-1] + os.sep + j
            else:
                kk = '/article' + tailpath.split("article")[-1] + os.sep + j
            imgimg += '<img ' + f'src=\"{kk}\" style=\"width = 30%;margin-top:6px;margin-bottom:6px;\"" />\n'
    markdown = markdown2.markdown(markdown)
    if abs(modifytime - createtime) > 3600:
        postDate = datetime.fromtimestamp(modifytime).isoformat()[:19][:-3].replace("T", " ")
        markdown = markdown + f"<span @click=\"cardClick\">------修改时间日期：{postDate}</span>"
    markdown = "<h3>" + markdown + "</h3>\n<p>" + header + "</p><br>" + imgimg

    upvote = []
    comment = []
    kshoucang = []
    click = False
    clickshoucang = False
    maillogin = '#'
    if 'mail' in req.keys():
        maillogin = req['mail']
    # with open(file, 'w', encoding='utf-8') as obj:upvote_comment
    #     json.dump(Setting_Formel, obj, indent=2, ensure_ascii=False)
    tails = txtfile
    if tails not in kseamutexpiaduan.keys():
        kseamutexpiaduan[tails] = Semaphore(value=1)

    upvotecomment = os.path.join(tailpath, 'upvote_comment.json')
    if not os.path.exists(upvotecomment):
        os.system(f"touch \"{upvotecomment}\"")

    kseamutexpiaduan[tails].acquire()
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
            for i in upvote:
                if len(maillogin)!=1 and maillogin == i:
                    click = True
                    break
            for i in kshoucang:
                if len(maillogin)!=1 and maillogin == i:
                    clickshoucang = True
                    break
    kseamutexpiaduan[tails].release()
    kseamutexpiaduan.pop(tails)

    topPath = os.path.join(tailpath, "TOP.text")
    if os.path.exists(topPath):
        return JsonResponse({"markdown" : markdown, 'path': pathkkk, "upvote":upvote, 'comment':comment, 'click':click, \
                            'clickshoucang':clickshoucang, 'kshoucang':kshoucang, 'title':dirname, "original":original, 'isTop':True}, \
                                safe = False)
    else:
        return JsonResponse({"markdown" : markdown, 'path': pathkkk, "upvote":upvote, 'comment':comment, 'click':click, \
                            'clickshoucang':clickshoucang, 'kshoucang':kshoucang, 'title':dirname, "original":original, 'isTop':False}, \
                                safe = False)

def modify(request):
    global allfile, kseamutexpiaduan, path, allmutex
    allfile = None
    # req = request.GET.dict()
    req = json.loads(request.body)
    basepath = deepcopy(path)

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

    # https://docs.djangoproject.com/en/5.1/ref/request-response/#top
    # req = request.GET.dict()
    # req = request.POST.dict()
    tailpath = req["path"]
    editcontent = req['editcontent']

    allpath = os.listdir(tailpath)
    allpath = sorted(allpath.__iter__(), key=lambda x:os.path.getmtime(os.path.join(tailpath, x)))
    # original = original.split("\n")
    # keep = []
    # j = -1
    # for i in range(len(original) - 1, -1, -1):
    #     if '---------------修改时间日期：' in original[i]:
    #         j = i
    #         break
    # if j < 0 and len(keep)==0:
    #     keep = original
    # else:
    #     keep = "\n".join(keep)
    # postDate = datetime.fromtimestamp(time.time() +timezone).isoformat()[:19]
    # writeable = editcontent + f"：{postDate}" + "\n---------------第一版：" + keep
    modified = False
    for j in allpath:
        if '.txt' in j:
            markdownpth = os.path.join(tailpath, j)
            if tailpath not in allmutex.keys():
                allmutex[tailpath] = Semaphore(value=1)
            allmutex[tailpath].acquire()
            with open(markdownpth, 'w', encoding = 'utf-8') as obj:
                obj.write(editcontent)
            allmutex[tailpath].release()
            modified = True
            break
    if not modified:
        markdownpth = os.path.join(tailpath, "content.txt")
        if tailpath not in allmutex.keys():
                allmutex[tailpath] = Semaphore(value=1)
        allmutex[tailpath].acquire()
        with open(markdownpth, 'w', encoding = 'utf-8') as obj:
            obj.write(editcontent)
        allmutex[tailpath].release()
    return JsonResponse({"ret" : True}, safe = False)

def delete(request):
    global allfile, allmutex
    # req = request.GET.dict()
    req = json.loads(request.body)
    currentpage = req["path"]
    #print(currentpage)
    rz = renzheng(request)
    rzret = json.loads(rz.content)
    passed = False
    get = {'quanxian': -1}
    if "mail" in req.keys():
        get = json.loads(getusername(request).content)
        if get['quanxian'] < 1000000 and not rzret['ret'] and 'password' in req.keys() and check_logined(req['mail'], req['password']):
            # basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
            passed = True
            if f"/people/{get['mail']}/" not in currentpage or '20'!=currentpage.split(os.sep)[-1][:2]:
                return JsonResponse( { "ret" : -100} , safe = False)
        elif get['quanxian'] < 1000000 and get['ret']==2:
            return JsonResponse( { "ret" : -100} , safe = False)
        elif  get['quanxian'] == 1000000:
            passed = True

    if not passed and not rzret['ret']:
        return JsonResponse( { "ret" : -100} , safe = False)
    # elif not passed and rzret['ret']:
    #     get = json.loads(getusername(request).content)
        # if get['ret'] > 0:
        #     basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")

    try:
        allfile = None
        if get['quanxian'] == 1000000 and get['mail']!=get['urlmail']:
            notify_administer(currentpage, get['truemail'], get['mail'], get['urlmail'], True)
        elif get['quanxian'] == 1000000 and get['mail']==get['urlmail']:
            notify_administer(currentpage, get['truemail'], get['mail'], get['urlmail'], False)
        if currentpage not in allmutex.keys():
                allmutex[currentpage] = Semaphore(value=1)
        allmutex[currentpage].acquire()
        #print(currentpage)
        shutil.rmtree(str(currentpage))
        allmutex[currentpage].release()
        return JsonResponse( { "done" : currentpage, 'ret': True} , safe = False)
    except Exception as e:
        print(2222222, e)
        return JsonResponse( { "done" : currentpage, 'ret':0 } , safe = False)

def post_think(request):
    global allfile, path
    allfile = None
    # req = request.GET.dict()
    req = json.loads(request.body)
    basepath = deepcopy(path)
    postdate = str(req["postdate"])

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

    postdate = postdate[:-3] + "." + postdate[-3:]
    postdate = datetime.fromtimestamp(float(postdate) + timezone).isoformat()[:19]
    postdate = postdate.replace("T", " ").replace(":", "_")
    
    imgpostdate = str(req["imgpostdate"])
    if len(imgpostdate) > 6:
        imgpostdate = imgpostdate[:-3] + "." + imgpostdate[-3:]
        imgpostdate = datetime.fromtimestamp(float(imgpostdate) + timezone).isoformat()[:19]
        imgpostdate = imgpostdate.replace("T", " ").replace(":", "_")
    text_content = req["text_content"]
    
    if len(imgpostdate) > 6:
        upPath = os.path.join(basepath, imgpostdate)
    else:
        upPath = os.path.join(basepath, postdate)
   
    if not os.path.exists(upPath):
        os.mkdir(upPath)
    
    with open(os.path.join(upPath, "content.txt"), 'w', encoding='utf-8') as obj:
        obj.write(text_content)
    
    if len(imgpostdate) > 0:
        os.rename(upPath, os.path.join(basepath, postdate))
    return JsonResponse( { "ret" : True} , safe = False)

@csrf_exempt
def uploadImg(request):
    global allfile, path
    allfile = None
    # body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    req = request.POST.dict()
    postdate = req["postdate"]
    basepath = deepcopy(path)

    # if "mail" in req.keys():
    #     # if check_logined(req['mail'], req['password']):
    #     basepath = basepath.replace("/article/", f"/people/{get['mail']}/")

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

    # https://docs.djangoproject.com/zh-hans/5.1/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile
    uploadImageName = request.FILES['file'].name
    # https://docs.djangoproject.com/zh-hans/5.1/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile
    # uploadType = request.FILES['file'].content_type
    # assert 1==0, (time.time(), postdate)
    savepath = ""
    if 'detail' in req.keys():
        savepath = req['path']
    else:
        postdate = postdate[:-3] + "." + postdate[-3:]
        postDa = datetime.fromtimestamp(float(postdate) + timezone).isoformat()[:19]
        postDate = postDa.replace("T", " ").replace(":", "_")
        savepath = os.path.join(basepath, postDate)
        if not os.path.exists(savepath):
            os.mkdir(savepath)

    for i in os.listdir(savepath):
        if uploadImageName==i:
            uploadImageName = uploadImageName.replace(".", "_%d."%(np.random.randint(999999999)))
            break

    dirlast = savepath.split(os.sep)[-1]
    
    imgpath = os.path.join(savepath, uploadImageName)

    handle_uploaded_file(request.FILES['file'], imgpath)
    uploadImageName, nowpath = replacewithjpg(imgpath)
    
    return JsonResponse( { "dirname" : dirlast, "path":savepath, 'ret':True} , safe = False)

def placeTop(request):
    global allfile
    allfile = None
    # req = request.GET.dict()
    req = json.loads(request.body)
    placepath = req["path"]

    rz = renzheng(request)
    rzret = json.loads(rz.content)
    passed = False
    if "mail" in req.keys():
        get = json.loads(getusername(request).content)
        if not rzret['ret'] and 'password' in req.keys() and check_logined(req['mail'], req['password']):
            # placepath = placepath.replace("/article/", f"/people/{get['mail']}/")
            passed = True
            if f"/people/{get['mail']}/" not in placepath or '20'!=placepath.split(os.sep)[-1][:2]:
                return JsonResponse( { "ret" : -100} , safe = False)
        elif get['ret']==2:
            return JsonResponse( { "ret" : -100} , safe = False)
    if not passed and not rzret['ret']:
        return JsonResponse( { "ret" : -100} , safe = False)
    # elif not passed and rzret['ret']:
        # get = json.loads(getusername(request).content)
        # if get['ret'] > 0:
            # placepath = placepath.replace("/article/", f"/people/{get['urlmail']}/")

    # dirname = placepath.split(os.sep)[-1]
    
    pathkkkTmp = os.path.join(placepath, "TOP.text")
    with open(pathkkkTmp, 'w', encoding="utf-8") as obj:
        obj.write("")

    # postDa = datetime.fromtimestamp(time.time() + timezone).isoformat()[:19]
    # postDate = postDa.replace("T", " ").replace(":", "_")
    
    # os.rename(placepath, placepath.replace(dirname, postDate))
    # return JsonResponse( { "path" : placepath.replace(dirname, postDate) , 'ret':True} , safe = False)
    return JsonResponse( { "path" : "" , 'ret':True} , safe = False)


def cancelPlaceTop(request):
    global allfile
    allfile = None
    # req = request.GET.dict()
    req = json.loads(request.body)
    placepath = req["path"]

    rz = renzheng(request)
    rzret = json.loads(rz.content)
    passed = False
    if "mail" in req.keys():
        get = json.loads(getusername(request).content)
        if not rzret['ret'] and 'password' in req.keys() and check_logined(req['mail'], req['password']):
            # placepath = placepath.replace("/article/", f"/people/{get['mail']}/")
            passed = True
            if f"/people/{get['mail']}/" not in placepath or '20'!=placepath.split(os.sep)[-1][:2]:
                return JsonResponse( { "ret" : -100} , safe = False)
        elif get['ret']==2:
            return JsonResponse( { "ret" : -100} , safe = False)
    if not passed and not rzret['ret']:
        return JsonResponse( { "ret" : -100} , safe = False)

    pathkkkTmp = os.path.join(placepath, "TOP.text")
    if os.path.exists(pathkkkTmp):
        os.remove(pathkkkTmp)
    return JsonResponse( { "path" : "" , 'ret':True} , safe = False)

kseamutexpiaduan = {}
kshoucangmutexpianduan = Semaphore(value=1)
def kshoucang(request):
    global path, kseamutexpiaduan, kshoucangmutexpianduan
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
    
    filepath = os.path.join(basepath, 'kshoucangpianduan.json')

    if not os.path.exists(filepath):
        kshoucangmutexpianduan.acquire()
        with open(filepath, 'w', encoding='utf-8') as obj:
            json.dump([], obj, indent=2, ensure_ascii=False)
        kshoucangmutexpianduan.release()
        
    kshoucangmutexpianduan.acquire()
    with open(filepath, 'r', encoding='utf-8') as obj:
        try:
            kshoucangJson = json.load(obj)
        except:
            kshoucangJson = []
        if req['click']:
            kshoucangJson.append(req['title'].replace(" ", '-') + "===" + f"{req['mail']}#/think/detail/{req['mail']}?plan="+ req['path'])
        else:
            try:
                kshoucangJson.remove(req['title'].replace(" ", '-') + "===" + f"{req['mail']}#/think/detail/{req['mail']}?plan=" + req['path'])
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
    kshoucangmutexpianduan.release()

    kshoucangmutexpianduan.acquire()
    with open(filepath, 'w', encoding='utf-8') as obj:
        json.dump(kshoucangJson, obj, indent=2, ensure_ascii=False)
    kshoucangmutexpianduan.release()

    pathkkk = req['path']
    tails = pathkkk.split(os.sep)[-1]
    if tails not in kseamutexpiaduan.keys():
        kseamutexpiaduan[tails] = Semaphore(value=1)
    # kk = Semaphore(value=1)
    jsonpath = os.path.join(pathkkk, 'upvote_comment.json')
    
        # with open(file, 'w', encoding='utf-8') as obj:
        #     json.dump(Setting_Formel, obj, indent=2, ensure_ascii=False)
    kseamutexpiaduan[tails].acquire()
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
    kseamutexpiaduan[tails].release()

    kseamutexpiaduan[tails].acquire()
    with open(jsonpath, 'w', encoding='utf-8') as obj:
        json.dump(jsonfile, obj, indent=2, ensure_ascii=False)
    kseamutexpiaduan[tails].release()
    kseamutexpiaduan.pop(tails)
    return JsonResponse( { "ret" : True } , safe = False)

# kcommentmutex = {}
def comment_add(request):
    global path, kseamutexpiaduan #, kcommentmutex
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
    if tails not in kseamutexpiaduan.keys():
        kseamutexpiaduan[tails] = Semaphore(value=1)
    # kk = Semaphore(value=1)
    jsonpath = os.path.join(pathkkk, 'upvote_comment.json')
    
        # with open(file, 'w', encoding='utf-8') as obj:
        #     json.dump(Setting_Formel, obj, indent=2, ensure_ascii=False)
    postDate = datetime.fromtimestamp(time.time() +timezone).isoformat()[:19] #.replace(":", "_")
    postDate = postDate.replace("T", " ")
    kseamutexpiaduan[tails].acquire()
    with open(jsonpath, 'r', encoding='utf-8') as obj:
        try:
            jsonfile = json.load(obj)
        except:
            jsonfile = {"upvote":[], 'comment':[], 'kshoucang':[]}
        jsonfile['comment'].append(["http://zoujiu.com.cn/"+req['mail'], req['comment'], " - - - " + postDate, req['mail'], get['nickname']])
    kseamutexpiaduan[tails].release()

    kseamutexpiaduan[tails].acquire()
    with open(jsonpath, 'w', encoding='utf-8') as obj:
        json.dump(jsonfile, obj, indent=2, ensure_ascii=False)
    kseamutexpiaduan[tails].release()
    kseamutexpiaduan.pop(tails)
    return JsonResponse( { "ret" : True } , safe = False)

def upvote_change(request):
    global path, kseamutexpiaduan
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
    if tails not in kseamutexpiaduan.keys():
        kseamutexpiaduan[tails] = Semaphore(value=1)
    # kk = Semaphore(value=1)
    jsonpath = os.path.join(pathkkk, 'upvote_comment.json')
    
        # with open(file, 'w', encoding='utf-8') as obj:
        #     json.dump(Setting_Formel, obj, indent=2, ensure_ascii=False)
    kseamutexpiaduan[tails].acquire()
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
    kseamutexpiaduan[tails].release()

    kseamutexpiaduan[tails].acquire()
    with open(jsonpath, 'w', encoding='utf-8') as obj:
        json.dump(jsonfile, obj, indent=2, ensure_ascii=False)
    kseamutexpiaduan[tails].release()
    kseamutexpiaduan.pop(tails)
    return JsonResponse( { "ret" : True } , safe = False)
