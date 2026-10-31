> English | [简体中文](README_CN.md)

# Personal Website (Ideas / Markdown Articles / Books / Videos / Zhihu / Fragments / Guestbook / Quick Links / Images)

A personal website built on **Vue 3 + Element Plus + Django**. Live demo: [http://zoujiu.com.cn](http://zoujiu.com.cn)

- Markdown article authoring (KaTeX math, tables, lists, code highlighting, etc.)
- Book and video upload & playback (hls.js), Zhihu articles, idea fragments, guestbook, quick links, daily images
- No database: users, articles, and settings are all stored in plain text files (txt / markdown)
- Multi-user isolation: every registered user gets an independent `people/<username>/` data directory
- Session persistence via js-cookie (30 days); registration, login, logout, and email-verification password reset
- Built-in draft box on the article publishing page: save drafts, list drafts, re-edit, delete; drafts auto-cleared after publishing (see 4.4)
- Built-in admin panel: view user list, create users, reset passwords, change roles, delete users
- Built-in Live2D widget: 23 open-source characters in 9 categories, per-account memory (works across devices),
  automatic holiday greetings on lunar-calendar festivals (Spring Festival / Mid-Autumn / New Year's Eve, etc.)
- Built-in music player (APlayer + Meting NetEase playlist, proxied by Django), floating above the widget on desktop
- Both the widget and the music player are draggable and dockable: drag to reposition (persisted in
  localStorage and restored on reload); double-click the widget / the player cover to reset
- Responsive layout: works on phones, tablets, and desktops

## Directory Structure

```
Personal_website_for_idea_markdown_article/
├── src/                    # Vue 3 frontend source
│   ├── views/              # Feature pages (home/csdn/zhihu/think/video/travel/...)
│   │   └── admin/          # Admin panel (admin only)
│   ├── router/routers.js   # Frontend routes (hash mode)
│   ├── common.js           # Shared helpers such as getusername (relative-path requests)
│   └── assets/main.css     # Global styles + responsive rules
├── mysite/                 # Django backend
│   ├── mysite/projectpaths.py  # Auto-locates the project root (no hardcoded absolute paths)
│   ├── csdn/               # Articles + user registration/login/admin APIs
│   ├── zhihu/ think/ video/ travel/ commonuse/ markdown_detail/ upload_video/
│   └── manage.py
├── article/                # Shared data (member.txt user table, register.txt codes, articles, etc.)
├── people/<username>/      # Per-user isolated data directory
├── public/live2d/          # Live2D widget assets (engine/styles/scripts/lunar library/23 model dirs)
├── vite.config.js          # Vite config (dev proxy to Django, build code splitting)
├── nginx_http.conf         # Production nginx config example (http)
└── nginx_https.conf        # Production nginx config example (https)
```

## 1. Prerequisites

### 1.1 Node.js

Install Node.js (v18+ recommended) from [https://nodejs.org/en/download](https://nodejs.org/en/download).

On macOS with Homebrew: `brew install node@22`

Optional registry mirror (mainland China):

```bash
npm config set registry https://registry.npmmirror.com
```

### 1.2 Install Frontend Dependencies

```bash
cd Personal_website_for_idea_markdown_article
npm install
```

Main dependencies: `vue` `vue-router` `element-plus` `axios` `js-cookie` `katex` `hls.js` `aplayer` (the widget music player); the widget's lunar-calendar conversion uses a self-hosted UMD build `public/live2d/solarlunar.min.js` (npm package solarlunar)

### 1.3 Python Environment

```bash
cd Personal_website_for_idea_markdown_article
python3 -m venv ./venv
source ./venv/bin/activate
python3 -m pip install -r ./mysite/requirements.txt
```

## 2. Local Development (no nginx required)

All frontend requests use relative paths; the Vite dev server automatically proxies `/csdn`, `/zhihu`, `/article`, `/people`, etc. to Django, so local development needs **no nginx**.

```bash
# Terminal 1: frontend (default port is 5173, customizable)
npm run dev -- --port 9000

# Terminal 2: backend
source ./venv/bin/activate
cd mysite
python3 manage.py runserver localhost:7009
```

Open `http://localhost:9000` in your browser.

- The backend address can be overridden via env var: `DJANGO_TARGET=http://127.0.0.1:7009 npm run dev`
- In DEBUG mode Django serves `/article`, `/people`, and `/hls` static files directly

## 3. Production Deployment (nginx)

```bash
# Build the frontend; output goes to dist/
npm run build

# Start the backend (in production set DJANGO_DEBUG=0 and let nginx serve static files)
source ./venv/bin/activate
cd mysite
DJANGO_DEBUG=0 python3 manage.py runserver localhost:7009
```

### Release Checklist

- `DJANGO_DEBUG=0`: local development enables DEBUG by default (runserver serves `/article` `/people` `/hls` directly);
  in production it must be 0 and nginx should serve these three directories. Note the **active settings live in the inner `mysite/mysite/settings.py`**
- `ALLOWED_HOSTS` is limited to `zoujiu.com.cn` / `121.40.168.141` / `localhost` / `127.0.0.1`;
  update `mysite/mysite/settings.py` when changing domains
- `SECRET_KEY`: prefers the env var `DJANGO_SECRET_KEY`, then `mysite/secret_key.txt`
  (a random key has been generated and is `.gitignore`d — never commit it)
- CSRF: `ScopedCsrfMiddleware` in `mysite/middleware.py` only enforces checks for Django admin (`/admin`);
  custom APIs authenticate via body params (no cookies) and are inherently CSRF-immune
- Passwords are only stored in salted format (`sha256s$<salt>$<digest>`); the legacy bare-sha256 format is fully
  deprecated and always fails verification — legacy users must re-register (see 4.1)
- Upload APIs only accept image extensions (jpg/jpeg/png/bmp/gif) and file names are stripped of path components
- Delete APIs and admin proxy-edit/proxy-upload are confined to the project's `people/` and `article/` directories to prevent path traversal
- In production, run Django with multiple gunicorn/uwsgi workers and apply rate limiting at nginx (see "Concurrency & Multi-user Notes")

See [nginx_http.conf](./nginx_http.conf) or [nginx_https.conf](./nginx_https.conf) for nginx config references, and adjust paths to your setup:

- `dist/` as the frontend static root
- `/article`, `/people`, `/hls` mapped to the same-named directories under the project root
- API prefixes such as `/csdn`, `/zhihu`, `/think`, `/video`, `/travel`, `/commonuse`, `/markdown_detail`, `/upload_video` proxied via proxy_pass to `http://localhost:7009`

Common commands:

```bash
nginx -c /path/to/nginx.conf   # start
nginx -s reload                # reload config
nginx -s stop                  # stop
```

## 4. Users & Permissions

### 4.1 User File Format

Users are stored in `article/member.txt`, one per line, fields separated by `<》!=$)(=$@`:

```
<password hash><》!=$)(=$@<email><》!=$)(=$@<nickname><》!=$)(=$@<role>
```

Password hashes must use the salted format: `sha256s$<salt>$<sha256(salt + frontend-sha256-value)>`.
The legacy bare-sha256 format is fully deprecated: the backend always rejects it, so legacy users must re-register.
The role field is an integer: `999999999` = site owner, `1000000` = super admin, `100` = regular admin, `1` = regular user.

### 4.2 Admin Panel (admins)

After logging in, admins see a **Manage** entry in the left menu (route `/admin/<username>`), which provides:

- View all registered users (username, email, nickname, role, whether the data directory exists)
- Create users (site owner / super admin only: create directly in the panel with email, username, and password)
- Reset any user's password
- Change user roles
- Delete users (personal data is automatically backed up to `article/deleted_users/`; the site-owner account is protected and cannot be deleted)

Backend APIs: `/csdn/admin_userlist`, `/csdn/admin_createuser`, `/csdn/admin_resetpass`, `/csdn/admin_setquanxian`, `/csdn/admin_deleteuser` — all verify admin identity.

### 4.3 Change the Admin Password

```bash
cd <project root>
# Pass the new password via --pw (or edit the default value in the script)
python3 genpassword.py --pw <new password>
```

Replace the first field of the admin row in `article/member.txt` with the printed `sha256s$salt$digest`
(the frontend sends the sha256 value on login; the backend verifies the salted format).

### 4.4 Draft Box (Article Publishing Page)

The publishing page (`/csdn/post_article`) offers drafts for logged-in users:

- **Save draft**: stores the current title and Markdown content into the personal draft box
  (`people/<username>/draft/<timestamp>.json`), up to 100 drafts per user
- **Draft box**: a dialog lists all drafts (title + save time), supporting:
  - **Re-edit**: refills the title and content for further editing; saving overwrites the original draft
  - **Delete**: removes a draft after confirmation
- **Auto-clear on publish**: after an article loaded from a draft is published successfully, that draft is removed automatically

Backend APIs: `/csdn/save_draft`, `/csdn/draft_list`, `/csdn/draft_get`, `/csdn/draft_delete`;
auth is identical to other write APIs (mail + password verified against member.txt);
draft directories are isolated per user and draft IDs accept digits only to prevent path injection.

## 5. Concurrency & Multi-user Notes

- Design targets: up to 1,000 concurrent users and 100 requests per second
- File writes are serialized with `threading.Semaphore` (`memmute`, `regmute`, etc.) to prevent concurrent corruption of txt files
- List caches are isolated per user data directory (`allfile = {}` keyed by basepath), so users never interfere with each other
- The frontend build applies code splitting (element-plus / katex / vendor as separate chunks) for better browser caching
- In production, run Django with multiple gunicorn/uwsgi workers and let nginx handle load balancing and rate limiting

## 6. Live2D Widget & Music Player

### 6.1 Live2D Widget (desktop ≥768px only)

- Assets and logic are self-hosted in `public/live2d/`; loaded by the inline script in `index.html`
  (solarlunar.min.js → live2d.min.js → waifu-tips.js, in order)
- Character list `public/live2d/model_list.json`: 23 open-source characters in 9 categories
  (all / male / female / cats / dogs / birds / panda / anime / history & deities)
- Widget toolbar: 🎵 music / 💬 chat / ⚙️ choose character / 🔄 switch / 📷 photo / ✖️ hide
- **Draggable & dockable**: drag anywhere on the widget to move it (toolbar buttons excluded); the position is
  persisted in localStorage and survives reloads; double-click resets it to the default bottom-right corner
- Character priority: account setting (`/csdn/get_widget`) > local record (localStorage) >
  day/night default (izumi from 20:00–8:00 next day, haruto otherwise)
- Adding a custom character: put the model directory in `public/live2d/model/<id>/` (entry named `index.json`),
  then register `{id, name, category, desc}` in `model_list.json`
- Lunar festival greetings: on load, the lunar date is derived from the solar date; when it hits a festival
  (Spring Festival / Lantern / Longtaitou / Shangsi / Duanwu / Qixi / Zhongyuan / Mid-Autumn / Chongyang / Laba / Xiaonian / New Year's Eve, dynamically detected),
  the greeting replaces the time-of-day welcome and joins the widget's random chat pool; leap months are excluded

### 6.2 Music Player (APlayer + Meting multi-source failover)

- Player module `src/music.js` (invoked by `initMusic()` in `src/main.js`); APlayer fixed mode floats above the widget
- **Draggable & dockable**: drag the player cover to move the whole player; the position is persisted in
  localStorage and survives reloads; double-click the cover to reset to the default bottom-right corner
- Multi-source failover: the `music_sources` list in `mysite/site_config.json` forms an ordered failover chain — **the first working source is used by default**; when a playlist fetch fails (502/empty/unplayable) or playback errors mid-stream (e.g. 403), the frontend automatically switches to the next source and resumes playing; if all sources fail it stops and logs a console warning
- Sources are configurable: edit the `music_sources` array (fields `name`/`server`/`type`/`id`; netease/tencent/kugou/kuwo supported) — takes effect after a refresh; deleting the key falls back to the 3 built-in NetEase playlists in `siteconfig.py`, and an empty array falls back to the legacy single-source fields `music_server`/`music_type`/`music_id`
- Meting requests are proxied through the Django endpoint `/csdn/meting` (with retries) to avoid direct-browser blocking/cors issues
- The widget's 🎵 button toggles play/pause; when a song starts, the widget announces it in a speech bubble

See [readme.txt](./readme.txt) for more details (customizations relative to the upstream crowya/live2d, scripts, easter eggs, etc.).

## 7. Mail Setup (Registration Verification Codes)

In `mysite/csdn/views.py`, function `mailsend(mail, modify=False, notify_guanliyuan=None)`:

```python
msg['From'] = '1069679911@qq.com'
smpt = smtplib.SMTP_SSL("smtp.qq.com", port=465)
smpt.login(user="1069679911@qq.com", password='<SMTP auth code>')
```

Enable SMTP in your QQ Mail settings, get an auth code, and replace the placeholder.

## My Blog

[http://zoujiu.com.cn](http://zoujiu.com.cn)

[https://zoujiu.blog.csdn.net/](https://zoujiu.blog.csdn.net/)

## Reference

Official docs and open-source projects referenced during development:

- [Vue.js](https://vuejs.org/)
- [Vite](https://vitejs.cn/vite3-cn/guide/)
- [Vue Router](https://router.vuejs.org/zh/)
- [Element Plus](https://element-plus.org/zh-CN/)
- [MDN Web Docs](https://developer.mozilla.org/en-US/)
- [live2d (crowya)](https://github.com/crowya/live2d)
