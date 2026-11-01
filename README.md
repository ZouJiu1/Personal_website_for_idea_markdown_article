> English | [简体中文](README_CN.md)

# Personal Website (Ideas / Markdown Articles / Books / Videos / Zhihu / Fragments / Guestbook / Quick Links / Images)

A personal website built on **Vue 3 + Element Plus + Django**. Live demo: [http://zoujiu.com.cn](http://zoujiu.com.cn)

- Markdown article authoring (KaTeX math, tables, lists, code highlighting, etc.)
- Book and video upload & playback (hls.js), Zhihu articles, idea fragments, guestbook, quick links, daily images
- No database: users, articles, and settings are all stored in plain text files (txt / markdown)
- Multi-user isolation: every registered user gets an independent `people/<username>/` data directory
- **URL privacy**: emails never appear in URLs — every account is mapped to a random 36-digit numeric
  uid (e.g. `/#/165984218734184801318416830165629911`), old email-form links are completely dead,
  and all generated links use the uid (see 4.8)
- Session persistence via js-cookie (30 days); registration, login, logout, and email-verification password reset
- Built-in draft box on the article publishing page: save drafts, list drafts, re-edit, delete; drafts auto-cleared after publishing (see 4.4)
- Article editor extras (see 4.5/4.6): **image management** — list/delete the images of an article or a fragment;
  deleting an image strips its references from the body and re-renders the preview; **historical documents** —
  every publish keeps a timestamped copy, readable (rendered), restorable into the editor, and deletable,
  with the current version protected
- Login dialog: press Enter in either input to log in (same as clicking the login button)
- Built-in admin panel: view user list, create users, reset passwords, change roles, delete users
- Built-in Live2D widget: 23 open-source characters in 9 categories, per-account memory (works across devices),
  all-day greetings + full-screen mouse-interactive particle effects on 29 Chinese & international festivals,
  plus everyday effects on normal days (900 shape families / 10000 variants)
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
│   ├── uidmap.py           # Email ↔ 36-digit uid mapping for URL privacy (persisted in uid_map.txt)
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
- nginx serves `/article` and `/people` with `Cache-Control: no-cache` (revalidation): unchanged files still
  hit a cheap 304, while images deleted via image management turn 404 immediately — no stale browser cache
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

After logging in, admins see a **Manage** entry in the left menu (route `/admin/<uid>`), which provides:

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

### 4.5 Article Editor: Image Management & Historical Documents

The editor page (`src/views/csdn/post.vue`) offers two management dialogs for the article owner (admins too):

- **Image management**: lists the images in the current article directory (thumbnail, size, upload time);
  deleting an image warns first if it is referenced by the body, then automatically strips the references
  (`<img src=...>` / `![...](...)`) from the editor content and re-renders the preview, so a deleted image
  disappears immediately instead of lingering via browser cache; re-publish to apply to the live article
- **Historical documents**: every publish keeps a timestamped Markdown copy in the article directory;
  the dialog lists all versions (the current one is tagged "current" and cannot be deleted) and supports:
  - **Read**: renders the chosen version in a dialog with the same preview pipeline (KaTeX, image paths rewritten)
  - **Restore**: loads that version's content back into the editor; re-publish to make it live
  - **Delete**: removes old versions after confirmation (the backend always rejects the current one)

Backend APIs: `/csdn/img_list`, `/csdn/img_delete`, `/csdn/history_list`, `/csdn/history_get`,
`/csdn/history_delete`; auth uses the request's own login identity (mail + password), paths are
realpath-confined to `people/`/`article/`, and regular users may only operate on their own directories.
Deleting an article (or a fragment, see 4.6) from the detail page returns to the list and reloads the
whole page, so the deleted entry disappears immediately instead of lingering in a stale list.

### 4.6 Fragment Detail Page: Image Management

The fragment detail page (`src/views/think_detail/tkdetail.vue`) offers the same image management dialog
(fragment owner / admins): list and delete the images of the current fragment directory; deleting an image
that is referenced by the fragment body warns first and strips the reference (submit the modification to
apply). Backend APIs: `/think/img_list`, `/think/img_delete`, with the same realpath confinement and
per-user isolation.

### 4.7 Editor Page: Editor/Preview Scroll Sync

On the editor page (`src/views/csdn/post.vue`), with the "跟随" (follow) checkbox on, scrolling the left
editor scrolls the right preview in sync:

- **Per-block paired anchors**: the source Markdown is split into blocks (paragraphs / headings /
  fenced code / `$$` math blocks / lists / quotes / tables / rules), and the preview's top-level
  rendered blocks are paired one-by-one in order, producing a "source scrollTop px → preview
  scrollTop px" anchor table with piecewise-linear interpolation; height mismatches from headings,
  image loading, LaTeX formula rendering, and code highlighting are all corrected by the next block
  anchor instead of a naive whole-page ratio
- **Reliability fallbacks**: if source and preview block counts diverge too much (renderer
  merging/splitting blocks), it falls back to heading-only anchors, and failing that to the
  whole-page proportional mapping; anchors must be strictly monotonic to avoid jumps
- **Timing**: anchors rebuild after rendering, after KaTeX rendering, and after all images have
  finished loading (pending images awaited via `load`/`error` events); window resizes also rebuild
- **Performance**: source-side pixels are measured with an off-screen mirror div styled exactly like
  the textarea; block splitting is a plain string scan

### 4.8 URL Privacy: Email → UID Mapping

URLs never expose emails (or phone-like prefixes). Every account is mapped to a random
**36-digit numeric uid**, so user-space URLs look like `/#/165984218734184801318416830165629911`
or `/#/think/<uid>?currentpage=1&pagesize=9` instead of containing the email.

- Mapping module: `mysite/uidmap.py`, persisted in `mysite/uid_map.txt` (auto-created, thread-safe,
  idempotent — a mapped email always gets the same uid back). On-disk layout is unchanged:
  directories stay `people/<email>/`; only the URL layer is mapped, so all existing ownership checks
  and statistics keep working
- Uids are generated at **registration** and **admin user creation**; existing accounts are mapped on
  first access (getusername / login / userlist). To map all existing accounts at once on the server
  (optional, same Python env as Django):

  ```bash
  cd mysite
  python3 manage.py shell -c '
  import os, uidmap
  from csdn import views as cv
  member = os.path.join(os.path.abspath(cv.__file__ + "/../../"), "..", "article", "member.txt")
  n = 0
  for parts in cv._read_members(member)[1]:
      mail = parts[1]
      if mail and "@" in mail:
          print(mail, "->", uidmap.mail_to_uid(mail))
          n += 1
  print("done:", n, "members mapped")
  '
  ```

- `POST /csdn/getusername` returns three extra fields: `urluid` (the raw URL segment — the frontend
  builds all links with it), `uid` (the logged-in user's own uid), `owneruid` (the site owner's uid,
  used for anonymous/bare-domain fallback jumps)
- **Old email-form URLs are completely dead**: the backend resolves an `@`-containing segment to
  anonymous (no user data is returned), and the frontend redirects such links to the site owner's
  homepage; user-space write guards compare the page owner (uid resolved to email) with the logged-in
  identity, so ownership of articles / images / settings / think / video / travel is unaffected
- Bare domain (`http://site/`, `/#`, `/#/`) jumps straight to the site owner's uid homepage — an
  inline script in `index.html` (before the app boots, backed by a localStorage-cached uid) plus a
  router-level redirect fallback
- The site owner account is configurable via `site_owner_mail` in `mysite/site_config.json`
  (default `homepage@gmail.com`)

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
  persisted in localStorage and survives reloads; double-click resets it to the default bottom-right corner;
  on window resize / browser zoom a dragged position is clamped back into the viewport (the remembered spot
  is restored when the window grows again)
- Character priority: account setting (`/csdn/get_widget`) > local record (localStorage) >
  day/night default (izumi from 20:00–8:00 next day, haruto otherwise)
- Adding a custom character: put the model directory in `public/live2d/model/<id>/` (entry named `index.json`),
  then register `{id, name, category, desc}` in `model_list.json`
- **Festival system (29 Chinese & international festivals, all-day)**: lunar festivals (Renri / Lantern /
  Shangsi / Duanwu / Qixi / Zhongyuan / Mid-Autumn / Chongyang / Xiayuan / Laba / Xiaonian / New Year's Eve /
  Spring Festival; she-ri and sanfu derived from ganzhi) + solar festivals (New Year's Day / Labor Day /
  National Day / Qingming) + international ones (Valentine's / Halloween / Thanksgiving / Christmas /
  US Independence Day); greetings fire multiple times a day — one random line on load plus a 50% chance to
  join each idle-chat batch; festival windows: Spring Festival day 1–9, National Day 7 days, Labor Day 5 days,
  most others 3 days, Qixi / Valentine's / Chongyang / New Year's Eve single-day; 2020 deduplicated lines
  (200 each for Spring Festival & National Day)
- **Festival full-screen effects**: each festival has its own effect pool (12+ for regular festivals, 20 for
  New Year's Day & Mid-Autumn, 40 for Spring Festival & National Day); effects stay all day across the
  viewport, one random effect on load and a new random one every 10 minutes; luminous elements are drawn
  additively so overlaps glow; festival effects are always on and cannot be disabled
- **Everyday effects (non-festival, 10000 variants)**: 7032 base elements (900 shape families — the
  first 20 hand-drawn families keep the old g1~g1000 numbering, the other 880 are procedural curve
  families: Gielis superformula, rose curves, star polygons, hypo/epicycloids, Lissajous figures,
  Maurer roses, spirals, golden-angle seed heads, plus themed shapes such as lightning bolts, DNA
  double helices, benzene rings & molecules, atomic orbits, wave packets, constellations, pixel grids,
  butterfly curves, Cassini ovals, lemniscates, knots, teardrops, clocks & gears, arch bridges,
  circuit traces, abacuses, function plots, prisms, apples, galaxies, compasses, honeycombs, snow
  crystals, mandalas, pinwheels, sprouts and cells; 109 families carry a nested two-layer param) ×
  8 palettes × 5 speeds × 3 sizes × 4 densities; curves are baked into cached Path2D objects and
  28 luminous families blend additively; all-day, one random variant on load, rotating every
  10 minutes; 94 memorable days (Newton / Tesla / Maxwell / Marie Curie / Einstein / von Neumann /
  Yuan Longping / Tu Youyou etc. scientist anniversaries and world days like World Water Day) bias
  the element choice semantically — Tesla → lightning, chemists → benzene, physicists → atoms,
  mathematicians → function plots / abacuses / pixel grids, Mao Yisheng → arch bridges, Newton →
  prism & apple, astronomers → constellations & galaxies, biologists → cells / DNA / butterflies;
  can be toggled in the theme panel
- **Mouse interaction**: particles are gently pushed away as the cursor sweeps by (the faster the
  cursor moves, the stronger the push), nearby particles light up and spin faster; clicking sends
  out a ripple push-wave (with the firework effect, a burst explodes right at the click point)
- **Theme panel config**: festival-effect size slider (0.5–4×, default 1.9); everyday-effects toggle; manual
  selection of the everyday effect's element / palette / speed / size / density (any of them can stay
  random); settings persist in localStorage and apply instantly
- **Hide & restore**: click ✖️ to collapse the widget and a fully visible vertical 【看 板 郎】 tab appears
  at the bottom-right; click the tab to bring it back
- **Robustness**: the 600K-char tips corpus is preloaded into memory on page load and re-fetched
  automatically if it ever goes missing; if the browser reclaims the WebGL context after long idling,
  the model reloads itself so the character never disappears; idle chat shows 3 random lines at a time,
  with the bubble duration scaled to the text length

### 6.2 Music Player (APlayer + Meting multi-source failover)

- Player module `src/music.js` (invoked by `initMusic()` in `src/main.js`); APlayer fixed mode floats above the widget
- **Draggable & dockable**: drag the player cover to move the whole player; the position is persisted in
  localStorage and survives reloads; double-click the cover to reset to the default bottom-right corner;
  on window resize / browser zoom a dragged position is clamped back into the viewport, and the default
  position/width adapt on narrow viewports (no overflowing the screen left edge)
- Multi-source failover: the `music_sources` list in `mysite/site_config.json` forms an ordered failover chain — **the first working source is used by default**; when a playlist fetch fails (502/empty/unplayable) or playback errors mid-stream (e.g. 403), the frontend automatically switches to the next source and resumes playing; if all sources fail it stops and logs a console warning
- Sources are configurable: edit the `music_sources` array (fields `name`/`server`/`type`/`id`; netease/tencent/kugou/kuwo supported) — takes effect after a refresh; the defaults span 4 platforms (NetEase / QQ Music / Kugou / Kuwo) so a single platform outage does not kill playback; deleting the key falls back to the built-in cross-platform list in `siteconfig.py`, and an empty array falls back to the legacy single-source fields `music_server`/`music_type`/`music_id`
- Multi-endpoint API failover: the Django proxy `/csdn/meting` tries the `music_apis` endpoints in order (each with retries; timeouts / error pages / non-JSON responses cause a skip to the next endpoint) before returning 502 — the frontend then switches to the next playback source; deleting `music_apis` falls back to the single legacy `music_api`
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
