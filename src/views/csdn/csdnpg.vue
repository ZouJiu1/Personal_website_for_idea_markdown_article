<template>
  <div class="app-container">
    <!-- <el-card shadow="always"> -->
      <div id='csdnpg'>
        <el-link type="primary" id='csdnpglink' href="https://zoujiu.blog.csdn.net/" target="_blank">CSDN</el-link>
        <el-input
          v-model="search_param.search"
          placeholder="标题、日期或者内容, 空格 分隔"
          style="width: 30%; margin-left:20px;"
          class="filter-item"
        />
        <el-button
          class="filter-item"
          type="primary"
          @click="handleSearch"
          style="margin-left:20px;text-align:center;"
          >
          搜索
        </el-button>
        <el-button
          class="filter-item"
          type="primary"
          @click="resetSearch"
          style="text-align:center;"
          >
          重置
        </el-button>
        <el-checkbox 
          v-model="checke" label="包含leetcode和PAT" 
          :true-value="1"
          :false-value="0"
          border
          style="text-align:center;margin-left:13px;margin-top:2px;" @Change="handleCheckbox"/>
        <el-button
          class="filter-item"
          type="success"
          @click="postarticle"
          style="text-align:center;margin-left:100px;"
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
        <div class="card-header" style="font-size: 20px; color: #00ff00; overflow:auto;" @click="cardClick">
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
          <el-col :span="20" :lg="6">
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
import { ElMessage } from 'element-plus'
import getusername from '/src/common.js'
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
      nowpage: Number(this.$router.currentRoute._value.query.currentpage),
      nowpagesize: Number(this.$router.currentRoute._value.query.pagesize),
      search_param: {
        currentpage: Number(this.$router.currentRoute._value.query.currentpage),
        pagesize: Number(this.$router.currentRoute._value.query.pagesize),
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
      //   baseURL: 'http://localhost:7009/csdn/clickpage',
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
        baseURL: 'http://localhost:7009/csdn/kshoucang',
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
      const instance = axios.create({
        baseURL: 'http://localhost:7009/csdn/comment_add',
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
        baseURL: 'http://localhost:7009/csdn/upvote_change',
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
        baseURL: 'http://localhost:7009/csdn/index',
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
        let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
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
      let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
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
        baseURL: 'http://localhost:7009/csdn/index',
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
      let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
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

      let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
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
      if(ele.childNodes.length==1 && ele.nextSibling) {
        this.search(ele.nextSibling);
      }
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
        this.$router.push({ path: '/csdn/markdown_detail/'+gu.urlmail, query: { plan: this.dire_path }});
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
        this.$router.push({ path: '/csdn/post_article/'+gu.urlmail});
      } else {
        this.$router.push({ path: '/csdn/post_article/*'});
      }
    },
  },
}
</script>

<style scoped>
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
</style>
