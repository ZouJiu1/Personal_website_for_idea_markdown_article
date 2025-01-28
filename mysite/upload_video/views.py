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

import sys
import json
sys.path.append(os.path.abspath(__file__ + "/../../"))
from manage import timezone
from csdn.views import check_logined, getusername, renzheng, notify_administer
from copy import deepcopy
import shutil

# https://docs.djangoproject.com/zh-hans/5.1/topics/http/file-uploads/
def handle_uploaded_file(f, savename):
    with open(savename, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)
        # destination.write(f)

@csrf_exempt
def index(request):
    return HttpResponse("1")

@csrf_exempt
def upload(request):
    # return HttpResponse("Hello, world. You're at the polls index.")
    global allfile, path
    allfile = None
    # body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    req = request.POST.dict()
    # https://docs.djangoproject.com/zh-hans/5.1/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile
    uploadImageName = request.FILES['file'].name
    tail = "." + uploadImageName[-6:].split(".")[-1] 
    # assert 1==0, (re, uploadImageName)
    # https://docs.djangoproject.com/zh-hans/5.1/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile
    # uploadType = request.FILES['file'].content_type
    # assert 1==0, (time.time(), postdate)
    describe = req['textarea1']
    postDa = datetime.fromtimestamp(time.time() +timezone).isoformat()[:19]
    postDate = postDa.replace("T", " ").replace(":", "_")

    # if not os.path.exists(savepath):
    #     os.mkdir(savepath)
    basepath = deepcopy(path)
    # if "mail" in req.keys():
    #     # if check_logined(req['mail'], req['password']):
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

    savepath = deepcopy(basepath)
    
    dirlast = savepath.split(os.sep)[-1]
    
    videopath = os.path.join(savepath, uploadImageName)
    # if '.mp4' not in uploadImageName and '.webm' not in uploadImageName: //no need, .vue checked already
    #     return JsonResponse( { "ret" : -200} , safe = False)
    if os.path.exists(videopath):
        uploadImageName = uploadImageName.replace(tail, "_" + postDate[:10] + tail)
        videopath = os.path.join(savepath, uploadImageName)
    handle_uploaded_file(request.FILES['file'], videopath)
    
    txtpath = os.path.join(savepath, uploadImageName.replace(tail, ".txt"))
    with open(txtpath, 'w', encoding="utf-8") as obj:
        obj.write(uploadImageName + "<,=!>" + describe + "\n")
        obj.write(postDate + "\n")
    
    return JsonResponse( { "dirname" : dirlast, "path":savepath} , safe = False)

def delete(request):
    global allfile
    # req = request.GET.dict()
    req = json.loads(request.body)
    txtpath = req["txt"]
    ideopath = req["ideo"]

    rz = renzheng(request)
    rzret = json.loads(rz.content)
    passed = False
    get = {'quanxian': -1}
    if "mail" in req.keys():
        get = json.loads(getusername(request).content)
        if get['quanxian'] < 1000000 and not rzret['ret'] and 'password' in req.keys() and check_logined(req['mail'], req['password']):
            # basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
            passed = True
            if f"/people/{get['mail']}/" not in ideopath or f"/people/{get['mail']}/" not in txtpath or \
                '.txt' not in txtpath or ('.mp4' not in ideopath and '.webm' not in ideopath):
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
        # shutil.rmtree(currentpage)
        if get['quanxian'] == 1000000 and get['mail']!=get['urlmail']:
            notify_administer([txtpath, ideopath], get['truemail'], get['mail'], get['urlmail'], False)
        elif get['quanxian'] == 1000000 and get['mail']==get['urlmail']:
            notify_administer([txtpath, ideopath], get['truemail'], get['mail'], get['urlmail'], True)
        os.remove(txtpath)
        os.remove(ideopath)
        return JsonResponse( { "done" : txtpath, 'ret': True} , safe = False)
    except:
        return JsonResponse( { "done" : txtpath, 'ret':0 } , safe = False)
