// 站点音乐播放器：APlayer（fixed 模式）+ Meting 协议在线歌单。
// 与看板郎（Live2D）完全分离、互不依赖：播放器直接挂 document.body，自带独立的
// 拖拽移动（按住封面/歌名区拖动，≥5px 生效）、双击封面复位默认位置、
// localStorage(aplayer_pos) 位置记忆；看板郎的移动/停靠在 index.html attachWaifuDrag，各自独立。
// 播放源多源容灾：源列表来自 mysite/site_config.json 的 music_sources（可手动配置），
// 默认用列表第一个可用源；某源歌单拉取失败/返回为空/播放中音频报错时自动切换下一个源。
// 播放时广播 window 事件 'waifu-song'，看板郎（public/live2d/waifu-tips.js）据此报幕。
import APlayer from 'aplayer'
import 'aplayer/dist/APlayer.min.css'

// 播放器独立样式：默认贴屏幕右下（right 让出看板郎默认占位 250px + 20px 间距，二者不重叠）。
// 底部上抬 34px，避开页脚右下角的日期时间。
// APlayer 自带的 body/lrc 是 position:fixed 锚定视口，这里改为 absolute 锚定容器，
// 拖拽容器 left/top 时整体跟随。仅作用于播放器自身，与 #waifu 无任何关联。
const PLAYER_CSS = `
.aplayer * { color: #666; }
.aplayer.aplayer-fixed {
	position: fixed; left: auto; right: 270px; bottom: 34px;
	/* 宽度上限跟随视口：浏览器放大/窗口缩窄后不会超出屏幕左侧 */
	width: 400px; max-width: calc(100vw - 16px); margin: 0;
	/* 播放器压在页脚与看板郎之上会遮挡内容：降级到看板郎(#waifu z-index:1)之下，
	   二者即使碰在一起也由看板郎居上，不再出现“播放器跑到 live2d 上面”。 */
	z-index: 0;
}
.aplayer.aplayer-fixed .aplayer-body {
	position: absolute; left: auto; right: 0; bottom: 0;
	width: 400px; max-width: calc(100vw - 16px); margin: 0;
	z-index: 0;
}
.aplayer.aplayer-fixed .aplayer-lrc {
	position: absolute; left: 0; right: 0; bottom: 0; margin: 0;
	z-index: 0;
}
.aplayer.aplayer-fixed.aplayer-narrow .aplayer-lrc { opacity: 0; }
/* 窄视口（浏览器放大后视口 <720px）：右下让位缩小，避免与屏幕边缘/看板郎挤压出屏 */
@media (max-width: 720px) {
	.aplayer.aplayer-fixed { right: 8px; bottom: 8px; }
}
`

let styleInjected = false
function injectStyle() {
	if (styleInjected) return
	styleInjected = true
	const s = document.createElement('style')
	s.textContent = PLAYER_CSS
	document.head.appendChild(s)
}

// 读取多源配置：优先 music_sources（过滤缺 server/id 的无效项），为空时回退旧单源字段
async function loadSources() {
  const cfg = await fetch('/csdn/getSiteConfig').then(r => r.json())
  if (!cfg.music_enabled) return []
  let sources = Array.isArray(cfg.music_sources)
    ? cfg.music_sources.filter(s => s && s.server && s.id)
    : []
  if (!sources.length && cfg.music_server && cfg.music_id) {
    sources = [{ name: '', server: cfg.music_server, type: cfg.music_type || 'playlist', id: cfg.music_id }]
  }
  return sources
}

// 拉取某源歌单并映射为 APlayer 音频字段；非数组/空列表/全部无播放地址视为该源失效
async function fetchPlaylist(source) {
  const url = `/csdn/meting?server=${source.server}&type=${source.type || 'playlist'}&id=${source.id}`
  const list = await fetch(url).then(r => r.json())
  if (!Array.isArray(list) || list.length === 0 || !list.some(s => s.url)) {
    throw new Error('歌单为空或不可播放')
  }
  return list.map(s => ({
    name: s.name || s.title,
    artist: s.artist || s.author,
    url: s.url,
    cover: s.cover || s.pic,
    lrc: s.lrc,
  }))
}

// —— 播放器独立拖拽/停靠（与看板郎的 attachWaifuDrag 各自独立）——
// 拖拽手柄限定为封面（.aplayer-pic）与歌名/歌手文本（.aplayer-music），
// 不碰进度条/音量/播放按钮等交互控件，避免拖动误触。
// 位置存 localStorage(aplayer_pos_v2)，刷新恢复；双击手柄清除记忆复位默认右下角。
// v2：旧键 aplayer_pos 存的是拖拽绑定错位时代的坏数据（恒 {0,0}），直接弃用。
const POS_KEY = 'aplayer_pos_v2'
let dragEl = null      // 当前拖拽绑定的播放器容器（换源会重建容器，指向最新实例）
let dragState = null   // { sx, sy, ox, oy, w, h, moved }
let docHooksBound = false

// 默认右下角停靠：让出看板郎占位（右 270px）、上抬 34px 避开页脚日期时间。
// 用内联样式固定，不依赖 CSS 层叠顺序——APlayer 自带 .aplayer-fixed 默认是
// left:0/bottom:0（左下），若我们的覆盖样式没生效就会跑到左侧，内联可兜底。
function applyDefaultPos(el) {
  el.style.left = 'auto'
  el.style.top = 'auto'
  el.style.right = '270px'
  el.style.bottom = '34px'
}

function applySavedPos(el) {
  let p = null
  try { p = JSON.parse(localStorage.getItem(POS_KEY) || 'null') } catch (e) {}
  if (!(p && typeof p.left === 'number' && typeof p.top === 'number')) {
    applyDefaultPos(el)
    return
  }
  // 延迟到布局稳定后再恢复：APlayer 挂载瞬间可能尚未排版完成（offsetWidth 为 0、
  // 或被入场过渡放大到接近视口宽），立即读取尺寸会让钳制把 left/top 误算成 0，
  // 表现为“刷新后跑回左侧”。等两帧布局定稿后再取真实尺寸。
  const doApply = () => {
    const w = el.offsetWidth || 0
    const h = el.offsetHeight || 0
    // 尺寸未就绪（0 或异常撑满视口）时不按错误尺寸钳制，退回保守值，避免被误钳到 0
    const cw = (w > 0 && w < window.innerWidth) ? w : 300
    const ch = (h > 0 && h < window.innerHeight) ? h : 0
    el.style.right = 'auto'
    el.style.bottom = 'auto'
    el.style.left = Math.min(Math.max(p.left, 0), Math.max(window.innerWidth - cw, 0)) + 'px'
    el.style.top = Math.min(Math.max(p.top, 0), Math.max(window.innerHeight - ch, 0)) + 'px'
  }
  requestAnimationFrame(() => requestAnimationFrame(doApply))
}

function bindDocHooks() {
  if (docHooksBound) return
  docHooksBound = true
  document.addEventListener('mousemove', (e) => {
    if (!dragState || !dragEl) return
    if (!dragState.moved && Math.hypot(e.clientX - dragState.sx, e.clientY - dragState.sy) < 5) return
    dragState.moved = true
    const el = dragEl
    el.style.right = 'auto'
    el.style.bottom = 'auto'
    const left = Math.min(Math.max(e.clientX - dragState.ox, 0), window.innerWidth - dragState.w)
    const top = Math.min(Math.max(e.clientY - dragState.oy, 0), window.innerHeight - dragState.h)
    el.style.left = left + 'px'
    el.style.top = top + 'px'
  })
  document.addEventListener('mouseup', () => {
    if (!dragState) return
    if (dragState.moved && dragEl) {
      const left = parseInt(dragEl.style.left, 10) || 0
      const top = parseInt(dragEl.style.top, 10) || 0
      try { localStorage.setItem(POS_KEY, JSON.stringify({ left, top })) } catch (e) {}
    }
    dragState = null
  })
  // 浏览器窗口缩放/改变大小时，位置同步变化：
  // 默认停靠（无 left/top）由 CSS 的 right/bottom 锚点自动跟随；
  // 拖拽过的拉回可视区内（不改写记忆位置，恢复大窗口自动回原位）。
  window.addEventListener('resize', () => {
    const el = dragEl
    if (!el || (!el.style.left && !el.style.top)) return
    const w = el.offsetWidth, h = el.offsetHeight
    const left = parseFloat(el.style.left) || 0
    const top = parseFloat(el.style.top) || 0
    const nl = Math.min(Math.max(left, 0), Math.max(window.innerWidth - w, 0))
    const nt = Math.min(Math.max(top, 0), Math.max(window.innerHeight - h, 0))
    if (nl !== left || nt !== top) {
      el.style.left = nl + 'px'
      el.style.top = nt + 'px'
    }
  })
}

function attachPlayerDrag(el) {
  // 清理拖拽绑定错位时代的旧键（坏数据恒 {0,0}），避免它继续污染位置恢复
  try { localStorage.removeItem('aplayer_pos') } catch (e) {}
  applySavedPos(el)   // 换源重建容器后同样恢复记忆位置（无记忆时回默认右下角）
  dragEl = el
  bindDocHooks()
  el.addEventListener('mousedown', (e) => {
    if (e.button !== 0) return
    if (!e.target.closest || !e.target.closest('.aplayer-pic, .aplayer-music')) return
    const r = el.getBoundingClientRect()
    dragState = { sx: e.clientX, sy: e.clientY, ox: e.clientX - r.left, oy: e.clientY - r.top,
                  w: r.width, h: r.height, moved: false }
  })
  // 双击封面/歌名：清除记忆并复位到默认右下角（清空内联定位，交给 PLAYER_CSS 的
  // right/bottom 锚点——含窄视口媒体查询，避免内联值盖掉响应式让位）
  el.addEventListener('dblclick', (e) => {
    if (!e.target.closest || !e.target.closest('.aplayer-pic, .aplayer-music')) return
    try { localStorage.removeItem(POS_KEY) } catch (err) {}
    el.style.transition = 'none'
    el.style.left = ''
    el.style.top = ''
    el.style.right = ''
    el.style.bottom = ''
    setTimeout(() => { el.style.transition = '' }, 60)
  })
}

export function initMusic() {
  if (window.innerWidth < 768) return
  injectStyle()
  loadSources()
    .then(sources => {
      if (!sources.length) return
      let ap = null
      let container = null
      let current = -1   // 当前生效源下标；-1 表示尚未成功建起播放器

      // 用第 i 个源重建播放器；wasPlaying=true 时恢复自动播放。
      // 该源失效（请求失败/空歌单）自动顺延到下一源；全部失效则停止并告警。
      const useSource = (i, wasPlaying) => {
        if (i >= sources.length) {
          console.warn('[music] 所有播放源均不可用，播放器停止初始化')
          return
        }
        const s = sources[i]
        fetchPlaylist(s)
          .then(audio => {
            if (ap) {
              try { ap.destroy() } catch (e) { /* 忽略销毁异常 */ }
              ap = null
            }
            if (container && container.parentNode) {
              container.parentNode.removeChild(container)
            }
            container = document.createElement('div')
            document.body.appendChild(container)   // 独立挂载，与看板郎无关
            ap = new APlayer({
              container,
              fixed: true,
              lrcType: 3,       // lrc 字段为歌词 URL
              listFolded: true, // 列表默认收起，点播放器上的列表按钮展开
              autoplay: false,
              storageName: 'zoujiu-aplayer', // 记住播放进度/音量
              audio,
            })
            // 拖拽/位置记忆必须绑在 APlayer 渲染出的 .aplayer.aplayer-fixed（真正
            // position:fixed 的元素）上：container 本身是 static 空壳，往它身上设
            // left/top 无效。且要在渲染完成后绑定——此时才有真实尺寸，位置恢复的
            // 视口钳制才不会被空壳的全宽 offsetWidth 误钳到 0
            attachPlayerDrag(container.querySelector('.aplayer.aplayer-fixed') || container)
            window.__ap = ap // Live2D 挂件 🎵 按钮通过它播放/暂停
            current = i
            const sourceName = s.name || `${s.server}:${s.id}`
            console.info(`[music] 播放源就绪：${sourceName}${i > 0 ? '（已自动切换）' : ''}`)
            ap.on('play', () => {
              const cur = currentSong()
              if (!cur) return
              window.dispatchEvent(new CustomEvent('waifu-song', { detail: { name: cur.name, artist: cur.artist } }))
            })
            // 播放中音频失效（外链 403/断链等）：切到下一个可用源并恢复播放
            ap.on('error', () => {
              if (current !== i) return // 已切走，忽略旧实例残留事件
              console.warn(`[music] 播放源「${sourceName}」音频失效，自动切换下一源`)
              useSource(i + 1, !ap.audio.paused)
            })
            if (wasPlaying) {
              ap.play()
            }
          })
          .catch(err => {
            console.warn(`[music] 播放源「${s.name || s.server}:${s.id}」失效：${err.message}`)
            useSource(i + 1, wasPlaying)
          })
      }

      const currentSong = () => {
        try {
          return ap.list.audios[ap.list.index] || ap.list.audios[0]
        } catch (e) {
          return null
        }
      }

      useSource(0, false)
    })
    .catch(err => console.warn('[music] 音乐播放器初始化失败：', err))
}
