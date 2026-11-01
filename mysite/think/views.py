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
from csdn.views import handle_uploaded_file, replacewithjpg, getTail
from csdn.views import check_logined, getusername, renzheng, notify_administer, ADMIN_QUANXIAN, check_identity, is_admin, is_super_admin, _member_level
from mysite.projectpaths import find_top_marker, TOP_THINK, web_relative_path
import markdown2
import re as regular
from copy import deepcopy
import json
from threading import Semaphore
import shutil

sys.path.append(os.path.abspath(__file__ + "/../../"))
from manage import timezone
import siteconfig   # 站点统一配置（mysite/site_config.json，修改即时生效）

path = os.path.abspath(__file__ + "/../../../article/zhihu_spider_selenium/think")
mainpath = os.path.abspath(__file__ + "/../../../dist/article")
if os.path.exists(mainpath):
    path = path.replace("/article/", '/dist/article/')

def rep(i):
    return i.replace(":", "_").replace("_问号_", "？").replace("_感叹号_", "！").\
              replace("小于", "<").replace("大于", ">").replace("_逗号_", "，").\
              replace("_空格_", " ").replace("_冒号_", "：").replace("_顿号_", "、")

allfile = {}  # 按 basepath 隔离的多用户缓存，避免用户间串数据
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
        currentpage = int(siteconfig.get('default_currentpage'))
    try:
        pagesize = int(req["pagesize"])
    except:
        pagesize = int(siteconfig.get('default_pagesize_think'))
    search = req["search"]
    reset = int(req["reset"])

    # reset = 1
    basepath = deepcopy(path)

    get = json.loads(getusername(request).content)
    if get['ret'] > 0:
        basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")
    # if "mail" in req.keys():
        # if check_logined(req['mail'], req['password']):
        # basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
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
        ret = cache[(currentpage-1) * pagesize : currentpage * pagesize]
        # 点赞/收藏高亮是查看者个人状态：对本页条目浅拷贝后按请求者重算，
        # 防止高亮状态随首个查看者的身份固化进缓存、泄漏给其他查看者
        if maillogin != '#':
            ret = [dict(x, click=(maillogin in x['upvote']), clickshoucang=(maillogin in x['kshoucang'])) for x in ret]
        return JsonResponse({"collect":ret, "length":len(cache)}, safe = False)
    keep = '素 家 黄色 7元 方便面 骚扰 耳塞 APP 广告 短信 色情 献 血 卡片 书'.split(" ")
    TOPTOP = []
    # 目录结构不完整的用户（如数据迁移/目录被删）访问动态页时，目录可能不存在，直接 listdir 会 500
    os.makedirs(basepath, exist_ok=True)
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
            open(upvotecomment, 'a').close()
        upvote = []
        comment = []
        kshoucang = []
        # 点赞/收藏高亮不入缓存：构建时一律中性 False，返回前按查看者重算（见函数开头）
        click = False
        clickshoucang = False
        tails = i
        # setdefault 原子创建锁；读取期间不 pop（与写接口共用同一锁对象）
        sem = kseamutexpiaduan.setdefault(tails, Semaphore(value=1))
        sem.acquire()
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
        sem.release()

        modifytime = 0
        createtime = 0
        for j in allpath:
            if '.txt' in j and '.txt.swp' not in j:
                markdownpth = os.path.join(nth, j)
                # at = os.path.getatime(markdownpth)
                # ct = os.path.getctime(markdownpth)
                modifytime = os.path.getmtime(markdownpth) + timezone
                # 目录名不是合法日期（如手工创建的目录）时按 0 处理，避免 500
                try:
                    createtime = datetime.timestamp(datetime.fromisoformat(i.replace("_", ":")))
                except ValueError:
                    createtime = 0
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
        if abs(modifytime - createtime) > int(siteconfig.get('modified_label_seconds')):
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
            topPath = find_top_marker(nth, TOP_THINK)
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
    # 搜索结果不入缓存：缓存只存中性全量列表，避免污染后续无搜索请求
    if len(search)==0:
        allfile[basepath] = collect
    ret = collect[(currentpage-1) * pagesize : currentpage * pagesize]
    # 构建路径（含搜索）同样按查看者重算个性化状态：缓存与 collect 中存的均为中性数据
    if maillogin != '#':
        ret = [dict(x, click=(maillogin in x['upvote']), clickshoucang=(maillogin in x['kshoucang'])) for x in ret]
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

    # 目录不存在（内容已被删除）时返回空壳详情，避免 listdir 直接 500
    if not os.path.isdir(tailpath):
        return JsonResponse({"markdown" : "", 'path': pathkkk, "upvote":[], 'comment':[], 'click':False, \
                            'clickshoucang':False, 'kshoucang':[], 'title':"", "original":"", 'isTop':False}, \
                                safe = False)

    # 安全：详情读取收容在项目内（people/article/dist），防止传 /etc 等任意路径读 .txt 探测文件系统
    realdetail = os.path.realpath(tailpath)
    root = os.path.realpath(os.path.abspath(__file__ + "/../../../"))
    allowed_roots = [os.path.join(root, 'people') + os.sep,
                     os.path.join(root, 'article') + os.sep,
                     os.path.join(root, 'dist') + os.sep]
    if not any(realdetail.startswith(a) for a in allowed_roots):
        return JsonResponse({"markdown" : "", 'path': pathkkk, "upvote":[], 'comment':[], 'click':False, \
                            'clickshoucang':False, 'kshoucang':[], 'title':"", "original":"", 'isTop':False}, \
                                safe = False)

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
        if '.txt' in j and '.txt.swp' not in j:
            txtfile = j
            markdownpth = os.path.join(tailpath, j)
            with open(markdownpth, 'r', encoding = 'utf-8') as obj:
                markdown = obj.read().strip()
                original = deepcopy(markdown)
            modifytime = os.path.getmtime(markdownpth) + timezone

            # 目录名不是合法日期（如手工创建的目录）时按 0 处理，避免 500
            try:
                createtime = datetime.timestamp(datetime.fromisoformat(lasttail))
            except ValueError:
                createtime = 0
        if '.jpg' in j.lower() or '.png' in j.lower() or '.gif' in j.lower() or \
                '.bmp' in j.lower() or 'jpeg' in j.lower():
            if 'people' in tailpath:
                kk = '/people' + tailpath.split("people")[-1] + os.sep + j
            else:
                kk = '/article' + tailpath.split("article")[-1] + os.sep + j
            imgimg += '<img ' + f'src=\"{kk}\" style=\"width = 30%;margin-top:6px;margin-bottom:6px;\"" />\n'
    markdown = markdown2.markdown(markdown)
    # 与 index() 列表页统一使用站点配置的「已修改」标签阈值
    if abs(modifytime - createtime) > int(siteconfig.get('modified_label_seconds')):
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
    # 锁名必须与写接口（kshoucang/comment_add/upvote_change）一致用目录名，
    # 否则详情读与点赞/评论写各持一把锁，并发下读写不互斥
    tails = tailpath.split(os.sep)[-1]
    # setdefault 原子创建锁；读取期间不 pop（与写接口共用同一锁对象）
    sem = kseamutexpiaduan.setdefault(tails, Semaphore(value=1))

    upvotecomment = os.path.join(tailpath, 'upvote_comment.json')
    if not os.path.exists(upvotecomment):
        open(upvotecomment, 'a').close()

    sem.acquire()
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
    sem.release()

    topPath = find_top_marker(tailpath, TOP_THINK)
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
    allfile.clear()
    # req = request.GET.dict()
    req = json.loads(request.body)
    basepath = deepcopy(path)
    tailpath = req["path"]
    editcontent = req['editcontent']

    auth = check_identity(request, req)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
    tailreal = os.path.realpath(tailpath)  # 用 realpath 归一化后做归属校验，防止 ../ 路径穿越篡改他人内容
    if is_admin(get['quanxian']):
        pass  # 管理员可修改任何用户的内容
    elif get['urlmail'] != get['mail'] or f"/people/{get['mail']}/" not in tailreal:
        # 普通用户只能修改自己目录下的内容。
        # uid 化后 URL 不含邮箱，页面主人判定改用 getusername 还原出的 urlmail
        # （原来是 URL 子串判断，uid 形态下恒为 False 会误拒本人操作）
        return JsonResponse( { "ret" : -100} , safe = False)

    if not os.path.isdir(tailpath):
        return JsonResponse( { "ret" : -100} , safe = False)

    # 内容容量上限，防止超大 payload 落盘（与 csdn postArticle 一致）
    if len(editcontent) > 5 * 1024 * 1024:
        return JsonResponse({"ret": -2, "msg": "内容过大（超过5MB）"}, safe=False)

    allpath = os.listdir(tailpath)
    allpath = sorted(allpath.__iter__(), key=lambda x:os.path.getmtime(os.path.join(tailpath, x)))
    # setdefault 原子创建锁：check-then-set 写法在并发下会各自 new 出不同锁对象，锁失效
    sem = allmutex.setdefault(tailpath, Semaphore(value=1))

    def atomic_write(target, content):
        # 原子写：先写临时文件再 os.replace，进程中断也不会留下截断的半截内容
        tmp = target + ".tmp"
        with open(tmp, 'w', encoding='utf-8') as obj:
            obj.write(content)
        os.replace(tmp, target)

    modified = False
    for j in allpath:
        if '.txt' in j and '.txt.swp' not in j:
            markdownpth = os.path.join(tailpath, j)
            sem.acquire()
            try:
                atomic_write(markdownpth, editcontent)
            finally:
                sem.release()
            modified = True
            break
    if not modified:
        markdownpth = os.path.join(tailpath, "content.txt")
        sem.acquire()
        try:
            atomic_write(markdownpth, editcontent)
        finally:
            sem.release()
    return JsonResponse({"ret" : True}, safe = False)

def delete(request):
    global allfile, allmutex
    # req = request.GET.dict()
    req = json.loads(request.body)
    currentpage = req["path"]
    #print(currentpage)
    auth = check_identity(request, req, admin_bypass=True)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    realdel = os.path.realpath(currentpage)  # realpath 归一化后再校验归属，防 ../ 穿越删除他人目录
    if not is_admin(get['quanxian']) and (f"/people/{get['mail']}/" not in realdel or '20'!=os.path.basename(realdel)[:2]):
        return JsonResponse( { "ret" : -100} , safe = False)

    try:
        allfile.clear()
        if is_admin(get['quanxian']) and get['mail']!=get['urlmail']:
            # 与 csdn/travel/upload_video 保持一致：删除他人内容时备份到 administer/ 供恢复
            notify_administer(currentpage, get['truemail'], get['mail'], get['urlmail'], False)
        elif is_admin(get['quanxian']) and get['mail']==get['urlmail']:
            notify_administer(currentpage, get['truemail'], get['mail'], get['urlmail'], True)
        if currentpage not in allmutex.keys():
                allmutex[currentpage] = Semaphore(value=1)
        allmutex[currentpage].acquire()
        #print(currentpage)
        try:
            shutil.rmtree(str(currentpage))
        finally:
            # rmtree 失败也必须释放锁，否则该目录的后续操作全部死锁
            allmutex[currentpage].release()
        return JsonResponse( { "done" : currentpage, 'ret': True} , safe = False)
    except Exception as e:
        print(2222222, e)
        return JsonResponse( { "done" : currentpage, 'ret':0 } , safe = False)

def post_think(request):
    global allfile, path
    allfile.clear()
    # req = request.GET.dict()
    req = json.loads(request.body)
    basepath = deepcopy(path)

    auth = check_identity(request, req)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
    # uid 化后 URL 不含邮箱，页面主人判定改用还原出的 urlmail（子串判断会误拒本人）
    if get['urlmail'] != get['mail']:
        return JsonResponse( { "ret" : -100} , safe = False)
    postdate = str(req["postdate"])

    # 时间参数来自客户端，垃圾输入会让 float()/fromtimestamp() 直接 500
    try:
        postdate = postdate[:-3] + "." + postdate[-3:]
        postdate = datetime.fromtimestamp(float(postdate) + timezone).isoformat()[:19]
        postdate = postdate.replace("T", " ").replace(":", "_")

        imgpostdate = str(req["imgpostdate"])
        if len(imgpostdate) > 6:
            imgpostdate = imgpostdate[:-3] + "." + imgpostdate[-3:]
            imgpostdate = datetime.fromtimestamp(float(imgpostdate) + timezone).isoformat()[:19]
            imgpostdate = imgpostdate.replace("T", " ").replace(":", "_")
    except (ValueError, OSError, OverflowError):
        return JsonResponse( { "ret" : -1, "msg" : "时间参数不合法" } , safe = False)
    text_content = req["text_content"]
    # 内容容量上限，防止超大 payload 落盘（与 csdn postArticle 一致）
    if len(text_content) > 5 * 1024 * 1024:
        return JsonResponse({"ret": -2, "msg": "内容过大（超过5MB）"}, safe=False)

    if len(imgpostdate) > 6:
        upPath = os.path.join(basepath, imgpostdate)
    else:
        upPath = os.path.join(basepath, postdate)

    if not os.path.exists(upPath):
        # 新用户首次发布时 people/<mail>/zhihu_spider_selenium/think 可能整条不存在，
        # 用 makedirs 递归创建，避免 FileNotFoundError 导致 500
        os.makedirs(upPath, exist_ok=True)

    with open(os.path.join(upPath, "content.txt"), 'w', encoding='utf-8') as obj:
        obj.write(text_content)

    if len(imgpostdate) > 6:
        target = os.path.join(basepath, postdate)
        try:
            os.rename(upPath, target)
        except OSError:
            # 目标目录已存在（同秒已有发布）：把图片搬进目标目录，避免 ENOTEMPTY 500
            if os.path.realpath(upPath) != os.path.realpath(target):
                for f in os.listdir(upPath):
                    shutil.move(os.path.join(upPath, f), os.path.join(target, f))
                os.rmdir(upPath)
    return JsonResponse( { "ret" : True} , safe = False)

@csrf_exempt
def uploadImg(request):
    global allfile, path
    allfile.clear()
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
    auth = check_identity(request, req)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
    # uid 化后 URL 不含邮箱，页面主人判定改用还原出的 urlmail（子串判断会误拒本人）
    if get['urlmail'] != get['mail']:
        return JsonResponse( { "ret" : -100} , safe = False)

    # https://docs.djangoproject.com/zh-hans/5.1/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile
    uploadImageName = request.FILES['file'].name
    # 安全：仅允许图片扩展名上传，防止 .html/.svg 等可执行内容落到静态目录形成存储型 XSS
    if not getTail(uploadImageName):
        return JsonResponse({ "ret" : -1, "msg" : "仅支持上传图片（jpg/jpeg/png/bmp/gif）" }, safe=False)
    # 安全：剥离路径成分，防文件名携带 ../ 逃逸保存目录
    uploadImageName = os.path.basename(uploadImageName)
    # https://docs.djangoproject.com/zh-hans/5.1/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile
    # uploadType = request.FILES['file'].content_type
    # assert 1==0, (time.time(), postdate)
    savepath = ""
    if 'detail' in req.keys():
        savepath = req['path']
        # 安全：realpath 归一化后必须收容在项目内（people/article/dist），
        # 原来的子串判断可被 /people/x/../../evil 形式的路径绕过
        realsave = os.path.realpath(savepath)
        root = os.path.realpath(os.path.abspath(__file__ + "/../../../"))
        allowed_roots = [os.path.join(root, 'people') + os.sep,
                         os.path.join(root, 'article') + os.sep,
                         os.path.join(root, 'dist') + os.sep]
        if not os.path.isdir(savepath) or not any(realsave.startswith(a) for a in allowed_roots):
            return JsonResponse( { "ret" : -100} , safe = False)
        # 普通用户只能上传到自己目录，管理员可上传到任何收容目录
        if not is_admin(get.get('quanxian')) and f"/people/{get['mail']}/" not in realsave:
            return JsonResponse( { "ret" : -100} , safe = False)
    else:
        try:
            postdate = postdate[:-3] + "." + postdate[-3:]
            postDa = datetime.fromtimestamp(float(postdate) + timezone).isoformat()[:19]
        except (ValueError, OSError, OverflowError):
            return JsonResponse( { "ret" : -1, "msg" : "时间参数不合法" } , safe = False)
        postDate = postDa.replace("T", " ").replace(":", "_")
        savepath = os.path.join(basepath, postDate)
        if not os.path.exists(savepath):
            # 递归创建，兼容新用户首次上传
            os.makedirs(savepath, exist_ok=True)

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
    allfile.clear()
    # req = request.GET.dict()
    req = json.loads(request.body)
    placepath = req["path"]

    auth = check_identity(request, req)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    if is_admin(get['quanxian']):
        if not os.path.isdir(placepath):
            return JsonResponse( { "ret" : -100} , safe = False)
        pass  # 管理员可置顶/取消置顶任何用户的内容
    else:
        realtop = os.path.realpath(placepath)  # realpath 防穿越；目录必须真实存在，避免对已删内容写 TOP.text 500
        if f"/people/{get['mail']}/" not in realtop or '20'!=os.path.basename(realtop)[:2] or not os.path.isdir(placepath):
            return JsonResponse( { "ret" : -100} , safe = False)

    # dirname = placepath.split(os.sep)[-1]
    
    pathkkkTmp = os.path.join(placepath, "TOP.text")
    with open(pathkkkTmp, 'w', encoding="utf-8") as obj:
        obj.write("")
    # 统一命名：清掉历史遗留的另一种命名，避免出现双标记
    legacy = os.path.join(placepath, "TOP.txt")
    if os.path.exists(legacy):
        os.remove(legacy)

    # postDa = datetime.fromtimestamp(time.time() + timezone).isoformat()[:19]
    # postDate = postDa.replace("T", " ").replace(":", "_")
    
    # os.rename(placepath, placepath.replace(dirname, postDate))
    # return JsonResponse( { "path" : placepath.replace(dirname, postDate) , 'ret':True} , safe = False)
    return JsonResponse( { "path" : "" , 'ret':True} , safe = False)


def cancelPlaceTop(request):
    global allfile
    allfile.clear()
    # req = request.GET.dict()
    req = json.loads(request.body)
    placepath = req["path"]

    auth = check_identity(request, req)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    if is_admin(get['quanxian']):
        pass  # 管理员可置顶/取消置顶任何用户的内容
    else:
        realtop = os.path.realpath(placepath)  # realpath 防穿越
        if f"/people/{get['mail']}/" not in realtop or '20'!=os.path.basename(realtop)[:2]:
            return JsonResponse( { "ret" : -100} , safe = False)

    # 兼容两种历史命名，全部清除
    for name in ("TOP.text", "TOP.txt"):
        p = os.path.join(placepath, name)
        if os.path.exists(p):
            os.remove(p)
    return JsonResponse( { "path" : "" , 'ret':True} , safe = False)

def check_item_path(pathkkk):
    """点赞/评论/收藏的 path 安全校验：必须是 people/ 下以日期(20)开头的 think 目录，
    防止路径遍历在任意目录写 upvote_comment.json"""
    try:
        real = os.path.realpath(pathkkk)
        root = os.path.realpath(os.path.abspath(__file__ + "/../../../"))
        people_root = os.path.join(root, 'people') + os.sep
        if not real.startswith(people_root):
            return False
        # 目录必须真实存在（已删除的内容一律拒绝，避免写 upvote_comment.json 时 FileNotFoundError 500）
        return os.path.isdir(real) and os.path.basename(real.rstrip(os.sep))[:2] == '20'
    except Exception:
        return False

kseamutexpiaduan = {}
kshoucangmutexpianduan = Semaphore(value=1)
def kshoucang(request):
    global path, kseamutexpiaduan, kshoucangmutexpianduan
    body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    req = json.loads(body)

    # req = request.POST.dict()
    # 校验前置：非法 path 直接拒绝，不能先把自己的收藏清单写了一半再返回 -100（状态分裂）
    if not check_item_path(req['path']):
        return JsonResponse( { "ret" : -100 } , safe = False)
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    # kkkpath = deepcopy(basepath)
    auth = check_identity(request, req)
    get = auth['get']
    if not auth['passed']:
        return JsonResponse( { "ret" : -100} , safe = False)
    basepath = basepath.replace("/article/", f"/people/{get['mail']}/")

    filepath = os.path.join(basepath, 'kshoucangpianduan.json')
    # 用户从未发布过任何内容时 people/<mail>/ 目录可能不存在，直接写会 FileNotFoundError(500)
    os.makedirs(basepath, exist_ok=True)

    kshoucangmutexpianduan.acquire()
    try:
        # 读-改-写合并到同一次加锁：原来读、写分开两次加锁，中间的窗口会被并发请求穿插
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as obj:
                json.dump([], obj, indent=2, ensure_ascii=False)
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
        with open(filepath, 'w', encoding='utf-8') as obj:
            json.dump(kshoucangJson, obj, indent=2, ensure_ascii=False)
    finally:
        kshoucangmutexpianduan.release()

    pathkkk = req['path']
    tails = pathkkk.split(os.sep)[-1]
    # setdefault 原子创建锁；读写合并到同一次加锁；不再 pop 锁（pop 会让并发等待者拿到已移除的锁对象）
    sem = kseamutexpiaduan.setdefault(tails, Semaphore(value=1))
    jsonpath = os.path.join(pathkkk, 'upvote_comment.json')

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
    global path, kseamutexpiaduan #, kcommentmutex
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
    # 评论内容校验：去空白后非空且不超过 2000 字（与 csdn comment_add 一致）
    comment_text = str(req.get('comment', '')).strip()
    if len(comment_text)==0:
        return JsonResponse( { "ret" : -2, "msg" : "评论不能为空" } , safe = False)
    if len(comment_text) > 2000:
        return JsonResponse( { "ret" : -2, "msg" : "评论不能超过 2000 字" } , safe = False)
    tails = pathkkk.split(os.sep)[-1]
    # setdefault 原子创建锁；读写合并到同一次加锁；不再 pop 锁（原因同 kshoucang）
    sem = kseamutexpiaduan.setdefault(tails, Semaphore(value=1))
    jsonpath = os.path.join(pathkkk, 'upvote_comment.json')

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
        jsonfile['comment'].append(["http://zoujiu.com.cn/"+req['mail'], comment_text, " - - - " + postDate, req['mail'], get['nickname']])
        with open(jsonpath, 'w', encoding='utf-8') as obj:
            json.dump(jsonfile, obj, indent=2, ensure_ascii=False)
    finally:
        sem.release()
    return JsonResponse( { "ret" : True } , safe = False)

def upvote_change(request):
    global path, kseamutexpiaduan
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
    sem = kseamutexpiaduan.setdefault(tails, Semaphore(value=1))
    jsonpath = os.path.join(pathkkk, 'upvote_comment.json')

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

# ==================== 片段配图管理 ====================
# 片段的图片与 content.txt 同目录存放（people/<mail>/.../think/<postdate>/）。
# 供片段详情页「图片管理」列出/删除配图；鉴权与其他写接口一致：登录/管理员 + realpath 归属校验。
_thinkimg_mutex = Semaphore(value=1)
_IMG_TAILS = ('.jpg', '.png', '.jpeg', '.bmp', '.gif')

def _think_img_auth(request, req):
    """片段图片接口统一鉴权：通过返回 (dirpath, '')，失败返回 ('', 原因)。
    dirpath 为片段目录 realpath：仅允许 people/ 或 article/ 内；普通用户仅限本人目录，管理员不限。"""
    auth = check_identity(request, req, admin_bypass=True)
    get = auth['get']
    if not auth['passed']:
        return '', '未登录或校验失败'
    root = os.path.realpath(os.path.abspath(__file__ + "/../../../"))
    dirpath = str(req.get('path', ''))
    if dirpath and not dirpath.startswith('/'):
        # 相对路径按项目根解析（与站点 /people/... 静态路径一致），避免受 Django 进程 cwd 影响
        dirpath = os.path.join(root, dirpath)
    real = os.path.realpath(dirpath) if dirpath else ""
    allowed_roots = [os.path.join(root, 'people') + os.sep, os.path.join(root, 'article') + os.sep]
    if not real or not any(real.startswith(a) for a in allowed_roots) or not os.path.isdir(real):
        return '', '片段目录不存在或路径非法'
    # 身份取「请求自带且已通过 check_logined 校验的 mail」，
    # 不能用 getusername 从 URL 解析的 get['mail']——部分 URL 形态（短 urlmail 等）
    # 会把已登录用户匿名化成 None，导致本人操作自己的片段也被误判越权。
    mail = str(req.get('mail', ''))
    if not (is_admin(get.get('quanxian', -1)) or is_admin(_member_level(req))):
        own_root = os.path.join(root, 'people', mail) + os.sep
        if not mail or not real.startswith(own_root):
            return '', '只能操作自己的内容'
    return real, ''

def _img_safe_name(name):
    """校验客户端传来的文件名：必须是纯文件名（无路径成分、无 ..）且为图片扩展名。"""
    name = str(name or '')
    if not name or name != os.path.basename(name) or '..' in name:
        return ''
    if not any(name.lower().endswith(t) for t in _IMG_TAILS):
        return ''
    return name

def img_list(request):
    """片段配图列表。req: {mail, password, path}；返回 [{name,url,size,mtime}] 按时间倒序。"""
    try:
        req = json.loads(request.body)
    except Exception:
        return JsonResponse({"ret": -100}, safe=False)
    dirpath, err = _think_img_auth(request, req)
    if err:
        return JsonResponse({"ret": -100, "msg": err}, safe=False)
    images = []
    try:
        for f in os.listdir(dirpath):
            if not any(f.lower().endswith(t) for t in _IMG_TAILS):
                continue
            p = os.path.join(dirpath, f)
            try:
                st = os.stat(p)
            except Exception:
                continue
            images.append({"name": f,
                           "url": web_relative_path(p),
                           "size": st.st_size,
                           "mtime": datetime.fromtimestamp(st.st_mtime + timezone).strftime('%Y-%m-%d %H:%M:%S')})
        images.sort(key=lambda x: x["mtime"], reverse=True)
    except Exception:
        return JsonResponse({"ret": -2, "msg": "片段目录不存在或已删除"}, safe=False)
    return JsonResponse({"ret": 1, "images": images}, safe=False)

def img_delete(request):
    """删除片段配图。req: {mail, password, path, name}。"""
    try:
        req = json.loads(request.body)
    except Exception:
        return JsonResponse({"ret": -100}, safe=False)
    dirpath, err = _think_img_auth(request, req)
    if err:
        return JsonResponse({"ret": -100, "msg": err}, safe=False)
    name = _img_safe_name(req.get('name', ''))
    if not name:
        return JsonResponse({"ret": -100, "msg": "非法图片文件名"}, safe=False)
    p = os.path.join(dirpath, name)
    if not os.path.realpath(p).startswith(dirpath + os.sep):
        return JsonResponse({"ret": -100, "msg": "非法图片路径"}, safe=False)
    _thinkimg_mutex.acquire()
    try:
        if not os.path.exists(p):
            return JsonResponse({"ret": -2, "msg": "图片不存在或已删除"}, safe=False)
        os.remove(p)
    finally:
        _thinkimg_mutex.release()
    return JsonResponse({"ret": 1}, safe=False)
