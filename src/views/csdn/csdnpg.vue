<template>
  <div class="app-container">
    <!-- <el-card shadow="always"> -->
      <div id='csdnpg' class="search-toolbar">
        <el-link type="primary" id='csdnpglink' href="https://zoujiu.blog.csdn.net/" target="_blank">CSDN</el-link>
        <el-input
          v-model="search_param.search"
          placeholder="标题、日期或者内容, 空格 分隔"
          class="filter-item search-input"
          clearable
          @keyup.enter="handleSearch"
        />
        <el-button
          class="filter-item"
          type="primary"
          @click="handleSearch"
          >
          搜索
        </el-button>
        <el-button
          class="filter-item"
          @click="resetSearch"
          >
          重置
        </el-button>
        <el-checkbox
          v-model="checke" label="包含leetcode和PAT"
          :true-value="1"
          :false-value="0"
          border
          @Change="handleCheckbox"/>
        <el-button
          class="filter-item toolbar-push"
          type="success"
          @click="postarticle"
          >
          发表
        </el-button>
      </div>
    <!-- </el-card> -->
    <el-card
      v-for="o in result"
      :key="o" 
      class="el-card-detail"
      shadow="always"
      style="overflow:auto;"
    >
      <template #header>
        <div class="card-header" style="font-size: 20px; font-weight: 600; color: #000000; background-color: #FF00FF; overflow:auto;" @click="cardClick" v-if="o.isTop">
          <span @click="cardClick"> {{ o["title"] }}</span>
          <span class="top-badge" @click="cardClick" style="margin-left: 10vh; background-color: #1989fa;color:#ffffff; font-weight: 900;">TOP</span>
          <span hidden><p :hidden="true" @click="cardClick" class="hiddenp"> {{ o["path"] }} </p></span>
        </div>
        <div class="card-header" style="font-size: 20px; color: #000000; background-color: #ffffff; overflow:auto;" @click="cardClick" v-if="!o.isTop">
          <span @click="cardClick"> {{ o["title"] }} </span>
          <span hidden><p :hidden="true" @click="cardClick" class="hiddenp"> {{ o["path"] }} </p></span>
        </div>
      </template>
      <span style="width:60%; font-size: 16px; color: #000000;" @click="cardClick">
        {{ o["markdown"] }}
      </span>
      <span hidden><p :hidden="true" @click="cardClick" class="hiddenp"> {{ o["path"] }} </p></span>
      <template #footer>
        <el-row :gutter="0">
          <el-col :span="2" :push="0">
            <div class="zanzan" @click="upvoteclick" v-if="o.click" style="background-color:rgb(159.5, 206.5, 255);font-weight:600;">
              <!-- <span style="color:#000000;"> -->
                <!-- <el-icon size="20" color="#100ee0"><CaretTop /></el-icon> -->
              {{ o['upvote'].length }}👍赞
              <span hidden><p :hidden="true" class="hiddenp"> {{o["click"]}} {{ o["path"] }} </p></span>
              <!-- </span> -->
            </div>
            <div class="zanzan" @click="upvoteclick" v-if="!o.click" style="background-color:rgba(23, 114, 246, .1);">
              <!-- <span style="color:#000000;"> -->
                <!-- <el-icon size="20" color="#100ee0"><CaretTop /></el-icon> -->
              {{ o['upvote'].length }}👍赞
              <span hidden><p :hidden="true" class="hiddenp"> {{o["click"]}} {{ o["path"] }} </p></span>
              <!-- </span> -->
            </div>
          </el-col>
          <el-col :span="2" :pull="0">
            <div class="pinglun">
              <span style="color:rgba(23, 114, 246);" @click="commentdialog" id="pinglunpinglun">{{ o['comment'].length }}评论</span>
              <span hidden><p :hidden="true" class="hiddenp"> {{ o["path"] }} </p></span>
            </div>
          </el-col>
          <el-col :span="2" :pull="0">
            <div class="shoucangshoucang" @click="shoucang" v-if="o.clickshoucang" style="background-color:rgb(159.5, 206.5, 255);font-weight:600;">
              {{ o['kshoucang'].length }}收藏
              <span hidden><p :hidden="true" class="hiddenp"> {{o["clickshoucang"]}} {{ o["path"] }} </p></span>
            </div>
            <div class="shoucangshoucang" @click="shoucang" v-if="!o.clickshoucang" style="background-color:rgba(23, 114, 246, .1);">
              {{ o['kshoucang'].length }}收藏
              <span hidden><p :hidden="true" class="hiddenp"> {{o["clickshoucang"]}} {{ o["path"] }} </p></span>
            </div>
            <!-- <div class="zanzan">
              <span style="color:rgba(23, 114, 246);" @click="shoucang">{{ o['kshoucang'].length }}收藏</span>
              <span hidden><p :hidden="true" class="hiddenp"> {{o["clickshoucang"]}} {{ o["path"] }} </p></span>
            </div> -->
          </el-col>
          <el-col :span="2" :pull="0">
            <div class="zhuanfa" @click="forwardArticle" style="color:rgba(23, 114, 246);cursor:pointer;">
              🔁转发
              <span hidden><p :hidden="true" class="hiddenp"> {{ o["path"] }} </p></span>
            </div>
          </el-col>
          <!-- 时间列：赞/评/藏/转发各 2 格共 8 格，这里 16 格正好补满 24 格，
               之前 18 格导致总跨度 26 > 24，时间被挤到第二行 -->
          <el-col :span="16">
            <div class="card-footer" style="overflow:auto; font-size: 16px; color: #0000ee;" @click="cardClick">
              <span @click="cardClick"> {{ o["date"] }} </span>
              <span hidden><p :hidden="true" class="hiddenp"> {{ o["path"] }} </p></span>
            </div>
          </el-col>
        </el-row>
      </template>
    </el-card>
    <el-dialog v-model="commentvisible" title="评论" width="90%" style="height:96%;margin-top:6px;">
      <textarea 
        spellcheck="false"
        id="textarea_input"
        v-model="textarea_content"
        style="width:100%;height:auto;overflow: auto;"
      >
      </textarea>
      <br>
      <el-button @click="uploadComment">
        提交
      </el-button>
      <br>
      <!-- <span       
        id="commentsigleid"
      ></span> -->
      <span       
        v-for="oh in commentsigle"
        :key="oh"
        id="commentsigleid"
      >
        <span style="font-weight:600;color:rgb(121.3, 187.1, 255);">
          
          <a :href="oh[0]" target="_blank">
            <span>{{ oh[4] }}---</span>{{ oh[3] }}
          </a>
          ：
        </span>
        <span style="font-weight:300;color:#000000;">{{ oh[1] }}</span>
        <span style="font-weight:600;color:rgb(121.3, 187.1, 255);">{{ oh[2] }}</span>
        <br>
      </span>
    </el-dialog>
  </div>
  <el-pagination 
    layout='total, sizes, prev, pager, next, jumper'
    :page-sizes="[6,10,20,30,60,100]"
    background
    v-model:page-size="search_param.pagesize"
    v-model:current-page="search_param.currentpage"
    :total="total"
    @size-change="page_Size_Change"
    @update:current-page="current_Page_Change"
    style="margin-left:20%; margin-top:20px; margin-bottom: 20px;"
  />
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
import Cookies from 'js-cookie';
import { ElMessage, ElMessageBox } from 'element-plus'
import getusername, { getCookieDays } from '/src/common.js'
import { toggleRowStatus } from 'element-plus/es/components/table/src/util';
export default {
  name: 'app',
  data() {
    return {
      total: 0,
      result: [],
      commentvisible:false,
      textarea_content: "",
      dire_path: "",
      checke: 1,
      shoucangEle: "",
      commentsigle:[],
      nowpage: Number(this.$router.currentRoute._value.query.currentpage) || 1,
      nowpagesize: Number(this.$router.currentRoute._value.query.pagesize) || 30,
      search_param: {
        currentpage: Number(this.$router.currentRoute._value.query.currentpage) || 1,
        pagesize: Number(this.$router.currentRoute._value.query.pagesize) || 30,
        search: "",
        reset: 0,
        checke: 0,
      },
    }
  },
  mounted(){
    this.clickpage();
    this.axiosget();
  },
  watch: {
    // $router.path,
  },
  methods: {
    clickpage() {
      if(Cookies.get("checke")) {
        this.checke = parseInt(Cookies.get("checke"));
      }
      // const instance = axios.create({
      //   baseURL: '/csdn/clickpage',
      //   timeout: 20000,
      // });
      
      // // console.log(this.search_param);
      // await instance({
      //   method: 'GET',
      //   headers: {
      //     'X-Requested-With': 'XMLHttpRequest'
      //   },
      //   params: {'type' : 'csdn'},
      // }).then((response) => {
      // });
    },
    async shoucang(event) {
      let id = document.URL;
      id = id.substring(0, 50);
      let index = id.indexOf("/zj");

      if(!Cookies.get("mail") && index < 0) {
        ElMessage.error("没有登陆不能操作！");
        return
      }
      this.search(event.srcElement);
      let star = this.dire_path.indexOf(" ");
      // 兜底：卡片隐藏节点没取到时 dire_path 无空格，继续走会拼出垃圾 path 打到后端
      if(star < 0) {
        ElMessage.error("操作异常，请刷新页面后重试！");
        return;
      }
      // let first = this.dire_path.split(" ");
      let first = [this.dire_path.substring(0, star)];
      first[1] = this.dire_path.substring(star + 1);
      let clicka = true;
      if(first[0]=='false') {
        clicka = false;
      }
      let path = first[1];

      let title = "";
      for(let i = 0; i < this.result.length; i++) {
        if(this.result[i]['path']==path) {
          title = this.result[i]['title'];
          break
        }
      }

      let kkk = event.srcElement.innerText;
      let pinglunEle = event.srcElement;
      let k0 = kkk.substring(kkk.length - 2);
      let k1 = Number(kkk.substring(0, kkk.length - 2));

      // let file = event.srcElement.childNodes[3].childNodes[0].innerHTML;
      // console.log(event, this.dire_path, first, k0, k1, path ,clicka);
      if(clicka) {
        clicka = false;
        k1 = Math.max(0, k1 - 1);
        event.srcElement.innerHTML = `${k1.toString()}${k0} <span hidden><p :hidden="true" class="hiddenp">false ${path}</p></span>`;
        // event.target.style.setProperty("background-color", "rgba(23, 114, 246, .1)");
      } else {
        clicka = true;
        k1 = Math.max(0, k1 + 1);
        event.srcElement.innerHTML = `${k1.toString()}${k0} <span hidden><p :hidden="true" class="hiddenp">true ${path}</p></span>`;
        // event.target.style.setProperty("background-color", "rgb(159.5, 206.5, 255)");
        // event.target.style.setProperty("background-color", "rgb(255,255, 255)");
        // event.target.style.setProperty("color", "rgb(255,255, 255)");
      }
      
      const instance = axios.create({
        baseURL: '/csdn/kshoucang',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {'mail': Cookies.get("mail"), 'password':Cookies.get("password"), 'url':document.URL,
          'click':clicka, 'path':path, 'title':title,
        },
      }).then((response) => {
        this.search_param.reset = 1;
        this.resetSearch();
        // alert(response);
        // console.log(response.data);
        // console.log(response.type);
        // console.log(response.status);
        // console.log(response.statusText);
        // console.log(response.headers);
        // console.log(response.config);

      });
    },
    async uploadComment() {
      let id = document.URL;
      id = id.substring(0, 50);
      let index = id.indexOf("/zj");

      if(!Cookies.get("mail") && index < 0) {
        ElMessage.error("没有登陆不能操作！");
        return
      }
      // 前端先行校验，与后端 comment_add 的容量限制保持一致
      if(!this.textarea_content || this.textarea_content.trim()==="") {
        ElMessage.warning("评论内容不能为空！");
        return;
      }
      if(this.textarea_content.length > 2000) {
        ElMessage.warning("评论过长，最多2000字！");
        return;
      }
      const instance = axios.create({
        baseURL: '/csdn/comment_add',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {'mail': Cookies.get("mail"), 'password':Cookies.get("password"), 'url':document.URL,
          'path':this.dire_path, 'comment':this.textarea_content,
        },
      }).then(async (response) => {
        this.commentvisible = false;
        await this.resetSearch();
        this.textarea_content = "";

        let ele = document.getElementsByClassName("pinglun");
        for(let i = 0; i < ele.length; i++) {
          // console.log(ele[i].childNodes[1].childNodes[0]);
          if(ele[i].childNodes[1].childNodes[0].innerText==this.dire_path) {
            ele[i].childNodes[0].click();
            break;
          }
        }
        // this.shoucangEle.click();
        // let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
        // Cookies.remove("csdndetail_reload");
        // Cookies.set("csdndetail_reload", 0, { expires: expiresdate });
        // for(let i = 0; i < this.result.length; i++) {
        //   if(this.result[i]['path']==this.dire_path) {
        //     this.commentsigle = this.result[i]['comment'];
        //     break
        //   }
        // }
        // this.commentvisible = true;
        // alert(response);
        // console.log(response.data);
        // console.log(response.type);
        // console.log(response.status);
        // console.log(response.statusText);
        // console.log(response.headers);
        // console.log(response.config);

      });
    },
    commentdialog(event) {
      let id = document.URL;
      id = id.substring(0, 50);
      let index = id.indexOf("/zj");

      if(!Cookies.get("mail") && index < 0) {
        ElMessage.info("没有登陆不能评论！");
        // return
      }
      let kkk = event.srcElement.innerText;
      // let k0 = kkk.substring(kkk.length - 2);
      this.shoucangEle = event.srcElement;
      let k1 = Number(kkk.substring(0, kkk.length - 2));
      // console.log(k1, kkk);
      if(k1==0) {
        ElMessage.info("没有任何评论！");
        if(!Cookies.get("mail")) {
          return;
        }
      }
      this.search(event.srcElement);
      for(let i = 0; i < this.result.length; i++) {
        if(this.result[i]['path']==this.dire_path) {
          this.commentsigle = this.result[i]['comment'];
          break
        }
      }
      // let kl = document.getElementById("commentsigleid");
      // kl.innerHTML = this
      // console.log(event, this.dire_path, this.commentsigle);
      this.commentvisible = true;
    },
    async upvoteclick(event) {
      let id = document.URL;
      id = id.substring(0, 50);
      let index = id.indexOf("/zj");

      if(!Cookies.get("mail") && index < 0) {
        ElMessage.error("没有登陆不能操作！");
        return
      }
      this.search(event.srcElement);
      let star = this.dire_path.indexOf(" ");
      // 兜底：卡片隐藏节点没取到时 dire_path 无空格，继续走会拼出垃圾 path 打到后端
      if(star < 0) {
        ElMessage.error("操作异常，请刷新页面后重试！");
        return;
      }
      // let first = this.dire_path.split(" ");
      let first = [this.dire_path.substring(0, star)];
      first[1] = this.dire_path.substring(star + 1);
      let clicka = true;
      if(first[0]=='false') {
        clicka = false;
      }
      let path = first[1];

      let kkk = event.srcElement.innerText;
      let k0 = kkk.substring(kkk.length - 3);
      let k1 = Number(kkk.substring(0, kkk.length - 3));

      // let file = event.srcElement.childNodes[3].childNodes[0].innerHTML;
      // console.log(event, this.dire_path, first, k0, k1, path ,clicka);
      if(clicka) {
        clicka = false;
        k1 = Math.max(0, k1 - 1);
        event.srcElement.innerHTML = `${k1.toString()}${k0} <span hidden><p :hidden="true" class="hiddenp">false ${path}</p></span>`;
        // event.target.style.setProperty("background-color", "rgba(23, 114, 246, .1)");
      } else {
        clicka = true;
        k1 = Math.max(0, k1 + 1);
        event.srcElement.innerHTML = `${k1.toString()}${k0} <span hidden><p :hidden="true" class="hiddenp">true ${path}</p></span>`;
        // event.target.style.setProperty("background-color", "rgb(159.5, 206.5, 255)");
      }
      
      const instance = axios.create({
        baseURL: '/csdn/upvote_change',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {'mail': Cookies.get("mail"), 'password':Cookies.get("password"), 'url':document.URL,
          'click':clicka, 'path':path,
        },
      }).then((response) => {
        this.search_param.reset = 1;
        this.resetSearch();
        // alert(response);
        // console.log(response.data);
        // console.log(response.type);
        // console.log(response.status);
        // console.log(response.statusText);
        // console.log(response.headers);
        // console.log(response.config);

      });
    },
    async axiosget() {
      // console.log(this.$router.currentRoute._value.query.currentpage);
      // console.log(this.$router);
      // console.log(Cookies.get("csdnsearch"));
      // this.search_param.currentpage = this.$router.currentRoute._value.query.currentpage;
      // this.$router.currentRoute._value.query.currentpage = this.search_param.currentpage;
      if(Cookies.get("checke")) {
        this.search_param.checke = parseInt(Cookies.get("checke"));
      } else {
        this.search_param.checke = this.checke;
      }
      this.search_param.mail = Cookies.get("mail");
      this.search_param.password = Cookies.get("password");
      this.search_param.url = document.URL

      if(Cookies.get("csdnsearch") && Cookies.get("csdnsearch").length) {
        // let cklen = Cookies.get("csdnsearch").length;
        // let kk = Cookies.get("csdnsearch");
        // this.search_param.search = kk[0];
        // this.result = [];
        // for(let i = 1; i < cklen - 1; i++) {
        //   this.result[this.result.length] = kk[i];
        // }
        // this.total = kk[cklen - 1];
        this.search_param.search = Cookies.get("csdnsearch");
        // return;
      }
      if(Cookies.get("csdnReset") && Cookies.get("csdnReset") == 1) {
        this.search_param.reset = 1;
      }
      // console.log('22222222222', document.cookie);
      const instance = axios.create({
        baseURL: '/csdn/index',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      // let gu;
      // await getusername(document.URL).then((response) => {
      //   gu = response;
      // });

      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: this.search_param,
      }).then((response) => {
        // alert(response);
        // console.log(response.data);
        // console.log(response.type);
        // console.log(response.status);
        // console.log(response.statusText);
        // console.log(response.headers);
        // console.log(response.config);
        // console.log(this.nowpage)
        this.result = response.data.collect;
        this.total = response.data.length;
        this.search_param.currentpage = this.nowpage;
        this.search_param.pagesize = this.nowpagesize;
        // let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
        let expiresdate = new Date(new Date().getTime() + getCookieDays() * 24 * 60 * 60 * 1000);
        // console.log('99999999999', document.cookie, mail, password);
        Cookies.remove("csdn");
        Cookies.remove("csdnpage");
        Cookies.set("csdn", this.nowpage, { expires: expiresdate });
        Cookies.set('csdnpage', this.nowpagesize, { expires: expiresdate });

        Cookies.remove("csdnReset");
        this.search_param.reset = 0;
        if(this.search_param.mail) {
          this.search_param.mail = "";
          this.search_param.url = "";
          this.search_param.password = "";
          delete this.search_param.mail;
          delete this.search_param.password;
        }
        // location.replace("?currentpage=" + this.nowpage);
        // this.$router.push({ path: '/csdn/'+gu.urlmail,  query:{"currentpage": this.nowpage}})
        // console.log(window.history.state)
      });
    },
    handleCheckbox() {
      Cookies.remove("checke");
      let expiresdate = new Date(new Date().getTime() + getCookieDays() * 24 * 60 * 60 * 1000);
      Cookies.set("checke", this.checke, { expires: expiresdate });
      this.search_param.reset = 1;
      this.search_param.currentpage = 1;
      // this.search_param.currentpage = this.$router.currentRoute._value.query.currentpage;
      this.search_param.pagesize = 20;
      this.search_param.search = "";
      this.$router.currentRoute._value.query.currentpage = 1;
      this.nowpage = 1;
      this.nowpagesize = 20;
      this.axiosget();
      this.search_param.reset = 0;
    },
    async current_Page_Change(val) {
      // console.log(val);
      this.$router.currentRoute._value.query.currentpage = Number(val);
      this.nowpage = Number(val);

      // let gu;
      // await getusername(document.URL).then((response) => {
      //   gu = response;
      // });
      let url = document.URL;
      let id = url.indexOf("?");
      let front = url.substring(0, id);
      url = front + "?currentpage=" + this.nowpage + "&pagesize=" + this.nowpagesize;
      location.replace(url);
      // location.reload();
      // this.$router.push({ path: '/csdn/'+gu.urlmail,  query:{"currentpage": this.nowpage, "pagesize": this.nowpagesize}})
      this.search_param.reset = 0;
      await this.axiosget();
    },
    async page_Size_Change(val) {
      this.$router.currentRoute._value.query.pagesize = Number(val);
      this.nowpagesize = Number(val);

      // let gu;
      // await getusername(document.URL).then((response) => {
      //   gu = response;
      // });
      let url = document.URL;
      let id = url.indexOf("?");
      let front = url.substring(0, id);
      url = front + "?currentpage=" + 1 + "&pagesize=" + this.nowpagesize;
      location.replace(url);
      // location.reload();
      // this.$router.push({ path: '/csdn/'+gu.urlmail,  query:{"currentpage": this.nowpage, "pagesize": this.nowpagesize}})
      this.search_param.reset = 1;
      await this.axiosget();
    },
    handleSearch() {
      this.search_param.reset = 1;
      const instance = axios.create({
        baseURL: '/csdn/index',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      this.search_param.password = Cookies.get("password");
      this.search_param.mail = Cookies.get("mail");
      this.search_param.url = document.URL;

      instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: this.search_param,
      }).then((response) => {
        // alert(response);
        // console.log(response.data);
        // console.log(response.type);
        // console.log(response.status);
        // console.log(response.statusText);
        // console.log(response.headers);
        // console.log(response.config);
        this.result = response.data.collect;
        this.total = response.data.length;
        this.search_param.reset = 0;
      });
      let expiresdate = new Date(new Date().getTime() + getCookieDays() * 24 * 60 * 60 * 1000);
      Cookies.remove("csdnsearch");
      Cookies.remove("csdn");
      Cookies.remove("csdnpage");
      Cookies.set("csdn", this.nowpage, { expires: expiresdate });
      Cookies.set('csdnpage', this.nowpagesize, { expires: expiresdate });

      Cookies.set("csdnsearch", this.search_param.search, { expires: expiresdate });
      this.search_param.password = "";
      this.search_param.mail = "";
      this.search_param.url = "";
    },
    async resetSearch() {
      this.search_param.reset = 1;
      this.nowpage = 1;
      this.search_param.currentpage = this.nowpage;
      this.search_param.pagesize = this.nowpagesize;
      this.search_param.search = "";

      let expiresdate = new Date(new Date().getTime() + getCookieDays() * 24 * 60 * 60 * 1000);
      Cookies.remove("csdnsearch");
      Cookies.remove("csdnReset");
      Cookies.set("csdnsearch", "", { expires: expiresdate });

      // let gu;
      // await getusername(document.URL).then((response) => {
      //   gu = response;
      // });
      let url = document.URL;
      let id = url.indexOf("?");
      let front = url.substring(0, id);
      url = front + "?currentpage=" + this.nowpage + "&pagesize=" + this.nowpagesize;
      location.replace(url);
      // location.reload();
      // this.$router.push({ path: '/csdn/'+gu.urlmail,  query:{"currentpage": this.nowpage, "pagesize": this.nowpagesize}})
      await this.axiosget();
    },
    search(ele) {
      if(ele.nodeName=="#text" || ele.nodeName=="LI") {
        // console.log("textli", ele);
        return;
      }
      // console.log(ele);
      if(ele.className=="hiddenp") {
        // console.log(ele);
        // console.log(ele.innerText);
        // console.log(ele.outerText);
        // console.log(ele.nodeValue);
        // console.log(ele.innerText.toString());
        this.dire_path = ele.innerText.toString();
        return;
      }
      for(let i = 0; i < ele.childNodes.length; i++) {
        this.search(ele.childNodes[i]);
      }
      if(ele.nextElementSibling) {
        this.search(ele.nextElementSibling);
      }
    },
    // URL 隐私：邮箱 -> uid 查询（公开 userlist 已带 uid）。
    // 转发链接/转发链中的主页链接不能出现邮箱；拉取失败或用户已删除时回退原串
    // （旧邮箱 URL 后端仍兼容，只是不再新增邮箱形态链接）
    async buildUidLookup() {
      const cache = (this._uidLookupMap && Date.now() - this._uidLookupAt < 300000)
        ? this._uidLookupMap : null;
      if (cache) {
        return cache;
      }
      let map = {};
      try {
        const instance = axios.create({ baseURL: '/csdn/userlist', timeout: 20000 });
        const response = await instance({
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
          data: {},
        });
        if (response.data && response.data.ret === 1) {
          (response.data.users || []).forEach((u) => {
            if (u.mail && u.uid) {
              map[u.mail] = u.uid;
            }
          });
        }
      } catch (e) {
        map = {};
      }
      // 自己的邮箱兜底用 localStorage 缓存的 my_uid（登录者必然在 userlist 里，一般走不到）
      const lookup = (mail) => map[mail]
        || (mail && mail === Cookies.get('mail') ? (localStorage.getItem('my_uid') || mail) : mail);
      this._uidLookupMap = lookup;
      this._uidLookupAt = Date.now();
      return lookup;
    },
    // 转发：把他人文章以片段形式转发到自己的片段空间（复用已登录即可用的 post_think 接口）
    async forwardArticle(event) {
      // 先向后端确认登录态，避免 Cookie 残留导致"看似登录"却实际未登录
      let gu;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      if (!gu || gu.ret <= 0 || !Cookies.get('mail') || !Cookies.get('password')) {
        ElMessage.error('请先登录后再转发！');
        return;
      }
      // 从卡片隐藏元素中取原文路径
      // 注意：hiddenp 位于 <span hidden> 内，outerText 恒为空，必须用 textContent
      let node = event.target;
      let originPath = '';
      while (node) {
        const hp = node.querySelector ? node.querySelector('.hiddenp') : null;
        if (hp && hp.textContent && hp.textContent.trim()) {
          originPath = hp.textContent.trim();
          break;
        }
        node = node.parentElement;
      }
      if (!originPath) {
        ElMessage.error('转发失败，未找到原文！');
        return;
      }
      const myMail = Cookies.get('mail');
      // 取卡片正文：用于 100 字摘要 + 识别已有的转发链（支持链式转发）
      let cardText = '';
      const card = event.target.closest ? event.target.closest('.el-card') : null;
      if (card) {
        const body = card.querySelector('.el-card__body');
        if (body) {
          cardText = (body.innerText || '').replace(/\s+/g, ' ').trim();
        }
      }
      let chain = [];
      const chainMatch = cardText.match(/转发自\s*([^\n]{0,200})/);
      if (chainMatch) {
        const names = chainMatch[1].match(/@[A-Za-z0-9_\-\.]+/g) || [];
        chain = names.map((s) => s.slice(1));
      }
      let summary = cardText.replace(/^🔁\s*转发自[^。]*?(?=\s|$)/, '').trim();
      if (summary.length > 100) {
        summary = summary.slice(0, 100) + '…';
      }
      // URL 隐私：转发生成的链接（查看全文/转发链主页链接）中用户段一律用 uid
      const uidOf = await this.buildUidLookup();
      ElMessageBox.prompt('文章将以片段形式转发到你的片段空间，可附上你的想法', '转发文章', {
        confirmButtonText: '转发',
        cancelButtonText: '取消',
        inputPlaceholder: '说点什么（可选）',
        inputType: 'textarea',
      }).then(({ value }) => {
        // 从路径提取原作者（people/<mail>/），公共区默认 homepage
        let owner = 'homepage@gmail.com';
        if (originPath.includes('/people/')) {
          const parts = originPath.split('/people/')[1].split('/');
          if (parts.length > 1 && parts[0]) {
            owner = parts[0];
          }
        }
        const link = location.origin + '/#/csdn/markdown_detail/' + uidOf(owner) + '?plan=' + encodeURIComponent(originPath);
        // 转发链：我 → 原作者 → 更早的转发者（用户名都可点击跳转到其主页）
        const mails = [myMail, owner];
        chain.forEach((m) => {
          if (m && mails.indexOf(m) < 0) {
            mails.push(m);
          }
        });
        const chainStr = mails.map((m) => '[@' + m + '](/#/' + uidOf(m) + ')').join(' → ');
        let content = '🔁 转发自 ' + chainStr + ' 的文章';
        if (summary) {
          content += '\n\n> ' + summary;
        }
        content += '\n\n[查看全文](' + link + ')';
        if (value && value.trim()) {
          content += '\n\n' + value.trim();
        }
        const instanc = axios.create({
          baseURL: '/think/post_think',
          timeout: 20000,
        });
        instanc({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
          },
          data: {
            "postdate": Date.now(),
            "imgpostdate": "",
            "text_content": content,
            'mail': myMail,
            'password': Cookies.get('password'),
            // 必须带上自己的账号，后端会校验 mail 是否出现在 url 中
            'url': location.origin + '/#/think/' + myMail,
          },
        }).then((response) => {
          if (response.data.ret < 0) {
            ElMessage.error('转发失败，请先登录！');
            return;
          }
          ElMessage.success('转发成功，已发布到你的片段空间！');
        }).catch(() => {
          ElMessage.error('网络错误，转发失败！');
        });
      }).catch(() => {});
    },
    async cardClick(event) {
      this.search(event.target);
      // let markdown_path = "";
      // if (event.target.className=="") {
      //   markdown_path = event.target.nextSibling.outerText;
      // } else {
      //   markdown_path = event.target.childNodes[1].childNodes[1].outerText;
      // }
      // alert(markdown_path);
      // console.log(event);
      // console.log();
      let gu;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      // window.history.pushState({ page: 1 }, "标题 1", "?page=1");
      // console.log(window.history.state)
      if(gu && gu.ret > 0) {
        // uid 化后用 URL 原始段（uid）建链接，避免把邮箱写回地址栏
        this.$router.push({ path: '/csdn/markdown_detail/'+(gu.urluid || gu.urlmail), query: { plan: this.dire_path }});
      } else {
        this.$router.push({ path: '/csdn/markdown_detail/*', query: { plan: this.dire_path }});
      }
    },
    async postarticle() {
      let gu;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      // console.log(gu);
      if(gu && gu.ret > 0) {
        this.$router.push({ path: '/csdn/post_article/'+(gu.urluid || gu.urlmail)});
      } else {
        this.$router.push({ path: '/csdn/post_article/*'});
      }
    },
  },
}
</script>

<style scoped>
/* 资料搜索工具栏：flex 统一排列（替代散排 margin 硬凑），回车触发、可清空 */
.search-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  margin-bottom: 12px;
  background: linear-gradient(135deg, rgba(64, 158, 255, .07), rgba(103, 194, 58, .07));
  border: 1px solid rgba(64, 158, 255, .18);
  border-radius: 10px;
}
.search-toolbar .search-input {
  width: 30%;
  min-width: 220px;
}
/* 发表等次要操作推到行尾 */
.search-toolbar .toolbar-push {
  margin-left: auto;
}
@media (max-width: 768px) {
  .search-toolbar .search-input {
    width: 100%;
    min-width: 0;
  }
  .search-toolbar .toolbar-push {
    margin-left: 0;
  }
}
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  position: relative;
  top: -10px;
}

h3 {
  font-size: 1.2rem;
}

.el-card-detail {
  width: 80%;
  color: #00ff00;
  margin-top: 3px;
  margin-left: 10%;
  margin-right: 10%;
}

/* 压缩卡片上下间距：header/body/footer 默认 padding 过大（20px 级），
   统一收紧；简介内容本身不做任何截断/压缩 */
.el-card-detail :deep(.el-card__header) {
  padding: 8px 16px;
}
.el-card-detail :deep(.el-card__header).card-header,
.el-card-detail :deep(.card-header) {
  font-size: 20px;
  line-height: 1.4;
  padding: 2px 0;
}
.el-card-detail :deep(.el-card__body) {
  padding: 10px 16px;
}
.el-card-detail :deep(.el-card__footer) {
  padding: 6px 16px 8px;
}
/* 时间与左侧赞/评/藏/转发同行垂直居中对齐 */
.el-card-detail :deep(.el-card__footer) .el-row {
  align-items: center;
}
.el-card-detail :deep(.card-footer) {
  line-height: 28px;
}

.zanzan{
  background:rgba(23, 114, 246, .1);
  color: #1772f6;
  border-color: transparent;
  border-radius: 3px;
  padding-left: 6px;
  padding-right: 6px;
  padding-top: 3px;
  padding-bottom: 3px;
  width:fit-content;
}
.pinglun {
  background:rgba(23, 114, 246, .1);
  color: #1772f6;
  border-color: transparent;
  border-radius: 3px;
  padding-left: 6px;
  padding-right: 6px;
  padding-top: 3px;
  padding-bottom: 3px;
  width:fit-content;
}
.shoucangshoucang {
  background:rgba(23, 114, 246, .1);
  color: #1772f6;
  border-color: transparent;
  border-radius: 3px;
  padding-left: 6px;
  padding-right: 6px;
  padding-top: 3px;
  padding-bottom: 3px;
  width:fit-content;
}

/* .zanzan:hover{
} */

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

/* 手机端适配：搜索区换行、卡片与分页占满宽度、底部操作栏自适应换行 */
@media (max-width: 768px) {
  #csdnpg .search-input {
    width: calc(100% - 12px) !important;
    margin-left: 6px !important;
  }

  #csdnpg .el-button {
    margin-left: 6px !important;
    margin-top: 6px;
  }

  #csdnpg .el-checkbox {
    margin-left: 6px !important;
    margin-top: 6px;
  }

  .top-badge {
    margin-left: 6px !important;
  }

  .el-card-detail {
    width: 100%;
    margin-left: 0;
    margin-right: 0;
  }

  .el-card-detail .el-col {
    flex: 0 0 auto;
    max-width: 100%;
  }

  .el-card-detail .el-col:last-child {
    flex: 0 0 100%;
    max-width: 100%;
  }

  .el-pagination {
    margin-left: 4px !important;
    margin-right: 4px !important;
    flex-wrap: wrap;
    row-gap: 6px;
  }
}
</style>
