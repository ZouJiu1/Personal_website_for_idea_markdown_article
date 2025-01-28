import os
import json
import re
import time
import shutil
import numpy as np
from copy import deepcopy as dcp

def confirm():
    csdn = r'/home/admin/vue-project/article/csdn_spider_selenium/article'
    zhihu = r'/home/admin/vue-project/article/zhihu_spider_selenium/article'
    csdnlist = os.listdir(csdn)
    zhihulist = os.listdir(zhihu)
    ret = []
    for i in csdnlist:
        ic = dcp(i)
        for j in zhihulist:
            jc = dcp(j)
            if '.txt' in i or '.txt' in j:
                continue
            num = 0
            i = re.sub(r'_.._', "", i)
            j = re.sub(r'_.._', "", j)
            i = re.sub(r'_', '', i)
            i = re.sub(r'-', '', i)
            i = re.sub(r'\d', '', i)
            i = re.sub(r'\.', '', i)
            i = re.sub(r'\s', '', i)
            i = re.sub(r' ', '', i)
            j = re.sub(r'_', '', j)
            j = re.sub(r'-', '', j)
            j = re.sub(r'\d', '', j)
            j = re.sub(r'\.', '', j)
            j = re.sub(r'\s', '', j)
            j = re.sub(r' ', '', j)
            if '属地' in j:
                j = j[:-4]
            if '部分'in i[-4:]:
                i = i[:-4]
            if i[:int(len(i)*0.9)]==j[:int(len(j)*0.9)]: # or i[:10]==j[:10]
                ret.append([ic, jc])
            # leni = len(i)
            # lenj = len(j)
            # for ic in i:
            #     for jc in j:
            #         if ic==jc:
            #             num += 1
            # if abs(leni - lenj) < 4 and num / max(leni, lenj) > 0.7:
            #     ret.append([i, j])
    for i, j in ret:
        # shutil.rmtree(os.path.join(csdn, i))
        os.system("rm -rf %s"%os.path.join(csdn, i))
        tm = i[:22]
        id = -1
        try:
            id = j.index("_IP")
        except:
            pass
        if id >= 0:
            jc = j[:id]
        else:
            jc = j
        jc = tm + jc[16:]
        if jc[-1]=='_':
            jc = jc[:-1]
        os.system("cp -rf %s %s"%(os.path.join(zhihu, j), os.path.join(csdn, jc)))
        # shutil.copytree(os.path.join(zhihu, j), os.path.join(csdn, jc))
    k = 0

def idtran():
    csdn = r'/home/admin/vue-project/article/csdn_spider_selenium/article'
    zhihu = r'/home/admin/vue-project/article/zhihu_spider_selenium/article'
    savepath = r'/home/admin/vue-project/article/idtranslate.json'
    csdnlist = os.listdir(csdn)
    zhihulist = os.listdir(zhihu)
    ret = {'zhihu2id': {}, 'csdn2id':{}, 'id2zhihu':{}, "id2csdn":{}}
    for i in csdnlist:
        # nr = np.random.randint(1000000000000000000)
        if len(i) < 2:
            continue
        if i[0]!='2':
            i = '2099-00-00_空格_00_%d_%d_'%(np.random.randint(10, 60), np.random.randint(10, 60)) + i
        nr = i[:22].replace("_空格_", "").replace("-", "").replace("_", "")
        nr = str(nr) + str(int(time.time() + np.random.randint(100000000)))
        ret['csdn2id'][i] = nr
        ret['id2csdn'][nr] = i
        # time.sleep(1)
        
    for i in zhihulist:
        # nr = np.random.randint(1000000000000000000)
        if len(i) < 2:
            continue
        if i[0]!='2':
            i = '2099-00-00_00_%d_'%(np.random.randint(10, 60)) + i
        nr = i[:16].replace("_空格_", "").replace("-", "").replace("_", "")
        nr = str(nr) + str(int(time.time() + np.random.randint(100000000)))
        ret['zhihu2id'][i] = nr
        ret['id2zhihu'][nr] = i
        # time.sleep(1)
    ww = len(ret['zhihu2id'])
    kk = len(ret['id2zhihu'])
    assert len(ret['zhihu2id'])==len(ret['id2zhihu'])
    assert len(ret['csdn2id'])==len(ret['id2csdn'])
    assert set(list(ret['zhihu2id'].values()))==set(list(ret['id2zhihu'].keys()))
    assert set(list(ret['csdn2id'].values()))==set(list(ret['id2csdn'].keys()))
    with open(savepath, 'w', encoding='utf-8') as obj:
        json.dump(ret, obj, indent=2, ensure_ascii=False)
    # k = 0

if __name__=="__main__":
    confirm()
    idtran()