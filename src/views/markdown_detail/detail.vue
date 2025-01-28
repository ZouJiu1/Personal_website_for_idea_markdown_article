<template>
  <!-- <div id="firstmath">$c = \sqrt{a^2 + b^2}$</div>
  <div>
    <span> 
      $\frac{A+C}{2}$
    </span>
  </div> -->
    <!--
      http://121.40.168.141:7000
      http://localhost:7009
      http://localhost:7009
      http://localhost/hls/live.m3u8
      http://localhost:7009/hls/live.m3u8
      [kalman推导](http://localhost:7009/#/csdn/markdown_detail?plan=/home/admin/vue-project/article/zhihu_spider_selenium/article/2023-08-22_14_00_%E5%8D%A1%E5%B0%94%E6%9B%BC%E6%BB%A4%E6%B3%A2%E6%8E%A8%E5%AF%BC%E5%92%8C%E5%BA%94%E7%94%A8Kalman_%E7%A9%BA%E6%A0%BC_filter_IP_%E5%B1%9E%E5%9C%B0%E4%B8%8A%E6%B5%B7/%E5%8D%A1%E5%B0%94%E6%9B%BC_.md#csdn/markdown_detail): 
    -->
  <el-button type="primary" plain @click="PrePage" class="PrePage_class">上一页</el-button>
  <el-button
    class="filter-item"
    type="success"
    @click="handleEdit"
    style="text-align:center; margin-left:70%;"
    >
    编辑
  </el-button>
  <el-button
    class="filter-item"
    type="warning"
    @click="dialogFormVisible = true"
    style="text-align:center; margin-left:2%;"
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
    style="text-align:center; margin-left:2%;"
    >
    最上面
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
  <div id="detailvue" class="detailarticle">
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
// import renderMathInElement from 'katex/contrib/auto-render/auto-render.js'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import Cookies from "js-cookie";
import getusername from '/src/common.js'
// import imgURL from '/home/zj/zoujiu_blogown/vue-project/article/csdn_spider_selenium/article/2024-09-16_空格_13_43_28_临时发布的文篇_感叹号_/1寸_1__.jpg'
export default {
  name: 'markdown_detail',
  data() {
    return {
      result: "",
      postkey: "",
      path: "",
      resultresult: {'path': "", "upvote":[], 'comment':[], 'click':false,
                     'clickshoucang':false, 'kshoucang':[], 'title':""},
      dialogFormVisible: false,
      textarea_content: "",
      kshoucanglength:0,
      kdianzanlength:0,
      commentvisible: false,
      dialogFormVisible_top: false,
    }
  },
  mounted(){
    this.detailget();
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
        params: {'type' : 'csdn_zhihu_detail'},
      }).then((response) => {
      });
      // console.log(window);
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
          'click':this.resultresult['clickshoucang'], 'path':this.resultresult['path'], 'title':this.resultresult['title'],
        },
      }).then((response) => {
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
          'path':this.resultresult['path'], 'comment':this.textarea_content,
        },
      }).then((response) => {
        this.commentvisible = false;
        this.textarea_content = "";
        location.reload();

        let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
        Cookies.remove("csdndetail_reload");
        Cookies.set("csdndetail_reload", 1, { expires: expiresdate });
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

      });
    },
    async handleTop() {
      const instance = axios.create({
        baseURL: 'http://localhost:7009/csdn/placeTopTop',
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
      this.postkey = "";
    },
    async detailget() {
      // console.log(this.$router);
      this.path = this.$router.currentRoute._value.query.plan;
      
      const instance = axios.create({
        baseURL: 'http://localhost:7009/markdown_detail/index',
       timeout: 20000,
      });
      
      // console.log(this.search_param);
      await instance({
        method: 'GET',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        params: {"path":this.path, 'url':document.URL, 'mail':Cookies.get("mail"), 'password':Cookies.get("password")},
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
        this.resultresult = response.data;
        let detailvue = document.getElementById("detailvue");

        this.kdianzanlength = this.resultresult['upvote'].length;
        this.kshoucanglength = this.resultresult['kshoucang'].length;
        // console.log(detailvue);
        // console.log(this.result);
        // console.log( "imgURL",imgURL);
        // detailvue.innerHTML = "<img src=\"/article/csdn_spider_selenium/article/2024-09-16_空格_13_43_28_临时发布的文篇_感叹号_/1寸_1__.jpg\"/>";
        // detailvue.innerHTML = "<img src=\"/article/csdn_spider_selenium/article/2024-09-16_空格_13_43_28_临时发布的文篇_感叹号_/1寸_1__.jpg\"/>";
        // detailvue.innerHTML = "<img src=\"https://pic3.zhimg.com/v2-d98fe6a0590ba30f4398094ec902ed3c_r.jpg\">";
        
        // let htmlctl = katex.renderToString(this.result, {throwOnError: false});
        detailvue.innerHTML = this.result;

        let katex_element_collect = document.getElementsByClassName("katexspan");
        let len = katex_element_collect.length;
        for(let i = 0; i < len; i++) {
          let kec = katex_element_collect[i];
          katex.render(kec.outerText, kec, {
            throwOnError: false
          });
        }

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
        // let kkk = new URL("/Users/zoujiu/Desktop/webpage/vue-project/article/github_yolov3/8.jpg", import.meta.url).href;
        // console.log(kkk);
        // this.$alert(kkk);
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
      // render();
      let reload = Cookies.get('csdndetail_reload')
      if(reload==1) {
        let pinglun = document.getElementById("pinglunpinglun");
        pinglun.click();
        let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
        Cookies.remove("csdndetail_reload");
        Cookies.set("csdndetail_reload", 0, { expires: expiresdate });
      }
    },
    getImage(k) {
      // console.log(k);
    },
    async PrePage() {
      let zhihu = this.path.indexOf("zhihu_");
      // console.log("zhihu");
      // console.log(zhihu);
      if(zhihu >= 0) {
        this.$router.push({ path: '/zhihu/*', });
        this.$router.go(-1);
      } else {
        // let url = document.URL;
        // let end = url.indexOf("?plan");
        // let md = 'markdown_detail';
        // let start = url.indexOf(md);
        // let mail = url.substring(start + md.length + 1, end);

        // let kk = 0;
        // console.log(window.history);
        // url = window.history.state.back;
        // let equal = url.indexOf("currentpage=");
        // let lecur = "currentpage=".length
        // kk = url.substring(equal + lecur)
        // console.log(mail);
        let gu;
        await getusername(document.URL).then((response) => {
          gu = response;
        });
        // let urlrul = document.URL;
        // if(gu && gu.ret > 0) {
        //   index = urlrul.indexOf(gu.mail);
        // }
        // if(gu && gu.ret > 0 && index < 0) {
        //   this.$router.push({ path: '/csdn/' + this.findmail(urlrul)});
        // }
        if(gu && gu.ret > 0) {
          // this.$router.push({ path: '/csdn/'+gu.urlmail}); // query:{"currentpage": 1, "pagesize":20}
          this.$router.push({ path: '/csdn/' + gu.urlmail,  query:{"currentpage": Cookies.get("csdn"), "pagesize": Cookies.get("csdnpage")}});
        } else {
          // this.$router.push({ path: '/csdn/zj'}); //, query:{"currentpage": 1, "pagesize":20}
          this.$router.push({ path: '/csdn/homepage'}); //, query:{"currentpage": 1, "pagesize":20}
        }
        // this.$router.go(-1);
      }
      // this.$router.go(-1);
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
        baseURL: 'http://localhost:7009/csdn/delete',
        timeout: 20000,
      });
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
    },
    handleEdit() {
      let zhihu = this.path.indexOf("zhihu_");
      // console.log("zhihu");
      // console.log(zhihu);
      if(zhihu >= 0) {
        this.$router.push({ path: '/zhihu/notify_edit/*', });
      }
      // this.$router.go(-1);
      // console.log(document.URL);
      let url = document.URL;
      let end = url.indexOf("?plan");
      let md = 'markdown_detail';
      let start = url.indexOf(md);
      let mail = url.substring(start + md.length + 1, end);
      // console.log(111111, mail);
      this.$router.push({ path: '/csdn/post_article/' + mail, query: { plan: this.path }});
    },
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

.detailarticle {
  margin-left:10%; 
  margin-right:10%;
  background-color:#ffffff;
  padding-left:60px;
  padding-right: 60px;
  padding-top: 30px;
  padding-bottom: 30px;
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

:deep(.img_blank_class) {
  width: 79%;
  /* align: center; */
  margin-left:10%;
  overflow: auto;
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


:deep(strong) {
  font-weight: 790;
}

:deep(p strong) {
  font-weight: 790;
}

/* :deep(p code) {
  padding: 6px;
  margin: 0 0 3px;
  background: #dfe0e2;
  overflow: auto;
  font-weight:600;
} */

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
:deep(#detailvue) {
  width: 30%;
  margin-left: 20%;
  margin-right: 20%;
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

:deep(.post_revise_time) {
  margin-left: 70%;
  font-size: 16px;
  font-weight: 600;
  margin-bottom:100px;
}
.PrePage_class {
  margin-top:10px;
  margin-bottom:0px;
  margin-left:3px;
}
</style>
  