// 站点音乐播放器：APlayer（fixed 模式，悬浮在看板郎上方）+ Meting 协议在线歌单
// 播放源多源容灾：源列表来自 mysite/site_config.json 的 music_sources（可手动配置），
// 默认用列表第一个可用源；某源歌单拉取失败/返回为空/播放中音频报错时自动切换下一个源。
// 播放时广播 window 事件 'waifu-song'，看板郎（public/live2d/waifu-tips.js）据此报幕。
import APlayer from 'aplayer'
import 'aplayer/dist/APlayer.min.css'

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

// 音乐播放器可拖拽停靠：按住封面图拖动整个悬浮播放器（localStorage 记忆，刷新恢复），
// 双击封面复位到默认右下角。封面（.aplayer-pic）本身无播放交互，作拖拽把手不与按钮冲突。
function attachAplayerDrag(aplayerEl) {
  if (!aplayerEl || aplayerEl.dataset.dragBound === '1') return
  aplayerEl.dataset.dragBound = '1'
  const KEY = 'aplayer_pos'
  const pic = aplayerEl.querySelector('.aplayer-pic')
  if (!pic) return
  const pin = (left, top) => {
    aplayerEl.style.right = 'auto'
    aplayerEl.style.bottom = 'auto'
    aplayerEl.style.left = left + 'px'
    aplayerEl.style.top = top + 'px'
  }
  // 恢复记忆位置（等 APlayer 完成初始布局后应用）
  try {
    const p = JSON.parse(localStorage.getItem(KEY) || 'null')
    if (p && typeof p.left === 'number' && typeof p.top === 'number') {
      requestAnimationFrame(() => pin(p.left, p.top))
    }
  } catch (e) { /* 忽略脏数据 */ }
  let drag = null
  pic.addEventListener('mousedown', (e) => {
    if (e.button !== 0) return
    const r = aplayerEl.getBoundingClientRect()
    drag = { sx: e.clientX, sy: e.clientY, ox: e.clientX - r.left, oy: e.clientY - r.top,
             w: r.width, h: r.height, moved: false }
    e.preventDefault() // 阻止封面默认图片拖拽
  })
  document.addEventListener('mousemove', (e) => {
    if (!drag) return
    if (!drag.moved && Math.hypot(e.clientX - drag.sx, e.clientY - drag.sy) < 5) return
    drag.moved = true
    const left = Math.min(Math.max(e.clientX - drag.ox, 0), window.innerWidth - drag.w)
    const top = Math.min(Math.max(e.clientY - drag.oy, 0), window.innerHeight - drag.h)
    pin(left, top)
  })
  document.addEventListener('mouseup', () => {
    if (!drag) return
    if (drag.moved) {
      const left = parseInt(aplayerEl.style.left, 10) || 0
      const top = parseInt(aplayerEl.style.top, 10) || 0
      try { localStorage.setItem(KEY, JSON.stringify({ left, top })) } catch (e) { /* 忽略 */ }
    }
    drag = null
  })
  pic.addEventListener('dblclick', () => {
    try { localStorage.removeItem(KEY) } catch (e) { /* 忽略 */ }
    aplayerEl.style.left = 'auto'
    aplayerEl.style.top = 'auto'
    aplayerEl.style.right = ''
    aplayerEl.style.bottom = ''
  })
}

export function initMusic() {
  if (window.innerWidth < 768) return
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
            document.body.appendChild(container)
            ap = new APlayer({
              container,
              fixed: true,
              lrcType: 3,       // lrc 字段为歌词 URL
              listFolded: true, // 列表默认收起，点播放器上的列表按钮展开
              autoplay: false,
              storageName: 'zoujiu-aplayer', // 记住播放进度/音量
              audio,
            })
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
            // 每次重建播放器实例后重新挂拖拽（src/music.js 顶部定义）
            requestAnimationFrame(() => {
              const el = container.querySelector('.aplayer.aplayer-fixed')
              if (el) attachAplayerDrag(el)
            })
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
