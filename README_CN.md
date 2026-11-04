> English | [简体中文](README_CN.md)

# 个人网站（想法 / Markdown 文章 / 图书 / 视频 / 知乎 / 片段 / 游客 / 常用 / 图片）

基于 **Vue 3 + element-plus + Django** 的个人网站，线上示例：[http://zoujiu.com.cn](http://zoujiu.com.cn)

- 支持 Markdown 文章创作（数学公式 KaTeX、表格、列表、代码高亮等）
- 支持图书、视频上传与播放（hls.js）、知乎文章、想法片段、游客留言、常用网站、每日图片
- 不使用数据库：用户、文章、设置等全部保存在 txt / markdown 等文本文件中
- 多用户隔离：每个注册用户拥有独立的 `people/<用户名>/` 数据目录，互不影响
- **网址隐私**：网址中永不出现邮箱——每个账号映射为一个随机 36 位纯数字 uid
  （如 `/#/165989218739189801318616830165629911`），旧邮箱形态链接彻底失效，
  站内所有生成的链接均使用 uid（见 4.8）
- js-cookie 维持登录态（30 天），支持注册、登录、登出、邮箱验证码改密
- 文篇发布页内置草稿箱：保存草稿、草稿箱列表、再次编辑、删除，发布成功自动清稿（见 4.4）
- 文篇编辑页附加能力（见 4.5/4.6）：**图片管理**——列出/删除文篇或片段的配图，删除时自动剥离
  正文中的引用并重渲染预览；**历史文档**——每次发布都保留带时间戳的历史版本，支持阅读
  （渲染预览）、恢复到编辑器、删除旧版本，当前版本受保护不可删
- 登录弹窗：两个输入框内按 Enter 即可登录（等同点击登录按钮）
- 内置注册管理页面：管理员可查看用户列表、新建用户、重置密码、修改权限、删除用户
- 三层安全防护：nginx 限流（10 请求/秒 + 每 IP 并发连接数限制）→ 防洪水中间件（突发 100 请求/秒、
  持续 3000 请求/分钟、后台接口单独限速）→ 敏感接口限流（登录 20 次/10 分钟、注册 5 次/小时、
  验证码同邮箱 60 秒 1 封）；上传接口服务端二次校验（图片 ≤13MB + 文件头魔数、视频 mp4/webm
  ≤2G + 魔数、文件名剥离路径防目录穿越）
- 凭据库隔离：member.txt（全量用户表）与 oldpassword/（历史密码备份）存放在部署根 data/
  私有目录（nginx 不服务，首次启动自动从旧静态目录迁移）；nginx 同时封堵 article/ 下全部数据 txt 的直接下载
- 站点配置管理：site_config.json 全部配置项进入管理页弹窗，仅站长可见可改，修改需点确认生效，删除操作三次确认
- 左侧栏实时显示在线人数（绿色呼吸动效，60 秒轮询），在线计数不设上限
- 看板郎鼠标互动引擎：1792 种随机互动预设（14 种移动力场 × 16 种点击效果 × 8 种光标拖尾，
  每 10 分钟随特效轮换），约三分之一预设带看板郎力场（粒子绕角色公转 / 角色光环）；
  悬停吹星星、快速掠过带起粒子风、点击/连点角色触发台词与粒子爆发（详见 6.1）
- 内置 Live2D 看板郎挂件：23 个开源形象按 9 大分类自选，账号级记忆（换设备也生效），
  29 个中外节日全天祝福 + 全屏粒子特效（可用鼠标互动），非节日也有平日特效
  （900 个图形家族 / 10000 种组合）
- 内置音乐播放器（APlayer + Meting 网易云歌单，Django 服务端代理转发），桌面端悬浮于看板郎上方
- 看板郎与音乐播放器均可拖拽停靠：按住拖动改变位置（localStorage 记忆，刷新恢复），
  看板郎双击复位、音乐播放器双击封面复位
- 响应式布局：适配手机、平板与桌面浏览器，支持浏览器拖宽与窗口大小变化

## 目录结构

```
Personal_website_for_idea_markdown_article/
├── src/                    # Vue3 前端源码
│   ├── views/              # 各功能页面（home/csdn/zhihu/think/video/travel/...）
│   │   └── admin/          # 注册管理页面（仅管理员可见）
│   ├── router/routers.js   # 前端路由（hash 模式）
│   ├── common.js           # getusername 等公共方法（相对路径请求）
│   └── assets/main.css     # 全局样式 + 响应式适配
├── mysite/                 # Django 后端
│   ├── mysite/projectpaths.py  # 项目根目录自动定位（无需硬编码绝对路径）
│   ├── mysite/antiflood.py # 防洪水中间件（突发/持续限速 + admin 限速 + 在线计数刷新，MIDDLEWARE 首位）
│   ├── csdn/               # 文篇 + 用户注册/登录/管理接口
│   ├── uidmap.py           # 邮箱 ↔ 36 位 uid 映射（网址隐私，持久化在 uid_map.txt）
│   ├── ratelimit.py        # 滑动窗口限流器（登录/注册/验证码等敏感接口）
│   ├── online.py           # 同时在线用户计数（5 分钟滑动窗口，按 IP 去重）
│   ├── zhihu/ think/ video/ travel/ commonuse/ markdown_detail/ upload_video/
│   └── manage.py
├── data/                   # 私有数据（member.txt 用户表、oldpassword/ 历史密码备份；nginx 不服务，防直接下载）
├── article/                # 公共数据（register.txt 验证码、文章等）
├── people/<用户名>/        # 每个注册用户的独立数据目录
├── public/live2d/          # Live2D 看板郎挂件资源（引擎/样式/文案/农历库/23 个模型目录）
├── vite.config.js          # Vite 配置（开发代理转发到 Django，构建代码分割）
├── nginx_http.conf         # 生产环境 nginx 配置示例（http）
└── nginx_https.conf        # 生产环境 nginx 配置示例（https）
```

## 1. 环境准备

### 1.1 Node.js

参考 [https://nodejs.org/zh-cn/download](https://nodejs.org/zh-cn/download) 安装 Node.js（建议 v18+）。

macOS 可用 Homebrew：`brew install node@22`

设置镜像加速（可选）：

```bash
npm config set registry https://registry.npmmirror.com
```

### 1.2 安装前端依赖

```bash
cd Personal_website_for_idea_markdown_article
npm install
```

主要依赖：`vue` `vue-router` `element-plus` `axios` `js-cookie` `katex` `hls.js` `aplayer`（看板郎音乐播放器）；看板郎农历换算用自托管 UMD `public/live2d/solarlunar.min.js`（npm 包 solarlunar）

### 1.3 Python 环境

```bash
cd Personal_website_for_idea_markdown_article
python3 -m venv ./venv
source ./venv/bin/activate
python3 -m pip install -r ./mysite/requirements.txt
```

## 2. 本地调试（不需要 nginx）

前端所有请求均为相对路径，Vite 开发服务器会自动把 `/csdn`、`/zhihu`、`/article`、`/people` 等前缀代理到 Django，本地调试**无需 nginx**。

```bash
# 终端 1：启动前端（默认 5173 端口，可自定）
npm run dev -- --port 9000

# 终端 2：启动后端
source ./venv/bin/activate
cd mysite
python3 manage.py runserver localhost:7290
```

浏览器访问 `http://localhost:9000`。

- 后端地址可用环境变量覆盖：`DJANGO_TARGET=http://127.0.0.1:7290 npm run dev`
- DEBUG 模式下 Django 会直接提供 `/article`、`/people`、`/hls` 静态资源

## 3. 生产部署（nginx）

```bash
# 打包前端，产物在 dist/
npm run build

# 启动后端（生产务必以 DJANGO_DEBUG=0 关闭调试，静态资源改由 nginx 伺服）
source ./venv/bin/activate
cd mysite
DJANGO_DEBUG=0 python3 manage.py runserver localhost:7290
```

### 发布检查清单

- `DJANGO_DEBUG=0`：本地调试默认开 DEBUG（runserver 直接伺服 `/article` `/people` `/hls`），
  生产必须置 0，改由 nginx 直接伺服这三个目录。注意**激活配置在内层 `mysite/mysite/settings.py`**
- `ALLOWED_HOSTS` 已限定 `zoujiu.com.cn` / `121.40.168.141` / `localhost` / `127.0.0.1`，
  换域名需同步修改 `mysite/mysite/settings.py`
- `SECRET_KEY`：优先环境变量 `DJANGO_SECRET_KEY`，其次 `mysite/secret_key.txt`
  （随机密钥已生成，已加入 `.gitignore`，勿提交仓库）
- CSRF：`mysite/middleware.py` 的 `ScopedCsrfMiddleware` 仅对 Django admin（`/admin`）启用校验；
  自定义 API 认证走 body 传参（不读 cookie），天然免疫 CSRF，不受影响
- 密码只存加盐格式（`sha256s$盐$摘要`），旧格式（裸 sha256）已彻底弃用，旧用户需重新注册（见 4.1）
- 上传接口服务端二次校验：图片仅 jpg/jpeg/png/bmp/gif 且 ≤13MB、视频仅 mp4/webm 且 ≤2G，
  均校验文件头魔数（防改后缀伪装），文件名剥离路径成分防目录穿越
- 凭据库不在静态目录：member.txt / oldpassword/ 位于部署根 `data/`（首次启动自动迁移），
  nginx 对 article/ 下全部数据 txt deny，防止直接下载用户表
- nginx 对 `/article`、`/people` 下发 `Cache-Control: no-cache`（回源校验）：未变更的文件仍走
  廉价 304，而经图片管理删除的图片立即变 404，浏览器缓存不再残留旧图
- 删除接口（delete）与管理员代编辑/代传图均限制在项目 `people/`、`article/` 目录内，防路径穿越
- 生产建议 gunicorn/uwsgi 多 worker 运行并由 nginx 限流（见「并发与多用户说明」）

nginx 配置参考 [nginx_http.conf](./nginx_http.conf) 或 [nginx_https.conf](./nginx_https.conf)，按实际目录修改：

- `dist/` 作为前端静态根目录
- `/article`、`/people`、`/hls` 指向项目根目录下的同名目录
- `/csdn`、`/zhihu`、`/think`、`/video`、`/travel`、`/commonuse`、`/markdown_detail`、`/upload_video` 等接口前缀 proxy_pass 到 `http://localhost:7290`

常用命令：

```bash
nginx -c /path/to/nginx.conf   # 启动
nginx -s reload                # 重载配置
nginx -s stop                  # 停止
```

## 4. 用户与权限

### 4.1 用户文件格式

用户保存在部署根 `data/member.txt`（私有目录，nginx 不服务；首次启动自动从旧的静态目录
`article/member.txt` 迁移），每行一个用户，字段以 `<》!=$)(=$@` 分隔：

```
<密码哈希><》!=$)(=$@<邮箱><》!=$)(=$@<昵称><》!=$)(=$@<权限>
```

密码哈希只允许加盐格式：`sha256s$<盐>$<sha256(盐+前端sha256值)>`。
旧格式（裸 sha256）已彻底弃用：后端一律校验失败，旧用户需重新注册。
权限字段为整数，`999999999` 表示站长，`1000000` 表示超级管理员，`100` 表示普通管理员，`1` 表示普通用户。

### 4.2 注册管理页面（管理员）

管理员登录后，左侧菜单会出现 **管理** 入口（路由 `/admin/<uid>`），功能包括：

- 查看全部注册用户（用户名、邮箱、昵称、权限、数据目录是否存在）
- 新建用户（仅站长 / 超级管理员：直接在管理页面创建，需提供邮箱、用户名与密码）
- 重置任意用户密码
- 修改用户权限
- 删除用户（个人数据目录自动备份到 `article/deleted_users/`，站长账号受保护不可删除）

后端接口：`/csdn/admin_userlist`、`/csdn/admin_createuser`、`/csdn/admin_resetpass`、`/csdn/admin_setquanxian`、`/csdn/admin_deleteuser`，均校验管理员身份。

### 4.3 修改管理员密码

```bash
cd 项目根目录
# 用 --pw 指定新密码（也可直接改脚本内默认值后运行）
python3 genpassword.py --pw 新密码
```

将输出的 `sha256s$盐$摘要` 整串替换 `data/member.txt` 中管理员行的第一段即可
（登录时前端传 sha256 值，后端按加盐格式校验）。

### 4.4 草稿箱（文篇发布页）

文篇发布页（`/csdn/post_article`）提供草稿功能，仅登录用户可用：

- **保存草稿**：将当前标题与 Markdown 内容存入个人草稿箱
  （`people/<用户名>/draft/<时间戳>.json`），每用户上限 100 篇
- **草稿箱**：弹窗列表展示全部草稿（标题 + 保存时间），支持：
  - **再次编辑**：回填标题与内容继续写，保存时覆盖原稿
  - **删除**：确认后从草稿箱移除
- **发布自动清稿**：由草稿载入的文章发布成功后，自动从草稿箱移除对应草稿

后端接口：`/csdn/save_draft`、`/csdn/draft_list`、`/csdn/draft_get`、`/csdn/draft_delete`，
鉴权与其他写接口一致（mail + password 走 member.txt 校验）；
草稿目录按用户隔离，编号仅允许纯数字，防路径注入。

### 4.5 文篇编辑页：图片管理与历史文档

编辑页（`src/views/csdn/post.vue`）为文章归属者（管理员亦可）提供两个管理弹窗：

- **图片管理**：列出当前文章目录下的配图（缩略图、大小、上传时间）；删除图片时若被正文引用
  会先提醒，删除成功后自动剥离正文中的引用（`<img src=...>` / `![...](...)`）并重渲染预览，
  图片立刻消失而不是靠浏览器缓存残留；重新发布后线上文章同步生效
- **历史文档**：每次发布都会在文章目录留下一份带时间戳的 Markdown 历史版本；弹窗列出全部
  版本（当前版本打「当前」标签且不可删除），支持：
  - **阅读**：用与预览一致的渲染管线（KaTeX、图片路径改写）在弹窗内渲染该版本
  - **恢复**：把该版本内容载回编辑器，重新发布后生效
  - **删除**：确认后删除旧版本（后端始终拒绝删除当前版本）

后端接口：`/csdn/img_list`、`/csdn/img_delete`、`/csdn/history_list`、`/csdn/history_get`、
`/csdn/history_delete`；鉴权使用请求自带的登录身份（mail + password），路径 realpath 限制在
`people/`/`article/` 内，普通用户仅能操作本人目录。
在详情页删除整篇文篇（或片段，见 4.6）后会返回列表并整页刷新，被删条目立即消失，
不会残留在旧列表里。

### 4.6 片段详情页：图片管理

片段详情页（`src/views/think_detail/tkdetail.vue`）提供同款图片管理弹窗（片段归属者/管理员）：
列出并删除当前片段目录下的配图；删除被正文引用的图片会先提醒并自动剥离引用（记得提交修改
使其生效）。后端接口：`/think/img_list`、`/think/img_delete`，防穿越与按用户隔离策略一致。

### 4.7 文篇编辑页：编辑/预览滚动跟随

编辑页（`src/views/csdn/post.vue`）勾选"跟随"后，左侧滚动时右侧预览同步跟随：

- **逐块配对锚点**：源 Markdown 按块划分（段落/标题/```代码围栏```/`$$` 公式块/列表/引用/
  表格/分割线），预览侧取渲染后的顶级块按顺序一一配对，构建"源滚动 px → 预览滚动 px"
  锚点表并分段线性插值；标题、图片加载、LaTeX 公式渲染高度、代码块高亮等造成的两侧
  高度失配都由下一个块锚点自动校正，而不是按整页比例硬算
- **可靠性兜底**：源块数与预览块数差异过大（渲染器合并/拆块）时自动退回"仅标题行锚点"，
  再不行退回整页比例映射；锚点要求严格单调递增，避免跳变
- **时机**：渲染完成、KaTeX 渲染完、图片全部加载完成后重建锚点（未加载完的图片等
  `load/error` 事件）；窗口 resize 也会重建
- **性能**：源侧像素用与 textarea 同样式的离屏镜像 div 测量，块划分纯字符串扫描

### 4.8 网址隐私：邮箱 → uid 映射

网址中永不出现邮箱（或形似手机号的前缀）。每个账号映射为一个随机 **36 位纯数字 uid**，
用户空间网址形如 `/#/165989218739189801318616830165629911` 或
`/#/think/<uid>?currentpage=1&pagesize=9`，不再包含邮箱。

- 映射模块：`mysite/uidmap.py`，持久化在 `mysite/uid_map.txt`（自动创建、线程安全、
  幂等——已映射的邮箱永远返回同一个 uid）。磁盘布局不变：目录仍是 `people/<邮箱>/`，
  仅在 URL 层做映射，既有的归属校验与统计全部沿用
- **注册**与**管理员新建用户**时即生成 uid；存量账号在首次被访问时
  （getusername / login / userlist）自动补建。要在服务器上一次性为全部存量账号建映射
  （可选，用与 Django 相同的 Python 环境执行）：

  ```bash
  cd mysite
  python3 manage.py shell -c '
  import os, uidmap
  from csdn import views as cv
  member = cv.MEMBER_TXT   # 凭据库已迁至部署根 data/member.txt
  n = 0
  for parts in cv._read_members(member)[1]:
      mail = parts[1]
      if mail and "@" in mail:
          print(mail, "->", uidmap.mail_to_uid(mail))
          n += 1
  print("done:", n, "members mapped")
  '
  ```

- `POST /csdn/getusername` 新增三个字段：`urluid`（URL 原始用户段——前端建链接一律用它）、
  `uid`（登录者自己的 uid）、`owneruid`（站长 uid，匿名/裸域回退跳转用）
- **旧邮箱形态网址彻底失效**：后端把含 `@` 的段按匿名处理（不返回任何该用户数据），
  前端把这类链接重定向到站长主页；用户空间写守卫按「页面主人（uid 还原为邮箱）与登录者
  身份比对」判定，文篇/图片/设置/think/视频/旅行等的归属权限不受影响
- 裸域名（`http://站点/`、`/#`、`/#/`）直达站长 uid 主页——`index.html` 内联脚本
  （应用启动前，localStorage 缓存 uid 兜底）+ 路由层 redirect 兜底
- 站长账号可在 `mysite/site_config.json` 的 `site_owner_mail` 配置
  （默认 `homepage@gmail.com`）

## 5. 并发与多用户说明

- 设计目标：每秒最多 100 个请求；同时在线人数不设上限（左侧栏实时显示当前在线数）
- 三层限流：
  - nginx `limit_req`（10 请求/秒，burst 20，nodelay）+ `limit_conn`（每 IP 20 并发连接），全部
    API location 共享计数
  - Django 防洪水中间件 `mysite/mysite/antiflood.py`（挂 MIDDLEWARE 首位）：突发 100 请求/秒、
    持续 3000 请求/分钟、`/admin*` 60 次/分钟，超限返回 429 + Retry-After；在线计数
    `mysite/online.py`（5 分钟滑动窗口按 IP 去重）也在此刷新
  - 敏感接口限流 `mysite/ratelimit.py`：登录 20 次/10 分钟、注册 5 次/小时、验证码同邮箱
    60 秒 1 封且每 IP 10 封/小时、找回密码校验 15 次/10 分钟
- 上传服务端二次校验（前端校验之外再拦一道）：图片（`/csdn/uploadImg`、`/csdn/mainpageuploadImg`）
  仅 jpg/jpeg/png/bmp/gif 且 ≤13MB；视频（`/upload_video/upload`）仅 mp4/webm 且 ≤2G；
  均校验文件头魔数（防改后缀伪装脚本/网页），文件名 basename 剥离路径成分防目录穿越
- 敏感数据封堵：member.txt 与 oldpassword/ 存部署根 `data/`（nginx 不服务）；nginx 对
  `article/` 下 member.txt、oldpassword/、register/clickpage 等数据 txt 全部 deny，
  防止直接下载用户表与统计库
- 文件写入使用 `threading.Semaphore` 信号量串行化（`memmute`、`regmute` 等），避免并发写坏 txt 文件
- 列表缓存按用户数据目录隔离（`allfile = {}` 以 basepath 为键），用户之间互不影响
- 前端构建做了代码分割（element-plus / katex / vendor 单独打包），利于浏览器缓存
- 生产环境建议用 gunicorn / uwsgi 多 worker 运行 Django，由 nginx 做负载与限流

## 6. Live2D 看板郎挂件与音乐播放器

### 6.1 看板郎挂件（仅桌面端 ≥768px 加载）

- 素材与逻辑自托管于 `public/live2d/`，加载入口在 `index.html` 内联脚本
  （solarlunar.min.js → live2d.min.js → waifu-tips.js 按序加载）
- 形象清单 `public/live2d/model_list.json`：23 个开源形象，9 大分类
  （全部/男性/女性/猫咪/狗狗/鸟类/熊猫/动漫/历史·仙神）
- 挂件工具栏：🎵 音乐 / 💬 聊天 / ⚙️ 选形象 / 🔄 切换 / 📷 拍照 / ✖️ 隐藏
- **可拖拽停靠**：按住看板郎任意处拖动即可移动（工具栏按钮除外），松手后位置存入
  localStorage（刷新/重开浏览器都保持）；双击看板郎复位到默认右下角；窗口缩放/浏览器
  变焦时拖拽位置自动钳回可视区（窗口恢复后回到记忆位置）
- 初始形象优先级：账号配置（`/csdn/get_widget`）> 本机记录（localStorage）>
  昼夜默认（20:00–次日 8:00 izumi，其余时间 haruto）
- 添加自定义形象：模型目录放入 `public/live2d/model/<id>/`（入口命名 `index.json`），
  再在 `model_list.json` 注册 `{id, name, category, desc}` 即可
- **节日系统（29 个中外节日，全天生效）**：农历节日（人日/元宵/上巳/端午/七夕/中元/中秋/重阳/下元/
  腊八/小年/除夕/春节，社日与三伏按干支推算）+ 公历节日（元旦/劳动节/国庆/清明）+ 国际节日
  （情人节/万圣节/感恩节/圣诞节/美国独立日）；节日期间多次祝福——首屏问候随机一句、闲聊时
  有一半概率插入节日祝福；节日窗口：春节初一到初九、国庆 7 天、劳动节 5 天、一般节日 3 天，
  七夕/情人节/重阳/除夕当天；祝福语全部去重（2020 条，春节/国庆各 200 条）
- **节日全屏特效**：每个节日有独立特效池（普通节日 12 种以上，元旦/中秋 20 种，春节/国庆 40 种），
  节日期间全天常驻、可视区全屏，进站随机 1 种、每 10 分钟随机换 1 种；发光元素叠加混合，
  重叠处更亮；节日特效默认开启不可关闭
- **平日特效（非节日，10000 种）**：7032 种基础元素（900 个图形家族：前 20 个手绘家族保持
  g1~g1000 老编号不变，后 880 个为程序化曲线家族——Gielis 超级公式、玫瑰线、星形多边形、
  内外摆线、利萨茹曲线、Maurer 星网、螺线、黄金角种子盘，以及闪电、DNA 双螺旋、苯环/分子、
  原子轨道、波包、星座、像素点阵、蝴蝶曲线、卡西尼卵形线、双纽线、纽结、泪滴、钟面/齿轮、
  拱桥、电路走线、算盘、函数曲线、三棱镜、苹果、星系、罗盘、蜂巢、雪晶、曼陀罗、风车、
  嫩芽、细胞等主题图形；109 个家族带双层嵌套参数档）× 8 套配色 × 5 档速度 × 3 档尺寸 ×
  4 档密度组合；曲线元素烘焙成 Path2D 缓存，28 个发光家族叠加混合；全天常驻、每 10 分钟
  随机换 1 种；94 个有来历的日子（牛顿/特斯拉/麦克斯韦/居里夫人/爱因斯坦/冯·诺依曼/袁隆平/
  屠呦呦等中外科学家纪念日，世界水日/地球日等世界日）当天特效按语义偏向对应元素——
  特斯拉→闪电、化学家→苯环、物理学家→原子、数学家→函数曲线/算盘/像素点阵、茅以升→拱桥、
  牛顿→三棱镜/苹果、天文学家→星座/星系、生物学家→细胞/DNA/蝴蝶；主题面板可开关
- **特效鼠标互动（1792 种随机预设）**：14 种移动力场（推开/吸附/环绕/涡旋/弹簧/果冻/点燃/冻结/
  分流/环形归位/尾风/引力井/弹球/磁吸抖散）× 16 种点击效果（爱心/星星迸发、彩带环、螺旋、喷泉、
  花开、黑洞、彩虹环、雨滴、粒子笼、引力爆发、星光领域、颜色洗牌、冲击波、流星雨等）× 8 种
  光标拖尾（星光/彗星/泡泡/爱心/星星/花瓣/星尘/无），全组合 1792 个命名预设随机抽取，每 10 分钟
  随特效轮换一起换，另有 5 档强度随机；约三分之一预设带看板郎力场——粒子绕角色公转（well）
  或角色附近点亮成光环（aura）；点击涟漪与冲击波附带可见扩散波纹
- **看板郎与用户互动**：悬停角色附近角色朝光标吹星星、光标快速掠过带起粒子风、点击角色迸发
  星星爱心并偶尔回应一句台词、2.5 秒内连点 5 次触发大爆发+摇晃+「别戳啦」台词、点击特效波及
  角色会被吓一跳冒泡泡、换装时旧形象炸星星新形象冒爱心、拍照/右键彩蛋配星光、闲置搭话冒爱心；
  特效每 9~16 秒从角色身上飘出一小股当前配色粒子，节日当天角色上场自带进场彩蛋
- **主题面板配置**：节日特效大小滑块（0.5–4 倍，默认 1.9）；**平日特效大小滑块**（0.5–4 倍，
  默认 1.8，曲线描边随尺寸加粗、粒子数量随面积补偿）；平日特效开关；手动指定平日特效的
  元素/配色/速度/尺寸（0.5–3 连续滑块）/密度（任意项可保持随机）；配置存 localStorage、
  改完立即生效
- **隐藏与恢复**：点 ✖️ 收起看板郎，右下角露出【看 板 郎】竖排标签（完整可见），点标签即恢复
- **稳健性**：语料 60 万字符进页面即预加载常驻内存，失效自动重拉；闲置后 WebGL 上下文被浏览器
  回收时自动重载模型，人物不会消失；闲聊一次随机 3 句、按字数延长气泡时长

### 6.2 音乐播放器（APlayer + Meting 多源容灾）

- 播放器模块 `src/music.js`（`src/main.js` 中 `initMusic()` 调用），APlayer fixed 模式悬浮于看板郎上方
- **可拖拽停靠**：按住播放器封面拖动即可移动整个播放器，松手后位置存入 localStorage
  （刷新保持）；双击封面复位到默认右下角；窗口缩放/浏览器变焦时拖拽位置自动钳回可视区，
  窄视口下默认位置与宽度自适应（不会超出屏幕左缘）
- 播放源多源容灾：`mysite/site_config.json` 的 `music_sources` 列表按顺序组成容灾链，**默认使用第一个可用源**；某源歌单拉取失败（502/空列表/不可播）或播放中音频报错（断链 403）时，前端自动切换下一个源并恢复播放，全部失效则停止并打印控制台告警
- 播放源可手动配置：增删改 `music_sources` 数组元素（字段 `name`/`server`/`type`/`id`，支持 netease/tencent/kugou/kuwo），保存刷新即生效；默认源覆盖 4 个平台（网易云/QQ 音乐/酷狗/酷我），单一平台接口故障不影响整体播放；删除该键回退 `siteconfig.py` 内置跨平台默认列表，空数组时回退旧单源字段 `music_server`/`music_type`/`music_id`
- 解析 API 多端点容灾：Django 代理 `/csdn/meting` 按 `music_apis` 端点列表逐个尝试（每端点含重试，超时/错误页/非 JSON 响应自动跳下一个），全部失效才报 502——前端随后切换下一个播放源；删除 `music_apis` 回退旧单端点 `music_api`
- 挂件 🎵 按钮 = 播放/暂停，开始播放时看板郎气泡报幕歌名

更多细节（与原仓库 crowya/live2d 的差异定制、文案、彩蛋等）见 [readme.txt](./readme.txt)。

## 7. 邮件设置（注册验证码）

文件 `mysite/csdn/views.py` 中函数 `mailsend(mail, modify=False, notify_guanliyuan=None)`：

```python
msg['From'] = '1069679911@qq.com'
smpt = smtplib.SMTP_SSL("smtp.qq.com", port=465)
smpt.login(user="1069679911@qq.com", password='<SMTP授权码>')
```

在 QQ 邮箱设置中开启 SMTP 服务并获取授权码后替换。

## 我的博客

[http://zoujiu.com.cn](http://zoujiu.com.cn)

[https://zoujiu.blog.csdn.net/](https://zoujiu.blog.csdn.net/)

## Reference

本项目开发过程中参考的官方文档与开源项目：

before 2026-10-30, no AI code

- [Vue.js](https://vuejs.org/)
- [Vite](https://vitejs.cn/vite3-cn/guide/)
- [Vue Router](https://router.vuejs.org/zh/)
- [Element Plus](https://element-plus.org/zh-CN/)
- [MDN Web Docs](https://developer.mozilla.org/en-US/)
- [live2d（crowya）](https://github.com/crowya/live2d)
