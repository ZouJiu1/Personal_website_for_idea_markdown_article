from django.http import HttpResponse
# from rest_framework.response import Response
# from rest_framework import status
from django.http import JsonResponse
import os
# from datetime import datetime
# import markdown2
# import time
# import re as regular
import json
# import shutil
# import numpy as np
path = os.path.abspath(__file__ + "/../../../article/csdn_spider_selenium/article")
addpath = os.path.abspath(__file__ + "/../../")
mainpath = os.path.abspath(__file__ + "/../../../dist/article")
if os.path.exists(mainpath):
    path = path.replace("/article/", '/dist/article/')
# addpath = addpath.replace("/article/", '/dist/article/')
import sys
sys.path.append(addpath)
sys.path.append(os.path.abspath(__file__ + "/../../"))
from csdn.views import getusername, renzheng, check_logined, kshoucangmutex
from think.views import kshoucangmutexpianduan
from manage import timezone
from datetime import datetime
# from manage import timezone
# from markdown_detail.views import remove_code, addback_code, remove_katex, addback_katex
# from django.views.decorators.csrf import csrf_exempt
from copy import deepcopy
import json
from threading import Semaphore
import re as regular
import time
import smtplib
from email.message import EmailMessage

def index(request):
    return HttpResponse(".")

textarea_content_predefined = \
'''
在线课堂
学堂在线===https://www.xuetangx.com
中国大学MOOC慕课===https://www.icourse163.org
coursera===https://www.coursera.org/
edx===https://www.edx.org
udacity===https://www.udacity.com/
网易公开课===http://open.163.com

编程
Leetcode===https://leetcode.com
PAT===https://pintia.cn/home
PATest===https://www.patest.cn
CSP===https://www.cspro.org/Notices
Hello算法===https://www.hello-algo.com
LeetcodeWiki===https://doocs.github.io/leetcode
Kaggle===https://www.kaggle.com/
天池===https://tianchi.aliyun.com/
oi-wiki===https://oi-wiki.org
Github===https://github.com
CSDN===https://zoujiu.blog.csdn.net
stackoverflow===https://stackoverflow.com
知乎===https://www.zhihu.com/people/zoujiu1
阿里云工作台===https://home.console.aliyun.com/home/dashboard/ProductAndService
前端MDN===https://developer.mozilla.org/zh-CN/docs
shiyanlou===https://www.shiyanlou.com/
动手学RL===https://hrl.boyuai.com/chapter/ending
LLM===https://www.nvidia.com/en-us/learn/learning-path/generative-ai-llm/?deeplink=courses--4#courses-item-7757ba5d77
生成式人工智能（AIGC）之备案要求===https://mp.weixin.qq.com/s?__biz=MzkxMjYwMzMxMA==&mid=2247490590&idx=1&sn=6c7903c4fe11c6b3ee72fd4f6c5f5330&chksm=c0bb5752aefec38a64c30f9de1336dbff9760453d3b3735fcc63181cb11542f126a841843f67&mpshare=1&scene=23&srcid=1225RTXuAFdlUFvs7iGar1b4&sharer_shareinfo=9846e8a96b02f30dab883da3cf6ed782&sharer_shareinfo_first=9846e8a96b02f30dab883da3cf6ed782#rd
音视频开发中文===https://avmedia.0voice.com/?id=311

AI智能
pytorch===https://pytorch.org/
PyTorch-github===https://github.com/pytorch/pytorch
nvidia===https://www.nvidia.cn
tensorrt===https://developer.nvidia.com/tensorrt
Tensorrt-github===https://github.com/NVIDIA/TensorRT
keras===https://keras.io
Keras-github===https://github.com/keras-team/keras
tensorflow===https://tensorflow.org
tensorflow-github===https://github.com/tensorflow/tensorflow
阿里通义万相===https://tongyi.aliyun.com/wanxiang
腾讯智影===https://zenvideo.qq.com/image/create

网上购物
京东===https://jd.com/
淘宝===http://www.taobao.com/
拼多多===https://www.pinduoduo.com/
当当图书===https://www.dangdang.com
阿里1688===https://www.1688.com/

在线书籍
鸟哥的Linux私房菜===https://vbird.org.cn/
动手学Reinforce Learning===https://hrl.boyuai.com/

高中本科生研究生
隆回县第二中学===http://www.lhez.net/index.asp
学信网===http://www.chsi.com.cn
中国研究生招生信息网===https://yz.chsi.com.cn
N诺计算机===https://noobdream.com
爱启航===https://www.iqihang.com/ark/exam25?code=10
浙江大学研究生招生网===grs.zju.edu.cn/yjszs/redir.php?catalog_id=139436&object_id=145597
考研400分到底有多难?-知乎===https://www.zhihu.com/question/294241400

法律
知恒===http://www.zhihenglawyer.com

社保或公积金
长沙住房公积金管理中心===http://gjjzx.changsha.gov.cn/
长沙市12333公共服务平台===https://www.cs12333.com/revision/#/
北京住房公积金网===https://gjj.beijing.gov.cn
北京市人力资源和社会保障局===https://rsj.beijing.gov.cn/
北京市人力资源和社会保障局===https://fuwu.rsj.beijing.gov.cn/zhrs/yltc/

镜像
tsinghua===https://mirrors.tuna.tsinghua.edu.cn
熊猫===https://sc.panda321.com/scholar?cites=17925554201740498286&as_sdt=2005&sciodt=0,5&hl=zh-CN
iMyShare-Google国内镜像网站===https://imyshare.com/site/551/

软件
今日水印相机APP===https://www.jinrishuiyinxiangji.com/
Git===https://git-scm.com
QQ===https://im.qq.com
向日葵===https://sunlogin.oray.com/
vscode===https://code.visualstudio.com
win10===https://www.microsoft.com/zh-cn/software-download/windows10ISO
Microsoft帐户===https://account.microsoft.com/?ref=MeControl
faststonecapture===https://www.faststonecapture.cn
filezilla===https://filezilla-project.org
ffmpeg===https://ffmpeg.org/documentation.html
CMakeDocument===https://cmake.org/cmake/help/git-stage
CMake===https://cmake.org
Docker===https://docs.docker.com/desktop/setup/install
qemu===https://www.qemu.org/documentation
COCO_Dataset===https://cocodataset.org/#download
pascal_VOC_Dataset===http://host.robots.ox.ac.uk/pascal/VOC/voc2012/index.html#data
raspberrypi===https://www.raspberrypi.com/software
GNU-Make===https://www.gnu.org/software/make/
Clang===https://clang.llvm.org/docs/CrossCompilation.html
llvm===https://llvm.org/docs/HowToCrossCompileLLVM.html
阿里云盘===https://www.aliyundrive.com
panbaidu===https://pan.baidu.com
钉钉===https://www.dingtalk.com
teamviewer===https://www.teamviewer.cn
nmap===https://nmap.org/docs.html
bluestacks===https://www.bluestacks.com/download.html
genymotion===https://www.genymotion.com/product-desktop/download/
高漫===https://www.gaomon.cn/
edge===https://www.microsoft.com/zh-cn/edge/download?form=MA13FJ
office===https://account.microsoft.com/profile/edit-picture?ref=MeControl&refd=www.office.com
python===https://www.python.org/downloads/windows/
winrar===https://www.winrar.com.cn/
weixin===https://weixin.qq.com/
360===https://www.360.cn/
VMware-FusionDoc===https://docs.vmware.com/cn/VMware-Fusion/13/com.vmware.fusion.using.doc/GUID-F2874B79-A32A-4B83-914F-9838372D47CD.html
VMware-Fusion===https://support.broadcom.com/group/ecx/productdownloads?subfamily=VMware+Fusion
Vmware-workstation===https://www.vmware.com/products/desktop-hypervisor/workstation-and-fusion
tightvnc===https://www.tightvnc.com/
ultravnc===https://uvnc.com/downloads/ultravnc.html
obs-studio===https://obsproject.com/
VLC-Video===https://get.videolan.org/vlc/3.0.21/win64/vlc-3.0.21-win64.exe
7z===https://www.7-zip.org/download.html
virtualbox===https://www.virtualbox.org/wiki/Downloads
Linux常用命令的===https://gnu-linux.readthedocs.io/zh/latest/Chapter01/00_systemctl.html
todesk===https://www.todesk.com/
anydesk===https://anydesk.com/zhs
tensorrt===https://developer.nvidia.com/tensorrt-getting-started
wireshark===https://www.wireshark.org

邮箱
QQ邮箱===https://mail.qq.com
Google邮箱===https://mail.google.com
126邮箱===http://mail.126.com/
139邮箱===http://mail.10086.cn/
Outlook邮箱===https://outlook.live.com/
foxmail邮箱===https://www.foxmail.com/

社交
知乎===https://www.zhihu.com/explore
weibo===https://weibo.com
tieba===https://tieba.baidu.com/index.html
QQ空间===http://qzone.qq.com/

企业
国家知识产权局===https://www.cnipa.gov.cn/
天眼查===https://www.tianyancha.com/
企查查===https://www.qcc.com/
国家企业信用信息公示系统===http://www.gsxt.gov.cn/index.html
中国邮政局申诉网站===http://sswz.spb.gov.cn/
个人信用信息服务平台===https://ipcrs.pbccrc.org.cn
国家税务总局全国增值税发票查验平台===https://inv-veri.chinatax.gov.cn
国家食品药品监督管理总局===www.sda.gov.cn/WS01/CL0001/
全国劳动人事争议在线调解服务平台===http://tiaojie.12333.gov.cn/portal/
全国人社政务服务平台===https://www.12333.gov.cn/
全国消毒产品网上备案信息服务平台===https://credit.jdzx.net.cn/xdcp/loginPage/query?queryParams=info&getInput=%E6%AC%A1%E6%B0%AF%E9%85%B8%E6%B6%88%E6%AF%92%E7%89%87

生活旅游交通
天气===https://www.weather.com.cn
飞猪旅行===https://www.fliggy.com/
12306铁路官方网站===https://www.12306.cn/
携程网===https://www.ctrip.com/
马蜂窝===http://www.mafengwo.cn/

News
人民日报===http://paper.people.com.cn/rmrb/paperindex.htm
中国共产党网===http://www.12371.cn/
凤凰资讯===http://news.ifeng.com/
环球网===http://www.huanqiu.com/
参考消息===http://www.cankaoxiaoxi.com/
半月谈===http://www.banyuetan.org/
人民网===http://www.people.com.cn/
三联生活周刊===http://www.lifeweek.com.cn/
中国政府网===http://www.gov.cn/jrzg/
中国军网===http://www.81.cn/
中国经济网===http://www.ce.cn/
中国文明网===http://www.wenming.cn/
中国青年网===http://www.youth.cn/
南方网===http://www.southcn.com/
国际在线===http://www.cri.cn/index.html
法制网===http://www.legaldaily.com.cn/
中国警察网===http://www.cpd.com.cn/
海外网===http://www.haiwainet.cn/
新华网===http://www.xinhuanet.com/
央视网新闻===http://news.cntv.cn/
中国新闻网===https://www.chinanews.com/
凤凰军事===http://news.ifeng.com/mil/
腾讯新闻===https://www.qq.com/
网易新闻===https://news.163.com/

公安
湖南公安服务平台===https://fwpt.hnga.gov.cn
湖南一件事一次办===https://zwfw-new.hunan.gov.cn
上海一网通办===http://zwdt.sh.gov.cn
中华人民共和国公安部===https://www.mps.gov.cn/
公安部互联网交通安全综合服务管理平台===https://gab.122.gov.cn/m/index/
起点容易上瘾xidu===https://www.qidian.com/
QQ阅读容易上瘾xidu===http://book.qq.com/
番茄容易上瘾xidu===https://fanqienovel.com/
黄赌毒xidu===https://www.mps.gov.cn/

视频
腾讯===https://v.qq.com
优酷===https://v.youku.com
爱奇艺===https://www.iqiyi.com
抖音===https://v.douyin.com
快手===https://v.kuaishou.com
bilibili===https://www.bilibili.com
央视网===https://tv.cctv.com/
央广网===http://www.cnr.cn/
芒果TV===http://www.mgtv.com/
CCTV5===http://sports.cntv.cn/

慈善
义乌===https://ywscszh.cn
浙江===https://www.zcf.org.cn
山大===https://www.jjh.sdu.edu.cn

健康证
上海市从业人员预防性健康检查信息系统===https://jkz.sh.cn

血液
长沙血液中心===https://www.csxyzx.org
上海市血液中心===https://www.sbc.org.cn
无偿献血科普知识===https://www.bjredcross.org.cn/contents/gxbgzdwywjs/2023112918560.html
夏季献血应注意的事项===https://www.csxyzx.org/index.php/site/page/index/3325/category_id/10858/news_id/18339/ct_id/276/okcode/be0f94dcaff7be04ade79f87b0a33cbc0023d02e6a4f7aff3d2b27ac3ff74678
献血的人须知===https://www.sbc.org.cn/portal/article/index/id/9380/cid/25.html
献血注意事项及流程===https://www.sbc.org.cn/portal/article/index/id/9381/cid/25.html
二十四节气之霜降：献血能喝咖啡么？===https://www.sbc.org.cn/portal/article/index/id/10003/cid/25.html
二十四节气之寒露：献血前应该喝糖水还是盐水？===https://www.sbc.org.cn/portal/article/index/id/10002/cid/25.html
二十四节气之秋分：X医生谈血液丨献血后补充哪种食物才能快速恢复元气？===https://www.sbc.org.cn/portal/article/index/id/10001/cid/25.html
献血常识 上海市血液中心===https://www.sbc.org.cn/portal/list/index/id/25.html?fuid=19&page=2
献血前后应注意些什么？===https://www.sbc.org.cn/portal/article/index/id/6969/cid/25.html
献血丢失的血液需要多久能恢复?需要“静养”、“进补”吗？===https://www.sbc.org.cn/portal/article/index/id/6968/cid/25.html
二十四节气之秋分：X医生谈血液丨献血后补充哪种食物才能快速恢复元气？===https://www.sbc.org.cn/portal/article/index/id/10001/cid/25.html
瘦子要如何健康地增重？|丁香医生===https://dxy.com/article/6262
苦恼，怎么吃都长不胖？！瘦子如何成功增重20斤？|丁香医生===https://dxy.com/article/79507
想增肌增重？瘦子们看过来|丁香医生===https://dxy.com/article/3426

Mac
MacbookPro13===https://support.apple.com/zh-cn/111339
mac重装===https://support.apple.com/zh-cn/guide/mac-help/mchlp1599/10.15/mac/10.15
tuxera===https://ntfsformac.tuxera.com/
西数paragon_ntfsmac===https://support-eu.wd.com/app/answers/detailweb/a_id/34871/~/external-drive%3A-paragon-ntfs-driver-for-mac
homebrew===https://docs.brew.sh/

dictionary
欧路===https://www.eudic.net/
mdict===https://www.mdict.cn/wp/?lang=zh

日历
日历网===https://www.rili.com.cn/wannianli/
日历===https://wannianrili.bmcx.com/

绘画
阿里通义万相===https://tongyi.aliyun.com/wanxiang
腾讯智影===https://zenvideo.qq.com/image/create
znrpa===https://ai.znrpa.com/midjourney
kbzu===https://bzu.cn/auth
tusiart===https://tusiart.com/
liblib===https://www.liblib.art/sd
nvidia===https://www.nvidia.cn/studio/canvas/
yunjie===https://www.yunjie.art/
ai-bot===https://ai-bot.cn/best-ai-painting-tools/
baidu文心一格===https://yige.baidu.com/
StableDiffusion===https://github.com/Stability-AI/StableDiffusion
stable-diffusion===https://github.com/CompVis/stable-diffusion
奇域===https://www.qiyuai.net/
秒画商汤呢===https://miaohua.sensetime.com/generate
whee===https://www.whee.com/
触手===https://acgnai.art/create/profession
即梦===https://jimeng.jianying.com
提示词===https://www.eudic.net/v4/en/app/download

音乐
QQ音乐===http://y.qq.com/
酷狗音乐===http://www.kugou.com/

合集
hao123===https://www.hao123.com/?from=offline_host

'''

def removekongge(i):
    i = i.strip()
    if len(i)==0:
        return ""
    while i[0]==' ':
        i = i[1:]
    while i[-1]==' ':
        i = i[:-1]
    return i

def parseTxt(textarea_content):
    result = []
    lines = textarea_content.split("\n")
    modify = []
    for i in lines:
        i = removekongge(i.strip())
        if len(i)==0:
            modify.append('\n')
            continue
        i = regular.sub('=?=?=? *http', "===http", i)
        modify.append(i + '\n')
        if '===' not in i:
            result.append([i, []])
            continue
        j = i.split('===')
        j[0] = removekongge(j[0])
        j[1] = removekongge(j[1])
        try:
            result[-1][1].append([j[0], j[1]])
        except:
            result[-1][1].append([j[0], ""])
            continue
    return result, modify

filemutex = Semaphore(value=1)
def getfiledata(request):
    global path, textarea_content_predefined, filemutex, kshoucangmutex, kshoucangmutexpianduan
    # body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    # req = json.loads(body)

    # req = request.POST.dict()
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    get = json.loads(getusername(request).content)
    # basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    if get['ret'] > 0:
        basepath = basepath.replace("/article/", f"/people/{get['urlmail']}/")

    file = os.path.join(basepath, 'commonuse.txt')
    if not os.path.exists(file):
        with open(file, 'w', encoding='utf-8') as obj:
            obj.write(textarea_content_predefined + '\n')
            app = '\n收藏\n'
            apppianduan = '\n片段\n'
            result, modify = parseTxt(textarea_content_predefined + app + apppianduan)
            return JsonResponse( { "ret": True, 'textarea_content': textarea_content_predefined, \
                                  'result':result[:-2], 'result2':result[-2:] }, safe = False)

    filepath = os.path.join(basepath, 'kshoucang.json')
    kshoucangmutex.acquire()
    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='utf-8') as obj:
            json.dump([], obj, indent=2, ensure_ascii=False)
    delet = []
    with open(filepath, 'r', encoding='utf-8') as obj:
        try:
            kshoucangJson = json.load(obj)
        except:
            kshoucangJson = []
        for i in kshoucangJson:
            ij = i.split("?plan=")[-1]
            if not os.path.exists(ij):
                delet.append(i)
        for i in delet:
            kshoucangJson.remove(i)
        app = '\n'.join(kshoucangJson)
        app = '\n收藏\n' + app

    if len(delet)!=0:
        with open(filepath, 'w', encoding='utf-8') as obj:
            json.dump(kshoucangJson, obj, indent=2, ensure_ascii=False)
    kshoucangmutex.release()

    filepathPD = os.path.join(basepath, 'kshoucangpianduan.json')
    kshoucangmutexpianduan.acquire()
    if not os.path.exists(filepathPD):
        with open(filepathPD, 'w', encoding='utf-8') as obj:
            json.dump([], obj, indent=2, ensure_ascii=False)
    delet = []
    with open(filepathPD, 'r', encoding='utf-8') as obj:
        try:
            kshoucangpianduanJson = json.load(obj)
        except:
            kshoucangpianduanJson = []
        for i in kshoucangpianduanJson:
            ij = i.split("?plan=")[-1]
            if not os.path.exists(ij):
                delet.append(i)
        for i in delet:
            try:
                kshoucangpianduanJson.remove(i)
            except:
                continue
        apppianduan = '\n'.join(kshoucangpianduanJson)
        apppianduan = '\n片段\n' + apppianduan
    if len(delet)!=0:
        with open(filepathPD, 'w', encoding='utf-8') as obj:
            json.dump(kshoucangpianduanJson, obj, indent=2, ensure_ascii=False)
    kshoucangmutexpianduan.release()

    with open(file, 'r', encoding='utf-8') as obj:
        text = obj.read()
        result, modify = parseTxt(text.strip())

        text2 = text + "\n" + app + '\n' + apppianduan
        __result2, modify___ = parseTxt(text2.strip())
    filemutex.acquire()
    with open(file, 'w', encoding='utf-8') as obj:
        obj.write(''.join(modify))
    filemutex.release()

    return JsonResponse( { "ret": True, 'textarea_content': text, 'result':__result2[:-2], 'result2':__result2[-2:]}, safe = False)

def submitAddwebsite(request):
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
            basepath = basepath.replace("/article/", f"/people/{get['mail']}/")
    
    file = os.path.join(basepath, 'commonuse.txt')
    result, modify = parseTxt(req['textarea_content'])
    filemutex.acquire()
    with open(file, 'w', encoding='utf-8') as obj:
        obj.write(''.join(modify))
    filemutex.release()
    return JsonResponse( { "ret": True, 'result':result}, safe = False)

def getbingimg(request):
    global path
    kasepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    file = os.path.join(kasepath, 'everydayimg.txt')
    result = ""
    with open(file, 'r', encoding='utf-8') as obj:
        result = obj.read().strip()
    return JsonResponse( { "ret": True, 'result':result}, safe = False)

def mailsend(mail):
    # https://docs.python.org/3.12/library/smtplib.html#module-smtplib
    # https://docs.python.org/3.12/library/email.examples.html#email-examples
    # https://wx.mail.qq.com/list/readtemplate?name=app_intro.html#/agreement/authorizationCode
    msg = EmailMessage()
    msg.set_content(f'数据下载请求：{mail}\n\n\nhttp://zoujiu.com.cn')
    msg['Subject'] = "zoujiu.com.cn数据下载请求"
    msg['From'] = '1069679911@qq.com'
    msg['To'] = "1069679911@qq.com"
    # smtplib.SMTP()
    smpt = smtplib.SMTP_SSL("smtp.qq.com", port=465)
    # smpt.connect("smtp.qq.com", port=465)
    smpt.login(user="1069679911@qq.com", password='qqaymrpfctvlbcif')
    # smpt.sendmail()
    try:
        smpt.send_message(msg)
    except:
        return '------'
    # smpt.close()
    smpt.quit()
    return

mutexdownload = Semaphore(value=1)
def downloadall(request):
    global path, mutexdownload
    body = request.body
    # https://docs.djangoproject.com/zh-hans/5.1/ref/request-response/
    req = json.loads(body)

    # req = request.POST.dict()
    basepath = os.sep.join(deepcopy(path).split(os.sep)[:-2]) + os.sep
    file = os.path.join(basepath, 'download.txt')
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
    if basepath[-1]==os.sep:
        asepath = basepath[:-1]
    else:
        asepath = basepath
    receivemail = req['receivemail']

    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as obj:
            for i in obj.readlines():
                if receivemail in i:
                    return JsonResponse( { "ret" : 2} , safe = False)

    postDate = datetime.fromtimestamp(time.time() +timezone).isoformat()[:19].replace(":", "_")
    postDate = postDate.replace("T", " ")
    savepath = os.path.join(basepath, 'download.zip')

    mutexdownload.acquire()
    with open(file, 'a+', encoding='utf-8') as obj:
        obj.write(f"{receivemail}==;<=={asepath}==;<=={savepath}==;<=={postDate}\n")
    mutexdownload.release()
    mailsend(f"{receivemail}==;<=={asepath}==;<=={savepath}==;<=={postDate}")
    
    cmd = f"cd {asepath} && nohup zip -r -q {savepath} {asepath} &"
    # os.system(cmd)
    return JsonResponse( { "ret" : 10} , safe = False)