<template>
  <div class="app-container">
    <!-- <el-card shadow="always"> -->
    <div>
      <div class="post-toolbar" style="margin-top:-2px;">
        <el-button type="primary" plain @click="PrePage" class="PrePage_class">上一页</el-button>
        <el-link type="primary" href="https://zoujiu.blog.csdn.net/" target="_blank" style="margin-left:10px;">CSDN</el-link>
        <span hidden>
          <el-input
            v-model="postkey"
            placeholder="输入发布密钥"
            style="width: 30%; margin-left:20px;"
            class="filter-item password"
            id="elinput"
            type="password"
          />
        </span>
        <el-button
          class="filter-item"
          type="primary"
          @click="handlePost"
          style="margin-left:20px;text-align:center;"
          >
          发布
        </el-button>
        <el-button
          class="filter-item"
          type="primary"
          style="margin-left:20px;text-align:center;"
          @click="upLoadbutton"
          >
          上传图片
        </el-button>
        <el-dialog v-model="dialogFormVisible" title="上传图片" width="min(500px, 92%)">
          <el-upload
            v-model:file-list="fileList"
            class="upload-demo"
            action="/csdn/uploadImg"
            multiple
            :on-preview="handleUpPreview"
            :on-remove="handleRemove"
            :before-remove="beforeRemove"
            :limit="20"
            :on-exceed="handleExceed"
            :on-success="handleUpLoadSuccess"
            :data="data"
            :before-upload="handlebefore_Upload"
          >
            <el-button type="primary">Click to upload</el-button>
            <template #tip>
              <div class="el-upload__tip">
                jpg/png/jpeg/bmp/gif files with a size less than 13Mb.
              </div>
            </template>
          </el-upload>
        </el-dialog>
        <el-dialog v-model="draftDialogVisible" title="草稿箱" width="min(640px, 92%)">
          <el-table :data="draftList" v-loading="draftLoading" size="small" max-height="420">
            <el-table-column label="标题" show-overflow-tooltip>
              <template #default="scope">
                <span>{{ scope.row.title || '（无标题）' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="save_time" label="保存时间" width="170" />
            <el-table-column label="操作" width="160">
              <template #default="scope">
                <el-button size="small" type="primary" @click="loadDraft(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteDraft(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="!draftLoading && draftList.length===0" style="text-align:center;color:#999;padding:20px 0;">
            草稿箱空空如也，写点什么然后点【保存草稿】吧
          </div>
        </el-dialog>
        <el-button
          class="filter-item"
          type="warning"
          @click="saveDraft"
          style="margin-left:36px;text-align:center;"
          >
          保存草稿
        </el-button>
        <el-button
          class="filter-item"
          type="warning"
          plain
          @click="openDraftBox"
          style="margin-left:10px;text-align:center;"
          >
          草稿箱
        </el-button>
        <el-button
          class="filter-item"
          type="success"
          @click="handlePreview"
          style="margin-left:60px;text-align:center;"
          >
          显示Markdown
        </el-button>
        <el-button
          class="filter-item"
          type="success"
          @click="handlePreview_interval"
          style="margin-left:10px;text-align:center;"
          >
          每隔6s显示Markdown
        </el-button>
        <el-checkbox v-model="scrollChangealway" label="跟随" size="middle" 
          style="margin-left:6px;"
        />
        <!-- <span style="margin-left:20px;font-weight:600;font-size:23px;">markdown格式</span> -->
      </div>
      <div class="title-row" style="margin-top:-10px;margin-bottom: 2px;">
        <span style="margin-left:6%;font-weight:600;font-size:26px;margin-top:3px;">标题</span>
        <el-input
          v-model="title"
          placeholder="输入文篇标题"
          style="width: 60%; margin-left:20px;overflow:auto;font-size:26px;font-weight:300;"
          class="filter-item"
          id="elinput_title"
        />
      </div>
    <!-- </el-card> -->
    </div>
    <el-container>
      <el-main class="lefteditor">
        <!-- <div class="editor"> -->
          <!-- https://html.spec.whatwg.org/multipage/interaction.html#attr-contenteditable -->
          <!-- <pre class="editor__inner markdown-highlighting" contenteditable="true" style="padding: 10px 16px 315px;">
            Main1
          </pre> -->
          <textarea 
            spellcheck="false" 
            class="textarea_class" 
            id="textarea_input"
            v-model="textarea_content"
            @scroll="scrollChange"
          ></textarea>
        <!-- </div> -->
      </el-main>
      <el-main class="previewclass" id="previewHalf">
        点击【显示Markdown】按钮就可以查看左侧文本的Markdown渲染
      </el-main>
    </el-container>
  </div>
  <el-backtop :bottom="100">
    <div
      style="
        height: 100%;
        width: 100%;
        background-color: var(--el-bg-color-overlay);
        box-shadow: var(--el-box-shadow-lighter);
        text-align: center;
        line-height: 40px;
        color: #1989fa;
      "
    >
      上面
    </div>
  </el-backtop>
</template>

<script>
import axios from 'axios'
import katex from "katex"
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import Cookies from 'js-cookie';
import getusername from '/src/common.js'
// import type {UploadProps, UploadUserFile} from 'element-plus'
// import saveFile from "../../javascript/common.js"
export default {
  name: 'app',
  data() {
    return {
      title: "",
      postkey: "",
      intervalId: "",
      draft_id: "",
      draftDialogVisible: false,
      draftList: [],
      draftLoading: false,
      dialogFormVisible: false,
      elaside: "",
      save: false,
      path: "",
      fileList: "",
      old_title: "",
      dirname: "",
      textarea_content: "",
      scrollChangealway: true,
      data: {
        "title": "",
        "old_title":"",
        "path": "",
        "dirname": "",
      },
      form: reactive({
        name: '',
        region: '',
        date1: '',
        date2: '',
        delivery: false,
        type: [],
        resource: '',
        desc: '',
      }),
    }
  },
  mounted(){
    // this.clickpage();
    this.getPrimaryText();
    this.hidden_elaside();
    this.editArticleLoad();
    // 窗口尺寸变化会影响左右滚动量与锚点，重新计算
    this._onResize = () => { this.buildScrollAnchors(); };
    window.addEventListener("resize", this._onResize);
  },
  beforeUnmount(){
    // 退出编辑页时停止定时器，防止后台持续请求
    if(this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = "";
    }
    if(this._onResize) {
      window.removeEventListener("resize", this._onResize);
    }
  },
  watch: {},
  methods: {
    scrollChange(event) {
      if(!this.scrollChangealway) {
        return;
      }
      const ta = event.target;
      const pre = document.getElementById("previewHalf");
      if(!pre) {
        return;
      }
      const srcMax = ta.scrollHeight - ta.clientHeight;
      if(srcMax <= 0) {
        return;
      }
      // 有标题锚点则按锚点分段插值（图片/标题高度不同导致的失配由锚点校正），
      // 否则退回整体比例映射（保留原有行为）。
      const anchors = this._scrollAnchors;
      if(anchors && anchors.s && anchors.s.length >= 2) {
        pre.scrollTop = this.mapScrollTop(ta.scrollTop, anchors.s, anchors.p);
      } else {
        pre.scrollTop = (pre.scrollHeight - pre.clientHeight) * (ta.scrollTop / srcMax);
      }
    },
    // 在 [ss] -> [pp] 之间做分段线性插值，两端锚定 0 与最大滚动量
    mapScrollTop(v, ss, pp) {
      if(v <= ss[0]) return pp[0];
      if(v >= ss[ss.length - 1]) return pp[pp.length - 1];
      let i = 1;
      while(i < ss.length - 1 && ss[i] < v) i++;
      const x0 = ss[i - 1], x1 = ss[i], y0 = pp[i - 1], y1 = pp[i];
      if(x1 === x0) return y0;
      return y0 + (y1 - y0) * (v - x0) / (x1 - x0);
    },
    // 依据源文本标题行与右预览标题元素，构建“源滚动px -> 预览滚动px”的锚点
    buildScrollAnchors() {
      const ta = document.getElementById("textarea_input");
      const pre = document.getElementById("previewHalf");
      if(!ta || !pre) {
        this._scrollAnchors = null;
        return;
      }
      const src = this.textarea_content || ta.value || "";
      const srcIdx = [];
      const re = /^([ \t]*#{1,6}[ \t]+)[^\n]*/gm;
      let m;
      while((m = re.exec(src)) !== null) {
        srcIdx.push(m.index);
      }
      const heads = pre.querySelectorAll("h1, h2, h3, h4, h5, h6");
      const srcMax = ta.scrollHeight - ta.clientHeight;
      const preMax = pre.scrollHeight - pre.clientHeight;
      if(srcMax <= 0 || preMax <= 0) {
        this._scrollAnchors = null;
        return;
      }
      const n = Math.min(srcIdx.length, heads.length);
      const s = [0], p = [0];
      for(let i = 0; i < n; i++) {
        const sp = Math.max(0, Math.min(srcMax, this.measureSourcePx(ta, src, srcIdx[i])));
        const pp = Math.max(0, Math.min(preMax, heads[i].getBoundingClientRect().top - pre.getBoundingClientRect().top + pre.scrollTop));
        // 保证严格单调递增，避免插值分母为负或跳变
        if(sp > s[s.length - 1] && pp >= p[p.length - 1]) {
          s.push(sp);
          p.push(pp);
        }
      }
      if(s[s.length - 1] < srcMax) {
        s.push(srcMax);
        p.push(preMax);
      }
      this._scrollAnchors = s.length >= 2 ? { s, p } : null;
    },
    // 用与 textarea 完全一致样式的镜像 div 测量源文本某字符处的像素高度
    measureSourcePx(ta, src, offset) {
      let mirror = document.getElementById("_taMirror");
      if(!mirror) {
        mirror = document.createElement("div");
        mirror.id = "_taMirror";
        mirror.setAttribute("aria-hidden", "true");
        document.body.appendChild(mirror);
      }
      const cs = getComputedStyle(ta);
      const st = mirror.style;
      st.position = "absolute";
      st.left = "-10000px";
      st.top = "0";
      st.visibility = "hidden";
      st.pointerEvents = "none";
      st.width = ta.clientWidth + "px";
      st.boxSizing = cs.boxSizing;
      st.font = cs.font;
      st.fontSize = cs.fontSize;
      st.lineHeight = cs.lineHeight;
      st.letterSpacing = cs.letterSpacing;
      st.wordSpacing = cs.wordSpacing;
      st.padding = cs.padding;
      st.border = cs.border;
      st.tabSize = cs.tabSize;
      st.whiteSpace = "pre-wrap";
      st.wordBreak = "break-word";
      st.overflowWrap = "break-word";
      mirror.textContent = src.slice(0, offset);
      return mirror.scrollHeight;
    },
    // 渲染完成后刷新锚点；若预览含未加载完成的图片，等图片加载完再刷（图片高度计入滚动量）
    scheduleScrollAnchors() {
      const pre = document.getElementById("previewHalf");
      if(!pre) return;
      const imgs = Array.from(pre.querySelectorAll("img"));
      const pending = imgs.filter(im => !im.complete);
      if(pending.length === 0) {
        this.buildScrollAnchors();
        return;
      }
      let left = pending.length;
      const done = () => { if(--left <= 0) this.buildScrollAnchors(); };
      pending.forEach(im => {
        im.addEventListener("load", done, { once: true });
        im.addEventListener("error", done, { once: true });
      });
    },
    async clickpage() {
      const instance = axios.create({
        baseURL: '/csdn/clickpage',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      await instance({
        method: 'GET',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        params: {'type' : 'post'},
      }).then((response) => {
      });
    },
    async getPrimaryText() {
      const instance = axios.create({
        baseURL: '/csdn/getPrimaryText',
       timeout: 20000,
      });
      
      // console.log(this.search_param);
      await instance({
        method: 'GET',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
      }).then((response) => {
        this.textarea_content = response.data.text;
      });
      // let sharet = "45c144247124160a29e93a160e62bc7128bd33a9da552c1b9441d562240754637b38e5a25fa151044e902b99ff22ec91ffa9e9e0e2edde67317cc04adf329b78";
      // this.sha(this.postkey).then((r)=>{
      //   if(sharet == r) {
      //     this.dialogFormVisible = true;
      //   } else {
      //     this.$alert("发布密钥不正确，自动取消上传");
      //   }
      // });
    },
    hidden_elaside() {
      this.elaside = document.getElementById("elaside");
      this.elaside.hidden = true;
    },
    async upLoadbutton() {
      if(this.intervalId) {
        ElMessage("关闭【每隔6s显示Markdown】");
        clearInterval(this.intervalId);
      }
      const instance = axios.create({
        baseURL: '/csdn/renzheng',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      let gu;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      instance({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        withCredentials: true,
        data: {"postkey":this.postkey},
      }).then((response) => {
        if(response.data.ret || (gu && gu.ret == 1)) {
          this.dialogFormVisible = true;
        } else {
          // this.$alert("发布密钥不正确，自动取消上传");
          ElMessage.error("没有登陆自动取消上传");
        }
      });
      // this.postkey = "";
      // let sharet = "45c144247124160a29e93a160e62bc7128bd33a9da552c1b9441d562240754637b38e5a25fa151044e902b99ff22ec91ffa9e9e0e2edde67317cc04adf329b78";
      // this.sha(this.postkey).then((r)=>{
      //   if(sharet == r) {
      //     this.dialogFormVisible = true;
      //   } else {
      //     this.$alert("发布密钥不正确，自动取消上传");
      //   }
      // });
    },
    async editArticleLoad() {
      let gu;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      if(gu && gu.ret > 0) {
        let input = document.getElementsByClassName("password");
        input[0].setAttribute('disabled', "true");
        // delete input.disabled;
      }
      this.draft_id = ""; // 进入编辑页时清掉草稿上下文；载入/保存草稿时再重新设置
      this.path = this.$router.currentRoute._value.query.plan;
      if(!this.path) {
        return;
      }
      this.data.path = this.path;
      // console.log(this.path);
      const instance = axios.create({
        baseURL: '/csdn/editArticle',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      instance({
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
        },
        params: {"path": this.path},
        withCredentials: true,
      }).then((response) => {
        this.title = response.data.title;
        this.old_title = response.data.title;
        this.dirname = response.data.dirname;
        this.data.dirname = response.data.dirname;
        this.data.old_title = response.data.title;
        this.textarea_content = response.data.markdown;
        this.setTextarea(response.data.markdown);
        let textarea_input = document.getElementById("textarea_input");
        // console.log(textarea_input.value);
        // console.log(response.data.markdown);
        if(textarea_input.value!=response.data.markdown) {
          textarea_input.value = response.data.markdown;
          this.textarea_content = response.data.markdown;
        }
        this.axiospost(response.data.markdown);
      });
    },
    setTextarea(txt="") {
      this.textarea_content = txt;
    },
    async draftRequest(url, payload) {
      const instance = axios.create({ baseURL: url, timeout: 20000 });
      const response = await instance({
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
        data: payload,
        withCredentials: true,
      });
      return response.data;
    },
    async saveDraft() {
      const mail = Cookies.get("mail");
      const password = Cookies.get("password");
      if(!mail || !password) {
        ElMessage.error("请先登录后再保存草稿");
        return;
      }
      if(this.title.trim()==="" && this.textarea_content.trim()==="") {
        ElMessage.error("标题和内容不能同时为空");
        return;
      }
      try {
        const r = await this.draftRequest('/csdn/save_draft', {
          mail: mail, password: password,
          title: this.title, markdown: this.textarea_content,
          draft_id: this.draft_id || "",
        });
        if(r.ret === 1) {
          this.draft_id = r.draft_id;
          ElMessage.success("草稿已保存");
        } else {
          ElMessage.error(r.msg || "草稿保存失败");
        }
      } catch(e) {
        ElMessage.error("草稿保存失败");
      }
    },
    async openDraftBox() {
      const mail = Cookies.get("mail");
      const password = Cookies.get("password");
      if(!mail || !password) {
        ElMessage.error("请先登录后查看草稿箱");
        return;
      }
      this.draftDialogVisible = true;
      this.draftLoading = true;
      try {
        const r = await this.draftRequest('/csdn/draft_list', { mail: mail, password: password });
        if(r.ret === 1) {
          this.draftList = r.drafts || [];
        } else {
          this.draftList = [];
          ElMessage.error(r.msg || "草稿列表获取失败");
        }
      } catch(e) {
        this.draftList = [];
        ElMessage.error("草稿列表获取失败");
      } finally {
        this.draftLoading = false;
      }
    },
    async loadDraft(item) {
      try {
        const r = await this.draftRequest('/csdn/draft_get', {
          mail: Cookies.get("mail"), password: Cookies.get("password"), id: item.id,
        });
        if(r.ret === 1) {
          // 草稿是新文章：清掉文章编辑态，回填标题与内容
          this.path = "";
          this.old_title = "";
          this.dirname = "";
          this.data.path = "";
          this.data.old_title = "";
          this.data.dirname = "";
          this.title = r.title;
          this.textarea_content = r.markdown;
          this.setTextarea(r.markdown);
          this.draft_id = r.id;
          this.draftDialogVisible = false;
          ElMessage.success("草稿已载入，可继续编辑");
        } else {
          ElMessage.error(r.msg || "草稿读取失败");
        }
      } catch(e) {
        ElMessage.error("草稿读取失败");
      }
    },
    deleteDraft(item) {
      this.$confirm(`确定删除草稿【${item.title || '（无标题）'}】？`, "删除确认", {type: 'warning'})
        .then(async () => {
          try {
            const r = await this.draftRequest('/csdn/draft_delete', {
              mail: Cookies.get("mail"), password: Cookies.get("password"), id: item.id,
            });
            if(r.ret === 1) {
              if(this.draft_id === item.id) {
                this.draft_id = "";
              }
              ElMessage.success("草稿已删除");
              this.openDraftBox();
            } else {
              ElMessage.error(r.msg || "草稿删除失败");
            }
          } catch(e) {
            ElMessage.error("草稿删除失败");
          }
        }).catch(() => {});
    },
    handlePreview() {
      if(this.intervalId) {
        clearInterval(this.intervalId);
      }
      ElMessage("显示Markdown，并关闭【每隔6s显示Markdown】");
      this.save = false;
      // console.log(this.textarea_content);
      this.axiospost(this.textarea_content);
    },
    async handlePreview_interval() {
      const instance = axios.create({
        baseURL: '/csdn/renzheng',
       timeout: 20000,
      });

      let gu;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      
      // console.log(this.search_param);
      instance({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        withCredentials: true,
        data: {"postkey":this.postkey},
      }).then((response) => {
        if(response.data.ret || (gu && gu.ret == 1)) {
          this.$confirm("每隔6s显示Markdown").then(()=>{
              this.intervalId = setInterval(() => {
              this.save = false;
              this.axiospost();
            }, 6000);
          })
        } else {
          // this.$alert("发布密钥不正确");
          ElMessage.error("发布密钥不正确");
        }
      });
      this.postkey = "";
    },
    async axiospost(textarea_content="") {
      if(textarea_content.length==0) {
        textarea_content = this.textarea_content;
      }
      if(this.intervalId && this.save) {
        ElMessage("关闭【每隔6s显示Markdown】");
        clearInterval(this.intervalId);
      }
      const instance = axios.create({
        baseURL: '/csdn/postArticle',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      let pt = "";
      if(this.path) {
        pt = this.path;
      }
      let gu, mail="";
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      if(gu && gu.ret > 0) {
        mail = gu.mail;
      }
      await instance({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
        },
        data: {"textarea": textarea_content, "title": this.title, 
               "save": this.save, "old_title":this.old_title, "dirname":this.dirname, 
               "path":pt, 'mail':mail},
        withCredentials: true,
      }).then((response) => {
        // alert(response);
        // console.log(response.data);
        // console.log(response.type);
        // console.log(response.status);
        // console.log(response.statusText);
        // console.log(response.headers);
        // console.log(response.config);
        this.result = response.data.markdown;
        this.path = response.data.path;
        let preview = document.getElementById("previewHalf");
        // console.log(this.result);
        preview.innerHTML = this.result;

        let katex_element_collect = document.getElementsByClassName("katexspan");
        let len = katex_element_collect.length;
        for(let i = 0; i < len; i++) {
          let kec = katex_element_collect[i];
          katex.render(kec.outerText, kec, {
            throwOnError: false
          });
        }

        // 预览刚更新，先失效旧锚点，再按图片加载情况重建（图片高度计入后才准确）
        this._scrollAnchors = null;
        this.scheduleScrollAnchors();
      });
    },
    postarticle() {
      this.$router.push({ path: '/csdn/post_article/*'});
    },
    async sha(str) { 
      const textEncoder = new TextEncoder(); 
      const message = textEncoder.encode(str); 
      // Cannot read properties of undefined (reading 'digest')
      // https://stackoverflow.com/questions/46670556/how-to-enable-crypto-subtle-for-unsecure-origins-in-chrome/46671627#46671627
      // https://github.com/RBND-studio/flows-js/issues/186
      const messageDigest = await crypto.subtle.digest('SHA-512', message); 
      const hexDigest = Array.from(new Uint8Array(messageDigest)) 
      .map((x) => x.toString(16).padStart(2, '0')) 
      .join(''); 
      // console.log(hexDigest); 
      return hexDigest;
    },
    async handlePost() {
      /*
      # title

      ## input

      $\frac{1}{6}$

      * number one
      * number

      **strong**

      > reference

      */
      // let textarea_input = document.getElementById("textarea_input");
      // let elinput = document.getElementById("elinput");
      // console.log(textarea_input);
      // console.log(elinput);
      // console.log(this.postkey);
      // console.log(this.textarea_content);
      // console.log(this.sha(this.postkey));
      if(this.intervalId) {
            ElMessage("关闭【每隔6s显示Markdown】");
            clearInterval(this.intervalId);
      }
      const instance = axios.create({
        baseURL: '/csdn/renzheng',
       timeout: 20000,
      });
      
      // console.log(this.search_param);
      let gu;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      await instance({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        withCredentials: true,
        data: {"postkey":this.postkey},
      }).then(async (response) => {
        if(response.data.ret || (gu && gu.ret == 1)) {
          // console.log(r);
          this.save = true;
          const instan = axios.create({
            baseURL: '/csdn/postArticle',
            timeout: 20000,
          });
          
          // console.log(this.search_param);
          let pt = "";
          if(this.path) {
            pt = this.path;
          }
          let gu;
          await getusername(document.URL).then((response) => {
            gu = response;
          });
          await instan({
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-Requested-With': 'XMLHttpRequest',
            },
            data: {"textarea": this.textarea_content, "title": this.title, 'postkey':this.postkey,
                  "save": this.save, "old_title":this.old_title, "dirname":this.dirname, 
                  'url':document.URL,
                  "path":pt, "mail" : Cookies.get("mail"), "password":Cookies.get("password")},
            withCredentials: true,
          }).then(async (response) => {
            this.result = response.data.markdown;
            this.path = response.data.path;
            // this.$alert("发布成功了的");
            ElMessage.success("发布成功了的");
            if(this.draft_id) {
              // 发布成功后自动移除对应草稿
              const draft_payload = {"mail": Cookies.get("mail"), "password": Cookies.get("password"), "id": this.draft_id};
              const draft_inst = axios.create({ baseURL: '/csdn/draft_delete', timeout: 20000 });
              draft_inst({
                method: 'POST',
                headers: {'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest'},
                data: draft_payload,
              }).then((resp) => {
                if(resp.data && resp.data.ret === 1) {
                  ElMessage("对应草稿已从草稿箱移除");
                }
              }).catch(() => {});
              this.draft_id = "";
            }
            this.elaside.hidden = false;
            // this.$router.go(-2);
            if(this.path) {
              let zhihu = this.path.indexOf("zhihu_");
              // console.log("zhihu");
              // console.log(zhihu);
              if(zhihu >= 0) {
                this.$router.push({ path: '/zhihu/*',});
              } else {
                if(gu && gu.ret > 0) {
                  // this.$router.push({ path: '/csdn/' + gu.mail,});
                  this.$router.push({ path: '/csdn/' + gu.urlmail,  query:{"currentpage": Cookies.get("csdn"), "pagesize": Cookies.get("csdnpage")}});
                } else {
                  // this.$router.push({ path: '/csdn/zj',});
                  this.$router.push({ path: '/csdn/homepage@gmail.com',});
                }
              } 
            } else {
              this.$router.push("/");
            }
          })
        } else {
          // this.$alert("发布密钥不正确，自动取消发布");
          ElMessage.error("没有登陆自动取消发布");
        }
      });
      this.postkey = "";
      // let sharet = "45c144247124160a29e93a160e62bc7128bd33a9da552c1b9441d562240754637b38e5a25fa151044e902b99ff22ec91ffa9e9e0e2edde67317cc04adf329b78";
      // this.sha(this.postkey).then((r)=>{
      //   if(sharet == r) {
      //     // console.log(r);
      //     if(this.intervalId) {
      //       ElMessage("关闭【每隔6s显示Markdown】");
      //       clearInterval(this.intervalId);
      //     }
      //     this.save = true;
      //     this.axiospost();
      //     this.$alert("发布成功了的");
      //     this.elaside.hidden = false;
      //     this.$router.go(-2);
      //   } else {
      //     this.$alert("发布密钥不正确，自动取消发布");
      //   }
      // });
    }, 
    async PrePage() {
      this.title="";
      this.postkey="";
      this.save=false;
      this.draft_id="";
      this.textarea_content="";
      this.old_title = "";
      this.dirname = "";
      if(this.intervalId) {
        clearInterval(this.intervalId);
      }
      this.elaside.hidden = false;
      this.data.dirname   = "";
      this.data.old_title = "";
      this.data.title     = "";
      this.data.path      = "";
      // this.$router.go(-1);
      let gu;
      this.elaside = document.getElementById("elaside");
      this.elaside.hidden = false;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      if(this.path) {
        let zhihu = this.path.indexOf("zhihu_");
        // console.log("zhihu");
        // console.log(zhihu);
        if(zhihu >= 0) {
          this.$router.push({ path: '/zhihu/*',});
        } else {
          if(gu && gu.ret > 0) {
            // this.$router.push({ path: '/csdn/' + gu.urlmail});
            this.$router.push({ path: '/csdn/' + gu.urlmail,  query:{"currentpage": Cookies.get("csdn"), "pagesize": Cookies.get("csdnpage")}});
          } else {
            // this.$router.push({ path: '/csdn/zj'});
            // this.$router.push({ path: '/csdn/homepage@gmail.com'});
            this.$router.push({ path: '/csdn/homepage@gmail.com',  query:{"currentpage": Cookies.get("csdn"), "pagesize": Cookies.get("csdnpage")}});
          }
        } 
      } else {
        if(gu && gu.ret > 0) {
          // this.$router.push({ path: '/csdn/' + gu.urlmail});
          this.$router.push({ path: '/csdn/' + gu.urlmail,  query:{"currentpage": Cookies.get("csdn"), "pagesize": Cookies.get("csdnpage")}});
        } else {
          // this.$router.push({ path: '/csdn/zj'});
          // this.$router.push({ path: '/csdn/homepage@gmail.com'});
          this.$router.push({ path: '/csdn/homepage@gmail.com',  query:{"currentpage": Cookies.get("csdn"), "pagesize": Cookies.get("csdnpage")}});
        }
      }
      // this.$router.push({ path: '/csdn/markdown_detail', hash: '#csdn/markdown_detail', query: { plan: this.path }});
    },
    handleRemove(file, uploadFiles) {
      // console.log(file, uploadFiles)
    },

    handleUpPreview(uploadFile) {
      // console.log(uploadFile)
    },

    handleExceed(files, uploadFiles) {
      ElMessage.warning(
        `最多上传 20 张图片，本次选择了 ${files.length} 张，合计 ${
          files.length + uploadFiles.length
        } 张`
      )
    },

    beforeRemove(uploadFile, uploadFiles) {
      ElMessage.warning(
        `Cancel the transfer of ${uploadFile.name} `
      )
    },
    handlebefore_Upload(rawFile) {
      if(this.intervalId) {
        ElMessage("关闭【每隔6s显示Markdown】");
        clearInterval(this.intervalId);
      }
      if(this.title == "" || this.title.length < 6) {
        ElMessage.error('上传前需要先填写完整标题!');
        return false;
      } else if (rawFile.type !== 'image/jpeg' && rawFile.type !== "image/png"
                && rawFile.type !== "image/gif" && rawFile.type !== "image/bmp"
                && rawFile.type !== "image/jpg") {
        ElMessage.error('不是图片格式!');
        return false;
      } else if (rawFile.size / 1024 / 1024 > 13) {
        ElMessage.error('图片占用磁盘大小不能 > 13MB!');
        return false;
      }
      this.data.title = this.title;
      this.data.postkey = this.postkey;
      this.data.mail = Cookies.get("mail");
      this.data.url = document.URL;
      this.data.password = Cookies.get("password");
      return true;
    },
    handleUpLoadSuccess(response) {
      // console.log("success");
      // console.log(response);
      if(this.intervalId) {
        ElMessage.warning("关闭【每隔6s显示Markdown】");
        clearInterval(this.intervalId);
      }
      this.data.mail = "";
      this.data.password = "";
      this.data.dirname = response.dirname;
      this.data.old_title = response.title;
      this.data.path = response.path;
      this.path = response.path;
      this.data.title = this.title;
      this.old_title = this.title;
      this.dirname = response.dirname;
      this.textarea_content += response.uploadname;
      this.data.url = "";
      this.handlePreview();
      ElMessage.warning("图片在左侧最底下！");
    }
  },
}
</script>

<style scoped>
:deep(table thead tr th) {
    vertical-align: bottom;
    /* border-bottom: 2px solid #ddd; */
    /* background-color: #c7254e; */
}
:deep(table) {
    display: block;
    width: 100%;
    width: max-content;
    max-width: 100%;
    overflow: auto;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    font-size: 16px;
    line-height: 1.5;
    word-wrap: break-word;
    background-color: #ffffff;
    /* border-top: 2px solid #ddd; */
    border-bottom: 2px solid #ddd;
    /* font-variant: tabular-nums; */
}
:deep(hr) {
    display: block;
    margin-block-start: 0.5em;
    margin-block-end: 0.5em;
    margin-inline-start: auto;
    margin-inline-end: auto;
    unicode-bidi: isolate;
    overflow: hidden;
    border-style: inset;
    border-width: 1px;

    margin-top: 30px;
    margin-bottom: 20px;
    border: 0;
    border-top: 1px solid #6c6a6a;
    width: 50%;
}
:deep(table th) {
  font-weight: 600;
}
:deep(table th:nth-child(odd)) {
  background-color: #c8ecf2;
}
:deep(table th, table td) {
  padding: 6px 13px;
  border-top: 2px solid #ddd;
  border-bottom: 2px solid #ddd;
  /* border: 1px solid var(--borderColor-default, var(--color-border-default)); */
}
:deep(table thead tr th, table tbody tr th,
      table tfoot tr th, table thead tr td, 
      table tbody tr td, table tfoot tr td) {
    /* padding: 8px; */
    line-height: 1.42857143;
    vertical-align: top;
    /* border-top: 1px solid #ddd; */
    border-top: 2px solid #ddd;
    border-left: 2px solid #ddd;
    border-right: 2px solid #ddd;
    /* border-bottom: 2px solid #ddd; */
    padding: 6px 13px;
}
:deep(tbody tr:nth-child(odd) td, 
      tbody tr:nth-child(odd) th) {
  background-color: #f9f9f9;
}
:deep(tbody tr td:nth-child(odd), 
      tbody tr th:nth-child(odd)) {
  background-color: #c8ecf2;
}
:deep(tbody tr td:nth-child(even), 
      tbody tr th:nth-child(even)) {
  background-color: #f9f9f9;
}
:deep(tbody tr:nth-child(even) td, 
      tbody tr:nth-child(even) th) {
  background-color: #b4c3f8;
  color:#ffffff;
}
:deep(thead) {
    display: table-header-group;
    vertical-align: middle;
    unicode-bidi: isolate;
    border-color: inherit;
}
:deep(tbody) {
    display: table-row-group;
    vertical-align: middle;
    unicode-bidi: isolate;
    border-color: inherit;
}
:deep(tr) {
    display: table-row;
    vertical-align: inherit;
    unicode-bidi: isolate;
    border-color: inherit;
}
:deep(td) {
    display: table-cell;
    vertical-align: inherit;
    unicode-bidi: isolate;
    border-top: 1px solid #ddd;
    border-left: 1px solid #ddd;
    border-right: 1px solid #ddd;
}
:deep(.warningclass) {
  background-color: palegoldenrod;
  padding-left: 6px;
  padding-right: 6px;
  padding-top: 1px;
  padding-bottom: 1px;
}
textarea {
  width: 100%;
  height: 100vh;
}

:deep(.editor__inner) {
  margin: 0;
  font-family: -apple-system,SF UI Text,Arial,PingFang SC,Hiragino Sans GB,Microsoft YaHei,WenQuanYi Micro Hei,sans-serif;
  font-variant-ligatures: no-common-ligatures;
  white-space: pre-wrap;
  word-break: break-word!important;
  border: 0px solid #ffffff;
}

:deep(.markdown-highlighting) {
  color: #4d4d4d;
  caret-color: #000;
  font-family: inherit;
  font-size: inherit;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: antialiased;
  font-weight: 400;
}
/*
  font-weight: 100;
*/

.editor {
  position:absolute;
  width: 42%;
  height: 100%;
  overflow: auto;
  border: 0px solid #ffffff;
}

.lefteditor {
  width: 50%;
  height: 82vh;
  background-color: #ffeeee;
  border: 0px solid #ffffff;
  padding: 2px;
}

.textarea_class {
  border: 0px solid #ffffff;
  height: 98%;
  font-size: 1.1em;
  color: #000000;
  background-color: #ffffff;
}

.previewclass {
  width: 50%;
  height: 82vh;
  background-color: #eeffee;
}

.app-container {
  height: 100%;
}

.demo-left {
  background: #444;
  display: -ms-flexbox;
  display: flex;
  -ms-flex-direction: column;
  flex-direction: column;
}

:deep(.preview_img) {
  width: 79%;
  overflow:auto;
}

.el-card-detail {
  width: 80%;
  color: #00ff00;
  margin-top: 3px;
  margin-left: 10%;
  margin-right: 10%;
}

.el-card-detail:hover {
  outline: 1 !important;
  color: #6681fa !important;
  background: #79bbff !important;
}
.el-card-detail:active {
  color: #eeffee !important;
  background: #eeaaee !important;
}
.el-card-detail.is-active {
  color: #337ecc !important;
  background: #ffeeee !important;
}

:deep(h1) {
  display: block;
  font-size: 4.5vh;
  margin-block-start: 0.67em;
  margin-block-end: 0.67em;
  margin-inline-start: 0px;
  margin-inline-end: 0px;
  font-weight: bold;
  unicode-bidi: isolate;
}
:deep(h2) {
  clear: left;
  margin-top: 0.6em;
  margin-bottom: 0.2em;
  font-size: 3.6vh;
  line-height: 1.1;
  font-weight: bold;
}

:deep(h3) {
  clear: left;
  margin-top: 0.5em;
  margin-bottom: 0.2em;
  font-size: 2.9vh;
  line-height: 1.1;
  font-weight: bold;
}

:deep(h4) {
  clear: left;
  margin-top: 0.4em;
  margin-bottom: 0.1em;
  font-size: 2.3vh;
  line-height: 1.1;
  font-weight: bold;
}

:deep(strong) {
  font-weight: 790;
}

:deep(p strong) {
  font-weight: 790;
}

:deep(p code) {
  padding: 2px;
  /* margin: 0 0 3px; */
  background-color: #f9f2f4;
  border-radius:2px;
  color:#c7254e;
  /* overflow: auto; */
  font-weight:600;
}

:deep(blockquote p) {
  display: block;
  padding: 16px;
  margin: 0 0 24px;
  border-left: 8px solid #dddfe4;
  background: #eef0f4;
  overflow: auto;
  word-break: break-word!important;
}

:deep(h5, h6) {
  clear: left;
  margin-top: 0.3em;
  margin-bottom: 0.1em;
  font-size: 1.9vh;
  line-height: 1.0;
  font-weight: bold;
}

:deep(p) {
  margin: 1.4em 0;
  display: block;
  margin-block-start: 1em;
  margin-block-end: 1em;
  margin-inline-start: 0px;
  margin-inline-end: 0px;
  unicode-bidi: isolate;
  word-break: break-word;
  line-height: 1.6;
  font-family: -apple-system,BlinkMacSystemFont,Helvetica Neue,PingFang SC,var(--zFontSansSerif),Microsoft YaHei,Source Han Sans SC,Noto Sans CJK SC,WenQuanYi Micro Hei,sans-serif;
  font-size: 1.1em;
}

:deep(*, *::before, *::after) {
  /* box-sizing: border-box; */
  /* margin: 0; */
  /* font-weight: normal; */
}

:deep(.codestyle) {
  display: block;
  padding: 1px;
  margin: 0 0 2px;
  color:#000000;
  font-weight:600;
  background-color: #f2f3f4;  /* ffeeee f2f3f4;*/
  border-left: 8px solid #16dd30;
  overflow: auto;
  word-break: break-word!important;
  height: auto;
}

:deep(.writing_margin) {
  overflow:auto;
  margin-top: 6px;
  margin-left: 20px;
  margin-right: 10px;
  margin-bottom: 6px;
}

.PrePage_class {
  margin-top:10px;
  margin-bottom:0px;
  margin-left:3px;
}

/* 手机端适配：工具栏按钮换行、标题输入占满、编辑器与预览改为上下堆叠 */
@media (max-width: 768px) {
  .post-toolbar .el-button {
    margin-left: 6px !important;
    margin-top: 6px;
  }

  .title-row > span {
    margin-left: 6px !important;
  }

  .title-row .el-input {
    width: 100% !important;
    margin-left: 0 !important;
    margin-top: 4px;
  }

  .app-container .el-container {
    flex-direction: column;
  }

  .lefteditor,
  .previewclass {
    width: 100%;
  }

  .previewclass :deep(img) {
    max-width: 100%;
    height: auto;
  }
}

</style>
