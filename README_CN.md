> English | [简体中文](README_CN.md)

# 个人网站（想法 / Markdown 文章 / 图书 / 视频 / 知乎 / 片段 / 游客 / 常用 / 图片）

基于 **Vue 3 + element-plus + Django** 的个人网站，线上示例：[http://zoujiu.com.cn](http://zoujiu.com.cn)

- 支持 Markdown 文章创作（数学公式 KaTeX、表格、列表、代码高亮等）
- 支持图书、视频上传与播放（hls.js）、知乎文章、想法片段、游客留言、常用网站、每日图片
- 不使用数据库：用户、文章、设置等全部保存在 txt / markdown 等文本文件中
- 多用户隔离：每个注册用户拥有独立的 `people/<用户名>/` 数据目录，互不影响
- js-cookie 维持登录态（30 天），支持注册、登录、登出、邮箱验证码改密
- 文篇发布页内置草稿箱：保存草稿、草稿箱列表、再次编辑、删除，发布成功自动清稿（见 4.4）
- 内置注册管理页面：管理员可查看用户列表、新建用户、重置密码、修改权限、删除用户
- 内置 Live2D 看板郎挂件：23 个开源形象按 9 大分类自选，账号级记忆（换设备也生效），
  农历传统节日（春节 / 中秋 / 除夕等）自动换上节日问候语
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
│   ├── csdn/               # 文篇 + 用户注册/登录/管理接口
│   ├── zhihu/ think/ video/ travel/ commonuse/ markdown_detail/ upload_video/
│   └── manage.py
├── article/                # 公共数据（member.txt 用户表、register.txt 验证码、文章等）
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
python3 manage.py runserver localhost:7009
```

浏览器访问 `http://localhost:9000`。

- 后端地址可用环境变量覆盖：`DJANGO_TARGET=http://127.0.0.1:7009 npm run dev`
- DEBUG 模式下 Django 会直接提供 `/article`、`/people`、`/hls` 静态资源

## 3. 生产部署（nginx）

```bash
# 打包前端，产物在 dist/
npm run build

# 启动后端（生产务必以 DJANGO_DEBUG=0 关闭调试，静态资源改由 nginx 伺服）
source ./venv/bin/activate
cd mysite
DJANGO_DEBUG=0 python3 manage.py runserver localhost:7009
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
- 上传接口仅接受图片扩展名（jpg/jpeg/png/bmp/gif），文件名已剥离路径成分
- 删除接口（delete）与管理员代编辑/代传图均限制在项目 `people/`、`article/` 目录内，防路径穿越
- 生产建议 gunicorn/uwsgi 多 worker 运行并由 nginx 限流（见「并发与多用户说明」）

nginx 配置参考 [nginx_http.conf](./nginx_http.conf) 或 [nginx_https.conf](./nginx_https.conf)，按实际目录修改：

- `dist/` 作为前端静态根目录
- `/article`、`/people`、`/hls` 指向项目根目录下的同名目录
- `/csdn`、`/zhihu`、`/think`、`/video`、`/travel`、`/commonuse`、`/markdown_detail`、`/upload_video` 等接口前缀 proxy_pass 到 `http://localhost:7009`

常用命令：

```bash
nginx -c /path/to/nginx.conf   # 启动
nginx -s reload                # 重载配置
nginx -s stop                  # 停止
```

## 4. 用户与权限

### 4.1 用户文件格式

用户保存在 `article/member.txt`，每行一个用户，字段以 `<》!=$)(=$@` 分隔：

```
<密码哈希><》!=$)(=$@<邮箱><》!=$)(=$@<昵称><》!=$)(=$@<权限>
```

密码哈希只允许加盐格式：`sha256s$<盐>$<sha256(盐+前端sha256值)>`。
旧格式（裸 sha256）已彻底弃用：后端一律校验失败，旧用户需重新注册。
权限字段为整数，`999999999` 表示站长，`1000000` 表示超级管理员，`100` 表示普通管理员，`1` 表示普通用户。

### 4.2 注册管理页面（管理员）

管理员登录后，左侧菜单会出现 **管理** 入口（路由 `/admin/<用户名>`），功能包括：

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

将输出的 `sha256s$盐$摘要` 整串替换 `article/member.txt` 中管理员行的第一段即可
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

## 5. 并发与多用户说明

- 设计目标：最多 1000 人同时在线，每秒最多 100 个请求
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
  localStorage（刷新/重开浏览器都保持）；双击看板郎复位到默认右下角
- 初始形象优先级：账号配置（`/csdn/get_widget`）> 本机记录（localStorage）>
  昼夜默认（20:00–次日 8:00 izumi，其余时间 haruto）
- 添加自定义形象：模型目录放入 `public/live2d/model/<id>/`（入口命名 `index.json`），
  再在 `model_list.json` 注册 `{id, name, category, desc}` 即可
- 农历传统节日问候：加载时按当天公历换算农历，命中春节 / 元宵 / 龙抬头 / 上巳 /
  端午 / 七夕 / 中元 / 中秋 / 重阳 / 腊八 / 小年 / 除夕（动态判断）时，
  节日问候语取代时段欢迎语，并加入看板郎随机闲聊池；闰月不参与匹配

### 6.2 音乐播放器（APlayer + Meting 多源容灾）

- 播放器模块 `src/music.js`（`src/main.js` 中 `initMusic()` 调用），APlayer fixed 模式悬浮于看板郎上方
- **可拖拽停靠**：按住播放器封面拖动即可移动整个播放器，松手后位置存入 localStorage
  （刷新保持）；双击封面复位到默认右下角
- 播放源多源容灾：`mysite/site_config.json` 的 `music_sources` 列表按顺序组成容灾链，**默认使用第一个可用源**；某源歌单拉取失败（502/空列表/不可播）或播放中音频报错（断链 403）时，前端自动切换下一个源并恢复播放，全部失效则停止并打印控制台告警
- 播放源可手动配置：增删改 `music_sources` 数组元素（字段 `name`/`server`/`type`/`id`，支持 netease/tencent/kugou/kuwo），保存刷新即生效；删除该键回退 `siteconfig.py` 内置默认 3 个网易云榜单，空数组时回退旧单源字段 `music_server`/`music_type`/`music_id`
- Meting 请求经 Django 服务端代理 `/csdn/meting` 转发（含重试），避免浏览器直连被断连/跨域拦截
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

- [Vue.js](https://vuejs.org/)
- [Vite](https://vitejs.cn/vite3-cn/guide/)
- [Vue Router](https://router.vuejs.org/zh/)
- [Element Plus](https://element-plus.org/zh-CN/)
- [MDN Web Docs](https://developer.mozilla.org/en-US/)
- [live2d（crowya）](https://github.com/crowya/live2d)
