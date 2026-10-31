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
//    自定义模型：把模型目录放进 public/live2d/model/ 并在 model_list.json 注册即可。
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
		document.getElementById("waifu").style.bottom = 0;
	}, 0);

	// ===== 角色台词（per_model / per_category）：按当前形象动态替换戳/点/闲聊/欢迎语 =====
	// 当前角色的台词包（registerEventListener 拿到 result 后才有值；切换模型时原地改写）
	let tipsResult = null;
	let charGreeting = null; // 当前角色欢迎语数组；null 时 welcomeMessage 走默认时段文案

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
		merge(tipsResult.message.default, tips ? tips.chat : []);      // 空闲闲聊池
		for (const t of tipsResult.mouseover) {                        // 悬停文案
			if (t.selector === "#waifu #live2d") { merge(t.text, tips ? tips.mouseover : []); break; }
		}
		for (const t of tipsResult.click) {                            // 点击文案
			if (t.selector === "#waifu #live2d") { merge(t.text, tips ? tips.click : []); break; }
		}
	}

	function registerEventListener(result) {
		tipsResult = result; // 供角色台词系统读写（applyCharacterTips）
		// 台词库就绪后，立即为当前形象应用专属台词（戳/点/闲聊/欢迎语），
		// 放在首次欢迎语生成之前，让第一句问候就带角色口吻
		applyCharacterTips(localStorage.getItem("waifu-model"));
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
		document.querySelector("#waifu-tool .tool-switch").addEventListener("click", loadNextModel);
		document.querySelector("#waifu-tool .tool-photo").addEventListener("click", () => {
			showMessage("照好了嘛，是不是很帅呢？", 6000, 9);
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
		// 检测用户活动状态，并在空闲时显示消息
        let userAction = false,
            userActionTimer,
            messageArray = result.message.default,
            lastHoverElement;
        window.addEventListener("mousemove", () => userAction = true);
        window.addEventListener("keydown", () => userAction = true);
        setInterval(() => {
            if (userAction) {
                userAction = false;
                clearInterval(userActionTimer);
                userActionTimer = null;
            } else if (!userActionTimer) {
                userActionTimer = setInterval(() => {
                    showMessage(messageArray, 6000, 9);
                }, 20000);
            }
        }, 1000);
		showMessage(welcomeMessage(result.time), 7000, 11);
        window.addEventListener("mouseover", event => {
    		for (let tips of result.mouseover) {
    			if (!event.target.matches(tips.selector)) continue;
    			let text = randomSelection(tips.text);
    			text = text.replace("{text}", event.target.innerText);
    			showMessage(text, 4000, 8);
    			return;
    		}
    	});
    	window.addEventListener("click", event => {
    		for (let tips of result.click) {
    			if (!event.target.matches(tips.selector)) continue;
    			let text = randomSelection(tips.text);
    			text = text.replace("{text}", event.target.innerText);
    			showMessage(text, 4000, 8);
    			return;
    		}
    	});
    	// 右键彩蛋（原版为 jQuery 实现，这里改为原生事件）
    	document.getElementById("live2d").addEventListener("mousedown", e => {
    		if (e.button === 2) showMessage(result.message.secret_path, 4000, 12);
    	});
    	document.getElementById("live2d").addEventListener("contextmenu", e => e.preventDefault());
    	result.seasons.forEach(({ date, text }) => {
            const now = new Date(),
                after = date.split("-")[0],
                before = date.split("-")[1] || after;
            if ((after.split("/")[0] <= now.getMonth() + 1 && now.getMonth() + 1 <= before.split("/")[0]) && (after.split("/")[1] <= now.getDate() && now.getDate() <= before.split("/")[1])) {
                text = randomSelection(text);
                text = text.replace("{year}", now.getFullYear());
                messageArray.push(text);
            }
        });
        // 农历传统节日的祝福也加入闲聊池，节日当天看板郎会主动提起
        const lunarFestival = getLunarFestival();
        if (lunarFestival) messageArray.push(`今天是${lunarFestival.name}～${lunarFestival.msg}`);
        const devtools = () => { };
        console.log("%c" + result.message.console, devtools);
        devtools.toString = () => {
            showMessage(result.message.console, 6000, 9);
        };
        window.addEventListener("copy", () => {
            showMessage(result.message.copy, 6000, 9);
        });
        window.addEventListener("visibilitychange", () => {
            if (!document.hidden) showMessage(result.message.visibilitychange, 6000, 9);
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

    function welcomeMessage(time) {
        // 农历传统节日问候：优先于时段欢迎语（solarlunar.min.js 由 index.html 预加载）
        const festival = getLunarFestival();
        if (festival) {
            return `今天是农历${festival.monthCn}${festival.dayCn}<span>「${festival.name}」</span>，${festival.msg}`;
        }
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
    	if (messageTimer) {
    		clearTimeout(messageTimer);
    		messageTimer = null;
    	}
    	text = randomSelection(text);
    	sessionStorage.setItem("waifu-text", priority);
    	let tips = document.getElementById("waifu-tips");
    	tips.innerHTML = text;
    	tips.classList.add("waifu-tips-active");
    	messageTimer = setTimeout(() => {
    		sessionStorage.removeItem("waifu-text");
    		tips.classList.remove("waifu-tips-active");
    	}, timeout);
    }

	function showHitokoto() {
		fetch("https://v1.hitokoto.cn")
			.then(response => response.json())
			.then(result => {
				showMessage(result.hitokoto, 6000, 9);
			})
			.catch(() => showMessage("一言服务暂时联系不上，我说句心里话吧：今天也要加油哦！", 6000, 9));
	}

	// ===== 农历传统节日（solarlunar.min.js 提供公历→农历换算，UMD 全局名 solarLunar）=====
	const LUNAR_FESTIVALS = [
		{ month: 1, days: [1], name: "春节", msg: ["新年快乐！给你拜年啦～恭喜发财，红包拿来！(๑>؂<๑)", "大年初一，万事从头吉，祝你好运连连！"] },
		{ month: 1, days: [15], name: "元宵节", msg: ["元宵节快乐！记得吃汤圆哦，甜的咸的都好吃～", "花灯亮起来，元宵吃起来，团圆美满！"] },
		{ month: 2, days: [2], name: "龙抬头", msg: ["二月二，龙抬头，剃个龙头，一年都有精神头！"] },
		{ month: 3, days: [3], name: "上巳节", msg: ["三月三上巳节，正是踏青赏春的好时节～"] },
		{ month: 5, days: [5], name: "端午节", msg: ["端午安康！甜粽咸粽，你站哪一队？", "粽叶飘香，龙舟竞渡，端午安康！"] },
		{ month: 7, days: [7], name: "七夕节", msg: ["七夕快乐！今天要和喜欢的人一起过哦～", "鹊桥相会的日子，祝有情人终成眷属！"] },
		{ month: 7, days: [15], name: "中元节", msg: ["中元节，记得早点回家哦…别怕，我陪你！"] },
		{ month: 8, days: [15], name: "中秋节", msg: ["中秋快乐！月亮好圆，月饼好吃，你也一样！", "但愿人长久，千里共婵娟～中秋快乐！"] },
		{ month: 9, days: [9], name: "重阳节", msg: ["重阳节，记得给家里长辈打个电话问好呀！"] },
		{ month: 12, days: [8], name: "腊八节", msg: ["腊八到啦，喝碗热腾腾的腊八粥吧，过了腊八就是年！"] },
		{ month: 12, days: [23, 24], name: "小年", msg: ["小年快乐！祭灶扫尘，准备过年咯～"] },
	];
	// 返回今天命中的农历节日 {name, monthCn, dayCn, msg}；未命中返回 null。
	// 除夕无固定日期：若明天是正月初一，今天即为除夕。闰月不参与节日匹配。
	function getLunarFestival() {
		let lib = window.solarLunar;
		// 兼容两种 UMD 导出形态：{ solar2lunar, ... } 或 { default: { solar2lunar, ... } }
		if (lib && typeof lib.solar2lunar !== "function" && lib.default) lib = lib.default;
		if (!lib || typeof lib.solar2lunar !== "function") return null;
		const now = new Date();
		const today = lib.solar2lunar(now.getFullYear(), now.getMonth() + 1, now.getDate());
		if (!today || today.lMonth == null || today.isLeap) return null;
		const tomorrow = new Date(now.getTime() + 86400000);
		const tmr = lib.solar2lunar(tomorrow.getFullYear(), tomorrow.getMonth() + 1, tomorrow.getDate());
		if (tmr && !tmr.isLeap && tmr.lMonth === 1 && tmr.lDay === 1) {
			return { name: "除夕", monthCn: today.monthCn, dayCn: today.dayCn, msg: "今天是除夕！辞旧迎新，明年也要一起加油哦！" };
		}
		for (const f of LUNAR_FESTIVALS) {
			if (f.month === today.lMonth && f.days.includes(today.lDay)) {
				return { name: f.name, monthCn: today.monthCn, dayCn: today.dayCn, msg: randomSelection(f.msg) };
			}
		}
		return null;
	}

	function randomSelection(obj) {
		// 角色台词按“组”保存：先随机选一组，再随机选组内的一句，最终始终返回字符串。
		const selected = Array.isArray(obj) ? obj[Math.floor(Math.random() * obj.length)] : obj;
		return Array.isArray(selected) ? randomSelection(selected) : selected;
	}

	// ===== 形象库（多分类 + 用户自选，见 public/live2d/model_list.json）=====
	let modelList;
	async function loadModelList() {
		let response = await fetch(`${live2d_path}model_list.json`);
		modelList = await response.json();
	}

	function getCookie(name) {
		const m = document.cookie.match(new RegExp("(?:^|;\\s*)" + name + "=([^;]*)"));
		return m ? decodeURIComponent(m[1]) : "";
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
			if (data.ret === 1 && data.widget && data.widget.model) return data.widget;
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
		loadlive2d("live2d", `${live2d_path}model/${modelName}/index.json`);
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

	// 初始化优先级：账号配置 > 本机记录 > 按昼夜默认（白天 haruto，20 点至次日 8 点 izumi）
	(async function initModel() {
		localStorage.removeItem("modelId");        // 清理旧版数字下标存档
		localStorage.removeItem("modelTexturesId");
		if (!modelList) await loadModelList();
		const ids = modelList.models.map(m => m.id);
		const widget = await fetchUserWidget();
		let model = widget && ids.includes(widget.model) ? widget.model : null;
		if (!model) {
			model = localStorage.getItem("waifu-model");
			if (!model || !ids.includes(model)) model = null;
		}
		if (!model) {
			const hour = new Date().getHours();
			model = (hour >= 20 || hour < 8) ? "izumi" : "haruto";
		}
		loadModel(model);
		fetch(`${live2d_path}waifu-tips.json`)
			.then(response => response.json())
			.then(registerEventListener);
	})();

	// ===== 形象选择器（⚙️ 按钮，按分类挑选）=====
	function openModelPicker() {
		let picker = document.getElementById("waifu-picker");
		if (picker) { picker.classList.toggle("waifu-picker-hidden"); return; }
		if (!modelList) { loadModelList().then(openModelPicker); return; }
		document.body.insertAdjacentHTML("beforeend", `<div id="waifu-picker">
			<div class="waifu-picker-panel">
				<div class="waifu-picker-head">
					<span>🎨 选择你的看板郎形象</span>
					<span class="waifu-picker-close" role="button" title="关闭">✖️</span>
				</div>
				<div class="waifu-picker-tabs"></div>
				<div class="waifu-picker-list"></div>
				<div class="waifu-picker-foot">登录后选择会保存到账号，未登录仅本机生效。<br>想添加自己的形象？把模型目录放进 public/live2d/model/，再到 model_list.json 注册即可。</div>
			</div>
		</div>`);
		picker = document.getElementById("waifu-picker");
		picker.querySelector(".waifu-picker-close").addEventListener("click", () => picker.classList.add("waifu-picker-hidden"));
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
					loadModel(m.id, `${m.name}：${m.desc}`);
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
				document.getElementById("waifu").style.bottom = 0;
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
