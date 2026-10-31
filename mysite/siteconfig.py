"""站点统一配置加载器（配套 mysite/site_config.json）

用法：
    import siteconfig
    value = siteconfig.get('traveler_dedup_window_seconds')

规则：
- 按 mtime 缓存读取 site_config.json，修改 JSON 即时生效，无需重启 Django；
- JSON 缺失 / 损坏 / 键缺失时回退 DEFAULTS，服务不会因配置错误而崩溃；
- 值类型由调用方自行保证（int()/str() 包一层即可）；
- 配置文件中每个键上方有同名「_文档键」作详细注释（含义/修改方法/后果），
  以 _ 开头的键仅作文档，get() 永远不会返回它们。
"""
import json
import os

_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site_config.json')

DEFAULTS = {
    # 访客统计（csdn/views.py StatisticTravelerCount / read_traveler_count）
    'traveler_dedup_window_seconds': 600,   # 同一 IP 重复访问同一用户的去重窗口
    'traveler_cleanup_seconds': 3600,       # 内存访客表超时清理
    'traveler_baseline': 3600,              # 访客数展示下限
    'traveler_default_init': 100,           # 统计文件缺失/损坏时的初始值
    'traveler_filename': 'TravelerStatistics.txt',

    # 登录凭据 cookie 有效期（天数）。前端经 /csdn/getSiteConfig 白名单接口读取
    'cookie_login_days': 30,

    # 邮箱验证码（前端经 getSiteConfig 白名单读取 mail_resend_cooldown_seconds）
    'mail_resend_cooldown_seconds': 60,   # 前端两次发送验证码的最小间隔
    'verify_code_ttl_seconds': 86400,     # 验证码有效期（register 校验 dif >= TTL 即过期）

    # SMTP 发信（mailsend）
    'smtp_host': 'smtp.qq.com',
    'smtp_port': 465,
    'smtp_user': '1069679911@qq.com',
    'smtp_password': '1234567890',
    'site_domain': 'http://zoujiu.com.cn',
    'site_name': 'zoujiu.com.cn',         # 邮件主题前缀

    # 显示时区偏移（manage.timezone，全站时间戳换算用）
    'display_timezone_offset_seconds': 28800,

    # think 列表/详情「修改时间日期」标注阈值
    'modified_label_seconds': 3600,

    # travel 匿名留言长度校验
    'travel_min_email_len': 6,
    'travel_min_contact_len': 6,
    'travel_min_content_len': 10,
    'travel_max_content_len': 2000,         # travel 留言正文长度上限（防磁盘滥用）
    'travel_max_field_len': 100,            # travel 留言姓名/邮箱/联系方式长度上限

    # mainpage 个人卡片 / 左侧卡片 / 书架（csdn/views.py FormsubmitSetting / mainpagedataget）
    'setting_max_items': 60,                # SettingForm 条目数上限（防超大 payload 滥用磁盘，前端模板 60 条）
    'setting_max_field_len': 200,           # 个人卡片/左侧卡片单字段长度上限
    'book_max_field_len': 200,              # 书架条目 name/ratio/readdate/author/github 单字段长度上限
    'book_max_items': 30000,                # 书架总条目上限（addbook 超过上限且无空槽位可复用时拒绝）
    'book_default_pagesize': 20,            # 书架列表默认页大小（allbooks.vue 分页，不传 pagesize 时用）
    'book_max_pagesize': 100,               # 书架单页条数上限（防一次拉全量 30000 本打爆响应）
    'nickname_max_len': 50,                 # 用户昵称长度上限（member.txt，NicknameSetting）

    # 用户名长度规则（csdn/views.py getusername 短名守卫 / register 注册校验）
    'short_name_guard_max_length': 6,       # @前缀长度 <= 该值按匿名访客处理
    'min_username_prefix_length': 7,        # 注册时 @前缀最小长度

    # 开发服务器并发队列（manage.py）
    'server_request_queue_size': 128,       # socketserver listen backlog

    # 列表页默认分页（csdn/think/travel/video 的 index，页大小按模块分开配置）
    'default_currentpage': 1,
    'default_pagesize_csdn': 20,
    'default_pagesize_think': 10,
    'default_pagesize_travel': 10,
    'default_pagesize_video': 10,

    # 站内通知（csdn/views.py send_notice / get_notice / clear_notice）
    'notice_display_max': 200,        # 固定显示最近 N 条，同时是每用户存储上限
    'notice_clear_temporary': True,   # true=清空仅本次显示生效，刷新后通知恢复；false=持久清空

    # 音乐播放器（src/music.js，APlayer fixed 模式 + Meting 协议在线歌单）
    'music_enabled': True,
    'music_api': 'https://api.i-meto.com/meting/api',  # Meting 协议 API（可换自建）
    'music_server': 'netease',        # 音乐平台：netease/tencent/kugou/kuwo
    'music_type': 'playlist',         # music_id 解析类型：playlist/song/album/search
    'music_id': '3778678',            # 默认：网易云音乐热歌榜（旧单源字段，music_sources 为空时兜底）
    # 多播放源容灾列表：按顺序尝试，默认用第一个；某源失效自动切换下一个（前端 src/music.js）
    'music_sources': [
        {'name': '网易云·热歌榜', 'server': 'netease', 'type': 'playlist', 'id': '3778678'},
        {'name': '网易云·新歌榜', 'server': 'netease', 'type': 'playlist', 'id': '3779629'},
        {'name': '云音乐·经典榜', 'server': 'netease', 'type': 'playlist', 'id': '60198'},
    ],
    # SMTP 授权码（downloadall 数据下载邮件通知用）；敏感配置，不进 PUBLIC_KEYS 公开白名单
    'smtp_password': 'qqaymrpfctvlbcif',
}

_mtime = None
_data = {}


def get(key):
    """读取配置项；优先取 site_config.json，缺失/损坏/无该键时回退 DEFAULTS"""
    global _mtime, _data
    try:
        m = os.path.getmtime(_CONFIG_FILE)
    except OSError:
        m = None
    if m != _mtime:
        try:
            with open(_CONFIG_FILE, encoding='utf-8') as f:
                _data = json.load(f)
        except Exception:
            _data = {}
        _mtime = m
    return _data.get(key, DEFAULTS.get(key))
