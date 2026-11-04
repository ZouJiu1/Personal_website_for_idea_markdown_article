// 本文件源自 https://github.com/crowya/live2d（waifu-tips.js），
// 已按本站（Django + Vue / Element Plus）定制：
// 1) 移除音乐播放器依赖（APlayer / ap_init / aplayer_panel_toggle / 音乐按钮）；
// 2) 移除 jQuery，右键彩蛋改用原生 addEventListener；
// 3) 工具按钮由 FontAwesome 图标改为 emoji（站点无 FontAwesome）；
// 4) 一言接口请求失败时补充兜底提示；
// 5) 形象库多分类化（男性/女性/猫咪/狗狗/鸟类/熊猫/动漫/历史仙神），
//    ⚙️ 按钮打开形象选择器；登录用户的选择经 /csdn/set_widget 持久化到账号，
//    未登录仅存 localStorage（本机生效）；
// 6) 模型标识由数字下标改为字符串 id（= public/live2d/model/<id>/ 目录名），
//    自定义模型：把模型目录放进 public/live2d/model/ 并在 model_list.json 注册即可；
// 7) 公共语料预加载：脚本就位即请求 waifu-tips.json 并解析后常驻内存，与模型/配置请求并行，
//    不再等模型加载完才拿台词；切换形象直接复用内存里的解析结果，不重复请求。
function loadWidget() {
	localStorage.removeItem("waifu-display");
	sessionStorage.removeItem("waifu-text");
	document.body.insertAdjacentHTML("beforeend", `<div id="waifu">
			<div id="waifu-tips"></div>
			<canvas id="live2d" width="800" height="800"></canvas>
			<div id="waifu-tool">
				<span class="tool-music" role="button" title="播放/暂停音乐">🎵</span>
				<span class="tool-chat" role="button" title="来句一言">💬</span>
				<span class="tool-config" role="button" title="选择看板郎形象">⚙️</span>
				<span class="tool-switch" role="button" title="切换下一个形象">🔄</span>
				<span class="tool-photo" role="button" title="拍照">📷</span>
				<span class="tool-hide" role="button" title="隐藏看板郎">✖️</span>
			</div>
		</div>`);
	setTimeout(() => {
		// 默认停靠在右下角并上抬 58px，给页脚日期时间和音乐播放器留出空间
		document.getElementById("waifu").style.bottom = "58px";
	}, 0);

	// ===== 角色台词（per_model / per_category）：按当前形象动态替换戳/点/闲聊/欢迎语 =====
	// 当前角色的台词包（registerEventListener 拿到 result 后才有值；切换模型时原地改写）
	let tipsResult = null;
	let charGreeting = null; // 当前角色欢迎语数组；null 时 welcomeMessage 走默认时段文案
	let ownerLines = [];     // 当前主页主人的自定义台词组（[[句,…],…]），initModel 时经公开接口拉取
	let messageArray = [];   // 闲聊池（始终指向当前语料的 message.default，重载语料时整体替换）
	let tipsBound = false;   // 事件监听只绑定一次；重载语料只换数据，不重复 addEventListener

	// ===== 语料预加载与自愈：语料库有 60 万字符，越早进内存越好 =====
	// 脚本一执行就发起请求，与 model_list、主页主人配置请求并行；解析结果只做一次，
	// 之后常驻内存（切换形象、重复点 💬 都直接复用，不再走网络）。
	// 万一常驻内存的语料失效（被清空、结构被写坏、解析结果丢失），下面的自检会在下次用到
	// 台词时自动重新拉取、重新解析并放回内存，避免看板郎因为拿不到台词而卡死。
	let tipsReady = null;        // 当前这次加载的 Promise
	let tipsLoading = false;     // 是否有请求正在路上，防止并发重复下载
	let tipsRetryAt = 0;         // 失败退避时间戳，避免断网期间反复发请求
	const TIPS_RETRY_MS = 30000;

	// 结构自检：闲聊池存在且非空才算可用；其余字段用到时再兜底，缺了也不至于整体报废
	function tipsValid(result) {
		return !!(result && result.message && Array.isArray(result.message.default) && result.message.default.length > 0);
	}

	function preloadTips() {
		if (tipsValid(tipsResult)) return Promise.resolve(tipsResult); // 内存里还有，直接用
		if (tipsLoading) return tipsReady;                             // 正在下载，等同一个结果
		if (Date.now() < tipsRetryAt) return Promise.resolve(null);    // 退避期内先不重试
		tipsLoading = true;
		tipsReady = fetch(`${live2d_path}waifu-tips.json`)
			.then(response => {
				if (!response.ok) throw new Error(`HTTP ${response.status}`);
				return response.json();
			})
			.then(data => {
				if (!tipsValid(data)) throw new Error("语料结构异常");
				registerEventListener(data);
				return data;
			})
			.catch(err => {
				tipsRetryAt = Date.now() + TIPS_RETRY_MS;
				console.warn("看板郎语料加载失败，稍后会自动重试", err);
				return null;
			})
			.finally(() => {
				tipsLoading = false;
				// 没成功就清掉 Promise，让下一轮自检能重新发起请求
				if (!tipsValid(tipsResult)) tipsReady = null;
			});
		return tipsReady;
	}
	preloadTips();
	// 兜底自检：语料一直不在内存里就每 30 秒补一次；补上后自检立即变成空转，不再发请求
	setInterval(() => { if (!tipsValid(tipsResult)) preloadTips(); }, TIPS_RETRY_MS);
	// 断网恢复后立刻补一次，不用等到下一个自检周期
	window.addEventListener("online", () => preloadTips());

	// 模型 id → 台词包：per_model[id] 优先，其次 per_category[category]，都没有返回 null
	function getCharacterTips(modelId) {
		if (!tipsResult || !modelId) return null;
		const perModel = tipsResult.per_model || {};
		if (perModel[modelId]) return perModel[modelId];
		const m = (modelList && modelList.models || []).find(x => x.id === modelId);
		const perCat = tipsResult.per_category || {};
		return (m && perCat[m.category]) || null;
	}

	// 把角色台词合并进 result：专属台词排在通用台词前面（随机时更容易命中，也保留通用彩蛋）。
	// lastCharEntries 记录上次插入的专属台词组引用，切换角色时先整体移除再插入新的，
	// 避免反复切换导致台词池无限膨胀。
	let lastCharEntries = [];
	function applyCharacterTips(modelId) {
		if (!tipsResult) return;
		const tips = getCharacterTips(modelId);
		charGreeting = (tips && tips.greeting) || null;
		const merge = (arr, extra) => {
			for (let i = arr.length - 1; i >= 0; i--) {
				if (lastCharEntries.includes(arr[i])) arr.splice(i, 1);
			}
			if (Array.isArray(extra) && extra.length) {
				arr.unshift(...extra); // 整组插到最前，保持原有顺序
				lastCharEntries.push(...extra);
			}
		};
		merge(tipsResult.message.default, [...(tips ? tips.chat : []), ...getUserLines()]); // 闲聊池 = 公共语料 + 角色专属 + 主人自定义
		for (const t of tipsResult.mouseover || []) {                  // 悬停文案
			if (t.selector === "#waifu #live2d") { merge(t.text, tips ? tips.mouseover : []); break; }
		}
		for (const t of tipsResult.click || []) {                      // 点击文案
			if (t.selector === "#waifu #live2d") { merge(t.text, [...(tips ? tips.click : []), ...getUserLines()]); break; }
		}
	}

	// 三部分台词之"用户给的台词"：把主人配置的多组台词拍平成一维句池
	function getUserLines() {
		return ownerLines.flat().filter(s => typeof s === "string" && s.trim());
	}

	// 把当天命中的公历节日并入闲聊池；已经由节日系统接管的（元旦、国庆等）跳过，
	// 避免同一天出现两条重复的节日话。每次都往新的 messageArray 里追加，重载语料不会重复叠加。
	function appendSeasonLines(result) {
		const handled = getFestivalsToday().map(f => f.name);
		(result.seasons || []).forEach(({ date, text }) => {
			const now = new Date(),
				after = date.split("-")[0],
				before = date.split("-")[1] || after;
			if ((after.split("/")[0] <= now.getMonth() + 1 && now.getMonth() + 1 <= before.split("/")[0]) && (after.split("/")[1] <= now.getDate() && now.getDate() <= before.split("/")[1])) {
				if (handled.some(name => text.includes(name))) return;   // 节日系统会随机出更丰富的祝福
				text = randomSelection(text);
				text = text.replace("{year}", now.getFullYear());
				messageArray.push(text);
			}
		});
	}

	function registerEventListener(result) {
		if (!tipsValid(result)) return;    // 结构不对就丢弃这份数据，交给自愈逻辑重新拉取
		tipsResult = result;               // 供角色台词系统读写（applyCharacterTips）
		messageArray = result.message.default; // 闲聊池跟随最新语料（重载时整体替换，不累加）
		// 台词库就绪后，立即为当前形象应用专属台词（戳/点/闲聊/欢迎语），
		// 放在首次欢迎语生成之前，让第一句问候就带角色口吻
		applyCharacterTips(localStorage.getItem("waifu-model"));
		appendSeasonLines(result);
		// 监听器只绑定一次：重载语料时上面已替换好数据，这里直接返回，
		// 避免重复 addEventListener 导致提示重复触发、内存越堆越多
		if (tipsBound) return;
		tipsBound = true;
		document.querySelector("#waifu-tool .tool-music").addEventListener("click", () => {
			if (window.__ap) {
				window.__ap.toggle();
				showMessage(window.__ap.paused ? "音乐暂停啦，想听再点我哦。" : "🎵 好戏开场，听歌吧！", 3000, 8);
			} else {
				showMessage("音乐播放器还在准备中，稍等一下下～", 3000, 8);
			}
		});
		document.querySelector("#waifu-tool .tool-chat").addEventListener("click", showHitokoto);
		document.querySelector("#waifu-tool .tool-config").addEventListener("click", openModelPicker);
		document.querySelector("#waifu-tool .tool-switch").addEventListener("click", () => {
			// 换装互动：旧形象先炸一圈星星送别，新形象站好后 400ms 再冒一簇爱心打个招呼
			waifuBurst(["star", "sparkle"]);
			Promise.resolve(loadNextModel()).then(() => {
				setTimeout(() => waifuBurst(["heart", "sparkle", "petal"]), 400);
			}).catch(() => { });
		});
		document.querySelector("#waifu-tool .tool-photo").addEventListener("click", () => {
			showMessage("照好了嘛，是不是很帅呢？", 6000, 9);
			waifuBurst(["star", "sparkle"], 20);   // 拍照闪光：快门一响冒一圈星
			Live2D.captureName = "photo.png";
			Live2D.captureFrame = true;
		});
		document.querySelector("#waifu-tool .tool-hide").addEventListener("click", () => {
			localStorage.setItem("waifu-display", Date.now());
			showMessage("人生海海，祝你有帆也有岸。", 2000, 11);
			document.getElementById("waifu").style.bottom = "-500px";
			setTimeout(() => {
				document.getElementById("waifu").style.display = "none";
				document.getElementById("waifu-toggle").classList.add("waifu-toggle-active");
			}, 3000);
		});
		// 看板郎与用户的专属互动：点击角色时从角色身上迸发一圈粒子（配合语料里的点击文案一起出），
		// 偶尔慢半拍再补一小簇，像真的被戳到才反应过来；悬停/掠过/波及在特效引擎里处理
		let waifuClickTimes = [];
		document.getElementById("live2d").addEventListener("click", () => {
			waifuBurst(["star", "sparkle", "heart"]);
			if (Math.random() < 0.35) setTimeout(() => waifuBurst(["petal", "bubble"]), 500);
			// 连点彩蛋：2.5 秒内戳满 5 次，角色气得大爆发并摇晃两下（WAAPI 动画，无需样式表）
			const now = Date.now();
			waifuClickTimes = waifuClickTimes.filter(ts => now - ts < 2500);
			waifuClickTimes.push(now);
			if (waifuClickTimes.length >= 5) {
				waifuClickTimes = [];
				waifuBurst(["star", "heart", "petal", "sparkle"], 70);
				showMessage("别戳啦别戳啦！再戳我要生气了哦！", 4000, 12);
				const el = document.getElementById("waifu");
				if (el && el.animate) el.animate([
					{ transform: "translateX(0)" },
					{ transform: "translateX(-7px) rotate(-2deg)" },
					{ transform: "translateX(7px) rotate(2deg)" },
					{ transform: "translateX(-4px)" },
					{ transform: "translateX(0)" },
				], { duration: 480, easing: "ease-in-out" });
			}
		});
		// 检测用户活动状态，并在空闲时显示消息
		let userAction = false,
			userActionTimer;
		window.addEventListener("mousemove", () => userAction = true);
		window.addEventListener("keydown", () => userAction = true);
		setInterval(() => {
			if (userAction) {
				userAction = false;
				clearInterval(userActionTimer);
				userActionTimer = null;
			} else if (!userActionTimer) {
				userActionTimer = setInterval(() => {
					showChatBatch(messageArray, CHAT_BATCH_SIZE, 9);
					// 空闲搭话时配一簇爱心粒子：像角色主动朝用户挥手求关注
					waifuBurst(["heart", "sparkle"], 12);
				}, 20000);
			}
		}, 1000);
		const festivalGreeting = festivalWelcome();
		showMessage(festivalGreeting ? festivalGreeting.text : welcomeMessage(result.time || []), 7000, 11);
		// 节日期间特效常驻全屏；平日按主题配置里的开关决定是否播放
		startAmbientFx();
		window.addEventListener("mouseover", event => {
			for (let tips of (tipsResult && tipsResult.mouseover) || []) {
				if (!event.target.matches(tips.selector)) continue;
				let text = randomSelection(tips.text);
				text = text.replace("{text}", event.target.innerText);
				showMessage(text, 4000, 8);
				return;
			}
		});
		window.addEventListener("click", event => {
			for (let tips of (tipsResult && tipsResult.click) || []) {
				if (!event.target.matches(tips.selector)) continue;
				let text = randomSelection(tips.text);
				text = text.replace("{text}", event.target.innerText);
				showMessage(text, 4000, 8);
				return;
			}
		});
		// 右键彩蛋（原版为 jQuery 实现，这里改为原生事件）
		document.getElementById("live2d").addEventListener("mousedown", e => {
			if (e.button === 2) {
				showMessage(tipsResult.message.secret_path, 4000, 12);
				waifuBurst(["sparkle", "moonOrb"], 18);   // 右键彩蛋也配一圈星光
			}
		});
		document.getElementById("live2d").addEventListener("contextmenu", e => e.preventDefault());
		// 长时间闲置/后台待机后，浏览器会回收 WebGL 上下文，画布变空白但按钮和台词还在：
		// 这里记住丢失状态，等上下文恢复或切回页面时重新加载当前模型
		const live2dCanvas = document.getElementById("live2d");
		let modelContextLost = false;
		let modelReloadAt = 0;
		const reloadModelIfLost = () => {
			if (!modelContextLost) return;
			const now = Date.now();
			if (now - modelReloadAt < 10000) return;   // 防止连续事件重复加载
			modelReloadAt = now;
			modelContextLost = false;
			const current = localStorage.getItem("waifu-model");
			if (current) loadModel(current, "刚才屏幕打了个盹，我重新站好啦～");
		};
		live2dCanvas.addEventListener("webglcontextlost", e => {
			e.preventDefault();   // 允许浏览器稍后恢复上下文
			modelContextLost = true;
		}, false);
		live2dCanvas.addEventListener("webglcontextrestored", reloadModelIfLost, false);
		document.addEventListener("visibilitychange", () => {
			if (document.hidden) return;
			try {
				const gl = live2dCanvas.getContext("webgl2") || live2dCanvas.getContext("webgl");
				if (gl && gl.isContextLost && gl.isContextLost()) modelContextLost = true;
			} catch (e) { /* 部分浏览器不允许再次取上下文，忽略 */ }
			setTimeout(reloadModelIfLost, 800);
		});
		const devtools = () => { };
		console.log("%c" + result.message.console, devtools);
		devtools.toString = () => {
			showMessage(tipsResult.message.console, 6000, 9);
		};
		window.addEventListener("copy", () => {
			showMessage(tipsResult.message.copy, 6000, 9);
		});
		window.addEventListener("visibilitychange", () => {
			if (!document.hidden) showMessage(tipsResult.message.visibilitychange, 6000, 9);
		});
		// 看板郎歌曲报幕（src/music.js 在 play 事件时广播 waifu-song）
		window.addEventListener("waifu-song", e => {
			showMessage(`🎵 正在播放《${e.detail.name}》-${e.detail.artist}`, 5000, 8);
		});
		// 标签页标题彩蛋：切走标签时显示等待表情，切回时短暂显示欢迎语再还原
		const originTitle = document.title;
		document.addEventListener("visibilitychange", () => {
			if (document.hidden) {
				document.title = "(●—●)等你回来…";
			} else {
				document.title = "(◍•ᴗ•◍)欢迎回来！";
				setTimeout(() => { document.title = originTitle; }, 2000);
			}
		});
		// 键盘彩蛋：任意页面连按 666 触发看板郎夸夸
		let keyBuffer = "";
		window.addEventListener("keydown", e => {
			if (e.key && e.key.length === 1) {
				keyBuffer = (keyBuffer + e.key).slice(-6);
				if (keyBuffer.includes("666")) {
					keyBuffer = "";
					showMessage("你也觉得这个网站很棒吧！(〃'▽'〃)", 5000, 9);
				}
			}
		});
	}

	// 节日首屏问候：返回 { text, festival }，当天没有节日返回 null
	function festivalWelcome() {
		const festivals = getFestivalsToday();
		if (!festivals.length) return null;
		const festival = festivals[Math.floor(Math.random() * festivals.length)];
		const blessing = pickBlessing(festival);
		return blessing ? { text: `今天是${festival.dateLabel}，${blessing}`, festival } : null;
	}

	function welcomeMessage(time) {
		if (location.pathname === "/" && location.hash === "#/" || location.hash === "#/homepage") { // 如果是主页
			for (let { hour, text } of time) {
				const now = new Date(),
					after = hour.split("-")[0],
					before = hour.split("-")[1] || after;
				if (after <= now.getHours() && now.getHours() <= before) {
					// 当前角色有专属欢迎语时，50% 概率用角色问候替代时段欢迎语，两种口吻交替出现
					if (charGreeting && Math.random() < 0.5) return randomSelection(charGreeting);
					return text;
				}
			}
		}
		const text = `欢迎来到<span>「${document.title.split(" - ")[0]}」</span>`;
		let from;
		if (document.referrer !== "") {
			const referrer = new URL(document.referrer),
				domain = referrer.hostname.split(".")[1];
			const domains = {
				"baidu": "百度",
				"so": "360搜索",
				"google": "谷歌搜索"
			};
			if (location.hostname === referrer.hostname) return text;
			if (domain in domains) from = domains[domain];
			else from = referrer.hostname;
			return `Hello！来自 <span>${from}</span> 的朋友<br>${text}`;
		}
		return text;
	}

	let messageTimer;
	function showMessage(text, timeout, priority) {
		if (!text || (sessionStorage.getItem("waifu-text") && sessionStorage.getItem("waifu-text") > priority)) return;
		text = randomSelection(text);
		renderMessage(text, timeout, priority, false);
	}

	// 公共语料太多，一次抽 3 条一起展示；按行排版，并按字数给足阅读时间
	const CHAT_BATCH_SIZE = 3;
	const READING_MS_PER_CHAR = 140;   // 约 7 个汉字/秒，留出反应时间
	const CHAT_MAX_MS = 18000;         // 上限：不超过闲聊提醒的 20 秒间隔
	function pickChatLines(pool, count) {
		const lines = [],
			seen = new Set();
		for (let guard = 0; guard < count * 30 && lines.length < count; guard++) {
			const line = randomSelection(pool);
			if (typeof line !== "string" || !line.trim() || seen.has(line)) continue;
			seen.add(line);
			lines.push(line);
		}
		return lines;
	}
	function renderChatLines(lines) {
		return lines.map((line, i) =>
			`<div class="waifu-tips-line" style="animation-delay:${i * 90}ms">` +
			`<div class="waifu-tips-text">${line}</div></div>`
		).join("");
	}
	function chatDuration(lines) {
		const chars = lines.reduce((n, s) => n + s.replace(/\s/g, "").length, 0);
		return Math.min(CHAT_MAX_MS, 1500 + chars * READING_MS_PER_CHAR + (lines.length - 1) * 400);
	}
	function showChatBatch(pool, count, priority) {
		if (!pool || !pool.length) return;
		if (sessionStorage.getItem("waifu-text") && sessionStorage.getItem("waifu-text") > priority) return;
		const lines = pickChatLines(pool, count);
		if (!lines.length) return;
		// 节日当天有一半概率把其中一句换成节日祝福：每次随机换一句，一天里能听好几版
		const festivals = getFestivalsToday();
		if (festivals.length && Math.random() < 0.5) {
			const f = festivals[Math.floor(Math.random() * festivals.length)];
			const blessing = pickBlessing(f);
			if (blessing) lines[Math.floor(Math.random() * lines.length)] = blessing;
		}
		renderMessage(renderChatLines(lines), chatDuration(lines), priority, true);
	}
	function renderMessage(html, timeout, priority, multi) {
		// 内存里的语料一旦失效（被清空、结构被写坏），这里顺手触发一次后台重载；
		// 不耽误当前这条提示，重新解析好的语料会在下一次随机时生效
		if (!tipsValid(tipsResult)) preloadTips();
		if (messageTimer) {
			clearTimeout(messageTimer);
			messageTimer = null;
		}
		sessionStorage.setItem("waifu-text", priority);
		let tips = document.getElementById("waifu-tips");
		if (!tips) {
			// 提示框节点被移除/重建时补回来，避免之后所有台词都无处可显示
			const waifu = document.getElementById("waifu");
			if (!waifu) return;   // 看板郎整体被移除，静默跳过，不让异常扩散
			tips = document.createElement("div");
			tips.id = "waifu-tips";
			waifu.insertBefore(tips, waifu.firstChild);
		}
		try {
			tips.innerHTML = html;
			tips.classList.toggle("waifu-tips-multi", multi);
			tips.classList.add("waifu-tips-active");
		} catch (err) {
			// 渲染失败也不能把整个看板郎带崩：清掉优先级锁，下次还能正常出提示
			console.warn("看板郎台词渲染失败，已跳过本次提示", err);
			sessionStorage.removeItem("waifu-text");
			return;
		}
		messageTimer = setTimeout(() => {
			sessionStorage.removeItem("waifu-text");
			tips.classList.remove("waifu-tips-active");
		}, timeout);
	}

	// 一言等待期间的占位台词：点击立即回应（萌、礼貌、通用，各角色都适合），一言返回后覆盖。
	// 请求最长要等 9 秒，多备几条随机，免得同一句话反复出现显得敷衍。
	const HITOKOTO_WAITING = [
		"让我想想哦…💭",
		"稍等一下，我去摘一句漂亮话给你～",
		"唔…正在努力组织语言！",
		"马上就好，别眨眼哦～",
		"正在向太阳要一句话…",
		"我翻开小本本挑一句，你数三下就好。",
		"刚想到一句好话，被风吹跑了，我去追回来～",
		"台词太多啦，我正在里面翻找最合适的那句。",
		"正在把这句话擦干净、熨平整，马上递给你。",
		"别急别急，好句子都要慢慢酝酿才顺口。",
		"我在旧书页里夹了一句诗，正在小心地取出来。",
		"先喝口水润润嗓子，我这就把话想出来。",
		"灵感正在赶来的路上，应该很快就到。",
		"正在向月亮借一句温柔的话，稍等片刻。",
		"正在从词典里挑一句不肉麻又不敷衍的。",
		"等我三秒，我把这句话说得漂亮一点。",
		"句子们在排队，我让最顺口的那句先出来。",
		"正在把心里的想法翻译成好听的话。",
		"别走开，我正在给你挑一句压箱底的。",
		"我在书架上找那句能让人心里一暖的话。",
		"正在练习语气，怕说得不够好听。",
		"稍等，我在给这句话系个蝴蝶结。",
		"脑子转了两圈，句子马上就到。",
		"正在向海边的风讨一句祝福回来。",
		"让我把这句话念顺了，再讲给你听。",
		"我在抽屉里翻出一句旧的，先吹吹灰。",
		"排队的人有点多，你的那句马上轮到。",
		"好话不怕等，再给我一小会儿就好。",
		"正在把星光装进句子里，快好了。",
		"我正在确认这句话有没有说错，马上给你。",
	];
	let hitokotoSeq = 0;   // 连点 💬 时只认最后一次点击的响应，防止旧响应覆盖新提示
	function showHitokoto() {
		// 用户主动点击：清掉当前消息的优先级锁，否则欢迎语(11)/提醒(10)显示期间点击会被 showMessage 吞掉
		sessionStorage.removeItem("waifu-text");
		const seq = ++hitokotoSeq;
		const shownAt = Date.now();
		// 等待提示持续显示直到被正式台词覆盖（超时给很大值，不中途消失）
		showMessage(HITOKOTO_WAITING, 600000, 9);
		// 点击 💬：一言作为第一行，再补两句公共语料，凑成三行一起展示
		const reveal = lead => {
			const show = () => {
				if (seq !== hitokotoSeq) return;
				const pool = tipsResult && tipsResult.message.default.length
					? tipsResult.message.default : [...getUserLines(), "今天也要加油哦！"];
				const lines = lead
					? [lead, ...pickChatLines(pool, CHAT_BATCH_SIZE - 1)]
					: pickChatLines(pool, CHAT_BATCH_SIZE);
				if (!lines.length) return;
				renderMessage(renderChatLines(lines), chatDuration(lines), 9, true);
			};
			const rest = 3000 - (Date.now() - shownAt);
			if (rest > 0) setTimeout(show, rest); else show();
		};
		// 9 秒超时：超时中止请求并回退本地台词池（公共语料+角色专属+用户自定义已在 default 合并）
		const fallback = () => reveal(null);
		const ctrl = new AbortController();
		const timer = setTimeout(() => ctrl.abort(), 9000);
		fetch("https://v1.hitokoto.cn", { signal: ctrl.signal })
			.then(response => response.json())
			.then(result => {
				clearTimeout(timer);
				if (result && result.hitokoto) reveal(result.hitokoto);
				else fallback();
			})
			.catch(() => { clearTimeout(timer); fallback(); });
	}

	// ===== 节日系统（solarlunar.min.js 提供公历→农历、节气、干支换算，UMD 全局名 solarLunar）=====
	// 覆盖公历固定日、公历区间（清明/冬至）、农历日、第 N 个星期几（感恩节）、
	// 以及按干支推算的春社/秋社/三伏。每个节日都备了多句祝福：当天反复触发会随机换一句，
	// 不会一整天都是同一句话；effect 决定当天配哪种小特效。
	const FESTIVALS = [
		{
			name: "元旦", solar: [1, 1], effect: "confetti",
			blessings: [
				"元旦快乐！新的一年刚开始，先把想做的事写下来，一件件去完成。",
				"新年第一天，愿你今年的计划都能稳稳落地，不慌不忙。",
				"今天是元旦，日历翻到第一页，去年的遗憾就留在去年吧。",
				"元旦到了，祝你睡得好、吃得好、心情也好，简单的幸福最长久。",
				"新年新气象，愿你今年少熬夜、多运动，身体先跟上野心。",
				"元旦快乐！不管去年过得怎样，今天都是重新开始的好日子。",
				"一年之计在于春，元旦这天定个小目标，年底回头看会很欣慰。",
				"元旦快乐，愿你去年的努力在今年开花，慢慢来，都会有的。",
				"元旦这天老一辈讲究早起，图个一年都精神，睡到中午可就晚啦。",
				"新年第一天，把去年的账单和遗憾一起清一清，轻装上阵。",
				"元旦出门走走，哪怕只是绕小区一圈，也算给新的一年开个好头。",
				"元旦快乐！新买的日历可以挂上墙了，一页页翻过去就是一年。",
				"元旦的“元”是开始的意思，“旦”是早晨，合起来就是新年的第一个早晨。",
				"元旦这天把去年的照片整理一下，留几张真正想留的。",
				"新年第一天，给通讯录里很久没联系的人发句问候，不用等回音。",
				"元旦适合列一张“想做但一直没做”的清单，挑一件开始。",
				"元旦快乐！新的一年，先把手头的事做好，再去想更远的事。",
				"元旦出门前看一眼天气，北方的风比看上去更冷。",
				"新年第一天，家里的绿植浇浇水，也算给新岁添点生气。",
				"元旦的商场折扣多，但别为了便宜买用不上的东西。",
				"元旦这天吃顿热乎的早饭，一年都有好胃口。",
				"新年新气象，把桌面收拾干净，做事也会顺一点。",
				"元旦快乐！愿你去年的遗憾，都变成今年的经验。",
				"元旦期间高速车多，出门早点走，别把时间卡得太紧。",
				"新年第一天，给自己留半天什么都不做，也是种休息。",
				"元旦适合写下今年最想完成的三件事，写完贴在看得见的地方。",
				"元旦快乐！天冷记得多喝热水，别等嗓子疼才想起来。",
				"新年的第一笔开销，花在让自己变好的地方最值。",
				"元旦这天给爸妈打个电话，他们嘴上不说，心里盼着。",
				"元旦快乐！去年的账可以结了，今年的计划慢慢来。",
				"新年第一天，把手机相册清一清，腾出空间装新的日子。",
				"元旦出门看烟花，记得站在划定的安全区域里。",
				"元旦的钟声敲过，旧的一年就真的过去了，别回头太久。",
				"新年第一天，早餐加个鸡蛋，讨个圆圆满满的彩头。",
				"元旦快乐！新的一年，愿你少熬夜、多晒太阳。",
				"元旦这天可以把去年的日历取下来，换本新的挂上。",
				"新年第一天，和老朋友约顿饭，感情是吃出来的。",
				"元旦假期短，别安排太满，留点时间给自己喘口气。",
				"元旦快乐！愿你今年的体检报告，比去年更让人安心。",
				"新年第一天，把冬天的厚衣服拿出来晒晒，穿起来更暖。",
				"元旦逛超市记得列清单，不然一进去就买多了。",
				"元旦快乐！愿你去年的坚持，在今年有回响。",
				"新年第一天，把“改天再说”的事挑一件今天做完。",
				"元旦这天不妨走一段路，看看街上的年味。",
				"元旦快乐！新的一年，愿你遇事不慌，慢慢来。",
				"新年第一天，给孩子讲讲元旦的来历，也是种陪伴。",
				"元旦的电影院人多，想看的片子记得提前订票。",
				"元旦快乐！愿你今年的每一顿饭，都有人一起吃。",
				"新年第一天，把冰箱里过期的东西清掉，心里也清爽。",
				"元旦出门穿暖一点，感冒可不认节日。",
				"元旦快乐！新的一年，愿你手里有钱、心里有底。",
				"新年第一天，给自己买束花，几十块也能换来好心情。",
				"元旦的祝福不用太长，一句“新年好”就够真诚。",
				"元旦快乐！愿你去年的辛苦，都变成今年的底气。",
				"新年第一天，把窗帘拉开，让阳光进来。",
				"元旦适合去庙里或公园走走，图个心安。",
				"元旦快乐！新的一年，愿你少些内耗，多些行动。",
				"新年第一天，把闹钟往前调十分钟，从容一点出门。",
				"元旦的饺子、年糕、汤圆，吃哪个都图个好意头。",
				"元旦快乐！愿你今年想去的地方，都能真的去成。",
			],
		},
		{
			name: "人日", lunar: [1, 7], effect: "petal",
			blessings: [
				"正月初七是人日，传说这天是人类的生日，祝你生日快乐、岁岁安康。",
				"人日到啦，记得吃碗七宝羹或者面条，讨个顺顺利利的好彩头。",
				"今天是正月初七人日，愿你和家人都健健康康，平安就是福气。",
				"人日这天要吃面，长长的面条寓意长寿，别忘了给自己加个蛋。",
				"人日快乐！新的一年，先照顾好自己，才有力气照顾想照顾的人。",
				"人日这天有些地方要称体重，图个心里有数，别为了数字焦虑。",
				"正月初七，古人有登高赋诗的雅兴，今天读两页书也算应景。",
				"人日快乐！传说女娲第七天造人，所以今天人人都过生日。",
				"人日吃七样菜，芹菜、葱、蒜都算，图的是勤快、聪明、会打算。",
				"人日这天，古人有戴“人胜”的习俗，用彩纸剪成人形贴在屏风上。",
				"正月初七，天气好的话出门晒晒太阳，人也精神。",
				"人日吃七菜羹，七种蔬菜一起煮，清淡又应景。",
				"人日快乐！愿新的一年，你被这个世界温柔以待。",
				"正月初七，老话说这天不宜远行，在家陪陪家人挺好。",
				"人日这天可以量量身高，看看孩子又长高了多少。",
				"人日快乐！愿你在新的一年里，做自己喜欢的事。",
				"正月初七，年味还没散，剩菜记得热透再吃。",
				"人日适合拍张全家福，一年一张，攒起来就是岁月。",
				"人日快乐！愿你身边的人，都平平安安。",
				"正月初七吃面，面条越长，寓意福气越长久。",
				"人日这天给远方的亲人发个视频，看看彼此的样子。",
				"人日快乐！新的一年，愿你有事做、有人爱、有期待。",
				"正月初七，古人把这天当作“人的生日”，人人长一岁。",
				"人日出门走走，年后的街道已经慢慢恢复热闹。",
				"人日快乐！愿你今年的每一次努力，都被看见。",
				"正月初七，家里的年货该清点了，别放坏了。",
				"人日这天，给孩子讲讲故事，比塞红包更有意义。",
				"人日快乐！愿你在新的一年，睡得踏实、吃得香甜。",
				"正月初七，天气还冷，出门记得戴好围巾。",
				"人日吃七样菜，图的是新的一年样样都有。",
				"人日快乐！愿你今年的计划，都能一步一步落地。",
				"正月初七，把过年的剩饭剩菜清一清，给冰箱腾地方。",
				"人日这天，适合给自己写一封信，明年再打开。",
				"人日快乐！愿你去年的疲惫，在今年慢慢消散。",
				"正月初七，亲戚走得差不多了，家里也该静下来了。",
				"人日这天不妨早点睡，假期熬夜的账总要还。",
				"人日快乐！愿你今年遇到的都是好人，碰到的都是好事。",
				"正月初七，出门打工的人陆续返程，路上注意安全。",
				"人日适合把家里彻底打扫一遍，年也算过完了。",
				"人日快乐！愿你新的一年，心里有光、脚下有路。",
				"正月初七，给孩子准备好开学要用的东西，别临时抓瞎。",
				"人日这天，给帮过你的人发句谢谢，不用等过节。",
				"人日快乐！愿你在新的一年，少些将就、多些喜欢。",
				"正月初七，天气转暖，被子可以拿出来晒晒了。",
				"人日这天，泡杯热茶，安安静静坐一会儿。",
				"人日快乐！愿你今年的每一次出发，都有归途。",
				"正月初七，年后的第一顿家常饭，简单点也很好。",
				"人日这天，把过年收的红包记个账，心里有数。",
				"人日快乐！愿你新的一年，身体比去年更结实。",
				"正月初七，春天已经不远了，可以开始计划春游。",
				"人日这天，给家里老人量量血压，关心要落在实处。",
				"人日快乐！愿你今年的日子里，笑声比叹息多。",
				"正月初七，返程高峰，火车上记得看好行李。",
				"人日这天，把假期的照片挑几张洗出来，挂起来。",
				"人日快乐！愿你在新的一年，被人认真对待。",
				"正月初七，古人会在这天登高赋诗，你也可以写两句。",
				"人日这天，给阳台上的花换换土，新一年新气象。",
				"人日快乐！愿你今年的每一步，都走得心安。",
				"正月初七，把过年没吃完的糖果收好，慢慢吃。",
				"人日快乐！愿新的一岁，你比去年更自在。",
			],
		},
		{
			name: "元宵节", lunar: [1, 15], effect: "lantern",
			blessings: [
				"元宵节快乐！记得吃汤圆，甜的咸的都好吃，团圆才是重点。",
				"花灯亮起来了，元宵节记得出门看看灯，顺便猜两个灯谜。",
				"正月十五元宵节，一碗汤圆下肚，这个年才算真正过完。",
				"元宵节到啦，汤圆别贪多，糯米不好消化，吃几个意思到了就行。",
				"今天是元宵节，愿你的日子像汤圆一样，圆圆满满、甜甜蜜蜜。",
				"元宵节的月亮最圆，抬头看看，也把祝福送给远方的人。",
				"灯会热闹，人多的地方看好随身物品，元宵节玩得开心也要注意安全。",
				"元宵节快乐！吃汤圆的时候慢慢嚼，别烫着，也别噎着。",
				"元宵节也叫灯节，旧时家家户户挂灯，一路看过去像星河。",
				"有些地方元宵要“走三桥”，走过桥就算把病气甩在身后了。",
				"元宵节猜灯谜，猜不出也别较劲，图的是个乐子。",
				"元宵节吃汤圆别配冷饮，糯米遇冷更不好消化。",
				"元宵节的花灯再好看，也别伸手去摸，烫着或者碰坏都不好。",
				"元宵节晚上出门看灯，记得牵好孩子的手，人多容易走散。",
				"元宵的汤圆馅料多，花生、芝麻、豆沙，你最爱哪一种？",
				"元宵节快乐！愿今年的日子像灯笼一样红火。",
				"有些地方元宵要“送灯”，把灯送到祖坟前，寄托思念。",
				"元宵节猜灯谜，谜底大多是吉祥话，图个好彩头。",
				"元宵的糯米不好消化，老人和孩子要少吃一点。",
				"元宵节快乐！愿你和家人的距离，总是刚刚好的近。",
				"元宵这天晚上，月亮升起来的时候记得抬头看看。",
				"元宵的灯笼挂满街，拍照别只顾低头看手机。",
				"元宵节快乐！愿你去年的心愿，在今年圆满。",
				"有些地方元宵要吃“元宵”，滚出来的，比汤圆更有嚼劲。",
				"元宵节逛灯会，钱包手机放好，别给小偷可乘之机。",
				"元宵节快乐！愿你今年的路，亮堂堂的。",
				"元宵的灯谜猜不出来没关系，笑一笑也是过节。",
				"元宵节前后还在年里，见到长辈记得问声好。",
				"元宵节快乐！愿你的日子，甜而不腻。",
				"元宵这天有些地方要舞龙舞狮，锣鼓一响年味就回来了。",
				"元宵的汤圆趁热吃，凉了皮会硬，口感差很多。",
				"元宵节快乐！愿你和喜欢的人，年年都能一起看灯。",
				"元宵夜风凉，出门看灯记得多穿一件。",
				"元宵节的灯会人多，带孩子可以约定走散后的集合点。",
				"元宵节快乐！愿你的生活，像灯一样有光。",
				"元宵这天可以给远方的朋友发张花灯的照片。",
				"元宵的汤圆煮到浮起来就熟了，别煮太久。",
				"元宵节快乐！愿今年的你，比去年更从容。",
				"元宵节过后，年就算过完了，该收心了。",
				"元宵节快乐！愿你手头的事，都顺顺当当。",
				"元宵这天，家里的灯可以都打开，图个亮亮堂堂。",
				"元宵的灯谜有些很难，孩子猜不出别打击他。",
				"元宵节快乐！愿你今年少些烦恼，多些笑声。",
				"元宵节晚上放烟花要注意规定，别在禁放区点火。",
				"元宵的汤圆配点姜茶，胃里更舒服。",
				"元宵节快乐！愿你的家人，都在身边。",
				"元宵这天，给爸妈打个电话，问问他们吃汤圆没有。",
				"元宵节的灯会是拍照的好地方，记得给手机留点电。",
				"元宵节快乐！愿你今年想去的地方都能去成。",
				"元宵的糯米制品别给太小的孩子吃，容易噎着。",
				"元宵节快乐！愿你的努力，都有人看见。",
				"元宵这天晚上，把家里的灯都点亮，寓意光明顺遂。",
				"元宵节快乐！愿你和朋友的感情，越处越浓。",
				"元宵的汤圆可以自己包，和孩子一起动手更有意思。",
				"元宵节快乐！愿你今年身体康健，少跑医院。",
				"元宵节前后早晚温差大，出门记得带外套。",
				"元宵节快乐！愿你的每个小目标，都能实现。",
				"元宵这天，把过年的最后一点年货吃完，别浪费。",
				"元宵节快乐！愿你在新的一年，被好运偏爱。",
				"元宵节快乐！愿灯火可亲，家人可念。",
			],
		},
		{
			name: "春社", effect: "leaf", term: 3, stem: "戊", nth: 5,
			blessings: [
				"今天是春社，古时候人们在这天祭土地、祈丰年，愿今年风调雨顺。",
				"春社到了，正是春耕的时候，愿你播下的种子都能有个好收成。",
				"春社这天有吃社饭、喝社酒的习俗，图的就是一年顺遂。",
				"春社快乐！春天已经过半，趁着好天气多出去走走。",
				"春社这天，老辈人会去田埂上走一圈，看看麦苗返青没有。",
				"社日有分“社肉”的旧俗，邻里分一口，图的是和气。",
				"春社前后雨水多，出门带把伞，别嫌麻烦。",
				"春社这天，村里有请戏班唱社戏的旧俗。",
				"社日前后燕子回来了，抬头看看屋檐下的新泥。",
				"春社的社饭里会放腊肉、野菜，香得很。",
				"春社快乐！愿今年的庄稼，都长得壮实。",
				"春社这天不宜动土，是老辈人传下来的讲究。",
				"社日祭土地，求的是一年风调雨顺、五谷丰登。",
				"春社前后正是播种的时候，别误了农时。",
				"春社快乐！愿你在春天种下的愿望，秋天都有收成。",
				"春社这天，把家里的农具收拾收拾，该修修了。",
				"社日的社酒度数不高，尝尝就好，别贪杯。",
				"春社快乐！愿今年的雨水，来得刚刚好。",
				"春社这天，带孩子去田边认认庄稼，也是长见识。",
				"春社前后野菜最嫩，荠菜、马兰头都可以采。",
				"春社快乐！愿你今年的辛苦，都有回报。",
				"社日这天，邻里之间分一分社肉，和气最重要。",
				"春社的雨一下，地里的墒情就好，农人最盼这个。",
				"春社快乐！愿你家今年的粮仓，装得满满当当。",
				"春社这天，给院里的果树松松土、施施肥。",
				"社日前后青蛙开始叫了，田里的活也该忙起来。",
				"春社快乐！愿今年的春风，吹散你所有烦心事。",
				"春社这天，老农会看天色估年景，经验都是攒出来的。",
				"春社前后昼夜温差大，下地干活记得带件外套。",
				"春社快乐！愿你今年做的事，都有好结果。",
				"社日有“做社”的习俗，凑份子办席，吃的就是热闹。",
				"春社这天，别踩刚出苗的地，一脚就是一季的收成。",
				"春社快乐！愿今年风调雨顺，家家有余。",
				"社日的社糕、社饼，甜咸都有，趁热吃最香。",
				"春社前后是踏青的好时候，田埂上绿油油一片。",
				"春社快乐！愿你今年有个好开头。",
				"春社这天，把冬天的棉衣洗洗收起来，天要暖了。",
				"社日祭完土地，农人心里就踏实了，一年的希望都在地里。",
				"春社快乐！愿你今年的每一步，都踩在实处。",
				"春社这天，去菜市场买把春笋，尝尝春天的味道。",
				"春社前后雨水多，家里的墙角注意防潮。",
				"春社快乐！愿今年的日子，越过越有奔头。",
				"社日的旧俗里，还有妇女停针线的说法，歇一天也好。",
				"春社这天，给远处的亲戚打个电话，问问春耕的情况。",
				"春社快乐！愿你今年的心情，像春天一样舒展。",
				"春社前后种树正合适，成活率高。",
				"春社这天，把院子扫一扫，落叶沤肥正好。",
				"春社快乐！愿今年的饭桌上，常有新鲜的菜。",
				"社日有吃“社粥”的地方，杂粮一起熬，养胃。",
				"春社前后蜱虫开始活跃，去草地穿长裤。",
				"春社快乐！愿你今年的愿望，都能发芽。",
				"春社这天，看看天气，晴天就把被子晒出去。",
				"社日的热闹就这一天，过了还是要下地干活。",
				"春社快乐！愿今年的收成，配得上你的辛苦。",
				"春社前后桃花开了，赏花别折枝，看看就好。",
				"春社这天，给土地爷上炷香，图个心安。",
				"春社快乐！愿今年少些天灾，多些顺遂。",
				"社日之后，春天就真正热闹起来了。",
				"春社快乐！愿你今年，种什么得什么。",
				"春社这天，愿你家今年的种子，都落在好土里。",
			],
		},
		{
			name: "清明节", range: [[4, 4], [4, 6]], effect: "petal",
			blessings: [
				"今天是清明，扫墓祭祖、踏青插柳都是老习俗，路上注意安全。",
				"清明时节雨纷纷，出门记得带伞，山路湿滑要慢一点走。",
				"清明节，缅怀先人的同时也别忘了照顾好自己，好好吃饭。",
				"清明前后气温忽冷忽热，衣服别急着减，春捂还是有道理的。",
				"今天是清明，也是寒食，祭扫时别烧纸点香，用鲜花更妥当。",
				"清明踏青正当时，花粉多，过敏的人记得戴口罩。",
				"清明插柳的习俗传了很久，柳枝好活，插下去就是一片绿。",
				"清明踏青别踩农田，庄稼刚返青，一脚下去就是一年的收成。",
				"清明祭扫用鲜花、植树都挺好，比烧纸更安全也更干净。",
				"清明时节乍暖还寒，早晚温差大，外套还是带着吧。",
				"清明前后，江南的油菜花开成一片，值得去看看。",
				"清明祭扫要错峰，假期第一天路上最堵。",
				"清明这天，把先人的墓碑擦一擦，是份心意。",
				"清明不谈快乐，愿你平安顺遂就好。",
				"清明踏青可以放风筝，线要收好，别缠到电线上。",
				"清明前后雨水多，家里注意防潮，衣服别闷着。",
				"清明的青团用艾草汁和面，甜咸都好吃。",
				"清明时节，柳树抽芽，折一枝插在门口也是习俗。",
				"清明这天，带老人出门要慢一点，路滑。",
				"清明前后是采春茶的时候，新茶清香。",
				"清明祭扫别在山上抽烟，一个烟头能毁一片林。",
				"清明的雨说下就下，出门带把折叠伞不占地方。",
				"清明这天，给孩子讲讲家里的长辈，让他们知道来处。",
				"清明前后湿气重，关节不好的人注意保暖。",
				"清明的青团糯米多，一次吃一两个就够。",
				"清明踏青别走没路的地方，草深的地方有蛇虫。",
				"清明这天，把家里的照片翻出来看看，也是种怀念。",
				"清明前后昼夜温差大，出门带件薄外套。",
				"清明祭扫用鲜花，比烧纸更环保也更安全。",
				"清明这天，路上车多，开车别急，让一让。",
				"清明的艾草可以采回来晒干，煮水泡脚。",
				"清明前后是种树的好时候，栽一棵留个念想。",
				"清明这天，给远方的亲人打个电话，说说话。",
				"清明的雨落在瓦上，声音很好听，别嫌它烦。",
				"清明前后花粉多，过敏的人出门戴口罩。",
				"清明祭扫后别急着走，把垃圾带走。",
				"清明这天，家里的老人最需要陪伴，多坐一会儿。",
				"清明前后的春笋最鲜，油焖、炖汤都好。",
				"清明踏青拍照，别踩进花田里，农户心疼。",
				"清明这天，把冬天的厚被子收起来，换薄的。",
				"清明前后天气忽冷忽热，孩子穿衣要方便增减。",
				"清明祭扫的山路窄，停车别堵住别人。",
				"清明这天，煮一锅青团，家里就有了节气的味道。",
				"清明前后适合大扫除，把角落的灰清一清。",
				"清明这天，给先人说说家里的近况，他们会听见。",
				"清明的风大，放风筝要远离马路和电线。",
				"清明前后野菜肥，采的时候认准了再下手。",
				"清明这天，陪父母去趟老家，路远也值得。",
				"清明前后湿气重，被褥挑晴天晒晒。",
				"清明祭扫回来，先洗手再吃东西。",
				"清明这天，把家里的老物件擦擦灰，都是回忆。",
				"清明前后的雨，对庄稼是好事，别抱怨。",
				"清明这天，路上遇到祭扫的人，让一让。",
				"清明前后适合喝茶，明前茶贵，尝尝鲜就好。",
				"清明这天，把心里的话说给亲人听，别憋着。",
				"清明前后早晚凉，晨练别太早出门。",
				"清明的青团别买太多，放两天就硬了。",
				"清明这天，给孩子讲讲清明的由来，也是传承。",
				"清明前后雨水足，阳台的花该施肥了。",
				"清明这天，愿逝者安息，生者坚强。",
			],
		},
		{
			name: "上巳节", lunar: [3, 3], effect: "petal",
			blessings: [
				"三月初三上巳节，古人有临水洗濯、踏青游春的习俗，今天也出去走走吧。",
				"上巳节到了，春水初生，岸边风大，靠近水边要注意脚下。",
				"今天是上巳节，古时候人们在这天用荠菜煮鸡蛋，你也试试？",
				"上巳节快乐！春光正好，约上朋友去郊外走走，别辜负好天气。",
				"三月三上巳节，有些地方有对歌的习俗，热闹归热闹，别挤着。",
				"上巳节古人有“曲水流觞”的雅事，酒杯顺水漂，漂到谁面前谁作诗。",
				"三月三有些地方要蒸五色糯米饭，颜色都是草木染的。",
				"上巳节踏青，草丛里虫子开始活跃，穿长裤比短裤稳妥。",
				"上巳节前后，河边的柳树最好看。",
				"三月三有些地方要赶歌圩，热闹得很。",
				"上巳这天，古人有在水边祓禊的习俗，洗去晦气。",
				"上巳节快乐！愿你的春天，处处是花。",
				"三月三的荠菜花煮鸡蛋，是老一辈的讲究。",
				"上巳前后野菜多，采回来包饺子很香。",
				"上巳节这天，去公园走一走，看看新绿。",
				"上巳快乐！愿你的心情，像春天一样轻。",
				"三月三有些地方要吃五色饭，颜色好看。",
				"上巳前后天气回暖，可以开始晨跑了。",
				"上巳节这天，把冬天的厚袜子换掉，脚也轻松。",
				"上巳快乐！愿今年的你，少些疲惫。",
				"三月三的河边人多，看好孩子别靠水太近。",
				"上巳前后桃花、杏花都开了，赏花正当时。",
				"上巳节这天，泡一壶明前茶，坐着发会儿呆。",
				"上巳快乐！愿你的日子，有花有茶有闲。",
				"三月三的风筝飞得高，线要握稳。",
				"上巳前后空气潮湿，家里的米面注意防霉。",
				"上巳节这天，给朋友发张春天的照片。",
				"上巳快乐！愿你去年的辛苦，在今年开花。",
				"三月三的春水涨了，别在河边玩水。",
				"上巳前后种花正好，成活率高。",
				"上巳节这天，把窗户打开，让春风进来。",
				"上巳快乐！愿你的心事，都被春风吹散。",
				"三月三有些地方要祭祖，是份心意。",
				"上巳前后阳光好，被子拿出来晒晒。",
				"上巳节这天，吃点春笋、香椿，尝个鲜。",
				"上巳快乐！愿你的努力，早日有回响。",
				"三月三的郊外人多，垃圾记得带走。",
				"上巳前后昼夜温差大，出门带件外套。",
				"上巳节这天，和孩子一起认认路边的野花。",
				"上巳快乐！愿你的生活，常有小惊喜。",
				"三月三有些地方要喝桃花酒，浅尝即可。",
				"上巳前后草长莺飞，适合拍张春天的照片。",
				"上巳节这天，把家里的绿植换个盆。",
				"上巳快乐！愿你今年的愿望，都开花结果。",
				"三月三的集市热闹，买东西记得讲价。",
				"上巳前后雨水多，出门带伞。",
				"上巳节这天，给爸妈打个电话，说说春天。",
				"上巳快乐！愿你的身边，常有暖心的人。",
				"三月三的山路湿滑，登高穿防滑鞋。",
				"上巳前后适合踏青野餐，垃圾记得收好。",
				"上巳节这天，把去年的春装翻出来，还挺合身。",
				"上巳快乐！愿你的春天，有盼头。",
				"三月三的溪水清，别下去洗手洗脚，容易着凉。",
				"上巳前后花多，过敏的人随身带药。",
				"上巳节这天，给自己买束春天的花。",
				"上巳快乐！愿你的日子，越过越舒展。",
				"三月三的傍晚风凉，散步记得加件衣服。",
				"上巳前后适合整理衣柜，把冬装收起来。",
				"上巳节这天，晒晒太阳，补补钙。",
				"上巳快乐！愿春光不负赶路人。",
			],
		},
		{
			name: "端午节", lunar: [5, 5], effect: "leaf", colors: ["#7bc96f", "#4caf50", "#a5d6a7"],
			blessings: [
				"端午安康！粽子好吃，但糯米不好消化，一次别吃太多。",
				"端午节到了，门口挂艾草、身上佩香囊，都是驱蚊避秽的老讲究。",
				"今天是端午，看龙舟比赛记得站在安全线外，别往水边挤。",
				"端午安康！甜粽咸粽都随你，重要的是和家人一起吃。",
				"端午这天有喝雄黄酒的旧俗，现在别真喝，含酒精的东西要当心。",
				"端午节，记得把艾草挂起来，蚊子少了，晚上睡得也香。",
				"端午安康！天气渐热，粽子放冰箱也要尽快吃完，别放坏了。",
				"今天是端午节，愿你身体康健、诸事顺遂，烦恼都被龙舟带走。",
				"端午要系五彩绳，老话说能避五毒，端午后第一场雨再解下来。",
				"端午的粽子叶要煮过再用，不然容易裂，煮的时候加点盐更香。",
				"端午前后湿气重，艾草晒干了挂在门口，还能拿来煮水泡脚。",
				"端午看龙舟别下水，水急人多，安全比热闹重要。",
				"端午这天中午的太阳最毒，出门记得打伞涂防晒。",
				"端午的香囊可以自己缝，放点艾草薄荷，好闻又驱蚊。",
				"端午这天，把门上的艾草和菖蒲挂好，是老讲究。",
				"端午的咸鸭蛋流油最好吃，配粥一绝。",
				"端午快乐！愿你的身体，像龙舟一样有劲。",
				"端午前后蛇虫活跃，家里的角落撒点雄黄粉。",
				"端午的雄黄酒别给小孩碰，酒精对孩子没好处。",
				"端午包粽子，糯米别塞太满，煮的时候会胀开。",
				"端午快乐！愿你的日子，有滋有味。",
				"端午的龙舟鼓点一响，岸上的人也跟着热血。",
				"端午前后湿气重，红豆薏米水可以煮起来。",
				"端午的粽子冷水下锅，水开后再煮一个钟头。",
				"端午快乐！愿你和家人，都健健康康。",
				"端午这天，把五彩绳系在手腕上，图个平安。",
				"端午的艾草水可以洗澡，驱蚊又清爽。",
				"端午快乐！愿你去年的病痛，今年都远离。",
				"端午前后天气闷，家里的衣服要及时晾干。",
				"端午的粽子别空腹吃，糯米伤胃。",
				"端午快乐！愿你的生活，像粽子一样有料。",
				"端午这天，给孩子讲讲屈原的故事，也是传承。",
				"端午的香囊挂在书包上，孩子喜欢。",
				"端午快乐！愿你的每一步，都稳稳当当。",
				"端午前后蚊子多，纱窗记得检查。",
				"端午的粽子叶要洗净煮软，包起来才不破。",
				"端午快乐！愿你的端午，有粽有茶有家人。",
				"端午这天，看龙舟别翻越护栏，安全第一。",
				"端午的绿豆糕配粽子，甜咸正好。",
				"端午快乐！愿你的努力，都有回响。",
				"端午前后出汗多，记得补点淡盐水。",
				"端午的艾草晒干挂门口，能用到明年。",
				"端午快乐！愿你的心情，像江水一样开阔。",
				"端午这天，把家里的被褥拿出去晒晒。",
				"端午的粽子一次别买太多，放久了不新鲜。",
				"端午快乐！愿你的家人，都平平安安。",
				"端午前后雨水多，出门带伞。",
				"端午的龙舟赛在中午最热，记得防晒。",
				"端午快乐！愿你今年的心愿，都能实现。",
				"端午这天，给远方的朋友寄几个粽子。",
				"端午的艾叶煮鸡蛋，是老一辈的做法。",
				"端午快乐！愿你的日子，越过越顺。",
				"端午前后青梅熟了，泡一坛青梅酒。",
				"端午的粽子蘸白糖，是很多人的童年味道。",
				"端午快乐！愿你今年的身体，比去年棒。",
				"端午这天，把家里打扫一遍，用艾草水拖地。",
				"端午的香囊可以送给孩子，图个安康。",
				"端午快乐！愿你的端午，安康顺遂。",
				"端午前后别贪凉，空调温度别太低。",
				"端午快乐！愿你在夏天开始的时候，一切顺利。",
			],
		},
		{
			name: "初伏", effect: "ember", term: 12, stem: "庚", nth: 3,
			blessings: [
				"今天入初伏，一年里最热的日子开始了，绿豆汤可以安排上了。",
				"初伏到了，空调别开太低，室内外温差大最容易感冒。",
				"入伏第一天，记得多喝水、少在正午出门，防晒也要做足。",
				"初伏快乐！天热胃口差，吃点清淡的，别拿冰饮当饭吃。",
				"头伏饺子二伏面，老话这么讲，图个应景也图个胃口。",
				"初伏开始贴三伏贴的人多了，皮肤敏感的先问问医生。",
				"伏天出汗多，衣服湿了及时换，捂着容易起痱子。",
				"初伏这天，北方讲究吃饺子，图个“元宝”的好意头。",
				"入伏后中午别在太阳下久站，容易中暑。",
				"初伏快乐！愿你熬过酷暑，秋天有收获。",
				"伏天出汗多，衣服选棉麻的透气。",
				"初伏的绿豆汤煮到开花，晾温了喝最解暑。",
				"初伏快乐！愿你的夏天，有风有凉。",
				"入伏后胃口差，吃点酸的开开胃。",
				"初伏前后空调别开整夜，容易着凉。",
				"初伏快乐！愿你今年的夏天，不太难熬。",
				"伏天晒背是老讲究，选早上九十点钟。",
				"初伏的冬瓜汤清淡利尿，适合暑天。",
				"初伏快乐！愿你心里有片阴凉。",
				"入伏后老人和孩子最容易中暑，多留意。",
				"初伏前后把凉席拿出来洗洗晒晒。",
				"初伏快乐！愿你的夏天，少些烦躁。",
				"伏天喝水要少量多次，别一次灌一大瓶。",
				"初伏的苦瓜炒蛋，清火又下饭。",
				"初伏快乐！愿你今年的伏天，平平安安。",
				"入伏后室内外温差大，进出门缓一缓。",
				"初伏前后是冬病夏治的时候，三伏贴要问医生。",
				"初伏快乐！愿你身上无病，心里无事。",
				"伏天的西瓜别贪多，冰镇的更要少吃。",
				"初伏这天，把厚被子收起来，换上薄被。",
				"初伏快乐！愿你的夏天，有西瓜有晚风。",
				"入伏后蚊虫多，纱窗和蚊帐都检查一遍。",
				"初伏的丝瓜汤清甜，适合暑天喝。",
				"初伏快乐！愿你今年的努力，都有回报。",
				"伏天出门戴帽子，比涂防晒更实在。",
				"初伏前后雨水多，注意家里防潮。",
				"初伏快乐！愿你的心情，像树荫一样凉。",
				"入伏后别用冷水冲头，容易头疼。",
				"初伏的酸梅汤自己煮，比饮料健康。",
				"初伏快乐！愿你的家人，都安然度夏。",
				"伏天运动选早晚，中午别硬撑。",
				"初伏前后把风扇擦干净再用。",
				"初伏快乐！愿你今年夏天，少跑医院。",
				"入伏后饭菜别放太久，天热容易坏。",
				"初伏的凉面过一遍凉水，拌上麻酱很香。",
				"初伏快乐！愿你的日子，清清爽爽。",
				"伏天出汗后别马上吹空调，先擦干。",
				"初伏前后给孩子备好防晒帽。",
				"初伏快乐！愿你的夏天，有盼头。",
				"入伏后午睡二十分钟，下午精神很多。",
				"初伏的绿豆薏米粥，祛湿又解暑。",
				"初伏快乐！愿你的生活，冷暖刚好。",
				"伏天出门带瓶水，别等渴了才喝。",
				"初伏前后把冰箱清一清，腾地方放西瓜。",
				"初伏快乐！愿你的夏天，平安喜乐。",
				"入伏后洗澡水温别太低，温水更舒服。",
				"初伏这天，给爸妈打个电话，叮嘱他们防暑。",
				"初伏快乐！愿你熬过三伏，迎来秋凉。",
				"伏天心静自然凉，别跟自己较劲。",
				"初伏快乐！愿你这个夏天，过得舒心。",
			],
		},
		{
			name: "中伏", effect: "ember", term: 12, stem: "庚", nth: 4,
			blessings: [
				"今天进中伏，是一年里最闷热的一段，出门记得带水。",
				"中伏到了，出汗多，光喝水还不够，适当补点盐分。",
				"中伏天热，中午尽量别在太阳底下待着，小心中暑。",
				"中伏快乐！晚上睡觉空调定时关，别贪凉吹一整夜。",
				"中伏是一年里最熬人的一段，午睡二十分钟，下午能精神不少。",
				"中伏天喝冰水一时爽，肠胃弱的人还是常温的更稳妥。",
				"中伏湿气重，家里多开窗通风，被褥挑晴天晒一晒。",
				"中伏是一年里最热的一段，出门尽量避开正午。",
				"中伏快乐！愿你有空调有西瓜，安然度夏。",
				"中伏前后容易犯困，中午歇一会儿。",
				"中伏的绿豆汤别放太多糖，清淡更好。",
				"中伏快乐！愿你今年的夏天，不太难熬。",
				"中伏天热，心脑血管的人要格外当心。",
				"中伏前后别在户外剧烈运动，量力而行。",
				"中伏快乐！愿你的日子，有一处清凉。",
				"中伏的凉拌菜现做现吃，别放隔夜。",
				"中伏快乐！愿你的家人，都平平安安。",
				"伏天出汗多，内衣勤换，别捂出痱子。",
				"中伏前后食物容易变质，剩菜及时冷藏。",
				"中伏快乐！愿你的夏天，有风有雨有凉。",
				"中伏的冬瓜排骨汤，清淡又补水。",
				"中伏快乐！愿你今年的伏天，少些烦躁。",
				"中伏天热，车里别放打火机和香水。",
				"中伏前后孩子玩水要有大人看着。",
				"中伏快乐！愿你的努力，都有回响。",
				"中伏的西瓜切开尽快吃完，别放太久。",
				"中伏快乐！愿你的夏天，甜而不腻。",
				"伏天出门前看看温度，超过三十五度就别硬跑。",
				"中伏前后空调滤网该洗了，吹出来的风才干净。",
				"中伏快乐！愿你的生活，清凉自在。",
				"中伏的绿豆沙冰镇一下，是夏天的味道。",
				"中伏快乐！愿你的家人，都安然度夏。",
				"中伏天热，老人午睡要有人照看。",
				"中伏前后雨水多，出门带伞。",
				"中伏快乐！愿你的夏天，有盼头。",
				"中伏的冬瓜汤、丝瓜汤换着喝，不腻。",
				"中伏快乐！愿你今年的身体，比去年结实。",
				"伏天别贪凉睡地板，湿气重。",
				"中伏前后把竹席擦一遍，睡着更舒服。",
				"中伏快乐！愿你的心情，像树荫一样凉。",
				"中伏的凉面配黄瓜丝，爽口。",
				"中伏快乐！愿你的夏天，少些烦恼。",
				"中伏天热，别把孩子单独留在车里。",
				"中伏前后中午尽量别出门，有事晚点办。",
				"中伏快乐！愿你的日子，清清爽爽。",
				"中伏的酸梅汤冰镇后更好喝。",
				"中伏快乐！愿你的家人，都健健康康。",
				"伏天出汗多，记得补点盐分。",
				"中伏前后把被子拿出去晒晒，去潮气。",
				"中伏快乐！愿你的夏天，有惊无险。",
				"中伏的冬瓜丸子汤，鲜美又清淡。",
				"中伏快乐！愿你的努力，都有收获。",
				"中伏天热，开车的朋友注意轮胎气压。",
				"中伏前后别在太阳下晾太久，容易晒伤。",
				"中伏快乐！愿你的生活，安稳顺遂。",
				"中伏的绿豆汤晾温了再喝，别贪凉。",
				"中伏快乐！愿你熬过这段最热的日子。",
				"伏天里心平气和，比什么都解暑。",
				"中伏快乐！愿这个夏天，对你温柔一点。",
				"中伏的傍晚，太阳落山后出门走走，比白天舒服。",
			],
		},
		{
			name: "末伏", effect: "ember", term: 15, stem: "庚", nth: 1,
			blessings: [
				"今天末伏，最热的日子快熬到头了，再坚持一下。",
				"末伏到了，早晚开始有凉意，空调温度可以调高一点了。",
				"末伏天，暑气还没消，别急着吃太补的东西，清淡过渡就好。",
				"末伏快乐！秋天快来了，趁着这段时间把作息调回来。",
				"末伏有“秋老虎”的说法，白天照样热，别急着收凉席。",
				"末伏过后早晚转凉，睡觉盖条薄被，别让肚子受凉。",
				"末伏这段时间适合把夏天的作息慢慢往回调，早睡半小时。",
				"末伏到了，暑气开始收尾，早晚有凉意。",
				"末伏快乐！愿你的秋天，有个好开头。",
				"末伏前后早晚温差大，出门带件外套。",
				"末伏的西瓜可以少吃了，性凉。",
				"末伏快乐！愿你的日子，慢慢凉下来。",
				"末伏天热，别急着添厚衣服，也别继续贪凉。",
				"末伏前后把夏天的衣服洗洗收起来。",
				"末伏快乐！愿你的家人，都平安度秋。",
				"末伏的绿豆汤可以换成银耳汤，润燥。",
				"末伏快乐！愿你的夏天，有个圆满的收尾。",
				"末伏前后适合把作息调回来，早点睡。",
				"末伏快乐！愿你的努力，在秋天结果。",
				"末伏天热，空调温度可以调到二十六度。",
				"末伏的梨子开始上市，润肺。",
				"末伏快乐！愿你的身体，越来越舒坦。",
				"末伏前后雨水渐少，注意补水。",
				"末伏快乐！愿你的心情，像秋空一样高远。",
				"末伏的百合莲子汤，安神。",
				"末伏快乐！愿你的家人，都健健康康。",
				"末伏前后把凉席洗洗收起来。",
				"末伏快乐！愿你的秋天，有收获。",
				"末伏天热，别在正午晒被子，早晚更合适。",
				"末伏的葡萄甜了，尝个鲜。",
				"末伏快乐！愿你的生活，渐渐清爽。",
				"末伏前后给孩子准备好开学的东西。",
				"末伏快乐！愿你的努力，都有回响。",
				"末伏的银耳雪梨汤，润燥又甜。",
				"末伏快乐！愿你的秋天，少些干燥。",
				"末伏前后把风扇擦干净收起来。",
				"末伏快乐！愿你的日子，越过越顺。",
				"末伏天热，心静自然凉。",
				"末伏的莲藕排骨汤，正当季。",
				"末伏快乐！愿你的家人，都安然。",
				"末伏前后早晚出门散步，舒服。",
				"末伏快乐！愿你的身体，比夏天更结实。",
				"末伏的南瓜粥，暖胃。",
				"末伏快乐！愿你的秋天，有个好心情。",
				"末伏前后把空调滤网洗一洗。",
				"末伏快乐！愿你的生活，清清爽爽。",
				"末伏的板栗开始上市，糖炒的最香。",
				"末伏快乐！愿你的心愿，都在秋天实现。",
				"末伏前后注意防秋燥，多喝水。",
				"末伏快乐！愿你的家人，都平安喜乐。",
				"末伏的桂花快开了，等着闻香。",
				"末伏快乐！愿你的日子，有滋有味。",
				"末伏前后把夏天的凉鞋收起来。",
				"末伏快乐！愿你的努力，被看见。",
				"末伏的芋头蒸着吃，粉糯。",
				"末伏快乐！愿你的身体，舒舒服服。",
				"末伏前后早晚凉，睡觉盖条薄被。",
				"末伏快乐！愿你的秋天，顺顺利利。",
				"末伏的蝉声渐稀，夏天要走了。",
				"末伏快乐！愿你熬过酷暑，迎来秋凉。",
			],
		},
		{
			name: "七夕节", lunar: [7, 7], effect: "star", days: 1,
			blessings: [
				"七夕快乐！鹊桥相会的日子，愿你喜欢的人也在想着你。",
				"今天是七夕，抬头看看星空，牛郎织女的故事讲了上千年。",
				"七夕到了，送你一句：能一起吃饭、一起散步的人，才是最好的浪漫。",
				"七夕快乐！不管单身还是有伴，都要好好爱自己。",
				"七夕这天，古时候姑娘们会穿针乞巧，愿你手巧心也巧。",
				"七夕快乐！礼物不重要，被人惦记着才是真的甜。",
				"今天是七夕，晚上凉快，和喜欢的人一起散散步吧。",
				"七夕到了，愿你今年的心事都能有个好结果。",
				"七夕也叫乞巧节，古时姑娘们对着月亮穿针，比谁手更巧。",
				"七夕的巧果是炸出来的面点，甜香酥脆，做起来也不难。",
				"七夕这天有些地方要拜织女，供上瓜果，图个心灵手巧。",
				"七夕快乐！牛郎织女一年才见一面，我们天天能见面，已经很幸运了。",
				"七夕的夜晚，古人在院子里摆上瓜果，向织女乞巧。",
				"七夕快乐！愿你被人惦记，也惦记着别人。",
				"七夕的葡萄架下，传说能听见牛郎织女的私语。",
				"七夕这天，给自己买束花，单身也值得被爱。",
				"七夕的星空最值得看，找找银河在哪边。",
				"七夕快乐！愿你的喜欢，都有回应。",
				"七夕的巧果要用模具压出花样，好看又好吃。",
				"七夕前后晚上凉，出门散步记得加件衣服。",
				"七夕快乐！愿你和爱的人，慢慢变老。",
				"七夕这天，古时女子会对着月亮穿针引线。",
				"七夕的银河，是夏天最浪漫的一条线。",
				"七夕快乐！愿你的心事，有人愿意听。",
				"七夕的玫瑰贵，不如一起去看场星星。",
				"七夕这天，给喜欢的人写几句话，比发红包真诚。",
				"七夕快乐！愿你不将就，也不孤单。",
				"七夕的鹊桥一年一次，我们的日子要天天过。",
				"七夕前后蚊子多，晚上出门记得喷点花露水。",
				"七夕快乐！愿你今年，遇见对的人。",
				"七夕这天，把手机放下，抬头看看夜空。",
				"七夕的传说很美，日子还是要脚踏实地。",
				"七夕快乐！愿你的爱情，不慌不忙。",
				"七夕这天，和喜欢的人一起做顿饭。",
				"七夕的牛郎织女星，其实隔着十几光年。",
				"七夕快乐！愿你的每一个期待，都不落空。",
				"七夕前后正是葡萄成熟的季节，尝个鲜。",
				"七夕这天，给爸妈也发句祝福，他们也曾年轻。",
				"七夕快乐！愿你的日子，有甜有暖。",
				"七夕的星很亮，别让城市的灯遮住它们。",
				"七夕这天，把想说的话说出口，别留遗憾。",
				"七夕快乐！愿你所遇皆良人。",
				"七夕的夜风带着暑气，坐一会儿就凉快了。",
				"七夕这天，给远方的朋友发张星空的照片。",
				"七夕快乐！愿你的感情，细水长流。",
				"七夕的巧果甜，吃两块应应景。",
				"七夕这天，把心里的事理一理，别憋着。",
				"七夕快乐！愿你的付出，都有人珍惜。",
				"七夕前后立秋将至，早晚会凉一些。",
				"七夕这天，看星星记得带件外套。",
				"七夕快乐！愿你和喜欢的人，有说不完的话。",
				"七夕的银河横贯夜空，值得抬头看很久。",
				"七夕这天，愿单身的你也被世界温柔以待。",
				"七夕快乐！愿你的爱，先给自己。",
				"七夕的传说提醒我们，等待也是一种深情。",
				"七夕这天，给爱人一个拥抱，比礼物实在。",
				"七夕快乐！愿你的每一步，都有人同行。",
				"七夕的夜，适合安静地想一想自己想要什么。",
				"七夕快乐！愿你今年七夕，不孤单。",
				"七夕快乐！愿有情人，都能好好过日子。",
			],
		},
		{
			name: "中元节", lunar: [7, 15], effect: "lantern",
			blessings: [
				"今天是中元节，老话说这天要早点回家，路上别逗留太晚。",
				"中元节，也称盂兰盆节，缅怀逝去的亲人，也别忘了照顾好身边的人。",
				"七月十五中元节，有些地方有放河灯的习俗，水边风大要注意安全。",
				"中元节到了，夜里少去偏僻的地方，不是迷信，是图个心安。",
				"中元节，点一盏灯，愿远行的人都被温柔以待。",
				"中元节有些地方要祭祖，摆上饭菜，说几句家常话。",
				"中元节的河灯顺着水漂远，寄托的是思念，不是迷信。",
				"中元前后夜里凉，早点回家，也顺便早点休息。",
				"中元节前后，家里会摆上供品，点上香。",
				"中元节谈不上快乐，愿你心里安稳。",
				"中元节的夜里，街边的纸钱摊子多，注意防火。",
				"中元这天，给逝去的亲人烧一炷香，说说话。",
				"中元节的河灯，一盏一盏漂远，很好看也很安静。",
				"中元前后夜里凉，出门散步披件外套。",
				"中元这天，家里的老人会讲起从前的事，耐心听。",
				"中元节，记得给父母打个电话，他们也需要陪伴。",
				"中元节的供品，摆完记得收好，别浪费。",
				"中元这天，孩子问起鬼怪，别吓唬他。",
				"中元节前后雨水多，烧纸要选空旷的地方。",
				"中元节的夜晚，早点回家，家人会等你。",
				"中元这天，把家里的老照片拿出来擦擦。",
				"中元节，愿逝者安宁，生者珍惜眼前人。",
				"中元节的河灯顺水而去，寄托的是思念。",
				"中元前后蛇虫多，草木深的地方少去。",
				"中元这天，给先人摆双筷子，是份心意。",
				"中元节，愿所有的告别，都不太难过。",
				"中元节的夜里安静，适合想一些平时不想的事。",
				"中元这天，把心里的思念说给自己听。",
				"中元节，愿你在另一个世界的亲人，一切安好。",
				"中元前后天气转凉，注意别着凉。",
				"中元节的供果，挑新鲜的，摆完还能吃。",
				"中元这天，给远方的家人报个平安。",
				"中元节，愿活着的人，都把日子过好。",
				"中元节的香火味，是很多人童年的记忆。",
				"中元前后晚上别在河边久留，风大。",
				"中元这天，把老屋的门窗检查一遍。",
				"中元节，愿你的思念，有个安放的地方。",
				"中元节的纸灯，写上名字再放，是老习俗。",
				"中元这天，给家里的老人添件衣裳。",
				"中元节，愿逝去的亲人不再受苦。",
				"中元前后天黑得早了，下班路上注意安全。",
				"中元节的夜里，少去偏僻的地方，图个心安。",
				"中元这天，把家里的灯都打开，亮堂些。",
				"中元节，愿你在梦里见到想见的人。",
				"中元前后蚊子多，晚上出门喷点驱蚊水。",
				"中元节的供饭，摆完一家人再吃，是团圆。",
				"中元这天，给孩子讲讲家里的长辈，别忘了根。",
				"中元节，愿所有的思念，都被温柔接住。",
				"中元前后秋意渐浓，早晚加件衣服。",
				"中元节的夜里安静，适合早睡。",
				"中元这天，给爸妈做顿饭，比什么都实在。",
				"中元节，愿家人都平安，日子都顺遂。",
				"中元前后雨水多，家里注意防潮。",
				"中元节的香，点一炷就好，别熏着自己。",
				"中元这天，把心里的话写成字，烧给想念的人。",
				"中元节，愿你不害怕夜路，也不孤单。",
				"中元前后天气忽冷忽热，注意添减衣物。",
				"中元节的月亮，常常又圆又亮。",
				"中元这天，愿一切安好，无病无灾。",
				"中元节，愿思念有回响，人间皆平安。",
			],
		},
		{
			name: "秋社", effect: "leaf", term: 15, stem: "戊", nth: 5,
			blessings: [
				"今天是秋社，古时候人们在这天谢土地、庆丰收，愿你也收获满满。",
				"秋社到了，田里的庄稼快熟了，别忘了感谢一年的辛苦。",
				"秋社这天有吃社饭的习俗，热热闹闹吃一顿，图个五谷丰登。",
				"秋社快乐！秋高气爽，正是登高望远的好时候。",
				"秋社这天，农家会用新米做饭，第一碗先敬土地。",
				"秋社前后是收稻子的时候，晒谷场上一片金黄。",
				"秋社有“做社”的旧俗，全村凑钱办席，热闹一整天。",
				"秋社前后，稻田一片金黄，风一吹像波浪。",
				"秋社这天，农家会拿新米做饭，先敬土地。",
				"秋社快乐！愿今年的收成，装得下你的辛苦。",
				"秋社的社饭里会放新米、腊肉，香得很。",
				"秋社这天，村里的老人会说今年的年景。",
				"秋社快乐！愿你的努力，在秋天有回响。",
				"秋社前后是收玉米的时候，地里一片忙碌。",
				"秋社这天，把院子里的粮食摊开晒一晒。",
				"秋社快乐！愿今年的天气，帮农人一把。",
				"秋社的社戏一开锣，全村都来看。",
				"秋社前后早晚凉，下地干活带件外套。",
				"秋社快乐！愿你家今年的粮仓，满满当当。",
				"秋社这天，给土地爷上炷香，谢一年的照看。",
				"秋社的社酒，是用新米酿的，味道醇。",
				"秋社快乐！愿你的付出，都有回报。",
				"秋社前后柿子红了，摘几个尝尝。",
				"秋社这天，把农具收进仓，一年的活忙完了。",
				"秋社快乐！愿今年的收成，对得起汗水。",
				"秋社的社糕，甜糯可口，孩子最爱。",
				"秋社前后蚂蚱多，田边走走能看到。",
				"秋社快乐！愿你的日子，越过越殷实。",
				"秋社这天，邻里之间分一分新米，图个和气。",
				"秋社前后适合晒秋，红辣椒挂满墙。",
				"秋社快乐！愿今年的辛苦，都有个交代。",
				"秋社的社肉，用大锅炖，香飘半条街。",
				"秋社这天，把家里的粮囤检查一遍，防潮防鼠。",
				"秋社快乐！愿你的心愿，都能结果。",
				"秋社前后板栗熟了，糖炒的最香。",
				"秋社这天，给孩子讲讲粮食怎么来的。",
				"秋社快乐！愿今年的饭桌上，常有新米。",
				"秋社的社戏唱到半夜，热闹得很。",
				"秋社前后夜里凉，看戏记得带件衣服。",
				"秋社快乐！愿你的生活，五谷丰登。",
				"秋社这天，把新米煮一锅，闻闻米香。",
				"秋社前后南瓜熟了，蒸着吃最甜。",
				"秋社快乐！愿今年的雨水，来得是时候。",
				"秋社的社酒别贪杯，明天还要干活。",
				"秋社这天，给远方的亲人寄点新米。",
				"秋社快乐！愿你的付出，被看见。",
				"秋社前后天气干燥，注意防火。",
				"秋社这天，把晒谷场扫干净。",
				"秋社快乐！愿今年的日子，稳稳当当。",
				"秋社的社饭，一家人围着吃最香。",
				"秋社前后适合腌咸菜，冬天有得吃。",
				"秋社快乐！愿你的秋天，硕果累累。",
				"秋社这天，把家里的坛坛罐罐洗一洗。",
				"秋社前后红薯收了，烤着吃最香。",
				"秋社快乐！愿今年的光景，比去年好。",
				"秋社这天，给爸妈送点新米，是孝心。",
				"秋社前后早晚温差大，注意保暖。",
				"秋社快乐！愿你的努力，都有收成。",
				"秋社的月亮升起来了，晒谷场上一片银白。",
				"秋社快乐！愿今年风调雨顺，人人有余。",
			],
		},
		{
			name: "中秋节", lunar: [8, 15], effect: "lantern",
			blessings: [
				"中秋快乐！月亮圆了，记得给家里打个电话。",
				"今天是中秋，月饼甜腻，配杯热茶刚刚好。",
				"中秋到了，愿你不管身在何处，都有人惦记、有处团圆。",
				"中秋快乐！月亮很圆，愿你的生活也圆圆满满。",
				"中秋这天赏月别着凉，晚上风凉，记得披件外套。",
				"中秋快乐！月饼一次别吃太多，尤其是血糖高的人。",
				"八月十五中秋节，愿你和家人都平安顺遂，年年有今日。",
				"中秋到了，如果回不了家，就给家里报个平安吧。",
				"中秋供月要摆月饼和瓜果，苹果寓意平安，石榴寓意多子。",
				"中秋的月饼切开分着吃，一家人一人一块，才算团圆。",
				"中秋赏月别只顾拍照，抬头看两眼，月亮比照片好看。",
				"中秋前后螃蟹肥，但性寒，配姜茶吃更舒服。",
				"中秋给远方的朋友寄盒月饼，比发条消息更有分量。",
				"中秋的月亮一年里最圆，记得抬头看看。",
				"中秋快乐！愿你的家人，都在身边。",
				"中秋的月饼可以自己做，和孩子一起更有意思。",
				"中秋这天，把阳台收拾出来，摆张桌子赏月。",
				"中秋快乐！愿你去年的辛苦，今年有回报。",
				"中秋的螃蟹配黄酒，是很多人的心头好。",
				"中秋前后早晚凉，赏月记得加件外套。",
				"中秋快乐！愿你的生活，圆圆满满。",
				"中秋这天，给远方的朋友寄一盒月饼。",
				"中秋的桂花香了，泡壶桂花茶。",
				"中秋快乐！愿你的努力，都有回响。",
				"中秋的灯笼挂起来，孩子最喜欢。",
				"中秋这天，一家人吃顿饭，比什么都好。",
				"中秋快乐！愿你的心事，都能圆满。",
				"中秋的月饼别一次吃太多，热量不低。",
				"中秋前后是柚子上市的时候，酸甜正好。",
				"中秋快乐！愿你和家人，年年团圆。",
				"中秋这天，把父母的照片翻出来看看。",
				"中秋的月亮拍不出来，用眼睛记住就好。",
				"中秋快乐！愿你的日子，越过越甜。",
				"中秋的桂花酒度数不高，尝尝就好。",
				"中秋这天，给远方的亲人打个视频电话。",
				"中秋快乐！愿你的身边，常有温暖。",
				"中秋的月饼配茶，解腻。",
				"中秋前后天气好，适合出去走走。",
				"中秋快乐！愿你的心愿，都能实现。",
				"中秋这天，把家里的灯关掉，看看月亮。",
				"中秋的螃蟹性寒，配姜茶更舒服。",
				"中秋快乐！愿你的家人，都平平安安。",
				"中秋的月饼切成小块，一家人分着吃。",
				"中秋这天，给孩子讲讲嫦娥的故事。",
				"中秋快乐！愿你的生活，有滋有味。",
				"中秋前后蚊子还多，赏月喷点驱蚊水。",
				"中秋的月亮照在院子里，很安静。",
				"中秋快乐！愿你的付出，都被珍惜。",
				"中秋这天，把心里的话说给家人听。",
				"中秋的月饼盒别乱扔，可以收起来装东西。",
				"中秋快乐！愿你今年的中秋，不太孤单。",
				"中秋前后适合晒被子，秋高气爽。",
				"中秋的桂花落了一地，香味还在。",
				"中秋快乐！愿你的日子，稳稳当当。",
				"中秋这天，给爸妈做顿饭，他们嘴上说不麻烦。",
				"中秋的月饼种类多，挑一两种就好。",
				"中秋快乐！愿你的努力，被看见。",
				"中秋前后夜里凉，睡觉盖条薄被。",
				"中秋的月亮，照亮了回家的路。",
				"中秋快乐！愿人长久，共婵娟。",
			],
		},
		{
			name: "重阳节", lunar: [9, 9], effect: "leaf", days: 1,
			blessings: [
				"重阳节，记得给家里的长辈打个电话问声好。",
				"今天是重阳，登高望远是习俗，山路湿滑要穿防滑的鞋。",
				"重阳节有敬老的传统，陪家里老人吃顿饭比什么礼物都实在。",
				"重阳到了，菊花酒、重阳糕都尝一口，图个长长久久。",
				"重阳节快乐！秋天干燥，记得多喝水、多吃点梨。",
				"九九重阳，愿你和你爱的人都能健康长寿。",
				"重阳要插茱萸，古人说能避邪，如今更多是图个仪式感。",
				"重阳放风筝是老习俗，线放得越高，寓意烦恼越远。",
				"重阳糕层层叠叠，顶上插小旗，取“步步高”的意思。",
				"重阳登高别逞强，量力而行，膝盖不好的走平路也一样。",
				"重阳这天，陪长辈吃顿饭，比送礼实在。",
				"重阳快乐！愿家里的老人，都健康长寿。",
				"重阳登高，膝盖不好的走缓坡。",
				"重阳的菊花开了，赏菊别摘花。",
				"重阳前后秋燥，多喝水多吃梨。",
				"重阳快乐！愿你的父母，身体硬朗。",
				"重阳这天，给老人量量血压。",
				"重阳的茱萸可以买一小枝，插在瓶里。",
				"重阳快乐！愿你的家人，都平平安安。",
				"重阳的菊花酒香气清，浅尝即可。",
				"重阳这天，带老人去公园走走。",
				"重阳快乐！愿你的日子，长长久久。",
				"重阳的重阳糕，层层叠叠，寓意步步高。",
				"重阳前后早晚凉，老人出门多穿点。",
				"重阳快乐！愿你的努力，都有回响。",
				"重阳这天，给远方的长辈打个电话。",
				"重阳的菊花茶，清火明目。",
				"重阳快乐！愿你的心愿，都能实现。",
				"重阳登高看秋色，层林尽染。",
				"重阳这天，把家里的老照片整理一下。",
				"重阳快乐！愿你和家人，年年相聚。",
				"重阳的柿子熟了，软甜的正好。",
				"重阳前后天气干燥，注意防火。",
				"重阳快乐！愿你的生活，有滋有味。",
				"重阳这天，陪老人聊聊过去的事。",
				"重阳的菊花插在瓶里，能开一阵子。",
				"重阳快乐！愿你的家人，都健健康康。",
				"重阳登山的路上，注意脚下。",
				"重阳这天，给孩子讲讲敬老的道理。",
				"重阳快乐！愿你的父母，慢点变老。",
				"重阳的重阳糕配茶，不腻。",
				"重阳前后秋高气爽，适合拍照。",
				"重阳快乐！愿你的付出，都被看见。",
				"重阳这天，给家里老人买双舒服的鞋。",
				"重阳的菊花晒干可以泡茶。",
				"重阳快乐！愿你的日子，越过越顺。",
				"重阳登高别忘了带水。",
				"重阳这天，把院子里的落叶扫一扫。",
				"重阳快乐！愿你的家人，都安然。",
				"重阳的秋天，天很高，云很淡。",
				"重阳快乐！愿你的努力，都有收成。",
				"重阳这天，给长辈剪剪指甲，聊聊天。",
				"重阳前后适合喝蜂蜜水，润燥。",
				"重阳快乐！愿你的心愿，都能成真。",
				"重阳登高看日落，景色很好。",
				"重阳这天，把老人爱吃的菜做上。",
				"重阳快乐！愿你的家人，都长命百岁。",
				"重阳的菊花香，是秋天的味道。",
				"重阳快乐！愿你和家人，都平安喜乐。",
				"重阳快乐！愿岁岁重阳，人长久。",
			],
		},
		{
			name: "下元节", lunar: [10, 15], effect: "lantern",
			blessings: [
				"今天是下元节，民间有祭水官、放河灯的习俗，愿烦恼随水而去。",
				"下元节到了，天冷了，记得添件衣服，别硬扛。",
				"十月十五下元节，古时候这天要吃点热乎的，图个团圆。",
				"下元节，愿逝去的人安息，活着的人平安。",
				"下元节古时候要祭水官，祈求水路平安、家宅安宁。",
				"下元前后天气转冷，家里该把厚被子拿出来了。",
				"下元节吃糍粑的地方不少，糯软香甜，趁热最好吃。",
				"下元节前后，天冷了，厚被子该拿出来了。",
				"下元节快乐！愿你的家人，都平安顺遂。",
				"下元节的糍粑，趁热吃最香。",
				"下元这天，给家里的老人添件厚衣服。",
				"下元节前后雨水少，注意补水。",
				"下元节快乐！愿你去年的烦心事，都随水而去。",
				"下元节的河灯，寄托的是对平安的祈愿。",
				"下元这天，把家里的窗缝检查一遍，防风。",
				"下元节快乐！愿你的日子，安稳踏实。",
				"下元节的前身是祭水官，求水路平安。",
				"下元这天，煮一锅热汤，暖胃。",
				"下元节快乐！愿你的家人，都健健康康。",
				"下元节前后昼夜温差大，注意添衣。",
				"下元节的麻腐包子，是北方的老味道。",
				"下元节快乐！愿你的努力，都有回响。",
				"下元这天，把夏天的凉鞋彻底收起来。",
				"下元节前后适合腌菜，冬天有得吃。",
				"下元节快乐！愿你的心愿，都能实现。",
				"下元节的夜里安静，适合早睡。",
				"下元这天，给远方的亲人打个电话。",
				"下元节快乐！愿你的生活，平平顺顺。",
				"下元节前后天气干燥，注意防火。",
				"下元节的糍粑可以蘸黄豆粉，香。",
				"下元节快乐！愿你的家人，都安然。",
				"下元这天，把家里的取暖设备检查一遍。",
				"下元节前后雾霾天多，出门戴口罩。",
				"下元节快乐！愿你的付出，都被看见。",
				"下元节的汤圆，甜口咸口都行。",
				"下元这天，给爸妈买点过冬的东西。",
				"下元节快乐！愿你的日子，越过越暖。",
				"下元节前后菜价涨，囤点耐放的菜。",
				"下元节的麻腐，配点蒜末更香。",
				"下元节快乐！愿你的努力，都有收成。",
				"下元这天，把家里的地垫换成厚的。",
				"下元节前后天黑得早，下班路上注意安全。",
				"下元节快乐！愿你的家人，都平安喜乐。",
				"下元节的糍粑别吃太多，糯米不好消化。",
				"下元这天，给家里的花搬进屋里。",
				"下元节快乐！愿你的心事，都放下。",
				"下元节前后感冒多，注意保暖。",
				"下元节的汤里放点姜，驱寒。",
				"下元节快乐！愿你的身体，越来越结实。",
				"下元这天，把家里的药箱清点一遍。",
				"下元节前后适合泡脚，水温别太高。",
				"下元节快乐！愿你的日子，稳稳当当。",
				"下元节的灯火，照亮回家的路。",
				"下元节快乐！愿你的家人，都安康。",
				"下元这天，给远方的朋友发句问候。",
				"下元节前后柿子还挂着，摘几个。",
				"下元节快乐！愿你的心愿，都成真。",
				"下元节的夜里风大，关好门窗。",
				"下元节快乐！愿你的生活，有滋有味。",
				"下元节快乐！愿一切安好，无病无灾。",
			],
		},
		{
			name: "冬至", range: [[12, 21], [12, 22]], effect: "snow",
			blessings: [
				"冬至到了，北方吃饺子、南方吃汤圆，你那儿吃什么呢？",
				"今天是冬至，一年里白天最短的一天，从明天起天就慢慢长了。",
				"冬至大如年，记得吃顿热乎的，别随便对付一口。",
				"冬至这天要进补，但别一下吃太油腻，慢慢来。",
				"冬至快乐！天冷记得穿厚点，脖子和脚最容易受凉。",
				"冬至到，愿你碗里有热汤，身边有暖人。",
				"冬至这天北方家家包饺子，说是吃了不冻耳朵。",
				"冬至南方的汤圆要搓得圆，图个团团圆圆。",
				"冬至开始数九，一九二九不出手，最冷的日子还在后头。",
				"冬至进补别盲目，羊肉汤暖身，但容易上火的人少喝。",
				"冬至这天，北方的饺子馆排队最长。",
				"冬至快乐！愿你碗里有热汤，身上有暖衣。",
				"冬至的饺子馅可以换着花样，白菜猪肉最经典。",
				"冬至这天，南方的汤圆要搓得大小一致。",
				"冬至快乐！愿你的家人，都围在一张桌旁。",
				"冬至前后是一年里最冷的时候，注意保暖。",
				"冬至的羊肉汤，暖身又暖胃。",
				"冬至快乐！愿你的日子，越过越暖。",
				"冬至这天，把秋裤穿上，别硬扛。",
				"冬至的汤圆馅，黑芝麻最香。",
				"冬至快乐！愿你去年的辛苦，今年有回报。",
				"冬至前后昼短夜长，早点睡。",
				"冬至的饺子蘸醋，配瓣蒜，舒服。",
				"冬至快乐！愿你的家人，都平平安安。",
				"冬至这天，给远方的亲人打个电话。",
				"冬至的汤圆煮到浮起来就好了。",
				"冬至快乐！愿你的努力，都有回响。",
				"冬至前后适合进补，但别太油腻。",
				"冬至的羊肉汤里放点白萝卜，解腻。",
				"冬至快乐！愿你的心愿，都能实现。",
				"冬至这天，把家里的窗户关严，防风。",
				"冬至的汤圆可以做成咸的，也很好吃。",
				"冬至快乐！愿你的生活，圆圆满满。",
				"冬至前后手脚容易凉，睡前泡个脚。",
				"冬至的饺子可以多包点，冻起来慢慢吃。",
				"冬至快乐！愿你的家人，都健健康康。",
				"冬至这天，把家里的暖气片擦一擦。",
				"冬至的汤圆别煮太久，皮会破。",
				"冬至快乐！愿你的日子，有滋有味。",
				"冬至前后地滑，老人出门注意。",
				"冬至的饺子配一碗原汤，原汤化原食。",
				"冬至快乐！愿你的付出，都被看见。",
				"冬至这天，给爸妈寄点过冬的东西。",
				"冬至的汤圆一碗就好，糯米不好消化。",
				"冬至快乐！愿你的身体，越来越结实。",
				"冬至前后是晒腊味的时候。",
				"冬至的羊肉汤，加点胡椒粉更暖。",
				"冬至快乐！愿你的家人，都安然过冬。",
				"冬至这天，把家里的被子换成厚的。",
				"冬至的饺子馅里加点虾皮，鲜。",
				"冬至快乐！愿你的努力，都有收成。",
				"冬至前后适合围炉煮茶。",
				"冬至的汤圆配桂花蜜，甜香。",
				"冬至快乐！愿你今年的冬天，不太冷。",
				"冬至这天，给家里的老人暖好被窝。",
				"冬至的饺子，一家人一起包最好吃。",
				"冬至快乐！愿你的日子，稳稳当当。",
				"冬至前后注意用电安全，取暖器别靠太近。",
				"冬至的汤圆，代表团圆。",
				"冬至快乐！愿你和家人，都平安喜乐。",
			],
		},
		{
			name: "腊八节", lunar: [12, 8], effect: "snow",
			blessings: [
				"腊八到啦，喝碗热腾腾的腊八粥，过了腊八就是年。",
				"今天是腊八节，泡上一罐腊八蒜，等到过年正好吃。",
				"腊八粥食材多，煮之前记得把豆子提前泡上，才够软糯。",
				"腊八节快乐！天寒地冻，喝粥暖胃，出门记得戴帽子。",
				"腊八到了，年味一天比一天浓，家里该慢慢置办年货了。",
				"腊八节，愿这一碗热粥，把一年的辛苦都焐热了。",
				"腊八粥熬得越久越稠，豆子提前泡一夜，早上煮正好。",
				"腊八蒜要用紫皮蒜和米醋，泡到过年就绿了。",
				"腊八这天有些地方要祭祖敬神，供一碗粥，求个丰足。",
				"腊八过后就开始忙年了，扫尘、蒸馍、写春联都排上日程。",
				"腊八粥的米可以提前泡一夜，煮起来更省时间。",
				"腊八快乐！愿你的日子，越过越稠。",
				"腊八这天，把家里的罐子洗干净，准备泡蒜。",
				"腊八的腊八蒜，用紫皮蒜才绿得漂亮。",
				"腊八快乐！愿你的家人，都平安顺遂。",
				"腊八前后是一年最冷的时候，注意保暖。",
				"腊八粥里放点红枣、桂圆，甜香。",
				"腊八快乐！愿你去年的辛苦，今年有回报。",
				"腊八这天，给爸妈送一罐腊八蒜。",
				"腊八的豆子要挑饱满的，煮出来才面。",
				"腊八快乐！愿你的努力，都有回响。",
				"腊八前后适合腌腊肉，天冷不易坏。",
				"腊八粥的糖别放太多，甜了腻。",
				"腊八快乐！愿你的心愿，都能实现。",
				"腊八这天，把家里的年货单子列一列。",
				"腊八的粥熬得越久越香。",
				"腊八快乐！愿你的生活，有滋有味。",
				"腊八前后开始扫尘，为过年做准备。",
				"腊八的蒜泡到春节，正好配饺子。",
				"腊八快乐！愿你的家人，都健健康康。",
				"腊八这天，给远方的朋友寄点土特产。",
				"腊八粥可以放点花生，增加口感。",
				"腊八快乐！愿你的日子，稳稳当当。",
				"腊八前后天黑得早，下班注意安全。",
				"腊八的醋要用米醋，泡出来才香。",
				"腊八快乐！愿你的付出，都被看见。",
				"腊八这天，一家人围着一锅粥，很暖。",
				"腊八的粥剩了别倒，第二天热热还能吃。",
				"腊八快乐！愿你的身体，越来越结实。",
				"腊八前后是买春联的时候，挑副喜欢的。",
				"腊八的蒜瓣要剥干净，不然会坏。",
				"腊八快乐！愿你的家人，都安然。",
				"腊八这天，把家里的米面清点一下。",
				"腊八粥的食材可以按家里的存货来配。",
				"腊八快乐！愿你的努力，都有收成。",
				"腊八前后适合晒被子，天晴就晒。",
				"腊八的粥要小火慢熬，急不得。",
				"腊八快乐！愿你的日子，越过越暖。",
				"腊八这天，给爸妈打个电话，说说年货。",
				"腊八的蒜泡在阴凉处，别晒。",
				"腊八快乐！愿你的心愿，都能成真。",
				"腊八前后菜价涨，早点囤点。",
				"腊八的粥配点小咸菜，正好。",
				"腊八快乐！愿你的家人，都平安喜乐。",
				"腊八这天，把家里的旧东西清一清。",
				"腊八粥的枣要去核，吃着方便。",
				"腊八快乐！愿你去年的遗憾，都翻篇。",
				"腊八前后开始有年味了，心里也热乎。",
				"腊八的蒜绿了，年就近了。",
				"腊八快乐！愿你和家人，都顺顺利利。",
			],
		},
		{
			name: "除夕", chuxi: true, effect: "firework", days: 1,
			blessings: [
				"今天是除夕，辞旧迎新，年夜饭别吃太撑，守岁也别熬太晚。",
				"除夕快乐！贴春联、挂灯笼，忙完了坐下来好好吃顿饭。",
				"除夕夜，烟花热闹，但要遵守当地规定，注意安全。",
				"除夕到了，红包记得收，也记得给长辈拜个年。",
				"除夕这天要把家里打扫干净，寓意把晦气都扫出去。",
				"除夕快乐！新的一年，愿你和家人都平平安安。",
				"除夕夜守岁，记得给手机充好电，别错过朋友的祝福。",
				"今天是除夕，过去的都翻篇了，明天就是新的一年。",
				"除夕贴门神、贴春联，红纸一贴，年味就出来了。",
				"除夕的年夜饭要有鱼，取“年年有余”，但别剩太多。",
				"除夕守岁，长辈给压岁钱，图的是压住邪祟、平平安安。",
				"除夕放爆竹要看清当地规定，很多城市已经禁放了。",
				"除夕夜把垃圾留到初一以后再倒，是老辈人图吉利的老规矩。",
				"除夕这天，家家户户都在忙年夜饭。",
				"除夕快乐！愿你去年的辛苦，都有回报。",
				"除夕的春联要贴正，图个端正顺遂。",
				"除夕这天，把家里的灯都打开，亮堂。",
				"除夕快乐！愿你的家人，都围坐一桌。",
				"除夕的年夜饭要有鱼，讨个年年有余。",
				"除夕的饺子可以包几个带硬币的，图个彩头。",
				"除夕快乐！愿你的心愿，都能实现。",
				"除夕这天，给长辈磕个头、拜个年。",
				"除夕的春晚可以开着当背景音。",
				"除夕快乐！愿你的日子，越过越红火。",
				"除夕前后路上车少，开车也别太快。",
				"除夕的压岁钱，图的是压祟保平安。",
				"除夕快乐！愿你的努力，都有回响。",
				"除夕这天，把手机充好电，别错过祝福。",
				"除夕的烟花再好看，也要遵守规定。",
				"除夕快乐！愿你的家人，都平平安安。",
				"除夕这天，把去年的不顺心都留在门外。",
				"除夕的饺子要包得饱满，像元宝。",
				"除夕快乐！愿你的生活，有滋有味。",
				"除夕这天，给远方的亲人打个视频。",
				"除夕的鱼要留一点，寓意有头有尾。",
				"除夕快乐！愿你的身体，越来越结实。",
				"除夕前后天冷，守岁记得加件衣服。",
				"除夕的瓜子糖果摆上桌，图个热闹。",
				"除夕快乐！愿你的付出，都被看见。",
				"除夕这天，和孩子一起贴窗花。",
				"除夕的鞭炮声，是很多人记忆里的年味。",
				"除夕快乐！愿你的心愿，都能成真。",
				"除夕这天，把家里的垃圾先收好。",
				"除夕的饺子馅里加点韭菜，久财。",
				"除夕快乐！愿你的家人，都健健康康。",
				"除夕前后超市人多，早点买齐年货。",
				"除夕的餐桌要摆得满一点，图个丰足。",
				"除夕快乐！愿你的日子，稳稳当当。",
				"除夕这天，给爸妈倒杯酒，说句辛苦。",
				"除夕的红包，给孩子也给长辈。",
				"除夕快乐！愿你的努力，都有收成。",
				"除夕这天，把窗户上的旧窗花换掉。",
				"除夕的夜里冷，守岁别熬到太晚。",
				"除夕快乐！愿你的家人，都安然。",
				"除夕这天，把新衣服准备好，初一穿。",
				"除夕的钟声一响，就是新的一年。",
				"除夕快乐！愿你的生活，越过越顺。",
				"除夕这天，给一年里帮过你的人发句谢谢。",
				"除夕的灯火，照亮一家人的团圆。",
				"除夕快乐！愿你和家人，都平安喜乐。",
			],
		},
		{
			name: "春节", lunar: [1, 1], effect: "confetti", days: 9,
			blessings: [
				"春节快乐！新年好，祝你新的一年万事顺遂。",
				"大年初一，拜年啦！祝你身体健康、心想事成。",
				"春节到了，走亲访友记得带点心意，话别说得太满。",
				"新年第一天，愿你笑口常开，烦恼都留在去年。",
				"春节快乐！吃饭别贪杯，酒桌上量力而行。",
				"大年初一，愿你今年的每一步都走得踏实。",
				"春节到，红包拿来！开个玩笑，祝你新岁胜旧岁。",
				"春节快乐！放鞭炮要注意安全，别让孩子单独去点。",
				"大年初一不扫地、不倒垃圾，老话说怕把财气扫出去。",
				"初一要给长辈拜年，说句吉祥话，比什么礼物都暖。",
				"初二祭财神，中午吃碗馄饨，老话叫“元宝汤”。",
				"初五“破五”，商铺开市，很多禁忌到这天就解除了。",
				"初六送穷，把积攒的垃圾清出去，图个清爽利落。",
				"大年初一，见到邻居道声新年好，一年都和气。",
				"初一的早饭吃点甜的，图个一年甜头。",
				"大年初一不说不吉利的话，图个口彩。",
				"初一的红包给得开心，收得也开心。",
				"大年初二回娘家，女儿女婿一起回去看看。",
				"初二的午饭要丰盛，娘家人盼了一年。",
				"大年初三不出门，在家歇一天。",
				"初三的“赤狗日”老说法，如今就当个休息日。",
				"大年初四接灶神，厨房收拾干净。",
				"初四的剩菜可以吃完了，别浪费。",
				"大年初五迎财神，商铺放鞭炮开市。",
				"初五吃饺子，捏住“小人嘴”。",
				"大年初六送穷，把垃圾清出去。",
				"初六之后，年就算过得差不多了。",
				"春节走亲戚，礼物不必贵，心意到就行。",
				"春节串门别空手，一盒点心也是礼。",
				"春节聚餐，长辈先动筷。",
				"春节喝酒别劝酒，量力而行。",
				"春节给孩子压岁钱，记得说句祝福。",
				"春节的糖果瓜子摆一盘，来客随手抓。",
				"春节贴福字，倒着贴取“福到”。",
				"春节的窗花贴在玻璃上，红红火火。",
				"春节的年画换新的，屋里亮堂。",
				"春节的灯笼挂起来，门口就有年味。",
				"春节放鞭炮遵守规定，安全第一。",
				"春节出门拜年，提前打个电话。",
				"春节路上车多，开车慢一点。",
				"春节的火车站人多，看好孩子。",
				"春节的机票贵，早点订。",
				"春节在家陪爸妈，比出门旅游实在。",
				"春节可以带爸妈去看场电影。",
				"春节的庙会热闹，注意保管财物。",
				"春节的舞龙舞狮，孩子最喜欢。",
				"春节的糖葫芦，酸甜开胃。",
				"春节的饺子，一家人一起包。",
				"春节的鱼要剩一点，年年有余。",
				"春节的年糕，步步高。",
				"春节的汤圆，团团圆圆。",
				"春节的春卷要现炸现吃，咬一口就是春天的味道。",
				"春节的腊味，蒸一盘就香。",
				"春节的坚果备一点，来客好招待。",
				"春节的茶要泡热的，冬天暖手。",
				"春节把家里的旧对联撕干净再贴新的。",
				"春节的扫除要提前做完，初一不动扫帚。",
				"春节的垃圾初一先存着，初二再倒。",
				"春节的碗筷多备几副，来客不慌。",
				"春节的剩菜要热透再吃。",
				"春节的天气冷，出门穿厚点。",
				"春节的暖气房里干，多喝水。",
				"春节的作息别太乱，节后好调整。",
				"春节的电视节目多，挑喜欢的看。",
				"春节的棋牌局，图个乐，别赌钱。",
				"春节的红包可以包成书，送孩子一套好书。",
				"春节给老师发条祝福，别忘了师恩。",
				"春节给同事发条祝福，来年好共事。",
				"春节给老朋友打个电话，感情要维护。",
				"春节的祝福不用复制粘贴，自己写两句更真诚。",
				"春节快乐！愿你的家人，都平平安安。",
				"春节快乐！愿你的身体，越来越结实。",
				"春节快乐！愿你的日子，越过越红火。",
				"春节快乐！愿你去年的辛苦，今年有回报。",
				"春节快乐！愿你的努力，都有回响。",
				"春节快乐！愿你的心愿，都能实现。",
				"春节快乐！愿你的付出，都被看见。",
				"春节快乐！愿你的生活，有滋有味。",
				"春节快乐！愿你的日子，稳稳当当。",
				"春节快乐！愿你的家人，都健健康康。",
				"春节快乐！愿你的心情，像春天一样暖。",
				"春节快乐！愿你的路，越走越宽。",
				"春节快乐！愿你的烦恼，都被风吹散。",
				"春节快乐！愿你的钱包，鼓鼓囊囊。",
				"春节快乐！愿你的睡眠，踏踏实实。",
				"春节快乐！愿你的工作，顺顺利利。",
				"春节快乐！愿你的学业，步步高升。",
				"春节快乐！愿你的感情，甜甜蜜蜜。",
				"春节快乐！愿你的朋友，都是真心。",
				"春节快乐！愿你的家人，常伴左右。",
				"春节快乐！愿你的每一天，都有小确幸。",
				"春节快乐！愿你的每一步，都有收获。",
				"春节快乐！愿你的每一个决定，都不后悔。",
				"春节快乐！愿你的每一顿饭，都吃得香。",
				"春节快乐！愿你的每一个梦，都能实现。",
				"春节快乐！愿你的每一份善意，都有回音。",
				"春节快乐！愿你的每一次出发，都顺利。",
				"春节快乐！愿你的每一次坚持，都有意义。",
				"春节快乐！愿你的每一次努力，都不白费。",
				"春节快乐！愿你的每一天，都被温柔以待。",
				"春节快乐！愿你的家人，都笑口常开。",
				"春节快乐！愿你的日子，越过越有奔头。",
				"春节快乐！愿你的生活，热气腾腾。",
				"春节快乐！愿你的新年，万事顺遂。",
				"春节快乐！愿你的新岁，胜过往年。",
				"春节快乐！愿你的心，永远年轻。",
				"春节快乐！愿你的家，永远温暖。",
				"春节的拜年，先长辈后平辈，顺序别乱。",
				"春节的红包别当面拆，是老礼。",
				"春节的饭桌上，鱼头对着长辈。",
				"春节的饺子煮破了，说“挣了”。",
				"春节的碗打碎了，说“岁岁平安”。",
				"春节的春联上下联别贴反，看尾字平仄。",
				"春节的门神贴在外侧，脸对脸。",
				"春节的福字大门正贴，柜子倒贴。",
				"春节的窗花贴完，屋里立刻有了年味。",
				"春节的灯笼挂一对，才对称。",
				"春节的鞭炮屑别急着扫，图个红火。",
				"春节的香烛点完，记得熄灭。",
				"春节的供品摆完，一家人分着吃。",
				"春节的祖坟前，去上炷香。",
				"春节的家谱可以翻出来，给孩子讲讲。",
				"春节的老照片，一年翻一次。",
				"春节的旧衣服，可以捐出去。",
				"春节的冰箱别塞太满，留点空间。",
				"春节的剩饭可以做成炒饭。",
				"春节的饺子馅，白菜要挤干水。",
				"春节的鱼，清蒸最鲜。",
				"春节的鸡，白切最嫩。",
				"春节的腊肉，蒸之前先泡。",
				"春节的年糕，煎着吃香。",
				"春节的汤圆，煮到浮起来。",
				"春节的春卷，油温别太高。",
				"春节的八宝饭，甜糯。",
				"春节的糖果，别让孩子吃太多。",
				"春节的坚果，注意别卡着孩子。",
				"春节的热茶，待客最合适。",
				"春节的水果，摆一盘橙子，图个吉利。",
				"春节的橘子，寓意大吉。",
				"春节的苹果，寓意平安。",
				"春节的甘蔗，寓意节节高。",
				"春节的年夜饭，荤素搭配。",
				"春节的饺子，蘸醋配蒜。",
				"春节的饭桌，给老人留主位。",
				"春节的碗筷，先给长辈。",
				"春节的饭菜，别做太多。",
				"春节的家宴，凉菜先上。",
				"春节的汤要最后上桌，热乎乎地喝一碗，胃里暖暖的。",
				"春节的甜点，饭后吃。",
				"春节的茶，饭后半小时再喝。",
				"春节的客人走时，送到门口。",
				"春节的礼物，双数吉利。",
				"春节的红包，新钞最好。",
				"春节的压岁钱，睡前放枕下。",
				"春节的拜年话，说“新年好”就够。",
				"春节的祝福短信，别群发。",
				"春节的视频通话，多陪老人聊会儿。",
				"春节的假期，别全用来应酬。",
				"春节的旅行，避开热门景点。",
				"春节的车票，提前抢。",
				"春节的高速，错峰出行。",
				"春节的景区，早点到。",
				"春节的酒店，提前订。",
				"春节的行李，别带太多。",
				"春节的天气，多看一眼预报。",
				"春节的雨雪天，路上慢点。",
				"春节的冰面，别上去玩。",
				"春节的烟花，别对着人放。",
				"春节的孔明灯，很多地方禁放。",
				"春节的山林，别带火种。",
				"春节的取暖器，别靠窗帘。",
				"春节的电热毯，睡前关掉。",
				"春节的煤气，用完关阀。",
				"春节的门窗，出门关好。",
				"春节的宠物，别喂年货。",
				"春节的巧克力，别给狗吃。",
				"春节的葡萄，别给猫狗。",
				"春节的葱蒜，别给猫狗。",
				"春节的花，百合对猫有毒。",
				"春节的水仙，别让宠物啃。",
				"春节的年宵花，选好养的。",
				"春节的绿植，浇水别太勤。",
				"春节的对联，贴前擦干净门。",
				"春节的灯笼，别挂太高。",
				"春节的彩灯，注意用电安全。",
				"春节的插座，别超负荷。",
				"春节的充电器，不用就拔。",
				"春节的手机，别玩太久。",
				"春节的眼睛，也要休息。",
				"春节的作息，尽量规律。",
				"春节的锻炼也别停，饭后散散步，比一直坐着舒服。",
				"春节的散步，饭后半小时。",
				"春节的聚会，注意通风。",
				"春节的感冒，别硬扛。",
				"春节的药，备一点常用药。",
				"春节的医院，急诊不放假。",
				"春节的安全，比热闹重要。",
				"春节的团圆，才是最珍贵的年货。",
				"春节的陪伴，比红包更暖。",
				"春节的团聚，是一年最踏实的时刻。",
			],
		},
		{
			name: "龙抬头", lunar: [2, 2], effect: "petal",
			blessings: [
				"二月二龙抬头，去理个发，图个一年精神头。",
				"今天是龙抬头，有些地方要吃春饼、炒豆子，热热闹闹讨个彩头。",
				"龙抬头到了，春天真正开始了，可以慢慢减衣服，但别一下减太多。",
				"二月二，愿你抬起头，往前走，好运跟着来。",
				"二月二这天理发叫“剃龙头”，图一年精神。",
				"龙抬头要吃春饼、猪头肉，有些地方还炒黄豆。",
				"二月二之后虫子多了，家里角落该打扫一遍。",
				"二月二这天，理发店最忙，最好提前预约。",
				"龙抬头快乐！愿今年的你，抬头见喜。",
				"龙抬头的春饼要薄，卷上豆芽和肉丝。",
				"二月二的炒豆子，嘎嘣脆，孩子爱吃。",
				"龙抬头前后气温回升，可以慢慢减衣。",
				"龙抬头快乐！愿你的努力，都有回响。",
				"二月二的蝎子、蜈蚣都出来了，家里角落要清扫。",
				"龙抬头的猪头肉，是很多地方的老讲究。",
				"龙抬头快乐！愿你的家人，都健健康康。",
				"二月二这天，把家里的被子拿出去晒。",
				"龙抬头的理发，叫“剃龙头”，图个精神。",
				"龙抬头快乐！愿你的日子，越过越顺。",
				"二月二的饺子，叫“龙耳”，吃着应景。",
				"龙抬头的面条，叫“龙须”，长长顺顺。",
				"龙抬头快乐！愿你的心愿，都能实现。",
				"二月二的春耕快开始了，农人开始忙。",
				"龙抬头前后桃花开了，可以去看。",
				"龙抬头快乐！愿你的身体，越来越结实。",
				"二月二的剪指甲，老话说正月别剪，这天剪正好。",
				"龙抬头的爆米花，叫“金豆开花”。",
				"龙抬头快乐！愿你的付出，都被看见。",
				"二月二这天，给孩子理个发，精神一学期。",
				"龙抬头的前后雨水多，出门带伞。",
				"龙抬头快乐！愿你的生活，有滋有味。",
				"二月二的韭菜最嫩，包饺子正好。",
				"龙抬头前后适合踏青，草都绿了。",
				"龙抬头快乐！愿你的家人，都平安喜乐。",
				"二月二的扫房，把冬天积的灰清一清。",
				"龙抬头这天，给家里的老人理理发。",
				"龙抬头快乐！愿你去年的辛苦，今年有回报。",
				"二月二的荠菜，可以挖回来包馄饨。",
				"龙抬头前后天气多变，注意添减衣物。",
				"龙抬头快乐！愿你的努力，都有收成。",
				"二月二这天，把门窗的合页上点油。",
				"龙抬头的传说，是龙王抬头布雨，万物复苏。",
				"龙抬头快乐！愿你的日子，稳稳当当。",
				"二月二的爆米花，自己在家也能做。",
				"龙抬头前后适合给车做个保养。",
				"龙抬头快乐！愿你今年的计划，都落地。",
				"二月二这天，把阳台的花浇透水。",
				"龙抬头的春饼，卷什么随你，图个咬春。",
				"龙抬头快乐！愿你的心情，像春天一样暖。",
				"二月二前后蛇虫出洞，草丛里当心。",
				"龙抬头这天，给孩子讲讲龙抬头的来历。",
				"龙抬头快乐！愿你的路，越走越宽。",
				"二月二的理发，避开人多的时间段。",
				"龙抬头前后适合晾晒冬天的厚衣。",
				"龙抬头快乐！愿你的睡眠，踏踏实实。",
				"二月二这天，早点回家，陪家人吃顿饭。",
				"龙抬头快乐！愿你的心眼，都亮堂。",
				"二月二的春饼，配碗小米粥，舒服。",
				"龙抬头快乐！愿你的每一步，都有收获。",
				"龙抬头快乐！愿今年抬头见喜，低头见财。",
			],
		},
		{
			name: "小年", lunarDays: { month: 12, days: [23, 24] }, effect: "confetti",
			blessings: [
				"小年到啦，祭灶、扫尘，把一年的灰尘都扫出去。",
				"今天是腊月二十三小年，南方不少地方是二十四，你那儿哪天过？",
				"小年快乐！糖瓜粘嘴，愿你来年说话都甜甜的。",
				"小年到了，年货可以慢慢备起来了，别等到最后几天挤。",
				"小年祭灶，供糖瓜是为了让灶王爷“上天言好事”。",
				"小年扫尘要扫房梁和床底，一年攒的灰都在那儿。",
				"小年之后开始蒸馒头、炸丸子，年味一天比一天浓。",
				"小年这天，北方吃糖瓜，南方吃年粽。",
				"小年快乐！愿你的日子，甜甜蜜蜜。",
				"小年的祭灶，要在灶前摆上糖和水。",
				"小年这天，把厨房彻底擦一遍。",
				"小年快乐！愿你的家人，都平平安安。",
				"小年的扫尘，从里往外扫，图个干净。",
				"小年前后开始炸丸子、蒸馒头。",
				"小年快乐！愿你去年的辛苦，今年有回报。",
				"小年这天，把窗帘拆下来洗洗。",
				"小年的糖瓜粘牙，吃一两个就够。",
				"小年快乐！愿你的努力，都有回响。",
				"小年前后菜市场最热闹，年货慢慢备。",
				"小年这天，给爸妈打电话说说到家的日子。",
				"小年快乐！愿你的心愿，都能实现。",
				"小年的灶糖，祭完还能吃。",
				"小年这天，把家里的旧报纸清掉。",
				"小年快乐！愿你的生活，有滋有味。",
				"小年的灶神像，贴上新的。",
				"小年前后适合把床单被套换新的。",
				"小年快乐！愿你的身体，越来越结实。",
				"小年这天，把家里的灯泡检查一遍。",
				"小年的糖瓜，孩子最喜欢。",
				"小年快乐！愿你的付出，都被看见。",
				"小年前后快递多，注意查收。",
				"小年这天，把冰箱里的东西清点一下。",
				"小年快乐！愿你的日子，稳稳当当。",
				"小年的年货，先买耐放的。",
				"小年前后路上车多，注意安全。",
				"小年快乐！愿你的家人，都健健康康。",
				"小年这天，把家里的垃圾清出去。",
				"小年的饺子，有些地方小年也吃。",
				"小年快乐！愿你的心情，像糖一样甜。",
				"小年前后适合把春联找出来。",
				"小年这天，给家里添点新碗筷。",
				"小年快乐！愿你的路，越走越宽。",
				"小年的祭灶，说几句好话，图个吉利。",
				"小年前后天冷，出门穿厚点。",
				"小年快乐！愿你的睡眠，踏踏实实。",
				"小年这天，把阳台的杂物收拾一下。",
				"小年的糖瓜，粘住灶王爷的嘴，让他多说好话。",
				"小年快乐！愿你的工作，顺顺利利。",
				"小年前后适合大扫除，一天一间屋。",
				"小年这天，把旧衣服整理出来。",
				"小年快乐！愿你的家人，都笑口常开。",
				"小年的馒头，蒸得白白胖胖。",
				"小年前后可以开始写春联了。",
				"小年快乐！愿你的心愿，都能成真。",
				"小年这天，把家里的年画挂上。",
				"小年快乐！愿你的日子，越过越红火。",
				"小年前后可以给家里换个新桌布。",
				"小年的糖瓜，别忘了给邻居送两块。",
				"小年快乐！愿你的家人，都平安喜乐。",
				"小年快乐！愿年味一天比一天浓。",
			],
		},
		{
			name: "国庆节", solar: [10, 1], effect: "confetti", days: 7, colors: ["#ff4d4f", "#ffd666", "#ffa940", "#f5222d"],
			blessings: [
				"国庆节快乐！假期出门人多，早点订票、早点出发。",
				"今天是国庆，祝愿祖国繁荣昌盛，也祝你假期过得舒心。",
				"国庆假期长，出去玩记得看好随身物品，别光顾着拍照。",
				"国庆快乐！高速免费车多，开车别急，安全第一。",
				"国庆节，景区人挤人，想去热门地方就早点到。",
				"今天是国庆，宅家也是一种过法，睡到自然醒也很幸福。",
				"国庆快乐！七天假别全用来补觉，留一天出去走走。",
				"国庆节，祝福祖国，也祝福你，日子越过越有奔头。",
				"国庆假期出门，提前看好返程票，别卡在最后一天。",
				"国庆景区排队难免，带点水和零食，别硬扛。",
				"国庆节高速免费，出发前检查胎压和油量。",
				"国庆在家也不错，把想看的剧和书补一补。",
				"国庆节的升旗仪式很庄重，有机会可以去看看。",
				"国庆这天，很多城市有升旗仪式，可以带孩子去看。",
				"国庆快乐！愿你的假期，过得舒心。",
				"国庆的景区门票，提前在线上买好。",
				"国庆出门带好身份证和充电宝。",
				"国庆快乐！愿你的家人，都平平安安。",
				"国庆的高速服务区人多，提前上厕所。",
				"国庆的自驾，出发前检查轮胎和刹车。",
				"国庆快乐！愿你的旅途，一路顺风。",
				"国庆的火车票，候补也是一种办法。",
				"国庆的飞机，提前两小时到机场。",
				"国庆快乐！愿你的行程，不太赶。",
				"国庆的酒店，看清楚是否可退。",
				"国庆的景区，避开中午的人流高峰。",
				"国庆快乐！愿你的照片，都拍得好看。",
				"国庆的古镇，早上人少，适合逛。",
				"国庆的海边，注意涨潮时间。",
				"国庆快乐！愿你的心情，像天气一样晴。",
				"国庆的山路，弯多，开慢点。",
				"国庆的露营地，提前预约。",
				"国庆的露营地，记得带驱蚊液。",
				"国庆的夜市，小吃多，注意卫生。",
				"国庆的博物馆，需要提前预约。",
				"国庆快乐！愿你的脚步，都不白走。",
				"国庆的公园，适合野餐。",
				"国庆的野餐，垃圾记得带走。",
				"国庆快乐！愿你的家人，都笑得开心。",
				"国庆的亲子游，行程别排太满。",
				"国庆的孩子，牵好手。",
				"国庆快乐！愿你的钱包，花得值。",
				"国庆的纪念品，别买太多。",
				"国庆的伴手礼，选轻便的。",
				"国庆快乐！愿你的朋友，都真诚。",
				"国庆的聚会，适量饮酒。",
				"国庆的烧烤，注意防火。",
				"国庆快乐！愿你的身体，扛得住折腾。",
				"国庆的天气，早晚凉，带件外套。",
				"国庆的雨具，随身带着。",
				"国庆快乐！愿你的心情，不被堵车影响。",
				"国庆的堵车，备点水和零食。",
				"国庆的导航，多备一条路线。",
				"国庆快乐！愿你的假期，有点收获。",
				"国庆的七天，留一天给自己。",
				"国庆的宅家，把想看的书看完。",
				"国庆快乐！愿你的日子，越过越有奔头。",
				"国庆的家里，把换季的衣服整理好。",
				"国庆的阳台，晒晒太阳。",
				"国庆快乐！愿你的努力，都被看见。",
				"国庆的清晨，街道很安静。",
				"国庆的傍晚，晚霞很好看。",
				"国庆的月亮，十五前后最圆。",
				"国庆快乐！愿你的心愿，都能实现。",
				"国庆的秋天，桂花香了。",
				"国庆的螃蟹，正当季。",
				"国庆的柿子红了，挑软一点的，甜得刚好。",
				"国庆快乐！愿你的生活，有滋有味。",
				"国庆的糖炒栗子，热乎的最好吃。",
				"国庆的烤红薯，暖手。",
				"国庆快乐！愿你的家人，都健健康康。",
				"国庆的饺子，一家人一起包。",
				"国庆的火锅，热气腾腾。",
				"国庆快乐！愿你的日子，稳稳当当。",
				"国庆的茶可以慢慢喝，不赶时间的时候，日子才像日子。",
				"国庆的棋局，输赢都别较真。",
				"国庆快乐！愿你的心情，一直放松。",
				"国庆的午睡，睡到自然醒。",
				"国庆的早市，菜新鲜。",
				"国庆快乐！愿你的胃口，一直好。",
				"国庆的书店，人不多，适合逛。",
				"国庆的电影，提前选好座位。",
				"国庆快乐！愿你的时间，都花在喜欢的事上。",
				"国庆的演出，提前查好时间。",
				"国庆的展览，慢慢看。",
				"国庆快乐！愿你的眼界，越来越宽。",
				"国庆的老街，适合慢慢走。",
				"国庆的小店，藏着好味道。",
				"国庆快乐！愿你的发现，都是惊喜。",
				"国庆的旧友，约一约。",
				"国庆的长辈，去看看。",
				"国庆快乐！愿你的陪伴，都不算晚。",
				"国庆的孩子，多陪一会儿。",
				"国庆的爱人，一起散散步。",
				"国庆快乐！愿你的感情，越来越好。",
				"国庆的自己，也别忘了照顾。",
				"国庆的夜晚，早点睡。",
				"国庆快乐！愿你的睡眠，踏踏实实。",
				"国庆的第二天，别熬夜。",
				"国庆的第五天，收收心。",
				"国庆快乐！愿你的节后，不太累。",
				"国庆的返程，错峰走。",
				"国庆的行李，别落下东西。",
				"国庆快乐！愿你的归途，一路平安。",
				"国庆的钥匙，出门检查。",
				"国庆的煤气，出门关好。",
				"国庆快乐！愿你的家，一直安稳。",
				"国庆的门窗，锁好再走。",
				"国庆的快递，让邻居帮忙收。",
				"国庆的花草，出门前浇透。",
				"国庆快乐！愿你的花，都开得好。",
				"国庆的宠物，安排好寄养。",
				"国庆的鱼缸，检查过滤。",
				"国庆快乐！愿你的小动物，都平安。",
				"国庆的冰箱，清空易坏的。",
				"国庆的剩菜，别留太久。",
				"国庆快乐！愿你的餐桌，常有热菜。",
				"国庆的碗筷，洗好收好。",
				"国庆的垃圾，出门前倒掉。",
				"国庆快乐！愿你的家，干干净净。",
				"国庆的被子，出门前晒好。",
				"国庆的衣服，按天气带。",
				"国庆快乐！愿你的行李，不多不少。",
				"国庆的鞋子，穿舒服的。",
				"国庆出门把伞放包里，秋天的雨说来就来。",
				"国庆快乐！愿你的路上，不淋雨。",
				"国庆的药，常用药带一点。",
				"国庆的创可贴，备几片。",
				"国庆快乐！愿你的旅途，无病无灾。",
				"国庆的口罩，人多的地方戴上。",
				"国庆的洗手，勤一点。",
				"国庆快乐！愿你的身体，棒棒的。",
				"国庆的水，随身带一瓶。",
				"国庆的零食，别带太多。",
				"国庆快乐！愿你的胃，不受委屈。",
				"国庆的相机，电池充好。",
				"国庆的内存卡，清一清。",
				"国庆快乐！愿你的照片，都存得下。",
				"国庆的耳机，别开太大声。",
				"国庆的眼睛，多看看风景。",
				"国庆快乐！愿你的视界，越来越清晰。",
				"国庆的脖子，别一直低头。",
				"国庆的腰，坐久了起来走走。",
				"国庆快乐！愿你的身体，没有酸痛。",
				"国庆的脚，走多了泡泡脚。",
				"国庆出门在外，手要勤洗，吃什么都安心。",
				"国庆快乐！愿你的每一天，都舒服。",
				"国庆的夜晚，数数星星。",
				"国庆的清晨，听听鸟叫。",
				"国庆快乐！愿你的耳朵，听见好声音。",
				"国庆的风，吹吹很舒服。",
				"国庆的云，看看很白。",
				"国庆快乐！愿你的抬头，都有好风景。",
				"国庆的雨，听听就好。",
				"国庆的雪，北方可能下了。",
				"国庆快乐！愿你的季节，刚刚好。",
				"国庆的黄昏，适合散步。",
				"国庆的清晨，适合跑步。",
				"国庆快乐！愿你的身体，越来越结实。",
				"国庆的饭后，走一走。",
				"国庆的睡前，放下手机。",
				"国庆快乐！愿你的睡眠，越来越香。",
				"国庆的早晨，喝杯温水。",
				"国庆的午后，眯一会儿。",
				"国庆快乐！愿你的精神，一直好。",
				"国庆的家人，聊聊天。",
				"国庆的朋友，叙叙旧。",
				"国庆快乐！愿你的关系，越来越近。",
				"国庆的邻居，打个招呼。",
				"国庆的同事，问声好。",
				"国庆快乐！愿你的周围，都是善意。",
				"国庆的陌生人，也帮一把。",
				"国庆的老人，扶一扶。",
				"国庆快乐！愿你的善意，都有回响。",
				"国庆的孩子，多夸夸。",
				"国庆的父母，多陪陪。",
				"国庆快乐！愿你的家人，都安心。",
				"国庆的自己，多抱抱。",
				"国庆的眼泪，允许流。",
				"国庆快乐！愿你的情绪，都被接纳。",
				"国庆的开心，记下来。",
				"国庆的遗憾，放下来。",
				"国庆快乐！愿你的心里，没有负担。",
				"国庆的计划，慢慢做。",
				"国庆的目标，一步步来。",
				"国庆快乐！愿你的努力，都有结果。",
				"国庆的今天，好好过。",
				"国庆的明天，慢慢来。",
				"国庆快乐！愿你的日子，一天比一天好。",
				"国庆的假期，好好休息。",
				"国庆的工作，节后再说。",
				"国庆快乐！愿你分得清轻重。",
				"国庆的祖国，越来越好。",
				"国庆的生活，越来越甜。",
				"国庆快乐！愿你的心愿，都成真。",
				"国庆的团圆，最珍贵。",
				"国庆的平安，最重要。",
				"国庆快乐！愿你和家人，都平安。",
				"国庆的七天，过得充实。",
				"国庆的假期，愿你睡得饱、吃得好。",
			],
		},
		{
			name: "劳动节", solar: [5, 1], effect: "confetti", days: 5,
			blessings: [
				"劳动节快乐！辛苦了这么久，今天该好好歇一歇。",
				"今天是五一，出门玩记得避峰，景区第一天最挤。",
				"劳动节到了，向每一个认真生活的人致敬。",
				"五一快乐！放假也别昼夜颠倒，作息乱了节后更累。",
				"劳动节，把手头的活放一放，陪家人吃顿饭吧。",
				"今天是五一，天气正好，去公园走走比刷手机强。",
				"五一假期五天，近处走走比长途奔波更省心。",
				"劳动节前后天气正好，晒被子、洗窗帘都合适。",
				"五一出门记得防晒，春天的太阳也不温柔。",
				"劳动节，给还在岗位上的人说声辛苦了。",
				"五一这天，把工作群静音，好好歇一天。",
				"劳动节快乐！愿你的付出，都有回报。",
				"五一的景区，第一天最挤，第二天好些。",
				"五一的机票，提前一个月订便宜。",
				"劳动节快乐！愿你的身体，越来越结实。",
				"五一的露营，注意防蚊虫。",
				"五一的野餐，食物要冷藏。",
				"劳动节快乐！愿你的家人，都平平安安。",
				"五一的天气，早晚还凉。",
				"五一的雨，来得快去得也快。",
				"劳动节快乐！愿你的心情，像春风一样轻。",
				"五一的公园，花开得正好。",
				"五一的湖边，风大，注意帽子。",
				"劳动节快乐！愿你的日子，清清爽爽。",
				"五一的古镇，人也不少。",
				"五一的自驾，避开热门线路。",
				"劳动节快乐！愿你的旅途，不堵车。",
				"五一的民宿，提前看评价。",
				"五一的农家乐，菜新鲜。",
				"劳动节快乐！愿你的口味，都被满足。",
				"五一的烧烤，生熟分开。",
				"五一的夜市，吃点热乎的。",
				"劳动节快乐！愿你的胃，舒舒服服。",
				"五一的折扣，别冲动消费。",
				"五一的快递，可能延迟。",
				"劳动节快乐！愿你的钱包，花得值。",
				"五一的书店，人少清净。",
				"五一的书，读两页也好。",
				"劳动节快乐！愿你的心，静得下来。",
				"五一的电影，挑部轻松的。",
				"五一的音乐，放点轻快的。",
				"劳动节快乐！愿你的耳朵，听到喜欢的歌。",
				"五一的花市，买束花回家。",
				"五一的绿植，换盆正合适。",
				"劳动节快乐！愿你的家，绿意盎然。",
				"五一的阳台，晒晒太阳。",
				"五一的被子，拿出去晒。",
				"劳动节快乐！愿你的睡眠，香香甜甜。",
				"五一的早饭，慢慢吃。",
				"五一的午饭，做点家常菜。",
				"劳动节快乐！愿你的餐桌，热气腾腾。",
				"五一的晚饭，少吃点。",
				"五一的散步，饭后半小时。",
				"劳动节快乐！愿你的身体，轻松自在。",
				"五一的家人，多聊聊。",
				"五一的朋友，约一约。",
				"劳动节快乐！愿你的关系，越来越近。",
				"五一的自己，也放个假。",
				"五一的心情，自己说了算。",
				"劳动节快乐！愿你的劳动，都被尊重。",
			],
		},
		{
			name: "情人节", solar: [2, 14], effect: "petal", days: 1,
			blessings: [
				"情人节快乐！有伴的好好过，单身的也要好好爱自己。",
				"今天是情人节，礼物不在于贵，心意到了就好。",
				"情人节到了，花店生意最好，别忘了提前订。",
				"情人节快乐！比起玫瑰，一句真心话更让人记很久。",
				"今天是情人节，愿你喜欢的人恰好也喜欢你。",
				"情人节，两个人一起做顿饭也很浪漫，不一定非得下馆子。",
				"情人节送花不如送对方真正想要的东西，先问问再说。",
				"情人节的餐厅要提前订，不然只能在门口排队。",
				"情人节快乐！一起看场电影、散散步，也是很好的过法。",
				"情人节，别拿礼物的价格衡量心意，量力而行最舒服。",
				"情人节这天，花店的花涨价，早点买。",
				"情人节快乐！愿你的爱，先给自己。",
				"情人节的餐厅，提前一周订。",
				"情人节的礼物，实用比花哨好。",
				"情人节快乐！愿你的感情，细水长流。",
				"情人节的巧克力，自己做的更有心意。",
				"情人节的电影，挑部两个人都喜欢的。",
				"情人节快乐！愿你和喜欢的人，有说不完的话。",
				"情人节的散步，比逛街舒服。",
				"情人节的夜景，慢慢看。",
				"情人节快乐！愿你的日子，有甜有暖。",
				"情人节的花，不必是玫瑰。",
				"情人节的卡片，手写的更动人。",
				"情人节快乐！愿你的心意，被好好收下。",
				"情人节的晚餐，在家做也浪漫。",
				"情人节的蜡烛，注意防火。",
				"情人节快乐！愿你的夜晚，温柔安静。",
				"情人节的红酒，适量就好。",
				"情人节的甜品，分着吃更甜。",
				"情人节快乐！愿你的甜蜜，不腻。",
				"情人节的话，真心最重要。",
				"情人节的拥抱，比礼物实在。",
				"情人节快乐！愿你的拥抱，不缺席。",
				"情人节的单身，也值得庆祝。",
				"情人节的自己，买件喜欢的衣服。",
				"情人节快乐！愿你的喜欢，都有回应。",
				"情人节的暗恋，说出口也好。",
				"情人节的勇气，值得表扬。",
				"情人节快乐！愿你的勇敢，不被辜负。",
				"情人节的距离，不是问题。",
				"情人节的电话，比消息暖。",
				"情人节快乐！愿你的想念，被听见。",
				"情人节的等待，也有意义。",
				"情人节的相遇，都算幸运。",
				"情人节快乐！愿你的相遇，都不迟。",
				"情人节的父母，也过个节。",
				"情人节的孩子，讲讲什么是爱。",
				"情人节快乐！愿你的家，充满爱。",
				"情人节的朋友，也可以送束花。",
				"情人节的同事，说句节日好。",
				"情人节快乐！愿你的周围，都有善意。",
				"情人节的天气，冷不冷都要穿暖。",
				"情人节的雨，带把伞。",
				"情人节快乐！愿你的路上，有人撑伞。",
				"情人节的夜晚，早点回家。",
				"情人节的月亮，陪着你。",
				"情人节快乐！愿你的心，不孤单。",
				"情人节的明天，照常过日子。",
				"情人节的平常，也是浪漫。",
				"情人节快乐！愿你的爱，长长久久。",
			],
		},
		{
			name: "万圣节", solar: [10, 31], effect: "leaf", colors: ["#ff9f43", "#a55eea", "#feca57", "#576574"],
			blessings: [
				"万圣节快乐！南瓜灯点起来，糖果记得给来敲门的小朋友留点。",
				"今天是万圣节，化装派对好玩，但别玩太晚，路上注意安全。",
				"万圣节到了，装扮可以吓人，玩笑别开过头就行。",
				"万圣节快乐！南瓜派烤起来，甜食虽好，别一次吃太多。",
				"今天是万圣节，带孩子要糖的话，记得看好人和车。",
				"万圣节的夜晚风凉，扮装再薄也要记得加件外套。",
				"万圣节的南瓜灯是把南瓜掏空刻出来的，里面放小灯就行。",
				"万圣节“不给糖就捣蛋”，带孩子要糖记得看好路口。",
				"万圣节化装别用劣质颜料，皮肤敏感的先试一小块。",
				"万圣节的装饰蜡烛别放在窗帘旁边，防火第一。",
				"万圣节的南瓜要挑圆一点的，好刻。",
				"万圣节快乐！愿你的夜晚，有点小刺激。",
				"万圣节的糖果，别给太小的孩子整颗。",
				"万圣节的装扮，注意别挡住视线。",
				"万圣节快乐！愿你的创意，都被夸。",
				"万圣节的派对，提前说好结束时间。",
				"万圣节的化妆，先在手腕试色。",
				"万圣节快乐！愿你的皮肤，不过敏。",
				"万圣节的南瓜灯，用电子蜡烛更安全。",
				"万圣节的门铃，晚上别按太晚。",
				"万圣节快乐！愿你的邻居，都友善。",
				"万圣节的糖，家长先检查一遍。",
				"万圣节的路线，走亮的地方。",
				"万圣节快乐！愿你的路上，不害怕。",
				"万圣节的衣服，加点反光条。",
				"万圣节的斗篷，别太长，容易绊倒。",
				"万圣节快乐！愿你的脚步，都稳当。",
				"万圣节的妆容，回家记得卸干净。",
				"万圣节的假发，注意防火。",
				"万圣节快乐！愿你的头发，都安好。",
				"万圣节的恐怖片，量力而行。",
				"万圣节的鬼屋，心脏不好的别进。",
				"万圣节快乐！愿你的心跳，都正常。",
				"万圣节的南瓜派，烤好趁热吃。",
				"万圣节的苹果，裹上糖浆。",
				"万圣节快乐！愿你的甜点，都好吃。",
				"万圣节的聚会，别喝太多。",
				"万圣节的代驾，提前约。",
				"万圣节快乐！愿你的回家路，平安。",
				"万圣节的宠物，别吓它。",
				"万圣节的猫，别涂颜料。",
				"万圣节快乐！愿你的小动物，都安心。",
				"万圣节的装饰，别挡消防通道。",
				"万圣节的蜡烛，远离窗帘。",
				"万圣节快乐！愿你的家，安全第一。",
				"万圣节的蜘蛛网，别缠到灯上。",
				"万圣节的骷髅，挂在稳的地方。",
				"万圣节快乐！愿你的布置，都牢固。",
				"万圣节的音乐，别开太大声。",
				"万圣节的邻居，有老人就小声点。",
				"万圣节快乐！愿你的热闹，不扰人。",
				"万圣节的糖，留几颗给自己。",
				"万圣节的南瓜籽，晒干能炒。",
				"万圣节快乐！愿你的南瓜，不浪费。",
				"万圣节的第二天，把装饰收好。",
				"万圣节的妆，别留到第二天。",
				"万圣节快乐！愿你的皮肤，好好休息。",
				"万圣节的照片，记得拍。",
				"万圣节的回忆，值得留。",
				"万圣节快乐！愿你的秋天，有趣有味。",
			],
		},
		{
			name: "感恩节", nthWeekday: { month: 11, weekday: 4, nth: 4 }, effect: "leaf",
			blessings: [
				"感恩节快乐！今天适合给帮过你的人发条消息，说声谢谢。",
				"今天是感恩节，火鸡吃不吃无所谓，感恩的心意要到位。",
				"感恩节到了，谢谢这一年里没有放弃的自己。",
				"感恩节快乐！记得给家里打个电话，他们也一直在惦记你。",
				"今天是感恩节，感谢那些在你难的时候伸过手的人。",
				"感恩节，一顿热饭、一句谢谢，就是最好的仪式感。",
				"感恩节的餐桌少不了火鸡、南瓜派和蔓越莓酱。",
				"感恩节第二天是“黑色星期五”，打折虽好，别冲动下单。",
				"感恩节，给这一年帮过你的人发条消息，不用很长。",
				"感恩节快乐！认真说一句谢谢，比转发祝福更有分量。",
				"感恩节的火鸡，烤之前要腌透。",
				"感恩节快乐！愿你的付出，都被记得。",
				"感恩节的南瓜派，配奶油好吃。",
				"感恩节的餐桌，摆上喜欢的餐具。",
				"感恩节快乐！愿你的家人，都围坐一桌。",
				"感恩节的蔓越莓酱，酸甜解腻。",
				"感恩节的土豆泥，加点黄油更香。",
				"感恩节快乐！愿你的胃口，一直好。",
				"感恩节的感谢，具体一点更动人。",
				"感恩节的短信，别群发。",
				"感恩节快乐！愿你的心意，被收到。",
				"感恩节的电话，打给爸妈。",
				"感恩节的拥抱，给身边的人。",
				"感恩节快乐！愿你的身边，都温暖。",
				"感恩节的老师，发条消息。",
				"感恩节的同事，说声谢谢。",
				"感恩节快乐！愿你的工作，都顺利。",
				"感恩节的朋友，约顿饭。",
				"感恩节的邻居，送点吃的。",
				"感恩节快乐！愿你的周围，都和气。",
				"感恩节的自己，也谢谢。",
				"感恩节的眼泪，也值得。",
				"感恩节快乐！愿你的情绪，被接纳。",
				"感恩节的遗憾，也是成长。",
				"感恩节的失败，教会你东西。",
				"感恩节快乐！愿你的路，越走越明白。",
				"感恩节的天气，冷了。",
				"感恩节的围巾，戴上。",
				"感恩节快乐！愿你的冬天，不冷。",
				"感恩节的壁炉，注意通风。",
				"感恩节的蜡烛，别离窗帘太近。",
				"感恩节快乐！愿你的家，暖烘烘。",
				"感恩节的黑色星期五，列清单再买。",
				"感恩节的特价，别冲动。",
				"感恩节快乐！愿你的钱包，花得值。",
				"感恩节的快递，耐心等。",
				"感恩节的退货，看清楚规则。",
				"感恩节快乐！愿你的购物，都顺心。",
				"感恩节的剩菜，做成三明治。",
				"感恩节的火鸡骨，熬汤。",
				"感恩节快乐！愿你的食物，不浪费。",
				"感恩节的散步，饭后走一走。",
				"感恩节的球赛，看看就好。",
				"感恩节快乐！愿你的休闲，都开心。",
				"感恩节的假期，好好休息。",
				"感恩节的家人，多陪陪。",
				"感恩节快乐！愿你的时间，花得值。",
				"感恩节的感谢，说出来。",
				"感恩节的心意，做出来。",
				"感恩节快乐！愿你的每一天，都值得感恩。",
			],
		},
		{
			name: "圣诞节", solar: [12, 25], effect: "snow",
			blessings: [
				"圣诞快乐！街上彩灯亮起来了，记得抬头看看。",
				"今天是平安夜，苹果记得吃，图个平平安安的好意头。",
				"圣诞节到了，礼物不在贵贱，拆开时的那声惊喜最珍贵。",
				"圣诞快乐！天冷，出门看灯会记得戴围巾。",
				"圣诞节，商场人多，带孩子的话一定牵好手。",
				"圣诞快乐！愿你的袜子里装的不是礼物，是一整年的好运。",
				"今天是圣诞，热红酒好喝，但含酒精，开车的人别碰。",
				"圣诞快乐！不管过不过这个节，开心最重要。",
				"圣诞节街上会有圣诞树和彩灯，晚上看更漂亮。",
				"圣诞节的姜饼人烤起来简单，和孩子一起做很有意思。",
				"圣诞袜挂在床头，第二天早上总能摸到点小惊喜。",
				"圣诞节聚会多，喝酒就别开车，代驾提前约。",
				"圣诞快乐！交换礼物重在心意，几十块的小东西也能很暖。",
				"圣诞节的圣诞树，挂上彩灯和小球。",
				"圣诞快乐！愿你的愿望，都被听见。",
				"圣诞节的礼物，包装纸选喜庆的。",
				"圣诞节的袜子，挂在床头。",
				"圣诞快乐！愿你的惊喜，都不迟到。",
				"圣诞节的姜饼屋，和孩子一起搭。",
				"圣诞节的颂歌，商场里最好听。",
				"圣诞快乐！愿你的耳朵，听到好歌。",
				"圣诞节的雪，南方少见。",
				"圣诞节的围巾，红绿配色最应景。",
				"圣诞快乐！愿你的冬天，暖融融。",
				"圣诞节的聚餐，热红酒别开车喝。",
				"圣诞节的蛋糕，切一块就好。",
				"圣诞快乐！愿你的甜点，都好吃。",
				"圣诞节的卡片，手写几句。",
				"圣诞节的祝福，别只发红包。",
				"圣诞快乐！愿你的心意，被收到。",
				"圣诞节的商场，人多，看好包。",
				"圣诞节的折扣，别冲动。",
				"圣诞快乐！愿你的钱包，花得值。",
				"圣诞节的电影，温馨的最适合。",
				"圣诞节的音乐，放一整天。",
				"圣诞快乐！愿你的心情，一直好。",
				"圣诞节的灯展，晚上看最美。",
				"圣诞节的拍照，穿亮色的衣服。",
				"圣诞快乐！愿你的照片，都好看。",
				"圣诞节的雪人，堆在家门口。",
				"圣诞节的雪仗，注意别打脸。",
				"圣诞快乐！愿你的冬天，有雪有笑。",
				"圣诞节的壁炉，烧得旺一点。",
				"圣诞节的毛衣，穿厚一点。",
				"圣诞快乐！愿你的身体，暖暖的。",
				"圣诞节的脚，泡个热水。",
				"圣诞节的手，涂点护手霜。",
				"圣诞快乐！愿你的皮肤，不干裂。",
				"圣诞节的早晨，慢慢醒来。",
				"圣诞节的早餐，做点热的。",
				"圣诞快乐！愿你的胃口，一直好。",
				"圣诞节的家人，一起看部电影。",
				"圣诞节的朋友，互送小礼物。",
				"圣诞快乐！愿你的关系，越来越近。",
				"圣诞节的邻居，说句节日好。",
				"圣诞节的同事，分点糖果。",
				"圣诞快乐！愿你的周围，都和气。",
				"圣诞节的自己，也要有礼物。",
				"圣诞节的夜晚，早点睡。",
				"圣诞快乐！愿你的梦里，有礼物。",
			],
		},
		{
			name: "美国独立日", solar: [7, 4], effect: "firework",
			blessings: [
				"今天是美国独立日，7 月 4 日，看烟花记得站在安全距离外。",
				"美国独立日到了，那边的朋友今天放假，祝他们节日快乐。",
				"7 月 4 日是美国国庆，烧烤和烟花是标配，热闹归热闹，注意防火。",
				"今天美国独立日，愿无论在哪的人，都能平安喜乐。",
				"美国独立日的烟花通常在晚上九点以后，提前找好观看位置。",
				"独立日烧烤要注意生熟分开，肉一定要烤透。",
				"美国独立日，很多地方有游行和社区野餐，气氛很热闹。",
				"美国独立日的烧烤，肉要烤透。",
				"美国独立日快乐！愿你的假期，热闹。",
				"独立日的烟花，站在安全距离外看。",
				"独立日的游行，早点去占位置。",
				"美国独立日快乐！愿你的家人，都平安。",
				"独立日的野餐，食物要冷藏。",
				"独立日的饮料，冰镇的。",
				"美国独立日快乐！愿你的胃口，一直好。",
				"独立日的国旗，挂在家门口。",
				"独立日的红白蓝，配色好看。",
				"美国独立日快乐！愿你的日子，多彩。",
				"独立日的社区活动，带孩子去。",
				"独立日的音乐，听听乡村乐。",
				"美国独立日快乐！愿你的耳朵，享受。",
				"独立日的湖边，人多，注意孩子。",
				"独立日的游泳，别去深水区。",
				"美国独立日快乐！愿你的夏天，安全。",
				"独立日的太阳，很晒，涂防晒。",
				"独立日的帽子，戴一顶。",
				"美国独立日快乐！愿你的皮肤，不晒伤。",
				"独立日的冰淇淋，吃一支。",
				"独立日的西瓜，切一盘。",
				"美国独立日快乐！愿你的夏天，甜甜的。",
				"独立日的热狗，配芥末。",
				"独立日的玉米，烤着吃。",
				"美国独立日快乐！愿你的食物，都香。",
				"独立日的蚂蚁，注意别爬食物。",
				"独立日的蚊虫，喷点驱蚊水。",
				"美国独立日快乐！愿你的夜晚，不被咬。",
				"独立日的停车场，早点去。",
				"独立日的交通，会堵。",
				"美国独立日快乐！愿你的路上，不堵。",
				"独立日的烟花声，宠物会怕。",
				"独立日的猫狗，关在屋里。",
				"美国独立日快乐！愿你的小动物，都安心。",
				"独立日的噪音，心脏不好的注意。",
				"独立日的老人，早点休息。",
				"美国独立日快乐！愿你的家人，都舒心。",
				"独立日的垃圾，带走。",
				"独立日的草地，别留痕迹。",
				"美国独立日快乐！愿你的环境，干干净净。",
				"独立日的烧烤架，用完熄火。",
				"独立日的火种，别留在草地。",
				"美国独立日快乐！愿你的假期，无火患。",
				"独立日的第二天，早点休息。",
				"独立日的照片，记得整理。",
				"美国独立日快乐！愿你的回忆，都美好。",
				"独立日的朋友，聚一聚。",
				"独立日的邻居，打个招呼。",
				"美国独立日快乐！愿你的周围，都友善。",
				"独立日的自由，值得珍惜。",
				"独立日的平安，最要紧。",
				"美国独立日快乐！愿无论在哪，都平安喜乐。",
			],
		},
	];

	let festivalCache = { key: "", list: [] };
	const ganzhiCache = {};   // 干支节日按年缓存，避免每次闲聊都重算

	function getLunarLib() {
		let lib = window.solarLunar;
		// 兼容两种 UMD 导出形态：{ solar2lunar, ... } 或 { default: { solar2lunar, ... } }
		if (lib && typeof lib.solar2lunar !== "function" && lib.default) lib = lib.default;
		return lib && typeof lib.solar2lunar === "function" ? lib : null;
	}

	// 节气日期：n 为节气序号（1 小寒、3 立春、12 夏至、15 立秋、24 冬至），返回当日 Date
	function termDate(lib, year, n) {
		const day = lib.getTerm(year, n);
		return day > 0 ? new Date(year, Math.ceil(n / 2) - 1, day) : null;
	}

	// 从 start 当天起，第 nth 个天干为 stem 的日子（春社/秋社用戊日，三伏用庚日）
	function nthStemDay(lib, start, stem, nth) {
		const date = new Date(start);
		for (let i = 0; i < 70; i++) {
			const info = lib.solar2lunar(date.getFullYear(), date.getMonth() + 1, date.getDate());
			if (info && typeof info.gzDay === "string" && info.gzDay.charAt(0) === stem) {
				if (--nth === 0) return date;
			}
			date.setDate(date.getDate() + 1);
		}
		return null;
	}

	function ganzhiFestivalDate(lib, year, f) {
		const cacheKey = `${year}-${f.name}`;
		if (cacheKey in ganzhiCache) return ganzhiCache[cacheKey];
		const start = termDate(lib, year, f.term);
		ganzhiCache[cacheKey] = start ? nthStemDay(lib, start, f.stem, f.nth) : null;
		return ganzhiCache[cacheKey];
	}

	// 某月第 n 个星期几（感恩节 = 11 月第 4 个星期四）
	function nthWeekdayDate(year, month, weekday, nth) {
		const first = new Date(year, month - 1, 1);
		return new Date(year, month - 1, 1 + (weekday - first.getDay() + 7) % 7 + (nth - 1) * 7);
	}

	// 节日持续天数：默认 3 天（当天 + 后两天），国庆 7 天，春节 初一到初九 9 天，
	// 除夕、七夕、情人节、重阳只过当天
	const FESTIVAL_DEFAULT_DAYS = 3;
	const addDays = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };

	// 节日可能的起始日：公历年与农历年错位、年末年初跨年都要覆盖，所以前后各看一年
	function festivalStartDates(f, year, lib) {
		const starts = [];
		if (f.solar) {
			starts.push(new Date(year, f.solar[0] - 1, f.solar[1]));
			starts.push(new Date(year - 1, f.solar[0] - 1, f.solar[1]));
			return starts;
		}
		if (f.range) {
			starts.push(new Date(year, f.range[0][0] - 1, f.range[0][1]));
			starts.push(new Date(year - 1, f.range[0][0] - 1, f.range[0][1]));
			return starts;
		}
		if (f.nthWeekday) {
			for (const yy of [year, year - 1]) starts.push(nthWeekdayDate(yy, f.nthWeekday.month, f.nthWeekday.weekday, f.nthWeekday.nth));
			return starts;
		}
		if (!lib) return starts;
		if (f.stem) {
			for (const yy of [year, year - 1]) {
				const date = ganzhiFestivalDate(lib, yy, f);
				if (date) starts.push(date);
			}
			return starts;
		}
		if (f.chuxi) {
			// 除夕 = 正月初一的前一天，大小月都能对上
			for (const ly of [year - 1, year, year + 1]) {
				const s = lib.lunar2solar(ly, 1, 1);
				if (s && s.cYear) starts.push(addDays(new Date(s.cYear, s.cMonth - 1, s.cDay), -1));
			}
			return starts;
		}
		if (f.lunar || f.lunarDays) {
			const month = f.lunar ? f.lunar[0] : f.lunarDays.month;
			const days = f.lunar ? [f.lunar[1]] : f.lunarDays.days;
			for (const ly of [year - 1, year, year + 1]) {
				for (const day of days) {
					const s = lib.lunar2solar(ly, month, day);
					if (s && s.cYear) starts.push(new Date(s.cYear, s.cMonth - 1, s.cDay));
				}
			}
		}
		return starts;
	}

	// 返回今天命中的所有节日（节日期间按持续天数命中，可能不止一个），结果按天缓存
	function getFestivalsToday() {
		const now = new Date();
		const y = now.getFullYear(), m = now.getMonth() + 1, d = now.getDate();
		const key = `${y}-${m}-${d}`;
		if (festivalCache.key === key) return festivalCache.list;
		const lib = getLunarLib();
		const lunarToday = lib ? lib.solar2lunar(y, m, d) : null;
		const lunarLabel = lunarToday && lunarToday.monthCn ? `农历${lunarToday.monthCn}${lunarToday.dayCn}` : "";
		const solarLabel = `${m}月${d}日`;
		const todayDate = new Date(y, m - 1, d);
		const list = [];
		const add = (f, label) => list.push({ name: f.name, effect: f.effect, effects: festivalEffects(f), colors: f.colors, blessings: f.blessings, dateLabel: label });

		for (const f of FESTIVALS) {
			const days = f.days || FESTIVAL_DEFAULT_DAYS;
			const hit = festivalStartDates(f, y, lib).some(start => todayDate >= start && todayDate <= addDays(start, days - 1));
			if (!hit) continue;
			const lunarFestival = !!(f.lunar || f.lunarDays || f.chuxi);
			add(f, lunarFestival && lunarLabel ? lunarLabel : solarLabel);
		}
		festivalCache = { key, list };
		return list;
	}

	// 随机取一句祝福：尽量避开上一句，保证一天里多次祝福不会连着重复
	let lastFestivalBlessing = "";
	function pickBlessing(f) {
		if (!f || !Array.isArray(f.blessings) || !f.blessings.length) return "";
		const pool = f.blessings.filter(b => b !== lastFestivalBlessing);
		const text = randomSelection(pool.length ? pool : f.blessings);
		lastFestivalBlessing = text;
		return text;
	}

	// ===== 节日特效池：每个节日在原有基础上再加 6 种，元旦/中秋加 10 种，春节/国庆加 20 种 =====
	// 每次出节日祝福时从这里随机挑 1 种，所以同一个节日也不会老是同一种效果。
	// "元素:配色" 表示换一套配色的同一元素，看起来是另一种特效。
	const EFFECT_POOLS = {
		元旦: ["confetti", "ribbon", "balloon", "firework", "sparkle", "star", "snow", "snowflake", "bubble", "heart",
			"confetti:red", "firecracker", "shootingStar", "sun", "snowman", "candy", "lanternString", "kite", "cloud", "gift"],
		人日: ["petal", "heart", "balloon", "bubble", "sparkle", "ribbon",
			"kite", "cloud", "sun", "shootingStar", "candy", "chrysanthemum"],
		元宵节: ["lantern", "skyLantern", "moonOrb", "star", "sparkle", "bubble", "firework", "confetti",
			"lanternString", "mooncake", "chrysanthemum", "shootingStar", "cloud", "candy"],
		春社: ["leaf", "petal", "sparkle", "bubble", "ribbon", "sunbeam",
			"kite", "cloud", "rain", "sun", "chrysanthemum", "shootingStar"],
		清明节: ["petal", "leaf", "snow", "ribbon", "bubble", "sunbeam",
			"rain", "cloud", "kite", "chrysanthemum", "sun", "shootingStar"],
		上巳节: ["petal", "bubble", "heart", "ribbon", "leaf", "sparkle",
			"kite", "cloud", "sun", "chrysanthemum", "shootingStar", "candy"],
		端午节: ["leaf", "flag", "sparkle", "bubble", "ribbon", "confetti",
			"zongzi", "rain", "sun", "cloud", "kite", "candy"],
		初伏: ["sunbeam", "ember", "spark", "bubble", "star", "sparkle",
			"sun", "rain", "cloud", "shootingStar", "kite", "candy"],
		中伏: ["sunbeam", "ember", "spark", "bubble", "star", "sparkle",
			"sun", "rain", "cloud", "shootingStar", "kite", "candy"],
		末伏: ["sunbeam", "ember", "spark", "bubble", "star", "sparkle",
			"sun", "rain", "cloud", "shootingStar", "kite", "candy"],
		七夕节: ["star", "sparkle", "heart", "petal", "skyLantern", "moonOrb", "bubble", "spark",
			"shootingStar", "cloud", "lanternString", "mooncake", "kite", "candy"],
		中元节: ["skyLantern", "lantern", "moonOrb", "bubble", "star", "spark",
			"lanternString", "cloud", "shootingStar", "mooncake", "rain", "chrysanthemum"],
		秋社: ["leaf", "maple", "sunbeam", "petal", "ribbon", "sparkle",
			"chrysanthemum", "kite", "cloud", "sun", "rain", "shootingStar"],
		中秋节: ["moonOrb", "skyLantern", "lantern", "star", "sparkle", "petal", "bubble", "confetti", "ribbon", "spark",
			"mooncake", "chrysanthemum", "cloud", "shootingStar", "lanternString", "kite", "sun", "rain", "star:gold", "petal:pink"],
		重阳节: ["leaf", "maple", "flag", "ribbon", "sunbeam", "sparkle",
			"chrysanthemum", "kite", "cloud", "sun", "rain", "shootingStar"],
		下元节: ["skyLantern", "lantern", "moonOrb", "bubble", "star", "spark",
			"lanternString", "cloud", "shootingStar", "mooncake", "rain", "sun"],
		冬至: ["snow", "snowflake", "sparkle", "star", "bubble", "ember",
			"snowman", "dumpling", "cloud", "sun", "candy", "shootingStar"],
		腊八节: ["snow", "snowflake", "ember", "spark", "star", "bubble",
			"snowman", "dumpling", "cloud", "sun", "candy", "shootingStar"],
		除夕: ["firework", "lantern", "skyLantern", "confetti", "ribbon", "sparkle", "star", "spark", "heart", "flag",
			"firecracker", "dumpling", "lanternString", "candy", "snowman", "shootingStar"],
		春节: ["confetti", "ribbon", "balloon", "firework", "lantern", "skyLantern", "heart", "flag",
			"sparkle", "star", "spark", "ember", "snow", "snowflake", "petal", "bubble", "gift", "bell",
			"sunbeam", "moonOrb",
			"firecracker", "dumpling", "lanternString", "candy", "snowman", "kite", "cloud", "shootingStar",
			"chrysanthemum", "sun", "confetti:red", "confetti:gold", "ribbon:red", "flag:red", "star:gold",
			"balloon:red", "bubble:blue", "heart:pink", "gift:gold", "lantern:warm",
			"redPacket", "riceCake", "tanghulu"],
		龙抬头: ["petal", "leaf", "ribbon", "sparkle", "bubble", "heart",
			"kite", "cloud", "sun", "rain", "chrysanthemum", "candy"],
		小年: ["confetti", "lantern", "firework", "heart", "ribbon", "sparkle",
			"firecracker", "candy", "dumpling", "snowman", "lanternString", "cloud"],
		国庆节: ["confetti", "ribbon", "balloon", "firework", "sparkle", "star", "flag", "heart", "spark",
			"sunbeam", "bubble", "snow", "leaf", "petal", "gift", "bell", "moonOrb", "ember", "skyLantern", "lantern",
			"firecracker", "lanternString", "kite", "cloud", "shootingStar", "sun", "candy", "rain",
			"chrysanthemum", "snowman", "confetti:red", "confetti:gold", "ribbon:red", "flag:red", "star:gold",
			"balloon:blue", "bubble:blue", "heart:pink", "firework:gold", "lantern:warm",
			"airplane", "suitcase", "zzz"],
		劳动节: ["confetti", "balloon", "ribbon", "bubble", "sparkle", "sunbeam",
			"kite", "cloud", "sun", "shootingStar", "candy", "rain"],
		情人节: ["heart", "petal", "ribbon", "bubble", "sparkle", "balloon",
			"candy", "cloud", "sun", "shootingStar", "kite", "chrysanthemum"],
		万圣节: ["pumpkin", "spark", "star", "leaf", "bubble", "sparkle",
			"jack", "candy", "cloud", "rain", "shootingStar", "kite", "ghost"],
		感恩节: ["leaf", "maple", "sunbeam", "sparkle", "ribbon", "heart",
			"chrysanthemum", "kite", "cloud", "sun", "rain", "shootingStar"],
		圣诞节: ["snow", "snowflake", "gift", "bell", "star", "sparkle", "ribbon", "bubble",
			"snowman", "candy", "cloud", "shootingStar", "sun", "rain"],
		美国独立日: ["firework", "spark", "flag", "confetti", "star", "sparkle",
			"firecracker", "sun", "cloud", "kite", "candy", "shootingStar"],
	};
	function festivalEffects(f) {
		const pool = f && EFFECT_POOLS[f.name];
		if (Array.isArray(pool) && pool.length) return pool;
		return (f && f.effect) ? [f.effect] : [];
	}

	// ===== 全屏特效基础：配色、变体与绘制元素 =====
	// 每种节日配不同元素：彩纸/彩带/圆环、花瓣、灯笼、落叶、雪花、星光、暖光、烟花等。
	const FX_PALETTE = {
		confetti: ["#ff6b6b", "#ffd93d", "#6bcb77", "#4d96ff", "#c780e8"],
		ribbon: ["#ff6b6b", "#ffd93d", "#6bcb77", "#4d96ff", "#c780e8"],
		balloon: ["#ff6b6b", "#ffd93d", "#4d96ff", "#6bcb77", "#c780e8"],
		petal: ["#ffb7c5", "#ffd1dc", "#f7a1b5", "#fff0f3"],
		heart: ["#ff8fab", "#ff5c8a", "#ffb3c1", "#f72585"],
		lantern: ["#ffb347", "#ff8c42", "#ffd166", "#ff7043"],
		skyLantern: ["#ffb347", "#ffca7a", "#ffd166", "#ffe8a3"],
		moonOrb: ["#fff3bf", "#ffe8a3", "#ffd43b"],
		leaf: ["#e8a33d", "#d98324", "#b5651d", "#c96f2f"],
		maple: ["#e8590c", "#f08c00", "#c92a2a", "#d9480f"],
		snow: ["#ffffff", "#eaf4ff", "#d8ecff"],
		snowflake: ["#ffffff", "#eaf4ff", "#d8ecff"],
		star: ["#ffe066", "#fff3bf", "#ffd43b", "#a5d8ff"],
		sparkle: ["#fff3bf", "#ffe066", "#ffffff", "#a5d8ff"],
		spark: ["#ffd166", "#ff9f43", "#fff3bf"],
		ember: ["#ff9f43", "#ffc078", "#ff6b35"],
		firework: ["#ff6b6b", "#ffd93d", "#6bcb77", "#4d96ff", "#c780e8", "#ffffff"],
		bubble: ["#d0ebff", "#e7f5ff", "#a5d8ff"],
		sunbeam: ["#ffe066", "#ffd43b", "#fff3bf"],
		flag: ["#ff4d4f", "#ffd666", "#4d96ff", "#ffffff"],
		gift: ["#ff6b6b", "#ffd93d", "#6bcb77", "#4d96ff"],
		bell: ["#ffd43b", "#ffe066", "#f59f00"],
		pumpkin: ["#ff922b", "#f76707", "#ffa94d"],
		snowman: ["#ffffff", "#eaf4ff", "#cfe8ff"],
		firecracker: ["#ff4d4f", "#ffd666", "#ffa940"],
		lanternString: ["#ffb347", "#ffd166", "#ffe8a3"],
		dumpling: ["#fff3e0", "#ffe8cc", "#ffd8a8"],
		mooncake: ["#e8b04b", "#d99a35", "#f0c76b"],
		zongzi: ["#4caf50", "#69db7c", "#a5d6a7"],
		jack: ["#ff922b", "#f76707", "#ffa94d"],
		kite: ["#ff6b6b", "#ffd93d", "#4d96ff", "#c780e8"],
		chrysanthemum: ["#ffd43b", "#ffe066", "#f59f00", "#ff922b"],
		shootingStar: ["#fff3bf", "#ffe066", "#ffffff"],
		sun: ["#ffd43b", "#ffe066", "#ffa940"],
		rain: ["#a5d8ff", "#d0ebff", "#74c0fc"],
		cloud: ["#ffffff", "#eaf4ff", "#dbeafe"],
		candy: ["#ff6b6b", "#ffd93d", "#6bcb77", "#c780e8"],
		ghost: ["#f8f9fa", "#e9ecef", "#dee2e6"],
		redPacket: ["#ff4d4f", "#ffd666", "#f5222d"],
		riceCake: ["#fff8e1", "#fff3e0", "#ffe8cc"],
		tanghulu: ["#e03131", "#f03e3e", "#ff6b6b"],
		airplane: ["#74c0fc", "#a5d8ff", "#4dabf7", "#ffffff"],
		suitcase: ["#ffa94d", "#ff922b", "#f76707"],
		zzz: ["#b197fc", "#d0bfff", "#9775fa"],
	};
	// 同一元素换个配色也算一种特效，用来给节日凑足更多花样（名字写成 "元素:配色"）
	const FX_VARIANT_PALETTES = {
		red: ["#ff4d4f", "#ffd666", "#ffa940", "#f5222d"],
		gold: ["#ffd43b", "#ffe066", "#f59f00", "#ffa940"],
		pink: ["#ff8fab", "#ffc2d1", "#ffb3c1", "#f7a1b5"],
		blue: ["#74c0fc", "#a5d8ff", "#4dabf7", "#d0ebff"],
		green: ["#69db7c", "#8ce99a", "#40c057", "#a5d6a7"],
		purple: ["#b197fc", "#d0bfff", "#9775fa", "#e5dbff"],
		warm: ["#ffb347", "#ffd166", "#ff8c42", "#ffe8a3"],
		white: ["#ffffff", "#eaf4ff", "#d8ecff"],
	};
	// 速度 / 尺寸 / 密度三档参数，和元素、配色一起组合出大量不同观感的特效
	const FX_SPEEDS = { xslow: 0.3, slow: 0.55, normal: 1, fast: 1.7, xfast: 2.4 };
	const FX_SIZES = { small: 0.7, normal: 1, large: 1.45 };
	const FX_DENSITY = { sparse: 0.5, normal: 1, dense: 1.5, xdense: 2.2 };
	// ===== 900 个图形家族 → 7032 种基础元素（家族 × 参数档 × 6 种描边风格） =====
	// 前 20 个是手绘基础家族（保持原有顺序与参数档，g1~g1000 编号不变，老配置不受影响）；
	// 后 880 个是程序化曲线家族（带 curve 字段，由 drawCurveFamily 烘焙成 Path2D 绘制）。
	const FX_LEGACY_FAMILIES = [
		{ key: "poly", tag: "star", from: 3, to: 22 },
		{ key: "star", tag: "star", from: 3, to: 22 },
		{ key: "flower", tag: "petal", from: 3, to: 22 },
		{ key: "spark", tag: "sparkle", from: 3, to: 14 },
		{ key: "ring", tag: "bubble", from: 1, to: 12 },
		{ key: "dots", tag: "bubble", from: 1, to: 12 },
		{ key: "wave", tag: "rain", from: 1, to: 10 },
		{ key: "arc", tag: "rain", from: 1, to: 10 },
		{ key: "gear", tag: "star", from: 6, to: 15 },
		{ key: "burst", tag: "sparkle", from: 4, to: 15 },
		{ key: "diamond", tag: "star", from: 1, to: 6 },
		{ key: "cross", tag: "star", from: 2, to: 7 },
		{ key: "chevron", tag: "flag", from: 1, to: 6 },
		{ key: "crescent", tag: "moonOrb", from: 1, to: 6 },
		{ key: "leaf", tag: "leaf", from: 1, to: 6 },
		{ key: "heart", tag: "heart", from: 1, to: 3 },
		{ key: "ribbon", tag: "ribbon", from: 1, to: 3 },
		{ key: "bubble", tag: "bubble", from: 1, to: 3 },
		{ key: "square", tag: "confetti", from: 1, to: 3 },
		{ key: "hex", tag: "snowflake", from: 1, to: 3 },
	];
	// —— 880 个新图形家族：经典参数曲线 + 学者/纪念日主题图形 ——
	// 说明：本环境联网检索工具不可用，曲线选型采用数学界与粒子特效领域的成熟通用方案：
	// Gielis 超级公式、玫瑰线 r=cos(kθ)、星形多边形 {p/q}、内/外摆线（万花尺）、利萨茹曲线、
	// Maurer 玫瑰星网、蝴蝶曲线（Fay）、卡西尼卵形线、伯努利双纽线、纽结投影、
	// 阿基米德/对数/费马螺线、黄金角向日葵种子盘（均见 Wolfram MathWorld 等通用数学资料）；
	// 主题图形则呼应"有来历的日子"：闪电（特斯拉）、DNA 双螺旋、苯环与分子（化学家）、
	// 原子轨道（物理学家）、拱桥（茅以升）、三棱镜与苹果（牛顿）、函数曲线/算盘/像素点阵/
	// 电路走线（数学家与计算机先驱）、星座与星系（天文学）、蝴蝶曲线/细胞/嫩芽（生物学家）、
	// 罗盘、蜂巢、雪晶、曼陀罗、风车等。
	// curve 字段：t=生成器；open=开放路径（实心风格退化为描边）；g=发光家族；
	// m=飘法（still 原地 / rise 上升 / fall 下落，缺省 fall）。
	const FX_EXTRA_FAMILIES = (() => {
		const list = [];
		// two=2 的家族有两档参数：第二档会在原图内再叠一层 55% 缩放 + 25° 旋转的副本
		const add = (key, tag, two, curve) => list.push({ key, tag, from: 1, to: two ? 2 : 1, curve });
		let i;

		// A. Gielis 超级公式（48 个）：m/n 参数组各不相同，圆的"万能推广"
		i = 0;
		for (const m of [2, 3, 4, 5, 6, 7, 8, 9, 10, 12]) {
			const sets = m === 2
				? [[0.5, 0.5, 0.5], [1, 1, 1], [2, 2, 2]]
				: [[0.4, 0.6, 0.6], [1, 1, 1], [2, 4, 4], [3, 8, 8], [6, 12, 12]];
			for (const [n1, n2, n3] of sets) { add(`sf${m}_${i}`, "star", i % 4 === 1, { t: "super", m, n1, n2, n3 }); i++; }
		}
		// B. 星形多边形 {p/q}（31 个）：绕圈一笔画星
		i = 0;
		for (let p = 5; p <= 14; p++)
			for (let q = 2; q <= (p - 1) / 2; q++) { add(`sp${p}_${q}`, "star", i % 4 === 0, { t: "star", p, q }); i++; }
		add("sp16_5", "star", false, { t: "star", p: 16, q: 5 });
		// C. 内摆线/万花尺（22 个）
		i = 0;
		for (const [R, r, d] of [[5, 1, 1], [5, 2, 1], [5, 2, 2], [5, 3, 1], [5, 3, 2], [5, 4, 2], [6, 1, 1], [6, 2, 1], [6, 2, 3], [6, 3, 2], [6, 4, 3], [6, 5, 2], [7, 1, 2], [7, 2, 1], [7, 2, 3], [7, 3, 2], [7, 4, 3], [7, 5, 2], [7, 6, 3], [8, 3, 4], [8, 5, 3], [4, 1, 2]]) {
			add(`hy${i}`, "star", i === 0 || i === 6 || i === 12 || i === 18, { t: "hypo", R, r, d }); i++;
		}
		// D. 玫瑰线 r=cos(pθ/q)（22 个）：整数 k 是 k 瓣花，分数 k 是编花环
		i = 0;
		for (const [p, q] of [[2, 1], [3, 1], [4, 1], [5, 1], [6, 1], [7, 1], [8, 1], [9, 1], [10, 1], [11, 1], [12, 1], [13, 1], [3, 2], [5, 2], [7, 2], [9, 2], [11, 2], [2, 3], [4, 3], [5, 3], [7, 3], [8, 3]]) {
			add(`rs${p}_${q}`, "petal", i === 2 || i === 8 || i === 14 || i === 20, { t: "rose", p, q }); i++;
		}
		// E. 利萨茹曲线（20 个）：示波器上的经典图形
		i = 0;
		for (const [a, b, ph] of [[1, 2, 0], [1, 2, Math.PI / 4], [1, 3, 0], [1, 3, Math.PI / 4], [2, 3, 0], [2, 3, Math.PI / 4], [3, 4, 0], [3, 4, Math.PI / 4], [3, 5, 0], [4, 5, 0], [2, 5, 0], [3, 2, Math.PI / 4], [1, 4, 0], [1, 5, 0], [2, 1, Math.PI / 4], [3, 1, 0], [4, 1, Math.PI / 4], [5, 2, 0], [5, 3, Math.PI / 4], [5, 4, 0]]) {
			add(`li${a}_${b}_${i}`, "petal", i % 5 === 0, { t: "liss", a, b, ph }); i++;
		}
		// F. 外摆线（11 个）：心形线、肾脏线、毛茛线一族
		i = 0;
		for (const [R, r, d] of [[1, 1, 1], [2, 1, 1], [2, 1, 2], [3, 1, 1], [3, 1, 2], [4, 1, 1], [5, 1, 1], [3, 2, 2], [2, 3, 1], [5, 2, 3], [4, 3, 2]]) {
			add(`ep${i}`, "heart", i === 0 || i === 5, { t: "epi", R, r, d }); i++;
		}
		// G. Maurer 玫瑰星网（14 个）
		i = 0;
		for (const [n, d] of [[2, 71], [2, 97], [3, 71], [3, 113], [4, 71], [4, 99], [5, 71], [5, 97], [6, 71], [6, 137], [7, 71], [7, 113], [8, 71], [9, 137]]) {
			add(`mr${n}_${d}`, "star", i === 0 || i === 7, { t: "maurer", n, d, open: 1 }); i++;
		}
		// H. 螺线家族（9 个）：阿基米德/对数/费马 + 菊石化石（达尔文的地质年代）
		add("sr_arch2", "wave", false, { t: "aspi", kind: "arch", turns: 2, open: 1 });
		add("sr_arch3", "wave", false, { t: "aspi", kind: "arch", turns: 3, open: 1 });
		add("sr_arch4", "wave", false, { t: "aspi", kind: "arch", turns: 4, open: 1 });
		add("sr_arch5", "wave", false, { t: "aspi", kind: "arch", turns: 5, open: 1 });
		add("sr_log22", "spiral", false, { t: "aspi", kind: "log", b: 0.22, open: 1 });
		add("sr_log35", "spiral", false, { t: "aspi", kind: "log", b: 0.35, open: 1 });
		add("sr_fermat", "wave", false, { t: "aspi", kind: "fermat", open: 1 });
		add("sr_ammon1", "spiral", false, { t: "aspi", kind: "ammon", open: 1 });
		add("sr_ammon2", "spiral", false, { t: "aspi", kind: "ammon", b: 0.3, open: 1 });
		// I. 波纹多边形（12 个）：圆形/多边形边界上叠一圈正弦波
		i = 0;
		for (const [base, bumps] of [[0, 5], [0, 6], [0, 7], [0, 8], [0, 9], [0, 10], [0, 11], [0, 12], [3, 3], [3, 4], [4, 3], [4, 4]]) {
			add(`wp${base}_${bumps}`, "wave", i === 0 || i === 6, { t: "wavepoly", base, bumps, amp: 0.22 }); i++;
		}
		// J. 向日葵种子盘（5 个）：黄金角逐点排布，斐波那契的既视感
		add("sflo60", "spiral", true, { t: "sunflo", count: 60 });
		add("sflo90", "spiral", false, { t: "sunflo", count: 90 });
		add("sflo140", "spiral", false, { t: "sunflo", count: 140 });
		add("sfloS80", "spiral", true, { t: "sunflo", count: 80, spiral: 1 });
		add("sfloS120", "spiral", false, { t: "sunflo", count: 120, spiral: 1 });
		// K. 闪电（6 个）：特斯拉 / 法拉第 / 爱迪生
		i = 0;
		for (let s = 1; s <= 6; s++) { add(`bolt${s}`, "bolt", i === 0, { t: "bolt", seed: s, forks: 2, open: 1, g: 1 }); i++; }
		// L. DNA 双螺旋（3 个）
		add("helix15", "helix", false, { t: "helix", twists: 1.5, open: 1, m: "still" });
		add("helix2", "helix", false, { t: "helix", twists: 2, open: 1, m: "still" });
		add("helix3", "helix", false, { t: "helix", twists: 3, open: 1, m: "still" });
		// M. 苯环与分子（7 个）：门捷列夫 / 居里夫人 / 拉瓦锡们的化学键
		add("bz1", "benzene", false, { t: "benzene", inner: 0.45, open: 1, m: "still" });
		add("bz2", "benzene", false, { t: "benzene", inner: 0.5, dots: 1, open: 1, m: "still" });
		add("bz3", "benzene", false, { t: "benzene", inner: 0.55, inner2: 1, open: 1, m: "still" });
		add("bz4", "benzene", false, { t: "benzene", inner: 0.3, dots: 1, open: 1, m: "still" });
		add("mol1", "benzene", false, { t: "mol", seed: 1, open: 1, m: "still" });
		add("mol2", "benzene", false, { t: "mol", seed: 2, open: 1, m: "still" });
		add("mol3", "benzene", false, { t: "mol", seed: 3, open: 1, m: "still" });
		// N. 原子（5 个）：卢瑟福椭圆轨道 / 玻尔圆轨道
		add("atomR1", "atom", true, { t: "atom", orbits: 2, open: 1, g: 1, m: "still" });
		add("atomR2", "atom", false, { t: "atom", orbits: 3, open: 1, g: 1, m: "still" });
		add("atomR3", "atom", true, { t: "atom", orbits: 4, open: 1, g: 1, m: "still" });
		add("atomB1", "atom", false, { t: "atom", kind: "bohr", n: 2, open: 1, g: 1, m: "still" });
		add("atomB2", "atom", false, { t: "atom", kind: "bohr", n: 4, open: 1, g: 1, m: "still" });
		// O. 电磁波包（4 个）：麦克斯韦
		i = 0;
		for (const [f, env] of [[3, 1.5], [5, 1.5], [7, 1.5], [5, 3]]) {
			add(`wpk${f}_${String(env).replace(".", "_")}`, "wave", false, { t: "wpacket", f, env, open: 1, g: 1, m: "still" }); i++;
		}
		// P. 星座（3 个）：牛顿 / 开普勒 / 玻尔们的天空
		for (const s of [2, 5, 9]) add(`con${s}`, "star", false, { t: "constel", seed: s, open: 1, g: 1, m: "still" });
		// Q. 像素点阵（5 个）：图灵机 / 巴贝奇分析机
		add("px1", "matrix", false, { t: "matrix", seed: 1, size: 4, m: "still" });
		add("px2", "matrix", false, { t: "matrix", seed: 2, size: 4, m: "still" });
		add("px3", "matrix", false, { t: "matrix", seed: 3, size: 4, m: "still" });
		add("px4", "matrix", false, { t: "matrix", seed: 4, size: 5, m: "still" });
		add("px5", "matrix", false, { t: "matrix", seed: 5, size: 5, m: "still" });
		// R. 蝴蝶曲线（2 个）：达尔文 / 生物多样性
		add("bfly1", "butterfly", false, { t: "butterfly" });
		add("bfly2", "butterfly", false, { t: "butterfly", wings: 1 });
		// S. 卡西尼卵形线（2 个）：从花生到双星
		add("cas55", "petal", false, { t: "cassini", a: 0.55 });
		add("cas80", "petal", false, { t: "cassini", a: 0.8 });
		// T. 伯努利双纽线（1 个）：无穷符号
		add("lemn1", "petal", false, { t: "lemn" });
		// U. 纽结投影（3 个）：三叶结 / 五瓣结
		add("kn1", "petal", false, { t: "knot", p: 1, q: 2 });
		add("kn2", "petal", false, { t: "knot", p: 1, q: 3 });
		add("kn3", "petal", false, { t: "knot", p: 2, q: 5 });
		// V. 泪滴与蛋形（2 个）
		add("tear1", "petal", false, { t: "tear", kind: "drop" });
		add("egg1", "petal", false, { t: "tear", kind: "egg" });
		// W. 钟面与齿轮（5 个）：巴贝奇 / 图灵的计算机器
		add("clk1", "clock", false, { t: "clock", open: 1, m: "still" });
		add("clk2", "clock", false, { t: "clock", ticks: 24, open: 1, m: "still" });
		add("cog1", "clock", false, { t: "clock", kind: "cog", teeth: 6, open: 1, m: "still" });
		add("cog2", "clock", false, { t: "clock", kind: "cog", teeth: 9, open: 1, m: "still" });
		add("cog3", "clock", false, { t: "clock", kind: "cog", teeth: 12, open: 1, m: "still" });
		// X. 拱桥（3 个）：茅以升
		add("arch1", "arch", false, { t: "arch", spans: 1, open: 1 });
		add("arch2", "arch", false, { t: "arch", spans: 2, open: 1 });
		add("arch3", "arch", false, { t: "arch", spans: 3, open: 1 });
		// Y. 电路走线（3 个）
		for (const s of [1, 2, 3]) add(`ckt${s}`, "circuit", false, { t: "circuit", seed: s, open: 1, m: "still" });
		// Z. 算盘（2 个）：华罗庚 / 吴文俊
		add("ab1", "abacus", false, { t: "abacus", rods: 2, open: 1, m: "still" });
		add("ab2", "abacus", false, { t: "abacus", rods: 3, open: 1, m: "still" });
		// AA. 函数曲线（5 个）：欧拉 / 高斯 / 黎曼们的小黑板
		add("pl1", "plot", false, { t: "plot", kind: "sine", open: 1, m: "still" });
		add("pl2", "plot", false, { t: "plot", kind: "gauss", open: 1, m: "still" });
		add("pl3", "plot", false, { t: "plot", kind: "parab", open: 1, m: "still" });
		add("pl4", "plot", false, { t: "plot", kind: "pend", open: 1, m: "still" });
		add("pl5", "plot", false, { t: "plot", kind: "cubic", open: 1, m: "still" });
		// AB. 三棱镜与色散（3 个）：牛顿的光学
		i = 0;
		for (const rays of [5, 6, 7]) { add(`prz${rays}`, "prism", i === 0, { t: "prism", rays, open: 1, g: 1, m: "still" }); i++; }
		// AC. 苹果（1 个）：砸中牛顿的那一颗
		add("apl1", "apple", false, { t: "apple" });
		// AD. 星系旋臂（3 个）
		i = 0;
		for (const arms of [2, 3, 4]) { add(`gx${arms}`, "galaxy", i === 0, { t: "galaxy", arms, open: 1, g: 1, m: "still" }); i++; }
		// AE. 罗盘玫瑰（1 个）
		add("cmp1", "star", false, { t: "compass", m: "still" });
		// AF. 蜂巢（1 个）
		add("hny1", "star", false, { t: "honey", m: "still" });
		// AG. 雪晶（5 个）：六向主干 + 分叉
		i = 0;
		for (const [arms, depth, hex] of [[6, 1, 0], [6, 2, 1], [6, 2, 0], [8, 1, 0], [12, 1, 1]]) {
			add(`dc${arms}_${depth}`, "snowflake", false, { t: "dend", arms, depth, hex, open: 1 }); i++;
		}
		// AH. 曼陀罗（4 个）：花瓣圈与圆点圈交替
		i = 0;
		for (const [rings, dots] of [[2, 0], [3, 0], [4, 0], [3, 1]]) { add(`md${rings}_${dots}`, "star", i === 0 || i === 2, { t: "mandala", rings, dots, m: "still" }); i++; }
		// AI. 风车（3 个）：弯叶片
		for (const b of [4, 6, 8]) add(`pw${b}`, "star", false, { t: "pin", blades: b, m: "still" });
		// AJ. 嫩芽（2 个）：袁隆平 / 世界森林日
		add("spr1", "sprout", false, { t: "sprout", kind: "single" });
		add("spr2", "sprout", false, { t: "sprout", kind: "double" });
		// AK. 细胞（2 个）：生物学家们的显微镜
		add("cel1", "cell", false, { t: "cell", seed: 1, m: "still" });
		add("cel2", "cell", false, { t: "cell", seed: 2, m: "still" });

		// ===== AL. 参数扩展族（+600）：把 20+280 扩到 20+880 = 900 个家族 =====
		// 复用上方 38 个曲线生成器，只增参数档，不新增绘制引擎；全部追加在末尾，
		// 因此前 300 个家族（含 g1~g1000）编号与顺序不变，老配置/本地缓存持续有效。
		// 每个 add = 1 个家族；two 参数家族另有第二档元素。
		let j;

		// AL-1. 超级公式（60 个）：m 3..17 × 4 组 n，花色/尖角密度各不同
		j = 0;
		for (const m of [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17])
			for (const [n1, n2, n3] of [[0.75, 1, 1], [0.5, 2, 2], [1, 4, 4], [0.3, 1, 1]])
				add(`sv${m}_${j}`, "star", j % 5 === 0, { t: "super", m, n1, n2, n3 }), j++;

		// AL-2. 星形多边形 {p/q}（64 个）：p 16..23，更"尖"的多角星
		j = 0;
		for (let p = 16; p <= 23; p++)
			for (let q = 2; q <= (p - 1) / 2; q++) add(`st${p}_${q}`, "star", j % 5 === 0, { t: "star", p, q }), j++;

		// AL-3. 玫瑰线（39 个）：p 14..26 × q 1..3，花瓣更密的花环
		j = 0;
		for (let p = 14; p <= 26; p++)
			for (const q of [1, 2, 3]) add(`rk${p}_${q}`, "petal", j % 6 === 0, { t: "rose", p, q }), j++;

		// AL-4. 利萨茹曲线（72 个）：a 2..13 × b{3,4,7} × 相位{0,π/4}
		j = 0;
		for (let a = 2; a <= 13; a++)
			for (const b of [3, 4, 7])
				for (const ph of [0, Math.PI / 4]) add(`le${a}_${b}_${j}`, "petal", j % 6 === 0, { t: "liss", a, b, ph }), j++;

		// AL-5. 内摆线/万花尺（40 个）：R 4..13 × 4 组 (r,d)
		j = 0;
		for (let R = 4; R <= 13; R++)
			for (const [r, d] of [[1, 1], [2, 1], [2, 2], [3, 2]]) add(`hn${R}_${j}`, "star", j % 6 === 0, { t: "hypo", R, r, d }), j++;

		// AL-6. 外摆线（30 个）：心形/肾脏线一族，R 2..16 × d 1..2
		j = 0;
		for (let R = 2; R <= 16; R++)
			for (const d of [1, 2]) add(`en${R}_${j}`, "heart", j % 6 === 0, { t: "epi", R, r: 1, d }), j++;

		// AL-7. Maurer 玫瑰星网（40 个）：n 2..9 × 5 个 d
		j = 0;
		for (let n = 2; n <= 9; n++)
			for (const d of [67, 83, 101, 127, 149]) add(`mn${n}_${d}`, "star", false, { t: "maurer", n, d, open: 1 }), j++;

		// AL-8. 波纹多边形（35 个）：base 0..6 × bumps 4..8
		j = 0;
		for (let base = 0; base <= 6; base++)
			for (let bumps = 4; bumps <= 8; bumps++) add(`wr${base}_${bumps}`, "wave", j % 6 === 0, { t: "wavepoly", base, bumps, amp: 0.2 }), j++;

		// AL-9. 螺线家族（16 个）：阿基米德/对数/费马 + 菊石
		j = 0;
		for (let turns = 2; turns <= 9; turns++) add(`sc${turns}`, "wave", false, { t: "aspi", kind: "arch", turns, open: 1 });
		for (const b of [0.15, 0.25, 0.4, 0.5]) add(`sg${String(b).replace(".", "")}`, "spiral", false, { t: "aspi", kind: "log", b, open: 1 });
		add("sf2", "wave", false, { t: "aspi", kind: "fermat", open: 1 });
		for (const b of [0.2, 0.4, 0.6]) add(`sa${String(b).replace(".", "")}`, "spiral", false, { t: "aspi", kind: "ammon", b, open: 1 });

		// AL-10. 纽结投影（24 个）：更多 (p,q) 组合的彩带结
		for (const [p, q] of [[1, 2], [1, 3], [1, 4], [1, 5], [2, 3], [2, 5], [2, 7], [3, 4], [3, 5], [3, 7], [3, 8], [4, 5], [4, 7], [4, 9], [5, 6], [5, 7], [5, 8], [5, 9], [6, 7], [6, 11], [7, 8], [7, 9], [7, 10], [8, 9]])
			add(`kb${p}_${q}`, "petal", false, { t: "knot", p, q });

		// AL-11. 泪滴/蛋形/水滴（12 个）
		for (const kind of ["drop", "drop", "drop", "egg", "egg", "egg", "drop", "egg", "drop", "egg", "drop", "egg"])
			add(`tk${j}`, "petal", false, { t: "tear", kind }), j++;

		// AL-12. 钟面与齿轮（18 个）：表盘刻度 + 更多齿数
		for (const teeth of [4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16])
			add(`cg${teeth}`, "clock", false, { t: "clock", kind: "cog", teeth, open: 1, m: "still" });
		for (const ticks of [4, 6, 12, 30, 48, 60])
			add(`cd${ticks}`, "clock", false, { t: "clock", ticks, open: 1, m: "still" });

		// AL-13. 雪晶（12 个）：更多臂数与分叉深度
		for (const [arms, depth, hex] of [[6, 3, 1], [8, 2, 1], [8, 3, 0], [10, 2, 1], [12, 2, 1], [12, 3, 0], [14, 1, 0], [16, 1, 1], [6, 1, 1], [8, 1, 1], [10, 1, 0], [12, 1, 0]])
			add(`dk${arms}_${depth}`, "snowflake", false, { t: "dend", arms, depth, hex, open: 1 });

		// AL-14. 曼陀罗（16 个）：rings 2..9 × dots{0,1}
		for (let rings = 2; rings <= 9; rings++)
			for (const dots of [0, 1]) add(`mb${rings}_${dots}`, "star", false, { t: "mandala", rings, dots, m: "still" });

		// AL-15. 补充混合（88 个）：玫瑰/向日葵/卡西尼/蝴蝶/星系/罗盘/风车/蜂巢 的更多档位
		j = 0;
		for (let p = 27; p <= 34; p++) for (const q of [1, 2, 3, 4, 5]) add(`rm${p}_${q}`, "petal", false, { t: "rose", p, q }), j++;                 // 40
		for (const c of [30, 45, 55, 70, 100, 130, 160]) add(`sm${c}`, "spiral", false, { t: "sunflo", count: c });                                     // 7
		for (const a of [0.5, 0.6, 0.65, 0.7, 0.75, 0.85, 0.9, 0.95]) add(`cx${String(a * 100 | 0)}`, "petal", false, { t: "cassini", a });                 // 8
		for (let s = 1; s <= 6; s++) add(`bf${s}`, "butterfly", false, { t: "butterfly", seed: s });                                                     // 6
		for (let arms = 5; arms <= 8; arms++) add(`ga${arms}`, "galaxy", false, { t: "galaxy", arms, open: 1, g: 1, m: "still" });                         // 4
		for (let s = 1; s <= 6; s++) add(`cm${s}`, "star", false, { t: "compass", seed: s, m: "still" });                                                  // 6
		for (const [blades, curve] of [[3, 0.4], [5, 0.4], [7, 0.5], [9, 0.5], [10, 0.6], [12, 0.6]])
			add(`pn${blades}`, "star", false, { t: "pin", blades, curve, m: "still" });                                                                     // 6
		for (const rings of [2, 3, 4, 5, 6]) add(`hb${rings}`, "star", false, { t: "honey", rings, m: "still" });                                          // 5
		// 6 个双纽线/泪珠/苹果混合彩蛋
		for (const [t, a] of [["lemn", 0], ["lemn", 0], ["apple", 0], ["apple", 0], ["cassini", 0.45], ["cassini", 0.7]])
			add(`mx${j}`, "petal", false, t === "apple" ? { t, } : { t, a }), j++;

		// AL-16. 补足到 +600（34 个）：玫瑰 24 + 超级公式 10
		for (let p = 35; p <= 40; p++) for (const q of [1, 2, 3, 4]) add(`rn${p}_${q}`, "petal", false, { t: "rose", p, q });   // 6×4 = 24
		for (const m of [18, 19]) for (const [n1, n2, n3] of [[0.6, 1, 1], [1, 3, 3], [0.4, 2, 2], [1, 5, 5], [2, 3, 3]])
			add(`sw${m}_${j}`, "star", false, { t: "super", m, n1, n2, n3 }), j++;                                             // 2×5 = 10

		return list;
	})();
	const FX_ELEMENT_FAMILIES = [...FX_LEGACY_FAMILIES, ...FX_EXTRA_FAMILIES];   // 20 + 880 = 900 家族
	const FX_ELEMENT_STYLES = ["fill", "outline", "double", "dashed", "dotted", "twoTone"];
	const FX_ELEMENTS = (() => {
		const list = [];
		for (const f of FX_ELEMENT_FAMILIES) {
			for (let p = f.from; p <= f.to; p++) {
				for (const style of FX_ELEMENT_STYLES) list.push({ family: f.key, tag: f.tag, param: p, style, curve: f.curve || null });
			}
		}
		return list;   // 1172 组（家族 × 参数档）× 6 风格 = 7032 种基础元素
	})();

	// 通用元素怎么飘：气泡/环/月牙往上，星/火花/齿轮原地，其余往下；
	// 880 个曲线家族自带 m 字段（still 原地 / rise 上升 / fall 下落，缺省 fall）
	function genericMotion(family, curve) {
		if (curve) return curve.m || "fall";
		if (family === "bubble" || family === "ring" || family === "crescent") return "rise";
		if (family === "star" || family === "spark" || family === "burst" || family === "gear") return "still";
		return "fall";
	}

	function resolveFx(name) {
		// 名字格式："元素[:配色][#速度,尺寸,密度]"，元素可以是 g1~g7032 或内置类型
		const [base, tag] = String(name || "").split("#");
		const [type, variant] = base.split(":");
		const [speedTag, sizeTag, densityTag] = (tag || "").split(",");
		const gm = /^g(\d+)$/.exec(type || "");
		const index = gm ? Math.max(1, Math.min(FX_ELEMENTS.length, parseInt(gm[1], 10) || 1)) - 1 : -1;
		// 尺寸 tag 支持两形态：小/中/大档位（small/normal/large），或 "n数字"（手动配置滑块的连续倍率，如 n1.5）
		const numSize = /^n([\d.]+)$/.exec(sizeTag || "");
		return {
			type: index >= 0 ? "generic" : type,
			element: index >= 0 ? FX_ELEMENTS[index] : null,
			colors: FX_VARIANT_PALETTES[variant] || null,
			speed: FX_SPEEDS[speedTag] || 1,
			sizeMul: numSize ? Math.min(3, Math.max(0.5, parseFloat(numSize[1]) || 1)) : (FX_SIZES[sizeTag] || 1),
			densityMul: FX_DENSITY[densityTag] || 1,
		};
	}

	// ===== 平日特效：元素 × 配色 × 速度 × 尺寸 × 密度，组合出 10000 种 =====
	// 平日特效开关（主题配置里可切换），节日特效不受此开关影响。
	const WEEKDAY_FX_KEY = "waifu-fx-weekday";
	function weekdayFxEnabled() {
		try { return localStorage.getItem(WEEKDAY_FX_KEY) !== "0"; } catch (e) { return true; }
	}
	const EVERYDAY_FX = (() => {
		const legacy = Object.keys(FX_PALETTE);
		const palettes = Object.keys(FX_VARIANT_PALETTES);
		const speeds = Object.keys(FX_SPEEDS);
		const sizes = Object.keys(FX_SIZES);
		const densities = Object.keys(FX_DENSITY);
		const out = new Set();
		let guard = 0;
		// 组合总量约 337 万（7032 元素 × 8 配色 × 5 速度 × 3 尺寸 × 4 密度），随机抽 10000 个不重复的组合即可
		while (out.size < 10000 && guard < 80000) {
			guard++;
			const useGeneric = Math.random() < 0.85;
			const type = useGeneric
				? `g${1 + Math.floor(Math.random() * FX_ELEMENTS.length)}`
				: legacy[Math.floor(Math.random() * legacy.length)];
			const p = palettes[Math.floor(Math.random() * palettes.length)];
			const sp = speeds[Math.floor(Math.random() * speeds.length)];
			const sz = sizes[Math.floor(Math.random() * sizes.length)];
			const de = densities[Math.floor(Math.random() * densities.length)];
			out.add(`${type}:${p}#${sp},${sz},${de}`);
		}
		return [...out];
	})();

	// 主题配置里手动指定的平日特效；未填的维度随机
	const WEEKDAY_CUSTOM_KEY = "waifu-fx-custom";
	function weekdayCustom() {
		try {
			const raw = localStorage.getItem(WEEKDAY_CUSTOM_KEY);
			if (!raw) return null;
			const cfg = JSON.parse(raw);
			return (cfg && cfg.enabled) ? cfg : null;
		} catch (e) { return null; }
	}
	function customFxName(cfg) {
		const palettes = Object.keys(FX_VARIANT_PALETTES);
		const speeds = Object.keys(FX_SPEEDS);
		const sizes = Object.keys(FX_SIZES);
		const densities = Object.keys(FX_DENSITY);
		const pick = (arr, v) => arr.includes(v) ? v : arr[Math.floor(Math.random() * arr.length)];
		const n = parseInt(cfg.element, 10);
		const el = (n >= 1 && n <= FX_ELEMENTS.length) ? n : 1 + Math.floor(Math.random() * FX_ELEMENTS.length);
		// 尺寸：滑块数值（cfg.sizeNum）优先，连续倍率编码成 "n数字" tag；勾了随机则用随机档位
		const sz = (cfg.sizeRandom || typeof cfg.sizeNum !== "number")
			? pick(sizes, cfg.size)
			: `n${cfg.sizeNum}`;
		return `g${el}:${pick(palettes, cfg.palette)}#${pick(speeds, cfg.speed)},${sz},${pick(densities, cfg.density)}`;
	}

	// 平日里的"有来历的一天"：科学家诞辰、世界日等，只影响当天特效的偏好元素
	const EVERYDAY_THEMES = {
		"01-04": { name: "牛顿诞辰", types: ["star", "sparkle", "shootingStar", "moonOrb", "cloud", "sun", "prism", "apple", "atom", "spiral", "plot"] },
		"01-05": { name: "徐霞客诞辰", types: ["leaf", "sprout", "cloud", "kite", "arch"] },
		"01-08": { name: "霍金诞辰", types: ["star", "shootingStar", "moonOrb", "sparkle", "cloud", "galaxy", "atom", "plot"] },
		"01-09": { name: "茅以升诞辰", types: ["shootingStar", "cloud", "star", "sun", "arch"] },
		"01-20": { name: "安培诞辰", types: ["bolt", "wave", "atom", "spark"] },
		"01-23": { name: "严济慈诞辰", types: ["star", "sparkle", "moonOrb", "cloud", "atom"] },
		"01-27": { name: "丁肇中诞辰", types: ["star", "sparkle", "shootingStar", "moonOrb", "atom"] },
		"02-02": { name: "世界湿地日", types: ["bubble", "cloud", "rain", "leaf", "petal"] },
		"02-05": { name: "王选诞辰", types: ["shootingStar", "star", "bubble", "cloud", "matrix", "circuit"] },
		"02-08": { name: "门捷列夫诞辰", types: ["bubble", "sparkle", "star", "cloud", "benzene"] },
		"02-11": { name: "爱迪生诞辰", types: ["spark", "sparkle", "star", "sun", "lantern", "bolt"] },
		"02-12": { name: "达尔文诞辰", types: ["leaf", "petal", "cloud", "sun", "rain", "butterfly", "cell", "helix"] },
		"02-15": { name: "伽利略诞辰", types: ["star", "moonOrb", "shootingStar", "sparkle", "plot", "wave"] },
		"02-19": { name: "哥白尼诞辰", types: ["moonOrb", "star", "shootingStar", "cloud", "galaxy", "atom"] },
		"02-22": { name: "赫兹诞辰", types: ["wave", "bolt", "sparkle", "star"] },
		"03-03": { name: "世界野生动植物日", types: ["leaf", "petal", "cloud", "sun"] },
		"03-07": { name: "竺可桢诞辰", types: ["cloud", "rain", "sun", "leaf", "wave", "sprout"] },
		"03-14": { name: "爱因斯坦诞辰·圆周率日", types: ["star", "moonOrb", "shootingStar", "sparkle", "sun", "atom", "wave", "spiral", "plot", "matrix", "galaxy"] },
		"03-15": { name: "消费者权益日", types: ["heart", "bubble", "sparkle", "ribbon"] },
		"03-16": { name: "欧姆诞辰", types: ["bolt", "wave", "matrix", "spark"] },
		"03-21": { name: "世界森林日", types: ["leaf", "maple", "cloud", "sun", "petal", "sprout"] },
		"03-22": { name: "世界水日", types: ["bubble", "rain", "cloud", "kite", "wave"] },
		"03-23": { name: "世界气象日", types: ["cloud", "rain", "sun", "kite", "wave"] },
		"04-03": { name: "珍·古道尔诞辰", types: ["leaf", "petal", "cloud", "sun", "cell", "butterfly", "helix"] },
		"04-04": { name: "丘成桐诞辰·郭永怀诞辰", types: ["spiral", "plot", "star", "atom"] },
		"04-06": { name: "沃森诞辰（DNA 双螺旋）", types: ["helix", "cell", "bubble"] },
		"04-15": { name: "欧拉诞辰", types: ["star", "sparkle", "shootingStar", "bubble", "spiral", "plot"] },
		"04-22": { name: "世界地球日", types: ["leaf", "cloud", "bubble", "sun", "rain", "sprout", "cell"] },
		"04-23": { name: "世界读书日", types: ["petal", "ribbon", "cloud", "lanternString"] },
		"04-24": { name: "中国航天日", types: ["shootingStar", "star", "moonOrb", "cloud", "galaxy", "atom"] },
		"04-25": { name: "DNA 日·马可尼诞辰", types: ["bubble", "sparkle", "star", "cloud", "helix", "cell"] },
		"04-28": { name: "哥德尔诞辰", types: ["matrix", "plot", "spiral", "star"] },
		"04-30": { name: "高斯诞辰·香农诞辰", types: ["shootingStar", "star", "bubble", "sparkle", "spiral", "plot", "matrix"] },
		"05-05": { name: "马克思诞辰", types: ["heart", "ribbon", "cloud", "sun", "star"] },
		"05-08": { name: "世界微笑日", types: ["heart", "candy", "balloon", "sparkle"] },
		"05-11": { name: "费曼诞辰", types: ["star", "sparkle", "shootingStar", "moonOrb"] },
		"05-12": { name: "国际护士节·吴文俊诞辰", types: ["heart", "bubble", "sparkle", "sun", "spiral", "plot"] },
		"05-18": { name: "国际博物馆日", types: ["ribbon", "lanternString", "cloud", "petal"] },
		"05-22": { name: "国际生物多样性日", types: ["leaf", "petal", "cloud", "bubble", "butterfly", "cell", "helix"] },
		"05-23": { name: "林奈诞辰", types: ["petal", "leaf", "butterfly", "cell"] },
		"05-28": { name: "童第周诞辰·王淦昌诞辰", types: ["bubble", "sparkle", "cloud", "sun", "cell", "helix", "atom"] },
		"05-31": { name: "世界无烟日", types: ["cloud", "bubble", "sun", "heart"] },
		"06-05": { name: "世界环境日", types: ["leaf", "sun", "cloud", "rain", "sprout"] },
		"06-08": { name: "世界海洋日", types: ["bubble", "cloud", "rain", "kite"] },
		"06-13": { name: "麦克斯韦诞辰", types: ["spark", "star", "shootingStar", "sparkle", "wave", "bolt"] },
		"06-14": { name: "世界献血日", types: ["heart", "bubble", "sparkle", "sun"] },
		"06-19": { name: "帕斯卡诞辰", types: ["plot", "matrix", "bubble", "star"] },
		"06-23": { name: "图灵诞辰", types: ["shootingStar", "star", "bubble", "cloud", "matrix", "circuit", "clock", "abacus"] },
		"06-25": { name: "邓稼先诞辰", types: ["star", "sparkle", "shootingStar", "sun", "atom"] },
		"06-26": { name: "国际禁毒日", types: ["heart", "leaf", "sun", "cloud"] },
		"07-10": { name: "特斯拉诞辰", types: ["spark", "shootingStar", "sparkle", "sun", "star", "bolt", "wave"] },
		"07-20": { name: "人类登月纪念日", types: ["moonOrb", "star", "shootingStar", "cloud", "galaxy", "atom"] },
		"08-06": { name: "弗莱明诞辰", types: ["bubble", "sparkle", "heart", "cloud", "cell"] },
		"08-09": { name: "阿伏伽德罗诞辰·侯德榜诞辰", types: ["benzene", "bubble", "sparkle", "star"] },
		"08-12": { name: "国际青年日", types: ["kite", "balloon", "confetti", "sun"] },
		"08-16": { name: "于敏诞辰", types: ["atom", "star", "galaxy", "sun"] },
		"08-26": { name: "拉瓦锡诞辰", types: ["benzene", "bubble", "sparkle", "sun"] },
		"08-28": { name: "周培源诞辰", types: ["atom", "wave", "star", "sparkle"] },
		"08-30": { name: "卢瑟福诞辰", types: ["atom", "galaxy", "sparkle", "star"] },
		"09-06": { name: "道尔顿诞辰", types: ["benzene", "bubble", "star", "sparkle"] },
		"09-07": { name: "袁隆平诞辰", types: ["leaf", "sun", "cloud", "petal", "sprout"] },
		"09-16": { name: "国际臭氧层日", types: ["cloud", "bubble", "sun", "leaf"] },
		"09-17": { name: "黎曼诞辰", types: ["spiral", "plot", "star", "galaxy"] },
		"09-21": { name: "国际和平日", types: ["heart", "cloud", "sun", "balloon"] },
		"09-22": { name: "法拉第诞辰", types: ["spark", "star", "sparkle", "sun", "bolt", "wave"] },
		"09-23": { name: "苏步青诞辰", types: ["spiral", "plot", "star", "bubble"] },
		"09-25": { name: "摩尔根诞辰", types: ["cell", "helix", "butterfly", "petal"] },
		"09-26": { name: "巴甫洛夫诞辰", types: ["cell", "heart", "bubble", "sparkle"] },
		"09-27": { name: "世界旅游日", types: ["kite", "cloud", "sun", "balloon"] },
		"10-07": { name: "玻尔诞辰", types: ["star", "moonOrb", "sparkle", "shootingStar", "atom", "galaxy"] },
		"10-10": { name: "世界精神卫生日", types: ["heart", "bubble", "cloud", "sun"] },
		"10-16": { name: "世界粮食日·钱三强诞辰", types: ["leaf", "sun", "cloud", "petal", "sprout", "atom"] },
		"10-20": { name: "钟南山诞辰", types: ["heart", "bubble", "sun", "sparkle"] },
		"10-21": { name: "诺贝尔诞辰", types: ["benzene", "atom", "sparkle", "star"] },
		"10-24": { name: "列文虎克诞辰", types: ["cell", "bubble", "sparkle", "star"] },
		"10-25": { name: "伽罗瓦诞辰", types: ["plot", "star", "bolt", "spark"] },
		"10-26": { name: "李四光诞辰", types: ["leaf", "cloud", "sun", "sparkle"] },
		"10-28": { name: "陈省身诞辰", types: ["spiral", "plot", "star", "petal"] },
		"11-07": { name: "居里夫人诞辰", types: ["spark", "sparkle", "star", "sun", "benzene", "atom"] },
		"11-08": { name: "记者节", types: ["lanternString", "cloud", "ribbon", "star"] },
		"11-09": { name: "消防宣传日", types: ["ember", "spark", "firecracker", "sun", "bolt"] },
		"11-12": { name: "华罗庚诞辰", types: ["shootingStar", "star", "bubble", "sparkle", "spiral", "plot", "abacus"] },
		"11-14": { name: "世界糖尿病日", types: ["heart", "bubble", "sun", "sparkle"] },
		"12-01": { name: "世界艾滋病日", types: ["heart", "bubble", "ribbon", "sparkle"] },
		"12-02": { name: "全国交通安全日", types: ["flag", "cloud", "sun", "sparkle"] },
		"12-04": { name: "国家宪法日", types: ["flag", "star", "ribbon", "lanternString"] },
		"12-05": { name: "国际志愿者日", types: ["heart", "balloon", "candy", "sparkle"] },
		"12-10": { name: "阿达·洛芙莱斯诞辰", types: ["bubble", "shootingStar", "star", "cloud", "matrix", "circuit", "plot"] },
		"12-11": { name: "钱学森诞辰", types: ["shootingStar", "star", "moonOrb", "cloud", "atom", "galaxy"] },
		"12-25": { name: "朱光亚诞辰", types: ["star", "sparkle", "shootingStar", "sun", "atom"] },
		"12-26": { name: "巴贝奇诞辰", types: ["bubble", "sparkle", "star", "cloud", "matrix", "clock", "circuit", "abacus"] },
		"12-27": { name: "开普勒诞辰·巴斯德诞辰", types: ["moonOrb", "star", "shootingStar", "bubble", "galaxy", "benzene"] },
		"12-28": { name: "冯·诺依曼诞辰", types: ["matrix", "circuit", "clock", "abacus"] },
		"12-30": { name: "屠呦呦诞辰", types: ["leaf", "bubble", "sun", "sparkle", "benzene", "cell", "helix"] },
	};

	// 当天可用的平日特效：手动配置优先；否则有来历的日子偏向对应元素，其余从 10000 种里随机
	function everydayFxPool() {
		const cfg = weekdayCustom();
		if (cfg) return [customFxName(cfg)];
		const now = new Date();
		const key = `${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
		const theme = EVERYDAY_THEMES[key];
		if (!theme) return EVERYDAY_FX;
		const filtered = EVERYDAY_FX.filter(name => {
			const raw = name.split(":")[0].split("#")[0];
			const gm = /^g(\d+)$/.exec(raw);
			const tag = gm ? FX_ELEMENTS[(parseInt(gm[1], 10) || 1) - 1].tag : raw;
			return theme.types.includes(tag);
		});
		return filtered.length ? filtered : EVERYDAY_FX;
	}
	// ===== 鼠标互动引擎：14 种移动力场 × 16 种点击效果 × 8 种光标拖尾 =====
	// 全组合出 1792 个命名预设（远超 300 种），随全屏特效每 10 分钟一起轮换：
	// 同一种特效配上不同互动预设，观感完全不同。全部纯 canvas 实现，无 DOM 开销。
	// 参数约定：dx/dy = 粒子相对光标的方向，d = 距离，near = 0~1 越近越大，mf = 当前预设
	const MOUSE_MOVES = {
		// 推开（经典手感）：光标像一阵风把粒子吹开，移动越快推得越远
		push(q, dx, dy, d, near, s, mf) {
			const f = near * 1.7 * mf.str * (1 + Math.min(1.2, s.ms / 22));
			q.x += (dx / d) * f; q.y += (dy / d) * f; q.glow = near;
		},
		// 吸附：光标是磁铁，粒子往光标上贴
		pull(q, dx, dy, d, near, s, mf) {
			const f = near * 1.5 * mf.str;
			q.x -= (dx / d) * f; q.y -= (dy / d) * f; q.glow = near * 0.8;
		},
		// 环绕：粒子绕着光标打转，像小行星带
		orbit(q, dx, dy, d, near, s, mf) {
			const f = near * 1.4 * mf.str;
			q.x += (-dy / d) * f; q.y += (dx / d) * f; q.glow = near;
		},
		// 涡旋：被吸进来同时旋转，像水流进下水口
		vortex(q, dx, dy, d, near, s, mf) {
			const f = near * 1.2 * mf.str;
			q.x += ((dx / d) * 0.5 - (dy / d)) * f;
			q.y += ((dy / d) * 0.5 + (dx / d)) * f;
			q.glow = near;
		},
		// 弹簧：被拉过去又被弹回来，来回震荡
		spring(q, dx, dy, d, near, s, mf) {
			const f = near * 1.6 * mf.str * Math.sin(Date.now() / 260 + q.phase);
			q.x -= (dx / d) * f; q.y -= (dy / d) * f; q.glow = near * 0.7;
		},
		// 果冻：近距离左右抖动，Q 弹 Q 弹的
		jelly(q, dx, dy, d, near, s, mf) {
			const f = near * 1.3 * mf.str * Math.sin(Date.now() / 55 + q.phase);
			q.x += (-dy / d) * f; q.y += (dx / d) * f * 0.4; q.glow = near;
		},
		// 点燃：光标是火苗，附近的粒子被点亮并往上飘
		ignite(q, dx, dy, d, near, s, mf) {
			q.y -= near * 1.6 * mf.str; q.glow = Math.min(1, near * 1.4);
		},
		// 冻结：光标是冰块，附近粒子被冻住停在半空
		freeze(q, dx, dy, d, near, s, mf) {
			q.y -= q.vy * near * 0.9; q.x -= q.vx * near * 0.9;
			q.glow = near * 0.5; q.frost = Math.max(q.frost || 0, near);
		},
		// 分流：粒子从光标两侧分开，像船头破浪
		split(q, dx, dy, d, near, s, mf) {
			q.x += (dx >= 0 ? 1 : -1) * near * 2.1 * mf.str; q.glow = near;
		},
		// 环形归位：把粒子推到光标周围 60px 的环上排列
		ringPush(q, dx, dy, d, near, s, mf) {
			const err = d - 60;
			q.x += (dx / d) * err * 0.06 * mf.str; q.y += (dy / d) * err * 0.06 * mf.str;
			q.glow = near * 0.9;
		},
		// 尾风：光标移动方向带起一阵风，粒子被吹着跑
		wind(q, dx, dy, d, near, s, mf) {
			q.x += (s.mdx || 0) * 0.16 * near * mf.str;
			q.y += (s.mdy || 0) * 0.16 * near * mf.str;
			q.glow = near * 0.7;
		},
		// 引力井：光标很"重"，粒子路过时轨道被掰弯
		gravityWell(q, dx, dy, d, near, s, mf) {
			const f = near * 1.1 * mf.str;
			q.x += (-(dy / d) * 0.85 - (dx / d) * 0.3) * f;
			q.y += ((dx / d) * 0.85 - (dy / d) * 0.3) * f;
			q.glow = near * 0.8;
		},
		// 弹球：猛地弹开，带一点过冲
		bounce(q, dx, dy, d, near, s, mf) {
			const f = near * near * 3.2 * mf.str * (1 + Math.min(1, s.ms / 30));
			q.x += (dx / d) * f; q.y += (dy / d) * f; q.glow = near;
		},
		// 磁吸抖散：吸过来的同时横向抖开，像铁屑遇到磁铁又互相排斥
		magnetJitter(q, dx, dy, d, near, s, mf) {
			const f = near * 1.2 * mf.str;
			q.x -= (dx / d) * f * 0.7 + Math.sin(Date.now() / 70 + q.phase) * near * 1.1;
			q.y -= (dy / d) * f * 0.7; q.glow = near;
		},
	};

	// 临时粒子（拖尾/点击迸发共用）：有寿命、会淡出，用现有元素绘制函数渲染
	function spawnTemp(s, x, y, opts) {
		if (!s.temp) s.temp = [];
		if (s.temp.length > 260) s.temp.splice(0, s.temp.length - 260);
		s.temp.push({
			x, y,
			vx: opts.vx || 0, vy: opts.vy || 0, g: opts.g || 0,
			age: 0, life: opts.life || 700,
			size: opts.size || 7, rot: Math.random() * Math.PI * 2,
			vr: (Math.random() - 0.5) * 0.14,
			phase: Math.random() * Math.PI * 2,
			color: opts.color || "#ffd43b",
			type: opts.type || "sparkle",
			kind: Math.floor(Math.random() * 3),
		});
	}
	function tempBurst(s, x, y, n, opts) {
		const colors = (s.palette && s.palette.length) ? s.palette : FX_PALETTE.confetti;
		for (let i = 0; i < n; i++) {
			const a = Math.random() * Math.PI * 2;
			const v = (opts.v || 2.2) * (0.5 + Math.random() * 0.8);
			spawnTemp(s, x, y, {
				vx: Math.cos(a) * v, vy: Math.sin(a) * v - (opts.up || 0),
				g: opts.g || 0, life: (opts.life || 800) * (0.6 + Math.random() * 0.7),
				size: (opts.size || 8) * (0.6 + Math.random() * 0.8),
				color: colors[Math.floor(Math.random() * colors.length)],
				type: opts.types ? opts.types[Math.floor(Math.random() * opts.types.length)] : "sparkle",
			});
		}
	}

	// 点击互动效果（x/y 为点击坐标；ripple 由 onClick 分支直接设置）
	const MOUSE_CLICKS = {
		heartBurst(s, x, y) { tempBurst(s, x, y, 26, { types: ["heart", "heart", "sparkle"], v: 2.6, up: 0.8, life: 950, size: 9 }); },
		starBurst(s, x, y) { tempBurst(s, x, y, 30, { types: ["star", "sparkle"], v: 3.2, life: 900, size: 9 }); },
		confettiRing(s, x, y) { tempBurst(s, x, y, 36, { types: ["confetti", "ribbon"], v: 3.6, life: 1100, size: 8 }); },
		spiral(s, x, y) {
			// 螺旋扩散：切向 + 向外，转着圈飞出去
			const colors = (s.palette && s.palette.length) ? s.palette : FX_PALETTE.confetti;
			for (let i = 0; i < 30; i++) {
				const a = i / 30 * Math.PI * 2;
				spawnTemp(s, x, y, {
					vx: Math.cos(a) * 1.1 - Math.sin(a) * 2.0, vy: Math.sin(a) * 1.1 + Math.cos(a) * 2.0,
					g: 0.006, life: 1000 + i * 18, size: 7,
					color: colors[i % colors.length], type: i % 3 ? "sparkle" : "star",
				});
			}
		},
		fountain(s, x, y) {
			// 喷泉：从点击处向上喷，受重力落下
			for (let i = 0; i < 34; i++) {
				spawnTemp(s, x + (Math.random() - 0.5) * 14, y, {
					vx: (Math.random() - 0.5) * 2.4, vy: -(3.2 + Math.random() * 3.4),
					g: 0.055, life: 1300, size: 8,
					color: (s.palette || FX_PALETTE.confetti)[Math.floor(Math.random() * (s.palette || FX_PALETTE.confetti).length)],
					type: ["bubble", "sparkle", "star"][Math.floor(Math.random() * 3)],
				});
			}
		},
		bloom(s, x, y) { tempBurst(s, x, y, 24, { types: ["petal", "petal", "sparkle"], v: 1.4, life: 1400, size: 10 }); },
		blackHole(s, x, y) {
			// 黑洞：附近粒子被猛地吸到点击处，再炸出一圈星
			for (const q of s.parts) {
				const dx = x - q.x, dy = y - q.y, d = Math.hypot(dx, dy);
				if (d < 300 && d > 1) { q.x += (dx / d) * (1 - d / 300) * 26; q.y += (dy / d) * (1 - d / 300) * 26; q.glow = 1; }
			}
			tempBurst(s, x, y, 22, { types: ["star", "sparkle"], v: 3.8, life: 800, size: 7 });
		},
		rainbowRing(s, x, y) {
			const rainbow = ["#ff595e", "#ffca3a", "#8ac926", "#1982c4", "#6a4c93", "#ff7ab6", "#00c2a8"];
			for (let i = 0; i < 28; i++) {
				const a = i / 28 * Math.PI * 2;
				spawnTemp(s, x + Math.cos(a) * 12, y + Math.sin(a) * 12, {
					vx: Math.cos(a) * 2.8, vy: Math.sin(a) * 2.8, life: 1000, size: 9,
					color: rainbow[i % rainbow.length], type: i % 2 ? "bubble" : "sparkle",
				});
			}
		},
		rainDrop(s, x, y) {
			for (let i = 0; i < 20; i++) {
				spawnTemp(s, x + (Math.random() - 0.5) * 160, y - 120 - Math.random() * 80, {
					vy: 4.5 + Math.random() * 2, life: 900, size: 8,
					color: "#a5d8ff", type: "rain",
				});
			}
		},
		cage(s, x, y) {
			// 粒子笼：把附近粒子推到点击处 90px 的球面上，短暂困住
			for (const q of s.parts) {
				const dx = q.x - x, dy = q.y - y, d = Math.hypot(dx, dy);
				if (d < 260 && d > 1) {
					const err = d - 90;
					q.x += (dx / d) * err * 0.35; q.y += (dy / d) * err * 0.35; q.glow = 0.9;
				}
			}
		},
		attractBurst(s, x, y) {
			for (const q of s.parts) {
				const dx = x - q.x, dy = y - q.y, d = Math.hypot(dx, dy);
				if (d > 1) { q.x += (dx / d) * 9; q.y += (dy / d) * 9; q.glow = 0.8; }
			}
		},
		twinkleZone(s, x, y) {
			// 星光领域：点击处附近 1.6 秒内粒子疯狂闪烁
			const until = performance.now() + 1600;
			for (const q of s.parts) {
				if (Math.hypot(q.x - x, q.y - y) < 190) q.twinkle = until;
			}
		},
		swapColor(s) {
			// 颜色洗牌：全场粒子重新分配配色，视觉焕然一新
			const colors = (s.palette && s.palette.length) ? s.palette : FX_PALETTE.confetti;
			for (const q of s.parts) q.color = colors[Math.floor(Math.random() * colors.length)];
		},
		shockwave(s, x, y) { s.ripple = { x, y, born: performance.now(), big: true }; },
		meteorShower(s, x, y) {
			for (let i = 0; i < 12; i++) {
				spawnTemp(s, x + (Math.random() - 0.5) * 200 - 100, y - 200 - Math.random() * 160, {
					vx: 2.4 + Math.random() * 1.6, vy: 1.4 + Math.random(), life: 1200, size: 10,
					color: "#fff3bf", type: "shootingStar",
				});
			}
		},
	};

	// 光标拖尾：移动时在光标处留下短命粒子（节流由 onMove 控制）
	const MOUSE_TRAILS = {
		sparkleTrail(s, x, y) {
			spawnTemp(s, x, y, { vx: (Math.random() - .5) * .6, vy: -0.3, life: 520, size: 5 + Math.random() * 4, type: "sparkle" });
		},
		cometTrail(s, x, y) {
			spawnTemp(s, x, y, { vx: (Math.random() - .5) * .4, vy: 0.2, life: 640, size: 11, type: "star" });
			spawnTemp(s, x + 6, y + 4, { life: 380, size: 5, type: "sparkle" });
		},
		bubbleTrail(s, x, y) {
			spawnTemp(s, x, y, { vx: (Math.random() - .5) * .5, vy: -0.55, life: 900, size: 5 + Math.random() * 5, type: "bubble", color: "#d0ebff" });
		},
		heartTrail(s, x, y) {
			spawnTemp(s, x, y, { vx: (Math.random() - .5) * .5, vy: -0.7, life: 760, size: 7, type: "heart", color: "#ff8fab" });
		},
		starTrail(s, x, y) {
			spawnTemp(s, x, y, { vx: (Math.random() - .5) * .7, vy: (Math.random() - .5) * .7, life: 560, size: 6 + Math.random() * 4, type: "star", color: "#ffe066" });
		},
		petalTrail(s, x, y) {
			spawnTemp(s, x, y, { vx: (Math.random() - .5) * .8, vy: 0.5, life: 980, size: 8, type: "petal", color: "#ffb7c5" });
		},
		dustTrail(s, x, y) {
			const colors = (s.palette && s.palette.length) ? s.palette : FX_PALETTE.confetti;
			spawnTemp(s, x, y, { vx: (Math.random() - .5) * .9, vy: (Math.random() - .5) * .9, life: 480, size: 3 + Math.random() * 3, type: "snow", color: colors[Math.floor(Math.random() * colors.length)] });
		},
	};

	// 看板郎（Live2D）与特效的互动锚点：角色中心坐标；手机端/隐藏时返回 null
	function waifuCenter() {
		const el = document.getElementById("waifu");
		if (!el) return null;
		const r = el.getBoundingClientRect();
		if (r.width < 10 || r.height < 10) return null;
		return { x: r.left + r.width / 2, y: r.top + r.height * 0.42 };
	}
	// 从看板郎身上迸发一圈粒子（点击角色/换装/连点彩蛋时），n 可指定数量
	function waifuBurst(kinds, n) {
		if (!fxState) return;
		const c = waifuCenter();
		if (!c) return;
		tempBurst(fxState, c.x, c.y, n || 34, { types: kinds || ["star", "sparkle", "heart"], v: 3.0, up: 1.2, life: 1100, size: 9 });
	}

	// 互动预设注册表：14 力场 × 16 点击 × 8 拖尾 全组合 = 1792 个命名预设
	// （远超 300 种），强度分 5 档、1/3 带看板郎力场（well 公转 / aura 点亮），
	// 进页面与每次特效轮换时从中随机抽取
	const MOUSE_FX_PRESETS = (() => {
		const moves = Object.keys(MOUSE_MOVES);
		const clicks = ["ripple", "heartBurst", "starBurst", "confettiRing", "shockwave", "spiral",
			"fountain", "bloom", "blackHole", "rainbowRing", "rainDrop", "cage",
			"attractBurst", "twinkleZone", "swapColor", "meteorShower"];
		const trails = ["none", "sparkleTrail", "cometTrail", "bubbleTrail", "heartTrail", "starTrail", "petalTrail", "dustTrail"];
		const out = [];
		for (let m = 0; m < moves.length; m++) {
			for (let c = 0; c < clicks.length; c++) {
				for (let tr = 0; tr < trails.length; tr++) {
					const i = out.length;
					out.push({
						move: moves[m],
						click: clicks[c],
						trail: trails[tr],
						str: 0.7 + (i % 5) * 0.35,
						// 1/3 的预设带看板郎力场：粒子绕着角色转（well）或被角色点亮（aura）
						waifu: (i % 3 === 0) ? (i % 2 ? "well" : "aura") : null,
					});
				}
			}
		}
		return out;
	})();
	function pickMouseFx() {
		return MOUSE_FX_PRESETS[Math.floor(Math.random() * MOUSE_FX_PRESETS.length)];
	}

	// ===== 全屏特效循环：节日默认播放，平日按开关播放，每 10 分钟随机换一种 =====
	// 进页面先随机挑一种，之后每 10 分钟换一次；刷新页面重新随机。
	const FX_ROTATE_MS = 10 * 60 * 1000;
	// 节日特效整体放大的倍数，主题配置面板可调（localStorage: waifu-fx-festival-boost），默认 1.9
	const FX_FESTIVAL_BOOST_DEFAULT = 1.9;
	function festivalBoost() {
		try {
			const v = parseFloat(localStorage.getItem("waifu-fx-festival-boost"));
			if (!isNaN(v)) return Math.min(4, Math.max(0.5, v));
		} catch (e) { }
		return FX_FESTIVAL_BOOST_DEFAULT;
	}
	// 平日特效整体放大的倍数，主题配置面板滑块可调（localStorage: waifu-fx-weekday-boost），
	// 默认 1.8：小/中/大三档一起上调约 80%，配合下方更粗的曲线描边，函数图形不再糊成一团
	const FX_WEEKDAY_BOOST_DEFAULT = 1.8;
	function weekdayBoost() {
		try {
			const v = parseFloat(localStorage.getItem("waifu-fx-weekday-boost"));
			if (!isNaN(v)) return Math.min(4, Math.max(0.5, v));
		} catch (e) { }
		return FX_WEEKDAY_BOOST_DEFAULT;
	}
	let fxState = null;

	// 当前时段可用的特效池：节日优先（默认开启、不可配置）；平日看开关
	function ambientFxPool() {
		const todays = getFestivalsToday();
		if (todays.length) {
			const festival = todays[Math.floor(Math.random() * todays.length)];
			return { list: festivalEffects(festival), colors: festival.colors, festival: true };
		}
		if (!weekdayFxEnabled()) return null;
		return { list: everydayFxPool(), colors: null, festival: false };
	}

	function pickAmbientFx() {
		const pool = ambientFxPool();
		if (!pool || !pool.list.length) return null;
		const name = pool.list[Math.floor(Math.random() * pool.list.length)];
		return { name, colors: pool.colors, festival: !!pool.festival };
	}

	function stopAmbientFx() {
		if (!fxState) return;
		cancelAnimationFrame(fxState.raf);
		clearInterval(fxState.rotateTimer);
		window.removeEventListener("resize", fxState.onResize);
		if (fxState.onMove) window.removeEventListener("mousemove", fxState.onMove);
		if (fxState.onClick) window.removeEventListener("click", fxState.onClick);
		fxState.canvas.remove();
		fxState = null;
	}

	function startAmbientFx() {
		if (fxState || !document.body) return;
		if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
		if (!ambientFxPool()) return;
		const canvas = document.createElement("canvas");
		canvas.className = "waifu-festival-fx";
		document.body.appendChild(canvas);
		const ctx = canvas.getContext("2d");
		if (!ctx) { canvas.remove(); return; }
		fxState = {
			canvas, ctx, W: 0, H: 0,
			type: "", element: null, palette: [], parts: [], bursts: [], nextBurst: 0,
			speedMul: 1, sizeMul: 1, densityMul: 1, raf: 0, rotateTimer: 0, onResize: null,
			mx: -9999, my: -9999, ms: 0, mdx: 0, mdy: 0, ripple: null, onMove: null, onClick: null,
			// 鼠标互动预设（1792 种里随机）+ 临时粒子（拖尾/迸发）+ 悬停/掠过/呼出节流
			mouseFx: pickMouseFx(), temp: [], lastTrail: 0, prevT: 0,
			hoverAt: 0, swipeAt: 0, waifuEmitAt: 0,
		};
		// 鼠标互动：按当前预设的力场响应光标；移动方向带风；节流生成光标拖尾；
		// 与角色的互动：悬停时朝光标吹星星、快速掠过时带起粒子风（均限频）
		fxState.onMove = e => {
			if (fxState.mx > -9000) {
				const dx = e.clientX - fxState.mx, dy = e.clientY - fxState.my;
				fxState.ms = fxState.ms * 0.6 + Math.min(40, Math.hypot(dx, dy)) * 0.4;   // 平滑鼠标速度
				fxState.mdx = dx; fxState.mdy = dy;                                        // 本帧位移（尾风用）
			}
			fxState.mx = e.clientX;
			fxState.my = e.clientY;
			// 光标拖尾（每 55ms 最多一个，避免拖尾粒子刷屏）
			const mf = fxState.mouseFx;
			if (mf && mf.trail !== "none") {
				const now = performance.now();
				if (now - fxState.lastTrail > 55) {
					fxState.lastTrail = now;
					MOUSE_TRAILS[mf.trail](fxState, e.clientX, e.clientY);
				}
			}
			// 与看板郎的鼠标互动（都有限频，不会刷屏）：
			const wc = waifuCenter();
			if (wc) {
				const wd = Math.hypot(e.clientX - wc.x, e.clientY - wc.y);
				const now = performance.now();
				// 悬停：光标凑近角色时，角色朝光标方向「吹」出几颗小星星（害羞回应，2.5 秒一次）
				if (wd < 170 && now - fxState.hoverAt > 2500) {
					fxState.hoverAt = now;
					const a = Math.atan2(e.clientY - wc.y, e.clientX - wc.x);
					for (let i = 0; i < 3; i++) {
						spawnTemp(fxState, wc.x + Math.cos(a) * 30, wc.y + Math.sin(a) * 30, {
							vx: Math.cos(a) * (1 + Math.random()), vy: Math.sin(a) * (1 + Math.random()) - .4,
							life: 800, size: 7, type: "sparkle", color: "#ffd6ff",
						});
					}
				}
				// 快速掠过：光标高速扫过角色身边，带起一阵粒子风（像风吹乱了头发，1.2 秒一次）
				if (wd < 220 && fxState.ms > 26 && now - (fxState.swipeAt || 0) > 1200) {
					fxState.swipeAt = now;
					const colors = (fxState.palette && fxState.palette.length) ? fxState.palette : FX_PALETTE.confetti;
					for (let i = 0; i < 10; i++) {
						spawnTemp(fxState, wc.x + (Math.random() - .5) * 70, wc.y + (Math.random() - .5) * 90, {
							vx: (fxState.mdx || 0) * .12 + (Math.random() - .5), vy: (fxState.mdy || 0) * .12 - .5,
							life: 700, size: 6, type: "sparkle",
							color: colors[Math.floor(Math.random() * colors.length)],
						});
					}
				}
			}
		};
		fxState.onClick = e => {
			if (!fxState) return;
			// 点在看板郎身上由专属互动处理（waifuBurst + 文案），这里跳过避免叠加
			if (e.target && e.target.closest && e.target.closest("#waifu")) return;
			const x = e.clientX, y = e.clientY;
			const mf = fxState.mouseFx || { click: "ripple" };
			if (fxState.type === "firework") {
				spawnFireworkBurst(fxState, x, y);
			} else if (mf.click === "ripple") {
				fxState.ripple = { x, y, born: performance.now() };
			} else {
				const fn = MOUSE_CLICKS[mf.click];
				if (fn) fn(fxState, x, y);
			}
			// 点击落在角色 260px 内：特效波及到看板郎，被「吓一跳」冒一小簇泡泡，
			// 三成概率慢半拍嘀咕一句——用户没点角色，角色也会对身边的动静有反应
			const wc = waifuCenter();
			if (wc && Math.hypot(x - wc.x, y - wc.y) < 260) {
				waifuBurst(["bubble", "sparkle"], 14);
				if (Math.random() < 0.3) {
					const lines = ["哇！吓我一跳……", "欸？旁边好热闹～", "呀，就在我旁边炸开了！", "咳咳，我什么都没看见。"];
					setTimeout(() => showMessage(lines[Math.floor(Math.random() * lines.length)], 2500, 8), 350);
				}
			}
		};
		window.addEventListener("mousemove", fxState.onMove);
		window.addEventListener("click", fxState.onClick);
		// 跟随窗口大小铺满可视区，高清屏按像素比放大，避免发虚
		const resize = () => {
			if (!fxState) return;
			const W = Math.max(1, window.innerWidth), H = Math.max(1, window.innerHeight);
			const dpr = Math.min(2, window.devicePixelRatio || 1);
			canvas.width = Math.round(W * dpr);
			canvas.height = Math.round(H * dpr);
			canvas.style.width = W + "px";
			canvas.style.height = H + "px";
			ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
			fxState.W = W;
			fxState.H = H;
			fxState.parts = buildFxParticles(fxState.type, W, H, fxState.palette, fxState.sizeMul, fxState.densityMul, fxState.element);
		};
		fxState.onResize = resize;
		window.addEventListener("resize", resize);
		resize();
		switchAmbientFx();
		// 节日进场彩蛋：角色上场先在自己的位置放一发大迸发（用当天节日配色，
		// 平日特效不打扰）——让「角色」和「节日特效」从第一秒就绑定在一起
		setTimeout(() => {
			if (!fxState || !fxState.entry || !fxState.entry.festival) return;
			const c = waifuCenter();
			if (c) tempBurst(fxState, c.x, c.y - 30, 46, { types: ["star", "sparkle", "heart"], v: 4.2, up: 1.6, life: 1300, size: 9 });
		}, 900);
		fxState.rotateTimer = setInterval(() => {
			// 既没有节日、平日特效又被关掉时收掉；否则换一种继续放
			if (!ambientFxPool()) { stopAmbientFx(); return; }
			switchAmbientFx();
		}, FX_ROTATE_MS);
		if (!fxState.raf) animateFestivalFx(performance.now());
	}

	// 切换/应用特效：keepEntry 传入时不重新随机，只按新参数重建（调大小、改配置时保持当前特效）
	function switchAmbientFx(keepEntry) {
		if (!fxState) return;
		const entry = keepEntry || pickAmbientFx();
		if (!entry) return;
		fxState.entry = entry;
		const fx = resolveFx(entry.name);
		fxState.type = fx.type;
		fxState.element = fx.element || null;
		fxState.speedMul = fx.speed || 1;
		// 节日特效按主题面板配置的整体倍数放大；平日特效按「平日特效大小」滑块整体放大
		// （默认 1.8 倍，小/中/大三档一起上调，手动配置里的尺寸滑块是相对此倍率的精细微调）
		fxState.sizeMul = (fx.sizeMul || 1) * (entry.festival ? festivalBoost() : weekdayBoost());
		fxState.densityMul = fx.densityMul || 1;
		fxState.palette = fx.colors || ((entry.colors && entry.colors.length) ? entry.colors : (FX_PALETTE[fx.type] || FX_PALETTE.confetti));
		fxState.bursts = [];
		fxState.nextBurst = 0;
		fxState.ripple = null;   // 切换特效时清掉旧涟漪，避免新特效画出旧点击的波纹
		fxState.parts = buildFxParticles(fx.type, fxState.W, fxState.H, fxState.palette, fxState.sizeMul, fxState.densityMul, fxState.element);
		// 特效每 10 分钟轮换时，鼠标互动预设一起换（1792 种里重新随机）：
		// 同一种特效配上不同力场/点击/拖尾，观感完全不同；keepEntry（仅调大小/改开关）时保持不变
		if (!keepEntry) fxState.mouseFx = pickMouseFx();
	}

	// 主题配置里切换"平日特效"后立刻生效：关掉就收，打开就开；
	// 调整节日特效大小等配置时保持当前特效不变，只按新参数重建
	window.addEventListener("waifu-fx-config", () => {
		if (fxState) {
			if (!ambientFxPool()) { stopAmbientFx(); return; }
			switchAmbientFx(fxState.entry);
			return;
		}
		startAmbientFx();
	});

	function fxRise(type, element) {
		if (type === "generic") return !!element && genericMotion(element.family, element.curve) === "rise";
		return type === "lantern" || type === "ember" || type === "balloon" || type === "skyLantern"
			|| type === "spark" || type === "bubble" || type === "sunbeam" || type === "moonOrb"
			|| type === "kite";
	}

	function fxStill(type, element) {
		if (type === "generic") return !!element && genericMotion(element.family, element.curve) === "still";
		return type === "star" || type === "sparkle" || type === "sun";
	}

	function buildFxParticles(type, W, H, palette, sizeMul, densityMul, element) {
		if (!type || !W || !H || type === "firework") return [];
		const rise = fxRise(type, element);
		const still = fxStill(type, element);
		const drift = type === "cloud";
		// 图形放大后单个粒子占屏更多，按 sizeMul 的平方根补偿数量（面积∝size²，取 √ 控制开销），
		// 避免「放大后画面变稀疏」；上限同步放宽到 320
		const sizeComp = Math.sqrt(Math.max(0.5, sizeMul || 1) / 1.45);
		const count = Math.min(320, Math.max(30, Math.round((W / 14) * (densityMul || 1) * sizeComp)));
		const parts = [];
		for (let i = 0; i < count; i++) {
			parts.push({
				x: Math.random() * W,
				y: rise ? H * (0.4 + Math.random() * 0.6) : (still || drift ? Math.random() * H : -Math.random() * H * 0.6),
				vx: (Math.random() - 0.5) * 0.6,
				vy: 0.35 + Math.random() * 1.1,
				size: (6 + Math.random() * 9) * (sizeMul || 1),
				rot: Math.random() * Math.PI * 2,
				vr: (Math.random() - 0.5) * 0.09,
				color: palette[Math.floor(Math.random() * palette.length)],
				phase: Math.random() * Math.PI * 2,
				kind: Math.floor(Math.random() * 3),   // 同类特效里换着花样画
				el: element || null,
			});
		}
		return parts;
	}

	// 可见涟漪：点击处扩散的圆环（普通涟漪一圈白色；冲击波 big 更大更粗，再补一道彩色内环）
	// 之前只有粒子推力、没有可见波纹，用户点「涟漪/冲击波」感知不到效果
	function drawRipples(s, t) {
		if (!s.ripple) return;
		const age = (t - s.ripple.born) / (s.ripple.big ? 900 : 700);
		if (age >= 1) { s.ripple = null; return; }
		const ctx = s.ctx;
		const radius = s.ripple.big ? 70 + age * 320 : 20 + age * 170;   // 与粒子推力半径同步扩散
		ctx.save();
		ctx.globalCompositeOperation = "lighter";
		ctx.strokeStyle = "rgba(255,255,255,0.55)";
		ctx.globalAlpha = 1 - age;
		ctx.lineWidth = (s.ripple.big ? 5 : 3) * (1 - age) + 0.5;
		ctx.beginPath();
		ctx.arc(s.ripple.x, s.ripple.y, radius, 0, Math.PI * 2);
		ctx.stroke();
		if (s.ripple.big) {   // 冲击波内圈：当前特效配色的彩色光环
			ctx.strokeStyle = (s.palette && s.palette[0]) || "#ffd93d";
			ctx.globalAlpha = (1 - age) * 0.7;
			ctx.lineWidth = 2.5 * (1 - age) + 0.5;
			ctx.beginPath();
			ctx.arc(s.ripple.x, s.ripple.y, radius * 0.66, 0, Math.PI * 2);
			ctx.stroke();
		}
		ctx.restore();
	}

	function animateFestivalFx(t) {
		const s = fxState;
		if (!s) return;
		s.ctx.clearRect(0, 0, s.W, s.H);
		if (s.type === "firework") drawFireworks(s, t);
		else drawFxParticles(s, t);
		drawTempParticles(s, t);   // 临时粒子两种特效模式都画（拖尾/点击/角色互动）
		drawRipples(s, t);         // 点击涟漪/冲击波的可见圆环
		// 看板郎周期性「呼出」特效：每隔 9~16 秒从角色身上飘出一小股当前配色粒子，
		// 像角色在呼吸/施法——特效仿佛就是从角色身上长出来的（特效 → 角色的存在感）
		if (t > (s.waifuEmitAt || 0)) {
			s.waifuEmitAt = t + 9000 + Math.random() * 7000;
			const c = waifuCenter();
			if (c) {
				const colors = (s.palette && s.palette.length) ? s.palette : FX_PALETTE.confetti;
				const n = 8 + Math.floor(Math.random() * 8);
				for (let i = 0; i < n; i++) {
					spawnTemp(s, c.x + (Math.random() - .5) * 54, c.y + (Math.random() - .5) * 64, {
						vx: (Math.random() - .5) * .8, vy: -0.6 - Math.random() * .9,
						life: 1400 + Math.random() * 900, size: 6 + Math.random() * 5,
						color: colors[Math.floor(Math.random() * colors.length)],
						type: ["sparkle", "star", "bubble"][Math.floor(Math.random() * 3)],
					});
				}
			}
		}
		s.raf = requestAnimationFrame(animateFestivalFx);
	}

	// 发光类元素清单：用"叠加"混合绘制，重叠处越叠越亮，像真的灯光
	const FX_GLOW_TYPES = {
		star: 1, sparkle: 1, ember: 1, sunbeam: 1, moonOrb: 1, sun: 1,
		shootingStar: 1, skyLantern: 1, lantern: 1, lanternString: 1,
	};
	// 平日通用元素里的"发光家族"（星/火花/爆芒/圆环/月牙）同样享受灯光效果
	function fxIsGlow(type, element) {
		if (type === "generic") {
			if (element && element.curve) return !!element.curve.g;   // 曲线家族：闪电/原子/星系/星座/波包/棱镜等标记 g 的发亮
			const f = element && element.family;
			return f === "star" || f === "spark" || f === "burst" || f === "ring" || f === "crescent";
		}
		return !!FX_GLOW_TYPES[type];
	}

	// 用当前颜色铺一圈柔光（发光类元素打底用，两个圆就有灯光感，开销极小）
	function drawGlow(ctx, r, alpha) {
		const prev = ctx.globalAlpha;
		ctx.globalAlpha = prev * alpha;
		ctx.beginPath();
		ctx.arc(0, 0, r, 0, Math.PI * 2);
		ctx.fill();
		ctx.globalAlpha = prev;
	}

	function drawFxParticles(s, t) {
		const type = s.type, ctx = s.ctx, W = s.W, H = s.H;
		const rise = fxRise(type, s.element);
		const still = fxStill(type, s.element);
		const drift = type === "cloud";
		const speed = (type === "rain" ? 4.5 : (type === "shootingStar" ? 2.6 : 1)) * (s.speedMul || 1);
		// 当前鼠标互动预设（1792 种里的一种）：力场 + 点击 + 拖尾 + 可选看板郎力场
		const mf = s.mouseFx || { move: "push", str: 1, waifu: null };
		// 看板郎力场锚点：带 waifu 字段的预设才取角色中心（避免每帧白算 getBoundingClientRect）
		const waifuField = mf.waifu ? waifuCenter() : null;
		// 点击涟漪：从点击处向外扩散的一圈推力波（shockwave 大涟漪更快更远），寿命到自然消散
		let ripple = null;
		if (s.ripple) {
			const life = s.ripple.big ? 900 : 600;
			const age = (t - s.ripple.born) / life;
			if (age >= 1) s.ripple = null;
			else ripple = { cx: s.ripple.x, cy: s.ripple.y, rr: s.ripple.big ? 70 + age * 320 : 20 + age * 170, fade: 1 - age, band: s.ripple.big ? 70 : 42 };
		}
		for (const q of s.parts) {
			q.x += drift ? 0.25 : q.vx + Math.sin(t / 700 + q.phase) * 0.3;
			q.y += rise ? -q.vy * 0.55 * (s.speedMul || 1) : (still || drift ? 0 : q.vy * speed);
			// 鼠标互动：按当前预设的力场响应光标（推开/吸附/环绕/涡旋/弹簧……共 14 种），
			// 力场函数自己负责点亮（q.glow）和冻结（q.frost）等副作用
			q.glow = 0;
			{
				const dx = q.x - s.mx, dy = q.y - s.my;
				const d2 = dx * dx + dy * dy;
				if (d2 < 16900 && d2 > 0.01) {
					const d = Math.sqrt(d2);
					const near = 1 - d / 130;
					const fn = MOUSE_MOVES[mf.move] || MOUSE_MOVES.push;
					fn(q, dx, dy, d, near, s, mf);
				}
			}
			// 看板郎力场（约 1/3 的互动预设带）：well = 粒子绕着角色公转，aura = 角色周围被点亮
			if (waifuField) {
				const dx = q.x - waifuField.x, dy = q.y - waifuField.y;
				const d2 = dx * dx + dy * dy;
				if (mf.waifu === "well") {
					const d = Math.sqrt(d2) || 1;
					if (d > 30 && d < 480) {
						const near = Math.max(0.15, 1 - Math.abs(d - 210) / 210);   // 越贴近 210px 轨道受力越强
						const f = near * 1.35;
						const err = (210 - d) * 0.018;                              // 径向修正：把粒子拉回轨道
						q.x += (-(dy / d) * 0.9 + (dx / d) * err) * f;               // 切向 = 公转方向
						q.y += ((dx / d) * 0.9 + (dy / d) * err) * f;
						q.glow = Math.max(q.glow, f * 0.45);
					}
				} else if (d2 < 62500) {   // aura：角色周围 250px 内的粒子被点亮，像角色自带光环
					q.glow = Math.max(q.glow, 1 - Math.sqrt(d2) / 250);
				}
			}
			// 点击涟漪推力波
			if (ripple) {
				const dx = q.x - ripple.cx, dy = q.y - ripple.cy;
				const d = Math.sqrt(dx * dx + dy * dy) || 1;
				const band = Math.abs(d - ripple.rr);
				if (band < ripple.band) {
					const f = (1 - band / ripple.band) * 3.4 * ripple.fade;
					q.x += (dx / d) * f;
					q.y += (dy / d) * f;
				}
			}
			// 飘出可视区就从另一头补回来，特效一直持续、不会越放越空
			if (rise && q.y < -40) { q.y = H + 30; q.x = Math.random() * W; }
			else if (!rise && !still && !drift && q.y > H + 40) { q.y = -40; q.x = Math.random() * W; }
			if (q.x < -70) q.x = W + 60;
			else if (q.x > W + 70) q.x = -60;
			q.rot += q.vr * (1 + (q.glow || 0) * 2);   // 靠近光标的粒子转得更快
			ctx.save();
			ctx.translate(q.x, q.y);
			ctx.rotate(q.rot);
			ctx.fillStyle = q.color;
			if (still) ctx.globalAlpha *= 0.45 + 0.55 * Math.abs(Math.sin(t / 320 + q.phase));
			if (q.twinkle) {   // 星光领域：点击处附近的粒子在时限内疯狂闪烁
				if (t > q.twinkle) q.twinkle = 0;
				else ctx.globalAlpha *= 0.35 + 0.65 * Math.abs(Math.sin(t / 60 + q.phase));
			}
			if (q.frost) {     // 冻结余韵：粒子被冰过之后泛蓝白色，随时间缓慢融化
				ctx.fillStyle = "#d0ebff";
				ctx.globalAlpha = Math.min(1, ctx.globalAlpha * (1 + q.frost * 0.5));
				q.frost *= 0.96;
				if (q.frost < 0.02) q.frost = 0;
			}
			if (q.glow) ctx.globalAlpha = Math.min(1, ctx.globalAlpha * (1 + q.glow * 0.4));   // 悬停点亮
			if (fxIsGlow(type, q.el)) ctx.globalCompositeOperation = "lighter";   // 灯光元素叠色，重叠处更亮
			drawFxShape(ctx, type, q);
			ctx.restore();
		}
		// 鼠标速度随帧衰减，停下后推力回落
		s.ms *= 0.94;
	}

	// 临时粒子（光标拖尾/点击迸发/角色呼出）：独立于常驻粒子，带速度、重力和寿命。
	// 单独成函数：烟花模式下也要画（拖尾/点击/角色互动在烟花特效下同样生效）
	function drawTempParticles(s, t) {
		if (!s.temp || !s.temp.length) { s.prevT = t; return; }
		const ctx = s.ctx;
		const dt = Math.min(50, t - (s.prevT || t));   // 帧间隔（ms），切后台回来不超过 50ms 防跳变
		s.prevT = t;
		const k = dt / 16.7;                            // 归一到 60fps 的步长倍率
		for (let i = s.temp.length - 1; i >= 0; i--) {
			const p = s.temp[i];
			p.age += dt;
			if (p.age >= p.life) { s.temp.splice(i, 1); continue; }
			p.vy += p.g * k;
			p.x += p.vx * k;
			p.y += p.vy * k;
			p.rot += p.vr * k;
			const prog = p.age / p.life;                // 出生 15% 内淡入，之后一路淡出
			ctx.save();
			ctx.translate(p.x, p.y);
			ctx.rotate(p.rot);
			ctx.fillStyle = p.color;
			ctx.globalAlpha *= prog < 0.15 ? prog / 0.15 : 1 - (prog - 0.15) / 0.85;
			drawFxShape(ctx, p.type, p);
			ctx.restore();
		}
	}

	function drawFxShape(ctx, type, q) {
		if (type === "generic") { drawGenericElement(ctx, q); return; }
		if (type === "confetti") drawConfetti(ctx, q);
		else if (type === "ribbon") drawRibbon(ctx, q);
		else if (type === "balloon") drawBalloon(ctx, q);
		else if (type === "petal") drawPetal(ctx, q);
		else if (type === "heart") drawHeart(ctx, q);
		else if (type === "lantern") drawLantern(ctx, q);
		else if (type === "skyLantern") drawSkyLantern(ctx, q);
		else if (type === "moonOrb") drawMoonOrb(ctx, q);
		else if (type === "leaf") drawLeaf(ctx, q);
		else if (type === "maple") drawMaple(ctx, q);
		else if (type === "snow") drawSnow(ctx, q);
		else if (type === "snowflake") drawSnowflake(ctx, q);
		else if (type === "star") drawStar(ctx, q);
		else if (type === "sparkle") drawSparkle(ctx, q);
		else if (type === "bubble") drawBubble(ctx, q);
		else if (type === "sunbeam") drawSunbeam(ctx, q);
		else if (type === "flag") drawFlag(ctx, q);
		else if (type === "gift") drawGift(ctx, q);
		else if (type === "bell") drawBell(ctx, q);
		else if (type === "pumpkin") drawPumpkin(ctx, q);
		else if (type === "snowman") drawSnowman(ctx, q);
		else if (type === "firecracker") drawFirecracker(ctx, q);
		else if (type === "lanternString") drawLanternString(ctx, q);
		else if (type === "dumpling") drawDumpling(ctx, q);
		else if (type === "mooncake") drawMooncake(ctx, q);
		else if (type === "zongzi") drawZongzi(ctx, q);
		else if (type === "jack") drawJack(ctx, q);
		else if (type === "kite") drawKite(ctx, q);
		else if (type === "chrysanthemum") drawChrysanthemum(ctx, q);
		else if (type === "shootingStar") drawShootingStar(ctx, q);
		else if (type === "sun") drawSun(ctx, q);
		else if (type === "rain") drawRain(ctx, q);
		else if (type === "cloud") drawCloud(ctx, q);
		else if (type === "candy") drawCandy(ctx, q);
		else if (type === "ghost") drawGhost(ctx, q);
		else if (type === "redPacket") drawRedPacket(ctx, q);
		else if (type === "riceCake") drawRiceCake(ctx, q);
		else if (type === "tanghulu") drawTanghulu(ctx, q);
		else if (type === "airplane") drawAirplane(ctx, q);
		else if (type === "suitcase") drawSuitcase(ctx, q);
		else if (type === "zzz") drawZzz(ctx, q);
		else drawEmber(ctx, q);
	}

	// ===== 880 个曲线家族的绘制引擎 =====
	// 每个家族的 curve 定义先展开成"原始坐标"的图元（折线/线段/圆点/矩形），
	// 再按全局最大半径归一化到单位圆内、统一旋转缩放后写入 Path2D；
	// Path2D 按（家族, 参数）烘焙缓存，绘制时每帧只做平移旋转缩放 + fill/stroke。
	function fxCurveGcd(a, b) { while (b) { const t = a % b; a = b; b = t; } return a || 1; }

	// 各曲线家族 → 图元列表（坐标未归一化，最外层统一处理）
	function curvePrims(c) {
		const prims = [];
		const P = (pts, close) => prims.push({ k: "p", pts, close });
		const L = (x1, y1, x2, y2) => prims.push({ k: "l", x1, y1, x2, y2 });
		const D = (x, y, r) => prims.push({ k: "d", x, y, r });
		switch (c.t) {
			case "super": {   // Gielis 超级公式：一组 m/n 就是一朵完全不同的花
				const pts = [];
				for (let i = 0; i <= 200; i++) {
					const t = Math.PI * 2 * i / 200;
					const t1 = Math.pow(Math.abs(Math.cos(c.m * t / 4)), c.n2);
					const t2 = Math.pow(Math.abs(Math.sin(c.m * t / 4)), c.n3);
					const r = Math.pow(t1 + t2, -1 / c.n1);
					pts.push([r * Math.cos(t), r * Math.sin(t)]);
				}
				P(pts, true);
				break;
			}
			case "star": {   // 星形多边形 {p/q}：连完一圈正好回到起点，gcd>1 时是多条闭合折线
				const done = new Array(c.p).fill(false);
				for (let v0 = 0; v0 < c.p; v0++) {
					if (done[v0]) continue;
					const pts = [];
					let v = v0;
					do {
						done[v] = true;
						const a = Math.PI * 2 * v / c.p - Math.PI / 2;
						pts.push([Math.cos(a), Math.sin(a)]);
						v = (v + c.q) % c.p;
					} while (v !== v0);
					P(pts, true);
				}
				break;
			}
			case "hypo": {   // 内摆线（万花尺）
				const loops = c.r / fxCurveGcd(c.R, c.r);
				const T = Math.min(520, Math.max(140, Math.ceil(110 * loops)));
				const k = c.R - c.r, pts = [];
				for (let i = 0; i <= T; i++) {
					const t = Math.PI * 2 * loops * i / T;
					pts.push([k * Math.cos(t) + c.d * Math.cos(k * t / c.r), k * Math.sin(t) - c.d * Math.sin(k * t / c.r)]);
				}
				P(pts, true);
				break;
			}
			case "epi": {   // 外摆线：心形线、肾脏线、毛茛线一族
				const loops = c.r / fxCurveGcd(c.R, c.r);
				const T = Math.min(520, Math.max(140, Math.ceil(120 * loops)));
				const k = c.R + c.r, pts = [];
				for (let i = 0; i <= T; i++) {
					const t = Math.PI * 2 * loops * i / T;
					pts.push([k * Math.cos(t) - c.d * Math.cos(k * t / c.r), k * Math.sin(t) - c.d * Math.sin(k * t / c.r)]);
				}
				P(pts, true);
				break;
			}
			case "rose": {   // 玫瑰线 r = cos(pθ/q)：θ 扫满 2π·q 一定闭合（多走的部分是重描）
				const q = c.q || 1, pts = [];
				const T = Math.min(560, Math.max(180, 90 * q));
				for (let i = 0; i <= T; i++) {
					const t = Math.PI * 2 * q * i / T;
					const r = Math.cos(c.p * t / q);
					pts.push([r * Math.cos(t), r * Math.sin(t)]);
				}
				P(pts, true);
				break;
			}
			case "liss": {   // 利萨茹曲线
				const pts = [];
				for (let i = 0; i <= 220; i++) {
					const t = Math.PI * 2 * i / 220;
					pts.push([Math.sin(c.a * t + (c.ph || 0)), Math.sin(c.b * t)]);
				}
				P(pts, true);
				break;
			}
			case "maurer": {   // Maurer 玫瑰星网：固定步长 d° 连 361 个点
				const pts = [];
				for (let k = 0; k <= 360; k++) {
					const t = c.d * Math.PI / 180 * k;
					const r = Math.cos(c.n * t);
					pts.push([r * Math.cos(t), r * Math.sin(t)]);
				}
				P(pts, false);
				break;
			}
			case "aspi": {   // 螺线一族：阿基米德 / 对数 / 费马 / 菊石
				if (c.kind === "ammon") {
					const b = c.b || 0.22, turn = Math.PI * 2 * 2.4, pts = [];
					for (let i = 0; i <= 260; i++) {
						const t = turn * i / 260;
						const r = Math.exp(b * t) / Math.exp(b * turn);
						pts.push([r * Math.cos(t), r * Math.sin(t)]);
					}
					P(pts, false);
					for (let i = 1; i <= 9; i++) {   // 隔壁：越过分室的径向短线
						const t = turn * i / 10, r = Math.exp(b * t) / Math.exp(b * turn);
						L(r * Math.cos(t) * 0.5, r * Math.sin(t) * 0.5, r * Math.cos(t), r * Math.sin(t));
					}
				} else {
					const turns = c.turns || 3, T = Math.min(460, 90 * turns), pts = [];
					for (let i = 0; i <= T; i++) {
						const t = Math.PI * 2 * turns * i / T, u = i / T;
						let r;
						if (c.kind === "log") r = Math.exp((c.b || 0.25) * t) / Math.exp((c.b || 0.25) * Math.PI * 2 * turns);
						else if (c.kind === "fermat") r = Math.sqrt(u);
						else r = u;
						pts.push([r * Math.cos(t), r * Math.sin(t)]);
					}
					P(pts, false);
					if (c.kind !== "log") for (let i = 0; i < 3; i++) {   // 三根辐条，风车感
						const a = Math.PI * 2 * i / 3;
						L(0, 0, Math.cos(a) * 0.45, Math.sin(a) * 0.45);
					}
				}
				break;
			}
			case "wavepoly": {   // 圆形/多边形边界上叠一圈正弦波
				const T = 260, base = c.base || 0, bumps = c.bumps || 6, amp = c.amp || 0.22, pts = [];
				for (let i = 0; i <= T; i++) {
					const t = Math.PI * 2 * i / T;
					let r;
					if (base) {
						const seg = Math.PI * 2 / base;
						const m = ((t % seg) + seg) % seg;
						r = Math.cos(seg / 2) / Math.cos(m - seg / 2) + amp * Math.sin(bumps * t);
					} else r = 1 + amp * Math.sin(bumps * t);
					pts.push([r * Math.cos(t), r * Math.sin(t)]);
				}
				P(pts, true);
				break;
			}
			case "sunflo": {   // 向日葵种子盘：黄金角 137.5° 逐点排布
				const cnt = c.count || 80, GA = Math.PI * (3 - Math.sqrt(5)), pts = [];
				for (let i = 0; i < cnt; i++) {
					const r = Math.sqrt((i + 0.5) / cnt), t = i * GA;
					const x = r * Math.cos(t), y = r * Math.sin(t);
					D(x, y, 0.32 / Math.sqrt(cnt) * (1.6 - r));
					pts.push([x, y]);
				}
				if (c.spiral) P(pts, false);   // 把种子串成螺旋折线
				break;
			}
			case "bolt": {   // 闪电：主通道 + 分叉
				let seed = c.seed || 1;
				const rnd = () => { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; };
				const pts = [[0, -1]];
				for (let i = 1; i <= 5; i++) pts.push([(rnd() - 0.5) * 1.6 * (1 - i / 7), -1 + 2 * i / 5]);
				P(pts, false);
				for (let f = 0; f < (c.forks || 2); f++) {
					const at = 1 + Math.floor(rnd() * 3);
					const [x0, y0] = pts[at];
					P([[x0, y0], [x0 + (rnd() - 0.5) * 1.1, y0 + 0.25], [x0 + (rnd() - 0.5) * 1.4, y0 + 0.5]], false);
				}
				break;
			}
			case "helix": {   // DNA 双螺旋：两条链 + 碱基横档
				const tw = c.twists || 2, a1 = [], a2 = [];
				for (let i = 0; i <= 150; i++) {
					const x = -1 + 2 * i / 150;
					const y = Math.sin(x * Math.PI * tw) * 0.5;
					a1.push([x, y]); a2.push([x, -y]);
				}
				P(a1, false); P(a2, false);
				for (let i = 0; i <= 6; i++) {
					const x = -1 + 2 * i / 6;
					const y = Math.sin(x * Math.PI * tw) * 0.5;
					L(x, y, x, -y);
				}
				break;
			}
			case "benzene": {   // 苯环：六边形 + 内圈，可加顶点电子与内接六边形
				const hex = [];
				for (let i = 0; i < 6; i++) { const a = Math.PI * i / 3; hex.push([Math.cos(a), Math.sin(a)]); }
				P(hex, true);
				D(0, 0, c.inner || 0.45);
				if (c.dots) for (let i = 0; i < 6; i++) { const a = Math.PI * i / 3; D(Math.cos(a), Math.sin(a), 0.12); }
				if (c.inner2) {
					const inner = [];
					for (let i = 0; i < 6; i++) { const a = Math.PI * i / 3 + Math.PI / 6; inner.push([Math.cos(a) * 0.58, Math.sin(a) * 0.58]); }
					P(inner, true);
				}
				break;
			}
			case "mol": {   // 分子：几个原子圆 + 化学键连线
				let seed = c.seed || 1;
				const rnd = () => { seed = (seed * 7919 + 17) % 104729; return seed / 104729; };
				const atoms = [];
				for (let i = 0; i < 4; i++) atoms.push([(rnd() - 0.5) * 1.6, (rnd() - 0.5) * 1.6]);
				for (let i = 1; i < atoms.length; i++) L(atoms[i - 1][0], atoms[i - 1][1], atoms[i][0], atoms[i][1]);
				for (const a of atoms) D(a[0], a[1], 0.24);
				break;
			}
			case "atom": {   // 卢瑟福椭圆轨道 / 玻尔圆轨道 + 电子
				if (c.kind === "bohr") {
					const n = c.n || 3;
					for (let i = 1; i <= n; i++) D(0, 0, i / n);
					D(0, 0, 0.14);
					for (let i = 1; i <= n; i++) { const a = i * 2.4; D(Math.cos(a) * i / n, Math.sin(a) * i / n, 0.07); }
				} else {
					const orbits = c.orbits || 3;
					for (let i = 0; i < orbits; i++) {
						const rot = Math.PI * i / orbits, pts = [];
						for (let j = 0; j <= 60; j++) {
							const t = Math.PI * 2 * j / 60;
							const ex = Math.cos(t), ey = Math.sin(t) * 0.38;
							pts.push([ex * Math.cos(rot) - ey * Math.sin(rot), ex * Math.sin(rot) + ey * Math.cos(rot)]);
						}
						P(pts, true);
					}
					D(0, 0, 0.15);
					for (let i = 0; i < orbits; i++) {
						const a = Math.PI * 2 * i / orbits + 0.7;
						D(Math.cos(a), Math.sin(a) * 0.38, 0.07);
					}
				}
				break;
			}
			case "wpacket": {   // 电磁波包：一段正弦 + 高斯包络线
				const f = c.f || 5, env = c.env || 1.5, wave = [], top = [], bot = [];
				for (let i = 0; i <= 150; i++) {
					const x = -1 + 2 * i / 150;
					const e = Math.exp(-env * x * x);
					wave.push([x, Math.sin(x * Math.PI * f) * 0.5 * e]);
					top.push([x, 0.6 * e]); bot.push([x, -0.6 * e]);
				}
				P(wave, false); P(top, false); P(bot, false);
				break;
			}
			case "constel": {   // 星座：几个亮点连线
				let seed = c.seed || 1;
				const rnd = () => { seed = (seed * 353 + 17) % 4096; return seed / 4096; };
				const stars = [];
				for (let i = 0; i < 7; i++) stars.push([(rnd() - 0.5) * 1.9, (rnd() - 0.5) * 1.9]);
				P(stars, false);
				for (const s of stars) D(s[0], s[1], 0.06);
				break;
			}
			case "matrix": {   // 像素点阵：随机点亮的方格
				let seed = c.seed || 1;
				const rnd = () => { seed = (seed * 137 + 91) % 4096; return seed / 4096; };
				const n = c.size || 4;
				for (let r = 0; r < n; r++) for (let col = 0; col < n; col++) {
					if (rnd() < 0.45) continue;
					prims.push({ k: "r", x: -1 + 2 * (col + 0.5) / n, y: -1 + 2 * (r + 0.5) / n, w: 1.7 / n, h: 1.7 / n });
				}
				break;
			}
			case "butterfly": {   // 蝴蝶曲线（Fay）：r = e^cosθ − 2cos4θ + sin^5(θ/12)
				const pts = [];
				for (let i = 0; i <= 480; i++) {
					const t = Math.PI * 24 * i / 480;
					const r = Math.exp(Math.cos(t)) - 2 * Math.cos(4 * t) + Math.pow(Math.sin(t / 12), 5);
					pts.push([r * Math.sin(t), -r * Math.cos(t)]);
				}
				P(pts, true);
				if (c.wings) { L(-0.25, 0.72, -0.55, 0.95); L(0.25, 0.72, 0.55, 0.95); }   // 触角
				break;
			}
			case "cassini": {   // 卡西尼卵形线：r² = a²cos2θ + sqrt(1 − a⁴sin²2θ)
				const a = c.a || 0.6, pts = [];
				for (let i = 0; i <= 240; i++) {
					const t = Math.PI * 2 * i / 240;
					const r = Math.sqrt(Math.max(0, a * a * Math.cos(2 * t) + Math.sqrt(Math.max(0, 1 - Math.pow(a, 4) * Math.pow(Math.sin(2 * t), 2)))));
					pts.push([r * Math.cos(t), r * Math.sin(t)]);
				}
				P(pts, true);
				break;
			}
			case "lemn": {   // 伯努利双纽线：两瓣无穷
				const lobes = [[], []];
				for (let i = 0; i <= 120; i++) {
					const t = -Math.PI / 4 + Math.PI / 2 * i / 120;
					const r = Math.sqrt(Math.max(0, Math.cos(2 * t)));
					lobes[0].push([r * Math.cos(t), r * Math.sin(t)]);
					lobes[1].push([-r * Math.cos(t), -r * Math.sin(t)]);
				}
				P(lobes[0], true); P(lobes[1], true);
				break;
			}
			case "knot": {   // 纽结投影：两个圆频率叠加出三叶/五瓣结
				const pts = [];
				for (let i = 0; i <= 240; i++) {
					const t = Math.PI * 2 * i / 240;
					pts.push([Math.sin(c.p * t) + 0.55 * Math.sin(c.q * t), Math.cos(c.p * t) + 0.55 * Math.cos(c.q * t)]);
				}
				P(pts, true);
				break;
			}
			case "tear": {   // 泪滴（立式心形线）/ 蛋形
				const pts = [];
				for (let i = 0; i <= 180; i++) {
					const t = Math.PI * 2 * i / 180;
					if (c.kind === "egg") pts.push([Math.cos(t), 1.15 * Math.sin(t) * (1 + 0.14 * Math.cos(t))]);
					else pts.push([(1 + 0.92 * Math.sin(t)) * Math.cos(t), (1 + 0.92 * Math.sin(t)) * Math.sin(t)]);
				}
				P(pts, true);
				break;
			}
			case "clock": {   // 钟面（指针停在 10:08）/ 方齿齿轮 + 轴孔
				if (c.kind === "cog") {
					const teeth = c.teeth || 9, pts = [];
					for (let i = 0; i < teeth * 2; i++) {
						const a = Math.PI * i / teeth;
						const r = i % 2 === 0 ? 1 : 0.78;
						pts.push([Math.cos(a) * r, Math.sin(a) * r]);
					}
					P(pts, true);
					D(0, 0, 0.3);
				} else {
					D(0, 0, 1);
					const tk = c.ticks || 12;
					for (let i = 0; i < tk; i++) {
						const a = Math.PI * 2 * i / tk;
						L(Math.cos(a) * 0.82, Math.sin(a) * 0.82, Math.cos(a) * 0.95, Math.sin(a) * 0.95);
					}
					L(0, 0, 0.45, -0.3);
					L(0, 0, -0.38, 0.6);
					D(0, 0, 0.07);
				}
				break;
			}
			case "arch": {   // 拱桥：桥面 + 拱圈 + 吊杆
				const spans = c.spans || 1, deck = 0.55;
				L(-1, deck, 1, deck);
				for (let s = 0; s < spans; s++) {
					const x0 = -1 + 2 * s / spans, x1 = -1 + 2 * (s + 1) / spans;
					const w = (x1 - x0) / 2, cx = x0 + w, dip = Math.min(0.9, w * 1.7);
					const pts = [];
					for (let i = 0; i <= 40; i++) {
						const t = Math.PI * i / 40;
						pts.push([cx - w * Math.cos(t), deck - dip * Math.sin(t)]);
					}
					P(pts, false);
					for (let i = 1; i <= 3; i++) {
						const t = Math.PI * i / 4;
						const bx = cx - w * Math.cos(t), by = deck - dip * Math.sin(t);
						L(bx, by, bx, deck);
					}
				}
				break;
			}
			case "circuit": {   // 电路走线：直角折线 + 焊点
				let seed = c.seed || 1;
				const rnd = () => { seed = (seed * 541 + 29) % 4096; return seed / 4096; };
				for (let tr = 0; tr < 3; tr++) {
					let x = -1 + rnd() * 0.6, y = -1 + rnd() * 0.8;
					const pts = [[x, y]];
					for (let b = 0; b < 3; b++) {
						if (b % 2 === 0) x = rnd() * 1.9 - 0.95; else y = rnd() * 1.9 - 0.95;
						pts.push([x, y]);
					}
					P(pts, false);
					D(pts[0][0], pts[0][1], 0.08);
					D(x, y, 0.08);
				}
				break;
			}
			case "abacus": {   // 算盘：框 + 中梁 + 档 + 算珠
				const rods = c.rods || 2;
				prims.push({ k: "r", x: 0, y: 0, w: 2, h: 1.7 });
				L(-1, 0.28, 1, 0.28);
				for (let i = 0; i < rods; i++) {
					const x = -1 + 2 * (i + 0.5) / rods;
					L(x, -0.85, x, 0.85);
					for (let b = 0; b < 2; b++) D(x, 0.56 - b * 0.24, 0.11);
					for (let b = 0; b < 3; b++) D(x, -0.18 - b * 0.28, 0.11);
				}
				break;
			}
			case "plot": {   // 小黑板：坐标轴 + 经典函数 / 单摆
				if (c.kind === "pend") {
					D(0, -0.9, 0.08);
					const len = 1.55, arc = [];
					for (let i = 0; i <= 60; i++) {
						const a = Math.PI * (4 / 3 + (2 / 3) * i / 60);   // 悬点下方的摆弧
						arc.push([Math.cos(a) * len * 0.85, -0.9 + Math.sin(a) * len * 0.85]);
					}
					P(arc, false);
					const a = Math.PI * (4 / 3 + 0.18);   // 摆到左下
					const bx = Math.cos(a) * len, by = -0.9 + Math.sin(a) * len;
					L(0, -0.9, bx, by);
					D(bx, by, 0.16);
				} else {
					L(-0.95, -0.95, -0.95, 0.95);
					L(-0.95, -0.95, 0.98, -0.95);
					const pts = [];
					for (let i = 0; i <= 120; i++) {
						const x = -0.95 + 1.93 * i / 120, u = i / 120;
						let y;
						if (c.kind === "sine") y = 0.75 * Math.sin(u * Math.PI * 2);
						else if (c.kind === "gauss") y = -0.95 + 1.75 * Math.exp(-3 * (u - 0.5) * (u - 0.5));
						else if (c.kind === "parab") y = -0.95 + 3.2 * (u - 0.5) * (u - 0.5);
						else y = 2.2 * Math.pow(u - 0.5, 3) + 0.3 * (u - 0.5);
						pts.push([x, y]);
					}
					P(pts, false);
				}
				break;
			}
			case "prism": {   // 三棱镜 + 色散光束
				const tri = [];
				for (let i = 0; i < 3; i++) { const a = Math.PI * 2 * i / 3 + Math.PI / 2; tri.push([Math.cos(a) * 0.7, Math.sin(a) * 0.7]); }
				P(tri, true);
				L(-1, -0.5, -0.22, -0.24);   // 入射光
				const rays = c.rays || 6;
				for (let i = 0; i < rays; i++) {
					const a = -0.35 + 0.7 * i / Math.max(1, rays - 1);
					L(0.2, 0.12, 1, 0.12 + a * 1.05);
				}
				break;
			}
			case "apple": {   // 苹果：果身 + 果柄 + 一片叶
				const body = [];
				for (let i = 0; i <= 60; i++) {
					const t = Math.PI * 2 * i / 60;
					const r = 0.85 * (1 + 0.08 * Math.cos(2 * t));
					body.push([Math.sin(t) * r, Math.cos(t) * r * 0.92]);
				}
				P(body, true);
				L(0, 0.78, 0.1, 1);
				P([[0.06, 0.93], [0.5, 0.83], [0.34, 0.55], [0.06, 0.72]], true);
				break;
			}
			case "galaxy": {   // 星系：对数螺线旋臂
				const arms = c.arms || 2;
				D(0, 0, 0.1);
				for (let a = 0; a < arms; a++) {
					const pts = [];
					for (let i = 0; i <= 70; i++) {
						const t = i / 70;
						const th = t * 3.1 + Math.PI * 2 * a / arms;
						const r = Math.exp(1.1 * t) / Math.exp(1.1);
						pts.push([r * Math.cos(th), r * Math.sin(th)]);
					}
					P(pts, false);
				}
				break;
			}
			case "compass": {   // 罗盘玫瑰：四长四短的菱形尖 + 中心
				for (let i = 0; i < 8; i++) {
					const a = Math.PI * 2 * i / 8;
					const long = i % 2 === 0 ? 1 : 0.55, w = 0.16;
					P([
						[Math.cos(a) * long, Math.sin(a) * long],
						[Math.cos(a + Math.PI / 2) * w, Math.sin(a + Math.PI / 2) * w],
						[Math.cos(a) * -0.16, Math.sin(a) * -0.16],
						[Math.cos(a - Math.PI / 2) * w, Math.sin(a - Math.PI / 2) * w],
					], true);
				}
				D(0, 0, 0.14);
				break;
			}
			case "honey": {   // 蜂巢：中心 + 六个邻接六边形，正好拼满
				const hex = (cx, cy) => {
					const pts = [];
					for (let i = 0; i < 6; i++) { const a = Math.PI * i / 3; pts.push([cx + Math.cos(a) * 0.5, cy + Math.sin(a) * 0.5]); }
					P(pts, true);
				};
				hex(0, 0);
				for (let i = 0; i < 6; i++) { const a = Math.PI * i / 3 + Math.PI / 6; hex(Math.cos(a) * 0.866, Math.sin(a) * 0.866); }
				break;
			}
			case "dend": {   // 雪晶：多向主干 + 分叉，可有中心六边形
				const arms = c.arms || 6, rings = c.depth || 1;
				for (let i = 0; i < arms; i++) {
					const a = Math.PI * 2 * i / arms;
					L(0, 0, Math.cos(a), Math.sin(a));
					for (let b = 0; b < rings; b++) {
						const r = 0.5 + b * 0.28, len = 0.26 - b * 0.08;
						const bx = Math.cos(a) * r, by = Math.sin(a) * r;
						L(bx, by, bx + Math.cos(a + 0.6) * len, by + Math.sin(a + 0.6) * len);
						L(bx, by, bx + Math.cos(a - 0.6) * len, by + Math.sin(a - 0.6) * len);
					}
				}
				if (c.hex) D(0, 0, 0.2);
				break;
			}
			case "mandala": {   // 曼陀罗：花瓣圈与圆点圈交替向外
				const rings = c.rings || 3;
				for (let ring = 0; ring < rings; ring++) {
					const r = (ring + 1) / rings, count = 8 + ring * 4;
					if ((ring + (c.dots ? 1 : 0)) % 2 === 0) {
						for (let i = 0; i < count; i++) {
							const a = Math.PI * 2 * i / count;
							const pr = 0.5 / rings, pts = [];
							for (let j = 0; j <= 12; j++) {
								const t = Math.PI * 2 * j / 12;
								pts.push([Math.cos(a) * r + Math.cos(t) * pr, Math.sin(a) * r + Math.sin(t) * pr * 0.6]);
							}
							P(pts, true);
						}
					} else {
						for (let i = 0; i < count; i++) {
							const a = Math.PI * 2 * i / count;
							D(Math.cos(a) * r, Math.sin(a) * r, 0.3 / rings);
						}
					}
				}
				break;
			}
			case "pin": {   // 风车：弯叶片一片扣一片
				const blades = c.blades || 6;
				for (let i = 0; i < blades; i++) {
					const a = Math.PI * 2 * i / blades;
					const pts = [[0, 0]];
					for (let j = 0; j <= 10; j++) {
						const t = j / 10;
						pts.push([Math.cos(a + t * 1.15) * t, Math.sin(a + t * 1.15) * t]);
					}
					pts.push([Math.cos(a + 1.15) * 0.22, Math.sin(a + 1.15) * 0.22]);
					P(pts, true);
				}
				break;
			}
			case "sprout": {   // 嫩芽：茎 + 两片子叶，double 再添两片小叶
				L(0, 1, 0, -0.05);
				P([[0, -0.05], [0.8, -0.45], [0.14, -0.7], [0, -0.3]], true);
				P([[0, -0.05], [-0.8, -0.45], [-0.14, -0.7], [0, -0.3]], true);
				if (c.kind === "double") {
					P([[0, 0.4], [0.45, 0.2], [0.08, 0.05], [0, 0.22]], true);
					P([[0, 0.4], [-0.45, 0.2], [-0.08, 0.05], [0, 0.22]], true);
				}
				break;
			}
			case "cell": {   // 细胞：细胞膜 + 细胞核 + 细胞器
				const body = [];
				for (let i = 0; i <= 60; i++) {
					const t = Math.PI * 2 * i / 60;
					const r = 0.95 * (1 + 0.06 * Math.sin(3 * t) + 0.04 * Math.cos(5 * t));
					body.push([Math.cos(t) * r, Math.sin(t) * r]);
				}
				P(body, true);
				D(-0.2, 0.08, 0.26);
				let seed = c.seed || 1;
				const rnd = () => { seed = (seed * 77 + 13) % 4096; return seed / 4096; };
				for (let i = 0; i < 5; i++) D((rnd() - 0.5) * 1.1, (rnd() - 0.5) * 1.1, 0.06 + rnd() * 0.06);
				break;
			}
		}
		return prims;
	}

	// 把图元归一化 + 旋转缩放后写入 path（mul/rot 用于第二层嵌套副本）
	function traceCurve(path, c, mul, rot) {
		const prims = curvePrims(c);
		let mx = 0;
		for (const g of prims) {
			if (g.k === "d") mx = Math.max(mx, Math.hypot(g.x, g.y) + g.r);
			else if (g.k === "l") mx = Math.max(mx, Math.abs(g.x1), Math.abs(g.y1), Math.abs(g.x2), Math.abs(g.y2));
			else if (g.k === "r") mx = Math.max(mx, Math.abs(g.x) + g.w / 2, Math.abs(g.y) + g.h / 2);
			else for (const p of g.pts) mx = Math.max(mx, Math.abs(p[0]), Math.abs(p[1]));
		}
		const k = (mul || 1) / (mx || 1);
		const cs = Math.cos(rot || 0), sn = Math.sin(rot || 0);
		const T = (x, y) => {
			const rx = x * cs - y * sn, ry = x * sn + y * cs;
			return [rx * k, ry * k];
		};
		for (const g of prims) {
			if (g.k === "d") {
				const a = T(g.x, g.y), r = Math.max(0.01, g.r * k);
				path.moveTo(a[0] + r, a[1]);
				path.arc(a[0], a[1], r, 0, Math.PI * 2);
			} else if (g.k === "l") {
				const a = T(g.x1, g.y1), b = T(g.x2, g.y2);
				path.moveTo(a[0], a[1]); path.lineTo(b[0], b[1]);
			} else if (g.k === "r") {
				const a = T(g.x - g.w / 2, g.y - g.h / 2), b = T(g.x + g.w / 2, g.y + g.h / 2);
				path.moveTo(a[0], a[1]); path.lineTo(b[0], a[1]); path.lineTo(b[0], b[1]); path.lineTo(a[0], b[1]); path.closePath();
			} else {
				for (let i = 0; i < g.pts.length; i++) {
					const a = T(g.pts[i][0], g.pts[i][1]);
					if (i === 0) path.moveTo(a[0], a[1]); else path.lineTo(a[0], a[1]);
				}
				if (g.close) path.closePath();
			}
		}
	}

	// （家族, 参数）→ 烘焙好的 Path2D 缓存；同一时刻只有一两种元素在飞，超过 48 个就清一次
	const FX_CURVE_CACHE = new Map();
	function curvePathFor(el) {
		const key = el.family + "|" + el.param;
		let p = FX_CURVE_CACHE.get(key);
		if (p) return p;
		const path = new Path2D();
		traceCurve(path, el.curve, 1, 0);
		if (el.param >= 2) traceCurve(path, el.curve, 0.55, 0.44);   // 第二层：55% 缩放 + 25° 旋转
		if (FX_CURVE_CACHE.size > 48) FX_CURVE_CACHE.clear();
		FX_CURVE_CACHE.set(key, path);
		return path;
	}

	// 通用元素：按图形家族 + 参数 + 描边风格绘制，7032 种各有差别
	function drawGenericElement(ctx, q) {
		const el = q.el;
		if (!el) return;
		const s = q.size, n = el.param, style = el.style;
		const open = !!(el.curve && el.curve.open);   // 开放路径（闪电/桥/电路等）只描线，不做实心
		const filled = !open && (style === "fill" || style === "double" || style === "twoTone");
		// 880 个曲线家族：走 Path2D 缓存，绘制路径与旧家族分开
		if (el.curve) {
			if (el.curve.g && (style === "fill" || style === "outline")) drawGlow(ctx, s * 0.62, 0.2);
			const path = curvePathFor(el);
			ctx.save();
			ctx.scale(s * 0.5, s * 0.5);
			// 线宽随图形尺寸线性放大（scale 后再回除，让屏幕实际线宽 = s * 比例）：
			// 之前只占 6% 且保底 1px，图形越大线条相对越细，函数曲线糊成细丝看不清。
			// 实心/描边比 13%，开放路径（闪电/桥/电路/函数曲线等纯描线）比 21%，小图保底 1.8px。
			const strokeRatio = open ? 0.21 : 0.13;
			ctx.lineWidth = Math.max(1.8, s * strokeRatio) / (s * 0.5);
			if (style === "dashed") ctx.setLineDash([0.32, 0.24]);
			else if (style === "dotted") ctx.setLineDash([0.05, 0.2]);
			if (filled) ctx.fill(path);
			if (!filled || style === "double" || style === "twoTone") {
				ctx.strokeStyle = style === "twoTone" ? "rgba(255, 255, 255, .85)" : q.color;
				ctx.stroke(path);
			}
			ctx.setLineDash([]);
			ctx.restore();
			if (filled && style === "fill") {   // 实心曲线也补一点左上高光
				const prev = ctx.globalAlpha;
				ctx.globalAlpha = prev * 0.26;
				ctx.fillStyle = "#ffffff";
				ctx.beginPath();
				ctx.arc(-s * 0.14, -s * 0.16, s * 0.12, 0, Math.PI * 2);
				ctx.fill();
				ctx.globalAlpha = prev;
			}
			return;
		}
		// 发光家族（星/火花/爆芒/圆环/月牙）先铺柔光，配合叠色混合像真的小灯
		if ((el.family === "star" || el.family === "spark" || el.family === "burst" || el.family === "ring" || el.family === "crescent")
			&& (style === "fill" || style === "outline")) {
			drawGlow(ctx, s * 0.62, 0.2);
		}
		ctx.save();
		if (style === "dashed") ctx.setLineDash([s * 0.16, s * 0.12]);
		else if (style === "dotted") ctx.setLineDash([1.5, s * 0.1]);
		ctx.lineWidth = Math.max(1, s * 0.06);
		ctx.beginPath();
		switch (el.family) {
			case "poly":
				for (let i = 0; i < n; i++) {
					const a = (Math.PI * 2 * i) / n - Math.PI / 2;
					const x = Math.cos(a) * s * 0.48, y = Math.sin(a) * s * 0.48;
					if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
				}
				ctx.closePath();
				break;
			case "star":
				for (let i = 0; i < n * 2; i++) {
					const a = (Math.PI * i) / n - Math.PI / 2;
					const r = i % 2 === 0 ? s * 0.5 : s * 0.22;
					const x = Math.cos(a) * r, y = Math.sin(a) * r;
					if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
				}
				ctx.closePath();
				break;
			case "flower":
				for (let i = 0; i < n; i++) {
					const a = (Math.PI * 2 * i) / n;
					const px = Math.cos(a) * s * 0.3, py = Math.sin(a) * s * 0.3;
					ctx.moveTo(px, py);
					ctx.ellipse(px, py, s * 0.2, s * 0.1, a, 0, Math.PI * 2);
				}
				break;
			case "spark":
				for (let i = 0; i < n; i++) {
					const a = (Math.PI * 2 * i) / n;
					ctx.moveTo(0, 0);
					ctx.lineTo(Math.cos(a) * s * 0.5, Math.sin(a) * s * 0.5);
				}
				break;
			case "ring":
				for (let i = 1; i <= n; i++) ctx.arc(0, 0, (s * 0.5 * i) / n, 0, Math.PI * 2);
				break;
			case "dots":
				for (let i = 0; i < n; i++) {
					const a = (Math.PI * 2 * i) / n;
					const cx = Math.cos(a) * s * 0.42, cy = Math.sin(a) * s * 0.42;
					ctx.moveTo(cx + s * 0.07, cy);
					ctx.arc(cx, cy, s * 0.07, 0, Math.PI * 2);
				}
				break;
			case "wave":
				for (let i = 0; i < n; i++) {
					const y = -s * 0.4 + (s * 0.8 * i) / Math.max(1, n - 1);
					ctx.moveTo(-s * 0.45, y);
					ctx.quadraticCurveTo(0, y - s * 0.16, s * 0.45, y);
				}
				break;
			case "arc":
				for (let i = 0; i < n; i++) ctx.arc(0, 0, s * (0.2 + 0.3 * (i / n)), 0.3, Math.PI * 1.1);
				break;
			case "gear":
				for (let i = 0; i < n * 2; i++) {
					const a = (Math.PI * i) / n;
					const r = i % 2 === 0 ? s * 0.5 : s * 0.38;
					const x = Math.cos(a) * r, y = Math.sin(a) * r;
					if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
				}
				ctx.closePath();
				break;
			case "burst":
				for (let i = 0; i < n; i++) {
					const a = (Math.PI * 2 * i) / n;
					ctx.moveTo(Math.cos(a) * s * 0.16, Math.sin(a) * s * 0.16);
					ctx.lineTo(Math.cos(a) * s * 0.5, Math.sin(a) * s * 0.5);
				}
				break;
			case "diamond":
				for (let i = 0; i < n; i++) {
					const off = (i - (n - 1) / 2) * s * 0.18;
					ctx.moveTo(0, off - s * 0.2);
					ctx.lineTo(s * 0.16, off);
					ctx.lineTo(0, off + s * 0.2);
					ctx.lineTo(-s * 0.16, off);
					ctx.closePath();
				}
				break;
			case "cross":
				for (let i = 0; i < n; i++) {
					const a = (Math.PI * i) / n;
					ctx.moveTo(-Math.cos(a) * s * 0.5, -Math.sin(a) * s * 0.5);
					ctx.lineTo(Math.cos(a) * s * 0.5, Math.sin(a) * s * 0.5);
				}
				break;
			case "chevron":
				for (let i = 0; i < n; i++) {
					const y = -s * 0.35 + (s * 0.7 * i) / Math.max(1, n - 1);
					ctx.moveTo(-s * 0.35, y);
					ctx.lineTo(0, y + s * 0.16);
					ctx.lineTo(s * 0.35, y);
				}
				break;
			case "crescent":
				ctx.arc(0, 0, s * 0.46, 0, Math.PI * 2);
				ctx.arc(s * 0.12 * n, 0, s * Math.max(0.1, 0.42 - 0.04 * n), 0, Math.PI * 2, true);
				break;
			case "leaf":
				ctx.moveTo(0, -s * 0.46);
				ctx.quadraticCurveTo(s * (0.16 + 0.04 * n), 0, 0, s * 0.46);
				ctx.quadraticCurveTo(-s * (0.16 + 0.04 * n), 0, 0, -s * 0.46);
				break;
			case "heart":
				for (let i = 0; i < n; i++) {
					const off = (i - (n - 1) / 2) * s * 0.3;
					ctx.moveTo(off, s * 0.2);
					ctx.bezierCurveTo(off - s * 0.26, -s * 0.08, off - s * 0.1, -s * 0.32, off, -s * 0.08);
					ctx.bezierCurveTo(off + s * 0.1, -s * 0.32, off + s * 0.26, -s * 0.08, off, s * 0.2);
				}
				break;
			case "ribbon":
				for (let i = 0; i < n; i++) {
					const off = (i - (n - 1) / 2) * s * 0.16;
					ctx.moveTo(-s * 0.4, off);
					ctx.quadraticCurveTo(0, off - s * 0.3, s * 0.4, off);
					ctx.quadraticCurveTo(0, off - s * 0.1, -s * 0.4, off);
				}
				break;
			case "bubble":
				for (let i = 0; i < n; i++) ctx.arc(0, 0, s * (0.2 + 0.12 * i), 0, Math.PI * 2);
				break;
			case "square":
				for (let i = 0; i < n; i++) {
					const r = s * (0.2 + 0.12 * i);
					ctx.rect(-r, -r, r * 2, r * 2);
				}
				break;
			case "hex":
				for (let i = 0; i < 6; i++) {
					const a = (Math.PI * i) / 3;
					const x = Math.cos(a) * s * 0.45, y = Math.sin(a) * s * 0.45;
					if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
				}
				ctx.closePath();
				break;
			default:
				ctx.arc(0, 0, s * 0.4, 0, Math.PI * 2);
		}
		if (filled) ctx.fill();
		if (style === "fill") {
			// 左上高光：实心图形有受光面，不再是一块死色
			const prev = ctx.globalAlpha;
			ctx.globalAlpha = prev * 0.26;
			ctx.fillStyle = "#ffffff";
			ctx.beginPath();
			ctx.arc(-s * 0.14, -s * 0.16, s * 0.12, 0, Math.PI * 2);
			ctx.fill();
			ctx.globalAlpha = prev;
		}
		if (!filled || style === "double" || style === "twoTone") {
			ctx.strokeStyle = style === "twoTone" ? "rgba(255, 255, 255, .85)" : q.color;
			ctx.stroke();
		}
		ctx.setLineDash([]);
		ctx.restore();
	}

	// —— 各类特效的绘制细节：同一类里也混着几种形状，看着不单调 ——
	function drawConfetti(ctx, q) {
		const s = q.size;
		if (q.kind === 0) {
			// 纸片翻面：绕水平轴翻转的错觉，比一块死板的色块生动
			const flip = Math.max(0.22, Math.abs(Math.cos(q.rot * 2.2 + q.phase)));
			ctx.save();
			ctx.scale(1, flip);
			ctx.fillRect(-s / 2, -s / 4, s, s / 2);
			ctx.restore();
		} else if (q.kind === 1) {
			// 飘带：一条弯弯的细长纸带
			ctx.strokeStyle = q.color;
			ctx.lineWidth = 3;
			ctx.beginPath();
			ctx.moveTo(-s / 2, 0);
			ctx.quadraticCurveTo(0, -s / 2, s / 2, 0);
			ctx.stroke();
		} else {
			ctx.strokeStyle = q.color;
			ctx.lineWidth = 2;
			ctx.beginPath();
			ctx.arc(0, 0, s / 2.6, 0, Math.PI * 2);
			ctx.stroke();
		}
	}

	function drawPetal(ctx, q) {
		const s = q.size;
		if (q.kind === 0) {
			ctx.beginPath();
			ctx.ellipse(0, 0, s / 2, s / 3.4, 0, 0, Math.PI * 2);
			ctx.fill();
			// 浅色描边，花瓣有通透感
			ctx.save();
			ctx.globalAlpha *= 0.35;
			ctx.strokeStyle = "#ffffff";
			ctx.lineWidth = 1;
			ctx.stroke();
			ctx.restore();
		} else if (q.kind === 1) {
			// 心形花瓣：两段曲线合成一片
			ctx.beginPath();
			ctx.moveTo(0, s / 2);
			ctx.quadraticCurveTo(s / 2, 0, 0, -s / 2);
			ctx.quadraticCurveTo(-s / 2, 0, 0, s / 2);
			ctx.fill();
		} else {
			ctx.beginPath();
			ctx.arc(0, 0, s / 6, 0, Math.PI * 2);
			ctx.fill();
		}
	}

	function drawLantern(ctx, q) {
		const s = q.size;
		ctx.save();
		ctx.globalAlpha *= 0.3;
		ctx.beginPath();
		ctx.arc(0, 0, s, 0, Math.PI * 2);   // 灯外的一圈光晕
		ctx.fill();
		ctx.restore();
		ctx.beginPath();
		ctx.ellipse(0, 0, s * 0.34, s * 0.42, 0, 0, Math.PI * 2);
		ctx.fill();
		// 内芯亮一点，像灯真的点着
		ctx.save();
		ctx.globalAlpha *= 0.55;
		ctx.fillStyle = "#ffe8a3";
		ctx.beginPath();
		ctx.arc(0, 0, s * 0.2, 0, Math.PI * 2);
		ctx.fill();
		ctx.restore();
		// 灯骨：几条竖向弧线，灯笼的骨架感
		ctx.save();
		ctx.globalAlpha *= 0.4;
		ctx.strokeStyle = q.color;
		ctx.lineWidth = 1;
		for (const dx of [-0.16, 0, 0.16]) {
			ctx.beginPath();
			ctx.moveTo(dx * s, -s * 0.38);
			ctx.quadraticCurveTo(dx * s * 1.5, 0, dx * s, s * 0.38);
			ctx.stroke();
		}
		ctx.restore();
		ctx.fillRect(-s * 0.2, -s * 0.52, s * 0.4, s * 0.12);   // 上盖
		ctx.fillRect(-s * 0.2, s * 0.4, s * 0.4, s * 0.12);     // 下盖
		ctx.strokeStyle = q.color;
		ctx.lineWidth = 1.5;
		ctx.beginPath();
		ctx.moveTo(0, s * 0.52);
		ctx.lineTo(0, s * 0.8);                                  // 流苏
		ctx.stroke();
	}

	function drawLeaf(ctx, q) {
		const s = q.size;
		ctx.beginPath();
		ctx.ellipse(0, 0, s / 2, s / 3.4, 0, 0, Math.PI * 2);
		ctx.fill();
		ctx.strokeStyle = "rgba(90, 50, 20, .35)";
		ctx.lineWidth = 1;
		ctx.beginPath();
		ctx.moveTo(-s / 2.4, 0);
		ctx.lineTo(s / 2.4, 0);                                  // 叶脉
		ctx.stroke();
	}

	function drawSnow(ctx, q) {
		const s = q.size;
		if (q.kind === 0) {
			ctx.beginPath();
			ctx.arc(0, 0, s / 4.2, 0, Math.PI * 2);
			ctx.fill();
			return;
		}
		// 六角雪花：三条线段交叉
		ctx.strokeStyle = q.color;
		ctx.lineWidth = 1.6;
		const r = s / 2.2;
		for (let i = 0; i < 3; i++) {
			const a = (Math.PI / 3) * i;
			ctx.beginPath();
			ctx.moveTo(-Math.cos(a) * r, -Math.sin(a) * r);
			ctx.lineTo(Math.cos(a) * r, Math.sin(a) * r);
			ctx.stroke();
		}
	}

	function drawStar(ctx, q) {
		const r = q.size / 2.8;
		drawGlow(ctx, r * 1.7, 0.25);   // 星光柔光打底
		if (q.kind === 0) {
			ctx.beginPath();
			ctx.arc(0, 0, r * 0.5, 0, Math.PI * 2);
			ctx.fill();
		} else if (q.kind === 1) {
			// 四角星
			ctx.beginPath();
			ctx.moveTo(0, -r);
			ctx.lineTo(r * 0.32, -r * 0.32);
			ctx.lineTo(r, 0);
			ctx.lineTo(r * 0.32, r * 0.32);
			ctx.lineTo(0, r);
			ctx.lineTo(-r * 0.32, r * 0.32);
			ctx.lineTo(-r, 0);
			ctx.lineTo(-r * 0.32, -r * 0.32);
			ctx.closePath();
			ctx.fill();
		} else {
			// 十字星芒
			ctx.fillRect(-r, -0.7, r * 2, 1.4);
			ctx.fillRect(-0.7, -r, 1.4, r * 2);
		}
	}

	function drawEmber(ctx, q) {
		const s = q.size;
		ctx.save();
		ctx.globalAlpha *= 0.35;
		ctx.beginPath();
		ctx.arc(0, 0, s * 0.7, 0, Math.PI * 2);   // 暖光光晕
		ctx.fill();
		ctx.restore();
		ctx.beginPath();
		ctx.arc(0, 0, s / 4, 0, Math.PI * 2);
		ctx.fill();
	}

	function drawRibbon(ctx, q) {
		const s = q.size;
		ctx.beginPath();
		ctx.moveTo(-s / 2, 0);
		ctx.quadraticCurveTo(0, -s / 2, s / 2, 0);
		ctx.quadraticCurveTo(0, -s / 4, -s / 2, 0);
		ctx.fill();
		// 中间叠一层浅色，缎带有层次而不是一整片色
		ctx.save();
		ctx.globalAlpha *= 0.3;
		ctx.fillStyle = "#ffffff";
		ctx.beginPath();
		ctx.moveTo(-s * 0.3, -s * 0.05);
		ctx.quadraticCurveTo(0, -s * 0.38, s * 0.3, -s * 0.05);
		ctx.quadraticCurveTo(0, -s * 0.22, -s * 0.3, -s * 0.05);
		ctx.fill();
		ctx.restore();
	}

	function drawBalloon(ctx, q) {
		const s = q.size;
		ctx.beginPath();
		ctx.ellipse(0, 0, s * 0.32, s * 0.4, 0, 0, Math.PI * 2);
		ctx.fill();
		// 左上高光 + 底部气球结，像真气球
		ctx.save();
		ctx.globalAlpha *= 0.35;
		ctx.fillStyle = "#ffffff";
		ctx.beginPath();
		ctx.ellipse(-s * 0.12, -s * 0.16, s * 0.07, s * 0.12, -0.5, 0, Math.PI * 2);
		ctx.fill();
		ctx.restore();
		ctx.fillStyle = q.color;
		ctx.beginPath();
		ctx.moveTo(-s * 0.05, s * 0.42);
		ctx.lineTo(s * 0.05, s * 0.42);
		ctx.lineTo(0, s * 0.32);
		ctx.closePath();
		ctx.fill();
		ctx.strokeStyle = q.color;
		ctx.lineWidth = 1;
		ctx.beginPath();
		ctx.moveTo(0, s * 0.4);
		ctx.quadraticCurveTo(s * 0.14, s * 0.62, 0, s * 0.88);   // 气球线
		ctx.stroke();
	}

	function drawHeart(ctx, q) {
		const r = q.size / 2.4;
		ctx.beginPath();
		ctx.moveTo(0, r * 0.85);
		ctx.bezierCurveTo(-r * 1.5, -r * 0.45, -r * 0.55, -r * 1.15, 0, -r * 0.45);
		ctx.bezierCurveTo(r * 0.55, -r * 1.15, r * 1.5, -r * 0.45, 0, r * 0.85);
		ctx.fill();
		// 左上高光，爱心更有立体感
		ctx.save();
		ctx.globalAlpha *= 0.32;
		ctx.fillStyle = "#ffffff";
		ctx.beginPath();
		ctx.arc(-r * 0.38, -r * 0.34, r * 0.2, 0, Math.PI * 2);
		ctx.fill();
		ctx.restore();
	}

	function drawSkyLantern(ctx, q) {
		const s = q.size;
		ctx.save();
		ctx.globalAlpha *= 0.26;
		ctx.beginPath();
		ctx.arc(0, 0, s * 0.9, 0, Math.PI * 2);   // 孔明灯的暖光
		ctx.fill();
		ctx.restore();
		const w = s * 0.34, h = s * 0.48;
		ctx.beginPath();
		ctx.moveTo(-w, h * 0.55);
		ctx.lineTo(-w * 0.72, -h * 0.75);
		ctx.lineTo(w * 0.72, -h * 0.75);
		ctx.lineTo(w, h * 0.55);
		ctx.closePath();
		ctx.fill();
		ctx.save();
		ctx.globalAlpha *= 0.75;
		ctx.fillStyle = "#ffe8a3";
		ctx.fillRect(-w * 0.45, h * 0.52, w * 0.9, h * 0.12);   // 底部灯火
		ctx.restore();
	}

	function drawMoonOrb(ctx, q) {
		const s = q.size;
		ctx.save();
		ctx.globalAlpha *= 0.3;
		ctx.beginPath();
		ctx.arc(0, 0, s * 0.95, 0, Math.PI * 2);   // 月华光晕
		ctx.fill();
		ctx.restore();
		ctx.beginPath();
		ctx.arc(0, 0, s * 0.4, 0, Math.PI * 2);
		ctx.fill();
		// 环形山：几个稍暗的小圆，月亮不再是光板一块
		ctx.save();
		ctx.globalAlpha *= 0.28;
		ctx.fillStyle = "#8a7a55";
		ctx.beginPath();
		ctx.arc(-s * 0.14, -s * 0.1, s * 0.07, 0, Math.PI * 2);
		ctx.fill();
		ctx.beginPath();
		ctx.arc(s * 0.12, s * 0.13, s * 0.05, 0, Math.PI * 2);
		ctx.fill();
		ctx.beginPath();
		ctx.arc(s * 0.1, -s * 0.17, s * 0.04, 0, Math.PI * 2);
		ctx.fill();
		ctx.restore();
		ctx.save();
		ctx.globalAlpha *= 0.55;
		ctx.strokeStyle = q.color;
		ctx.lineWidth = 1.2;
		ctx.beginPath();
		ctx.arc(0, 0, s * 0.62, 0, Math.PI * 2);
		ctx.stroke();
		ctx.restore();
	}

	function drawMaple(ctx, q) {
		const s = q.size;
		ctx.beginPath();
		for (let i = 0; i < 10; i++) {
			const ang = -Math.PI / 2 + i * Math.PI / 5;
			const rad = i % 2 === 0 ? s * 0.5 : s * 0.2;   // 五个角、五个凹口
			const x = Math.cos(ang) * rad, y = Math.sin(ang) * rad;
			if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
		}
		ctx.closePath();
		ctx.fill();
		ctx.strokeStyle = "rgba(90, 40, 10, .35)";
		ctx.lineWidth = 1;
		ctx.beginPath();
		ctx.moveTo(0, s * 0.42);
		ctx.lineTo(0, s * 0.7);   // 叶柄
		ctx.stroke();
	}

	function drawSnowflake(ctx, q) {
		const s = q.size;
		const r = s / 2.2;
		ctx.strokeStyle = q.color;
		ctx.lineWidth = 1.5;
		for (let i = 0; i < 3; i++) {
			const a = (Math.PI / 3) * i;
			const dx = Math.cos(a) * r, dy = Math.sin(a) * r;
			ctx.beginPath();
			ctx.moveTo(-dx, -dy);
			ctx.lineTo(dx, dy);
			ctx.stroke();
			for (const sgn of [-1, 1]) {   // 每根主枝两侧的小分叉
				const bx = dx * 0.55, by = dy * 0.55;
				ctx.beginPath();
				ctx.moveTo(bx, by);
				ctx.lineTo(bx - dy * 0.3 * sgn, by + dx * 0.3 * sgn);
				ctx.stroke();
			}
		}
	}

	function drawSparkle(ctx, q) {
		const r = q.size / 2.6;
		drawGlow(ctx, r * 1.9, 0.22);   // 闪芒柔光
		ctx.beginPath();
		ctx.moveTo(0, -r);
		ctx.lineTo(r * 0.18, -r * 0.18);
		ctx.lineTo(r, 0);
		ctx.lineTo(r * 0.18, r * 0.18);
		ctx.lineTo(0, r);
		ctx.lineTo(-r * 0.18, r * 0.18);
		ctx.lineTo(-r, 0);
		ctx.lineTo(-r * 0.18, -r * 0.18);
		ctx.closePath();
		ctx.fill();
	}

	function drawBubble(ctx, q) {
		const s = q.size;
		ctx.save();
		ctx.globalAlpha *= 0.85;
		ctx.strokeStyle = q.color;
		ctx.lineWidth = 1.6;
		ctx.beginPath();
		ctx.arc(0, 0, s * 0.38, 0, Math.PI * 2);
		ctx.stroke();
		ctx.restore();
		ctx.save();
		ctx.globalAlpha *= 0.9;
		ctx.beginPath();
		ctx.arc(-s * 0.12, -s * 0.12, s * 0.08, 0, Math.PI * 2);   // 高光
		ctx.fill();
		ctx.restore();
	}

	function drawSunbeam(ctx, q) {
		const s = q.size;
		ctx.save();
		ctx.globalAlpha *= 0.24;
		ctx.beginPath();
		ctx.ellipse(0, 0, s * 0.32, s * 0.85, 0, 0, Math.PI * 2);   // 暖光柱
		ctx.fill();
		ctx.restore();
		ctx.beginPath();
		ctx.arc(0, 0, s * 0.16, 0, Math.PI * 2);
		ctx.fill();
	}

	function drawFlag(ctx, q) {
		const s = q.size;
		ctx.fillRect(-s * 0.3, -s * 0.5, Math.max(1, s * 0.07), s);   // 旗杆
		ctx.beginPath();   // 杆顶小球
		ctx.arc(-s * 0.265, -s * 0.52, s * 0.06, 0, Math.PI * 2);
		ctx.fill();
		// 旗面随飘动相位做波浪起伏，像真旗子在风里
		const wave = Math.sin(q.rot * 3 + q.phase) * s * 0.07;
		const wave2 = Math.sin(q.rot * 3 + q.phase + Math.PI / 2) * s * 0.05;
		ctx.beginPath();
		ctx.moveTo(-s * 0.26, -s * 0.5);
		ctx.quadraticCurveTo(s * 0.1, -s * 0.43 + wave, s * 0.45, -s * 0.36 + wave);
		ctx.lineTo(s * 0.45, -s * 0.16 + wave2);
		ctx.quadraticCurveTo(s * 0.1, -s * 0.23 + wave2, -s * 0.26, -s * 0.16);
		ctx.closePath();
		ctx.fill();
	}

	function drawGift(ctx, q) {
		const s = q.size;
		ctx.fillRect(-s * 0.34, -s * 0.26, s * 0.68, s * 0.6);
		ctx.save();
		ctx.fillStyle = "rgba(255, 255, 255, .78)";
		ctx.fillRect(-s * 0.055, -s * 0.26, s * 0.11, s * 0.6);   // 竖丝带
		ctx.fillRect(-s * 0.34, -s * 0.04, s * 0.68, s * 0.1);    // 横丝带
		ctx.beginPath();   // 顶部蝴蝶结
		ctx.arc(-s * 0.08, -s * 0.32, s * 0.07, 0, Math.PI * 2);
		ctx.fill();
		ctx.beginPath();
		ctx.arc(s * 0.08, -s * 0.32, s * 0.07, 0, Math.PI * 2);
		ctx.fill();
		ctx.restore();
	}

	function drawBell(ctx, q) {
		const s = q.size;
		ctx.beginPath();
		ctx.moveTo(-s * 0.3, s * 0.22);
		ctx.quadraticCurveTo(-s * 0.3, -s * 0.42, 0, -s * 0.42);
		ctx.quadraticCurveTo(s * 0.3, -s * 0.42, s * 0.3, s * 0.22);
		ctx.closePath();
		ctx.fill();
		ctx.fillRect(-s * 0.36, s * 0.22, s * 0.72, s * 0.08);
		ctx.beginPath();
		ctx.arc(0, s * 0.38, s * 0.09, 0, Math.PI * 2);   // 铃舌
		ctx.fill();
	}

	// 南瓜瓜身：中间椭圆打底 + 左右各两条瓜瓣沟壑 + 左上角高光，比单个椭圆更立体
	function drawPumpkinBody(ctx, s, color) {
		ctx.save();
		ctx.fillStyle = color;
		ctx.beginPath();
		ctx.ellipse(0, 0, s * 0.42, s * 0.34, 0, 0, Math.PI * 2);
		ctx.fill();
		ctx.strokeStyle = "rgba(140, 60, 0, .30)";
		ctx.lineWidth = Math.max(1, s * 0.035);
		for (const dx of [-0.26, -0.13, 0.13, 0.26]) {   // 瓜瓣沟壑
			ctx.beginPath();
			ctx.ellipse(s * dx, 0, s * 0.13, s * 0.33, 0, 0, Math.PI * 2);
			ctx.stroke();
		}
		ctx.fillStyle = "rgba(255, 255, 255, .16)";
		ctx.beginPath();
		ctx.ellipse(-s * 0.12, -s * 0.14, s * 0.16, s * 0.1, -0.5, 0, Math.PI * 2);   // 圆润反光
		ctx.fill();
		ctx.restore();
	}

	// 南瓜的瓜蒂与叶片：弯曲小柄 + 一片叶，替代原来一根生硬的绿色短柱
	function drawPumpkinStem(ctx, s) {
		ctx.save();
		ctx.strokeStyle = "#5b8c3e";
		ctx.lineWidth = Math.max(1.2, s * 0.07);
		ctx.lineCap = "round";
		ctx.beginPath();
		ctx.moveTo(0, -s * 0.32);
		ctx.quadraticCurveTo(s * 0.06, -s * 0.46, -s * 0.02, -s * 0.55);
		ctx.stroke();
		ctx.fillStyle = "#4caf50";
		ctx.beginPath();
		ctx.ellipse(s * 0.15, -s * 0.5, s * 0.1, s * 0.05, -0.6, 0, Math.PI * 2);
		ctx.fill();
		ctx.restore();
	}

	function drawPumpkin(ctx, q) {
		drawPumpkinBody(ctx, q.size, q.color);
		drawPumpkinStem(ctx, q.size);
	}

	function drawSnowman(ctx, q) {
		const s = q.size;
		ctx.beginPath();
		ctx.arc(0, s * 0.18, s * 0.3, 0, Math.PI * 2);    // 下身
		ctx.fill();
		ctx.beginPath();
		ctx.arc(0, -s * 0.18, s * 0.2, 0, Math.PI * 2);   // 上身
		ctx.fill();
		ctx.save();
		ctx.fillStyle = "rgba(90, 90, 90, .55)";
		ctx.fillRect(-s * 0.18, -s * 0.42, s * 0.36, s * 0.08);   // 帽子
		ctx.restore();
		// 眼睛和胡萝卜鼻子，小雪人有了表情
		ctx.save();
		ctx.fillStyle = "rgba(40, 40, 40, .75)";
		ctx.beginPath();
		ctx.arc(-s * 0.06, -s * 0.2, s * 0.02, 0, Math.PI * 2);
		ctx.fill();
		ctx.beginPath();
		ctx.arc(s * 0.06, -s * 0.2, s * 0.02, 0, Math.PI * 2);
		ctx.fill();
		ctx.fillStyle = "rgba(235, 145, 35, .85)";
		ctx.beginPath();
		ctx.moveTo(0, -s * 0.17);
		ctx.lineTo(s * 0.035, -s * 0.13);
		ctx.lineTo(-s * 0.035, -s * 0.13);
		ctx.closePath();
		ctx.fill();
		ctx.restore();
	}

	function drawFirecracker(ctx, q) {
		const s = q.size;
		ctx.fillRect(-s * 0.16, -s * 0.34, s * 0.32, s * 0.6);   // 炮身
		ctx.save();
		ctx.fillStyle = "#ffd666";
		ctx.fillRect(-s * 0.16, -s * 0.06, s * 0.32, s * 0.1);   // 金箍
		ctx.restore();
		ctx.strokeStyle = "#ffd166";
		ctx.lineWidth = 1.2;
		ctx.beginPath();
		ctx.moveTo(0, -s * 0.34);
		ctx.quadraticCurveTo(s * 0.18, -s * 0.5, s * 0.06, -s * 0.62);   // 引线
		ctx.stroke();
	}

	function drawLanternString(ctx, q) {
		const s = q.size;
		ctx.strokeStyle = q.color;
		ctx.lineWidth = 1;
		ctx.beginPath();
		ctx.moveTo(0, -s * 0.62);
		ctx.lineTo(0, s * 0.62);   // 灯绳
		ctx.stroke();
		for (const dy of [-0.42, 0, 0.42]) {
			ctx.beginPath();
			ctx.arc(0, s * dy, s * 0.14, 0, Math.PI * 2);
			ctx.fill();
		}
	}

	function drawDumpling(ctx, q) {
		const s = q.size;
		ctx.beginPath();
		ctx.moveTo(-s * 0.4, s * 0.12);
		ctx.quadraticCurveTo(0, -s * 0.42, s * 0.4, s * 0.12);   // 饺子皮上沿
		ctx.quadraticCurveTo(0, s * 0.34, -s * 0.4, s * 0.12);
		ctx.fill();
		ctx.save();
		ctx.strokeStyle = "rgba(180, 140, 90, .45)";
		ctx.lineWidth = 1;
		ctx.beginPath();
		ctx.moveTo(-s * 0.22, -s * 0.02);
		ctx.quadraticCurveTo(0, -s * 0.28, s * 0.22, -s * 0.02);   // 捏褶
		ctx.stroke();
		ctx.restore();
	}

	function drawMooncake(ctx, q) {
		const s = q.size;
		const w = s * 0.32, h = s * 0.3;
		ctx.beginPath();
		if (ctx.roundRect) ctx.roundRect(-w, -h, w * 2, h * 2, s * 0.08);
		else ctx.rect(-w, -h, w * 2, h * 2);
		ctx.fill();
		ctx.save();
		ctx.strokeStyle = "rgba(120, 80, 20, .35)";
		ctx.lineWidth = 1;
		ctx.strokeRect(-w * 0.6, -h * 0.6, w * 1.2, h * 1.2);   // 饼面花纹框
		// 饼面纹点：四角小点 + 中心一个"馅"圆，更像一块月饼
		ctx.fillStyle = "rgba(120, 80, 20, .3)";
		for (const dx of [-1, 1]) {
			for (const dy of [-1, 1]) {
				ctx.beginPath();
				ctx.arc(dx * w * 0.36, dy * h * 0.36, s * 0.03, 0, Math.PI * 2);
				ctx.fill();
			}
		}
		ctx.beginPath();
		ctx.arc(0, 0, s * 0.05, 0, Math.PI * 2);
		ctx.fill();
		ctx.restore();
	}

	function drawZongzi(ctx, q) {
		const s = q.size;
		ctx.beginPath();
		ctx.moveTo(0, -s * 0.4);
		ctx.lineTo(s * 0.36, s * 0.28);
		ctx.lineTo(-s * 0.36, s * 0.28);
		ctx.closePath();
		ctx.fill();
		ctx.save();
		ctx.strokeStyle = "rgba(30, 90, 40, .45)";
		ctx.lineWidth = 1;
		ctx.beginPath();
		ctx.moveTo(-s * 0.24, s * 0.16);
		ctx.lineTo(s * 0.24, s * 0.16);   // 绑绳
		ctx.stroke();
		ctx.restore();
	}

	function drawJack(ctx, q) {
		const s = q.size;
		// 先铺一层从内透出的暖黄光晕，真的南瓜灯是"从洞里透光"的
		ctx.save();
		ctx.fillStyle = "rgba(255, 196, 64, .38)";
		drawGlow(ctx, s * 0.55, 0.9);
		ctx.restore();
		drawPumpkinBody(ctx, s, q.color);
		drawPumpkinStem(ctx, s);
		// 刻出来的脸：三角眼 + 三角鼻 + 锯齿嘴
		ctx.save();
		ctx.fillStyle = "rgba(40, 20, 5, .85)";
		ctx.beginPath();   // 左眼
		ctx.moveTo(-s * 0.26, -s * 0.12);
		ctx.lineTo(-s * 0.08, -s * 0.12);
		ctx.lineTo(-s * 0.17, -s * 0.02);
		ctx.closePath();
		ctx.fill();
		ctx.beginPath();   // 右眼
		ctx.moveTo(s * 0.08, -s * 0.12);
		ctx.lineTo(s * 0.26, -s * 0.12);
		ctx.lineTo(s * 0.17, -s * 0.02);
		ctx.closePath();
		ctx.fill();
		ctx.beginPath();   // 鼻子
		ctx.moveTo(-s * 0.05, -s * 0.02);
		ctx.lineTo(s * 0.05, -s * 0.02);
		ctx.lineTo(0, s * 0.05);
		ctx.closePath();
		ctx.fill();
		ctx.beginPath();   // 锯齿嘴
		ctx.moveTo(-s * 0.22, s * 0.1);
		ctx.lineTo(-s * 0.11, s * 0.02);
		ctx.lineTo(0, s * 0.12);
		ctx.lineTo(s * 0.11, s * 0.02);
		ctx.lineTo(s * 0.22, s * 0.1);
		ctx.lineTo(s * 0.13, s * 0.22);
		ctx.lineTo(-s * 0.13, s * 0.22);
		ctx.closePath();
		ctx.fill();
		ctx.restore();
	}

	function drawKite(ctx, q) {
		const s = q.size;
		ctx.beginPath();
		ctx.moveTo(0, -s * 0.42);
		ctx.lineTo(s * 0.3, 0);
		ctx.lineTo(0, s * 0.36);
		ctx.lineTo(-s * 0.3, 0);
		ctx.closePath();
		ctx.fill();
		ctx.save();
		ctx.strokeStyle = "rgba(255, 255, 255, .55)";
		ctx.lineWidth = 1;
		ctx.beginPath();
		ctx.moveTo(0, -s * 0.42);
		ctx.lineTo(0, s * 0.36);   // 骨架
		ctx.moveTo(-s * 0.3, 0);
		ctx.lineTo(s * 0.3, 0);
		ctx.stroke();
		ctx.restore();
		ctx.strokeStyle = q.color;
		ctx.lineWidth = 1.2;
		ctx.beginPath();
		ctx.moveTo(0, s * 0.36);
		ctx.quadraticCurveTo(s * 0.16, s * 0.5, 0, s * 0.64);   // 尾巴
		ctx.stroke();
	}

	function drawChrysanthemum(ctx, q) {
		const s = q.size;
		const r = s * 0.42;
		ctx.strokeStyle = q.color;
		ctx.lineWidth = 1.6;
		for (let i = 0; i < 10; i++) {
			const a = (Math.PI * 2 * i) / 10;
			ctx.beginPath();
			ctx.moveTo(0, 0);
			ctx.quadraticCurveTo(Math.cos(a) * r * 0.6, Math.sin(a) * r * 0.6, Math.cos(a) * r, Math.sin(a) * r);
			ctx.stroke();
		}
		ctx.beginPath();
		ctx.arc(0, 0, s * 0.1, 0, Math.PI * 2);   // 花心
		ctx.fill();
	}

	function drawShootingStar(ctx, q) {
		const s = q.size;
		drawGlow(ctx, s * 0.4, 0.3);   // 流星头部的光
		ctx.save();
		ctx.globalAlpha *= 0.45;
		ctx.strokeStyle = q.color;
		ctx.lineWidth = s * 0.1;
		ctx.beginPath();
		ctx.moveTo(0, 0);
		ctx.lineTo(-s * 0.16, -s * 0.9);   // 尾迹
		ctx.stroke();
		ctx.restore();
		ctx.beginPath();
		ctx.arc(0, 0, s * 0.12, 0, Math.PI * 2);
		ctx.fill();
	}

	function drawSun(ctx, q) {
		const s = q.size;
		ctx.save();
		ctx.globalAlpha *= 0.3;
		ctx.beginPath();
		ctx.arc(0, 0, s * 0.5, 0, Math.PI * 2);   // 日晕
		ctx.fill();
		ctx.restore();
		ctx.beginPath();
		ctx.arc(0, 0, s * 0.22, 0, Math.PI * 2);
		ctx.fill();
		ctx.strokeStyle = q.color;
		ctx.lineWidth = 1.4;
		for (let i = 0; i < 8; i++) {
			const a = (Math.PI * 2 * i) / 8;
			ctx.beginPath();
			ctx.moveTo(Math.cos(a) * s * 0.3, Math.sin(a) * s * 0.3);
			ctx.lineTo(Math.cos(a) * s * 0.44, Math.sin(a) * s * 0.44);   // 光芒
			ctx.stroke();
		}
	}

	function drawRain(ctx, q) {
		const s = q.size;
		ctx.strokeStyle = q.color;
		ctx.lineWidth = 1.2;
		ctx.beginPath();
		ctx.moveTo(0, -s * 0.5);
		ctx.lineTo(s * 0.12, s * 0.5);   // 斜雨丝
		ctx.stroke();
	}

	function drawCloud(ctx, q) {
		const s = q.size;
		ctx.beginPath();
		ctx.arc(-s * 0.2, 0, s * 0.2, 0, Math.PI * 2);
		ctx.arc(s * 0.05, -s * 0.06, s * 0.24, 0, Math.PI * 2);
		ctx.arc(s * 0.26, 0, s * 0.18, 0, Math.PI * 2);
		ctx.fill();
		ctx.save();
		ctx.globalAlpha *= 0.5;
		ctx.fillRect(-s * 0.36, s * 0.1, s * 0.7, s * 0.1);   // 云底
		ctx.restore();
	}

	function drawCandy(ctx, q) {
		const s = q.size;
		ctx.beginPath();
		ctx.ellipse(0, 0, s * 0.2, s * 0.14, 0, 0, Math.PI * 2);
		ctx.fill();
		// 糖纸上斜条纹，像包好的水果糖
		ctx.save();
		ctx.globalAlpha *= 0.4;
		ctx.strokeStyle = "#ffffff";
		ctx.lineWidth = Math.max(1, s * 0.03);
		for (const dx of [-0.12, -0.04, 0.04, 0.12]) {
			ctx.beginPath();
			ctx.moveTo(dx * s, -s * 0.12);
			ctx.lineTo((dx + 0.06) * s, s * 0.12);
			ctx.stroke();
		}
		ctx.restore();
		ctx.beginPath();   // 两头糖纸
		ctx.moveTo(-s * 0.2, 0);
		ctx.lineTo(-s * 0.4, -s * 0.12);
		ctx.lineTo(-s * 0.4, s * 0.12);
		ctx.closePath();
		ctx.fill();
		ctx.beginPath();
		ctx.moveTo(s * 0.2, 0);
		ctx.lineTo(s * 0.4, -s * 0.12);
		ctx.lineTo(s * 0.4, s * 0.12);
		ctx.closePath();
		ctx.fill();
	}

	function drawGhost(ctx, q) {
		const s = q.size;
		ctx.beginPath();
		ctx.arc(0, -s * 0.08, s * 0.32, Math.PI, 0);   // 圆头
		ctx.lineTo(s * 0.32, s * 0.28);
		for (let i = 0; i < 3; i++) ctx.lineTo(s * 0.32 - s * 0.21 * (i + 0.5), s * 0.2);   // 下摆波浪
		ctx.lineTo(-s * 0.32, s * 0.28);
		ctx.closePath();
		ctx.fill();
		ctx.save();
		ctx.fillStyle = "rgba(70, 70, 90, .75)";
		ctx.beginPath();
		ctx.arc(-s * 0.11, -s * 0.1, s * 0.045, 0, Math.PI * 2);   // 眼睛
		ctx.fill();
		ctx.beginPath();
		ctx.arc(s * 0.11, -s * 0.1, s * 0.045, 0, Math.PI * 2);
		ctx.fill();
		ctx.restore();
	}

	function drawRedPacket(ctx, q) {
		const s = q.size;
		ctx.beginPath();
		if (ctx.roundRect) ctx.roundRect(-s * 0.22, -s * 0.3, s * 0.44, s * 0.6, s * 0.05);
		else ctx.rect(-s * 0.22, -s * 0.3, s * 0.44, s * 0.6);
		ctx.fill();
		ctx.save();
		ctx.fillStyle = "#ffd666";
		ctx.beginPath();
		ctx.arc(0, s * 0.02, s * 0.09, 0, Math.PI * 2);   // 封口金印
		ctx.fill();
		ctx.restore();
	}

	function drawRiceCake(ctx, q) {
		const s = q.size;
		ctx.beginPath();
		if (ctx.roundRect) ctx.roundRect(-s * 0.3, -s * 0.18, s * 0.6, s * 0.36, s * 0.06);
		else ctx.rect(-s * 0.3, -s * 0.18, s * 0.6, s * 0.36);
		ctx.fill();
		ctx.save();
		ctx.strokeStyle = "rgba(190, 160, 110, .45)";
		ctx.lineWidth = 1;
		ctx.beginPath();
		ctx.moveTo(-s * 0.3, 0);
		ctx.lineTo(s * 0.3, 0);   // 年糕纹理
		ctx.stroke();
		ctx.restore();
	}

	function drawTanghulu(ctx, q) {
		const s = q.size;
		ctx.save();
		ctx.strokeStyle = "#c99a5b";
		ctx.lineWidth = Math.max(1, s * 0.05);
		ctx.beginPath();
		ctx.moveTo(0, -s * 0.5);
		ctx.lineTo(0, s * 0.5);   // 竹签
		ctx.stroke();
		ctx.restore();
		for (const dy of [-0.28, 0, 0.28]) {
			ctx.beginPath();
			ctx.arc(0, s * dy, s * 0.15, 0, Math.PI * 2);
			ctx.fill();
		}
		// 糖衣高光：每颗山楂左上一点亮光，糖壳透亮的感觉
		ctx.save();
		ctx.globalAlpha *= 0.4;
		ctx.fillStyle = "#ffffff";
		for (const dy of [-0.28, 0, 0.28]) {
			ctx.beginPath();
			ctx.arc(-s * 0.05, s * dy - s * 0.05, s * 0.04, 0, Math.PI * 2);
			ctx.fill();
		}
		ctx.restore();
	}

	function drawAirplane(ctx, q) {
		const s = q.size;
		ctx.beginPath();
		ctx.moveTo(0, -s * 0.5);
		ctx.lineTo(s * 0.1, -s * 0.1);
		ctx.lineTo(s * 0.5, s * 0.1);
		ctx.lineTo(s * 0.5, s * 0.2);
		ctx.lineTo(s * 0.1, s * 0.12);
		ctx.lineTo(s * 0.12, s * 0.4);
		ctx.lineTo(s * 0.24, s * 0.5);
		ctx.lineTo(-s * 0.24, s * 0.5);
		ctx.lineTo(-s * 0.12, s * 0.4);
		ctx.lineTo(-s * 0.1, s * 0.12);
		ctx.lineTo(-s * 0.5, s * 0.2);
		ctx.lineTo(-s * 0.5, s * 0.1);
		ctx.lineTo(-s * 0.1, -s * 0.1);
		ctx.closePath();
		ctx.fill();
		// 机身高光 + 机尾虚线尾迹，飞行的动感
		ctx.save();
		ctx.globalAlpha *= 0.3;
		ctx.fillStyle = "#ffffff";
		ctx.beginPath();
		ctx.ellipse(0, -s * 0.08, s * 0.07, s * 0.28, 0, 0, Math.PI * 2);
		ctx.fill();
		ctx.globalAlpha *= 0.9;
		ctx.strokeStyle = q.color;
		ctx.lineWidth = 1;
		ctx.setLineDash([s * 0.08, s * 0.1]);
		ctx.beginPath();
		ctx.moveTo(-s * 0.55, s * 0.15);
		ctx.lineTo(-s * 0.9, s * 0.15);
		ctx.stroke();
		ctx.setLineDash([]);
		ctx.restore();
	}

	function drawSuitcase(ctx, q) {
		const s = q.size;
		ctx.beginPath();
		if (ctx.roundRect) ctx.roundRect(-s * 0.3, -s * 0.22, s * 0.6, s * 0.48, s * 0.06);
		else ctx.rect(-s * 0.3, -s * 0.22, s * 0.6, s * 0.48);
		ctx.fill();
		ctx.save();
		ctx.strokeStyle = "rgba(80, 50, 20, .4)";
		ctx.lineWidth = Math.max(1, s * 0.05);
		ctx.beginPath();
		ctx.arc(0, -s * 0.22, s * 0.12, Math.PI, 0);   // 提手
		ctx.stroke();
		ctx.beginPath();
		ctx.moveTo(-s * 0.1, -s * 0.22);
		ctx.lineTo(-s * 0.1, s * 0.26);
		ctx.moveTo(s * 0.1, -s * 0.22);
		ctx.lineTo(s * 0.1, s * 0.26);   // 箱体分隔
		ctx.stroke();
		ctx.restore();
	}

	function drawZzz(ctx, q) {
		const s = q.size;
		ctx.save();
		ctx.font = `bold ${Math.max(8, s * 0.7)}px sans-serif`;
		ctx.textAlign = "center";
		ctx.textBaseline = "middle";
		ctx.fillText("Z", 0, 0);
		ctx.globalAlpha *= 0.6;
		ctx.font = `bold ${Math.max(6, s * 0.45)}px sans-serif`;
		ctx.fillText("Z", s * 0.3, -s * 0.3);
		ctx.restore();
	}

	// 烟花：随机位置不断炸开火星，受重力下坠并逐渐淡出（常驻循环）
	// 在指定位置放一朵烟花（点击处放的就是它；不传坐标则在常用位置随机一朵）
	function spawnFireworkBurst(s, cx, cy, t) {
		t = t || performance.now();
		const palette = s.palette, W = s.W, H = s.H;
		const color = palette[Math.floor(Math.random() * palette.length)];
		if (cx == null) { cx = W * (0.15 + Math.random() * 0.7); cy = H * (0.12 + Math.random() * 0.42); }
		const sparks = [];
		const n = Math.round((26 + Math.floor(Math.random() * 14)) * Math.min(1.6, s.densityMul || 1));
		for (let i = 0; i < n; i++) {
			const angle = (Math.PI * 2 * i) / n + Math.random() * 0.12;
			const speed = 1.3 + Math.random() * 2.4;
			sparks.push({ x: cx, y: cy, vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed, r: (1.2 + Math.random() * 1.6) * (s.sizeMul || 1) });
		}
		s.bursts.push({ sparks, color, born: t });
	}

	function drawFireworks(s, t) {
		const ctx = s.ctx;
		if (!s.nextBurst || t >= s.nextBurst) {
			spawnFireworkBurst(s);
			if (Math.random() < 0.35) spawnFireworkBurst(s);   // 偶尔两朵一起放
			s.nextBurst = t + 700 + Math.random() * 500;
		}
		ctx.globalCompositeOperation = "lighter";
		for (let i = s.bursts.length - 1; i >= 0; i--) {
			const b = s.bursts[i];
			const age = (t - b.born) / 1600;
			if (age >= 1) { s.bursts.splice(i, 1); continue; }
			ctx.globalAlpha = Math.max(0, 1 - age);
			ctx.fillStyle = b.color;
			for (const p of b.sparks) {
				p.x += p.vx;
				p.y += p.vy;
				p.vy += 0.035;
				p.vx *= 0.985;
				p.vy *= 0.985;
				// 鼠标互动：光标附近的火星会被轻轻推开，鼠标移动越快推得越远
				const dx = p.x - s.mx, dy = p.y - s.my;
				const d2 = dx * dx + dy * dy;
				if (d2 < 16900 && d2 > 0.01) {
					const d = Math.sqrt(d2);
					const f = (1 - d / 130) * 1.8 * (1 + Math.min(1.2, (s.ms || 0) / 22));
					p.x += (dx / d) * f;
					p.y += (dy / d) * f;
				}
				ctx.beginPath();
				ctx.arc(p.x, p.y, p.r * (1 - age * 0.6), 0, Math.PI * 2);
				ctx.fill();
			}
		}
		ctx.globalAlpha = 1;
		ctx.globalCompositeOperation = "source-over";
	}

	function randomSelection(obj) {
		// 角色台词按“组”保存：先随机选一组，再随机选组内的一句，最终始终返回字符串。
		const selected = Array.isArray(obj) ? obj[Math.floor(Math.random() * obj.length)] : obj;
		return Array.isArray(selected) ? randomSelection(selected) : selected;
	}

	// ===== 形象库（多分类 + 用户自选，见 public/live2d/model_list.json）=====
	let modelList;
	// 当前已加载的形象 id：用于避免重复加载同一模型（重复 loadlive2d 会让画布短暂空白）
	let currentModelName = null;
	async function loadModelList() {
		let response = await fetch(`${live2d_path}model_list.json`);
		modelList = await response.json();
	}

	function getCookie(name) {
		const m = document.cookie.match(new RegExp("(?:^|;\\s*)" + name + "=([^;]*)"));
		return m ? decodeURIComponent(m[1]) : "";
	}

	// 与后端 findurlmail 同规则：从页面 URL 解析当前主页主人（跳过模块前缀，兼容 history/hash 路由）
	const URL_MODULE_PREFIX = ["think", "csdn", "book", "zhihu", "video", "travel", "commonuse",
		"everydayimg", "admin", "people", "article", "markdown_detail", "post_article", "detail"];
	function findUrlmail() {
		const rest = location.href.replace(/^.*?:\/\//, "");
		const slash = rest.indexOf("/");
		let path = slash >= 0 ? rest.slice(slash) : "";
		path = path.split("?")[0];
		if (path.includes("#")) path = path.split("#")[1] || "";
		const segs = path.split("/").filter(Boolean);
		while (segs.length && URL_MODULE_PREFIX.includes(segs[0].toLowerCase())) segs.shift();
		return segs[0] || "";
	}

	// 公开读取指定用户（主页主人）的看板郎配置：形象 + 自定义台词；失败/未配置返回 null
	async function fetchOwnerWidget(mail) {
		try {
			const resp = await fetch("/csdn/get_widget_public", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ mail }),
			});
			const data = await resp.json();
			if (data.ret === 1 && data.widget) return data.widget;
		} catch (e) { /* 网络异常按未配置处理 */ }
		return null;
	}

	// 拉取登录用户的形象配置；未登录/请求失败返回 null
	async function fetchUserWidget() {
		const mail = getCookie("mail"), password = getCookie("password");
		if (!mail || !password) return null;
		try {
			const resp = await fetch("/csdn/get_widget", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ mail, password }),
			});
			const data = await resp.json();
			if (data.ret === 1 && data.widget) return data.widget;   // model/lines 任一字段都算有效配置
		} catch (e) { /* 网络异常按未配置处理 */ }
		return null;
	}

	// 保存形象选择：登录 → 存账号（换设备也生效）；未登录 → 仅本机 localStorage
	async function saveUserWidget(modelName) {
		localStorage.setItem("waifu-model", modelName);
		const mail = getCookie("mail"), password = getCookie("password");
		if (!mail || !password) {
			showMessage("未登录哦～形象先记在这台设备上，登录后就能跟着账号走啦。", 5000, 9);
			return;
		}
		try {
			const resp = await fetch("/csdn/set_widget", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ mail, password, widget: { model: modelName } }),
			});
			const data = await resp.json();
			showMessage(data.ret === 1 ? "形象已保存到你的账号，以后都由TA迎接你啦！" : "服务器没存上，不过本机已经记住啦。", 5000, 9);
		} catch (e) {
			showMessage("服务器没存上，不过本机已经记住啦。", 5000, 9);
		}
	}

	async function loadModel(modelName, message) {
		localStorage.setItem("waifu-model", modelName);
		applyCharacterTips(modelName); // 切换角色后台词（戳/点/闲聊/欢迎）立即换上该角色的口吻
		showMessage(message, 4000, 10);
		// 记录已加载形象；加载异常（模型文件损坏/并发切换）时回退到昼夜默认，
		// 避免画布停在空白状态再也出不来
		currentModelName = modelName;
		try {
			loadlive2d("live2d", `${live2d_path}model/${modelName}/index.json`);
		} catch (e) {
			console.warn("Live2D 模型加载失败", modelName, e);
			const fallback = (new Date().getHours() >= 20 || new Date().getHours() < 8) ? "izumi" : "haruto";
			if (modelName !== fallback) {
				currentModelName = fallback;
				loadlive2d("live2d", `${live2d_path}model/${fallback}/index.json`);
			}
		}
		console.log(`Live2D 模型 ${modelName} 加载完成`);
	}

	async function loadNextModel() {
		if (!modelList) await loadModelList();
		const models = modelList.models;
		const current = localStorage.getItem("waifu-model") || models[0].id;
		const index = models.findIndex(m => m.id === current);
		const next = models[(index + 1 + models.length) % models.length];
		loadModel(next.id, `${next.name}：${next.desc}`);
	}

	// 初始化优先级：主页主人配置 > 登录账号配置 > 本机记录 > 按昼夜默认（白天 haruto，20 点至次日 8 点 izumi）
	// 打开谁的主页就看到谁的形象、听到谁的自定义台词（公开接口读取，无需登录）
	async function resolveOwnerModel(urlmail) {
		const ownerWidget = urlmail ? await fetchOwnerWidget(urlmail) : null;
		const ids = modelList.models.map(m => m.id);
		ownerLines = ownerWidget && Array.isArray(ownerWidget.lines) ? ownerWidget.lines : [];
		let model = ownerWidget && ids.includes(ownerWidget.model) ? ownerWidget.model : null;
		if (!model) {
			const widget = await fetchUserWidget();
			model = widget && ids.includes(widget.model) ? widget.model : null;
		}
		// 本机记录只在没有页面主人时兜底（裸域名/未知页面）：本机形象是访客自己的选择，
		// 出现在别人的主页会张冠李戴——主人已识别（urlmail 存在）却没配置形象时，
		// 直接落到昼夜默认，而不是显示访客自己的角色
		if (!model && !urlmail) {
			model = localStorage.getItem("waifu-model");
			if (!model || !ids.includes(model)) model = null;
		}
		if (!model) {
			const hour = new Date().getHours();
			model = (hour >= 20 || hour < 8) ? "izumi" : "haruto";
		}
		return model;
	}

	(async function initModel() {
		localStorage.removeItem("modelId");        // 清理旧版数字下标存档
		localStorage.removeItem("modelTexturesId");
		// 形象清单先就绪，才能校验主人配置里的 id 是否有效
		if (!modelList) await loadModelList();
		loadModel(await resolveOwnerModel(findUrlmail()));
		// 语料在脚本加载时就开始预取；这里只是兜底：首屏没拿到（或内存里已失效）时再补一次，
		// 已经在内存里则直接复用，不会重复下载
		preloadTips();
	})();

	// ===== 形象选择器（⚙️ 按钮，按分类挑选）=====
	// 面板跟随看板郎定位：优先展开在看板郎左侧（看板郎可被拖到任意位置，不能钉死在屏幕左边），
	// 左侧放不下时换到右侧；垂直方向贴着看板郎底部、限制在视口内。拖拽/复位时由 index.html 回调同步。
	function syncPickerPos() {
		const picker = document.getElementById("waifu-picker");
		const waifu = document.getElementById("waifu");
		if (!picker || !waifu || picker.classList.contains("waifu-picker-hidden")) return;
		const w = waifu.getBoundingClientRect();
		const vw = window.innerWidth, vh = window.innerHeight;
		let left = w.left - 310;                                  // 面板宽 300 + 10px 间距，向左展开
		if (left < 10) left = Math.min(w.right + 10, vw - 310);   // 左侧放不下 → 换到看板郎右侧
		left = Math.max(10, Math.min(left, vw - 310));
		const bottom = Math.max(10, Math.min(vh - w.bottom, vh * 0.38));
		picker.style.left = left + "px";
		picker.style.top = "auto";
		picker.style.right = "auto";
		picker.style.bottom = bottom + "px";
	}
	window.waifuSyncPicker = syncPickerPos;   // 供 index.html 拖拽/复位时同步面板位置
	function openModelPicker() {
		let picker = document.getElementById("waifu-picker");
		if (picker) { picker.classList.toggle("waifu-picker-hidden"); syncPickerPos(); return; }
		if (!modelList) { loadModelList().then(openModelPicker); return; }
		document.body.insertAdjacentHTML("beforeend", `<div id="waifu-picker">
			<div class="waifu-picker-panel">
				<div class="waifu-picker-head">
					<span>🎨 看板郎设置</span>
					<span class="waifu-picker-close" role="button" title="关闭">✖️</span>
				</div>
				<div class="waifu-picker-views">
					<span class="waifu-picker-view waifu-picker-view-active" data-view="model" role="button">形象</span>
					<span class="waifu-picker-view" data-view="lines" role="button">台词</span>
				</div>
				<div class="waifu-picker-tabs"></div>
				<div class="waifu-picker-list"></div>
				<div class="waifu-lines" style="display:none">
					<div class="waifu-lines-groups"></div>
					<div class="waifu-lines-ops">
						<span class="waifu-lines-add" role="button">＋ 添加一组</span>
						<span class="waifu-lines-save" role="button">保存台词</span>
					</div>
					<div class="waifu-lines-tip">每组一个文本框，一行一句，可建多组。台词保存在自己账号（people/&lt;你&gt;/widget.json），别人打开你的主页时，看板郎会把它们和公共语料、角色专属台词一起随机说出。</div>
				</div>
				<div class="waifu-picker-foot">登录后选择会保存到账号，未登录仅本机生效。</div>
			</div>
		</div>`);
		picker = document.getElementById("waifu-picker");
		syncPickerPos();
		picker.querySelector(".waifu-picker-close").addEventListener("click", () => picker.classList.add("waifu-picker-hidden"));
		// 形象 / 台词 页签切换
		const tabsEl = picker.querySelector(".waifu-picker-tabs");
		const listEl = picker.querySelector(".waifu-picker-list");
		const linesEl = picker.querySelector(".waifu-lines");
		picker.querySelectorAll(".waifu-picker-view").forEach(v => {
			v.addEventListener("click", () => {
				picker.querySelectorAll(".waifu-picker-view").forEach(x => x.classList.remove("waifu-picker-view-active"));
				v.classList.add("waifu-picker-view-active");
				const isLines = v.dataset.view === "lines";
				tabsEl.style.display = isLines ? "none" : "";
				listEl.style.display = isLines ? "none" : "";
				linesEl.style.display = isLines ? "" : "none";
				if (isLines) loadLinesEditor();
			});
		});

		// ===== 台词编辑器：多组台词，存账号 widget.json 的 lines 字段 =====
		const groupsEl = picker.querySelector(".waifu-lines-groups");
		function addLineGroup(lines) {
			const div = document.createElement("div");
			div.className = "waifu-lines-group";
			div.innerHTML = `<div class="waifu-lines-group-head"><span>第 ${groupsEl.children.length + 1} 组</span><span class="waifu-lines-del" role="button" title="删除本组">🗑</span></div><textarea rows="4" placeholder="一行一句台词"></textarea>`;
			div.querySelector("textarea").value = (lines || []).join("\n");   // value 赋值，台词含特殊字符也安全
			div.querySelector(".waifu-lines-del").addEventListener("click", () => div.remove());
			groupsEl.appendChild(div);
		}
		async function loadLinesEditor() {
			const mail = getCookie("mail"), password = getCookie("password");
			if (!mail || !password) {
				groupsEl.innerHTML = '<div class="waifu-picker-empty">登录后才能配置自己的台词哦。</div>';
				return;
			}
			groupsEl.innerHTML = '<div class="waifu-picker-empty">读取中…</div>';
			const widget = await fetchUserWidget();
			const lines = widget && Array.isArray(widget.lines) ? widget.lines : [];
			groupsEl.innerHTML = "";
			lines.forEach(g => addLineGroup(g));
			if (!lines.length) addLineGroup([]);
		}
		picker.querySelector(".waifu-lines-add").addEventListener("click", () => {
			if (!getCookie("mail")) { showMessage("先登录，再给自己的看板郎写台词吧。", 4000, 9); return; }
			addLineGroup([]);
		});
		picker.querySelector(".waifu-lines-save").addEventListener("click", async () => {
			const mail = getCookie("mail"), password = getCookie("password");
			if (!mail || !password) { showMessage("先登录，台词才能保存到账号哦。", 4000, 9); return; }
			const lines = [...groupsEl.querySelectorAll("textarea")]
				.map(t => t.value.split("\n").map(s => s.trim()).filter(Boolean))
				.filter(g => g.length);                                  // 空组不上送
			try {
				const resp = await fetch("/csdn/set_widget", {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({ mail, password, widget: { lines } }),
				});
				const data = await resp.json();
				showMessage(data.ret === 1 ? "台词已保存到你的账号，来客也能听到啦！" : "保存失败，稍后再试试吧。", 4000, 9);
				// 正在浏览自己的主页时立即生效，无需刷新
				if (data.ret === 1 && findUrlmail() === mail) {
					ownerLines = lines;
					applyCharacterTips(localStorage.getItem("waifu-model"));
				}
			} catch (e) {
				showMessage("网络异常，台词没存上，稍后再试试吧。", 4000, 9);
			}
		});
		const tabs = picker.querySelector(".waifu-picker-tabs");
		const list = picker.querySelector(".waifu-picker-list");
		modelList.categories.forEach((cat, i) => {
			const tab = document.createElement("span");
			tab.className = "waifu-picker-tab" + (i === 0 ? " waifu-picker-tab-active" : "");
			tab.textContent = `${cat.icon} ${cat.name}`;
			tab.dataset.cat = cat.id;
			tab.setAttribute("role", "button");
			tab.addEventListener("click", () => {
				tabs.querySelectorAll(".waifu-picker-tab").forEach(t => t.classList.remove("waifu-picker-tab-active"));
				tab.classList.add("waifu-picker-tab-active");
				renderCards(cat.id);
			});
			tabs.appendChild(tab);
		});
		function renderCards(catId) {
			list.innerHTML = "";
			const models = modelList.models.filter(m => catId === "all" || m.category === catId);
			if (!models.length) {
				const empty = document.createElement("div");
				empty.className = "waifu-picker-empty";
				empty.textContent = "该分类暂时还没有现成的开源模型，欢迎按下方提示自行添加！";
				list.appendChild(empty);
				return;
			}
			const current = localStorage.getItem("waifu-model");
			models.forEach(m => {
				const card = document.createElement("div");
				card.className = "waifu-picker-card" + (m.id === current ? " waifu-picker-card-active" : "");
				card.innerHTML = `<div class="waifu-picker-name">${m.name}</div><div class="waifu-picker-desc">${m.desc}</div>`;
				card.setAttribute("role", "button");
				card.addEventListener("click", () => {
					// 重复点击当前形象不再重新加载：重复 loadlive2d 会让画布短暂空白
					if (m.id === currentModelName) {
						showMessage(`${m.name}：${m.desc}`, 4000, 10);
					} else {
						loadModel(m.id, `${m.name}：${m.desc}`);
					}
					saveUserWidget(m.id);
					list.querySelectorAll(".waifu-picker-card").forEach(c => c.classList.remove("waifu-picker-card-active"));
					card.classList.add("waifu-picker-card-active");
				});
				list.appendChild(card);
			});
		}
		renderCards("all");
	}
}

function initWidget() {
	document.body.insertAdjacentHTML("beforeend", `<div id="waifu-toggle">
			<span>看 板 郎</span>
		</div>`);
	let toggle = document.getElementById("waifu-toggle");
	toggle.addEventListener("click", () => {
		toggle.classList.remove("waifu-toggle-active");
		if (toggle.getAttribute("first-time")) {
			loadWidget();
			toggle.removeAttribute("first-time");
		} else {
			localStorage.removeItem("waifu-display");
			document.getElementById("waifu").style.display = "";
			setTimeout(() => {
				document.getElementById("waifu").style.bottom = "58px";   // 与默认停靠一致（上抬 58px）
			}, 0);
		}
	});
	if (localStorage.getItem("waifu-display") && Date.now() - localStorage.getItem("waifu-display") <= 86400000) {
		toggle.setAttribute("first-time", true);
		setTimeout(() => {
			toggle.classList.add("waifu-toggle-active");
		}, 0);
	} else {
		loadWidget();
	}
}

console.log('\n' + ' %c Live2D 看板郎' + ' %c https://github.com/crowya/live2d ' + '\n', 'color: #fadfa3; background: #030307; padding:5px 0;', 'background: #fadfa3; padding:5px 0;');
