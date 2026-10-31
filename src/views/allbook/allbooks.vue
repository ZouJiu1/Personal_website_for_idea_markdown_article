<template>
  <p class="book-topbar">
    <span class="book-topbar-text">
      <span class="page-title" style="font-size:4.4vh; font-weight:390; color:#000000; background-color: #ffffff;">图书以及在线课程</span>
      <span style="font-size:1vh; font-weight:390; color:#000000; background-color: #ffffff; margin-left: 6px;">
        个人信任保证
      </span>
    </span>
  <!-- <div
  v-for="o in allbook"
  :key="o"
  > -->
    <el-button class="book-add-btn" @click="SettingVisible = true">
      添加
    </el-button>
    <el-dialog v-model="SettingVisible" title="添加" width="min(600px, 92%)" height="90%">
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
      <el-form style="max-width: 900px" :model="onebook" status-icon
        label-width="auto" class="demo-ruleForm">
        <el-form-item label="描述" prop="">
          <el-input v-model="onebook.name" autocomplete="off" placeholder="书名" style="margin-bottom:2px;" />
          <el-input v-model="onebook.ratio" autocomplete="off" placeholder="进度" style="margin-bottom:2px;" />
          <el-input 
            v-model="onebook.readdate" 
            autocomplete="off" 
            placeholder="阅读起止时间" 
            style="margin-bottom:2px;"
          />
          <div>
          <el-checkbox 
            v-model="onebook.finished" label="已经看完这本书了" 
            :true-value="1"
            :false-value="0"
            border
            style="text-align:center;margin-left:1px;margin-top:3px;margin-bottom:3px;"
          />
          </div>
          <el-input v-model="onebook.author" autocomplete="off" placeholder="书籍第一个作者" style="margin-bottom:2px;" />
          <el-input v-model="onebook.github" autocomplete="off" placeholder="网址" style="margin-bottom:2px;" />
          <el-upload
            class="upload-demo"
            action="/csdn/mainpageuploadImg"
            multiple
            :on-preview="handleUpPreview"
            :on-remove="handleRemove"
            :before-remove="beforeRemove"
            :limit="30"
            :on-exceed="handleExceed"
            :on-success="handleUpLoadSuccess"
            :data="ImgbookUpload"
            :before-upload="handlebefore_Upload"
          >
            <el-button type="success" style="margin-left:20px; margin-top:2px;" @click="clickimage">上传书籍封面的图片</el-button>
            <template #tip>
              <div class="el-upload__tip">
                jpg/png/jpeg/bmp/gif files with a size less than 13Mb.
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <el-button type="primary" @click="submitAddbook" id="submitAddbook">
        提交
      </el-button>
    </el-dialog>
    <!-- <el-button :icon="Edit" :hidden="REGISTERVisible" style="margin-left:6px; text-align:center;"
      @click="ModifyVisible = true">
      修改
    </el-button> -->
    <el-dialog v-model="modifyvisible" title="修改" width="min(600px, 92%)" height="90%">
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
      <el-form style="max-width: 900px" :model="clickcard" status-icon
        label-width="auto" class="demo-ruleForm">
        <el-form-item label="描述" prop="">
          <el-input v-model="clickcard.name" autocomplete="off" placeholder="书名" style="margin-bottom:2px;" />
          <el-input v-model="clickcard.ratio" autocomplete="off" placeholder="进度" style="margin-bottom:2px;" />
          <el-input 
            v-model="clickcard.readdate" 
            autocomplete="off" 
            placeholder="阅读起止时间" 
            style="margin-bottom:2px;"
          />
          <div>
          <el-checkbox 
            v-model="clickcard.finished" label="已经看完这本书了" 
            :true-value="1"
            :false-value="0"
            border
            style="text-align:center;margin-left:1px;margin-top:3px;margin-bottom:3px;"
          />
          </div>
          <el-input v-model="clickcard.author" autocomplete="off" placeholder="书籍第一个作者" style="margin-bottom:2px;" />
          <el-input v-model="clickcard.github" autocomplete="off" placeholder="网址" style="margin-bottom:2px;" />
          <el-upload
            class="upload-demo"
            action="/csdn/mainpageuploadImg"
            multiple
            :on-preview="handleUpPreview"
            :on-remove="handleRemove"
            :before-remove="beforeRemove"
            :limit="30"
            :on-exceed="handleExceed"
            :on-success="handleUpLoadSuccess"
            :data="ImgbookModifyUpload"
            :before-upload="handleModifybefore_Upload"
          >
            <el-button type="success" style="margin-left:20px; margin-top:2px;" @click="clickimage">传图片</el-button>
            <template #tip>
              <div class="el-upload__tip">
                jpg/png/jpeg/bmp/gif files with a size less than 13Mb.
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <el-button type="primary" @click="submitModifybook" id="submitModifybook">
        提交
      </el-button>
    </el-dialog>
  </p>
  <el-input
    v-model="search_param"
    placeholder="书名或者进度或者网址或者时间，用空格分隔开"
    style="width: 26%; margin-left: 6px;"
    class="filter-item search-input"
    @keyup.enter="handleSearch"
  />
  <el-button
    class="filter-item"
    type="primary"
    @click="handleSearch"
    style="margin-left:2px;text-align:center;"
  >
    搜索
  </el-button>
  <el-button
    class="filter-item"
    type="primary"
    @click="handleReset"
    style="margin-left:2px;text-align:center;"
  >
  重置
  </el-button>
  <el-checkbox 
    v-model="checkboxval" label="已看完" 
    :true-value="1"
    :false-value="0"
    border
    style="text-align:center;margin-left:13px;margin-right:3px;" @Change="handleCheckbox"
  />
  <el-checkbox 
    v-model="checkpartialval" label="部分" 
    :true-value="1"
    :false-value="0"
    border
    style="text-align:center;margin-left:0px;" @Change="handleCheckbox"
  />
  <el-dialog v-model="deletevisible" title="删除" width="min(600px, 92%)" height="90%">
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
  <div v-if="allbook.length==0" class="book-empty">
    书架空空如也，点击上方【添加】录入图书
  </div>
  <el-card v-for="o in allbook" :key="'bk' + (o.n !== undefined ? o.n : o.name)" class="el-card-detail book-card"
          shadow="hover">
    <div class="book-main">
      <div class="book-title-row">
        <el-link type="primary" :href="o.website" class="book-title-link" target="_blank" :underline="false">
          <span class="book-title">{{ o["name"] }}</span>
        </el-link>
        <span v-if="o.finished" class="book-badge-finished">已看完</span>
      </div>
      <span v-if="o.markdown" class="book-desc">{{ o["markdown"] }}</span>
      <el-link v-if="o.github" type="primary" :href="o.github" class="book-github" target="_blank" :underline="false">
        {{ o["github"] }}
      </el-link>
      <div class="book-meta-row">
        <span v-if="o.ratio" class="book-ratio">{{ o["ratio"] }}</span>
        <template v-if="o.author">
          <span class="book-author-label">作者:</span>
          <span class="book-author">{{ o["author"] }}</span>
        </template>
        <span class="book-number">{{ o["number"] }}</span>
        <span @click="cardClick(o)" class="book-op book-op-edit">修改</span>
        <span @click="delcardClick(o)" class="book-op book-op-del">删除</span>
      </div>
    </div>
    <el-image class="book-cover" :src="o.img" lazy :zoom-rate="1.0" :max-scale="10" :min-scale="0.1"
      :preview-src-list="o.imglist" :initial-index="4" fit="cover">
      <template #placeholder>
        <div class="image-slot">Loading<span class="dot">...</span></div>
      </template>
    </el-image>
  </el-card>
  <!-- </div> -->
  <el-pagination
    layout="total, sizes, prev, pager, next, jumper"
    class="book-pagination"
    :page-sizes="[20, 50, 100]"
    background
    v-model:page-size="pagesize"
    v-model:current-page="currentpage"
    :total="total"
    @size-change="handleSizeChange"
    @update:current-page="handlePageChange"
    style="margin-left:20%; margin-top:20px; margin-bottom: 20px;"
  />
  <br>
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
import Cookies from 'js-cookie'
import { ElMessage } from 'element-plus'
// import getusername from '/src/common.js'
export default {
  name: 'app',
  data() {
    return {
      SettingVisible: false,
      clickcard: "",
      modifyvisible: false,
      deletevisible: false,
      onebook: {
        'name':"",
        'ratio':"",
        'readdate':"",
        'github':"",
        'author':"",
        "finished":1,
      },
      allbook: [
                {
                  "github": "",
                  "img": "/article/imgbook/all/SQL_Server从入门到精通（第5版）.jpg",
                  "name": "SQL Server从入门到精通",
                  "ratio": "大学期间全部看完了",
                  "finished": true,
                  "author": "明日科技",
                  "n": -1,
                  "readdate": "2016年暑假"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/数据挖掘导论.jpg",
                  "name": "数据挖掘导论",
                  "ratio": "大学期间全部看完了",
                  "finished": true,
                  "author": "[美]谭、斯坦巴克、库马尔",
                  "n": -2,
                  "readdate": "2017年暑假"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/推荐系统实践.jpg",
                  "name": "推荐系统实践",
                  "ratio": "大学期间全部看完了",
                  "finished": true,
                  "author": "项亮",
                  "n": -3,
                  "readdate": "2017年下半年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/TCP-IP详解卷1协议.jpg",
                  "name": "TCP/IP详解 卷1：协议",
                  "ratio": "大学课程学完了",
                  "finished": true,
                  "author": "凯文 R.福尔",
                  "n": -4,
                  "readdate": "2016年下半年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/Python密码学编程.jpg",
                  "name": "Python密码学编程",
                  "ratio": "大学课程学完了",
                  "finished": true,
                  "author": "(美)AlSweigart(斯维加特)",
                  "n": -5,
                  "readdate": "2017年上半年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/数据结构WHM.jpg",
                  "name": "数据结构",
                  "ratio": "大学课程学完了",
                  "finished": true,
                  "author": "王红梅",
                  "n": -6,
                  "readdate": "2017年上半年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/animal.jpg",
                  "name": "web安全和攻防",
                  "ratio": "大学课程学完了",
                  "finished": true,
                  "author": "",
                  "n": -7,
                  "readdate": "2017年上半年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/animal.jpg",
                  "name": "密码学算法",
                  "ratio": "大学课程学完了",
                  "finished": true,
                  "author": "",
                  "n": -8,
                  "readdate": "2017年下半年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/animal.jpg",
                  "name": "C语言上机",
                  "ratio": "大学上机课程学完了",
                  "finished": true,
                  "author": "",
                  "n": -9,
                  "readdate": "2016年下半年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/animal.jpg",
                  "name": "matlab上机",
                  "ratio": "大学上机课程学完了",
                  "finished": true,
                  "author": "",
                  "n": -10,
                  "readdate": "2017年上半年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/animal.jpg",
                  "name": "Linux上机",
                  "ratio": "大学上机课程学完了",
                  "finished": true,
                  "author": "",
                  "n": -11,
                  "readdate": "2016年下半年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/21天学通C语言.jpg",
                  "name": "21天学通C语言",
                  "ratio": "大学期间全部看完了",
                  "finished": true,
                  "author": "[美]布Bradley Jones Peter Aitken Dean Miller ",
                  "n": -12,
                  "readdate": "2016年暑假"
                },
                {
                  "github": "https://github.com/exacity/deeplearningbook-chinese",
                  "img": "/article/imgbook/all/深度学习.jpg",
                  "name": "深度学习（花书）",
                  "ratio": "200页-613页",
                  "finished": false,
                  "author": "[美]Ian Goodfellow（伊恩·古德费洛）",
                  "n": -13,
                  "readdate": "2017年暑假"
                },
                {
                  "github": "https://linux.vbird.org/",
                  "img": "/article/imgbook/all/鸟哥的Linux私房菜_基础学习篇_第四版.jpg",
                  "name": "鸟哥的Linux私房菜 基础学习篇",
                  "ratio": "工作需要哪就看哪，约60%",
                  "finished": false,
                  "author": "（台湾）鸟哥",
                  "n": -14,
                  "readdate": ""
                },
                {
                  "github": "https://linux.vbird.org/",
                  "img": "/article/imgbook/all/鸟哥的Linux私房菜：服务器架设篇.jpg",
                  "name": "鸟哥的Linux私房菜：服务器架设篇",
                  "ratio": "工作需要哪就看哪，约20%",
                  "finished": false,
                  "author": "（台湾）鸟哥",
                  "n": -15,
                  "readdate": ""
                },
                {
                  "github": "https://github.com/ZouJiu1/Internet-worm-chunistudy",
                  "img": "/article/imgbook/all/Python网络爬虫与信息提取.jpg",
                  "name": "Python网络爬虫与信息提取",
                  "ratio": "中国大学MOOC的课程视频全部看完了",
                  "finished": true,
                  "author": "北京理工大学",
                  "n": -16,
                  "readdate": ""
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/Python数据分析与展示.jpg",
                  "name": "Python数据分析与展示",
                  "ratio": "中国大学MOOC的课程视频全部看完了",
                  "finished": true,
                  "author": "北京理工大学",
                  "n": -17,
                  "readdate": ""
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/计算机组成原理（上）.jpg",
                  "name": "计算机组成原理（上）",
                  "ratio": "中国大学MOOC的课程视频全部看完了",
                  "finished": true,
                  "author": "哈尔滨工业大学",
                  "n": -18,
                  "readdate": "2023年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/计算机组成原理（下）.jpg",
                  "name": "计算机组成原理（下）",
                  "ratio": "中国大学MOOC的课程视频正在看",
                  "finished": false,
                  "author": "哈尔滨工业大学",
                  "n": -19,
                  "readdate": "2023年到..."
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/C++语言程序设计基础.jpg",
                  "name": "C++语言程序设计基础",
                  "ratio": "学堂在线的课程视频全部看完了",
                  "finished": true,
                  "author": "清华大学",
                  "n": -20,
                  "readdate": "2019-2020年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/C++语言程序设计进阶.jpg",
                  "name": "C++语言程序设计进阶",
                  "ratio": "学堂在线的课程视频全部看完了",
                  "finished": true,
                  "author": "清华大学",
                  "n": -21,
                  "readdate": "2019-2020年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/数据结构four.jpg",
                  "name": "数据结构",
                  "ratio": "130页-*页",
                  "finished": false,
                  "author": "严蔚敏",
                  "n": -22,
                  "readdate": "2017年上半年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/计算机组成原理four.jpg",
                  "name": "计算机组成原理",
                  "ratio": "100页-*页",
                  "finished": false,
                  "author": "唐朔飞",
                  "n": -23,
                  "readdate": "2023年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/计算机操作系统four.jpg",
                  "name": "计算机操作系统",
                  "ratio": "200页-*页",
                  "finished": false,
                  "author": "汤小丹",
                  "n": -24,
                  "readdate": "2023年到..."
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/计算机网络four.jpg",
                  "name": "计算机网络",
                  "ratio": "20页-*页",
                  "finished": false,
                  "author": "谢希仁",
                  "n": -25,
                  "readdate": "2017年上半年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/CUDA_C编程权威指南.jpg",
                  "name": "CUDA C编程权威指南",
                  "ratio": "150页-779页",
                  "finished": false,
                  "author": "[美]程润伟（John Cheng）",
                  "n": -26,
                  "readdate": "2023年到..."
                },
                {
                  "github": "https://github.com/ZouJiu1/CUDA-Programming",
                  "img": "/article/imgbook/all/CUDA_编程：基础与实践.jpg",
                  "name": "CUDA 编程：基础与实践",
                  "ratio": "全部看完了的",
                  "finished": true,
                  "author": "樊哲勇-清华",
                  "n": -27,
                  "readdate": "2023年下半年"
                },
                {
                  "github": "https://github.com/ZouJiu1/Hands-on-RL",
                  "img": "/article/imgbook/all/动手学强化学习.jpg",
                  "name": "动手学强化学习",
                  "ratio": "全部看完了的",
                  "finished": true,
                  "author": "张伟楠-上交",
                  "n": -28,
                  "readdate": "2023年下半年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/自然语言处理导论.jpg",
                  "name": "自然语言处理导论",
                  "ratio": "188页-603页",
                  "finished": false,
                  "author": "张奇-复旦",
                  "n": -29,
                  "readdate": "2024年到..."
                },
                {
                  "github": "https://github.com/ZouJiu1/Opencv_C_algorithm",
                  "img": "/article/imgbook/all/OpenCV算法精解：基于Python与C++.jpg",
                  "name": "OpenCV算法精解：基于Python与C++",
                  "ratio": "150页-420页",
                  "finished": false,
                  "author": "张平",
                  "n": -30,
                  "readdate": "2023年到..."
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/C++_Primer_Plus_(第6版)_中文版.jpg",
                  "name": "C++ Primer Plus (第6版)_中文版",
                  "ratio": "全部看完了的",
                  "finished": true,
                  "author": "[美] 史蒂芬·普拉达",
                  "n": -31,
                  "readdate": "2023年下半年"
                },
                {
                  "github": "https://github.com/ZouJiu1/multithread_Cplusplus",
                  "img": "/article/imgbook/all/C++_Concurrency_in_Action,_2nd_Edition.jpg",
                  "name": "C++ Concurrency in Action, 2nd Edition C++ 并发编程实战 第二版",
                  "ratio": "116页-360页",
                  "finished": false,
                  "author": "[英]安东尼",
                  "n": -32,
                  "readdate": "2023年下半年到..."
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/Java核心技术卷1基础知识_原书第11版.jpg",
                  "name": "Java核心技术卷1基础知识 原书第11版",
                  "ratio": "全部看完了的",
                  "finished": true,
                  "author": "[美] 凯·S.霍斯特曼",
                  "n": -33,
                  "readdate": "2024年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/Java核心技术·卷_II（原书第11版）_高级特性.jpg",
                  "name": "Java核心技术·卷 II（原书第11版） 高级特性",
                  "ratio": "160页-670页",
                  "finished": false,
                  "author": "[美] 凯·S.霍斯特曼",
                  "n": -34,
                  "readdate": "2024年到..."
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/JavaScript高级程序设计（第4版）.jpg",
                  "name": "JavaScript高级程序设计（第4版）",
                  "ratio": "全部看完了的",
                  "finished": true,
                  "author": "[美]马特·弗里斯比（Matt Frisbie）",
                  "n": -35,
                  "readdate": "2024年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/深入理解LINUX内核（第三版）.jpg",
                  "name": "深入理解LINUX内核",
                  "ratio": "160页-855页",
                  "finished": false,
                  "author": "[美]博韦，西斯特",
                  "n": -36,
                  "readdate": "2024年到..."
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/UNIX网络编程_卷1_套接字联网API_第3版.jpg",
                  "name": "UNIX网络编程 卷1 套接字联网API",
                  "ratio": "20页-820页",
                  "finished": false,
                  "author": "[美]W. 理查德",
                  "n": -37,
                  "readdate": "2024年到..."
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/计算机组成与设计-软件硬件接口.jpg",
                  "name": "计算机组成与设计-软件硬件接口",
                  "ratio": "146页-495页",
                  "finished": false,
                  "author": "[美]戴维·A. 帕特森",
                  "n": -38,
                  "readdate": "2024年到..."
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/量子物理学的世界.jpg",
                  "name": "量子物理学的世界（全彩）",
                  "ratio": "全部看完了的",
                  "finished": true,
                  "author": "（英）BrianClegg（布莱恩·克莱格）",
                  "n": -39,
                  "readdate": "2022年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/我们为什么要睡觉.jpg",
                  "name": "我们为什么要睡觉",
                  "ratio": "看完一半了的",
                  "finished": false,
                  "author": "[英]马修·沃克 后浪",
                  "n": -40,
                  "readdate": "2022年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/神秘的量子生命.jpg",
                  "name": "神秘的量子生命",
                  "ratio": "全部看完了的",
                  "finished": true,
                  "author": "（英）吉姆·艾尔－哈利利 约翰乔·麦克法登 ",
                  "n": -41,
                  "readdate": "2022年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/量子和粒子物理学何以解释一切.jpg",
                  "name": "量子和粒子物理学何以解释一切",
                  "ratio": "全部看完了的",
                  "finished": true,
                  "author": "(英)蒂姆·詹姆斯",
                  "n": -42,
                  "readdate": "2022年"
                },
                {
                  "github": "",
                  "img": "/article/imgbook/all/量子通史：量子物理史上的40个重大时刻.jpg",
                  "name": "量子通史：量子物理史上的40个重大时刻",
                  "ratio": "看完27%了",
                  "finished": false,
                  "author": "（英）吉姆·巴戈特",
                  "n": -43,
                  "readdate": "2022年"
                }
              ],
      targetn:"",
      postkey:"",
      search_param:"",
      checkboxval:1,
      checkpartialval:1,
      currentpage:1,
      pagesize:20,
      total:0,
    }
  },
  mounted() {
    // this.axiosget();
    // this.clickpage();
    this.getdata();
  },
  watch: {},
  methods: {
    handleReset() {
      this.search_param = "";
      this.checkboxval = 1;
      this.checkpartialval = 1;
      this.handleSearch();
    },
    getcheck() {
      let check = 2;
      if((this.checkboxval==1 && this.checkpartialval==1)||
        (this.checkboxval + this.checkpartialval==0)) {
        this.checkboxval = 1;
        this.checkpartialval = 1;
        check = 2;
      } else if(this.checkboxval==0 && this.checkpartialval==1) {
        check = 0;
      } else if(this.checkboxval==1 && this.checkpartialval==0) {
        check = 1;
      }
      return check;
    },
    // 统一加载入口：搜索/筛选/翻页/增删改后的刷新都走这里。
    // 书架扩容到 30000 本后前端必须分页拉取，后端带 currentpage/pagesize 只返回当前页
    async loadBooks(errmsg) {
      // 请求进行中直接忽略重复触发（防连点/翻页连击导致的请求风暴）
      if(this._loadBusy) {
        return;
      }
      this._loadBusy = true;
      const instance = axios.create({
        baseURL: '/csdn/mainpagedataget',
        timeout: 20000,
      });
      let mail = "";
      mail = Cookies.get("mail");
      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {'url' : document.URL, "mail":mail, "password":".", 'imgbook':true,
               'search':this.search_param, 'checkboxval':this.getcheck(),
               'currentpage':this.currentpage, 'pagesize':this.pagesize},
      }).then((response) => {
        let rd = (response.data && typeof response.data === 'object') ? response.data : {};
        // jfile 结构守卫，接口异常/返回非数组时不再抛 TypeError
        let jf = Array.isArray(rd.jfile) ? rd.jfile : [];
        this.total = Number(rd.length) || 0;
        // 后端页码钳制回填（当前页被删空/超界时自动回落到有效页），不触发二次请求
        let pg = Number(rd.page);
        if(pg >= 1 && pg !== this.currentpage) {
          this.currentpage = pg;
        }
        if(jf.length!=0) {
          this.allbook = jf;
        } else if(this.search_param.length>0) {
          this.allbook = [{'name':'Not Found'}];
          this.total = 0;
        } else {
          // 空书架清空列表，避免残留上一页旧数据
          this.allbook = [];
        }
        this.postkey = ""
      }).catch(() => {
        ElMessage.error(errmsg || "网络错误，加载书架失败！");
      }).finally(() => {
        this._loadBusy = false;
      });
    },
    async handleSearch() {
      // 搜索/重置总是回到第一页，避免旧页码超出新结果范围
      this.currentpage = 1;
      await this.loadBooks("网络错误，搜索失败！");
    },
    async handleCheckbox() {
      // 筛选条件变化后结果集变化，回第一页
      this.currentpage = 1;
      await this.loadBooks("网络错误，筛选失败！");
    },
    async getdata() {
      await this.loadBooks("网络错误，加载书架失败！");
    },
    async handlePageChange() {
      await this.loadBooks("网络错误，加载书架失败！");
    },
    async handleSizeChange() {
      // 每页条数变化后页码含义改变，回第一页
      this.currentpage = 1;
      await this.loadBooks("网络错误，加载书架失败！");
    },
    async submitAddbook() {
      let ok = true;
      if(this.targetn.length==0) {
        ElMessage.error('没有上传书本封面!');
        ok = false;
      }
      if(this.onebook.name.length < 2) {
        ElMessage.error('没有填写书名!');
        ok = false;
      }
      if(this.onebook.ratio.length < 2) {
        ElMessage.error('没有写阅读进度!');
        ok = false;
      }
      if(this.onebook.readdate.length < 2) {
        ElMessage.error('没有写阅读时间!');
        ok = false;
      }
      if(this.onebook.author.length < 2) {
        ElMessage.error('没有填写书籍作者!');
        ok = false;
      }
      if(this.onebook.finished == 1) {
        ElMessage.info('这本书籍已经看完了!');
      } else {
        ElMessage.info('这本书籍看了部分!');
      }
      if(!ok) {
        return false;
      }
      if(this._submitBusy) {
        return;
      }
      this._submitBusy = true;
      const instance = axios.create({
        baseURL: '/csdn/FormsubmitSetting',
        timeout: 20000,
      });

      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {'url' : document.URL, "mail":Cookies.get("mail"), "postkey":this.postkey,
              "password":Cookies.get("password"), 'addbook':this.onebook, 'SettingForm':"."},
      }).then((response) => {
        if(response.data.ret < 0) {
          // 业务失败（未登录/-107 书架已满等）时优先展示后端 msg
          ElMessage.error(response.data && response.data.msg ? String(response.data.msg) : '没有登陆不能修改!');
          return false;
        }
        // 新书追加在书架末尾：跳到估算的最后一页再刷新（页码越界由后端钳制兜底）
        this.currentpage = Math.floor(this.total / this.pagesize) + 1;
        this.getdata();
        this.postkey = "";
        this.SettingVisible = false;
        this.targetn = "";
        this.onebook.name = "";
        this.onebook.ratio = "";
        this.onebook.readdate = "";
        this.onebook.github = "";
        this.onebook.author = "";
        this.onebook.finished = 1;
        ElMessage.success('添加成功');
      }).catch(() => {
        ElMessage.error("网络错误，添加失败！");
      }).finally(() => {
        this._submitBusy = false;
      });
    },
    async submitModifybook() {
      let ok = true;
      if(this.clickcard.name.length < 2) {
        ElMessage.error('没有填写书名!');
        ok = false;
      }
      if(this.clickcard.ratio.length < 2) {
        ElMessage.error('没有写阅读进度!');
        ok = false;
      }
      if(this.clickcard.readdate.length < 2) {
        ElMessage.error('没有写阅读时间!');
        ok = false;
      }
      if(this.clickcard.author.length < 2) {
        ElMessage.error('没有填写书籍作者!');
        ok = false;
      }
      if(this.clickcard.finished == 1) {
        ElMessage.info('这本书籍已经看完了!');
      } else {
        ElMessage.info('这本书籍看了部分!');
      }
      if(!ok) {
        return false;
      }
      if(this._submitBusy) {
        return;
      }
      this._submitBusy = true;
      // if(this.targetn.length==0) {
      //   ElMessage.warning('没有上传书本封面!');
      //   return false;
      // }
      const instance = axios.create({
        baseURL: '/csdn/FormsubmitSetting',
        timeout: 20000,
      });

      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {'url' : document.URL, "mail":Cookies.get("mail"), "postkey":this.postkey,
              "password":Cookies.get("password"), 'SettingForm':".",
              'clickcard':'.', 'github':this.clickcard.github, 'name':this.clickcard.name,
              'n':this.clickcard.n, 'readdate':this.clickcard.readdate,
              'ratio':this.clickcard.ratio, 'finished':this.clickcard.finished,
              'author':this.clickcard.author},
      }).then((response) => {
        if(response.data.ret < 0) {
          // 业务失败（未登录/超限等）时优先展示后端 msg
          ElMessage.error(response.data && response.data.msg ? String(response.data.msg) : '没有登陆不能修改!');
          return false;
        }
        this.getdata();
        this.postkey = "";
        this.modifyvisible = false;
        this.targetn = "";
        this.clickcard.finished = 1;
        this.clickcard.author = "";
        ElMessage.success('修改成功');
      }).catch(() => {
        ElMessage.error("网络错误，修改失败！");
      }).finally(() => {
        this._submitBusy = false;
      });
    },
    clickimage(event) {
      // this.targetn = event.target.innerText;
      // this.targetn = this.targetn.substring(3);
      // console.log(99, event, this.targetn);
      // this.targetn = "--------";
    },
    ImgbookUpload() {
      return {"mail":Cookies.get("mail"), 
        "password":Cookies.get("password"), 'postkey':this.postkey,
        "url":document.URL,'ImgbookUpload':true};
    },
    ImgbookModifyUpload() {
      return {"mail":Cookies.get("mail"),
        "password":Cookies.get("password"), 'postkey':this.postkey,
        "url":document.URL,'ImgbookUpload':true, 'clickcard':".", 'n':this.clickcard.n};
    },
    async clickpage() {
      const instance = axios.create({
        baseURL: '/csdn/clickpage',
        timeout: 20000,
      });

      // console.log(this.search_param);
      await instance({
        method: 'GET',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        params: { 'type': 'book' },
      }).then((response) => {
      }).catch(() => {
      });
    },
    handleRemove(file, uploadFiles) {
      // console.log(file, uploadFiles)
    },

    handleUpPreview(uploadFile) {
      console.log(uploadFile)
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
      // console.log(11, rawFile);
      let ok = true;
      if(this.onebook.name.length < 2) {
        ElMessage.error('没有填写书名!');
        ok = false;
      }
      if(this.onebook.ratio.length < 2) {
        ElMessage.error('没有写阅读进度!');
        ok = false;
      }
      if(this.onebook.readdate.length < 2) {
        ElMessage.error('没有写阅读时间!');
        ok = false;
      }
      if(this.onebook.author.length < 2) {
        ElMessage.error('没有填写书籍作者!');
        ok = false;
      }
      if(this.onebook.finished == 1) {
        ElMessage.info('这本书籍已经看完了!');
      } else {
        ElMessage.info('这本书籍看了部分!');
      }
      if(!ok) {
        return false;
      }
      if (rawFile.type !== 'image/jpeg' && rawFile.type !== "image/png"
            && rawFile.type !== "image/gif" && rawFile.type !== "image/bmp"
            && rawFile.type !== "image/jpg") {
        ElMessage.warning('不是图片格式!');
        return false;
      } else if (rawFile.size / 1024 / 1024 > 13) {
        ElMessage.warning('图片占用磁盘大小不能 > 13MB!');
        return false;
      }
      return true;
    },
    handleModifybefore_Upload(rawFile) {
      // console.log(11, rawFile);
      let ok = true;
      if(this.clickcard.name.length < 2) {
        ElMessage.error('没有填写书名!');
        ok = false;
      }
      if(this.clickcard.ratio.length < 2) {
        ElMessage.error('没有写阅读进度!');
        ok = false;
      }
      if(this.clickcard.readdate.length < 2) {
        ElMessage.error('没有写阅读时间!');
        ok = false;
      }
      if(this.clickcard.author.length < 2) {
        ElMessage.error('没有填写书籍作者!');
        ok = false;
      }
      if(this.clickcard.finished == 1) {
        ElMessage.info('这本书籍已经看完了!');
      } else {
        ElMessage.info('这本书籍看了部分!');
      }
      if(!ok) {
        return false;
      }
      if (rawFile.type !== 'image/jpeg' && rawFile.type !== "image/png"
            && rawFile.type !== "image/gif" && rawFile.type !== "image/bmp"
            && rawFile.type !== "image/jpg") {
        ElMessage.warning('不是图片格式!');
        return false;
      } else if (rawFile.size / 1024 / 1024 > 13) {
        ElMessage.warning('图片占用磁盘大小不能 > 13MB!');
        return false;
      }
      return true;
    },
    cardClick(event) {
      // console.log(event, k);
      // 伪卡片（如搜索无结果的 {'name':'Not Found'}）无 n，先拦截再处理 ratio，避免 TypeError
      if(!event || event.n === undefined || event.n === null || Number(event.n) < 0) {
        ElMessage.warning('还没有属于您自己看过的图书，需要先【添加】才行!');
        return false;
      }
      let rt = event.ratio ? String(event.ratio) : ""
      let id = rt.indexOf(",");
      if(id > 0) {
        event.ratio = rt.substring(id + 2);
      }
      this.clickcard = event;
      this.modifyvisible = true;
    },
    delcardClick(event) {
      // console.log(event);
      // 伪卡片（如搜索无结果的 {'name':'Not Found'}）无 n，先拦截再处理 ratio，避免 TypeError
      if(!event || event.n === undefined || event.n === null || Number(event.n) < 0) {
        ElMessage.warning('还没有属于您自己看过的图书，需要先【添加】才行!');
        return false;
      }
      let rt = event.ratio ? String(event.ratio) : ""
      let id = rt.indexOf(",");
      if(id > 0) {
        event.ratio = rt.substring(id + 2);
      }
      this.clickcard = event;
      this.deletevisible = true;
    },
    async carddelete() {
      if(!this.clickcard || this.clickcard.n === undefined || this.clickcard.n === null || Number(this.clickcard.n) < 0) {
        ElMessage.warning('还没有属于您自己看过的图书，需要先【添加】才行!');
        return false;
      }
      if(this._submitBusy) {
        return;
      }
      this._submitBusy = true;
      let rt = this.clickcard.ratio
      let id = rt ? String(rt).indexOf(",") : -1;
      if(id > 0) {
        this.clickcard.ratio = String(rt).substring(id + 2);
      }
      const instance = axios.create({
        baseURL: '/csdn/FormsubmitSetting',
        timeout: 20000,
      });

      // console.log(this.search_param);
      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {'url' : document.URL, "mail":Cookies.get("mail"), "postkey":this.postkey,
              "password":Cookies.get("password"), 'n':this.clickcard.n, 'delete':true },
      }).then((response) => {
        if(response.data.ret < 0) {
          // 业务失败（未登录/超限等）时优先展示后端 msg
          ElMessage.error(response.data && response.data.msg ? String(response.data.msg) : '没有登陆不能修改!');
          this.deletevisible = false;
          return false;
        }
        // 删除成功仅刷新列表数据，不再整页 reload（避免 SPA 状态被整页刷新打断）
        this.getdata();
        this.postkey = "";
        this.deletevisible = false;
        this.clickcard = "";
        ElMessage.success('删除成功');
      }).catch(() => {
        ElMessage.error("网络错误，删除失败！");
      }).finally(() => {
        this._submitBusy = false;
      });
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
        ElMessage.error('没有登陆自动取消上传!!');
        return false;
      } else {
        this.targetn = "------";
      }
      // this.onebook.name = "";
      // this.onebook.ratio = "";
      // this.onebook.readdate = "";
      // this.onebook.github = "";
      // this.onebook.finished = 1;
      // this.onebook.author = "";
    },
  }
}
</script>

<style scoped>
.el-card__body {
  width:auto;
}

.el-card-detail {
  width: 80%;
  color: #303133;
  margin-top: 3px;
  margin-left: 10%;
  margin-right: 10%;
}

/* 卡片悬浮：轻提升 + 阴影加深（克制，不做整卡变色） */
.el-card-detail:hover {
  color: #303133 !important;
  background: #ffffff !important;
  box-shadow: 0 6px 18px rgba(0, 0, 0, .10);
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
.book-empty {
  width: 93%;
  margin-left: 7vh;
  padding: 6vh 0;
  text-align: center;
  color: #909399;
  font-size: 16px;
  background: #fafafa;
  border-radius: 8px;
}
.book-pagination {
  justify-content: center;
  flex-wrap: wrap;
}

/* ===== 顶部标题行：flex 布局，标题居中、添加按钮固定在行尾右侧，
   不再被 39% 边距的大标题挤到第二行 ===== */
.book-topbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 20px 0;
  margin: 0;
}
.book-topbar-text {
  flex: 1;
  text-align: center;
}
@media (max-width: 768px) {
  .book-topbar {
    flex-wrap: wrap;
    padding: 4px 10px 0;
  }
  .book-topbar-text {
    flex: 1 1 100%;
  }
  /* 窄屏时标题独占一行、按钮换行靠右 */
  .book-add-btn {
    margin-left: auto;
  }
}

/* ===== 书卡内部布局：左主区（标题/简介/链接/元信息）+ 右封面两栏结构，
   内容全部约束在卡片内，不再散排漂到右侧导致贴边被截 ===== */
.book-card {
  border-radius: 12px;
  transition: box-shadow .25s ease, transform .25s ease;
}
.book-card:hover {
  transform: translateY(-2px);
}
.book-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
}
/* 左主区：纵向堆叠，min-width:0 保证内部截断生效、不把封面挤出卡片 */
.book-main {
  flex: 1 1 0;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
/* 书名行：书名 + 已看完徽标同行，书名超长截断 */
.book-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.book-title-link {
  flex: 0 1 auto;
  min-width: 0;
}
.book-title {
  color: #303133;
  font-size: 19px;
  font-weight: 600;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-all;
}
.book-title-link:hover .book-title {
  color: var(--el-color-primary);
}
/* 简介两行截断，浅灰次要色 */
.book-desc {
  min-width: 0;
  font-size: 14px;
  color: #909399;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-all;
}
/* 封面固定尺寸 + 圆角，hover 轻缩放 */
.book-cover {
  width: 110px;
  height: 130px;
  border-radius: 8px;
  flex-shrink: 0;
  transition: transform .25s ease;
}
.book-cover:hover {
  transform: scale(1.03);
}
.book-ratio {
  font-size: 13px;
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  border-radius: 4px;
  padding: 2px 8px;
}
.book-github {
  align-self: flex-start;
  max-width: 100%;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.book-author-label {
  font-size: 14px;
  color: #606266;
  font-weight: 600;
}
.book-author {
  font-size: 14px;
  color: #c24ed4;
  font-weight: 600;
}
/* 元信息行：进度/作者/序号/操作，允许换行防止溢出 */
.book-meta-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  min-width: 0;
}
.book-number {
  margin-left: auto;
  font-size: 11px;
  color: #c0c4cc;
}
/* 「已看完」徽标：绿色系浅底，替代刺眼的大号洋红 */
.book-badge-finished {
  font-size: 12px;
  font-weight: 600;
  color: var(--el-color-success);
  background: var(--el-color-success-light-9);
  border: 1px solid var(--el-color-success-light-7);
  border-radius: 4px;
  padding: 2px 8px;
}
/* 修改/删除操作：可见的浅色文字，hover 明确反馈 */
.book-op {
  font-size: 12px;
  cursor: pointer;
  border-radius: 4px;
  padding: 2px 8px;
  transition: color .2s ease, background-color .2s ease;
}
.book-op-edit {
  color: #909399;
}
.book-op-edit:hover {
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}
.book-op-del {
  color: #909399;
}
.book-op-del:hover {
  color: var(--el-color-danger);
  background: var(--el-color-danger-light-9);
}
.el-card-detail.is-active {
  color: #303133 !important;
  background: #ffffff !important;
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

/* 手机端适配：标题边距缩小、搜索框与卡片占满可用宽度 */
@media (max-width: 768px) {
  .page-title {
    margin-left: 8px !important;
    font-size: 20px !important;
  }

  .book-add-btn {
    margin-left: 8px !important;
  }

  .search-input {
    width: calc(100% - 16px) !important;
    margin-left: 8px !important;
  }

  .el-card-detail {
    width: 100% !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
  }

  .book-cover {
    width: 30% !important;
    max-width: 100%;
  }

  .book-empty {
    width: 100% !important;
    margin-left: 0 !important;
  }

  .book-pagination {
    margin-left: 8px !important;
    margin-right: 8px !important;
  }

  /* 窄屏书卡：整体上下两栏（主区在上、封面在下居左缩小） */
  .book-card :deep(.el-card__body) {
    flex-direction: column;
    align-items: flex-start;
    padding: 12px 14px;
    gap: 8px;
  }
  .book-cover {
    width: 84px;
    height: 100px;
    align-self: flex-end;
  }
  .book-github {
    max-width: 100%;
  }
  .book-number {
    margin-left: 0;
  }
}
</style>
