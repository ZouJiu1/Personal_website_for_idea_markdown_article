========================================================
Live2D 看板郎（多分类形象库 + 用户自选形象）集成说明
========================================================

一、功能与素材来源（Reference）
1. 挂件脚本来源：https://github.com/crowya/live2d
   - 项目根目录 live2d/ 为该仓库的完整克隆；
   - public/live2d/ 中的 live2d.min.js 与 waifu.css 直接取自该仓库，
     waifu-tips.js / waifu-tips.json / model_list.json 在其基础上重写定制；
   - 该仓库基于 stevenjoezhang/live2d-widget 二次开发，特此致谢。
2. 形象模型来源（均为开源 npm 包或克隆仓库自带）：
   - 男性：live2d-widget-model-{haruto,izumi,chitose,hibiki}
   - 女性：shizuku / kesyoban（克隆仓库）/ koharu / haru01 / haru02 /
           nico / nito / nipsilon / tsumiki / z16
   - 猫咪：tororo（白猫虎白）、hijiki（黑猫羊羹），取自克隆仓库
   - 狗狗：live2d-widget-model-wanko（柴犬小圆）
   - 动漫：miku（初音未来）/ unitychan（Unity酱）/ epsilon2_1 / gf / pio
   - 历史·仙神：nietzsche（尼采）
   - 模型文件均已复制到 public/live2d/model/<id>/，
     包内 *.model.json 统一重命名为 index.json（加载器约定入口名）。
3. 渲染引擎：live2d.min.js（Live2D web core，随 crowya/live2d 仓库分发）。
4. 关于「鸟类 / 熊猫 / 孙悟空等仙神」：目前没有可靠的开源 Live2D 模型包
  （npm 上无 piyo/panda 等可用包，GitHub 公开仓库也未找到可商用/可自托管的
   孙悟空模型），分类已预留（选择器中显示提示），可自行获取模型后按下文添加。

二、与原仓库（crowya/live2d）的差异定制
1. 原仓库为女性语气文案、面向 Hexo 博客（依赖 jQuery + APlayer 音乐播放器 +
   FontAwesome）。本站为 Django + Vue(Element Plus)，故：
   - 音乐播放器改为本站独立模块（src/music.js，见下文）；
   - 删除 jQuery 依赖（$("#live2d") 改为原生 addEventListener）；
   - 工具按钮由 FontAwesome 图标改为 emoji（🎵 音乐 / 💬 聊天 / ⚙️ 选形象 /
     🔄 切换 / 📷 拍照 / ✖️ 隐藏），对应样式选择器由 .fa-* 改为 .tool-*；
   - waifu-tips.json 全部文案重写为中文，提示选择器改为本站
     Element Plus 组件（通知铃 [title='通知']、.el-menu-item、.el-textarea__inner 等）；
   - 一言接口（v1.hitokoto.cn）请求失败时补充了兜底提示。
2. 仅桌面端（screen.width >= 768）加载；加载入口在 index.html 内联脚本，
   资源自托管于 public/live2d/（Vite 按根路径 /live2d/ 伺服，dev 与 build 均生效）。
3. 模型标识由数字下标改为字符串 id（= model/<id>/ 目录名）。
   初始形象优先级：账号配置 > 本机记录（localStorage: waifu-model）>
   昼夜默认（20:00-次日 8:00 izumi，其余时间 haruto）。
4. 折叠标签文案由「猫 咪」改为「看 板 郎」。

三、多分类形象库与用户自选形象
1. 形象清单：public/live2d/model_list.json
   - categories：分类表（全部/男性/女性/猫咪/狗狗/鸟类/熊猫/动漫/历史仙神）；
   - models：每项 {id, name, category, desc}，id 即 model/<id>/ 目录名。
2. 前端选择器：挂件工具栏 ⚙️ 按钮打开，按分类 tab 筛选形象卡片；
   点选即切换形象并保存：
   - 已登录：POST /csdn/set_widget 保存到账号（people/<mail>/widget.json），
     换设备也生效；下次整页加载时 /csdn/get_widget 自动恢复；
   - 未登录：仅写 localStorage（本机生效）。
3. 后端接口（mysite/csdn/views.py + urls.py）：
   - POST /csdn/get_widget  {mail, password} → {ret, widget}
   - POST /csdn/set_widget  {mail, password, widget:{model}} → {ret}
   - 认证方式与其他接口一致（member.txt 校验）。
4. 如何添加自己的形象（用户可自行配置）：
   - 把模型目录放进 public/live2d/model/<你的id>/（入口必须叫 index.json）；
   - 在 public/live2d/model_list.json 的 models 数组注册一项
     {id, name, category, desc}；
   - 刷新页面即可在选择器中看到；也可给 model_list.json 新增分类。

四、文件清单
public/live2d/
├── live2d.min.js        模型渲染引擎（源自 crowya/live2d）
├── waifu.css            挂件样式（含 ⚙️ 形象选择器样式）
├── waifu-tips.js        挂件逻辑（多分类形象库 + 用户自选 + 选择器 + 农历节日问候）
├── waifu-tips.json      提示文案（中文 + 本站选择器）
├── solarlunar.min.js    公历→农历换算库（npm solarlunar 的 UMD 版，index.html 先于 waifu-tips.js 加载）
├── model_list.json      分类表 + 形象清单（23 个形象）
└── model/               haruto izumi chitose hibiki shizuku kesyoban koharu
                         haru01 haru02 nico nito nipsilon tsumiki z16
                         tororo hijiki wanko miku unitychan epsilon2_1 gf
                         pio nietzsche（各含 index.json）

========================================================
音乐播放器与彩蛋功能说明
========================================================

一、音乐播放器（APlayer + Meting 在线歌单）
1. 技术来源（Reference）：
   - APlayer 播放器：https://github.com/DIYgod/APlayer （npm 包 aplayer，Vite 打包）
   - Meting 协议 API：https://github.com/metowolf/Meting （公共实例 api.i-meto.com）
2. 实现文件：
   - src/music.js    播放器初始化模块（src/main.js 中 initMusic() 调用）
   - mysite/site_config.json 中 music_* 配置键（enabled/api/server/type/id），
     经 /csdn/getSiteConfig 白名单（mysite/csdn/views.py getSiteConfig）下发
3. 行为：
   - 桌面端（>=768px）加载，APlayer fixed 模式悬浮在 Live2D 看板郎上方（waifu.css 控制）；
   - 默认歌单为网易云音乐热歌榜（music_id=3778678），改 site_config.json 即可换歌单；
   - Meting 请求经本站 Django 服务端代理 /csdn/meting 转发（含 3 次重试），
     避免浏览器直连公共 Meting API 被断连/跨域拦截；
   - Live2D 挂件 🎵 按钮 = 播放/暂停；开始播放时看板郎气泡报幕歌名；
   - 切歌/进度/音量由 APlayer 自行记忆（localStorage: zoujiu-aplayer）。

二、彩蛋与小功能
1. 标签页标题彩蛋：切走标签标题变「(●—●)等你回来…」，切回变「(◍•ᴗ•◍)欢迎回来！」
   （public/live2d/waifu-tips.js）。
2. 键盘彩蛋：任意页面连按 666，看板郎气泡夸夸。
3. 回到顶部按钮：右下角 el-backtop，滚动出现在 src/App.vue。
4. 农历传统节日问候（public/live2d/waifu-tips.js）：
   - 挂载页加载时按当天公历经 solarlunar 换算农历，命中传统节日则用节日
     问候语取代时段欢迎语（如「今天是农历九月初九「重阳节」…」）；
   - 覆盖：春节、元宵、龙抬头、上巳、端午、七夕、中元、中秋、重阳、
     腊八、小年（腊月廿三/廿四）+ 除夕（动态判断：明天是正月初一即为除夕）；
   - 节日祝福语同时加入看板郎的随机闲聊池，节日当天会主动提起；
   - 闰月日期不参与匹配；节日表与文案在 waifu-tips.js 的 LUNAR_FESTIVALS，可自行增改。
