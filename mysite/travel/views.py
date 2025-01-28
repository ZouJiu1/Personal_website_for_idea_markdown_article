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
from csdn.views import getusername, renzheng, notify_administer
import markdown2
import re as regular
from csdn.views import check_logined
from copy import deepcopy
import json
import shutil

sys.path.append(os.path.abspath(__file__ + "/../../"))
from manage import timezone

path = os.path.abspath(__file__ + "/../../../article/zhihu_spider_selenium/travel")
mainpath = os.path.abspath(__file__ + "/../../../dist/article")
if os.path.exists(mainpath):
    path = path.replace("/article/", '/dist/article/')
def rep(i):
    return i.replace(":", "_").replace("_问号_", "？").replace("_感叹号_", "！").\
              replace("小于", "<").replace("大于", ">").replace("_逗号_", "，").\
              replace("_空格_", " ").replace("_冒号_", "：").replace("_顿号_", "、")

allfile = None
pre_page_size = None

def index(request):
    global allfile, global_page_size, path
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
    
    basepath = deepcopy(path)
    get = json.loads(getusername(request).content)
    if get['ret'] > 0:
        basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")
    # if "mail" in req.keys():
    #     if check_logined(req['mail'], req['password']):
    #         basepath = basepath.replace("/article/", f"/people/{get['mail']}/")

    # reset = 1
    if reset==1:
        allfile = None
    collect = []
    search = search.split(" ")
    while '' in search:
        search.remove("")
    if allfile!=None:
        ret = allfile[(currentpage-1) * pagesize : currentpage * pagesize]
        return JsonResponse({"collect":ret, "length":len(allfile)}, safe = False)
    # keep = '素 家 黄色 7元 方便面 骚扰 耳塞 APP 广告 短信 色情 献 血 卡片 书'.split(" ")
    for i in os.listdir(basepath):
        nth = os.path.join(basepath, i)
        if not os.path.isdir(nth):
            continue
        date = i.replace("_", ":")
        markdownpth = ''
        markdown = ""
        imgimg = ''
        allpath = os.listdir(nth)
        allpath = sorted(allpath.__iter__(), key=lambda x:os.path.getmtime(os.path.join(nth, x)))
        for j in allpath:
            if '.txt' in j:
                markdownpth = os.path.join(nth, j)
                with open(markdownpth, 'r', encoding = 'utf-8') as obj:
                    markdown = obj.read().strip()
                    markdownCopy = deepcopy(markdown)
                    mn = markdown.split("\n")
                    markdown = mn[0] + '\n' + "<p><span style=\"color:#000000;font-size=390;\">姓名：</span>\n<span style=\"color:#00ffee\">" + mn[1] + \
                        '</span>      <span style=\"color:#000000;font-size=390;\">邮箱：</span>\n<span style=\"color:#00ffee\">' + mn[2] + \
                        '</span>      <span style=\"color:#000000;font-size=390;\">Contact：</span>\n<span style=\"color:#00ffee\">' + mn[3] + "</span></p>\n"
                markdown = markdown2.markdown(markdown)
#                 markdown = regular.sub(r'<p>', '<p style=\"margin: 1.4em 0; \
# display: block; \
# margin-block-start: 1em; \
# margin-block-end: 1em; \
# margin-inline-start: 0px; \
# margin-inline-end: 0px; \
# unicode-bidi: isolate; \
# word-break: break-word; \
# line-height: 1.6; \
# font-family: -apple-system,BlinkMacSystemFont,Helvetica Neue,PingFang SC,var(--zFontSansSerif),Microsoft YaHei,Source Han Sans SC,Noto Sans CJK SC,WenQuanYi Micro Hei,sans-serif; \
# font-size: 1.1em;\">', markdown)
            # if '.jpg' in j or '.png' in j or '.gif' in j or '.bmp' in j or 'jpeg' in j:
            #     imgimg += '<img class=\"think_image\"  @click=\"cardClick\" '+' src=\"article/zhihu_spider_selenium/think/' + i + '/' + j + '\" style=\"width = 100%;margin-left:3px;\"" >' + \
            #        f"<p hidden=\"true\" @click=\"cardClick\" class=\"hiddenp\">{nth}</p>" + \
            #             '</img>'
        # find = False
        # markdown = "<p @click=\"cardClick\">" + markdown + \
        #     f"<p hidden @click=\"cardClick\" class=\"hiddenp\">{nth}</p>" + \
        #     "</p>\n"
        if markdown[-1] == '\n':
            markdown = markdown[:-1]
        for j in search:
            if j in markdownCopy or j in i or j.replace(":", "_") in i:
                collect.append({"date":date, "markdown": markdown, 'path' : nth})
                # find = True
                break
        # if len(markdown) + len(imgimg) < 200:
        #     show = markdown + imgimg
        if len(search)==0:
            collect.append({"date":date, "markdown": markdown, 'path' : nth})
    collect = sorted(collect.__iter__(), key = lambda x:x['date'], reverse=True)
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
    
# def detail(request):
#     global allfile, global_page_size
#     # https://docs.djangoproject.com/en/5.1/ref/request-response/#top
#     re = request.GET.dict()
#     tailpath = re["path"]
#     markdown = ""
#     imgimg = ''
#     allpath = os.listdir(tailpath)
#     allpath = sorted(allpath.__iter__(), key=lambda x:os.path.getmtime(os.path.join(tailpath, x)))
#     dirname = tailpath.split(os.sep)[-1]
#     header = dirname.replace("_", ":")
#     for j in allpath:
#         if '.txt' in j:
#             markdownpth = os.path.join(tailpath, j)
#             with open(markdownpth, 'r', encoding = 'utf-8') as obj:
#                 markdown = obj.read().strip()
#         # if '.jpg' in j or '.png' in j or '.gif' in j or '.bmp' in j or 'jpeg' in j:
#         #     imgimg += '<img '+'src=\"article/zhihu_spider_selenium/think/' + dirname + '/' + j + '\" style=\"width = 30%;margin-top:6px;margin-bottom:6px;\"" />\n'
#     markdown = markdown2.markdown(markdown)
#     markdown = "<h1>" + header + "</h1>\n" + markdown + "\n" + imgimg
#     return JsonResponse({"markdown" : markdown}, safe = False)

# def delete(request):
#     global allfile
#     re = request.GET.dict()
#     currentpage = re["path"]
#     import shutil
#     try:
#         allfile = None
#         shutil.rmtree(currentpage)
#         return JsonResponse( { "done" : currentpage } , safe = False)
#     except:
#         return JsonResponse( { "done" : currentpage } , safe = False)

def post_travel(request):
    global allfile, path
    allfile = None
    # req = request.GET.dict()
    req = json.loads(request.body)
    postdate = str(req["postdate"])

    basepath = deepcopy(path)

    get = json.loads(getusername(request).content)
    if get['ret'] > 0:
        basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")
    # if "mail" in req.keys():
    #     if check_logined(req['mail'], req['password']):
    #         basepath = basepath.replace("/article/", f"/people/{get['mail']}/")

    postdate = postdate[:-3] + "." + postdate[-3:]
    postdate = datetime.fromtimestamp(float(postdate) + timezone).isoformat()[:19]
    postdate = postdate.replace("T", " ").replace(":", "_")

    # imgpostdate = re["imgpostdate"]

    # imgpostdate = imgpostdate[:-3] + "." + imgpostdate[-3:]
    # imgpostdate = datetime.fromtimestamp(float(imgpostdate)).isoformat()[:19]
    # imgpostdate = imgpostdate.replace("T", " ").replace(":", "_")
    text_content = req["text_content"]
    
    # if len(imgpostdate) > 0:
    #     upPath = os.path.join(path, imgpostdate)
    # else:
    travelname = req["travelname"]
    travelemail = req["travelemail"]
    travelcontact = req["travelcontact"]
    
    # passd = True
    
    if len(travelemail) < 6 or "@" not in travelemail or len(travelcontact) < 6 or \
        len(travelname) == 0 or len(text_content) < 10:
        return JsonResponse( { "post" : False} , safe = False)
    
    upPath = os.path.join(basepath, postdate)
    
    if not os.path.exists(upPath):
        os.mkdir(upPath)
    
    with open(os.path.join(upPath, "content.txt"), 'w', encoding='utf-8') as obj:
        obj.write(text_content + "\n")
        obj.write(travelname + "\n" + travelemail + "\n" + travelcontact + '\n')
        # obj.write("<p><span style=\"color:#000000;font-size=390;\">姓名：</span>\n<span style=\"color:#00ffee\">" + travelname + \
        #     '</span>      <span style=\"color:#000000;font-size=390;\">邮箱：</span>\n<span style=\"color:#00ffee\">' + travelemail + \
        #     '</span>      <span style=\"color:#000000;font-size=390;\">Contact：</span>\n<span style=\"color:#00ffee\">' + travelcontact + "</span></p>\n")
    
    # if len(imgpostdate) > 0:
    #     os.rename(upPath, os.path.join(path, postdate))
    return JsonResponse( { "post" : True} , safe = False)

def delete(request):
    global allfile
    # req = request.POST.dict()
    req = json.loads(request.body)
    currentpage = req["path"]

    rz = renzheng(request)
    rzret = json.loads(rz.content)
    passed = False
    get = {'quanxian': -1}
    if "mail" in req.keys():
        get = json.loads(getusername(request).content)
        if get['quanxian'] < 1000000 and not rzret['ret'] and 'password' in req.keys() and check_logined(req['mail'], req['password']):
            # basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
            passed = True
            if f"/people/{get['mail']}/" not in currentpage:
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
            notify_administer(currentpage, get['mail'], get['urlmail'], True)
        elif get['quanxian'] == 1000000 and get['mail']==get['urlmail']:
            notify_administer(currentpage, get['mail'], get['urlmail'], False)
        shutil.rmtree(currentpage)
        return JsonResponse( { "ret" : True } , safe = False)
    except:
        return JsonResponse( { "ret" : 0 } , safe = False)

# @csrf_exempt
# def uploadImg(request):
#     global allfile
#     allfile = None
#     # body = request.body
#     # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
#     re = request.POST.dict()
#     postdate = re["postdate"]
#     # https://docs.djangoproject.com/zh-hans/5.1/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile
#     uploadImageName = request.FILES['file'].name
#     # https://docs.djangoproject.com/zh-hans/5.1/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile
#     # uploadType = request.FILES['file'].content_type
#     # assert 1==0, (time.time(), postdate)
#     postdate = postdate[:-3] + "." + postdate[-3:]
#     postDa = datetime.fromtimestamp(float(postdate)).isoformat()[:19]
#     postDate = postDa.replace("T", " ").replace(":", "_")
#     savepath = os.path.join(path, postDate)

#     if not os.path.exists(savepath):
#         os.mkdir(savepath)

#     for i in os.listdir(savepath):
#         if uploadImageName==i:
#             uploadImageName = uploadImageName.replace(".", "_%d."%(np.random.randint(999999999)))
#             break

#     dirlast = savepath.split(os.sep)[-1]
    
#     imgpath = os.path.join(savepath, uploadImageName)
#     handle_uploaded_file(request.FILES['file'], imgpath)
    
#     return JsonResponse( { "dirname" : dirlast, "path":savepath} , safe = False)
