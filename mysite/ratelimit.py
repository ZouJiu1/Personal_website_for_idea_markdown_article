"""轻量内存限流器：滑动窗口计数，线程安全，自动清理过期记录。

用途（防护入侵/攻击，减缓暴力破解与垃圾请求）：
  - login        ：每 IP 登录尝试限流（防密码爆破）
  - sendverify   ：每邮箱发送间隔 + 每 IP 每小时发信量（防邮件轰炸 / SMTP 配额耗尽）
  - register     ：每 IP 注册频次 + 每邮箱验证码校验次数（防验证码穷举）

说明：仅适合单进程部署（本站 runserver / 单 worker 场景）；定位是「减缓攻击」
而非精确配额，重启进程后计数清零（可接受——攻击者重新计数同样受窗限制约）。
"""

import threading
import time

_lock = threading.Lock()
# key -> 最近命中的时间戳列表（滑动窗口）
_hits = {}
# 机会式全量清理计数器：每 1024 次 record 清理一次全表，防键无限增长
_ops = 0
_CLEAN_EVERY = 1024


def _prune(now, window):
    """删掉全部键里过期的记录；空键移除。调用方必须已持有 _lock。"""
    global _hits
    cleaned = {}
    for key, ts in _hits.items():
        fresh = [t for t in ts if now - t < window]
        if fresh:
            cleaned[key] = fresh
    _hits = cleaned


def too_many(key, limit, window):
    """滑动窗口内 key 的命中次数是否已达上限（只查不记）。"""
    with _lock:
        now = time.time()
        ts = [t for t in _hits.get(key, []) if now - t < window]
        return len(ts) >= limit


def record(key, window):
    """记录一次命中（配合 too_many 实现「失败才计数」等延迟惩罚）。"""
    global _ops
    with _lock:
        now = time.time()
        ts = [t for t in _hits.get(key, []) if now - t < window]
        ts.append(now)
        _hits[key] = ts
        _ops += 1
        if _ops % _CLEAN_EVERY == 0:
            _prune(now, window)


def hit(key, limit, window):
    """尝试占用一个名额：窗口内未达上限则记录并返回 True，已达上限返回 False。"""
    with _lock:
        now = time.time()
        ts = [t for t in _hits.get(key, []) if now - t < window]
        if len(ts) >= limit:
            return False
        ts.append(now)
        _hits[key] = ts
        global _ops
        _ops += 1
        if _ops % _CLEAN_EVERY == 0:
            _prune(now, window)
        return True


def reset(key):
    """清空某键的计数（如登录成功后清失败记录）。"""
    with _lock:
        _hits.pop(key, None)
