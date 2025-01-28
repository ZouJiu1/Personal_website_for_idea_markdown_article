<template>
  <el-card class="el-card-detail" shadow="always" 
    style="margin-top:10px;margin-left:30px;margin-right:30px;margin-bottom:3px;overflow:auto;">
    <template #header>
      <div class="card-header" style="height:16px; font-size: 20px; color: #00ff00;">
        <span > 个人 </span>
        <el-button
          style="margin-left:10px; margin-bottom:10px; text-align:center;"
          @click="FunctiondialogSetting"
          >
          setting
        </el-button>
        <!-- <el-color-picker v-model="colortheme" show-alpha :predefine="predefineColors" /> -->
        <el-dialog v-model="dialogSetting" title="配置" width="60%" height="90%">
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
          <el-form
            v-for="tgf in SettingForm"
            :key="tgf"
            style="max-width: 600px"
            :model="tgf"
            status-icon
            label-width="auto"
            class="demo-ruleForm"
            >
            <el-form-item :label="tgf.n" prop="">
              <el-input
                v-model="tgf.introduction"
                placeholder="姓名、邮箱、Leetcode.若需要删除配置,请输入【/$删除$/】这六个字的"
                style="margin-bottom:2px;"
              />
              <el-input 
                v-model="tgf.link"
                autocomplete="off" 
                placeholder="https://github.com/ZouJiu1，没有的话不需要填写"
                style="margin-bottom:2px;"
              />
              <el-input 
                v-model="tgf.link_describe"
                autocomplete="off" 
                placeholder="邹九的GitHub，github.com/ZouJiu1，没有的话不需要填写"
                style="margin-bottom:2px;"
              />
              <el-input 
                v-model="tgf.other_describe"
                autocomplete="off" 
                placeholder="补充描述的, 展示图片的描述，没有图片的话不需要填写"
              />
              <el-input 
                v-model="tgf.button"
                autocomplete="off" 
                placeholder="按钮的名称"
              />
              <!-- <el-button
                class="filter-item"
                type="primary"
                style="margin-left:20px;margin-bottom:10px;text-align:center;"
                @click="upLoadbutton"
                >
                传图片{{ tgf.n }}
              </el-button>
              <el-dialog v-model="dialogFormVisible" title="传图片" width="500"> -->
                <el-upload
                  class="upload-demo"
                  action="http://localhost:7009/csdn/mainpageuploadImg"
                  multiple
                  :on-preview="handleUpPreview"
                  :on-remove="handleRemove"
                  :before-remove="beforeRemove"
                  :limit="30"
                  :on-exceed="handleExceed"
                  :on-success="handleUpLoadSuccess"
                  :data="dataimg"
                  :before-upload="handlebefore_Upload"
                >
                  <el-button type="success" style="margin-left:20px; margin-top:2px;" @click="clickimage">传图片{{ tgf.n }}</el-button>
                  <template #tip>
                    <div class="el-upload__tip" v-if="tgf.n == 1">
                      jpg/png/jpeg/bmp/gif files with a size less than 13Mb.
                    </div>
                  </template>
                </el-upload>
              <!-- </el-dialog> -->
            </el-form-item>
          </el-form>
          <el-button type="primary" @click="submitSettingForm" id="submitSettingForm">
            提交
          </el-button>
        </el-dialog>
      </div>
    </template>
    <p
      v-for="rt in result"
      :key="rt"
    >
      <span style="font-weight:600;">{{rt["introduction"]}}：</span>
      <el-link type="primary" :href="rt.link" style="margin-left:6px;font-size:16px;" target="_blank" >
        {{rt["link_describe"]}}
      </el-link>
      {{rt["other_describe"]}}
      <el-button
        v-if="rt.showbutton"
        class="filter-item"
        type="primary"
        style="margin-left:20px;text-align:center;margin-bottom:3px;"
        @click="rt.introductionVisible=true"
        >
        {{ rt["button"] }}
      </el-button>
      <el-dialog v-model="rt.introductionVisible">
        <div class="demo-image__lazy">
          <el-image v-for="url in rt.image" :key="url" :src="url" lazy :zoom-rate="1.0" :max-scale="10" :min-scale="0.1">
            <template #placeholder>
              <div class="image-slot">Loading<span class="dot">...</span></div>
            </template>
          </el-image>
        </div>
      </el-dialog>
    </p>
    <!-- <p><span style="font-weight:600;">姓名：</span>邹九</p>
    <p><span style="font-weight:600;">邮箱：</span>1069679911@qq.com</p>
    <p>
      <span style="font-weight:600;">攀拓PAT：</span>
      <el-link type="primary" href="https://github.com/ZouJiu1/PAT" style="margin-left:6px;" target="_blank" >
        github.com/ZouJiu1/PAT
      </el-link>
      ，甲级/乙级基本都刷完了
      <el-button
        class="filter-item"
        type="primary"
        style="margin-left:20px;text-align:center;"
        @click="dialogVisible=true"
        >
        PAT证书
      </el-button>
      <el-dialog v-model="dialogVisible">
        <div>
          <img src="/article/imgbook/PAT证书.jpg" alt="Preview Image" style="width:100%; overflow:auto;"/>
        </div>
      </el-dialog>
    </p>
    <p>
      <span style="font-weight:600;">Leetcode主页：</span>
      <el-link type="primary" href="https://leetcode.cn/u/shiheyingzhe/" style="margin-left:6px;" target="_blank" >
        leetcode.cn/u/shiheyingzhe/
      </el-link>
      ，刷完了406道题目
    </p>
    <p>
      <span style="font-weight:600;">Kaggle主页：</span>
      <el-link type="primary" href="https://www.kaggle.com/shiheyingzhe" style="margin-left:6px;" target="_blank" >
        www.kaggle.com/shiheyingzhe
      </el-link>
    </p> 
    <el-link type="primary" href="" target="_blank"></el-link> -->
    <!-- <template #footer>
      <div class="card-footer" style="height:16px; font-size: 16px; color: #0000ee;">
        <span >  </span>
      </div>
    </template> -->
  </el-card>
  <el-container>
    <el-main class="lefteditor">
      <!-- <div style="margin:6px 20px 30px 20px;">
        <el-link type="primary" href="https://github.com/ZouJiu1" target="_blank">GitHub [github.com/ZouJiu1]</el-link>
        <p>
          <el-link type="primary" href="https://github.com/ZouJiu1/numpy_lstm_RNN" style="margin-left:1px;color:#000000;" target="_blank">
            numpy实现所有前向传播和反向传播的LSTM、RNN，古诗词生成
          </el-link>
        </p>
        <p>
          <el-link type="primary" href="https://github.com/ZouJiu1/CNN_numpy" style="margin-left:1px;color:#000000;" target="_blank">
            numpy实现所有前向传播和反向传播的Alexnet分类CNN网络来train MNIST，准确率：96.2%
          </el-link>
        </p>
        <p>
          <el-link type="primary" href="https://github.com/ZouJiu1/numpy_transformer" style="margin-left:1px;color:#000000;" target="_blank">
            numpy实现所有前向传播和反向传播的transformer网络，包括VIT、MNIST分类 (准确率：97.2%) 、古诗词生成
          </el-link>
        </p>
        <p>
          <el-link type="primary" href="https://github.com/ZouJiu1/Pytorch_YOLOV3" style="margin-left:1px;color:#000000;" target="_blank">
            自己写好并且train的Yolov3网络，分类、分割、检测、关节点检测
          </el-link>
          <el-button
            class="filter-item"
            type="primary"
            style="margin-left:10px;text-align:center;"
            @click="dialogVisibledetect=true"
            >
            检测
          </el-button>
          <el-dialog v-model="dialogVisibledetect">
            <div class="demo-image__lazy">
              <el-image v-for="url in urlsdetect" :key="url" :src="url" lazy />
            </div>
          </el-dialog>
          <el-button
            class="filter-item"
            type="primary"
            style="margin-left:10px;text-align:center;"
            @click="dialogVisibleseg=true"
            >
            分割
          </el-button>
          <el-dialog v-model="dialogVisibleseg">
            <div class="demo-image__lazy">
              <el-image v-for="url in urlsseg" :key="url" :src="url" lazy />
            </div>
          </el-dialog>
          <el-button
            class="filter-item"
            type="primary"
            style="margin-left:10px;text-align:center;"
            @click="dialogVisibleseg_keypoint=true"
            >
            分割+keypoint
          </el-button>
          <el-dialog v-model="dialogVisibleseg_keypoint">
            <div class="demo-image__lazy">
              <el-image v-for="url in urlsseg_keypoint" :key="url" :src="url" lazy />
            </div>
          </el-dialog>
        </p>
      </div>
      <p style="margin:10px 20px 30px 20px;">
        <el-link type="primary" href="https://zoujiu.blog.csdn.net/" target="_blank">CSDN博客 [zoujiu.blog.csdn.net/]</el-link>
      </p>
      <p style="margin:10px 20px 10px 20px;">
        <el-link type="primary" href="https://www.zhihu.com/people/zoujiu1" target="_blank">知乎 [www.zhihu.com/people/zoujiu1]</el-link>
      </p> -->
      <p
        v-for="LfF in leftresult"
        :key="LfF"
        style="margin-bottom:20px;"
      >
          <el-link type="primary" :href="LfF.link" :style="LfF.style" target="_blank">
            {{ LfF['introduction'] }}
          </el-link>
          <el-button
            v-if="LfF.showfirst == 1"
            class="filter-item"
            type="primary"
            style="margin-left:10px;text-align:center;"
            @click="LfF.dialogVisibledetect=true"
            >
            {{LfF['button1']}}
          </el-button>
          <el-dialog v-model="LfF.dialogVisibledetect">
            <div class="demo-image__lazy">
              <el-image v-for="url in LfF.image1" :src="url" lazy :zoom-rate="1.0" :max-scale="10" :min-scale="0.1">
                <template #placeholder>
                  <div class="image-slot">Loading<span class="dot">...</span></div>
                </template>
              </el-image>
            </div>
          </el-dialog>
          <el-button
            v-if="LfF.showsecond == 1"
            class="filter-item"
            type="primary"
            style="margin-left:10px;text-align:center;"
            @click="LfF.dialogVisibleseg=true"
            >
            {{LfF['button2']}}
          </el-button>
          <el-dialog v-model="LfF.dialogVisibleseg">
            <div class="demo-image__lazy">
              <el-image v-for="url in LfF.image2" :src="url" lazy :zoom-rate="1.0" :max-scale="10" :min-scale="0.1">
                <template #placeholder>
                  <div class="image-slot">Loading<span class="dot">...</span></div>
                </template>
              </el-image>
            </div>
          </el-dialog>
          <el-button
            class="filter-item"
            v-if="LfF.showthird == 1"
            type="primary"
            style="margin-left:10px;text-align:center;"
            @click="LfF.dialogVisibleseg_keypoint=true"
            >
            {{LfF['button3']}}
          </el-button>
          <el-dialog v-model="LfF.dialogVisibleseg_keypoint">
            <div class="demo-image__lazy">
              <el-image v-for="url in LfF.image3" :src="url" lazy :zoom-rate="1.0" :max-scale="10" :min-scale="0.1">
                <template #placeholder>
                  <div class="image-slot">Loading<span class="dot">...</span></div>
                </template>
              </el-image>
            </div>
          </el-dialog>
      </p>
      <el-button
        style="margin-left:10px; text-align:center;"
        @click="LeftFunctiondialogSetting"
        >
        配置
      </el-button>
      <el-button type="success" @click="downloadzipvisible=true"
        style="margin-left:6px;margin-top:0px;"
      >
        下载
      </el-button>
      <el-dialog v-model="downloadzipvisible" title="提交下载请求" width="60%" height="90%">
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
        <br>
        <span>此操作会下载该用户所有资料用来自行备份</span>
        <br>
        <el-input
          v-model="receivemail"
          placeholder="请填写接收邮箱，最好是国内邮箱账号"
          style="width: 60%; margin-left:20px;margin-bottom:10px;"
          class="filter-item"
          id="elinputmail"
          @change="mailChange"
          @blur="mailChange"
        />
        <br>
        <el-button type="primary" @click="downloadzip" id="downloadidZip"
          style="margin-left:6px;margin-top:0px;"
        >
          确认下载所有
        </el-button>
      </el-dialog>
      <el-dialog v-model="LeftSettingVisible" title="配置" width="60%" height="90%">
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
          <el-form
            v-for="tgf in LeftSettingForm"
            :key="tgf"
            style="max-width: 600px"
            :model="tgf"
            status-icon
            label-width="auto"
            class="demo-ruleForm"
            >
            <el-form-item :label="tgf.n" prop="">
              <el-input
                v-model="tgf.introduction"
                placeholder="描述. 若需要删除配置,请输入【/$删除$/】这六个字的"
                style="margin-bottom:2px;"
              />
              <el-input 
                v-model="tgf.link"
                autocomplete="off" 
                placeholder="网址"
                style="margin-bottom:2px;"
              />
              <el-select
                v-model="tgf.color"
                placeholder="Select"
                size="small"
                style="width: 240px"
              >
                <el-option label="默认#000000" value="#000000" style="color:#000000;"></el-option>
                <el-option label="rgb(136, 187, 250)" value="rgb(136, 187, 250)" style="color:rgb(136, 187, 250);"></el-option>
                <el-option label="#ff4500" value="#ff4500" style="color:#ff4500;"></el-option>
                <el-option label="#ff8c00" value="#ff8c00" style="color:#ff8c00;"></el-option>
                <el-option label="#ffd700" value="#ffd700" style="color:#ffd700;"></el-option>
                <el-option label="#90ee90" value="#90ee90" style="color:#90ee90;"></el-option>
                <el-option label="#00ced1" value="#00ced1" style="color:#00ced1;"></el-option>
                <el-option label="#1e90ff" value="#1e90ff" style="color:#1e90ff;"></el-option>
                <el-option label="#c71585" value="#c71585" style="color:#c71585;"></el-option>
                <el-option label="rgba(255, 69, 0, 0.68)" value="rgba(255, 69, 0, 0.68)" style="color:rgba(255, 69, 0, 0.68);"></el-option>
                <el-option label="rgb(255, 120, 0)" value="rgb(255, 120, 0)" style="color:rgb(255, 120, 0);"></el-option>
                <el-option label="hsv(51, 100, 98)" value="hsv(51, 100, 98)" style="color:hsv(51, 100, 98);"></el-option>
                <el-option label="hsla(209, 100%, 56%, 0.73)" value="hsla(209, 100%, 56%, 0.73)" style="color:hsla(209, 100%, 56%, 0.73);"></el-option>
                <el-option label="#c7158577" value="#c7158577" style="color:#c7158577;"></el-option>
              </el-select>
              <el-input 
                v-model="tgf.button1"
                autocomplete="off" 
                placeholder="按钮1的描述"
                style="margin-bottom:2px;"
              />
              <el-upload
                class="upload-demo"
                action="http://localhost:7009/csdn/mainpageuploadImg"
                multiple
                :on-preview="handleUpPreview"
                :on-remove="handleRemove"
                :before-remove="beforeRemove"
                :limit="100"
                :on-exceed="handleExceed"
                :on-success="handleUpLoadSuccess"
                :data="leftdataimg1"
                :before-upload="handlebefore_Upload"
              >
                <el-button type="success" style="margin-left:20px; margin-top:2px;" @click="clickimage">传图片{{ tgf.n }}_1</el-button>
                  <template #tip>
                    <div class="el-upload__tip" v-if="tgf.n == 1">
                      jpg/png/jpeg/bmp/gif files with a size less than 13Mb.
                    </div>
                  </template>
              </el-upload>
              <el-input
                v-model="tgf.button2"
                autocomplete="off"
                placeholder="按钮2的描述"
                style="margin-bottom:2px;"
              />
              <el-upload
                  class="upload-demo"
                  action="http://localhost:7009/csdn/mainpageuploadImg"
                  multiple
                  :on-preview="handleUpPreview"
                  :on-remove="handleRemove"
                  :before-remove="beforeRemove"
                  :limit="100"
                  :on-exceed="handleExceed"
                  :on-success="handleUpLoadSuccess"
                  :data="leftdataimg2"
                  :before-upload="handlebefore_Upload"
                >
                  <el-button type="success" style="margin-left:20px; margin-top:2px;" @click="clickimage">传图片{{ tgf.n }}_2</el-button>
                </el-upload>
                <el-input 
                  v-model="tgf.button3"
                  autocomplete="off" 
                  placeholder="按钮3的描述"
                  style="margin-bottom:2px;"
                />
                <el-upload
                  class="upload-demo"
                  action="http://localhost:7009/csdn/mainpageuploadImg"
                  multiple
                  :on-preview="handleUpPreview"
                  :on-remove="handleRemove"
                  :before-remove="beforeRemove"
                  :limit="100"
                  :on-exceed="handleExceed"
                  :on-success="handleUpLoadSuccess"
                  :data="leftdataimg3"
                  :before-upload="handlebefore_Upload"
                >
                  <el-button type="success" style="margin-left:20px; margin-top:2px;" @click="clickimage">传图片{{ tgf.n }}_3</el-button>
                </el-upload>
            </el-form-item>
          </el-form>
          <el-button type="primary" @click="submitLeftSettingForm" id="submitLeftSettingForm">
            提交
          </el-button>
        </el-dialog>
  </el-main>
  <el-main class="preview" id="previewHalf">
    <div>
    <el-image 
      style="width:60%; overflow:auto;"
      src="/article/2寸.jpg"
      :zoom-rate="1.0"
      :max-scale="10"
      :min-scale="0.1"
      :preview-src-list="personImg"
      :initial-index="4"
      fit="cover"
      class="personimg"
    >
      <template #placeholder>
        <div class="image-slot">Loading<span class="dot">...</span></div>
      </template>
    </el-image>
    </div>
    <el-button
      style="margin-left:10px; text-align:center;"
      @click="pictureChange"
      >
      照片
    </el-button>
    <el-dialog v-model="PersonImageVisible" title="照片" width="60%" height="90%">
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
      <el-upload
        class="upload-demo"
        action="http://localhost:7009/csdn/mainpageuploadImg"
        multiple
        :on-preview="handleUpPreview"
        :on-remove="handleRemove"
        :before-remove="beforeRemove"
        :limit="1"
        :on-exceed="handleExceed"
        :on-success="handleUpLoadSuccess"
        :data="PersonImage"
        :before-upload="handlebefore_Upload"
        >
        <el-button type="success" style="margin-left:20px; margin-top:2px;" @click="clickimage">上传</el-button>
        <template #tip>
          <div class="el-upload__tip">
            jpg/png/jpeg/bmp/gif files with a size less than 13Mb.
          </div>
        </template>
      </el-upload>
      <div>
        <span style="font-size:18px;font-weight: 500;">昵称</span>
      </div>
      <el-input
        v-model="modifiednickname"
        placeholder="昵称，若不需要修改可以留空"
        style="width: 30%; margin-left:20px;margin-bottom:10px;margin-top:10px"
        class="filter-item"
        id="nickname"
      />
      <el-button type="primary" @click="NicknameSetting" id="NicknameSetting" style="margin-left:10px;">
        提交昵称修改
      </el-button>
    </el-dialog>
  </el-main>
</el-container>
</template>

<script>
import axios from 'axios'
import { ElMessage } from 'element-plus'
// import { Delete, Edit, Search, Share, Upload, Setting } from '@element-plus/icons-vue'
import Cookies from 'js-cookie'
import { ref } from 'vue'
import getusername from '/src/common.js'
export default {
  name: 'app',
  data() {
    return {
      dialogVisible: false,
      dialogVisibledetect: false,
      dialogVisibleseg: false,
      downloadzipvisible: false,
      LeftSettingVisible: false,
      dialogVisibleseg_keypoint: false,
      introductionVisible: false,
      PersonImageVisible: false,
      dialogSetting: false,
      imgdata: {mail:"", password:""},
      dialogFormVisible: false,
      postkey: "",
      modifiednickname:"",
      receivemail: "",
      result:[],
      leftresult:[],
      valueSelect:"rgb(136, 187, 250)",
      optionsSelect: ref([
        {'value':'rgb(136, 187, 250)','label':'rgb(136, 187, 250)'},
        {'value':'#ff4500','label':'#ff4500'},
        {'value':'#ff8c00','label':'#ff8c00'},
        {'value':'#ffd700','label':'#ffd700'},
        {'value':'#90ee90','label':'#90ee90'},
        {'value':'#00ced1','label':'#00ced1'},
        {'value':'#1e90ff','label':'#1e90ff'},
        {'value':'#c71585','label':'#c71585'},
        {'value':'rgba(255, 69, 0, 0.68)','label':'rgba(255, 69, 0, 0.68)'},
        {'value':'rgb(255, 120, 0)','label':'rgb(255, 120, 0)'},
        {'value':'hsv(51, 100, 98)','label':'hsv(51, 100, 98)'},
        {'value':'hsla(209, 100%, 56%, 0.73)','label':'hsla(209, 100%, 56%, 0.73)'},
        {'value':'#c7158577','label':'#c7158577'},
      ]),
      LeftSettingForm:[
        {"introduction":"", "link":"", "color":'#000000', "button1":"", "button2":"", "button3":"", 'n':1},
        {"introduction":"", "link":"", "color":'#000000', "button1":"", "button2":"", "button3":"", 'n':2},
        {"introduction":"", "link":"", "color":'#000000', "button1":"", "button2":"", "button3":"", 'n':3},
        {"introduction":"", "link":"", "color":'#000000', "button1":"", "button2":"", "button3":"", 'n':4},
        {"introduction":"", "link":"", "color":'#000000', "button1":"", "button2":"", "button3":"", 'n':5},
        {"introduction":"", "link":"", "color":'#000000', "button1":"", "button2":"", "button3":"", 'n':6},
        {"introduction":"", "link":"", "color":'#000000', "button1":"", "button2":"", "button3":"", 'n':7},
        {"introduction":"", "link":"", "color":'#000000', "button1":"", "button2":"", "button3":"", 'n':8},
        {"introduction":"", "link":"", "color":'#000000', "button1":"", "button2":"", "button3":"", 'n':9},
        {"introduction":"", "link":"", "color":'#000000', "button1":"", "button2":"", "button3":"", 'n':10},
      ],
      SettingForm: [
        {"introduction":"姓名", "link":"", "link_describe":"邹九", 'other_describe':"", "button":"", 'n':1},
        {"introduction":"邮箱", "link":"", "link_describe":"1069679911@qq.com", 'other_describe':"", "button":"", 'n':2},
        {"introduction":"攀拓PAT", "link":"https://github.com/ZouJiu1/PAT", "link_describe":"github.com/ZouJiu1/PAT", 'other_describe':"甲级/乙级基本都刷完了", "button":"PAT证书", 'n':3},
        {"introduction":"Leetcode主页", "link":"https://leetcode.cn/u/shiheyingzhe/", "link_describe":"leetcode.cn/u/shiheyingzhe/", 'other_describe':"刷完了406道题目", "button":"", 'n':4},
        {"introduction":"Kaggle主页", "link":"https://www.kaggle.com/shiheyingzhe", "link_describe":"www.kaggle.com/shiheyingzhe", 'other_describe':"", "button":"", 'n':5},
        {"introduction":"", "link":"", "link_describe":"", 'other_describe':"", "button":"", "n":6},
        {"introduction":"", "link":"", "link_describe":"", 'other_describe':"", "button":"", "n":7},
        {"introduction":"", "link":"", "link_describe":"", 'other_describe':"", "button":"", "n":8},
        {"introduction":"", "link":"", "link_describe":"", 'other_describe':"", "button":"", "n":9},
        {"introduction":"", "link":"", "link_describe":"", 'other_describe':"", "button":"", "n":10},
      ],
      personImg: ["/article/2寸.jpg",],
      urlsdetect: [
        "/article/github_yolov3/0.jpg",
        "/article/github_yolov3/1.jpg",
        "/article/github_yolov3/2.jpg",
        "/article/github_yolov3/3.jpg",
        "/article/github_yolov3/4.jpg",
        "/article/github_yolov3/5.jpg",
        "/article/github_yolov3/6.jpg",
        "/article/github_yolov3/7.jpg",
        "/article/github_yolov3/8.jpg",
        "/article/github_yolov3/9.jpg",
        "/article/github_yolov3/10.jpg",
        "/article/github_yolov3/11.jpg",
        "/article/github_yolov3/12.jpg",
        "/article/github_yolov3/13.jpg",
        "/article/github_yolov3/-1.jpg",
      ],
      urlsseg: [
        "/article/github_yolov3/segshow/000000004495.jpg",
        "/article/github_yolov3/segshow/000000025424.jpg",
        "/article/github_yolov3/segshow/000000033114.jpg",
        "/article/github_yolov3/segshow/000000089556.jpg",
        "/article/github_yolov3/segshow/000000112798.jpg",
        "/article/github_yolov3/segshow/000000122962.jpg",
        "/article/github_yolov3/segshow/000000133567.jpg",
        "/article/github_yolov3/segshow/000000181542.jpg",
        "/article/github_yolov3/segshow/000000205282.jpg",
        "/article/github_yolov3/segshow/000000228436.jpg",
        "/article/github_yolov3/segshow/000000268375.jpg",
        "/article/github_yolov3/segshow/000000270908.jpg",
        "/article/github_yolov3/segshow/000000297147.jpg",
        "/article/github_yolov3/segshow/000000344816.jpg",
        "/article/github_yolov3/segshow/000000385719.jpg",
        "/article/github_yolov3/segshow/000000504635.jpg",
        "/article/github_yolov3/segshow/000000546829.jpg",
        "/article/github_yolov3/segshow/000000568213.jpg",
      ],
      urlsseg_keypoint: [
        "/article/github_yolov3/keypoint_seg/000000001000.jpg",
        "/article/github_yolov3/keypoint_seg/000000031093.jpg",
        "/article/github_yolov3/keypoint_seg/000000041990.jpg",
        "/article/github_yolov3/keypoint_seg/000000052591.jpg",
        "/article/github_yolov3/keypoint_seg/000000060347.jpg",
        "/article/github_yolov3/keypoint_seg/000000072281.jpg",
        "/article/github_yolov3/keypoint_seg/000000086956.jpg",
        "/article/github_yolov3/keypoint_seg/000000091500.jpg",
        "/article/github_yolov3/keypoint_seg/000000118921.jpg",
        "/article/github_yolov3/keypoint_seg/000000172877.jpg",
        "/article/github_yolov3/keypoint_seg/000000173830.jpg",
        "/article/github_yolov3/keypoint_seg/000000181542.jpg",
        "/article/github_yolov3/keypoint_seg/000000186449.jpg",
        "/article/github_yolov3/keypoint_seg/000000257478.jpg",
        "/article/github_yolov3/keypoint_seg/000000274411.jpg",
        "/article/github_yolov3/keypoint_seg/000000295478.jpg",
        "/article/github_yolov3/keypoint_seg/000000302536.jpg",
        "/article/github_yolov3/keypoint_seg/000000309964.jpg",
        "/article/github_yolov3/keypoint_seg/000000345466.jpg",
        "/article/github_yolov3/keypoint_seg/000000357737.jpg",
        "/article/github_yolov3/keypoint_seg/000000391722.jpg",
        "/article/github_yolov3/keypoint_seg/000000398028.jpg",
        "/article/github_yolov3/keypoint_seg/000000410496.jpg",
        "/article/github_yolov3/keypoint_seg/000000412362.jpg",
        "/article/github_yolov3/keypoint_seg/000000463174.jpg",
        "/article/github_yolov3/keypoint_seg/000000470173.jpg",
        "/article/github_yolov3/keypoint_seg/000000477288.jpg",
        "/article/github_yolov3/keypoint_seg/000000498807.jpg",
        "/article/github_yolov3/keypoint_seg/000000500478.jpg",
        "/article/github_yolov3/keypoint_seg/000000515579.jpg",
        "/article/github_yolov3/keypoint_seg/000000517056.jpg",
        "/article/github_yolov3/keypoint_seg/000000554579.jpg",
        "/article/github_yolov3/keypoint_seg/000000574823.jpg",
      ],
      targetn: "-1",
      originnickname:"",
    }
  },
  watch: {},
  mounted(){
    // this.clickpage();
    this.getdata();
    // this.show();
    // this.leftgetdata();
    // this.getimage();
  },
  methods: {
    // show() {
    //   console.log(this.LeftSettingForm);
    //   console.log(this.SettingForm);
    // },
    mailChange() {
      // console.log(this.ruleForm.email);
      if(this.receivemail.length < 7) {
        ElMessage("邮箱格式不正确！");
        return false;
      }
      let r = this.receivemail;
      // console.log(r);
      let ret = r.indexOf("@");
      if( ret < 0) {                              // || r.indexOf(".com") < 0
        ElMessage("邮箱格式不正确！");
        return false;
      }
      return true;
    },
    async downloadzip() {
      if(!this.mailChange()) {
        this.downloadzipvisible = false;
        return false;
      }
      const instance = axios.create({
        baseURL: 'http://localhost:7009/commonuse/downloadall',
        timeout: 20000,
      });
      
      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {"url":document.URL, "mail":Cookies.get("mail"),
            "password":Cookies.get("password"), 'postkey':this.postkey,
            "receivemail":this.receivemail},
      }).then((response) => {
        if(response.data.ret < 0) {
          // ElMessage.error('输入的密钥不对!');
          ElMessage.error('没有登陆不能修改!');
          this.downloadzipvisible = false;
          return false;
        }else if(response.data.ret==2) {
          ElMessage.error(`已经提交过下载申请了，请勿重复申请下载!`);
          this.downloadzipvisible = false;
          return false;
        }
        this.postkey = "";
        this.downloadzipvisible = false;
        ElMessage.info('提交下载申请成功，一周内会发送到填写的邮箱!');
      });
    },
    pictureChange() {
      this.PersonImageVisible = true;
    },
    async FunctiondialogSetting() {
      let gu;
      await getusername(document.URL).then((response) => {
        gu = response;
      });

      const instance = axios.create({
        baseURL: 'http://localhost:7009/csdn/GetSetting',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {'SettingForm' : this.SettingForm, "url":document.URL, "mail":Cookies.get("mail"),
               "password":Cookies.get("password"), 'postkey':this.postkey,},
      }).then((response) => {
        if(gu && gu.ret==1) {
          this.modifiednickname = gu.username;
          this.originnickname = gu.username;
        }
        this.SettingForm = response.data.jfile;
        this.dialogSetting = true;
      });
    },
    async LeftFunctiondialogSetting() {
      const instance = axios.create({
        baseURL: 'http://localhost:7009/csdn/GetSetting',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {'SettingForm' : this.LeftSettingForm, "url":document.URL, "mail":Cookies.get("mail"),
               "password":Cookies.get("password"), 'postkey':this.postkey,'index':'.'},
      }).then((response) => {
        this.LeftSettingForm = response.data.jfile;
        this.LeftSettingVisible = true;
      });
    },
    clickimage(event) {
      this.targetn = event.target.innerText;
      this.targetn = this.targetn.substring(3);
      // console.log(99, event, this.targetn);
    },
    PersonImage() {
      ElMessage.success("肖像修改需要等几分钟才行，过会再来查看");
      return {"n":this.targetn, "mail":Cookies.get("mail"), 
        "password":Cookies.get("password"), 'postkey':this.postkey,
        "url":document.URL,'person':1};
    },
    leftdataimg1(){
      return {"n":this.targetn, "mail":Cookies.get("mail"), 
      "password":Cookies.get("password"), 'postkey':this.postkey,
      "url":document.URL,'index':1};
    },
    leftdataimg2(){
      return {"n":this.targetn, "mail":Cookies.get("mail"), 
      "password":Cookies.get("password"), 'postkey':this.postkey,
      "url":document.URL,'index':2};
    },
    leftdataimg3(){
      return {"n":this.targetn, "mail":Cookies.get("mail"), 
      "password":Cookies.get("password"), 'postkey':this.postkey,
      "url":document.URL,'index':3};
    },
    dataimg() {
      return {"n":this.targetn, "mail":Cookies.get("mail"), 
      "password":Cookies.get("password"), 'postkey':this.postkey,
      "url":document.URL};
    },
    async upLoadbutton() {
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
      }).then((response) => {
        if(response.data.ret || (gu && gu.ret > 0)) {
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
    async NicknameSetting() {
      const instance = axios.create({
        baseURL: 'http://localhost:7009/csdn/NicknameSetting',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      let mnn="";
      if(this.modifiednickname!=this.originnickname){
        mnn = this.modifiednickname;
      }
      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {"url":document.URL, "mail":Cookies.get("mail"),
            "password":Cookies.get("password"), 'postkey':this.postkey, 
            'modifiednickname':mnn},
      }).then((response) => {
        if(response.data.ret < 0) {
          // ElMessage.error('输入的密钥不对!');
          ElMessage.error('没有登陆不能修改!');
          this.PersonImageVisible = false;
          return false;
        }
        this.getdata();
        this.postkey = "";
        this.PersonImageVisible = false;
        location.reload();
      });
    },
    async submitSettingForm() {
      const instance = axios.create({
        baseURL: 'http://localhost:7009/csdn/FormsubmitSetting',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {'SettingForm' : this.SettingForm, "url":document.URL, "mail":Cookies.get("mail"),
            "password":Cookies.get("password"), 'postkey':this.postkey},
      }).then((response) => {
        if(response.data.ret < 0) {
          // ElMessage.error('输入的密钥不对!');
          ElMessage.error('没有登陆不能修改!');
          this.dialogSetting = false;
          return false;
        }
        this.getdata();
        this.postkey = "";
        this.dialogSetting = false;
      });
    },
    async submitLeftSettingForm() {
      const instance = axios.create({
        baseURL: 'http://localhost:7009/csdn/FormsubmitSetting',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {'SettingForm' : this.LeftSettingForm, "url" : document.URL, "mail" : Cookies.get("mail"),
               "password" : Cookies.get("password"), 'postkey' : this.postkey, 'Left' : '.'},
      }).then((response) => {
        if(response.data.ret < 0) {
          // ElMessage.error('输入的密钥不对!');
          ElMessage.error('没有登陆不能修改!');
          this.LeftSettingVisible = false;
          return false;
        }
        this.getdata();
        // this.postkey = "";
        this.LeftSettingVisible = false;
      });
    },
    async getdata() {
      const instance = axios.create({
        baseURL: 'http://localhost:7009/csdn/mainpagedataget',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      let mail = "";
      mail = Cookies.get("mail");
      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {'url' : document.URL, "mail":mail, "password":"."},
      }).then((response) => {
        this.result = response.data.jfile[0];
        let touxiang = response.data.jfile[1];
        this.leftresult = response.data.jfile[2];
        let pi = document.getElementsByClassName("personimg")[0].children[0];
        pi.src = touxiang;
        this.personImg[0] = touxiang;
        // console.log(pi);
      });
    },
    // async leftgetdata() {
    //   const instance = axios.create({
    //     baseURL: 'http://localhost:7009/csdn/mainpagedataget',
    //     timeout: 20000,
    //   });
      
    //   // console.log(this.search_param);
    //   let mail = "";
    //   mail = Cookies.get("mail");
    //   await instance({
    //     method: 'POST',
    //     headers: {
    //       'X-Requested-With': 'XMLHttpRequest'
    //     },
    //     data: {'url' : document.URL, "mail":mail, "password":".", "index":"."},
    //   }).then(async (response) => {
    //     console.log(response.data.jfile);
    //     this.leftresult = response.data.jfile;
    //   });
    // },
    // async getimage() {
    //   const instance = axios.create({
    //     baseURL: 'http://localhost:7009/csdn/mainpagedataget',
    //     timeout: 20000,
    //   });
      
    //   // console.log(this.search_param);
    //   let mail = "";
    //   mail = Cookies.get("mail");
    //   await instance({
    //     method: 'POST',
    //     headers: {
    //       'X-Requested-With': 'XMLHttpRequest'
    //     },
    //     data: {'url' : document.URL, "mail":mail, "password":".", "person":"."},
    //   }).then((response) => {
    //     this.kkk = response.data.jfile;
    //   });
    // },
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
        params: {'type' : 'home'},
      }).then((response) => {
      });
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
      // console.log(11, rawFile);
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
      this.imgdata.mail = "";
      this.imgdata.password = "";
      this.getdata();
      // this.postkey = "";
    },
    Getimgdata(n) {
      this.imgdata['n'] = n;
    }
  },
}
</script>

<style scoped>
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

p {
  margin: 0em 0;
  display: block;
  margin-block-start: 0.3em;
  margin-block-end: 0em;
  margin-inline-start: 0px;
  margin-inline-end: 0px;
  unicode-bidi: isolate;
  word-break: break-word;
  line-height: 100%;
  font-family: -apple-system,BlinkMacSystemFont,Helvetica Neue,PingFang SC,var(--zFontSansSerif),Microsoft YaHei,Source Han Sans SC,Noto Sans CJK SC,WenQuanYi Micro Hei,sans-serif;
  font-size: 1.1em;
}

.lefteditor {
  width: 61%;
  height: 55vh;
  background-color: #eeffee;
  border: 0px solid #ffffff;
}
.preview {
  width: 39%;
  height: 55vh;
  background-color: #eeffee;
}

.demo-image__lazy {
  height: 80vh;
  overflow-y: auto;
}
.demo-image__lazy .el-image {
  display: block;
  min-height: 200px;
  margin-bottom: 10px;
}
.demo-image__lazy .el-image:last-child {
  margin-bottom: 0;
}
</style>
