"""全局请求洪水防护中间件：防 DDoS / 短时大流量 / 慢速爆破（应用层）。

每 IP 双速率滑动窗口（复用 ratelimit 内存计数）：
  - 突发：每 1 秒最多 15 个请求（页面一次正常加载远低于此）
  - 持续：每 60 秒最多 300 个请求（翻页/搜索连点也够用）
  - 管理接口（路径含 admin_）：每 60 秒最多 60 个（防慢速逐个试 postkey/密码）

超出返回 429 + Retry-After。真正的 L3/L4 大流量 DDoS 需在 nginx / 云清洗层
处理（配合 limit_req，见部署说明）；本中间件兜住打到 Django 的应用层洪水，
防止文件 IO（member.txt / people 目录遍历）被刷到磁盘打满、进程卡死。

说明：计数在内存，重启清零（可接受）；单进程部署下精确。
"""

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

import ratelimit
import online

# 突发与持续阈值（每 IP）：按站点容量设定——最大并发 100 请求/秒
BURST_LIMIT, BURST_WINDOW = 100, 1
SUSTAIN_LIMIT, SUSTAIN_WINDOW = 3000, 60
# 管理接口更严格（正常管理页操作频率远低于此，防慢速爆破）
ADMIN_LIMIT, ADMIN_WINDOW = 60, 60


def _client_ip(request):
    """与 csdn/views._client_ip 一致：优先 nginx X-Forwarded-For 首段。"""
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '') or 'unknown'


class AntiFloodMiddleware(MiddlewareMixin):
    """每 IP 全局限流；被限的请求直接短路，不进入视图（不消耗文件 IO）。"""

    def process_request(self, request):
        ip = _client_ip(request)
        path = request.path or ''

        # 刷新该 IP 的活跃时间（「在线」计数的来源）；在线人数不设上限，不做容量拒绝
        online.touch(ip)

        # 突发：每秒 100 个（站点容量：最大并发 100 请求/秒）
        if not ratelimit.hit(f'flood:1s:{ip}', BURST_LIMIT, BURST_WINDOW):
            return self._blocked()
        # 持续：每分钟 3000 个
        if not ratelimit.hit(f'flood:60s:{ip}', SUSTAIN_LIMIT, SUSTAIN_WINDOW):
            return self._blocked(60)
        # 管理接口：每分钟 60 个（防慢速逐个尝试）
        if 'admin_' in path and not ratelimit.hit(f'flood:admin:{ip}', ADMIN_LIMIT, ADMIN_WINDOW):
            return self._blocked(60)
        return None

    @staticmethod
    def _blocked(retry_after=5):
        resp = JsonResponse(
            {"ret": -429, "msg": "请求过于频繁，请稍后再试"},
            safe=False,
        )
        resp.status_code = 429
        resp['Retry-After'] = str(retry_after)
        return resp
