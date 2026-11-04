"""同时在线用户计数（内存实现，线程安全），不设上限。

「在线」定义：最近 ONLINE_WINDOW 秒内有过任意请求的独立 IP（含未登录访客
与搜索引擎爬虫，作为活跃指标是合理的）。计数由 antiflood 中间件在全局
请求入口处刷新，视图层只读。

不做容量限制：无论多少人同时在线都正常服务，人数只用于左侧栏展示。
"""

import threading
import time

_lock = threading.Lock()
# ip -> 最后活跃时间戳
_last_seen = {}
# 机会式清理计数：每 256 次 touch 清理一次过期 IP，防字典无限增长
_ops = 0

# 最近 5 分钟内有请求的 IP 算「在线」
ONLINE_WINDOW = 300


def touch(ip):
    """记录一次活跃，返回当前在线人数（新 IP 立即计入）。"""
    global _ops
    with _lock:
        now = time.time()
        is_online = now - _last_seen.get(ip, 0) < ONLINE_WINDOW
        _ops += 1
        if _ops % 256 == 0:
            for k in [k for k, t in _last_seen.items() if now - t >= ONLINE_WINDOW]:
                _last_seen.pop(k, None)
        count = sum(1 for t in _last_seen.values() if now - t < ONLINE_WINDOW)
        _last_seen[ip] = now
        # 新加入的 IP 计入在线人数；已在名单的重复活跃不重复计数
        return count if is_online else count + 1


def count():
    """当前在线人数（只读，不动计数）。"""
    with _lock:
        now = time.time()
        return sum(1 for t in _last_seen.values() if now - t < ONLINE_WINDOW)
