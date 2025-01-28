<template>
  <div class="app-container">
    <!-- <el-card shadow="always"> -->
      <div style="margin-top: 3px;">
        <el-link type="primary" href="https://www.zhihu.com/people/zoujiu1/" target="_blank">知乎</el-link>
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
      </div>
    <!-- </el-card> -->
    <el-card 
      v-for="o in result"
      :key="o" 
      class="el-card-detail"
      shadow="always"
      @click="cardClick"
      style="overflow:auto;"
    >
      <template #header>
        <div class="card-header" style="overflow:auto; font-size: 20px; color: #00ff00;" @click="cardClick" >
          <span @click="cardClick"> {{ o["title"] }} </span>
          <span hidden><p hidden @click="cardClick" class="hiddenp"> {{ o["path"] }} </p></span>
        </div>
      </template>
      <span style="width:60%; font-size: 16px; color: #000000;" @click="cardClick">
        {{ o["markdown"] }}
      </span>
      <span hidden><p hidden @click="cardClick" class="hiddenp"> {{ o["path"] }} </p></span>
      <template #footer>
        <div class="card-footer" style="overflow:auto; font-size: 16px; color: #0000ee;" @click="cardClick">
          <span @click="cardClick"> {{ o["date"] }} </span>
          <span hidden><p hidden @click="cardClick" class="hiddenp"> {{ o["path"] }} </p></span>
        </div>
      </template>
    </el-card>
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
import getusername from '/src/common.js'
import Cookies from 'js-cookie'
export default {
  name: 'app',
  data() {
    return {
      total: 0,
      result: [],
      dire_path: "",
      
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
    // this.clickpage();
    this.axiosget();
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
        params: {'type' : 'zhihu'},
      }).then((response) => {
      });
    },
    axiosget() {
      const instance = axios.create({
        baseURL: 'http://localhost:7009/zhihu/index',
       timeout: 20000,
      });
      this.search_param.password = Cookies.get("password");
      this.search_param.mail = Cookies.get("mail");
      this.search_param.url = document.URL

      if(Cookies.get("zhihusearch") && Cookies.get("zhihusearch").length) {
        this.search_param.search = Cookies.get("zhihusearch");
      }
      if(Cookies.get("zhihuReset") && Cookies.get("zhihuReset") == 1) {
        this.search_param.reset = 1;
      }
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
      });
      this.search_param.password = "";
      this.search_param.mail = "";
      this.search_param.reset = 0;
      this.search_param.currentpage = this.nowpage;
      this.search_param.pagesize = this.nowpagesize;
      Cookies.remove("zhihuReset");
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
        baseURL: 'http://localhost:7009/zhihu/index',
        timeout: 20000,
      });
      this.search_param.password = Cookies.get("password");
      this.search_param.mail = Cookies.get("mail");
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
      });

      let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
      Cookies.remove("zhihusearch");
      Cookies.set("zhihusearch", this.search_param.search, { expires: expiresdate });
      this.search_param.password = "";
      this.search_param.mail = "";
    },
    async resetSearch() {
      this.search_param.reset = 1;
      this.nowpage = 1;
      this.search_param.currentpage = this.nowpage;
      this.search_param.pagesize = this.nowpagesize;
      this.search_param.search = "";

      // let gu;
      // await getusername(document.URL).then((response) => {
      //   gu = response;
      // });
      Cookies.remove("zhihusearch");
      Cookies.remove("zhihuReset");
      Cookies.set("zhihusearch", "", { expires: expiresdate });
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
      this.$router.push({ path: '/csdn/markdown_detail/*', query: { plan: this.dire_path }});
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

.greetings h1,
.greetings h3 {
  text-align: center;
}

@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>
