<template>
  <!-- <div id="firstmath">$c = \sqrt{a^2 + b^2}$</div>
  <div>
    <span> 
      $\frac{A+C}{2}$
    </span>
  </div> -->
  <el-button type="primary" plain @click="PrePage" class="PrePage_class">上一页</el-button>
  <el-button
    class="filter-item"
    type="warning"
    @click="dialogFormVisible = true"
    style="text-align:center; margin-left:60%;"
    >
    删除
  </el-button>
  <!-- <el-dialog v-model="dialogFormVisible" title="输入密钥删除" width="500"> -->
    <el-dialog v-model="dialogFormVisible" title="删除" width="500">
    <span hidden>
      <el-input
        v-model="postkey"
        style="width: 100%;overflow:auto;height:100%"
        placeholder="删除密钥"
        type="password"
      />
    </span>
    <el-button
      class="filter-item"
      type="warning"
      @click="handleDelete"
      style="text-align:center; margin-left:3px;margin-top:6px;"
      >
      确认删除
    </el-button>
  </el-dialog>
  <el-button
    class="filter-item"
    type="warning"
    @click="dialogFormVisible_top = true"
    style="text-align:center; margin-left:1%;"
    >
    最上面
  </el-button>
  <el-button
    class="filter-item"
    type="warning"
    @click="modifyvisible = true"
    style="text-align:center; margin-left:1%;"
    >
    修改
  </el-button>
  <!-- <el-dialog v-model="dialogFormVisible_top" title="输入密钥放在最上面" width="500"> -->
  <el-dialog v-model="dialogFormVisible_top" title="放在最上面的" width="500">
    <span hidden>
      <el-input
        v-model="postkey"
        style="width: 100%;overflow:auto;height:100%"
        placeholder="密钥"
        type="password"
      />
    </span>
    <el-button
      class="filter-item"
      type="warning"
      @click="handleTop"
      style="text-align:center; margin-left:3px;margin-top:6px;"
      >
      确认放在最上面
    </el-button>
  </el-dialog>
  <el-dialog v-model="modifyvisible" title="修改" width="90%" style="height:60%;margin-top:6px;">
    <el-input
      v-model="editcontent"
      style="width: 100%;overflow:auto;height:100%"
      type="textarea"
      :autosize="{ minRows: 3, maxRows: 9 }"
      placeholder="修改一个片段"
    />
    <br>
    <br>
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
        :on-success="handleUpLoadSuccess"
      >
        <el-icon><Plus /></el-icon>
    </el-upload>
    <br>
    <el-button @click="modify_content" style="margin-top:3px;">
      提交
    </el-button>
  </el-dialog>
  <el-affix :offset="130">
      <!-- <el-button type="primary">👍赞</el-button> -->
    <div class="zanzan" @click="upvoteclick" v-if="resultresult.click" 
      style="background-color:rgb(159.5, 206.5, 255);font-weight:600;
      margin-left:30px;margin-top:6px;
      ">
      {{kdianzanlength}}👍赞
    </div>
    <div class="zanzan" @click="upvoteclick" v-if="!resultresult.click"
      style="background-color:rgba(23, 114, 246, .1);
      margin-left:30px;margin-top:6px;
      ">
      {{kdianzanlength}}👍赞
    </div>
    <div class="pinglun" style="margin-left:30px;margin-top:6px;background-color:rgba(23, 114, 246, .1);">
      <span @click="commentdialog" id="pinglunpinglun">{{ resultresult['comment'].length }}评论</span>
    </div>

    <div class="shoucangshoucang" @click="shoucang" v-if="resultresult.clickshoucang" 
      style="background-color:rgb(159.5, 206.5, 255);font-weight:600;
      margin-left:30px;margin-top:6px;
      ">
      {{ kshoucanglength }}收藏
    </div>
    <div class="shoucangshoucang" @click="shoucang" v-if="!resultresult.clickshoucang" 
      style="background-color:rgba(23, 114, 246, .1);
      margin-left:30px;margin-top:6px;
      ">
      {{ kshoucanglength }}收藏
    </div>
  </el-affix>
  <div id="detailvue" class="detailthink">
  </div>
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
      v-for="oh in resultresult['comment']"
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
import katex from "katex"
import renderMathInElement from 'katex/contrib/auto-render/auto-render.js'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import Cookies from 'js-cookie';
import getusername from '/src/common.js'

export default {
  name: 'markdown_detail',
  data() {
    return {
      result: "",
      path: "",
      resultresult: {'path': "", "upvote":[], 'comment':[], 'click':false,
                     'clickshoucang':false, 'kshoucang':[], 'title':""},
      dialogFormVisible: false,
      textarea_content: "",
      modifyvisible: false,
      kshoucanglength:0,
      kdianzanlength:0,
      editcontent:"",
      commentvisible: false,
      dialogFormVisible_top: false,
      postkey: "",
      postkey_top: "",
      data: {
        "postdate": -10,
      },
    }
  },
  mounted(){
    // this.clickpage();
    this.detailget();
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
        params: {'type' : 'tkdetail'},
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
      // console.log(event, this.dire_path, first, k0, k1, path ,clicka);
      if(this.resultresult['clickshoucang']) {
        this.resultresult['clickshoucang'] = false;
        this.kshoucanglength = Math.max(0, this.kshoucanglength - 1);
        event.srcElement.innerHTML = `${this.kshoucanglength.toString()}收藏<span hidden><p :hidden="true" class="hiddenp">false</p></span>`;
      } else {
        this.resultresult['clickshoucang'] = true;
        this.kshoucanglength = Math.max(0, this.kshoucanglength + 1);
        event.srcElement.innerHTML = `${this.kshoucanglength.toString()}收藏<span hidden><p :hidden="true" class="hiddenp">true</p></span>`;
      }
      // console.log(this.resultresult);
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
          'click':this.resultresult['clickshoucang'], 'path':this.resultresult['path'], 'title':this.resultresult['title'],
        },
      }).then((response) => {
        let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
        Cookies.remove("thinkReset");
        Cookies.set("thinkReset", 1, { expires: expiresdate });
        // this.resetSearch();
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
          'path':this.resultresult['path'], 'comment':this.textarea_content,
        },
      }).then((response) => {
        this.commentvisible = false;
        this.textarea_content = "";
        location.reload();

        let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
        Cookies.remove("thinkdetail_reload");
        Cookies.set("thinkdetail_reload", 1, { expires: expiresdate });

        Cookies.remove("thinkReset");
        Cookies.set("thinkReset", 1, { expires: expiresdate });
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
      let k1 = this.resultresult['comment'].length;
      // console.log(k1, kkk);
      if(k1==0) {
        ElMessage.info("没有任何评论！");
        if(!Cookies.get("mail")) {
          return;
        }
      }
      // let kl = document.getElementById("commentsigleid");
      // kl.innerHTML = this
      // console.log(event, this.dire_path, this.commentsigle);
      this.commentvisible = true;
    },
    handlePictureCardPreview(uploadFile) {
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
      this.data.url = document.URL;
      this.data.detail = "think_detail";
      this.data.path = this.path;
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
        // ElMessage.error('输入的密钥不对, 自动取消上传!');
        ElMessage.error('没有登陆不能修改!');
        return false;
      }
      // console.log("success");
      // console.log(response);
      this.imgUpPath = response.path;
    },
    handleRemove(uploadFile, uploadFiles) {
      // console.log(uploadFile, uploadFiles);
    },
    async upvoteclick(event) {
      let id = document.URL;
      id = id.substring(0, 50);
      let index = id.indexOf("/zj");

      if(!Cookies.get("mail") && index < 0) {
        ElMessage.error("没有登陆不能操作！");
        return
      }
      let k1 = 0;
      // console.log(event, this.dire_path, first, k0, k1, path ,clicka);
      // console.log(this.kdianzanlength);
      if(this.resultresult['click']) {
        this.resultresult['click'] = false;
        this.kdianzanlength = Math.max(0, this.kdianzanlength - 1);
        // event.srcElement.innerHTML = `${this.kdianzanlength.toString()}👍赞<span hidden><p :hidden="true" class="hiddenp">false</p></span>`;
      } else {
        this.resultresult['click'] = true;
        this.kdianzanlength = Math.max(0, this.kdianzanlength + 1);
        // event.srcElement.innerHTML = `${this.kdianzanlength.toString()}👍赞<span hidden><p :hidden="true" class="hiddenp">true</p></span>`;
      }
      
      // console.log(this.kdianzanlength);
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
          'click':this.resultresult['click'], 'path':this.resultresult['path'],
        },
      }).then((response) => {
        // alert(response);
        // console.log(response.data);
        // console.log(response.type);
        // console.log(response.status);
        // console.log(response.statusText);
        // console.log(response.headers);
        // console.log(response.config);
        let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
        Cookies.remove("thinkReset");
        Cookies.set("thinkReset", 1, { expires: expiresdate });
      });
    },
    async handleTop() {
      const instance = axios.create({
        baseURL: 'http://localhost:7009/think/placeTop',
        timeout: 20000,
      });
          
      // console.log(this.search_param);
      instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {"path":this.path, 'mail':Cookies.get("mail"), 'password':Cookies.get("password"), 
              'postkey':this.postkey, 'url':document.URL,
        },
      }).then((response) => {
        if(response.data.ret < 0) {
          // ElMessage.error('输入的密钥不对！');
          ElMessage.error('没有登陆不能修改!');
          return false;
        }
        this.path = response.data.path;
        this.$router.go(-1);
        ElMessage("已经放在最上面");
      })
    },
    async modify_content() {
      this.path = this.$router.currentRoute._value.query.plan;
      const instance = axios.create({
        baseURL: 'http://localhost:7009/think/modify',
       timeout: 20000,
      });
      
      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {"path":this.path, "mail":Cookies.get("mail"), 'url':document.URL, 'password':Cookies.get("password"),
          'postkey':"-", 'editcontent':this.editcontent,
        },
      }).then((response) => {
        if(response.data.ret < 0) {
          // ElMessage.error('输入的密钥不对！');
          ElMessage.error('没有登陆不能修改!');
          return false;
        }
        ElMessage.success("片段已经发布");
        this.modifyvisible = false;
        location.reload();
      });
    },
    async detailget() {
      this.path = this.$router.currentRoute._value.query.plan;
      // console.log(this.path);
      const instance = axios.create({
        baseURL: 'http://localhost:7009/think/detail',
       timeout: 20000,
      });
      
      // console.log(this.search_param);
      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {"path":this.path, "mail":Cookies.get("mail"), 'url':document.URL},
      }).then((response) => {
        // alert(response);
        // console.log(response.data);
        // console.log(response.type);
        // console.log(response.status);
        // console.log(response.statusText);
        // console.log(response.headers);
        // console.log(response.config);
        this.result = response.data.markdown;
        this.editcontent = response.data.original;
        let detailvue = document.getElementById("detailvue");

        this.resultresult = response.data;

        this.kdianzanlength = this.resultresult['upvote'].length;
        this.kshoucanglength = this.resultresult['kshoucang'].length;
        // console.log(detailvue);
        // console.log(this.result);
        // detailvue.innerHTML = "<img src=\"getImage(\"/home/zj/zoujiu_blogown/vue-project/article/csdn_spider_selenium/article/juanzengjiludeneirong/0.jpg\")\">";
        // detailvue.innerHTML = "<img src=\"https://pic3.zhimg.com/v2-d98fe6a0590ba30f4398094ec902ed3c_r.jpg\">";
        
        // let htmlctl = katex.renderToString(this.result, {throwOnError: false});
        detailvue.innerHTML = this.result;

        // let katex_element_collect = document.getElementsByClassName("katexspan");
        // let len = katex_element_collect.length;
        // for(let i = 0; i < len; i++) {
        //   let kec = katex_element_collect[i];
        //   katex.render(kec.outerText, kec, {
        //     throwOnError: false
        //   });
        // }

        // renderMathInElement(detailvue, {
        //   // customised options
        //   // • auto-render specific keys, e.g.:
        //   delimiters: [
        //       {left: '$', right: '$', display: true},
        //   ],
        //   // • rendering keys, e.g.:
        //   throwOnError : false
        // });
        // // detailvue.innerHTML = this.result;
        

        // var imgimg = document.getElementsByClassName("img_blank_class");
        // console.log(imgimg);
        // var src;
        // for(let i=0; i < imgimg.length; i++) {
        //   let img = imgimg[i];
        //   console.log(img.src);
        //   console.log(img.baseURI);
        //   src = img.src;
        //   src = src.replace(img.baseURI, "/");
        //   console.log(src);
        //   // let index = img.find("");
        //   imgimg[i].src = new URL(src, import.meta.url).href; //https://blog.csdn.net/qq_43813351/article/details/129465422?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522535B307D-0005-4832-B344-227698E7F9A0%2522%252C%2522scm%2522%253A%252220140713.130102334.pc%255Fall.%2522%257D&request_id=535B307D-0005-4832-B344-227698E7F9A0&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~first_rank_ecpm_v1~rank_v31_ecpm-23-129465422-null-null.142^v100^pc_search_result_base9&utm_term=ReferenceError%3A%20require%20is%20not%20defined&spm=1018.2226.3001.4187
        // }
        // console.log(typeof(src));
        // console.log(imgimg[0].src.replace(imgimg[0].baseURI, "/")); 
        // // imgimg[0].src = new URL(imgimg[0].src.replace(imgimg[0].baseURI, "/"), import.meta.url).href;
        // let stk = "/home/zj/zoujiu_blogown/vue-project/article/csdn_spider_selenium/article/juanzengjiludeneirong/0.jpg";
        // let kk = String(stk);
        // let kkk = new URL("/home/zj/zoujiu_blogown/vue-project/article/csdn_spider_selenium/article/juanzengjiludeneirong/0.jpg", import.meta.url).href;
        // console.log(kkk);
        // imgimg[0].src

        // let element = document.getElementById("firstmath");
        // console.log(element);
        // console.log(document.getElementById("firstmath"));
        // katex.render("\\hat x_{k|k-1}+K_k(Z_k-H_k\\hat x_{k|k-1})", element, {
        //     throwOnError: false
        // });
        // let html = katex.renderToString("x_{k|k}=\hat x_{k|k-1}+K_k(Z_k-H_k\hat x_{k|k-1})", {
        //     throwOnError: false
        // });
        // console.log(html);
        // console.log(element);
        // element.innerHTML = html;
      });
      let reload = Cookies.get('thinkdetail_reload')
      if(reload==1) {
        let pinglun = document.getElementById("pinglunpinglun");
        pinglun.click();
        let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
        Cookies.remove("thinkdetail_reload");
        Cookies.set("thinkdetail_reload", 0, { expires: expiresdate });
      }
      // render();
    },
    getImage(k) {
      // console.log(k);
    },
    async PrePage() {
      // this.$router.go(-1);
      let gu;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      if(gu && gu.ret > 0) {
        this.$router.push({ path: '/think/'+gu.urlmail, query:{"currentpage": Cookies.get("think"), "pagesize": Cookies.get("thinkpage")}});
      } else {
        // this.$router.push({ path: '/think/zj'});
        this.$router.push({ path: '/think/homepage'});
      }
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
    async handleDelete() {
      this.dialogFormVisible = false;
      ElMessage.info("正在删除的请等待！");
      const instanc = axios.create({
        baseURL: 'http://localhost:7009/think/delete',
        timeout: 20000,
      });
            
      // console.log(this.path);
      instanc({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {"path": this.path, 'mail':Cookies.get("mail"), 
                "password":Cookies.get("password"), 'postkey':this.postkey,
                "url":document.URL},
      }).then((response) => {
        // console.log(response.data);
        if(response.data.ret > 0) {
          ElMessage.warning("已经删除了的！");
          this.PrePage();
        } else if(response.data.ret == 0) {
          ElMessage.warning("删除报错了的！");
          return false;
        }
        else {
          // ElMessage.warning("输入的密钥不对！");
          ElMessage.error('没有登陆不能修改!');
          return false;
        }
      });
      this.postkey = "";
      // // this.$confirm("确认删除").then(()=>{
      // let sharet = "45c144247124160a29e93a160e62bc7128bd33a9da552c1b9441d562240754637b38e5a25fa151044e902b99ff22ec91ffa9e9e0e2edde67317cc04adf329b78";
      // this.sha(this.postkey).then((r)=>{
      //   if(sharet == r) {
      //     const instance = axios.create({
      //       baseURL: 'http://localhost:7009/think/delete',
      //       timeout: 20000,
      //     });
            
      //       // console.log(this.path);
      //     instance({
      //         method: 'GET',
      //         headers: {
      //           'X-Requested-With': 'XMLHttpRequest'
      //         },
      //         params: {"path": this.path},
      //       }).then((response) => {
      //         // console.log(response.data);
      //         this.PrePage();
      //     });
      //   } else {
      //     this.$alert("密钥不正确，自动取消删除");
      //   }
      // });
    },
    handleEdit() {

    },
  },
}
</script>

<style scoped>
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

:deep(.zanzan){
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
:deep(.pinglun) {
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
:deep(.shoucangshoucang) {
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

.detailthink {
  margin-left:10%; 
  margin-right:10%;
  background-color:#ffffff;
  padding-left:60px;
  padding-right: 60px;
  padding-top: 30px;
  padding-bottom: 30px;
}

:deep(#detailvue) {
  width: 30%;
  margin-left: 20%;
  margin-right: 20%;
}

:deep(img) {
  width: 100%;
}

:deep(.codestyle) {
  background-color: #ffeeee;
}

:deep(.writing_margin) {
  overflow:auto;
  margin-top: 3em;
  margin-left: 20px;
  margin-right: 10px;
  margin-bottom: 20px;
}
.PrePage_class {
  margin-top:10px;
  margin-bottom:0px;
  margin-left:3px;
}
</style>
  