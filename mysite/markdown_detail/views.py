import os
import re
from django.http import HttpResponse
# from rest_framework.response import Response
# from rest_framework import status
from django.http import JsonResponse
import markdown2
import numpy as np
import time
from datetime import datetime
import json

import sys
sys.path.append(os.path.abspath(__file__ + "/../../"))
from manage import timezone, kseamutex
# from csdn.views import kseamutex
from threading import Semaphore
from copy import deepcopy

def remove_code(inp):
    collect = []
    start = 0
    tmp = []
    k = 0
    while "```" in inp[start:]:
        if len(tmp)==2:
            rand = "===" + str(np.random.randint(999999999999)) + str(time.time()) + "==="
            txt = inp[tmp[0] : tmp[1] + 3]
            collect.append([rand, txt[3:-3]])
            inp = inp.replace(txt, rand)
            tmp = []
            k = 0
            start = 0
        try:
            k = inp[start:].index("```")
            tmp.append(k + start)
        except:
            pass
        start = k + 3 
    return inp, collect

choyang = list('《《《》》》》》》《《《？？；；；；；；；；、、、、、、、、）））（（（（（？？？？？】】】【【【ABCDEFGHIJKLMNOPQRSTUVWXYZ'.upper())
choyang_Java = list('《《《》》》》》》《《《？？；；；；；；；；、、、、、、、、）））（（（（（？？？？？】】】【【【')

def java_sub_mail(inp):
    txt = inp[0]
    return f"<span style=\"color: rgb(0, 119, 170);font-weight:600;\">{txt}</span>"

def remove_marked_cpp(inp, type=""):
    global choyang
    left = 0
    right = 0
    ll = []
    rr = []
    collect = []
    i = 0
    while i < len(inp)-1:
    # for i in range(len(inp) - 1):
        if inp[i]=='/' and inp[i+1]=='*':
            left += 1
            ll.append(i)
        elif inp[i]=='*' and inp[i+1]=='/':
            right += 1
            rr.append(i)
        if left + right!=0 and left==right:
            # rand = np.random.choice(choyang, rr[-1] - ll[0] + 1)
            rand = np.random.choice(choyang, max(rr[-1] - ll[0] + 1, 100))
            rand = ''.join(rand) + '】'
            txt = inp[ll[0] : rr[-1] + 2]
            if type!='java':
                retxt = "<span style=\"color: slategray;font-weight:600;\">"+ txt.replace("<", "<span style=\"font-weight:600;\"><</span>") + "</span>"
            else:
                tmp = txt.replace("<", "<span style=\"font-weight:600;\"><</span>")
                tmp = re.sub(r'@[\w\d]* ?', java_sub_mail, tmp)
                retxt = "<span style=\"color: slategray;font-weight:600;\">"+ tmp + "</span>"
            collect.append([rand, retxt])
            inp = inp.replace(txt, rand)
            i = inp.index(rand) + len(rand) - 1
            # kk = inp[:i]
            # kkk = inp[i:]
            left = 0
            right = 0
            ll = []
            rr = []
        i += 1

    return inp, collect

def remove_marked_python(inp):
    global choyang
    left = 0
    right = 0
    ll = []
    rr = []
    collect = []
    i = 0
    while i < len(inp)-2:
    # for i in range(len(inp) - 2):
        if (inp[i]=='\'' and inp[i+1]=='\'' and inp[i+2]=='\'') or \
            (inp[i]=='\"' and inp[i+1]=='\"' and inp[i+2]=='\"'):
            if left==0:
                left += 1
                ll.append(i)
            else:
                right += 1
                rr.append(i)
        if left + right!=0 and left==right:
            # rand = np.random.choice(choyang, rr[-1] - ll[0] + 2)
            rand = np.random.choice(choyang, max(rr[-1] - ll[0] + 2, 100))
            rand = ''.join(rand) + '】'
            txt = inp[ll[0] : rr[-1] + 3]
            retxt = f"<span style=\"color:rgb(102, 153, 0); font-weight:600;\">{txt[:3]}</span>" + \
                "<span style=\"color: slategray;font-weight:600;\">"+ \
                txt[3:-3].replace("<", "<span style=\"font-weight:600;\"><</span>") + \
                    "</span>" + \
                f"<span style=\"color:rgb(102, 153, 0); font-weight:600;\">{txt[-3:]}</span>"
            collect.append([rand, retxt])
            inp = inp.replace(txt, rand)
            i = inp.index(rand) + len(rand) - 1
            left = 0
            right = 0
            ll = []
            rr = []
        i += 1

    return inp, collect

def remove_marked_javascript(inp):
    global choyang
    left = 0
    right = 0
    ll = []
    rr = []
    collect = []
    i = 0
    while i < len(inp)-2:
    # for i in range(len(inp) - 2):
        if left==0 and (inp[i]=='<' and inp[i+1]=='!' and inp[i+2]=='-' \
                        and (i+3!=len(inp)-1 and inp[i+3]=='-')):
            left += 1
            ll.append(i)
        elif right==0 and inp[i]=='-' and inp[i+1]=='-' and inp[i+2]=='>':
            right += 1
            rr.append(i)
        if left + right!=0 and left==right:
            # rand = np.random.choice(choyang, rr[-1] - ll[0] + 2)
            rand = np.random.choice(choyang, max(rr[-1] - ll[0] + 2, 100))
            rand = ''.join(rand) + '】'
            txt = inp[ll[0] : rr[-1] + 3]
            collect.append([rand, \
                "<span style=\"color: slategray;font-weight:600;\">"+ \
                txt.replace("<", "<span style=\"font-weight:600;\"><</span>") + "</span>"])
            inp = inp.replace(txt, rand)
            i = inp.index(rand) + len(rand) - 1
            left = 0
            right = 0
            ll = []
            rr = []
        i += 1

    return inp, collect

def remove_doublemarked_cpp(inp):
    global choyang
    collect = []
    lines = inp.split('\n')
    newline = []
    for l in lines:
        i = 0
        while i < len(l)-1:
        # for i in range(len(l) - 1):
            if l[i]=='/' and l[i+1]=='/':
                kk = 0
                for ij in range(i-1, -1,-1):
                    if l[ij]=='\'' or l[ij]=='\"':
                        kk += 1
                        break
                for ij in range(i+1, len(l), 1):
                    if l[ij]=='\'' or l[ij]=='\"':
                        kk += 1
                        break
                if kk==2:
                    i += 1
                    continue
                # rand = np.random.choice(choyang, len(l) - i - 1)
                rand = np.random.choice(choyang, max(len(l) - i - 1, 100))
                rand = ''.join(rand) + '】'
                txt = l[i:]
                retxt = "<span style=\"color: slategray;font-weight:600;\">"+ txt.replace("<", "<span><</span>") + "</span>"
                collect.append([rand, retxt])
                l = l.replace(txt, rand)
                i = l.index(rand) + len(rand) - 1
                break
            i += 1
        newline.append(l)
    inp = "\n".join(newline)
    return inp, collect

def remove_doublemarked_python(inp):
    global choyang
    collect = []
    lines = inp.split('\n')
    newline = []
    for l in lines:
        i = 0
        while i < len(l)-1:
        # for i in range(len(l) - 1):
            if l[i]=='#':
                kk = 0
                for ij in range(i-1, -1,-1):
                    if l[ij]=='\'' or l[ij]=='\"':
                        kk += 1
                        break
                for ij in range(i+1, len(l), 1):
                    if l[ij]=='\'' or l[ij]=='\"':
                        kk += 1
                        break
                if kk==2:
                    i += 1
                    continue
                # rand = np.random.choice(choyang, len(l) - i - 1)
                rand = np.random.choice(choyang, max(len(l) - i - 1, 100))
                rand = ''.join(rand) + '】'
                txt = l[i:]
                retxt = "<span style=\"color: slategray;font-weight:600;\">"+ txt.replace("<", "<span><</span>") + "</span>"
                collect.append([rand, retxt])
                l = l.replace(txt, rand)
                break
            i += 1
        newline.append(l)
    inp = "\n".join(newline)
    return inp, collect

def addback_common(markdown, collect):
    for i in collect:
        markdown = markdown.replace(i[0], i[1])
    return markdown

def remove_yinhao_cpp(inp):
    # global choyang
    # def replace_sub_yinhao(txt):
    #     # print(txt[0])
    #     # print(txt)
    #     return f"<span style='color:rgb(102, 153, 0);font-weight:600;'>{str(txt[0])}</span>"
    # inp = re.sub(r'''[\'\"][^'"]*[\'\"]''', replace_sub_yinhao, inp)
    
    global choyang
    left = 0
    right = 0
    ll = []
    rr = []
    collect = []
    lines = inp.split('\n')
    newline = []
    for l in lines:
        i = 0
        while i < len(l):
        # for i in range(len(l)):
            if l[i]=='\'' or l[i]=='\"':
                if i > 0 and l[i-1]=='\\':
                    i += 1
                    continue
                if left==0:
                    left += 1
                    ll.append(i)
                else:
                    right += 1
                    rr.append(i)
            if left + right!=0 and left==right:
                # rand = np.random.choice(choyang, rr[-1] - ll[0])
                rand = np.random.choice(choyang, max(rr[-1] - ll[0], 100))
                rand = ''.join(rand) + '】'
                txt = l[ll[0] : rr[-1] + 1]
                collect.append([rand, "<span style=\"color: rgb(102, 153, 0);font-weight:600;\">"+ txt + "</span>"])
                l = l.replace(txt, rand)
                i = l.index(rand) + len(rand) - 1
                left = 0
                right = 0
                ll = []
                rr = []
            i += 1
        newline.append(l)
        
    inp = "\n".join(newline)

    return inp, collect

def splited_js_css(inp):
    pass
    # left = 0
    # right = 0
    # for i in range(len(inp)):
    #     if inp[i:i+2**3]=='<script>':

dic = []
    
def replace_sub_html2(txt):
    global dic, choyang
    inp = txt[0]
    if len(inp)==0:
        return ""
    left = []
    for i in range(len(inp)):
        if inp[i]=='\'' or inp[i]=='\"':
            left.append(i)
    rand = np.random.choice(choyang, 100)
    rand = ''.join(rand) + '】】】'
    txt = inp[left[0]:left[-1]+1]
    txt__ = f"<span style=\"color:slategray;font-weight:600;\">{inp[left[0]]}</span>" + \
        f"<span style=\"color: rgb(0, 119, 170);font-weight:600;\">{inp[left[0]+1:left[-1]]}</span>" + \
        f"<span style=\"color:slategray;font-weight:600;\">{inp[left[-1]]}</span>"
    dic.append([rand, txt__])
    inp = inp.replace(txt, rand)
    return inp
    
def replace_sub_html3(txt):
    inp = txt[0]
    if len(inp)==0:
        return ""
        
    return f"<span style='color:rgb(102, 153, 0);font-weight:600;'>{inp[:-1]}</span>" + \
        f"<span style=\"color:slategray;font-weight:600;\">=</span>"
    
def replace_sub_html1(txt):
    global dic
    # print(txt[0])
    # print(txt)
    inp = txt[0]
    # inp_yinhao = re.findall(r'''= *[\'\"][\w \d=\.\?\+\t\r\-\(\)]*[\'\"]''', inp)
    inp_yinhao_ = re.sub(r'''= *[\'\"][\w :\#;%/\d=\.\?\+\t\r\-\(\)]*[\'\"]''', replace_sub_html2, inp)
        
    # inp_re = re.findall(r''' [\w \d=\.\?\+\t\r\-\(\)]*=''', inp_yinhao_)
    inp_re_ = re.sub(r''' [\w \d=\#:;@%/\'\"\.\?\+\t\r\-_\(\)]*=''', replace_sub_html3, inp_yinhao_)
    try:
        if inp_re_[:5]=='<span':
            id = inp_re_[2:].index("<span") + 2
        else:
            id = inp_re_.index("<span")
        inp_re_ = f"<span style=\"color:slategray;font-weight:600;\"><</span>" + \
            f"<span style=\"color: rgb(153, 0, 85);font-weight:600;\">{inp_re_[1:id]}</span>"+\
            inp_re_[id:-1] + f"<span style=\"color:slategray;font-weight:600;\">></span>"
    except:
        pass
    for i in dic:
        inp_re_ = inp_re_.replace(i[0], i[1])
    dic = []
    if inp==inp_re_:
        inp_re_ = f"<span style=\"color:slategray;font-weight:600;\"><</span>" + \
            f"<span style=\"color: rgb(153, 0, 85);font-weight:600;\">{inp_re_[1:-1]}</span>"+\
                f"<span style=\"color:slategray;font-weight:600;\">></span>"
    return inp_re_

dic0 = []

def replace_sub_html0(txt):
    global dic0
    inp = txt[0]
    retxt = f"<span style=\"color:slategray;font-weight:600;\"><</span>" + \
            f"<span style=\"color: rgb(153, 0, 85);font-weight:600;\">{inp[1:-1]}</span>"+\
                f"<span style=\"color:slategray;font-weight:600;\">></span>"
    rand = np.random.choice(choyang, 100)
    rand = ''.join(rand) + '】】】'
    dic0.append([rand, retxt])
    return rand
            
def addSpan(precode):
    global dic0, choyang, choyang_Java
    firstline = precode.split("\n")[0].lower()
    existFirst = True
    if len(firstline) == 0:
        existFirst = False
    type = ""
    if existFirst:
        while ' ' == firstline[0]:
            firstline = firstline[1:]
        if 'c++' in firstline or 'c plus plus' in firstline or 'cpp' in firstline or 'c' ==firstline[0]:
            type = 'c++'
        elif 'python' in firstline:
            type = "python"
        elif 'javascript' in firstline or 'html' in firstline:
            type = 'javascript'
        elif 'java' in firstline:
            type = 'java'
    else:
        if "#include" in precode or 'vector' in precode or 'using namespace' in precode or 'cout' in precode or 'cin' in precode: 
            type = "c++"
        elif "def " in precode or "print" in precode or "):" in precode or \
            ('import' in precode and 'as' in precode):
            type = "python"
        elif "document" in precode or "</style>" in precode or "</script>" in precode or \
            "</div>" in precode or "</video>" in precode or 'function()' in precode or \
            'getElementById' in precode or '</html>' in precode:
            type = "javascript"
        elif 'package' in precode or 'java.io' in precode or 'java.' in precode or \
            'extends' in precode:
                type = 'java'
    
        # print(yinhao_collect)
    numberCol = []
    def replace_number(txt):
        # print(txt[0])
        # print(txt)
        inp = txt[0]
        if inp in ['char16_t', 'char32_t','uint8_t','uint16_t','uint32_t','uint64_t','int8_t',\
                'int16_t', 'int32_t', 'int64_t']:
            return inp
        if type=='java':
            rand = np.random.choice(choyang_Java, 100)
        else:
            rand = np.random.choice(choyang, 100)
        rand = ''.join(rand) + '】】】'
        # rand = '；】】】'*30
        inp = "<span style=\"color:#990055;font-weight:600;\">%s</span>"%str(inp)
        numberCol.append([rand, inp])
        return rand
    # print(precode)
    
    cppInclude = []
    def replace_include(txt):
        i = txt[0]
        cppStyle = []
        incl = []
        # marked = -1
        for ij in range(len(i)):
            if (i[ij]=='<' or i[ij]=='>' or i[ij]=='\"' or i[ij]=='\'') and len(cppStyle) < 2:
                cppStyle.append(ij)
            # elif i[ij]=='/' and ij!=len(i)-1 and i[ij+1]=='/' and marked < 0:
            #     marked = ij
            elif (i[ij]=='#' or i[ij]=='e') and len(incl) < 2:
                incl.append(ij) 
        if len(cppStyle)==2:
            i = i[:cppStyle[0]] + f"<span style='color:rgb(102, 153, 0);font-weight:600;'>{i[cppStyle[0]]}</span>" + '<span style=\"color:rgb(102, 153, 0);font-weight:600;\">' + i[cppStyle[0] + 1:cppStyle[1] + 1] + '</span>' + i[cppStyle[1] + 1:]
        if len(incl)==2:
            i = i[:incl[0]] + '<span style=\"color:rgb(153, 0, 85);font-weight:600;\">' + i[incl[0]] + '</span>' + '<span style=\"color: rgb(0, 119, 170);font-weight:600;\">' + i[incl[0]+1:incl[1] + 1] + '</span>' + i[incl[1] + 1:]
        rand = np.random.choice(choyang, 100)
        rand = ''.join(rand) + '】】】'
        cppInclude.append([rand, i])
        return rand

    Js_html = []
    Js_color = []
    if type=='c++':
        precode, collect = remove_marked_cpp(precode)
        precode, d_collect = remove_doublemarked_cpp(precode)
        precode = re.sub('#include *[<\"\']\w*.?\w*[>\"\']', replace_include, precode)
        precode, yinhao_collect = remove_yinhao_cpp(precode)
        precode = re.sub(r"-?[\d]*\.?[\d]+(?!\d?_t|\s*{)", replace_number, precode)
    elif type=="python":
        precode, P_collect = remove_marked_python(precode)
        precode, P_d_collect = remove_doublemarked_python(precode)
        precode, yinhao_collect = remove_yinhao_cpp(precode)
        precode = re.sub(r"-?[\d]*\.?[\d]+", replace_number, precode)
    elif type=="javascript":
        precode, Js_collect = remove_marked_javascript(precode)
        precode, Js_Js_collect = remove_marked_cpp(precode)
        precode, Js_d_collect = remove_doublemarked_cpp(precode)

        # precode_html, precode_javascript, precode_style = splited_js_css(precode)
        precode = re.sub(r'''</\w+>''', replace_sub_html0, precode)
        precode = re.sub(r'''<[a-zA-Z][\w\s\d=:%"@/\\ \.\+\n\t\r\-\#\(\);']*/?>''', replace_sub_html1, precode)
        for i in dic0:
            precode = precode.replace(i[0], i[1])
        dic0 = []
        
        spl = precode.split("\n")
        for id, i in enumerate(spl):
            if '<span' in i:
                rand = np.random.choice(choyang, 160)
                rand = ''.join(rand) + '】】】'
                Js_html.append([rand, spl[id]])
                spl[id] = rand
        precode = "\n".join(spl)
        
        precode, yinhao_collect = remove_yinhao_cpp(precode)
        
        def replace_number_color(text):
            inp = text[0]
            rand = np.random.choice(choyang, 100)
            rand = ''.join(rand) + '】】】'
            Js_color.append([rand, f'<span>{inp}</span>'])
            return rand
            
        precode = re.sub(r"#[a-f0-9A-F][a-f0-9A-F][a-f0-9A-F][a-f0-9A-F][a-f0-9A-F][a-f0-9A-F]", \
            replace_number_color, precode)
        
        precode = re.sub(r"-?[\d]*\.?[\d]+", replace_number, precode)
    elif type=='java':
        precode, collect = remove_marked_cpp(precode, type='java')
        precode, d_collect = remove_doublemarked_cpp(precode)
        precode, yinhao_collect = remove_yinhao_cpp(precode)
        precode = re.sub(r"(?<!\w)-?[\d]*\.?[\d]+", replace_number, precode)
    
    allOperator = []
    file = []
    def replace_sub_operator(txt):
        inp = txt[0]
        file.append(inp)
        # np.random.seed(0)
        rand = np.random.choice(choyang, 100)
        rand = ''.join(rand) + '】】】'
        inp = f"<span style=\"color: rgb(154, 110, 58);font-weight:600;\">{inp}</span>"
        allOperator.append([rand, inp])
        return rand

    precode = re.sub(r'[\+\*/%&\^!<>\?=\|]', replace_sub_operator, precode)

    splited = precode.split("\n")
    extern = []
    for ik, i in enumerate(splited):
        if type=='c++':
            first = 0
            while first < len(i) and i[first]==' ':
                first += 1
            # i = i.replace(">>", "<span style='font-weight:600;'>>></span>").replace("<<", "<span style='font-weight:600;'><<</span>")
            # leftkuohao = re.findall(r" *[\w_\-\_\d]+ *\s*\(", i)
            # leftda = re.findall(r" *[\w_\-\_\d]+ *\s*\{", i)
            # for ilf in leftkuohao:
            #     ilf = ilf.replace("(", "")
            #     i = i.replace(ilf, "<span style=\"color:rgb(221, 74, 104);font-weight:600;\">%s</span>" % ilf)
            # for ilf in leftda:
            #     ilf = ilf.replace("{", "")
            #     i = i.replace(ilf, "<span style=\"color:rgb(221, 74, 104);font-weight:600;\">%s</span>" % ilf)

            def cpp_sub_xiaokuohao(text):
                inp = text[0]
                return f"<span style=\"color:rgb(221, 74, 104);font-weight:600;\">{inp[:-1]}</span>" + \
                    f"<span style=\"color: slategray;font-weight:600;\">(</span>"
            i = re.sub(r" *[\w_\-\_\d]+ *\s*\(", cpp_sub_xiaokuohao, i)
            
            def cpp_sub_dakuohao(text):
                inp = text[0]
                return f"<span style=\"color:rgb(221, 74, 104);font-weight:600;\">{inp[:-1]}</span>" + \
                    "<span style=\"color: slategray;font-weight:600;\">{</span>"
            i = re.sub(r" *[\w_\-\_\d]+ *\s*\{", cpp_sub_dakuohao, i)
            # https://learn.microsoft.com/zh-cn/cpp/c-language/c-keywords?view=msvc-170
            # https://learn.microsoft.com/zh-cn/cpp/cpp/keywords-cpp?view=msvc-170
            keyword = ['alignas', 'alignof', 'asm', 'auto', 'bool', 'break', 'case', 'catch', 'try',\
                'char', 'char16_t', 'char32_t', 'class', 'const', 'const_cast', 'constexpr',\
                'continue', 'decltype', 'default', 'delete', 'do', 'double', 'dynamic_cast', \
                'else', 'enum', 'explicit', 'export', 'extern', 'false', 'float','for', 'friend',\
                'goto', 'if', 'inline', 'int', 'long', 'long long', 'mutable', 'namespace', \
                'new', 'noexcept', 'nullptr', 'operator', 'private', 'protected', 'public',\
                'register', 'reinterpret_cast', 'return', 'short', 'string', 'signed', 'switch', 'template', \
                'this', 'thread_local', 'throw', 'true', 'try', 'typedef', 'typeid', 'typename', \
                'true', 'typedef', 'typeid', 'typename', 'union', 'unsigned', 'using', 'virtual', \
                'void', 'volatile', 'wchar_t', 'while','uint8_t','uint16_t','uint32_t','uint64_t','int8_t',\
                'int16_t', 'int32_t', 'int64_t']
            keyword = list(set(keyword))
            for ri in keyword:
                i = re.sub(r"(?<!\w)%s(?!\w)"%ri, "<span style=\"color:rgb(0, 119, 170);font-weight:600;\">%s</span>"%ri, i)

            # i = i.replace('{', "<span style=\"color:rgb(153, 153, 153);font-weight:600;\">{</span>")
            # i = i.replace('}', "<span style=\"color:rgb(153, 153, 153);font-weight:600;\">}</span>")
            # i = i.replace('}', "<span style=\"color:rgb(153, 153, 153);font-weight:600;\">}</span>")
            # symbol = ['&', "<", ">", '=', '-', '/', '+', '\\', '%', '.', '!', '?', \
            #     '`', '~', '!', '@', '#', '$', '^', '*']
            # i = i.replace("rgb(", "rgbkuohao")
            # i = i.replace(");font", "kuohao;font")
                
            # symbol = ['{', '}', '[', ']', '~', '`', '!', '@', '$', '%', '^', '&', '*', \
            #     '?', '.', '|']
            # for ri in symbol:
            #     if ri in i:
            #         i = i.replace(ri, "<span style=\"color:rgb(153, 153, 153);font-weight:600;\">%s</span>"%ri)

            # i = i.replace("rgbkuohao", "rgb(")
            # i = i.replace("kuohao;font", ");font")
        elif type=="python":
            # leftkuohao = re.findall(r" *\w+ *\s*\(", i)
            # leftda = re.findall(r" *\w+ *\s*\{", i)
            # for ilf in leftkuohao:
            #     ilf = ilf.replace("(", "")
            #     i = i.replace(ilf, "<span style=\"color:rgb(221, 74, 104);font-weight:600;\">%s</span>" % ilf)
            # for ilf in leftda:
            #     ilf = ilf.replace("{", "")
            #     i = i.replace(ilf, "<span style=\"color:rgb(221, 74, 104);font-weight:600;\">%s</span>" % ilf)
            def Py_sub_xiaokuohao(text):
                inp = text[0]
                return f"<span style=\"color: #dd4a68;font-weight:600;\">{inp[:-1]}</span>" + \
                    f"<span style=\"color: slategray;font-weight:600;\">(</span>"
            i = re.sub(r" *[\w_\-\_\d]+ *\s*\(", Py_sub_xiaokuohao, i)
            
            def Py_sub_dakuohao(text):
                inp = text[0]
                return f"<span style=\"color: #669900;font-weight:600;\">{inp[:-1]}</span>" + \
                    "<span style=\"color: slategray;font-weight:600;\">{</span>"
            i = re.sub(r" *[\w_\-\_\d]+ *\s*\{", Py_sub_dakuohao, i)
            # https://docs.python.org/3.12/reference/lexical_analysis.html#keywords
            keyword = ['await', 'pass', 'bool', 'break', 'case', 'catch', 'try', 'except', 'in', \
                'raise', 'finally', 'as', 'nonlocal', 'is', 'lambda', 'and', 'class', \
                'del', 'do', 'double', 'else', 'False', 'float','for', 'def', 'import', 'from', \
                'assert', 'global', 'if', 'return', 'continue', 'default', \
                'not', 'with', 'elif', 'async', 'or', 'yield', 'switch', 'throw', \
                        'True', 'while', 'None', "nan", 'infinity']
            keyword = list(set(keyword))
            for ri in keyword:
                i = re.sub(r"(?<!\w)%s(?!\w)"%ri, "<span style=\"color:rgb(0, 119, 170);font-weight:600;\">%s</span>"%ri, i)
                # i = i.replace(ri, "<span style=\"color:rgb(0, 119, 170);font-weight:600;\">%s</span>"%ri)
                
                # i = i.replace('{', "<span style=\"color:rgb(153, 153, 153);font-weight:600;\">{</span>")
                # i = i.replace('}', "<span style=\"color:rgb(153, 153, 153);font-weight:600;\">}</span>")
                # i = i.replace('}', "<span style=\"color:rgb(153, 153, 153);font-weight:600;\">}</span>")
                # symbol = ['&', "<", ">", '=', '-', '/', '+', '\\', '%', '.', '!', '?', \
                #     '`', '~', '!', '@', '#', '$', '^', '*']
                # i = i.replace("rgb(", "rgbkuohao")
                # i = i.replace(");font", "kuohao;font")
            # symbol = ['{', '}', '[', ']', '~', '`', '!', '@', '#', '$', '%', '^', '&', '*', \
            #     '?', '.', '|']
            # for ri in symbol:
            #     if ri in i:
            #         i = i.replace(ri, "<span style=\"color:rgb(153, 153, 153);font-weight:600;\">%s</span>"%ri)
            # i = i.replace("rgbkuohao", "rgb(")
            # i = i.replace("kuohao;font", ");font")
        elif type=='javascript':
            
            henggang = []
            def Js_sub_henggang(text):
                inp = text[0]
                rand = np.random.choice(choyang, 100)
                rand = ''.join(rand) + '】】】'
                retext = f"<span style=\"color: #ee9900;font-weight:600;\">{inp[:-1]}</span>" + \
                    f"<span style=\"color: slategray;font-weight:600;\">{inp[-1]}</span>"
                henggang.append([rand, retext])
                return rand
            i = re.sub(r"--[\w \_\-]*[):]", Js_sub_henggang, i)
            
            def Js_sub_maohao(text):
                inp = text[0]
                return f"<span style=\"color: #990055;font-weight:600;\">{inp[:-1]}</span>" + \
                    f"<span style=\"color: slategray;font-weight:600;\">:</span>"
            i = re.sub(r"[\w \_.\-]*:", Js_sub_maohao, i)
            
            def Js_sub_xiaokuohao(text):
                inp = text[0]
                return f"<span style=\"color: #dd4a68;font-weight:600;\">{inp[:-1]}</span>" + \
                    f"<span style=\"color: slategray;font-weight:600;\">(</span>"
            i = re.sub(r" *[\w_\-\_,\d]+ *\s*\(", Js_sub_xiaokuohao, i)

            def Js_sub_dakuohao(text):
                inp = text[0]
                return f"<span style=\"color: #669900;font-weight:600;\">{inp[:-1]}</span>" + \
                    "<span style=\"color: slategray;font-weight:600;\">{</span>"
            i = re.sub(r" *\w*[\w_\-\_,\d.#:\(\) ]+ *\s*\{", Js_sub_dakuohao, i)

            keyword = ['await', 'implements', 'package', 'interface', 'let', 'private', 'protected', \
                'public','static', 'break', 'case', 'catch', 'enum', 'class', 'const', 'continue',\
                'debugger', 'default', 'delete', 'do', 'else', 'export', 'extends', 'finally',\
                'for', 'function', 'if', 'import', 'in', 'instanceof', 'new', 'return', 'super',\
                'switch', 'this', 'throw', 'try', 'typeof', 'var', 'void', 'while', 'with', 'yield',\
                'from', 'of']
            keyword = list(set(keyword))
            for ri in keyword:
                i = re.sub(r"(?<!\w)%s(?!\w)"%ri, "<span style=\"color:rgb(0, 119, 170);font-weight:600;\">%s</span>"%ri, i)

            for ijk in henggang:
                i = i.replace(ijk[0], ijk[1])

            def Js_sub_important(text):
                inp = text[0]
                return f"<span style=\"color: #ee9900;font-weight:bold;\">{inp}</span>"
            i = re.sub(r"important", Js_sub_important, i)
        elif type=='java':
            Java_xiaokuohao = []
            def Java_sub_xiaokuohao(text):
                inp = text[0]
                rand = np.random.choice(choyang_Java, 100)
                rand = ''.join(rand) + '】】】'
                retxt = f"<span style=\"color: #dd4a68;font-weight:600;\">{inp[:-1]}</span>" + \
                    f"("
                Java_xiaokuohao.append([rand, retxt])
                return rand
            i = re.sub(r" *[\w\-\_\d]+ *\s*\(", Java_sub_xiaokuohao, i)
            
            keyword = ['abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', \
                'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'exports', 'extends', \
                'final', 'finally', 'float', 'for', 'goto', 'if', 'implements', 'import', 'instanceof', \
                'int', 'interface', 'long', 'native', 'new', 'null', 'module', 'open', \
                'opens', 'package', 'private', 'protected', 'provides', 'public', 'return', \
                'short', 'static', 'strictfp', 'super', 'switch', 'synchronized', 'this', \
                'throw', 'to', 'throws', 'transient', 'transitive', 'try', 'uses', 'var', \
                'void', 'volatile', 'with', 'while']

            keyword = list(set(keyword))
            for ri in keyword:
                i = re.sub(r"(?<!\w)%s(?!\w)"%ri, "<span style=\"color:rgb(0, 119, 170);font-weight:600;\">%s</span>"%ri, i)
            # i = re.sub(r"[. \n\(]([A-Z][a-zA-Z][a-z][\w\d]*)[\),;. \n]?", Java_sub_capital, i)

            def Java_sub_capital(text):
                inp = text[0]
                f = ''
                t = ''
                if inp[0] in ['(', '[', '\'', '\"', '>', '.', '】', '\n']:
                    f = inp[0]
                    inp = inp[1:]
                if inp[-1] in [')', ']', '[', '\'', '\"', '<', '.', ':', '?', ';', '\n',',']:
                    t = inp[-1]
                    inp = inp[:-1]
                retxt = f"{f}<span style=\"color: #dd4a68;font-weight:600;\">{inp}</span>{t}"
                return retxt
            
            i = re.sub(r"[】. \n(>]([A-Z][a-zA-Z\d_]*[a-z][\w\d_]*)[[),:?;. \n]?", Java_sub_capital, i)
            
            for ij in Java_xiaokuohao:
                i = i.replace(ij[0], ij[1])

        splited[ik] = i

    precode = "\n".join(splited)

    if type=='c++':
        precode = addback_common(precode, collect)
        precode = addback_common(precode, d_collect)
        precode = addback_common(precode, cppInclude)
    elif type=='python':
        precode = addback_common(precode, P_collect)
        precode = addback_common(precode, P_d_collect)
    elif type=='javascript':
        precode = addback_common(precode, Js_collect)
        precode = addback_common(precode, Js_d_collect)
        precode = addback_common(precode, Js_Js_collect)
        precode = addback_common(precode, Js_html)
        precode = addback_common(precode, Js_color)
    elif type=='java':
        precode = addback_common(precode, collect)
        precode = addback_common(precode, d_collect)
    
    if type=='c++' or type=='python' or type=='javascript' or type=='java':
        precode = addback_common(precode, yinhao_collect)
    
    precode = addback_common(precode, numberCol)
    precode = addback_common(precode, allOperator)
    # def replace_sub_yinhao(txt):
    #     # print(txt[0])
    #     # print(txt)
    #     return f"<span style='color:rgb(102, 153, 0);font-weight:600;'>{str(txt[0])}</span>"
    # precode = re.sub(r'''[\'\"][^'"]*[\'\"]''', replace_sub_yinhao, precode)
    # print(precode)
    ind = precode.index("\n")
    if not type:
        return precode[ind:]
    ft = firstline.replace("[]","")
    if len(ft)!=0:
        ft = ft[0].upper() + ft[1:].lower()
    precode = '<div style="background-color: #ffffff;"><span style="font-size: 26px;color:#000000;font-weight:600;">%s</span></div>'%ft + precode[ind:]
    dic0 = []
    # dic = []
    return precode

def addback_code(markdown, collect):
    for i in collect:
        codetext = addSpan(i[1])
        markdown = markdown.replace(i[0], \
'''<div class=\"codestyle\"><div class=\"writing_margin\"><pre><code>''' + codetext + \
'''
</code></pre></div></div>''')
    return markdown

def remove_katex(inp):
    collect = []
    start = 0
    tmp = []
    k = 0
    while "$" in inp[start:]:
        if len(tmp)==2:
            rand = "=,=?=" + str(np.random.randint(99999999999999)) + str(time.time()) + "=[];="
            if tmp[-1] - tmp[0]==1:
                kk = inp[tmp[0]:tmp[1] + 1]
                if kk=="$$":
                    collect.append([rand, '-$^kl12[].<>:"?-'])
                inp = inp[:tmp[0]] + rand + inp[tmp[1] + 1:]
                start = 0
                tmp = []
                k = 0
                continue
            txt = inp[tmp[0] : tmp[1] + 1]
            collect.append([rand, txt])
            inp = inp.replace(txt, rand)
            tmp = []
            k = 0
            start = 0
        try:
            k = inp[start:].index("$")
            tmp.append(k + start)
        except:
            pass
        start = k + 1
    return inp, collect

def addback_katex(markdown, collect):
    for i in collect:
        if '-$^kl12[].<>:"?-'==i[1]:
            markdown = markdown.replace(i[0],'<span>' + "$" + "</span>")
            continue
        markdown = markdown.replace(i[0], \
'''<span class=\"katexspan\">''' + i[1][1:-1] + \
'''
</span>''')
    return markdown

def rep(i):
    return i.replace(":", "_").replace("_问号_", "？").replace("_感叹号_", "！").replace("-感叹号-", "！").\
              replace("小于", "<").replace("大于", ">").replace("_逗号_", "，").replace("-逗号-", "，").\
              replace("_空格_", " ").replace("-空格-", " ").replace("_冒号_", "：").replace("-冒号-", "：").\
              replace("_顿号_", "、").replace("-顿号-", "、").replace("https_", "https:").\
              replace("http_", "http:")

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
    global choyang, kseamutex
    # https://docs.djangoproject.com/en/5.1/ref/request-response/#top
    req = request.GET.dict()
    # req = json.loads(request.body)
    pathkkk = req["path"]
    dirname = pathkkk.split(os.sep)[-2]
    filename = pathkkk.split(os.sep)[-1]
    
    predir = pathkkk.replace(filename, "")
    pathkkk = findlatest(predir)
    markdownpth = deepcopy(pathkkk)
    
    create = pathkkk.replace(filename, "create.txt")
    lastline = ""
    postDate = datetime.fromtimestamp(time.time() +timezone).isoformat()[:19]
    postDate = postDate.replace("T", " ")

    if '20'==dirname[:2] or '21' == dirname[:2]:
        date = rep(dirname[:22]).replace("_", ":")
        title = rep(dirname[23:])
    else:
        date = postDate
        title = rep(dirname)
    if 'zhihu_' in pathkkk:
        date = rep(dirname[:16]).replace("_", ":")
        date = date[:10] + " " + date[11:]
        title = rep(dirname[20 - 3:])

    if os.path.exists(create):
        ij = 0
        with open(create, 'r', encoding='utf-8') as obj:
            for i in obj.readlines():
                if ij==0:
                    date = i.strip().replace("_空格_", " ").replace("_", ":")
                ij += 1
                lastline = i.strip().replace("_空格_", " ").replace("_", ":")
                if 'zhihu_' in pathkkk:
                    lastline = i.strip().replace("_", ":")[:-1]
                    lastline = lastline[:10] + " " + lastline[11:]

    markdown = r''
    with open(pathkkk, 'r', encoding='utf-8') as obj:
        markdown = obj.read().strip()
    # assert 1==0, markdown
    index = pathkkk.index("vue-project")
    k = len(pathkkk) - 1
    while pathkkk[k]!=os.sep:
        k = k - 1
    if 'dist' in pathkkk:
        index += 16
    else:
        index += 11
    nextline_index = markdown.index("\n")
    firstline = markdown[:nextline_index]
    # markdown = rep(firstline).replace("_", " ") + markdown[nextline_index:]
    markdown = rep(firstline) + markdown[nextline_index:]
    markdown = markdown.replace("在这里插入图片描述", "")
    markdown, collect = remove_code(markdown)
    markdown, collect_katex = remove_katex(markdown)
    
    downline = []
    def remove_downline(text):
        inp = text[0]
        rand = np.random.choice(choyang, 100)
        rand = ''.join(rand) + '】】】'
        downline.append([rand, inp])
        return rand
        
    markdown = re.sub(r' *[\w\d\-\_]*\_[\w\d\-\_]* *', remove_downline, markdown)

    markdown = markdown2.markdown(markdown, extras=["tables", ])

    markdown = markdown.replace('''<img src=\"''',\
        '''<img crossorigin=\"use-credentials\" loading=\"eager\" class=\"img_blank_class\"''' + \
        '''src=\"''' + pathkkk[index : k] + os.sep)
    
    markdown = addback_code(markdown, collect)
    markdown = addback_katex(markdown, collect_katex)
    
    if title not in markdown[:100]:
        markdown = f"<h1>{title}</h1>\n\n" + markdown
    markdown = markdown.replace("<p><br></p>", "")
    markdown = markdown.replace("<a", "<a target=\"_blank\" ")
    def replace_weblink(inp):
        text = inp[0]
        id = text.index('</a>')
        text = text[:id+4] +'<br>'+ text[id+4:]
        return text
    def replace_line_delete(md):
        return  "<s>" + md[0][2:-2] + "</s>"
    def replace_warning(md):
        return '<div class=\"warningclass\">' + md[0][11+1:-3] + "</div>"
    markdown = re.sub(r'''</a>[\n ]*<a''', replace_weblink, markdown)
    markdown = re.sub(r'''~~.*~~''', replace_line_delete, markdown)
    markdown = re.sub(r''' *::: warning *\s.*\n:::''', replace_warning, markdown)
    markdown = markdown.replace("$在这里插入图片描述$", "")
    markdown = markdown + f"\n\n<span class=\"post_revise_time\">发布时间：{date}</span>\n \
    <span class=\"post_revise_time\">修改时间：{lastline}</span>\n<p><br></p>"

    for i in downline:
        markdown = markdown.replace(i[0], i[1])
    # markdown = markdown.replace("<em>", "")
    # markdown = markdown.replace("</em>", "")
# .\
#                         replace("<code>", \
# '''
# <div class=\"codestyle\">
# <div class=\"writing_margin\">
# <pre>
# <code>''').replace("</code>", \
# '''
# </code>
# </pre>
# </div>
# </div>''')
    markdown = replaceNextLine_br(markdown)

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
    tails = markdownpth.split(os.sep)[-1]
    if tails not in kseamutex.keys():
        kseamutex[tails] = Semaphore(value=1)

    upvotecomment = os.path.join(predir, 'upvote_comment.json')
    if not os.path.exists(upvotecomment):
        os.system(f"touch \"{upvotecomment}\"")

    kseamutex[tails].acquire()
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
    kseamutex[tails].release()
    kseamutex.pop(tails)

    return JsonResponse( { "markdown" : markdown, 'path': pathkkk, "upvote":upvote, 'comment':comment, 'click':click, \
                            'clickshoucang':clickshoucang, 'kshoucang':kshoucang, 'title':title} , safe = False)

def replaceNextLine_br(md):
    start = -1
    end = -1
    md += '123456789'
    nowlen = len(md)
    addlen = 0
    j = 0
    while j < nowlen + addlen - 1 or addlen!=0:
        addlen = 0
        nowlen = len(md)
        for i in range(j, nowlen, 1):
            if i < end:
                continue
            j = i
            if md[i:i + 3]=="<p>":
                start = 100
            elif md[i:i + 4]=="</p>":
                start = -1
            elif start > 0 and md[i]=='\n':
                md = md[:i] + "<br>" + md[i + 1:]
                end = i + 4
                addlen += 3
    return md[:-9]
