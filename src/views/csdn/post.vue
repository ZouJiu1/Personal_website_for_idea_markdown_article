<template>
  <div class="app-container">
    <!-- <el-card shadow="always"> -->
    <div>
      <div style="margin-top:-2px;">
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
        <el-dialog v-model="dialogFormVisible" title="上传图片" width="500">
          <el-upload
            v-model:file-list="fileList"
            class="upload-demo"
            action="http://localhost:7009/csdn/uploadImg"
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
        <!-- <el-button
          class="filter-item"
          type="primary"
          @click="handleSavedraft"
          style="margin-left:36px;text-align:center;"
          >
          保存草稿
        </el-button>
        <el-button
          class="filter-item"
          type="primary"
          @click="handleSavedraft"
          style="margin-left:10px;text-align:center;"
          >
          加载草稿
        </el-button> -->
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
      <div style="margin-top:-10px;margin-bottom: 2px;">
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
  },
  watch: {},
  methods: {
    scrollChange(event) {
      if(this.scrollChangealway) {
        let htmlHeight = event.target.clientHeight;
        let editorHeight = event.target.scrollHeight;
        let editorTop = event.target.scrollTop;
        let remain = editorHeight - htmlHeight;
        let ratio = editorTop / remain;

        let rightele = document.getElementById("previewHalf");
        rightele.scrollTop = (rightele.scrollHeight - htmlHeight) * ratio;
        // console.log(event, remain, editorTop, ratio,  rightele.scrollTop / rightele.scrollHeight);
      }
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
        params: {'type' : 'post'},
      }).then((response) => {
      });
    },
    async getPrimaryText() {
      const instance = axios.create({
        baseURL: 'http://localhost:7009/csdn/getPrimaryText',
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
        baseURL: 'http://localhost:7009/csdn/renzheng',
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
      this.path = this.$router.currentRoute._value.query.plan;
      if(!this.path) {
        return;
      }
      this.data.path = this.path;
      // console.log(this.path);
      const instance = axios.create({
        baseURL: 'http://localhost:7009/csdn/editArticle',
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
    handleSavedraft() {
      // this.save = true;
      // this.axiospost();
      // this.save = false;
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
        baseURL: 'http://localhost:7009/csdn/renzheng',
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
            }, 1000);
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
        baseURL: 'http://localhost:7009/csdn/postArticle',
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
        baseURL: 'http://localhost:7009/csdn/renzheng',
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
            baseURL: 'http://localhost:7009/csdn/postArticle',
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
                  this.$router.push({ path: '/csdn/homepage',});
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
            // this.$router.push({ path: '/csdn/homepage'});
            this.$router.push({ path: '/csdn/homepage',  query:{"currentpage": Cookies.get("csdn"), "pagesize": Cookies.get("csdnpage")}});
          }
        } 
      } else {
        if(gu && gu.ret > 0) {
          // this.$router.push({ path: '/csdn/' + gu.urlmail});
          this.$router.push({ path: '/csdn/' + gu.urlmail,  query:{"currentpage": Cookies.get("csdn"), "pagesize": Cookies.get("csdnpage")}});
        } else {
          // this.$router.push({ path: '/csdn/zj'});
          // this.$router.push({ path: '/csdn/homepage'});
          this.$router.push({ path: '/csdn/homepage',  query:{"currentpage": Cookies.get("csdn"), "pagesize": Cookies.get("csdnpage")}});
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
        `The limit is 3, you selected ${files.length} files this time, add up to ${
          files.length + uploadFiles.length
        } totally`
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

</style>
