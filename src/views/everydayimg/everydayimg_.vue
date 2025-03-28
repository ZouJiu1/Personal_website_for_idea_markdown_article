<template>
  <div id='everyday'>
    <!-- <span class="spandesk" id='spandesk'>
      </span>
    <br> -->
    <!-- <el-image 
      style="width:100%;height:100%"
      src="/article/everydayimg.png"
      :zoom-rate="1.0"
      :max-scale="10"
      :min-scale="0.1"
      :preview-src-list="imgsrc"
      fit="cover"
    >
      <template #placeholder>
        <div class="image-slot">Loading<span class="dot">...</span></div>
      </template>
    </el-image> -->
    <a href="https://dailybing.com" style='margin-top: 30px;color:#ffffff; font-size: 60px; color:blue;' target="_blank">Source From: Microsoft bing web search engine https://dailybing.com</a>
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessage } from 'element-plus'
// import { Delete, Edit, Search, Share, Upload, Setting } from '@element-plus/icons-vue'
import Cookies from 'js-cookie'
// import { ref } from 'vue'
import getusername from '/src/common.js'
export default {
  name: 'app',
  data() {
    return {
      imgsrc:["/article/everydayimg.png"],
      description: "",
    }
  },
  watch: {},
  mounted() {
    this.getdata();
  },
  methods: {
    async sleep(delay) { 
      return new Promise((resolve) => setTimeout(resolve, delay)); 
    },
    async getdata() {
      const instance = axios.create({
        baseURL: 'https://zoujiu.com.cn/commonuse/getbingimg',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      let wait_think_render = 100;
      await instance({
        method: 'GET',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        params: {}
      }).then(async (response) => {
        let rt = document.getElementById("spandesk");
        while(rt==null) {
          // console.log(rt, response.data.result)
          rt = document.getElementById("spandesk");
          await this.sleep(wait_think_render);
        }
        // console.log(rt, response.data.result)
        this.description = response.data.result;
        rt.innerHTML = this.description;
        // console.log(rt, response.data.result)
      });
    },
  },
}
</script>

<style scoped>
.spandesk {
  font-size:20px; 
  font-weight: 600; 
  margin-left: 3%;
  color:#ffffff;
  background-color: cadetblue;
  padding-left: 10px;
  padding-right: 10px;
  padding-top: 3px;
  padding-bottom: 3px;
}
.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: var(--el-fill-color-light);
  color: var(--el-text-color-secondary);
  font-size: 20px;
}
</style>
