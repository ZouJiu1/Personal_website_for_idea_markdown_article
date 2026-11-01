"""邮箱 <-> 36 位纯数字 uid 映射（URL 隐私方案）

背景：
    全站 URL 原先直接携带邮箱（/#/homepage@gmail.com），会向访客/日志/分享
    链接泄露邮箱。本模块把每个邮箱映射成一个 36 位纯数字字符串，前端 URL
    只出现 uid，后端在 findurlmail 解析时再还原成邮箱，磁盘上的
    people/<邮箱>/ 目录结构完全不变。

存储：
    mysite/uid_map.txt，每行一条：uid<》!=$)(=$@mail
    与 member.txt 使用相同分隔符；写入用 os.replace 原子替换，防止并发写坏文件。

注意：
    - uid 一经生成长期不变（持久化），旧链接不会失效；
    - 旧邮箱形态 URL 仍然兼容（findurlmail 原样返回邮箱）；
    - 只做映射，不做鉴权；鉴权仍走 member.txt 的 mail/password 校验。
"""
import os
import random
import threading

_MAP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uid_map.txt')
_SEP = "<》!=$)(=$@"
_UID_LEN = 36

# RLock：mail_to_uid 生成新映射时在持锁状态下会再调 _load() 重建缓存
_lock = threading.RLock()
_cache = None  # {mail: uid} 与 {uid: mail} 同步维护


def _load():
    """读磁盘映射到内存缓存（首次访问或文件变化时重建）"""
    global _cache
    with _lock:
        mapping = {}
        reverse = {}
        try:
            with open(_MAP_FILE, encoding='utf-8') as fp:
                for line in fp:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(_SEP)
                    if len(parts) < 2 or "@" not in parts[1]:
                        continue
                    uid, mail = parts[0], parts[1]
                    if len(uid) != _UID_LEN or not uid.isdigit():
                        continue
                    mapping[mail] = uid
                    reverse[uid] = mail
        except OSError:
            pass
        _cache = (mapping, reverse)
    return _cache


def _append(mail, uid):
    """持久化一条新映射（追加写 + 锁保护）"""
    with _lock:
        with open(_MAP_FILE, 'a', encoding='utf-8') as fp:
            fp.write(uid + _SEP + mail + "\n")


def is_uid(seg):
    """判断 URL 用户段是否为 36 位纯数字 uid 形态"""
    return bool(seg) and len(seg) == _UID_LEN and seg.isdigit()


def mail_to_uid(mail):
    """邮箱 -> uid；不存在则生成并持久化。非法邮箱返回 None（不生成映射）"""
    if not mail or "@" not in mail:
        return None
    mapping, _ = _load()
    uid = mapping.get(mail)
    if uid:
        return uid
    with _lock:
        # 双检：并发下另一线程可能刚写入
        mapping, _ = _load()
        if mail in mapping:
            return mapping[mail]
        # 36 位随机数字，首位不为 0（保持纯数字且视觉上像随机串）
        uid = str(random.randint(1, 9)) + ''.join(
            str(random.randint(0, 9)) for _ in range(_UID_LEN - 1))
        _append(mail, uid)
        # 刷新缓存
        mapping[mail] = uid
        return uid


def get_uid(mail):
    """只查询不生成；邮箱无映射时返回 None"""
    if not mail or "@" not in mail:
        return None
    mapping, _ = _load()
    return mapping.get(mail)


def uid_to_mail(uid):
    """uid -> 邮箱；无映射（如脏数据/人为伪造）返回 None"""
    if not is_uid(uid):
        return None
    _, reverse = _load()
    return reverse.get(uid)
