<template>
  <div class="app-container" id="thought"> 
    <!-- <el-card shadow="always"> -->
      <div style="margin-top:3px;">
        <!-- <span style="font-size:26px; font-weight:600; color:#00ffee;">游客</span> -->
        <el-input
          v-model="search_param.search"
          placeholder="日期或者内容, 空格 分隔"
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
        <!-- <el-button
          class="filter-item"
          type="success"
          @click="postTravel"
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
        :autosize="{ minRows: 3, maxRows: 10 }"
        @change="editPlaceChange"
        @blur="editPlaceChange"
        placeholder="编辑区，字数应 >= 10"
      />
      <span style="margin-top:16px;color:#000000;margin-left:6px;">*姓名：</span>
      <el-input
        v-model="travelname"
        style="width: 20%;margin-top:3px;"
        @change="nameChange"
        @blur="nameChange"
        placeholder="name"
        :prefix-icon="Name"
      />
      <span style="margin-top:16px;color:#000000;margin-left:6px;">*邮箱：</span>
      <el-input
        v-model="travelemail"
        style="width: 20%;margin-top:3px;"
        placeholder="@"
        @change="mailChange"
        @blur="mailChange"
        :prefix-icon="email"
      />
      <span style="margin-top:16px;color:#000000;margin-left:6px;">*Contact：</span>
      <el-input
        v-model="travelcontact"
        style="width: 20%;margin-top:3px;"
        @change="contactChange"
        @blur="contactChange"
        placeholder=""
        :prefix-icon="Contact"
      />
      <el-button
        class="filter-item"
        type="primary"
        @click="postTravel"
        style="text-align:center;margin-left:10%;margin-top:6px;"
        >
        发布
      </el-button>
    </el-card>
    <el-card
      v-for="o in result"
      :key="o"
      class="el-card-detail"
      shadow="always"
      @click="cardClick"
    >
      <template #header>
        <div class="card-header" style="height:16px; font-size: 20px; color: #00ff00;" @click="cardClick" >
          <span @click="cardClick"> {{ o["date"] }} </span>
        </div>
      </template>
      <span style="width:60%; font-size: 16px; color: #000000;" class="cardspan1" @click="cardClick">
        <!-- {{ o["markdown"] }} -->
        <div v-html="o.markdown">
        </div>
      </span>
      <span @click="delcardClick(o)" style="color:#f0f0f0;font-size:10px;font-weight:600;margin-left:10px;">删除</span>
    </el-card>
    <el-dialog v-model="deletevisible" title="删除" width="60%" height="90%">
      <span hidden>
        <el-input
          v-model="postkey"
          placeholder="输入发布密钥"
          style="width: 30%; margin-left:20px;margin-bottom:10px;"
          class="filter-item password"
          id="elinput"
          type="password"
        />
      </span>
      <el-button type="primary" @click="carddelete" id="carddelete" style="margin-left:20px;">
        确认删除
      </el-button>
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
import Cookies from 'js-cookie';
import getusername from '/src/common.js'

export default {
  name: 'app',
  data() {
    return {
      total: 0,
      deletevisible: false,
      result: [],
      dialogFormVisible: true,
      dire_path: "",
      postkey: "",
      textarea1: "",
      postdate: "",
      imgUpPath: "",
      travelname: "",
      travelemail: "",
      travelcontact: "",
      data: {
        "postdate": 10,
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
      upLoadbutton_hidden: false,
      elupload_hidden: true,
      nowpage: Number(this.$router.currentRoute._value.query.currentpage),
      nowpagesize: Number(this.$router.currentRoute._value.query.pagesize),
      search_param: {
        currentpage: Number(this.$router.currentRoute._value.query.currentpage),
        pagesize: Number(this.$router.currentRoute._value.query.pagesize),
        search: "",
        reset: 0,
      },
      clickcard: "",
    }
  },
  mounted(){
    // this.clickpage();
    this.axiosget(true);
  },
  watch: {},
  methods: {
    editPlaceChange() {
      if(this.textarea1.length < 10) {
        ElMessage("编辑区字数应该 >= 10");
        return false;
      }
      return true;
    },
    nameChange() {
      if(this.travelname.length == 0) {
        ElMessage("姓名字数应该 > 0");
        return false;
      }
      return true;
    },
    contactChange() {
      if(this.travelcontact.length < 6) {
        ElMessage("联系方式字数应该 >= 6");
        return false;
      }
      return true;
    },
    mailChange() {
      // console.log(this.ruleForm.email);
      if(this.travelemail.length < 7) {
        ElMessage("邮箱格式不正确！");
        return false;
      }
      let r = this.travelemail;
      // console.log(r);
      let ret = r.indexOf("@");
      if( ret < 0) {              // || r.indexOf(".com") < 0
        ElMessage("邮箱格式不正确！");
        return false;
      }
      return true;
    },
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
        params: {'type' : 'travel'},
      }).then((response) => {
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
    delcardClick(event) {
      // console.log(event);
      this.clickcard = event;
      this.deletevisible = true;
    },
    async carddelete() {
      const insta = axios.create({
        baseURL: 'http://localhost:7009/travel/delete',
        timeout: 20000,
      });
          
      // console.log(this.search_param);deletecard
      insta({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        withCredentials: true,
        data: {"path":this.clickcard.path, "postkey":this.postkey, 'mail':Cookies.get('mail'),
              'password':Cookies.get('password'), 'url':document.URL},
      }).then((response) => {
        if(response.data.ret > 0) {
          this.deletevisible = false;
          this.resetSearch();
          ElMessage.success("已经删除了的！");
        } else if(response.data.ret == 0) {
          ElMessage.error("删除报错了的！");
        }
        else {
          // this.$alert("发布密钥不正确！");
          ElMessage.error("发布密钥不正确！");
        }
      });
      this.postkey = "";
    },
    postTravel() {
      if(!this.mailChange() || !this.contactChange() || !this.nameChange() || !this.editPlaceChange()) {
        return;
      }
      // console.log(this.textarea1);
      // let sharet = "45c144247124160a29e93a160e62bc7128bd33a9da552c1b9441d562240754637b38e5a25fa151044e902b99ff22ec91ffa9e9e0e2edde67317cc04adf329b78";
      // this.sha(this.postkey).then((r)=>{
      //   if(sharet == r) {
      const instance = axios.create({
        baseURL: 'http://localhost:7009/travel/post_travel',
        timeout: 20000,
      });
      instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {"postdate" : Date.now(), "text_content" : this.textarea1,
              "travelname":this.travelname, "travelemail":this.travelemail, 
              "travelcontact":this.travelcontact,
              "mail":Cookies.get("mail"), "password":Cookies.get("password"),
              'url':document.URL
              },
      }).then((response) => {
        let pt = response.data.post;
        if(!pt) {
          // this.$alert("不符合要求的，自动取消上传");
          ElMessage.error("不符合要求的，自动取消上传");
        }
        this.resetSearch();
      });
      ElMessage.success("已发布");
      // self.resetSearch();
        // }
        // else {
        //   this.$alert("发布密钥不正确，自动取消发布");
        // }
      // });
    },
    upLoadbuttonThink() {
      const instance = axios.create({
        baseURL: 'http://localhost:7009/csdn/renzheng',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      instance({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        withCredentials: true,
        data: {"postkey":this.postkey, 'url':document.URL},
      }).then((response) => {
        if(response.data.ret) {
          this.upLoadbut = document.getElementById("upLoadbuttonThink");
          this.upLoadbut.hidden = true;
          this.elupload_hidden = false;
          this.upLoadbutton_hidden = true;
          this.data.postdate = Date.now();
          // console.log(this.postdate);
          ElMessage("可以上传图片");
        } else {
          this.elupload_hidden = true;
          this.upLoadbutton_hidden = false;
          // this.$alert("发布密钥不正确，自动取消上传");
          ElMessage.error("没有登陆自动取消上传");
        }
      });
      this.postkey = "";
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
      //     this.elupload_hidden = true;
      //     this.upLoadbutton_hidden = false;
      //     this.$alert("发布密钥不正确，自动取消上传");
      //   }
      // });
    },
    async sleep(delay) { 
      return new Promise((resolve) => setTimeout(resolve, delay)); 
    },
    // handlebefore_Upload(rawFile) {
    //   if (rawFile.type !== 'image/jpeg' && rawFile.type !== "image/png"
    //       && rawFile.type !== "image/gif" && rawFile.type !== "image/bmp"
    //       && rawFile.type !== "image/jpg") {
    //     ElMessage.error('不是图片格式!');
    //     return false;
    //   } else if (rawFile.size / 1024 / 1024 > 13) {
    //     ElMessage.error('图片占用磁盘大小不能 > 13MB!');
    //     return false;
    //   }
    //   return true;
    // },
    // handleUpLoadSuccess(response) {
    //   // console.log("success");
    //   // console.log(response);
    //   this.imgUpPath = response.path;
    // },
    // handleRemove(uploadFile, uploadFiles) {
    //   console.log(uploadFile, uploadFiles);
    // },
    handlePictureCardPreview(uploadFile) {
      this.dialogImageUrl = uploadFile.url;
      this.dialogVisible = true;
    },
    axiosget(wait=true) {

      if(Cookies.get("travelsearch") && Cookies.get("travelsearch").length) {
        this.search_param.search = Cookies.get("travelsearch");
      }
      if(Cookies.get("travelReset") && Cookies.get("travelReset") == 1) {
        this.search_param.reset = 1;
      }
      const instance = axios.create({
        baseURL: 'http://localhost:7009/travel/index',
       timeout: 20000,
      });
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
      Cookies.remove("travelReset");
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
        cnt += 1;
        if(cnt > 20) {
          break;
        }
        await this.sleep(wait_think_render); // 暂停约 100 毫秒
        // search = true;
        cpn = document.getElementsByClassName("cardspan1");
      }
      if(wait) {
        await this.sleep(1000); // 暂停约 100 毫秒
      }
      // let cpn = document.getElementsByClassName("cardspan1");
      // console.log(cpn);
      // console.log(cpn[0]);
      // console.log(cpn.length);
      let span1 = document.getElementsByClassName("cardspan1");
      let len = this.result.length;
      for(let i = 0; i < len; i++) {
        span1[i].innerHTML = this.result[i].markdown;
      }
      this.search_param.currentpage = this.nowpage;
      this.search_param.pagesize = this.nowpagesize;
      // console.log(document.getElementsByClassName("cardspan1").length);
      // console.log(span2);
    },
    async current_Page_Change(val) {
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
      this.search_param.reset = 1;
      // this.$router.push({ path: '/csdn/'+gu.urlmail,  query:{"currentpage": this.nowpage, "pagesize": this.nowpagesize}})
      await this.axiosget();
    },
    handleSearch() {
      this.search_param.reset = 1;
      const instance = axios.create({
        baseURL: 'http://localhost:7009/travel/index',
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
        // this.findkey(true);
      });
      this.search_param.password = "";
      this.search_param.mail = "";
      this.search_param.url = "";

      let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
      Cookies.set("travelsearch", this.search_param.search, { expires: expiresdate });
    },
    async resetSearch() {
      this.textarea1 = "";
      this.travelname = "";
      this.travelemail = "";
      this.travelcontact = "";

      let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
      Cookies.remove("travelsearch");
      Cookies.remove("travelReset");
      Cookies.set("travelsearch", "", { expires: expiresdate });

      this.search_param.reset = 1;
      this.nowpage = 1;
      this.search_param.currentpage = this.nowpage;
      this.search_param.pagesize = this.nowpagesize;
      this.search_param.search = "";

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
      await this.axiosget(true);
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
    cardClick(event) {
      // // console.log(event);
      // this.search(event.target);
      // // console.log(999);
      // // console.log(this.dire_path);
      // // if(event.target.className == "el-card__body") {
      // //   dire_path = event.target.childNodes[2].outerText;
      // // } else if(event.target.className == "el-card__body"){}
      // // console.log();
      // this.$router.push({ path: '/travel/detail', hash: '#travel/detail', query: { plan: this.dire_path }});
    },
  },
}
</script>

<style scoped>
/* :deep(p) {
  margin: 0em 0;
  display: block;
  margin-block-start: 1em;
  margin-block-end: 0em;
  margin-inline-start: 0px;
  margin-inline-end: 0px;
  unicode-bidi: isolate;
  word-break: break-word;
  line-height: 1.0;
  font-family: -apple-system,BlinkMacSystemFont,Helvetica Neue,PingFang SC,var(--zFontSansSerif),Microsoft YaHei,Source Han Sans SC,Noto Sans CJK SC,WenQuanYi Micro Hei,sans-serif;
  font-size: 1.1em;
} */

h1 {
  font-weight: 500;
  font-size: 2.6rem;
  position: relative;
  top: -10px;
}

h3 {
  font-size: 1.2rem;
}

:deep(.think_image){
  width:30%;
  overflow:auto;
}
.el-card-detail {
  width: 90%;
  color: #00ff00;
  margin-top: 6px;
  margin-left: 6%;
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
