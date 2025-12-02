<template>
  <div class="app-container" id="thought"> 
    <!-- <el-card shadow="always"> -->
      <div style="margin-top:3px;">
        <!-- <el-link type="primary" href="https://www.zhihu.com/people/zoujiu1/" target="_blank">知乎</el-link> -->
        <el-input
          v-model="search_param.search"
          placeholder="日期或者内容, 空格 分隔"
          style="width: 30%; margin-left:20px;"
          class="filter-item"
          id="riqisousuo"
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
        <!-- <el-button
          class="filter-item"
          type="success"
          @click="postThink"
          style="text-align:center;margin-left:100px;"
          >
          发表
        </el-button> -->
        <!-- onload="loadfun"  -->
      </div>
    <!-- </el-card> -->
    <el-card class="el-card-detail">
      <el-input
        v-model="textarea1"
        style="width: 100%;overflow:auto;height:100%"
        type="textarea"
        :autosize="{ minRows: 3, maxRows: 9 }"
        placeholder="发布一个片段"
      />
    <!-- <el-dialog v-model="dialogFormVisible" title="上传图片" width="500">
      <el-upload
        v-model:file-list="fileList"
        class="upload-demo"
        action="http://localhost:7009/think/uploadImg"
        multiple
        :on-preview="handleUpPreview"
        :on-remove="handleRemove"
        :before-remove="beforeRemove"
        :limit="3"
        :on-exceed="handleExceed"
        :on-success="handleUpLoadSuccess"
        :data="data"
        :before-upload="handlebefore_Upload"
      >
        <el-button type="primary" style="margin-top:3px;">Click to upload</el-button>
      </el-upload>
    </el-dialog> -->
    <div style="margin-top:3px;">
      <el-row :gutter="0">
        <el-col :span="2" :push="0">
          <div id="upLoadbuttonThink" :hidden="uploadimgvisible">
            <el-button
              class="filter-item"
              type="primary"
              @click="upLoadbuttonThink"
              style="text-align:center;margin-left:3px;margin-top:3px"
            >
              上传图片
            </el-button>
          </div>
        </el-col>
        <el-col :span="2" :push="0">
          <el-button
            class="filter-item"
            type="primary"
            @click="postThink"
            style="text-align:center;margin-left:60%;"
            >
            发布
          </el-button>
        </el-col>
      </el-row>
      <el-upload
        v-model:file-list="fileList"
        action="http://localhost:7009/think/uploadImg"
        list-type="picture-card"
        :on-preview="handlePictureCardPreview"
        :on-remove="handleRemove"
        :before-upload="handlebefore_Upload"
        id="elupload"
        :data="data"
        :limit="30"
        multiple
        :hidden="elupload_hidden"
        :on-success="handleUpLoadSuccess"
      >
        <el-icon><Plus /></el-icon>
      </el-upload>

      <el-dialog v-model="dialogVisible">
        <div>
          <img :src="dialogImageUrl" alt="Preview Image" style="width:100%; overflow:auto;"/>
        </div>
      </el-dialog>
    </div>

    <template #footer>
      <div class="card-footer" style="height:auto; font-size: 16px; color: #0000ee;">
        <span hidden>
          <el-input
            v-model="postkey" 
            placeholder="输入发布密钥"
            style="margin-left:6px;width:30%"
            class="filter-item"
            id="elinput"
            type="password"
          />
        </span>
        <!-- <el-button
          class="filter-item"
          type="primary"
          @click="postThink"
          style="text-align:center;margin-left:60%;"
          >
          发布
        </el-button> -->
      </div>
    </template>
        <!-- <el-button
        class="filter-item"
        type="primary"
        @click="resetSearch"
        style="text-align:center;"
        >
        发布
      </el-button> -->
      <!-- <template #footer>
        <div class="card-footer" style="height:100%; font-size: 16px; color: #0000ee;margin-left:90%;">
          <el-button
            class="filter-item"
            type="primary"
            @click="postThink"
            style="text-align:center;"
            >
            发布
          </el-button>
        </div>
      </template> -->
    </el-card>
    <el-card
      v-for="o in result"
      :key="o"
      class="el-card-detail"
      shadow="always"
      style="overflow:auto;"
    >
      <!-- <template #header>
        <div class="card-header" style="overflow:auto; font-size: 20px; color: #00ff00;" @click="cardClick" >
          <span @click="cardClick"> {{ o["date"] }} </span>
          <span hidden><p hidden @click="cardClick" class="hiddenp"> {{ o["path"] }} </p></span>
        </div>
      </template> -->
      <span style="width:60%; font-size: 16px; color: #000000;" @click="cardClick" v-if="!o.isTop">
        <div v-html="o.markdown" style="background-color: #ffffff;color: #000000;">
        </div>
        <!-- {{ o["markdown"] }} -->
        <!-- <span class="imageplot"></span> -->
      </span>
      <span style="width:60%; font-size: 16px; color: #000000; background-color: #FF00FF;" @click="cardClick" v-if="o.isTop">
        <div v-html="o.markdown" style="background-color: #FF00FF;color: aquamarine;">
        </div>
        <p style="background-color: #1989fa;color:#ffffff;margin-left: 90vh;padding-left: 3vh;margin-top: 2px;font-weight: 900;">TOP</p>
        <!-- {{ o["markdown"] }} -->
        <!-- <span class="imageplot"></span> -->
      </span>
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
              <span style="color:rgba(23, 114, 246);" @click="commentdialog">{{ o['comment'].length }}评论</span>
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
      <!-- <el-image
        v-for="img in o.imgimg"
        :key="img"
        lazy
        fit="contain" class="el-image__inner el-image__preview think_image"
        style="object-fit: scale-down;" @click="cardClick"
        :src="img">
        <span hidden><p hidden @click="cardClick" class="hiddenp">{{ o["path"] }}</p></span>
      </el-image> -->
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
// function loadfun() {
//   let cpn = document.getElementsByClassName("cardspan1");
//   console.log(cpn);
//   console.log(cpn[0]);
//   console.log(cpn.length);
// }
// window.onload = loadfun;
// let image = document.getElementsByClassName("app-container")[0]; 
// image.addEventListener("load", (event) => { 
//   let cpn = document.getElementsByClassName("cardspan1");
//   console.log(cpn);
//   console.log(cpn[0]);
//   console.log(cpn.length);
// });
var wait_think_render = 100;
import axios from 'axios'
import { ElMessage } from 'element-plus'
import getusername from '/src/common.js'
import Cookies from 'js-cookie'
export default {
  name: 'app',
  data() {
    return {
      total: 0,
      result: [],
      dialogFormVisible: true,
      dire_path: "",
  // 'fill',
  // 'contain',
  // 'cover',
  // 'none',
  // 'scale-down',
      imageFit: "contain",
      postkey: "",
      textarea1: "",
      postdate: "",
      imgUpPath: "",
      commentvisible:false,
      uploadimgvisible:false,
      textarea_content: "",
      dire_path: "",
      checke: 1,
      commentsigle:[],
      data: {
        "postdate": -10,
      },
      fileList: [
        // {
        //   name: 'food.jpeg',
        //   url: 'https://fuss10.elemecdn.com/3/63/4e7f3a15429bfda99bce42a18cdd1jpeg.jpeg?imageMogr2/thumbnail/360x360/format/webp/quality/100',
        // },
        // {
        //   name: 'plant-1.png',
        //   url: '/images/plant-1.png',
        // },
      ],
      dialogImageUrl: "",
      dialogVisible: false,
      // upLoadbutton_hidden: false,
      elupload_hidden: true,
      nowpage: Number(this.$router.currentRoute._value.query.currentpage),
      nowpagesize: Number(this.$router.currentRoute._value.query.pagesize),
      search_param: {
        currentpage: Number(this.$router.currentRoute._value.query.currentpage),
        pagesize: Number(this.$router.currentRoute._value.query.pagesize),
        search: "",
        reset: 0,
      },
    }
  },
  mounted(){
    this.axiosget(true);
    // this.clickpage();
  },
  watch: {},
  methods: {
    async clickpage() {
      const instance = axios.create({
        baseURL: 'http://localhost:7009/csdn/clickpage',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      await instance({
        method: 'GET',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        params: {'type' : 'thought'},
      }).then((response) => {
      });
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
      // console.log(event, this.dire_path);
      let clicka = true;
      if(first[0]=='false') {
        clicka = false;
      }
      let path = first[1];

      let title = "";
      for(let i = 0; i < this.result.length; i++) {
        if(this.result[i]['path']==path) {
          title = this.result[i]['date'];
          break
        }
      }

      let kkk = event.srcElement.innerText;
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
        baseURL: 'http://localhost:7009/think/kshoucang',
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
        baseURL: 'http://localhost:7009/think/comment_add',
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
      }).then((response) => {
        this.resetSearch();
        this.commentvisible = false;
        this.textarea_content = "";
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
      // console.log(event, this.dire_path);
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
        baseURL: 'http://localhost:7009/think/upvote_change',
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
    async sha(str) { 
      const textEncoder = new TextEncoder(); 
      const message = textEncoder.encode(str); 
      const messageDigest = await crypto.subtle.digest('SHA-512', message); 
      const hexDigest = Array.from(new Uint8Array(messageDigest)) 
      .map((x) => x.toString(16).padStart(2, '0')) 
      .join(''); 
      // console.log(hexDigest); 
      return hexDigest;
    },
    async postThink() {
      if(this.textarea1.length < 6) {
        ElMessage.error("字数太少了不能 < 6！");
        return;
      }
      const instanc = axios.create({
        baseURL: 'http://localhost:7009/think/post_think',
        timeout: 20000,
      });
      instanc({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
        },
        data: {"postdate" : Date.now(), "imgpostdate":this.data.postdate, 
                 "text_content" : this.textarea1, 'mail':Cookies.get("mail"), 
                 "password":Cookies.get("password"), 'postkey':this.postkey,
                'url':document.URL},
      }).then((response) => {
        if(response.data.ret < 0) {
          // ElMessage.error('输入的密钥不对！');
          ElMessage.error('没有登陆不能修改!');
          return false;
        }
        this.resetSearch();
        ElMessage.success("片段已经发布");
      });
      this.postkey = "";
      this.uploadimgvisible = false;
      this.elupload_hidden = true;
      // let sharet = "45c144247124160a29e93a160e62bc7128bd33a9da552c1b9441d562240754637b38e5a25fa151044e902b99ff22ec91ffa9e9e0e2edde67317cc04adf329b78";
      // this.sha(this.postkey).then((r)=>{
      //   if(sharet == r) {
      //     const instance = axios.create({
      //       baseURL: 'http://localhost:7009/think/post_think',
      //     timeout: 20000,
      //     });
      //     instance({
      //       method: 'GET',
      //       headers: {
      //         'X-Requested-With': 'XMLHttpRequest'
      //       },
      //       params: {"postdate" : Date.now(), "imgpostdate":this.data.postdate, "text_content" : this.textarea1},
      //     }).then((response) => {
      //       this.resetSearch();
      //     });
      //     ElMessage("片段已经发布");
      //   }
      //   else {
      //     this.$alert("发布密钥不正确，自动取消发布");
      //   }
      // });
    }, 
    async upLoadbuttonThink() {
      let gu;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      // const instance = axios.create({
      //   baseURL: 'http://localhost:7009/csdn/renzheng',
      //  timeout: 20000,
      // });
      
      // // console.log(this.search_param);
      // instance({
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'X-Requested-With': 'XMLHttpRequest'
      //   },
      //   withCredentials: true,
      //   data: {"postkey":this.postkey},
      // }).then((response) => {
        // if(response.data.ret || (gu && gu.ret == 1)) {
      if(gu && gu.ret == 1) {
        // let upLoadbut = document.getElementById("upLoadbuttonThink");
        // upLoadbut.hidden = true;
        this.elupload_hidden = false;
        // this.upLoadbutton_hidden = true;
        this.uploadimgvisible = true;
        this.data.postdate = Date.now();
        // console.log(this.postdate);
        ElMessage.success("可以上传图片");
      } else {
        this.elupload_hidden = true;
        this.uploadimgvisible = false;
        // this.upLoadbutton_hidden = false;
        // this.$alert("发布密钥不正确，自动取消上传");
        ElMessage.error("没有登陆自动取消上传");
      }
      // });
      // let sharet = "45c144247124160a29e93a160e62bc7128bd33a9da552c1b9441d562240754637b38e5a25fa151044e902b99ff22ec91ffa9e9e0e2edde67317cc04adf329b78";
      // this.sha(this.postkey).then((r)=>{
      //   if(sharet == r) {
      //     this.upLoadbut = document.getElementById("upLoadbuttonThink");
      //     this.upLoadbut.hidden = true;
      //     this.elupload_hidden = false;
      //     this.upLoadbutton_hidden = true;
      //     this.data.postdate = Date.now();
      //     // console.log(this.postdate);
      //     ElMessage("可以上传图片");
      //   } else {
          // this.elupload_hidden = true;
          // this.upLoadbutton_hidden = false;
          // this.$alert("发布密钥不正确，自动取消上传");
      //   }
      // });
    },
    async sleep(delay) { 
      return new Promise((resolve) => setTimeout(resolve, delay)); 
    },
    handlebefore_Upload(rawFile) {
      if (rawFile.type !== 'image/jpeg' && rawFile.type !== "image/png"
          && rawFile.type !== "image/gif" && rawFile.type !== "image/bmp"
          && rawFile.type !== "image/jpg") {
        ElMessage.error('不是图片格式!');
        return false;
      } else if (rawFile.size / 1024 / 1024 > 13) {
        ElMessage.error('图片占用磁盘大小不能 > 13MB!');
        return false;
      }
      this.data.mail = Cookies.get("mail");
      this.data.password = Cookies.get("password");
      this.data.postkey = this.postkey;
      this.data.url = document.URL;
      return true;
    },
    handleUpLoadSuccess(response, uploadFile, uploadFiles) {
      // console.log("success");
      // console.log(response);
      if(response.ret < 0) {
        // console.log(uploadFile, uploadFiles);
        while(uploadFiles.length > 0) {
          uploadFiles.pop();
        }
        uploadFile = undefined;
        // console.log(uploadFile, uploadFiles);
        this.data.postkey = "";
        // ElMessage.error('输入的密钥不对, 自动取消上传!');
        ElMessage.error('没有登陆不能修改!');
        return false;
      }
      // console.log("success");
      // console.log(response);
      this.data.postkey = "";
      this.imgUpPath = response.path;
    },
    handleRemove(uploadFile, uploadFiles) {
      // console.log(uploadFile, uploadFiles);
    },
    handlePictureCardPreview(uploadFile) {
      this.dialogImageUrl = uploadFile.url;
      this.dialogVisible = true;
    },
    axiosget(wait=true) {
      const instance = axios.create({
        baseURL: 'http://localhost:7009/think/index',
        timeout: 20000,
      });
      this.search_param.password = Cookies.get("password");
      this.search_param.mail = Cookies.get("mail");
      this.search_param.url = document.URL;

      if(Cookies.get("thinksearch") && Cookies.get("thinksearch").length) {
        this.search_param.search = Cookies.get("thinksearch");
      }
      if(Cookies.get("thinkReset") && Cookies.get("thinkReset") == 1) {
        this.search_param.reset = 1;
      }
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
        // this.findkey(wait);
        // console.log(response.data);
        // console.log(this.result.length);
        // let card = document.getElementsByClassName("el-card-detail");

        // let image = document.getElementsByClassName("app-container"); 
        // console.log(image);
        // image[0].addEventListener("load", (event) => { 
        //   let card = document.getElementsByClassName("el-card-detail");
        //   console.log(card.length);
        //   console.log(card);
        // }); 

        // console.log(card.length);
        // console.log(card);
        // console.log(" " + card.length + card);
        // console.log(card["0"]);
        // let cards = document.querySelector(".el-card-detail");
        // console.log(cards);
        // let spn1  = cards.querySelector(".cardspan1");
        // let spn2  = cards.querySelector(".cardspan2");

        // console.log(spn1);
        // console.log(spn2);

        // let span1 = document.getElementsByClassName("cardspan1");
        // let span2 = document.getElementsByClassName("cardspan2");
        // // // var len = this.result.length;
        // console.log(span1);
        // console.log(span1.length);
        // // console.log(document.getElementsByClassName("cardspan1").length);
        // console.log(span2);
        // console.log(span1[0]);
        // for(let i = 0; i < len; i++) {
        // console.log(span1[0]);
        // console.log(span1.item(0).innerText);
        // span1.item(0).innerHTML = "innerHTML" // "<p>虽然没有疾病没有寻麻疹，但是医院多的药不能浪费，过期就浪费了，做为预防手段，我会全部用掉，防晒袖套唔出痱子了，不戴防晒袖套了</p>"; //this.result[i].markdown;
        // span2.item(0).innerHTML = "span2";    //this.result[i].date;
        // }
      });
      this.search_param.password = "";
      this.search_param.mail = "";
      this.search_param.url = "";
      this.search_param.reset = 0;

      let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
      Cookies.remove("think");
      Cookies.remove("thinkpage");
      Cookies.set("think", this.nowpage, { expires: expiresdate });
      Cookies.set('thinkpage', this.nowpagesize, { expires: expiresdate });
      Cookies.remove("thinkReset");
    },
    async findkey(wait=false) {
      // while(document.getElementsByClassName("cardspan1").length!=20) {
      // //  document.getElementsByClassName("cardspan1");
      // //  document.getElementsByClassName("cardspan2");
      // }
      // // var len = this.result.length;
      // let search = false;

      let cpn = document.getElementsByClassName("cardspan1");
      let cnt = 0;
      while(cpn.length!=this.search_param.pagesize&&cpn.length!=this.total) {
        // console.log(1,cpn.length, this.total, this.search_param.pagesize);
        cnt += 1;
        if(cnt > 20) {
          break;
        }
        await this.sleep(wait_think_render); // 暂停约 100 毫秒
        // search = true;
        cpn = document.getElementsByClassName("cardspan1");
        // console.log(2,cpn.length, this.total, this.search_param.pagesize);
      }
      if(wait) {
        await this.sleep(1300); // 暂停约 100 毫秒
      }

      // let cpnn = document.getElementsByClassName("cardspan1");
      // console.log(cpnn);
      // console.log(cpn[0]);
      // console.log(cpn.length);
      let span1 = document.getElementsByClassName("cardspan1");
      let len = this.result.length;
      for(let i = 0; i < len; i++) {
        span1[i].innerHTML = this.result[i].markdown;
        // console.log(span1[i]);
//         let frag = this.result[i].markdown;
//         let span2 = span1[i].getElementsByClassName("imageplot")[0];
//         console.log(span2, this.result[i].imgimg);
//         let imglen = this.result[i].imgimg.length;
//         if(imglen==0) {
//           continue;
//         }
//         for(let j = 0; j < imglen; j++) {
//           frag += `
// <el-image class="el-image__inner lazy el-image__preview think_image" style="object-fit: scale-down;" @click="cardClick" src="${this.result[i].imgimg[j]}">
//   <span hidden><p hidden @click="cardClick" class="hiddenp">${this.result[i].path}</p></span>
// </el-image>

//           `;
//         }
//         // span2[i].innerHTML = frag;
//         span1[i].innerHTML = frag;
      }
      this.search_param.currentpage = this.nowpage;
      this.search_param.pagesize = this.nowpagesize;
      // let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
      let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
      // console.log('99999999999', document.cookie, mail, password);
      Cookies.remove("think");
      Cookies.remove("thinkpage");
      Cookies.set("think", this.nowpage, { expires: expiresdate });
      Cookies.set('thinkpage', this.nowpagesize, { expires: expiresdate });
//       for(let i = 0; i < len; i++) {
//         console.log(this.result[i].imgimg, this.result[i].imgimg.length)
//         let frag = "";
//         let imglen = this.result[i].imgimg.length;
//         for(let j = 0; j < imglen; j++) {
//           frag += `
// <el-image class="el-image__inner lazy el-image__preview think_image" style="object-fit: scale-down;" @click="cardClick" src="${this.result[i].imgimg[j]}">
//   <span hidden><p hidden @click="cardClick" class="hiddenp">${this.result[i].path}</p></span>
// </el-image>

//           `;
//         }
//         span2[i].innerHTML = frag;
//       }
      // await this.sleep(3000); // 暂停约 100 毫秒
      // span1 = document.getElementsByClassName("cardspan1");
      // for(let i = 0; i < len; i++) {
      //   // span1[i].innerHTML = this.result[i].markdown;
      //   span1[i].onload = function(ele) {
      //     console.log("offsetHeight: " + ele.offsetHeight); 
      //   };
      //   // console.log("offsetHeight: " + span1[i].offsetHeight); //JavaScript高级程序设计（第4版） 472 页
      // }
      // console.log(document.getElementsByClassName("cardspan1").length);
      // console.log(span2);
    },
    async current_Page_Change(val) {
      // let thoughtele = document.getElementById("riqisousuo");
      // let htmlele = document.getElementsByTagName("html")[0];
      // let height = htmlele.clientHeight;
      // console.log(thoughtele, thoughtele.scrollTop);
      // htmlele.scroll(0, -10000);
      // htmlele.scrollTop = 0;

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
      this.search_param.reset = 0;
      // this.$router.push({ path: '/csdn/'+gu.urlmail,  query:{"currentpage": this.nowpage, "pagesize": this.nowpagesize}})
      await this.axiosget();
    },
    async page_Size_Change(val) {
      let thoughtele = document.getElementById("thought");
      thoughtele.scrollTop = 0;
      
      this.$router.currentRoute._value.query.pagesize = val;
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
      this.search_param.reset = 1;
      // this.$router.push({ path: '/csdn/'+gu.urlmail,  query:{"currentpage": this.nowpage, "pagesize": this.nowpagesize}})
      await this.axiosget();
    },
    handleSearch() {
      this.search_param.reset = 1;
      this.search_param.password = Cookies.get("password");
      this.search_param.mail = Cookies.get("mail");
      this.search_param.url = document.URL;
      const instance = axios.create({
        baseURL: 'http://localhost:7009/think/index',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
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
        // this.findkey(true);
      });
      this.search_param.password = "";
      this.search_param.mail = "";
      this.search_param.url = "";

      let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
      Cookies.remove("thinksearch");
      Cookies.remove("think");
      Cookies.remove("thinkpage");
      Cookies.set("think", this.nowpage, { expires: expiresdate });
      Cookies.set('thinkpage', this.nowpagesize, { expires: expiresdate });
      Cookies.set("thinksearch", this.search_param.search, { expires: expiresdate });
    },
    async resetSearch() {
      this.search_param.reset = 1;
      this.nowpage = 1;
      this.search_param.currentpage = this.nowpage;
      this.search_param.pagesize = this.nowpagesize;
      this.search_param.search = "";
      this.uploadimgvisible = false;
      this.elupload_hidden = true;

      let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
      Cookies.remove("thinksearch");
      Cookies.remove("thinkReset");
      Cookies.set("thinksearch", "", { expires: expiresdate });

      this.textarea1 = "";
      this.postkey = "";

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
      await this.axiosget(true);
      // let mail = Cookies.get("mail");
      // if(!mail) {
      //   this.$router.push({ path: '/think/zj', });
      // } else {
      //   this.$router.push({ path: '/think/'+mail, });
      // }
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
    async cardClick(event) {
      // console.log(event);
      this.search(event.target);
      // console.log(999);
      // console.log(this.dire_path);
      // if(event.target.className == "el-card__body") {
      //   dire_path = event.target.childNodes[2].outerText;
      // } else if(event.target.className == "el-card__body"){}
      // console.log();
      let gu;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      if(gu && gu.ret > 0) {
        this.$router.push({ path: '/think/detail/' + gu.urlmail, query: { plan: this.dire_path }});
      } else {
        this.$router.push({ path: '/think/detail/*', query: { plan: this.dire_path }});
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

:deep(.think_image) {
  width:30%;
  margin-right: 3px;
  overflow:auto;
}

.el-card-detail {
  width: 90%;
  color: #00ff00;
  margin-top: 6px;
  margin-left: 6%;
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
