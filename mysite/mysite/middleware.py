from django.middleware.csrf import CsrfViewMiddleware


class ScopedCsrfMiddleware(CsrfViewMiddleware):
    """仅对 Django admin（/admin）启用 CSRF 校验的中间件。

    背景：
      - 本站自定义 API（/csdn/* 等）的认证方式是“每次请求在 body 里携带
        mail + sha256 密码”，后端从不读取 cookie 做鉴权（views.py 中无
        request.COOKIES 使用），攻击者无法伪造 body 凭据，天然免疫 CSRF；
      - 且这些接口数量众多、不带 csrf token，若全局启用官方校验会全部 403。

    因此继承官方 CsrfViewMiddleware：/admin 开头的请求走完整 CSRF 校验
    （admin 依赖 session 登录，是真正需要 CSRF 防护的 cookie 会话面），
    其余路径直接放行。
    """

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if not request.path.startswith('/admin'):
            return None
        return super().process_view(request, callback, callback_args, callback_kwargs)
