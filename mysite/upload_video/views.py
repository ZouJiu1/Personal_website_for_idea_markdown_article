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
allfile = {}  # 按 basepath 隔离的多用户缓存，避免用户间串数据
pre_page_size = None

import sys
import json
sys.path.append(os.path.abspath(__file__ + "/../../"))
from manage import timezone
from csdn.views import check_logined, getusername, renzheng, notify_administer, ADMIN_QUANXIAN, check_identity, is_admin, is_super_admin
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
    allfile.clear()
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
    auth = check_identity(request, req)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
    # uid 化后 URL 不含邮箱，页面主人判定改用还原出的 urlmail（子串判断会误拒本人）
    if get['urlmail'] != get['mail']:
        return JsonResponse( { "ret" : -100} , safe = False)

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

    auth = check_identity(request, req, admin_bypass=True)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    realtxt = os.path.realpath(txtpath)      # realpath 归一化后校验归属，防 ../ 穿越删除他人视频
    realideo = os.path.realpath(ideopath)
    if not is_admin(get['quanxian']) and (f"/people/{get['mail']}/" not in realideo or f"/people/{get['mail']}/" not in realtxt or \
        '.txt' not in realtxt or ('.mp4' not in realideo and '.webm' not in realideo)):
        return JsonResponse( { "ret" : -100} , safe = False)

    try:
        allfile.clear()
        # shutil.rmtree(currentpage)
        if is_admin(get['quanxian']) and get['mail']!=get['urlmail']:
            notify_administer([txtpath, ideopath], get['truemail'], get['mail'], get['urlmail'], False)
        elif is_admin(get['quanxian']) and get['mail']==get['urlmail']:
            notify_administer([txtpath, ideopath], get['truemail'], get['mail'], get['urlmail'], True)
        os.remove(txtpath)
        os.remove(ideopath)
        return JsonResponse( { "done" : txtpath, 'ret': True} , safe = False)
    except:
        return JsonResponse( { "done" : txtpath, 'ret':0 } , safe = False)
