<template>
  <div class="app-container">
    <!-- <el-card shadow="always"> -->
      <div style="margin-top:3px;">
        <el-input
          v-model="search_param.search"
          placeholder="描述或者日期"
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
        <span style="margin-left:20px;">浏览器不支持avi格式，最好是上传mp4、webm格式</span>
        <span hidden>
          <el-input
            v-model="postkey"
            placeholder="输入发布密钥"
            style="width: 10%; margin-left:6px;overflow:auto;"
            class="filter-item"
            id="elinput"
            type="password"
          />
        </span>
        <el-button
          class="filter-item"
          type="primary"
          style="margin-left:20px;text-align:center;"
          @click="handlebutton_upload"
          >
          发布一个视频
        </el-button>
        <el-dialog v-model="dialogFormVisible" title="发布一个视频" width="500">
          <el-input
            v-model="textarea1"
            style="width: 100%;overflow:auto;height:100%"
            placeholder="对视频的描述"
          />
          <el-upload
            class="upload-demo"
            style="margin-top:6px;"
            drag
            action="http://localhost:7009/upload_video/upload"
            :before-upload="handlebefore_Upload"
            :on-success="handleUpLoadSuccess"
            :data="data"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              Drop file here or <em>click to upload</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                webm/mp4 files with a size less than 2G
              </div>
            </template>
          </el-upload>
        </el-dialog>
      </div>
    <!-- </el-card> -->
    <el-card 
      class="el-card-detail"
      shadow="always"
      style="overflow:auto;"
      v-if="notrelease"
    >
      <template #header>
        <div style="overflow:auto; font-size: 18px; color: #ff9900;">
          <span style="margin-left:0px;color:chocolate;font-weight:600;">严格遵守法律法规，欢迎监督</span>
          <span style="margin-left:10px;">音频直播（消耗的流量很少，常开）</span>
          <span style="margin-left:10px;">视频直播（消耗的流量很多，平时基本不开）</span>
        </div>
      </template>
      <video id="livevideo" controls autoplay>
      </video>
      <template #footer>
        <div>
          <span style="color:#000000;">拖到最后就是直播，进度条是浏览器的缓存导致的</span>
          <el-button
            class="filter-item"
            type="primary"
            style="margin-left:6px;text-align:center;"
            @click="dialogFormVisible_liulinag=true;"
            >
            查看
          </el-button>
          <span style="margin-left:6px;">音频每小时消耗的流量，当前每小时消耗约16Mb流量。</span>
          <el-dialog v-model="dialogFormVisible_liulinag" title="纯音频直播每小时消耗流量" width="70vh">
            <el-table
              :data="tableData"
              style="width: 100%"
              :row-class-name="tableRowClassName"
            >
              <el-table-column prop="caiyanglv" label="采样率" />
              <el-table-column prop="minute" label="时间(min)" />
              <el-table-column prop="calcul" label="计算" />
              <el-table-column prop="result(Mb/hour)" label="结果(Mb/hour)" />
            </el-table>
            <span style="font-size:16px; color:#1989fa">
              若视频直播，配置是，视频输出：1280x720，24fps，音频输出：44100Hz，aac，24973168/1024/1024 * 60，1429Mb/Hour
            </span>
          </el-dialog>
        </div>
      </template>
    </el-card>
    <el-card 
      class="el-card-detail"
      shadow="always"
      style="overflow:auto;margin-top:10px;margin-bottom: 10px;"
    >
      <div style="overflow:auto; font-size: 18px; color: #ff9900;" id='audioplayback'>
        <span style="margin-left:0px;color:chocolate;font-weight:600;">
          音频</span>
        <el-cascader
          v-model="valueCascader"
          :options="options"
          :prop="props"
          @change="handleCascaderChange"
          style='margin-left:10px;'/>
        <audio id="liveaudio" controls style='margin-left:20px;width:60%;'>
          <!-- <source src="/home/zj/zoujiu_blogown/vue-project/hls/output.mpeg"> -->
          <!-- <source :src="valueCascader" id="audioSource" type="audio/mpeg"> -->
          <!-- <source src="/hls/output.mp3" type="audio/mpeg"> -->
        </audio>
      </div>
    </el-card>
    <el-card 
      v-for="o in result"
      :key="o" 
      class="el-card-detail"
      shadow="always"
      @click="cardClick"
      style="overflow:auto;"
    >
      <template #header>
        <div class="card-header" @click="cardClick" >
          <span @click="cardClick" style="overflow:auto; font-size: 20px; color: #000000; font-weight:600;">{{ o["describe"] }} </span>
          <span @click="cardClick" style="overflow:auto; font-size: 13px; color: #000000; margin-left:10%;">{{ o["title"] }} </span>
          <!-- <p :hidden="true" @click="cardClick" class="hiddenp"> {{ o["path"] }} </p> -->
        </div>
      </template>
      <span style="width:60%; font-size: 16px; color: #000000;" @click="cardClick">
        <!-- {{ o["path"] }} -->
        <!-- https://developer.mozilla.org/zh-CN/docs/Web/HTML/Element/video#%E5%B0%9D%E8%AF%95%E4%B8%80%E4%B8%8B -->
        <!-- https://developer.mozilla.org/en-US/docs/Web/Media/Formats/codecs_parameter -->
        <video controls id="myVideo">
          <source :src="o.path" type="video/x-msvideo">
          <source :src="o.path" type="video/avi">
          <source :src="o.path" type="video/mp4">
          <source :src="o.path" type="video/ogg">
          <source :src="o.path" type="video/webm">
        </video>
      </span>
      <!-- <p :hidden="true" @click="cardClick" class="hiddenp"> {{ o["path"] }} </p> -->
      <template #footer>
        <div class="card-footer" style="overflow:auto; font-size: 16px; color: #0000ee;" @click="cardClick">
          <span @click="cardClick"> {{ o["date"] }} </span>
          <span @click="delcardClick(o)" style="color:#f0f0f0;font-size:10px;font-weight:600;margin-left:60%;">删除</span>
          <!-- <p :hidden="true" @click="cardClick" class="hiddenp"> {{ o["path"] }} </p> -->
        </div>
      </template>
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
import axios from 'axios'
// import { reactive, ref } from 'vue'
import Hls from 'hls.js';
// import Player from 'xgplayer';
// import 'xgplayer/dist/index.min.css';
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import Cookies from 'js-cookie';
import getusername from '/src/common.js'
import notrelease from "/src/main.js"
export default {
  name: 'app',
  data() {
    return {
      total: 0,
      deletevisible: false,
      result: [],
      dire_path: "",
      textarea1: "",
      notrelease: notrelease,
      postkey: "",
      options: [],
      valueCascader: "",
      props: {'expandTrigger':'hover'},
      dialogFormVisible_liulinag: false,
      data: {
        "textarea1": "",
      },
      tableData: [
        {
          "caiyanglv":"7305",
          "minute":"2",
          "calcul":"664204/2/1024/1024 * 60 - 3",
          "result(Mb/hour)":"16M/H",
        },
        {
          "caiyanglv":"8000",
          "minute":"1",
          "calcul":"374920/1024/1024 * 60 - 3",
          "result(Mb/hour)":"18M/H",
        },
        {
          "caiyanglv":"11025",
          "minute":"1",
          "calcul":"522640/1024/1024 * 60 - 4",
          "result(Mb/hour)":"25M/H",
        },
        {
          "caiyanglv":"16000",
          "minute":"1",
          "calcul":"736208/1024/1024 * 60 - 6",
          "result(Mb/hour)":"36M/H",
        },
        {
          "caiyanglv":"22050",
          "minute":"1",
          "calcul":"982864/1024/1024 * 60 - 6",
          "result(Mb/hour)":"50M/H",
        },
        {
          "caiyanglv":"44100",
          "minute":"2",
          "calcul":"2177980/1024/1024/2 * 60 - 8",
          "result(Mb/hour)":"54M/H",
        },
        {
          "caiyanglv":"96000",
          "minute":"1",
          "calcul":"2213700/2/1024/1024 * 60 - 8",
          "result(Mb/hour)":"55M/H",
        },
      ],
      dialogFormVisible: false,
      nowpage: Number(this.$router.currentRoute._value.query.currentpage),
      nowpagesize: Number(this.$router.currentRoute._value.query.pagesize),
      search_param: {
        currentpage: Number(this.$router.currentRoute._value.query.currentpage),
        pagesize: Number(this.$router.currentRoute._value.query.pagesize),
        search: "",
        reset: 0,
      },
      clickcard:"",
    }
  },
  mounted(){
    // this.clickpage();
    this.livevideo_function();
    // this.xgplayer_start();
    this.axiosget();
  },
  watch: {},
  methods: {
    delcardClick(event) {
      // console.log(event);
      this.clickcard = event;
      this.deletevisible = true;
    },
    async carddelete() {
      const insta = axios.create({
        baseURL: 'http://localhost:7009/upload_video/delete',
        timeout: 20000,
      });
          
      // console.log(this.search_param);deletecard
      this.deletevisible = false;
      insta({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        withCredentials: true,
        data: {'url':document.URL, "txt":this.clickcard.txt, 'ideo':this.clickcard.ideo, 
              "postkey":this.postkey, 'mail':Cookies.get('mail'),
              'password':Cookies.get('password')},
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
        params: {'type' : 'video'},
      }).then((response) => {
      });
    },
    handleCascaderChange() {
      let audioplayback = document.getElementById("audioplayback");
      let audio = document.createElement("audio");
      audio.controls="true"; 
      audio.style='margin-left:20px;width:60%;';
      let item = document.createElement("source");
      item.src = this.valueCascader[1];
      item.type="audio/mpeg";
      audio.appendChild(item);
      audioplayback.removeChild(audioplayback.lastChild);
      audioplayback.appendChild(audio);
      // let liveaudio = document.getElementById('liveaudio');
      // liveaudio.lastChild.src = this.valueCascader;
      // liveaudio.innerHTML = "";
      // let item = document.createElement("source");
      // item.src = this.valueCascader;
      // item.type="audio/mpeg";
      // liveaudio.appendChild(item);
    },
    // xgplayer_start() {
    //   const player = new Player({
    //       id: 'videohls',
    //       url: '/hls/live.m3u8',
    //       height: '100%',
    //       width: '100%',
    //       autoplayMuted: true,
    //       autoplay: true
    //   })
    //   // player.start();
    //   // player.play();
    // },
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
    async handlebutton_upload() {
      let gu;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      const instance = axios.create({
        baseURL: 'http://localhost:7009/csdn/renzheng',
       timeout: 20000,
      });
      
      // console.log(this.search_param);
      await instance({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        withCredentials: true,
        data: {'url':document.URL, "postkey":this.postkey},
      }).then((response) => {
        if(response.data.ret || (gu && gu.ret == 1)) {
          this.dialogFormVisible = true;
        } else {
          // this.$alert("发布密钥不正确，自动取消发布");
          ElMessage.error("没有登陆自动取消发布");
        }
      });
      // this.postkey = "";
      // let sharet = "45c144247124160a29e93a160e62bc7128bd33a9da552c1b9441d562240754637b38e5a25fa151044e902b99ff22ec91ffa9e9e0e2edde67317cc04adf329b78";
      // this.sha(this.postkey).then((r)=>{
      //   if(sharet == r) {
      //     this.dialogFormVisible = true;
      //   } else {
      //     this.$alert("发布密钥不正确，自动取消发布");
      //   }
      // });
    },
    handleUpLoadSuccess() {
      // this.$alert("视频已经上传了！");
      ElMessage.success("视频已经上传了！");
      this.resetSearch();
      this.postkey = "";
      this.dialogFormVisible = false;
    },
    handlebefore_Upload(rawFile) {
      this.data.textarea1 = this.textarea1;
      this.data.mail = Cookies.get("mail");
      this.data.password = Cookies.get("password");
      this.data.postkey = this.postkey;
      this.data.url = document.URL;
      // console.log(this.data.textarea1);
      if(this.textarea1.length==0) {
        ElMessage.error("没填写视频描述，先填写再上传！");
        return false;
      }
      if (rawFile.type !== 'video/mp4' && rawFile.type !== "video/webm") {
        ElMessage.error('不支持这种视频格式!');
        return false;
      } else if (rawFile.size / 1024 / 1024 > (1024 * 2)) {
        ElMessage.error('视频占用磁盘大小不能 > 2G!');
        return false;
      }
      return true;
    },
    async livevideo_function(videoSrc = '/hls/live.m3u8') {
      if(!this.notrelease) {
        return;
      }
      var video__ = document.getElementById('livevideo');
      // var videoSrc_lv = '/hls/live.m3u8';
      let gu, videoSrc_lv="";
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      if(gu && gu.ret > 0) {
        videoSrc_lv = '/hls/'+ gu.mail +'.m3u8';
      } else {
        videoSrc_lv = videoSrc;
      }
      // videoSrc_lv = 'http://ivi.bupt.edu.cn/hls/cctv1hd.m3u8';
      // videoSrc_lv = '/home/zj/zoujiu_blogown/vue-project/article/video/IMG_8135(1).MP4';
      //
      // First check for native browser HLS support
      //
      if (video__.canPlayType('application/vnd.apple.mpegurl')) {
        video__.src = videoSrc_lv;
        // video__.src = 'http://ivi.bupt.edu.cn/hls/cctv1hd.m3u8';
        video__.addEventListener('loadedmetadata',function() {
          hls_lv.startLoad();
          video__.muted = false;
          video__.play();
        });
        // console.log('native HLS support');
        //
        // If no native HLS support, check if HLS.js is supported
        //
      } else if (Hls.isSupported()) {
        var hls_lv = new Hls({debug:false});
        hls_lv.loadSource(videoSrc_lv);
        hls_lv.attachMedia(video__);
        // hls_lv.on(Hls.Events.MANIFEST_PARSED, function(){
        //   video__.play();
        // });
        hls_lv.on(Hls.Events.MEDIA_ATTACHED, function () {
          // console.log('video and hls.js are now bound together !');
          // video__.muted = true;
          // video__.play();
        });
        hls_lv.on(Hls.Events.MANIFEST_PARSED, function (event, data) {
          // console.log(
            // 'manifest loaded, found ' + data.levels.length + ' quality level',
          // );
          video__.muted = false;
          video__.play();
          video__.autoplay = true;
          // video__.
        });
        // console.log('not native HLS support');
      } else {
        // console.log('wrong!');
      }
    },
    axiosget() {
      const instance = axios.create({
        baseURL: 'http://localhost:7009/video/index',
       timeout: 20000,
      });
      
      // console.log(this.search_param);
      let csrftoken = {};
      this.search_param.password = Cookies.get("password");
      this.search_param.mail = Cookies.get("mail");
      this.search_param.url = document.URL;
      if(Cookies.get("videosearch") && Cookies.get("videosearch").length) {
        this.search_param.search = Cookies.get("videosearch");
      }
      if(Cookies.get("videoReset") && Cookies.get("videoReset") == 1) {
        this.search_param.reset = 1;
      }
      instance({
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
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
        this.options = response.data.audio;
        if(this.options.length!=0) {
          // console.log(this.options[0]['children'])
          this.valueCascader = this.options[0]['children'][0]['value'];
          // let as = document.getElementById('audioSource');
          // as.src = this.valueCascader;
          let liveaudio = document.getElementById('liveaudio');

          let item = document.createElement("source");
          item.src = this.valueCascader;
          item.type="audio/mpeg";
          liveaudio.appendChild(item);
          // liveaudio.play();
        }
      });
      this.search_param.password = "";
      this.search_param.mail = "";
      this.search_param.url = "";
      this.search_param.currentpage = this.nowpage;
      this.search_param.pagesize = this.nowpagesize;
      Cookies.remove("videoReset");
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
      url = front + "?currentpage=" + this.nowpage + "&pagesize=" + this.nowpagesize;
      location.replace(url);
      // location.reload();
      this.search_param.reset = 1;
      // this.$router.push({ path: '/csdn/'+gu.urlmail,  query:{"currentpage": this.nowpage, "pagesize": this.nowpagesize}})
      await this.axiosget();
    },
    handleSearch() {
      this.search_param.reset = 1;
      const instance = axios.create({
        baseURL: 'http://localhost:7009/video/index',
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
      this.search_param.password = "";
      this.search_param.mail = "";
      this.search_param.url = "";
      let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
      Cookies.remove("videosearch");
      Cookies.set("videosearch", this.search_param.search, { expires: expiresdate });
    },
    async resetSearch() {
      this.search_param.reset = 1;
      // this.search_param.currentpage = 1;
      // this.search_param.pagesize = 20;
      this.nowpage = 1;
      this.search_param.currentpage = this.nowpage;
      this.search_param.pagesize = this.nowpagesize;
      this.search_param.search = "";

      // let gu;
      // await getusername(document.URL).then((response) => {
      //   gu = response;
      // });
      Cookies.remove("videosearch");
      Cookies.remove("videoReset");
      let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
      Cookies.set("videosearch", "", { expires: expiresdate });
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
    cardClick(event) {
      // this.search(event.target);
      // this.$router.push({ path: '/csdn/markdown_detail', hash: '#csdn/markdown_detail', query: { plan: this.dire_path }});


      // let markdown_path = "";
      // if (event.target.className=="") {
      //   markdown_path = event.target.nextSibling.outerText;
      // } else {
      //   markdown_path = event.target.childNodes[1].childNodes[1].outerText;
      // }
      // alert(markdown_path);
      // console.log(event);
      // console.log();
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

video {
  overflow:auto;
  width:100%;
  height:72vh;
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
.el-table .warning-row {
  --el-table-tr-bg-color: var(--el-color-warning-light-9);
}
.el-table .success-row {
  --el-table-tr-bg-color: var(--el-color-success-light-9);
}
</style>
