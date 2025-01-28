from django.http import HttpResponse
# from rest_framework.response import Response
# from rest_framework import status
from django.http import JsonResponse
import os
from datetime import datetime
import time
from django.views.decorators.csrf import csrf_exempt

path = os.path.abspath(__file__+"/../../../article/video")
mainpath = os.path.abspath(__file__ + "/../../../dist/article")
if os.path.exists(mainpath):
    path = path.replace("/article/", '/dist/article/')
allfile = None
pre_page_size = None
addpath = os.path.abspath(__file__ + "/../../")
import sys
sys.path.append(addpath)
from csdn.views import getusername
from copy import deepcopy
import json

def index(request):
    global allfile, global_page_size, path
    # https://docs.djangoproject.com/en/5.1/ref/request-response/#top
    hlspath = os.path.abspath(__file__+"/../../../hls")
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
    #     # if check_logined(req['mail'], req['password']):
    #     basepath = basepath.replace("/article/", f"/people/{get['mail']}/")

    collect = []
    search = search.split(" ")
    while '' in search:
        search.remove("")
    # if allfile!=None:
    #     ret = allfile[(currentpage-1) * pagesize : currentpage * pagesize]
    #     return JsonResponse({"collect":ret, "length":len(allfile)}, safe = False)
    for i in os.listdir(basepath):
        if '.txt' in i:
            continue
        if '.DS_Store' in i:
            continue
        if 'people' in basepath:
            kk = '/people' + basepath.split("people")[-1]
        else:
            kk = '/article' + basepath.split("article")[-1]
        filevideo = kk + os.sep + i
        if os.path.isdir(os.path.join(basepath, i)):
            nth = os.path.join(basepath, i)
            for j in os.listdir(nth):
                if '.txt 'in j:
                    continue
                filevideo = kk + os.sep + i + os.sep + j # os.path.join(r"/article/video/", i, j)
                head = j.split(".")[0]
                textfile = head + '.txt'
                txtpath = os.path.join(nth, textfile)
                ideopath = os.path.join(nth, j)
                break
        else:
            head = i.split(".")[0]
            textfile = head + '.txt'
            txtpath = os.path.join(basepath, textfile)
            ideopath = os.path.join(basepath, i)
        date = 'no date'
        description = ""
        title = ""
        ti = "no title"
        with open(txtpath, 'r', encoding='utf-8') as obj:
            num = 0
            for ij in obj.readlines():
                if num==0:
                    title = ij.strip()
                else:
                    date = ij.strip()
                    break
                num += 1
        # find = False
        date = date.replace("_", ":")
        if '<,=!>' in title:
            ti, description = title.split("<,=!>")
        for j in search:
            if j in title or j in date or j.replace(":", "_") in date:
                collect.append({"date":date, "title": ti, 'describe':description, "path":filevideo, \
                                'txt':txtpath, 'ideo':ideopath})
                find = True
                break
        if len(search)==0:
            collect.append({"date":date, "title": ti, 'describe':description, "path":filevideo, \
                            'txt':txtpath, 'ideo':ideopath})
    collect = sorted(collect.__iter__(), key = lambda x:x['date'], reverse=True)
    if allfile==None:
        allfile = collect
    ret = collect[(currentpage-1) * pagesize : currentpage * pagesize]
    
    audio = []
    # mpthreeall = []
    for i in os.listdir(hlspath):
        nth = os.path.join(hlspath, i)
        # mpthree = []
        if os.path.isdir(nth):
            audio.append({'value' : None, 'label' : i, "children":[]})
            for j in os.listdir(nth):
                if '.mp3' not in j:
                    continue
                audio[-1]['children'].append({'value' : os.path.join("/hls/", i, j), 'label' : j.replace(".mp3", "")})
            audio[-1]['children'] = sorted(audio[-1]['children'].__iter__(), key = lambda k : k['label'].replace("T","").replace("_", "").replace("-", ""))
    audio = sorted(audio.__iter__(), key = lambda k : k['label'].replace("T","").replace("_", "").replace("-", ""), reverse=True)
    # mpthree.sort()
    # mpthree.reverse()
    
    # for i in mpthree:
    #     fileaudio = os.path.join("/hls/", i)
    #     audio.append({'value':fileaudio, 'label':i.replace(".mp3", "")})

    return JsonResponse({"collect":ret, "length":len(collect), "audio":audio}, safe = False)

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

