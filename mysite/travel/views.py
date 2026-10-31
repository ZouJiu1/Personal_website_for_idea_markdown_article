from django.http import HttpResponse
# from rest_framework.response import Response
# from rest_framework import status
from django.http import JsonResponse
import os
import html
from datetime import datetime
import time
from django.views.decorators.csrf import csrf_exempt
import numpy as np
addpath = os.path.abspath(__file__ + "/../../")
import sys
sys.path.append(addpath)
from csdn.views import getusername, renzheng, notify_administer, ADMIN_QUANXIAN, check_identity, is_admin, is_super_admin
import markdown2
import re as regular
from csdn.views import check_logined
from copy import deepcopy
import json
import shutil

sys.path.append(os.path.abspath(__file__ + "/../../"))
from manage import timezone
import siteconfig   # 站点统一配置（mysite/site_config.json，修改即时生效）

path = os.path.abspath(__file__ + "/../../../article/zhihu_spider_selenium/travel")
mainpath = os.path.abspath(__file__ + "/../../../dist/article")
if os.path.exists(mainpath):
    path = path.replace("/article/", '/dist/article/')
def rep(i):
    return i.replace(":", "_").replace("_问号_", "？").replace("_感叹号_", "！").\
              replace("小于", "<").replace("大于", ">").replace("_逗号_", "，").\
              replace("_空格_", " ").replace("_冒号_", "：").replace("_顿号_", "、")

allfile = {}  # 按 basepath 隔离的多用户缓存，避免用户间串数据
pre_page_size = None

def index(request):
    global allfile, path
    # body 兜底：空 body / 非法 JSON / 非 dict 一律按匿名默认参数处理，不再 500
    try:
        req = json.loads(request.body)
        if not isinstance(req, dict):
            req = {}
    except Exception:
        req = {}
    try:
        currentpage = int(req["currentpage"])
    except Exception:
        currentpage = int(siteconfig.get('default_currentpage'))
    try:
        pagesize = int(req["pagesize"])
    except Exception:
        pagesize = int(siteconfig.get('default_pagesize_travel'))
    # 分页防呆：页码至少 1，页大小限制上限，防负数切片与超大响应
    currentpage = max(1, currentpage)
    pagesize = min(max(1, pagesize), 200)
    search = str(req.get("search", ""))
    try:
        reset = int(req.get("reset", 0))
    except Exception:
        reset = 0

    basepath = deepcopy(path)
    try:
        get = json.loads(getusername(request).content)
    except Exception:
        get = {"ret": 0}
    if get.get('ret', 0) > 0:
        basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")
    # if "mail" in req.keys():
    #     if check_logined(req['mail'], req['password']):
    #         basepath = basepath.replace("/article/", f"/people/{get['mail']}/")

    # reset = 1
    if reset==1:
        allfile.pop(basepath, None)
    collect = []
    search = search.split(" ")
    while '' in search:
        search.remove("")
    # 缓存只存「中性全量列表」：带搜索词时必须实时构建，否则搜索结果会污染缓存
    cache = allfile.get(basepath)
    if cache is not None and len(search)==0:
        ret = cache[(currentpage-1) * pagesize : currentpage * pagesize]
        return JsonResponse({"collect":ret, "length":len(cache)}, safe = False)
    # 目录结构不完整（新用户目录未建/数据迁移）时 listdir 会 500，先收容
    os.makedirs(basepath, exist_ok=True)
    for i in os.listdir(basepath):
        nth = os.path.join(basepath, i)
        if not os.path.isdir(nth):
            continue
        date = i.replace("_", ":")
        markdownpth = ''
        markdown = ""
        markdownCopy = ""   # 目录无 txt 文件时兜底，防下方搜索匹配 NameError
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
                    # 行数护栏：损坏/手改文件不足 4 行时缺省为空，不再 IndexError
                    _name = mn[1] if len(mn) > 1 else ""
                    _mail = mn[2] if len(mn) > 2 else ""
                    _contact = mn[3] if len(mn) > 3 else ""
                    # 公开匿名留言板的纯文本字段一律 HTML 转义，防存储型 XSS（前端 v-html 渲染）
                    markdown = mn[0] + '\n' + "<p><span style=\"color:#000000;font-size=390;\">姓名：</span>\n<span style=\"color:#00ffee\">" + html.escape(_name) + \
                        '</span>      <span style=\"color:#000000;font-size=390;\">邮箱：</span>\n<span style=\"color:#00ffee\">' + html.escape(_mail) + \
                        '</span>      <span style=\"color:#000000;font-size=390;\">Contact：</span>\n<span style=\"color:#00ffee\">' + html.escape(_contact) + "</span></p>\n"
                markdown = markdown2.markdown(markdown)
            # if '.jpg' in j or '.png' in j or '.gif' in j or '.bmp' in j or 'jpeg' in j:
            #     imgimg += '<img class=\"think_image\"  @click=\"cardClick\" '+' src=\"article/zhihu_spider_selenium/think/' + i + '/' + j + '\" style=\"width = 100%;margin-left:3px;\"" >' + \
            #        f"<p hidden=\"true\" @click=\"cardClick\" class=\"hiddenp\">{nth}</p>" + \
            #             '</img>'
        # find = False
        # markdown = "<p @click=\"cardClick\">" + markdown + \
        #     f"<p hidden @click=\"cardClick\" class=\"hiddenp\">{nth}</p>" + \
        #     "</p>\n"
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
    # 搜索结果不入缓存（与 csdn index 同规则），否则后续无搜索词请求会拿到过滤后的列表
    if len(search)==0:
        allfile[basepath] = collect
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
    # body 兜底：空 body / 非法 JSON / 缺字段一律按发布失败处理，不再 500
    try:
        req = json.loads(request.body)
        postdate = str(req["postdate"])
        text_content = str(req["text_content"])
        travelname = str(req["travelname"])
        travelemail = str(req["travelemail"])
        travelcontact = str(req["travelcontact"])
    except Exception:
        return JsonResponse( { "post" : False} , safe = False)

    # 时间戳解析失败（客户端传非法值）按发布失败处理
    try:
        postdate = postdate[:-3] + "." + postdate[-3:]
        postdate = datetime.fromtimestamp(float(postdate) + timezone).isoformat()[:19]
        postdate = postdate.replace("T", " ").replace(":", "_")
    except Exception:
        return JsonResponse( { "post" : False} , safe = False)

    basepath = deepcopy(path)

    try:
        get = json.loads(getusername(request).content)
    except Exception:
        get = {"ret": 0}
    if get.get('ret', 0) > 0:
        basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")
    # if "mail" in req.keys():
    #     if check_logined(req['mail'], req['password']):
    #         basepath = basepath.replace("/article/", f"/people/{get['mail']}/")

    # imgpostdate = re["imgpostdate"]

    # imgpostdate = imgpostdate[:-3] + "." + imgpostdate[-3:]
    # imgpostdate = datetime.fromtimestamp(float(imgpostdate)).isoformat()[:19]
    # imgpostdate = imgpostdate.replace("T", " ").replace(":", "_")


    # if len(imgpostdate) > 0:
    #     upPath = os.path.join(path, imgpostdate)
    # else:

    # min 校验（既有规则）+ max 校验（防磁盘滥用，上限可配置）
    _minlen = int(siteconfig.get('travel_min_email_len'))
    _mincontact = int(siteconfig.get('travel_min_contact_len'))
    _mincontent = int(siteconfig.get('travel_min_content_len'))
    _maxcontent = int(siteconfig.get('travel_max_content_len'))
    _maxfield = int(siteconfig.get('travel_max_field_len'))
    if len(travelemail) < _minlen or "@" not in travelemail or len(travelcontact) < _mincontact or \
        len(travelname) == 0 or len(text_content) < _mincontent:
        return JsonResponse( { "post" : False} , safe = False)
    if len(text_content) > _maxcontent or len(travelname) > _maxfield or \
        len(travelemail) > _maxfield or len(travelcontact) > _maxfield:
        return JsonResponse( { "post" : False} , safe = False)

    # XSS 清洗：公开留言板任何访客可写，正文剥离 script 块与 javascript: 协议；
    # 姓名/邮箱/联系方式原文入库，由 index 渲染侧统一 html.escape（唯一转义点，避免双重转义）
    text_content = regular.sub(r'(?is)<\s*script.*?(?:</\s*script\s*>|$)', '', text_content)
    text_content = regular.sub(r'(?i)javascript\s*:', '', text_content)

    upPath = os.path.join(basepath, postdate)

    if not os.path.exists(upPath):
        # 递归创建，兼容新用户首次发布
        os.makedirs(upPath, exist_ok=True)

    with open(os.path.join(upPath, "content.txt"), 'w', encoding='utf-8') as obj:
        obj.write(text_content + "\n")
        obj.write(travelname + "\n" + travelemail + "\n" + travelcontact + '\n')
        # obj.write("<p><span style=\"color:#000000;font-size=390;\">姓名：</span>\n<span style=\"color:#00ffee\">" + travelname + \
        #     '</span>      <span style=\"color:#000000;font-size=390;\">邮箱：</span>\n<span style=\"color:#00ffee\">' + travelemail + \
        #     '</span>      <span style=\"color:#000000;font-size=390;\">Contact：</span>\n<span style=\"color:#00ffee\">' + travelcontact + "</span></p>\n")

    # if len(imgpostdate) > 0:
    #     os.rename(upPath, os.path.join(path, postdate))
    # 发布成功后再失效缓存，校验失败不影响已有缓存
    allfile.clear()
    return JsonResponse( { "post" : True} , safe = False)

def delete(request):
    global allfile
    # body 兜底：空 body / 非法 JSON / 缺 path 一律按未授权处理，不再 500
    try:
        req = json.loads(request.body)
        currentpage = str(req["path"])
    except Exception:
        return JsonResponse( { "ret" : -100} , safe = False)

    auth = check_identity(request, req, admin_bypass=True)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    realdel = os.path.realpath(currentpage)  # realpath 归一化后校验归属，防 ../ 穿越删除他人留言
    # 路径收容：删除目标只允许两个根 ——
    #   1) 公共留言区 travel_root（仅管理员，且不能删根本身）
    #   2) 本人数据区 people/<mail>/zhihu_spider_selenium/travel（不能删根本身）
    ROOT = os.path.abspath(__file__ + "/../../../")
    travel_root = os.path.realpath(path)
    own_root = os.path.realpath(os.path.join(ROOT, "people", str(get.get('mail', '')), "zhihu_spider_selenium", "travel"))
    in_public = realdel.startswith(travel_root + os.sep)
    in_own = realdel.startswith(own_root + os.sep)
    if not in_public and not in_own:
        return JsonResponse( { "ret" : -100} , safe = False)
    if not is_admin(get.get('quanxian', -1)) and not in_own:
        return JsonResponse( { "ret" : -100} , safe = False)
    try:
        allfile.clear()
        if is_admin(get['quanxian']) and get['mail']!=get['urlmail']:
            # 与 csdn/think/upload_video 保持一致：删除他人内容时备份到 administer/ 供恢复
            notify_administer(realdel, get['truemail'], get['mail'], get['urlmail'], False)
        elif is_admin(get['quanxian']) and get['mail']==get['urlmail']:
            notify_administer(realdel, get['truemail'], get['mail'], get['urlmail'], True)
        shutil.rmtree(realdel)
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
