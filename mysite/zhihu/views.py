from django.http import HttpResponse
# from rest_framework.response import Response
# from rest_framework import status
from django.http import JsonResponse
import os
from datetime import datetime
import time
import json

path = os.path.abspath(__file__ + "/../../../article/zhihu_spider_selenium/article")
mainpath = os.path.abspath(__file__ + "/../../../dist/article")

addpath = os.path.abspath(__file__ + "/../../")
import sys
sys.path.append(addpath)
from manage import timezone
from csdn.views import getusername

if os.path.exists(mainpath):
    path = path.replace("/article/", '/dist/article/')
def rep(i):
    return i.replace(":", "_").replace("_问号_", "？").replace("_感叹号_", "！").\
              replace("小于", "<").replace("大于", ">").replace("_逗号_", "，").\
              replace("_空格_", " ").replace("_冒号_", "：").replace("_顿号_", "、")

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
    global allfile, path
    # https://docs.djangoproject.com/en/5.1/ref/request-response/#top
    # re = request.GET.dict()
    re = json.loads(request.body)
    try:
        currentpage = int(re["currentpage"])
    except:
        currentpage = 1
    try:
        pagesize = int(re["pagesize"])
    except:
        pagesize = 6
    search = re["search"]
    reset = int(re["reset"])

    get = json.loads(getusername(request).content)
    # basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    if get['ret'] > 0:
        path = path.replace("/article/", f"/people/{get['urlmail']}/")

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
    for i in os.listdir(path):
        nth = os.path.join(path, i)
        if not os.path.isdir(nth):
            continue
        if '20'==i[:2]:
            date = rep(i[:2**4+1])
            date = date[:10] + " " + date[11:]
            date = date[:13] + ":" + date[13+1:]
            date = date[:-1]
            title = rep(i[2**4+1:])
        else:
            postDate = datetime.fromtimestamp(time.time() + timezone).isoformat()[:19]
            postDate = postDate.replace("T", " ")
            date = date[:10] + " " + date[11:]
            # date = '9#########' #datetime.fromtimestamp(time.time()).isoformat()
            title = rep(i)
        markdown = "# no content\n# no content\n# no content\n"
        markdownpth = findlatest(nth)
        if len(markdownpth) > 0:
            with open(markdownpth, 'r', encoding = 'utf-8') as obj:
                markdown = obj.read().strip()
        else:
            markdownpth = os.path.join(nth, 'markdown.md')
            with open(markdownpth, 'w', encoding = 'utf-8') as obj:
                obj.write(markdown)
        find = False
        for j in search:
            if j in markdown or j in i or j.replace(":", "_") in i:
                collect.append({"date":date, "title": title, "markdown": markdown[:200], "path":markdownpth})
                find = True
                break
        if len(search)==0:
            collect.append({"date":date, "title": title, "markdown": markdown[:200], "path":markdownpth})
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

def notify_edit(request):
    global allfile
    allfile = None
    return HttpResponse("clear")