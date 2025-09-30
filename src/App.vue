<template>
  <div id='app'>
  <el-container class="layout-container-demo">
    <el-header class="el-header" id='elheader'>
      <div class="toolbar" >
        <span id='headerTitle' style="text-align:center; margin-right: 8px; margin-top: 10px;margin-left:30%;font-size:27px;">
          {{nicknamestart}}的个人页面
        </span>
        <!-- often used website <el-avatar shape="square" :size="30 + 10" src="/animal.JPG" style="align:right; margin-top: 2px" /> -->
        <!-- often used website <el-avatar shape="square" :size="30 + 10" src="/animal.JPG" style="align:right; margin-top: 2px" /> -->
        <span id='APPgeren' v-if="notrelease">
          <img src="/article/imgbook/all/animal.jpg" style="width:3em; margin-bottom: -2.3vh; scale:0.76;"/>
        </span>

        <!-- <link rel="icon" href="/animal.png"> -->
        <!-- <button :hidden="REGISTERVisible" @click="register" class="filter-item"
        style='margin-left:20%;text-align:center;background-color:#ffffff;border-color:#ffffff;'>
        注册</button>
        <button :hidden="LOGINVisible" @click="login" class="filter-item"
        style='margin-left:10px;text-align:center;background-color:#ffffff;border-color:#ffffff;'>
        登录</button>
        <button :hidden="dialogLogOutVisible" @click="logout" class="filter-item"
        style='margin-left:26%;text-align:center;background-color:#ffffff;border-color:#ffffff;'>
        logout</button> -->
        <span style="margin-left:40vh;" :hidden="registerbutton">
          <el-button
            :hidden="registerVisible"
            style="margin-left:0px;text-align:center;"
            @click="register"
            type="primary"
            text
            bg
            >
            注册
          </el-button>   <!--bg-->
        </span>
        <span style="margin-left:1vh;" :hidden="loginbutton">
          <el-button
            :hidden="loginVisible"
            style="margin-left:0px;text-align:center;"
            @click="login"
            type="primary"
            text
            bg
            >
            登录
          </el-button>  <!--bg-->
        </span>
        <span style="margin-left:40vh;" :hidden="logoutbutton">
          <el-button
            :hidden="logoutVisible"
            style="margin-left:0px;text-align:center;"
            @click="logout"
            type="info"
            text
            bg
            >
            登出
          </el-button>  <!--bg-->
        </span>
        <span :hidden="returnback" style="margin-left:44vh;">
          <el-button @click="returnbackhome" type="success">返回</el-button>
        </span>
        <el-dialog v-model="dialogLoginVisible" title="登录" width="77%" height="90%">
          <el-form
            style="max-width: 600px"
            :model="LoginForm"
            status-icon
            :rules="rules"
            label-width="auto"
            class="demo-ruleForm"
            >
            <el-form-item label="邮箱或用户名" prop="email">
              <el-input
                v-model="LoginForm.username"
                autocomplete="off"
                placeholder="@ || username"
                @change="usernameChange"
                @blur="usernameChange"
              />
            </el-form-item>
            <el-form-item label="Password" prop="pass">
              <el-input 
                v-model="LoginForm.password" 
                type="password" 
                autocomplete="off" 
                placeholder="*"
                @change="loginPassChange"
                @blur="loginPassChange"
                />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitLoginForm" id="submitLoginForm">
                点击登录主页
              </el-button>
              <el-button @click="resetLoginForm">重置</el-button>
              <el-button @click="forgetVisible = true">修改密钥</el-button>
              <el-dialog v-model="forgetVisible" title="修改密钥" width="90%" height="90%">
                <el-form
                  style="max-width: 600px"
                  :model="LoginForm"
                  status-icon
                  :rules="rules"
                  label-width="auto"
                  class="demo-ruleForm"
                  >
                  <el-form-item label="New Password" prop="pass">
                    <el-input 
                      v-model="ruleForm.pass" 
                      type="password" 
                      autocomplete="off" 
                      placeholder="*"
                      @change="pFirstChange"
                      @blur="pFirstChange"
                    />
                  </el-form-item>
                  <el-form-item label="New Password Confirm" prop="checkPass">
                      <el-input
                        v-model="ruleForm.checkPass"
                        type="password"
                        autocomplete="off"
                        placeholder="*"
                        @change="pSecondChange"
                        @blur="pSecondChange"
                      />
                  </el-form-item>
                  <el-form-item label="Email" prop="Email">
                      <el-input
                        v-model="ruleForm.email" 
                        placeholder="@"
                        @change="mailChange"
                        @blur="mailChange"
                        style="width:60%"/>
                        <el-button type="primary" style="margin-left:10px;" @click="SendVerifyRevisePassword">
                          点击发送邮箱验证
                        </el-button>
                  </el-form-item>
                  <el-form-item label="Email Confirm" prop="emailConfirm" >
                      <el-input
                        v-model="ruleForm.verifynumber"
                        placeholder="number"
                        @change="emailConfirmChange"
                        @blur="emailConfirmChange"
                        id="mailVerify"
                        style="width:30%"
                      />
                  </el-form-item>
                  <el-form-item>
                    <el-button @click="submitforgetpassword">提交</el-button>
                  </el-form-item>
                </el-form>
              </el-dialog>
            </el-form-item>
          </el-form>
        </el-dialog>
        <el-dialog v-model="dialogRegisterVisible" title="注册" width="77%" height="90%">
          <el-form
            style="max-width: 600px"
            :model="ruleForm"
            status-icon
            :rules="rules"
            label-width="auto"
            class="demo-ruleForm"
            >
            <el-form-item label="Password" prop="pass">
              <el-input 
                v-model="ruleForm.pass" 
                type="password" 
                autocomplete="off" 
                placeholder="*"
                @change="pFirstChange"
                @blur="pFirstChange"
                />
            </el-form-item>
            <el-form-item label="Password Confirm" prop="checkPass">
              <el-input
                v-model="ruleForm.checkPass"
                type="password"
                autocomplete="off"
                placeholder="*"
                @change="pSecondChange"
                @blur="pSecondChange"
              />
            </el-form-item>
            <el-form-item label="Email" prop="Email">
              <el-input 
                v-model="ruleForm.email" 
                placeholder="@"
                @change="mailChange"
                @blur="mailChange"
                style="width:60%"/>
                <el-button type="primary" style="margin-left:10px;" @click="SendVerify">
                  点击发送邮箱验证
                </el-button>
            </el-form-item>
            <el-form-item label="Email Confirm" prop="emailConfirm" >
              <el-input 
                v-model="ruleForm.verifynumber" 
                placeholder="number"
                @change="emailConfirmChange"
                @blur="emailConfirmChange"
                id="mailVerify"
                style="width:30%"
                />
            </el-form-item>
            <el-form-item label="昵称" prop="nickname" >
              <el-input
                v-model="ruleForm.nickname" 
                placeholder="nickname"
                @change="nicknameChange"
                @blur="nicknameChange"
                id="nickname"
                style="width:30%"
                />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitForm" id="submitRegister">
                提交
              </el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-dialog>
      </div>
    </el-header>
    <el-container>
      <el-aside class="el-aside" id='elaside'>
          <el-menu
          active-text-color="#ffd04b"
          class="el-menu-vertical-demo">
          <el-menu-item
          id='el-menu-item-1'
          @click="clickhome"
          >
          <!-- <router-link :to="{ name: 'home' }"> -->
            首页
          <!-- </router-link> -->
          </el-menu-item>

          <el-menu-item 
            @click="clickbook"
            id='el-menu-item-2' 
            >
            <!-- 本人看过的图书<router-link :to="{ name: 'book' }"> -->
              图书
            <!-- </router-link> -->
          </el-menu-item>

          <el-menu-item 
            @click="clickcsdn"
            id='el-menu-item-3'
            >
            <!-- <router-link :to="{ name: 'csdn' }"> -->
              <!-- <span v-if="zhihushow">CSDN<br></span> -->
              文篇
            <!-- </router-link> -->
          </el-menu-item>

          <el-menu-item 
            @click="clickvideo"
            id='el-menu-item-4'
            >
            <!-- <router-link :to="{ name: 'csdn' }"> -->
              视频
            <!-- </router-link> -->
          </el-menu-item>
          
          <el-menu-item 
            @click="clickzhihu"
            id='el-menu-item-5'
            v-if="zhihushow&&notrelease"
            >
            <!-- <router-link :to="{ name: 'zhihu' }"> -->
              知乎
            <!-- </router-link> -->
          </el-menu-item>

          <el-menu-item 
            @click="clickthink"
            id='el-menu-item-6'
            >
            <!-- <router-link :to="{ name: 'csdn' }"> -->
              片段
            <!-- </router-link> -->
          </el-menu-item>
          <el-menu-item 
            @click="clicktravel"
            id='el-menu-item-7'
            >
            <!-- <router-link :to="{ name: 'csdn' }"> -->
              游客
            <!-- </router-link> -->
          </el-menu-item>
          <el-menu-item 
            @click="clickcommon"
            id='el-menu-item-8'
            >
            <!-- <router-link :to="{ name: 'csdn' }"> -->
              常用
            <!-- </router-link> -->
          </el-menu-item>
          <el-menu-item 
            @click="clickeverydayimg"
            id='el-menu-item-9'
            style="font-weight: 200;"
            >
            <!-- <router-link :to="{ name: 'csdn' }"> -->
            图片
            <!-- </router-link> -->
          </el-menu-item>
        </el-menu>
        <el-text class="mx-1" type="success" style="color:#ffffff;">{{ TravelerStatistics }}</el-text>
        <el-button
          style="text-align:center;margin-top:23vh;"
          @click="themeChangevisible = true"
          type='primary'
        >
          主题
        </el-button>
        <el-dialog v-model="themeChangevisible" title="配置" width="70%" height="auto">
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
          <span style="font-size:16px;font-weight: 600;">方式一：</span>
          <el-checkbox v-model="checked1" label="纯色" size="large" 
            style="margin-left:10px;" @change="pureColorChange"
          />
          <el-select
            v-model="Themecolor"
            placeholder="主题"
            size="small"
            @change="changeSelect"
            style="width:20vh;margin-left:10px;"
          >
            <el-option label="默认rgb(136, 187, 250)" value="rgb(136, 187, 250)" style="color:rgb(136, 187, 250);"></el-option>
            <el-option label="圣诞" value="圣诞" style="color:rgb(77,128,95);"></el-option>
            <el-option label="除夕" value="除夕" style="color:rgb(197,78,73);"></el-option>
            <el-option label="国际劳动节" value="国际劳动节" style="color:rgb(79,130,30);"></el-option>
            <el-option label="端午节" value="端午节" style="color:rgb(110,110,110);"></el-option>
            <el-option label="中秋节" value="中秋节" style="color:rgb(196,111,39);"></el-option>
            <el-option label="情人节" value="情人节" style="color:rgb(200,180,160);"></el-option>
            <el-option label="国庆节" value="国庆节" style="color:rgb(116,160,93);"></el-option>
            <el-option label="感恩节" value="感恩节" style="color:rgb(141,64,27);"></el-option>
            <el-option label="万圣节" value="万圣节" style="color:rgb(242,167,67);"></el-option>
            <!-- <el-option label="#000000" value="#000000" style="color:#000000;"></el-option> -->
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
            <el-option label="#darkness" value="darkness" style="color:#000000;"></el-option>
          </el-select>
          <el-button type="primary" @click="submitColorForm" id="submitColorForm"
            style="margin-left:10px;"
          >
            提交
          </el-button>
          <br>
          <div style='margin-top:10px;'>
            <span style="font-size:16px;font-weight: 600;">方式二：</span>
            <span style="font-size:13px;font-weight: 300;margin-left:20px;">最上方长条的背景颜色</span>
            <el-color-picker v-model="color1" show-alpha :predefine="predefineColors" 
              @change="changeSelectSecond"
              style="margin-left:10px;"/>
            <el-input
              v-model="input1"
              style="width: 20vh;margin-left:3px;"
              disabled
              :placeholder="color1"
            />
            <span style="font-size:13px;font-weight: 300;margin-left:30px;">左侧目录的背景颜色</span>
            <el-color-picker v-model="color2" show-alpha :predefine="predefineColors" 
              @change="changeSelectSecond"
              style="margin-left:10px;"/>
            <el-input
              v-model="input2"
              style="width: 20vh;margin-left:3px;"
              disabled
              :placeholder="color2"
            />
            <span style="font-size:13px;font-weight: 300;margin-left:30px;">桌面的背景颜色</span>
            <el-color-picker v-model="color3" show-alpha :predefine="predefineColors" 
              @change="changeSelectSecond"
              style="margin-left:10px;"/>
            <el-input
              v-model="input3"
              style="width: 20vh;margin-left:3px;"
              disabled
              :placeholder="color3"
            />
            <el-button type="primary" @click="submitColorFormSecond" id="submitColorForm"
              style="margin-left:10px;"
            >
              提交
            </el-button>
          </div>
          <br>
          <el-button type="primary" @click="resetDefault" id="resetDefault"
            style="margin-left:3px;margin-top:10px;"
          >
            重置
          </el-button>
        </el-dialog>
      </el-aside>
      <el-main id='elmain'>
        <router-view />
      </el-main>
    </el-container>
    <div style="color:#666;padding:3px 0;width:100%;background-color: #f5f5f5;">
      <a 
      type="primary"
      href="https://beian.mps.gov.cn/#/query/webSearch?code=33078202002770" 
      rel="noreferrer" 
      target="_blank">
        <el-image 
        style="width:20px;"
        src="/article/logobeian.png"
        :zoom-rate="1.0"
        :max-scale="10"
        :min-scale="0.1"
        :preview-src-list="logobeian"
        :initial-index="4"
        fit="cover"
        />
      </a>
      <a 
        href="https://beian.mps.gov.cn/#/query/webSearch?code=33078202002770" 
        style="margin-left:3px;line-height:20px;font-size:16px;"
        target="_blank"
      >
        浙公网安备33078202002770号
      </a>
      <span style="margin-left:20px;line-height:20px;font-size:16px;color:#000000;">
        © 2024-2026 zoujiu.com.cn 版权所有
      </span>
      <span style="margin-left:20px;line-height:20px;font-size:16px;color:#000000;">
        ICP证:
      </span>
      <a type="primary" href="https://beian.miit.gov.cn/"
          style="margin-left:3px;line-height:20px;font-size:16px;" target="_blank" >
        湘ICP备2024086536号-1
      </a>
      <!-- <el-select
        v-model="Themecolor"
        placeholder="主题"
        @change="changeSelect"
        size="small"
        style="width:9vh;margin-left:30vh;"
      >
        <el-option label="defaultrgb(136, 187, 250)" value="rgb(136, 187, 250)" style="color:rgb(136, 187, 250);"></el-option>
        <el-option label="#000000" value="#000000" style="color:#000000;"></el-option>
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
      </el-select> -->
    </div>

  </el-container>
</div>
</template>

<script>
import axios from 'axios'
// import FormInstance from 'element-plus'
// import FormRules from 'element-plus'
// import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import getusername from '/src/common.js'
import Cookies from 'js-cookie'
import notrelease from "/src/main.js"
export default {
  name: 'app',
  data() {
    return {
      dialogRegisterVisible: false,
      postkey:"",
      checked1:true,
      themeChangevisible: false,
      ruleFormRef: "",
      sendret: true,
      notrelease: notrelease,
      dialogLoginVisible: false,
      forgetVisible: false,
      color1: 'rgb(136, 187, 250)',
      color2: 'rgb(86, 92, 99)',
      color3: 'rgb(255, 255, 255)',
      input1: "",
      input2: "",
      input3: "",
      returnback: true,
      TravelerStatistics:100,
      predefineColors: [
        'rgb(136, 187, 250)',
        '#ff4500',
        '#ff8c00',
        '#ffd700',
        '#90ee90',
        '#00ced1',
        '#1e90ff',
        '#c71585',
        'rgba(255, 69, 0, 0.68)',
        'rgb(255, 120, 0)',
        'hsv(51, 100, 98)',
        'hsva(120, 40, 94, 0.5)',
        'hsl(181, 100%, 37%)',
        'hsla(209, 100%, 56%, 0.73)',
        '#c7158577',
      ],
      Themecolor: "",
      Themeall: {
        "rgb(136, 187, 250)":{
          'elheader':"rgb(136, 187, 250)",
          'elaside':"rgb(136, 187, 250)",
          'el-menu-item-1':"rgb(86,92,99)",
          'el-menu-item-2':"rgb(86,92,99)",
          'el-menu-item-3':"rgb(86,92,99)",
          'el-menu-item-4':"rgb(86,92,99)",
          'el-menu-item-5':"rgb(86,92,99)",
          'el-menu-item-6':"rgb(86,92,99)",
          'el-menu-item-7':"rgb(86,92,99)",
          'el-menu-item-8':"rgb(86,92,99)",
          'el-menu-item-9':"rgb(86,92,99)",
          // "elmain":"rgb(136, 187, 250)",
          "elmain":"#ffffff",
        },
        "#ff4500":{
          'elheader':"#ff4500",
          'elaside':"#ff4500",
          'el-menu-item-1':"rgb(86,92,99)",
          'el-menu-item-2':"rgb(86,92,99)",
          'el-menu-item-3':"rgb(86,92,99)",
          'el-menu-item-4':"rgb(86,92,99)",
          'el-menu-item-5':"rgb(86,92,99)",
          'el-menu-item-6':"rgb(86,92,99)",
          'el-menu-item-7':"rgb(86,92,99)",
          'el-menu-item-8':"rgb(86,92,99)",
          'el-menu-item-9':"rgb(86,92,99)",
          "elmain":"#ff4500",
        },
        "#ff8c00":{
          'elheader':"#ff8c00",
          'elaside':"#ff8c00",
          'el-menu-item-1':"rgb(86,92,99)",
          'el-menu-item-2':"rgb(86,92,99)",
          'el-menu-item-3':"rgb(86,92,99)",
          'el-menu-item-4':"rgb(86,92,99)",
          'el-menu-item-5':"rgb(86,92,99)",
          'el-menu-item-6':"rgb(86,92,99)",
          'el-menu-item-7':"rgb(86,92,99)",
          'el-menu-item-8':"rgb(86,92,99)",
          'el-menu-item-9':"rgb(86,92,99)",
          "elmain":"#ff8c00",
        },
        "#ffd700":{
          'elheader':"#ffd700",
          'elaside':"#ffd700",
          'el-menu-item-1':"rgb(86,92,99)",
          'el-menu-item-2':"rgb(86,92,99)",
          'el-menu-item-3':"rgb(86,92,99)",
          'el-menu-item-4':"rgb(86,92,99)",
          'el-menu-item-5':"rgb(86,92,99)",
          'el-menu-item-6':"rgb(86,92,99)",
          'el-menu-item-7':"rgb(86,92,99)",
          'el-menu-item-8':"rgb(86,92,99)",
          'el-menu-item-9':"rgb(86,92,99)",
          "elmain":"#ffd700",
        },
        "#90ee90":{
          'elheader':"#90ee90",
          'elaside':"#90ee90",
          'el-menu-item-1':"rgb(86,92,99)",
          'el-menu-item-2':"rgb(86,92,99)",
          'el-menu-item-3':"rgb(86,92,99)",
          'el-menu-item-4':"rgb(86,92,99)",
          'el-menu-item-5':"rgb(86,92,99)",
          'el-menu-item-6':"rgb(86,92,99)",
          'el-menu-item-7':"rgb(86,92,99)",
          'el-menu-item-8':"rgb(86,92,99)",
          'el-menu-item-9':"rgb(86,92,99)",
          "elmain":"#90ee90",
        },
        "#00ced1":{
          'elheader':"#00ced1",
          'elaside':"#00ced1",
          'el-menu-item-1':"rgb(86,92,99)",
          'el-menu-item-2':"rgb(86,92,99)",
          'el-menu-item-3':"rgb(86,92,99)",
          'el-menu-item-4':"rgb(86,92,99)",
          'el-menu-item-5':"rgb(86,92,99)",
          'el-menu-item-6':"rgb(86,92,99)",
          'el-menu-item-7':"rgb(86,92,99)",
          'el-menu-item-8':"rgb(86,92,99)",
          'el-menu-item-9':"rgb(86,92,99)",
          "elmain":"#00ced1",
        },
        "#1e90ff":{
          'elheader':"#1e90ff",
          'elaside':"#1e90ff",
          'el-menu-item-1':"rgb(86,92,99)",
          'el-menu-item-2':"rgb(86,92,99)",
          'el-menu-item-3':"rgb(86,92,99)",
          'el-menu-item-4':"rgb(86,92,99)",
          'el-menu-item-5':"rgb(86,92,99)",
          'el-menu-item-6':"rgb(86,92,99)",
          'el-menu-item-7':"rgb(86,92,99)",
          'el-menu-item-8':"rgb(86,92,99)",
          'el-menu-item-9':"rgb(86,92,99)",
          "elmain":"#1e90ff",
        },
        "#c71585":{
          'elheader':"#c71585",
          'elaside':"#c71585",
          'el-menu-item-1':"rgb(86,92,99)",
          'el-menu-item-2':"rgb(86,92,99)",
          'el-menu-item-3':"rgb(86,92,99)",
          'el-menu-item-4':"rgb(86,92,99)",
          'el-menu-item-5':"rgb(86,92,99)",
          'el-menu-item-6':"rgb(86,92,99)",
          'el-menu-item-7':"rgb(86,92,99)",
          'el-menu-item-8':"rgb(86,92,99)",
          'el-menu-item-9':"rgb(86,92,99)",
          "elmain":"#c71585",
        },
        "rgba(255, 69, 0, 0.68)":{
          'elheader':"rgba(255, 69, 0, 0.68)",
          'elaside':"rgba(255, 69, 0, 0.68)",
          'el-menu-item-1':"rgb(86,92,99)",
          'el-menu-item-2':"rgb(86,92,99)",
          'el-menu-item-3':"rgb(86,92,99)",
          'el-menu-item-4':"rgb(86,92,99)",
          'el-menu-item-5':"rgb(86,92,99)",
          'el-menu-item-6':"rgb(86,92,99)",
          'el-menu-item-7':"rgb(86,92,99)",
          'el-menu-item-8':"rgb(86,92,99)",
          'el-menu-item-9':"rgb(86,92,99)",
          "elmain":"rgba(255, 69, 0, 0.68)",
        },
        "rgb(255, 120, 0)":{
          'elheader':"rgb(255, 120, 0)",
          'elaside':"rgb(255, 120, 0)",
          'el-menu-item-1':"rgb(86,92,99)",
          'el-menu-item-2':"rgb(86,92,99)",
          'el-menu-item-3':"rgb(86,92,99)",
          'el-menu-item-4':"rgb(86,92,99)",
          'el-menu-item-5':"rgb(86,92,99)",
          'el-menu-item-6':"rgb(86,92,99)",
          'el-menu-item-7':"rgb(86,92,99)",
          'el-menu-item-8':"rgb(86,92,99)",
          'el-menu-item-9':"rgb(86,92,99)",
          "elmain":"rgb(255, 120, 0)",
        },
        "hsv(51, 100, 98)":{
          'elheader':"hsv(51, 100, 98)",
          'elaside':"hsv(51, 100, 98)",
          'el-menu-item-1':"rgb(86,92,99)",
          'el-menu-item-2':"rgb(86,92,99)",
          'el-menu-item-3':"rgb(86,92,99)",
          'el-menu-item-4':"rgb(86,92,99)",
          'el-menu-item-5':"rgb(86,92,99)",
          'el-menu-item-6':"rgb(86,92,99)",
          'el-menu-item-7':"rgb(86,92,99)",
          'el-menu-item-8':"rgb(86,92,99)",
          'el-menu-item-9':"rgb(86,92,99)",
          "elmain":"hsv(51, 100, 98)",
        },
        "hsla(209, 100%, 56%, 0.73)":{
          'elheader':"hsla(209, 100%, 56%, 0.73)",
          'elaside':"hsla(209, 100%, 56%, 0.73)",
          'el-menu-item-1':"rgb(86,92,99)",
          'el-menu-item-2':"rgb(86,92,99)",
          'el-menu-item-3':"rgb(86,92,99)",
          'el-menu-item-4':"rgb(86,92,99)",
          'el-menu-item-5':"rgb(86,92,99)",
          'el-menu-item-6':"rgb(86,92,99)",
          'el-menu-item-7':"rgb(86,92,99)",
          'el-menu-item-8':"rgb(86,92,99)",
          'el-menu-item-9':"rgb(86,92,99)",
          "elmain":"hsla(209, 100%, 56%, 0.73)",
        },
        "#c7158577":{
          'elheader':"#c7158577",
          'elaside':"#c7158577",
          'el-menu-item-1':"rgb(86,92,99)",
          'el-menu-item-2':"rgb(86,92,99)",
          'el-menu-item-3':"rgb(86,92,99)",
          'el-menu-item-4':"rgb(86,92,99)",
          'el-menu-item-5':"rgb(86,92,99)",
          'el-menu-item-6':"rgb(86,92,99)",
          'el-menu-item-7':"rgb(86,92,99)",
          'el-menu-item-8':"rgb(86,92,99)",
          'el-menu-item-9':"rgb(86,92,99)",
          "elmain":"#c7158577",
        },
        "darkness":{
          'elheader':"#1f1f1f",
          'elaside':"#1f1f1f",
          'el-menu-item-1':"rgb(86,92,99)",
          'el-menu-item-2':"rgb(86,92,99)",
          'el-menu-item-3':"rgb(86,92,99)",
          'el-menu-item-4':"rgb(86,92,99)",
          'el-menu-item-5':"rgb(86,92,99)",
          'el-menu-item-6':"rgb(86,92,99)",
          'el-menu-item-7':"rgb(86,92,99)",
          'el-menu-item-8':"rgb(86,92,99)",
          'el-menu-item-9':"rgb(86,92,99)",
          "elmain":"#1f1f1f",
        },
        "圣诞":{
          'elheader':"url(/article/themeImg/Christmas/Christmas",
          'elaside':"rgb(77,128,95)",
          'el-menu-item-1':"rgb(77,128,95)",
          'el-menu-item-2':"rgb(77,128,95)",
          'el-menu-item-3':"rgb(77,128,95)",
          'el-menu-item-4':"rgb(77,128,95)",
          'el-menu-item-5':"rgb(77,128,95)",
          'el-menu-item-6':"rgb(77,128,95)",
          'el-menu-item-7':"rgb(77,128,95)",
          'el-menu-item-8':"rgb(77,128,95)",
          'el-menu-item-9':"rgb(77,128,95)",
          "elmain":"rgb(77,128,95)",
        },
        "除夕":{
          'elheader':"url(/article/themeImg/Chinese_New_Year/Chinese_New_Year",
          'elaside':"rgb(197,78,73)",
          'el-menu-item-1':"rgb(197,78,73)",
          'el-menu-item-2':"rgb(197,78,73)",
          'el-menu-item-3':"rgb(197,78,73)",
          'el-menu-item-4':"rgb(197,78,73)",
          'el-menu-item-5':"rgb(197,78,73)",
          'el-menu-item-6':"rgb(197,78,73)",
          'el-menu-item-7':"rgb(197,78,73)",
          'el-menu-item-8':"rgb(197,78,73)",
          'el-menu-item-9':"rgb(197,78,73)",
          "elmain":"rgb(197,78,73)",
        },
        "国际劳动节":{
          'elheader':"url(/article/themeImg/laodongjie/laodongjie",
          'elaside':"rgb(79,130,30)",
          'el-menu-item-1':"rgb(79,130,30)",
          'el-menu-item-2':"rgb(79,130,30)",
          'el-menu-item-3':"rgb(79,130,30)",
          'el-menu-item-4':"rgb(79,130,30)",
          'el-menu-item-5':"rgb(79,130,30)",
          'el-menu-item-6':"rgb(79,130,30)",
          'el-menu-item-7':"rgb(79,130,30)",
          'el-menu-item-8':"rgb(79,130,30)",
          'el-menu-item-9':"rgb(79,130,30)",
          "elmain":"rgb(79,130,30)",
        },
        "端午节":{
          'elheader':"url(/article/themeImg/duanwujie/duanwujie",
          'elaside':"rgb(110,110,110)",
          'el-menu-item-1':"rgb(110,110,110)",
          'el-menu-item-2':"rgb(110,110,110)",
          'el-menu-item-3':"rgb(110,110,110)",
          'el-menu-item-4':"rgb(110,110,110)",
          'el-menu-item-5':"rgb(110,110,110)",
          'el-menu-item-6':"rgb(110,110,110)",
          'el-menu-item-7':"rgb(110,110,110)",
          'el-menu-item-8':"rgb(110,110,110)",
          'el-menu-item-9':"rgb(110,110,110)",
          "elmain":"rgb(110,110,110)",
        },
        "中秋节":{
          'elheader':"url(/article/themeImg/midautumn/midautumn",
          'elaside':"rgb(196,111,39)",
          'el-menu-item-1':"rgb(196,111,39)",
          'el-menu-item-2':"rgb(196,111,39)",
          'el-menu-item-3':"rgb(196,111,39)",
          'el-menu-item-4':"rgb(196,111,39)",
          'el-menu-item-5':"rgb(196,111,39)",
          'el-menu-item-6':"rgb(196,111,39)",
          'el-menu-item-7':"rgb(196,111,39)",
          'el-menu-item-8':"rgb(196,111,39)",
          'el-menu-item-9':"rgb(196,111,39)",
          "elmain":"rgb(196,111,39)",
        },
        "情人节":{
          'elheader':"url(/article/themeImg/romantic/romantic",
          'elaside':"rgb(200,180,160)",
          'el-menu-item-1':"rgb(200,180,160)",
          'el-menu-item-2':"rgb(200,180,160)",
          'el-menu-item-3':"rgb(200,180,160)",
          'el-menu-item-4':"rgb(200,180,160)",
          'el-menu-item-5':"rgb(200,180,160)",
          'el-menu-item-6':"rgb(200,180,160)",
          'el-menu-item-7':"rgb(200,180,160)",
          'el-menu-item-8':"rgb(200,180,160)",
          'el-menu-item-9':"rgb(200,180,160)",
          "elmain":"rgb(200,180,160)",
        },
        "国庆节":{
          'elheader':"url(/article/themeImg/guoqing/guoqing",
          'elaside':"rgb(116,160,93)",
          'el-menu-item-1':"rgb(116,160,93)",
          'el-menu-item-2':"rgb(116,160,93)",
          'el-menu-item-3':"rgb(116,160,93)",
          'el-menu-item-4':"rgb(116,160,93)",
          'el-menu-item-5':"rgb(116,160,93)",
          'el-menu-item-6':"rgb(116,160,93)",
          'el-menu-item-7':"rgb(116,160,93)",
          'el-menu-item-8':"rgb(116,160,93)",
          'el-menu-item-9':"rgb(116,160,93)",
          "elmain":"rgb(116,160,93)",
        },
        "万圣节":{
          'elheader':"url(/article/themeImg/halloween/halloween",
          'elaside':"rgb(242,167,67)",
          'el-menu-item-1':"rgb(242,167,67)",
          'el-menu-item-2':"rgb(242,167,67)",
          'el-menu-item-3':"rgb(242,167,67)",
          'el-menu-item-4':"rgb(242,167,67)",
          'el-menu-item-5':"rgb(242,167,67)",
          'el-menu-item-6':"rgb(242,167,67)",
          'el-menu-item-7':"rgb(242,167,67)",
          'el-menu-item-8':"rgb(242,167,67)",
          'el-menu-item-9':"rgb(242,167,67)",
          "elmain":"rgb(242,167,67)",
        },
        "感恩节":{
          'elheader':"url(/article/themeImg/Thanksgiving/Thanksgiving",
          'elaside':"rgb(141,64,27)",
          'el-menu-item-1':"rgb(141,64,27)",
          'el-menu-item-2':"rgb(141,64,27)",
          'el-menu-item-3':"rgb(141,64,27)",
          'el-menu-item-4':"rgb(141,64,27)",
          'el-menu-item-5':"rgb(141,64,27)",
          'el-menu-item-6':"rgb(141,64,27)",
          'el-menu-item-7':"rgb(141,64,27)",
          'el-menu-item-8':"rgb(141,64,27)",
          'el-menu-item-9':"rgb(141,64,27)",
          "elmain":"rgb(141,64,27)",
        },
      },
      // dialogLogOutVisible: true,
      // LOGINVisible:false,
      // REGISTERVisible:false,
      logoutbutton: true,  
      loginbutton: false,  
      registerbutton: false,
      LoginForm: {
        password: "",
        username: "",
      },
      ruleForm: {
            pass: '',
            checkPass: '',
            email: '',
            verifynumber: '',
            nickname: "",
          },
      rules: "",
      logobeian: ["/article/logobeian.png"],
      zhihushow: true,
      nicknamestart:"邹九",
      first:true,
    }
  },
  watch: {},
  mounted() {
    // if(this.first) {
    // let url = document.URL;
    // this.clickhome();
    this.loading();
    this.getColor();
    //   this.first = false;
    // }
  },
  methods: {
    pureColorChange(value) {
      // console.log(value);
      this.changeSelect(this.Themecolor);
    },
    changeSelect(value) {
      // console.log(value);
      // let el_header = document.getElementById("elheader");
      // el_header.style.setProperty("background-color", value);
      let ele, item;
      // for(let pairs of Object.entries(this.Themeall)) {
      //   item = pairs[1];
        // for(let pe of Object.entries(item)) {
        //   ele = document.getElementById(pe[0]);
        //   console.log(pairs, pe, ele);
        //   ele.style = pe[1];
        // }
      // }
      item = this.Themeall[value];
      if(value=='darkness') {
        this.checked1 = false;
      }
      if(value=='圣诞'||value=="除夕"|| (value.indexOf("节") > 0)) {
        this.checked1 = false;
      }
      for(let pe of Object.entries(item)) {
        ele = document.getElementById(pe[0]);
        // console.log(this.checked1, ele, pe[1]);
        if(ele) {
          if(this.checked1) {
            if(pe[0]=='elheader') {
              ele.style.backgroundImage = "";
            }
            ele.style.setProperty("background-color", value);
          } else {
            if(value=='圣诞' && pe[0]=='elheader') {
              // let kk = ele.style.backgroundImage
              // console.log(this.checked1, kk, ele, pe[1]);
              let ran = Math.floor(Math.random() * 88);
              ele.style.setProperty("background-color", "rgb(77,128,95)");
              if(notrelease) {
                ele.style.backgroundImage = pe[1] + ran + ".png)";
              } else {
                ele.style.backgroundImage = pe[1] + ran + ".jpg)";
              }
              // kk = ele.style.backgroundImage
              // console.log(pe[1] + ran + ".png");
            }
            else if(value=='除夕' && pe[0]=='elheader') {
              // let kk = ele.style.backgroundImage
              // console.log(this.checked1, kk, ele, pe[1]);
              let ran = Math.floor(Math.random() * 116);
              ele.style.setProperty("background-color", "rgb(197,78,73)");
              if(notrelease) {
                ele.style.backgroundImage = pe[1] + ran + ".png)";
              } else {
                ele.style.backgroundImage=pe[1] + ran + ".jpg)";
              }
              // kk = ele.style.backgroundImage
              // console.log(pe[1] + ran + ".png");
            }
            else if(value=="国际劳动节" && pe[0]=='elheader') {
              let ran = Math.floor(Math.random() * 60);
              ele.style.setProperty("background-color", "rgb(79,130,30)");
              if(notrelease) {
                ele.style.backgroundImage = pe[1] + ran + ".png)";
              } else {
                ele.style.backgroundImage=pe[1] + ran + ".jpg)";
              }
            }
            else if(value=="端午节" && pe[0]=='elheader') {
              let ran = Math.floor(Math.random() * 52);
              ele.style.setProperty("background-color", "rgb(110, 110, 110)");
              if(notrelease) {
                ele.style.backgroundImage = pe[1] + ran + ".png)";
              } else {
                ele.style.backgroundImage=pe[1] + ran + ".jpg)";
              }
            }
            else if(value=="中秋节" && pe[0]=='elheader') {
              let ran = Math.floor(Math.random() * 96);
              ele.style.setProperty("background-color", "rgb(196,111,39)");
              if(notrelease) {
                ele.style.backgroundImage = pe[1] + ran + ".png)";
              } else {
                ele.style.backgroundImage=pe[1] + ran + ".jpg)";
              }
            }
            else if(value=="情人节" && pe[0]=='elheader') {
              let ran = Math.floor(Math.random() * 86);
              ele.style.setProperty("background-color", "rgb(200,180,160)");
              if(notrelease) {
                ele.style.backgroundImage = pe[1] + ran + ".png)";
              } else {
                ele.style.backgroundImage=pe[1] + ran + ".jpg)";
              }
            }
            else if(value=="国庆节" && pe[0]=='elheader') {
              let ran = Math.floor(Math.random() * 56);
              ele.style.setProperty("background-color", "rgb(116,160,93)");
              if(notrelease) {
                ele.style.backgroundImage = pe[1] + ran + ".png)";
              } else {
                ele.style.backgroundImage=pe[1] + ran + ".jpg)";
              }
            }
            else if(value=="万圣节" && pe[0]=='elheader') {
              let ran = Math.floor(Math.random() * 72);
              ele.style.setProperty("background-color", "rgb(242,167,67)");
              if(notrelease) {
                ele.style.backgroundImage = pe[1] + ran + ".png)";
              } else {
                ele.style.backgroundImage=pe[1] + ran + ".jpg)";
              }
            }
            else if(value=="感恩节" && pe[0]=='elheader') {
              let ran = Math.floor(Math.random() * 144);
              ele.style.setProperty("background-color", "rgb(141,64,27)");
              if(notrelease) {
                ele.style.backgroundImage = pe[1] + ran + ".png)";
              } else {
                ele.style.backgroundImage=pe[1] + ran + ".jpg)";
              }
            }
            else {
              if(pe[0]=='elheader') {
                ele.style.backgroundImage = "";
              }
              ele.style.setProperty("background-color", pe[1]);
              // console.log(this.checked1, kk, ele, pe[1]);
            }
          }
        }
      }
      // for(let pe of Object.entries(item)) {
      //   ele = document.getElementById(pe[0]);
      //   console.log(ele);
      // }
    },
    resetDefault() {
      this.checked1 = false;
      this.Themecolor = "rgb(136, 187, 250)";
      this.color1 = "rgb(136, 187, 250)";
      this.color2 = "rgb(86,92,99)";
      this.color3 = "rgb(255, 255, 255)";
      this.themeChangevisible = false;
      this.submitColorFormSecond();
      // this.changeSelect(this.Themecolor);
    },
    async getColor(value) {
      const instance = axios.create({
        baseURL: 'http://localhost:7009/csdn/getThemeColor',
        timeout: 20000,
      });
      
      // console.log(document.URL);
      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {"url":document.URL, "mail":Cookies.get("mail"),
               "password":Cookies.get("password"), 'postkey':this.postkey,},
      }).then((response) => {
        if(response.data.type=='1') {
          this.checked1 = response.data.checked1;
          this.Themecolor = response.data.Themecolor;
          this.changeSelect(this.Themecolor);
        } else {
          this.color1 = response.data.color1;
          this.color2 = response.data.color2;
          this.color3 = response.data.color3;
          this.changeSelectSecond();
        }
        this.TravelerStatistics = response.data.TravelerStatistics;
      });
    },
    async submitColorFormSecond() {
      const instance = axios.create({
        baseURL: 'http://localhost:7009/csdn/themeChange',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {"url":document.URL, "mail":Cookies.get("mail"),
               "password":Cookies.get("password"), 'postkey':this.postkey,'color1':this.color1,
              'color2':this.color2, 'color3':this.color3},
      }).then((response) => {
        if(response.data.ret < 0) {
          // ElMessage.error('输入的密钥不对!');
          ElMessage.error('没有登陆不能修改!');
          this.themeChangevisible = false;
          return false;
        }
        // console.log(this.Themecolor, this.themeChangevisible, this.Themeall[this.Themecolor]);
        this.changeSelectSecond();
        this.themeChangevisible = false;
      });
    },
    async submitColorForm() {
      const instance = axios.create({
        baseURL: 'http://localhost:7009/csdn/themeChange',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      await instance({
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {'checked1' : this.checked1, "url":document.URL, "mail":Cookies.get("mail"),
               "password":Cookies.get("password"), 'postkey':this.postkey,'Themecolor':this.Themecolor},
      }).then((response) => {
        if(response.data.ret < 0) {
          // ElMessage.error('输入的密钥不对!');
          ElMessage.error('没有登陆不能修改!');
          this.themeChangevisible = false;
          return false;
        }
        // console.log(this.Themecolor, this.themeChangevisible, this.Themeall[this.Themecolor]);
        this.changeSelect(this.Themecolor);
        this.themeChangevisible = false;
      });
    },
    changeSelectSecond() {
      let ele, item, cnt=0;
      item = this.Themeall["rgb(136, 187, 250)"];
      for(let pe of Object.entries(item)) {
        cnt++;
        ele = document.getElementById(pe[0]);
        // console.log(ele, pe[1], cnt);
        if(ele) {
          if(cnt <= 2) {
            ele.style.setProperty("background-color", this.color1);
          } else if(cnt==12) {
            ele.style.setProperty("background-color", this.color3);
          }
          else
          {
            ele.style.setProperty("background-color", this.color2);
          }
        }
      }
    },
    async submitforgetpassword() {
      if(this.mailChange() && this.pFirstChange() && this.pSecondChange() && this.sendret){
        ElMessage("passed!");
        const instance = axios.create({
          baseURL: 'http://localhost:7009/csdn/register',
          timeout: 20000,
        });
        
        // console.log(this.search_param);
        // console.log(this.ruleForm);
        await instance({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
          },
          data: {'information' : this.ruleForm, 'forget':true},
        }).then((response) => {
          let ret = response.data.ret;
          if(ret==100) {
            ElMessage("密钥已经修改了!");
            this.forgetVisible = false;
          }
        });
      } else {
        ElMessage('请检查password和邮箱地址的!');
      }
    },
    findmail(urlrul) {
      let mail = "";
      // let ind = urlrul.indexOf("/zj");
      let ind = urlrul.indexOf("/homepage");
      if(ind < 0) {
        let urlll = urlrul.substring(10);
        let fir = urlll.indexOf("/");
        let ur = urlll.substring(fir + 1);
        let sec = ur.indexOf('/');
        let secl = ur.indexOf('#');
        if(sec < 0) {
          sec = ur.length;
        }
        if(secl < 0) {
          secl = ur.length;
        }
        sec = Math.min(sec, secl);
        mail = urlrul.substring(fir + 11, 11 + sec + fir);
        this.zhihushow = false;
        let img = document.getElementById("APPgeren");
        // console.log(img);
        if(img) {
          img.hidden = true;
        }
        this.dialogLoginVisible = false;
        // console.log('gu', mail);
      }
      return mail
    },
    async returnbackhome() {
      let gu;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      if(gu.mail!=gu.urlmail) {
        // this.$router.push({ path: '/' + gu.mail});
        location.replace('/' + Cookies.get("mail"))
      }
    },
    async loading() {
      let gu, index = -1;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      // console.log('gu', gu, Cookies.get("mail"));
      // let urlrul = document.URL;
      // if(gu && gu.ret > 0) {
      //   index = urlrul.indexOf(gu.mail);
      // }
      // if(gu && gu.ret > 0 && index < 0) {
      //   this.$router.push({ path: '/' + this.findmail(urlrul)});
      // }
      if(!notrelease) {
        let lr = document.getElementById("linkicon");
        lr.href = '/article/logo.png';
      }
      let premail = undefined;
      premail = Cookies.get("premail");
      if(gu && gu.urlmail) {
        let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
        if(gu.urlmail!=premail) {
          Cookies.remove("csdnReset");
          Cookies.set("csdnReset", 1, { expires: expiresdate });
          Cookies.remove("thinkReset");
          Cookies.set("thinkReset", 1, { expires: expiresdate });
          Cookies.remove("travelReset");
          Cookies.set("travelReset", 1, { expires: expiresdate });
          Cookies.remove("videoReset");
          Cookies.set("videoReset", 1, { expires: expiresdate });
          Cookies.remove("zhihuReset");
          Cookies.set("zhihuReset", 1, { expires: expiresdate });
        }
        Cookies.set("premail", gu.urlmail, { expires: expiresdate });
      }
      if(gu && gu.ret > 0) {
        this.nicknamestart = gu.username;
        let username = gu.username;
        // console.log('username: ', username, Cookies.get("mail"), Cookies.get("password"));
        // let headerTitle = document.getElementById("headerTitle");
        // headerTitle.innerHTML = username + "的个人页面";

        let index = document.getElementById("indexHtmlTitle")
        // console.log(index, username);
        index.innerHTML = username + "的个人页面";

        this.dialogLoginVisible = false;

        if(gu.ret == 1) {
          this.logoutbutton = false;
          this.loginbutton = true;
          this.registerbutton = true;
        }

        // let csdn = document.getElementById("el-menu-item-3");
        // csdn.innerHTML = "文篇";
        // let all = document.getElementById("elaside");
        // let allchild = all.children[0];
        // // console.log(allchild);
        // let cot = allchild.children[4].textContent;
        // let ll = cot.indexOf("知乎");
        // // console.log(11111, cot, ll);
        // if(ll > 0) {
        //   allchild.removeChild(allchild.children[4]);
        // }
        let idzhi = document.URL;
        let zhi = idzhi.indexOf("/homepage")
        if(zhi < 0) {
          this.zhihushow = false;
        }

        let img = document.getElementById("APPgeren");
        // console.log(img);
        if(img && gu.urlmail != 'homepage') { 
          img.hidden = true;
        }
        // console.log(gu);
        if(gu.ret > 0 && gu.mail && gu.mail!=gu.urlmail) {
          // console.log(222222, gu);
          this.returnback = false;
          this.loginbutton = true;
          this.logoutbutton = true;
          this.registerbutton = true;
        }
        if(
          document.URL==("http://zoujiu.com.cn/" + gu.urlmail + "#/") || document.URL==("http://zoujiu.com.cn/#/" + gu.urlmail + "#/")
          || document.URL==("http://localhost/" + gu.urlmail + "#/") || document.URL==("http://localhost/#/" + gu.urlmail + "#/")
          || document.URL==("http://localhost:9000/" + gu.urlmail + "#/") || document.URL==("http://localhost:7009/" + gu.urlmail + "#/")
          || document.URL==("http://localhost:9000/#/" + gu.urlmail + "#/")
          || document.URL==("http://localhost:7009/#/" + gu.urlmail + "#/")
          || document.URL==("http://localhost:7009/" + gu.urlmail + "#/") || document.URL==("http://localhost:7009/#/" + gu.urlmail + "#/")
        ) {
          this.$router.push({ path: '/' + gu.urlmail});
        }
      } else {
        // if(gu.ret==0 && gu.urlmail=='zj' && Cookies.get("mail")) {
        //   this.returnback = false;
        //   this.loginbutton = true;
        //   this.registerbutton = true;
        // }
        if(
          document.URL=="http://zoujiu.com.cn/" || document.URL=="http://zoujiu.com.cn/#/"
          || document.URL=="http://localhost/" || document.URL=="http://localhost/#/"
          || document.URL=="http://localhost:9000/" || document.URL=="http://localhost:7009/"
          || document.URL=="http://localhost:9000/#/"
          || document.URL=="http://localhost:7009/#/"
          || document.URL=="http://localhost:7009/"|| document.URL=="http://localhost:7009/#/"
        ) {
          // this.$router.push({ path: '/zj'});
          // this.$router.push({ path: '/homepage'});
          location.replace("/homepage");
        }
        else {
          location.replace("/homepage");
        }
      }
      // console.log(document.URL);
    },
    register() {
      // this.ruleFormRef = ref<FormInstance>();
      // this.rules = FormRules({
      //       pass: [{ validator: this.validatePass, trigger: 'blur' }],
      //       checkPass: [{ validator: this.validatePass2, trigger: 'blur' }],
      //       age: [{ validator: this.checkAge, trigger: 'blur' }],
      //     });
      this.dialogRegisterVisible = true;
    },
    login() {
      this.dialogLoginVisible = true;
    },

    async SendVerifyRevisePassword() {
      if(!this.mailChange() && this.pFirstChange() && this.pSecondChange()) {
        ElMessage("邮箱格式不对不能发送！");
        return;
      }
      const instance = axios.create({
        baseURL: 'http://localhost:7009/csdn/sendverify',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      await instance({
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        params: {'mail':this.ruleForm.email, 'modify':true},
      }).then((response) => {
        this.sendret = response.data.number;
        if(this.sendret==2) {
          this.$alert("【" + this.ruleForm.email + "】这个邮箱已经注册过了，可以直接登录！");
          this.dialogRegisterVisible = false;
          this.resetForm();
        }
        else if(!this.sendret){
          ElMessage("send mail failed, please check email address！");
        } else {
          ElMessage("已经发送到邮箱了，有效期1天！");
        }
      });
    },
    async SendVerify() {
      if(!this.mailChange() && this.pFirstChange() && this.pSecondChange()) {
        ElMessage("邮箱格式不对不能发送！");
        return;
      }
      const instance = axios.create({
        baseURL: 'http://localhost:7009/csdn/sendverify',
        timeout: 20000,
      });
      
      // console.log(this.search_param);
      await instance({
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        params: {'mail':this.ruleForm.email},
      }).then((response) => {
        this.sendret = response.data.number;
        if(this.sendret==2) {
          this.$alert("【" + this.ruleForm.email + "】这个邮箱已经注册过了，可以直接登录！");
          this.dialogRegisterVisible = false;
          this.resetForm();
        }
        else if(!this.sendret){
          ElMessage("send mail failed, please check email address！");
        } else {
          ElMessage("已经发送到邮箱了，有效期1天！");
        }
      });
    },
    pFirstChange() {
      if(this.ruleForm.pass.length < 6 || this.ruleForm.pass.length > 26) {
        ElMessage("密码长度应该>6且<26！");
        return false;
      }
      let pass = this.ruleForm.pass;
      let sl = ".. ,./;\'[]=-`\\<>?:\"{}|~!@#$%^&*()_+-=，。/；‘【】、·《》？：“「」｜～！@#¥%……&*（）";
      let digit = 0, alpha = 0, special = 0;
      for(let i = 0; i < pass.length; i++) {
        if((pass[i] <='Z' && pass[i]>='A') || (pass[i] <='z' && pass[i]>='a')) {
          alpha = true;
        }
        if(pass[i]>=0 && pass[i]<='9') {
          digit = true;
        }
        if(sl.indexOf(pass[i]) > 0 || (sl.indexOf(pass[i])==0 && pass[i]==".")) {
          // console.log(pass, pass[i]);
          special = true;
        }
      }
      if(alpha && digit && special) {
        return true;
      } else {
        ElMessage("需要同时包含数字和英文字母和特殊字符！");
        return false;
      }
    }, 
    nicknameChange() {

    },
    pSecondChange() {
      if(this.ruleForm.pass!=this.ruleForm.checkPass){
        ElMessage("前后输入的密码不相同！");
        return false;
      }
      return true;
    },
    mailChange() {
      // console.log(this.ruleForm.email);
      if(this.ruleForm.email.length < 7) {
        ElMessage("邮箱格式不正确！");
        return false;
      }
      let r = this.ruleForm.email;
      // console.log(r);
      let ret = r.indexOf("@");
      if( ret < 0) {                              // || r.indexOf(".com") < 0
        ElMessage("邮箱格式不正确！");
        return false;
      }
      return true;
    },
    async submitForm() {
      if(this.mailChange() && this.pFirstChange() && this.pSecondChange() && this.sendret){
        ElMessage("passed!");
        const instance = axios.create({
          baseURL: 'http://localhost:7009/csdn/register',
          timeout: 20000,
        });
        
        // console.log(this.search_param);
        // console.log(this.ruleForm);
        await instance({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
          },
          data: {'information' : this.ruleForm},
        }).then((response) => {
          let ret = response.data.ret;
          if(ret==1) {
            ElMessage("已经成功注册!");
            this.dialogRegisterVisible = false;
          } else if(ret==-1) {
            ElMessage("验证数字串时间过期了！需要再次发送！");
          } else if(ret==-6) {
            ElMessage("已经注册过了，请勿重复注册，可以点击登录！");
          } else {
            ElMessage("验证失败了的！");
          }
        });
      } else {
        ElMessage('请检查password和邮箱地址的!');
      }
    },
    async submitLoginForm() {
      const instance = axios.create({
        baseURL: 'http://localhost:7009/csdn/login',
        timeout: 20000,
      });
      // console.log(this.search_param);
      await instance({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {'LoginForm' : this.LoginForm},
      }).then((response) => {
        let result = response.data;
        if(result.ret) {
          let mail = result.mail;
          let password = result.password;
          let username = result.username;
          ElMessage("登录成功了的!");
          // let expiresdate = new Date(new Date().getTime() + 60 * 24 * 60 * 60 * 1000);
          let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
          // console.log('99999999999', document.cookie, mail, password);
          Cookies.set("mail", mail, { expires: expiresdate });
          Cookies.set("password", password, { expires: expiresdate });
          Cookies.set("username", username, { expires: expiresdate });

          Cookies.remove("csdnReset");
          Cookies.set("csdnReset", 1, { expires: expiresdate });
          Cookies.remove("thinkReset");
          Cookies.set("thinkReset", 1, { expires: expiresdate });
          Cookies.remove("travelReset");
          Cookies.set("travelReset", 1, { expires: expiresdate });
          Cookies.remove("videoReset");
          Cookies.set("videoReset", 1, { expires: expiresdate });
          Cookies.remove("zhihuReset");
          Cookies.set("zhihuReset", 1, { expires: expiresdate });

          Cookies.remove("csdnsearch");
          Cookies.remove("thinksearch");
          Cookies.remove("travelsearch");
          Cookies.remove("zhihusearch");
          Cookies.remove("videosearch");
          // document.cookie = encodeURIComponent("expires") + "=" + encodeURIComponent("1s");
          // document.cookies = Cookies.set('name', 'value')
          // document.cookie = create_cookie(mail, password,'60d');
          // console.log('11111111111', document.cookie);
          // let headerTitle = document.getElementById("headerTitle");
          // headerTitle.innerHTML = username + "的个人页面";
          let index = document.getElementById("indexHtmlTitle")
          index.innerHTML = username + "的个人页面";

          this.dialogLoginVisible = false;
          // this.dialogLogOutVisible = false;
          // this.LOGINVisible = true;
          // this.REGISTERVisible = true;
          this.logoutbutton = false;
          this.loginbutton = true;
          this.registerbutton = true;
          
          this.nicknamestart = username;
          this.zhihushow = false;

          let img = document.getElementById("APPgeren");
          if(img) {
            img.hidden = true;
          }
          // let csdn = document.getElementById("el-menu-item-3");
          // csdn.innerHTML = "文篇";
          // let all = document.getElementById("elaside");
          // let allchild = all.children[0];
          // // console.log(allchild);
          // let cot = allchild.children[4].textContent;
          // let ll = cot.indexOf("知乎");
          // // console.log(11111, cot, ll);
          // if(ll > 0) {
          //   allchild.removeChild(allchild.children[4]);
          // }
          // location.reload();
          // this.$router.push({ path: '/' + mail});
          window.location.replace("/" + mail);
          // location.reload();
          this.returnback = true;
        } else {
          ElMessage("登录失败了的！");
        }
      });
      // this.$alert("登录以后请点击上方的【重置】按钮，获取个人资料！");
    },
    logout() {
      Cookies.remove("mail");
      Cookies.remove("password");
      Cookies.remove("username");
      Cookies.remove("csdndetail_reload");
      Cookies.remove("csdn");
      Cookies.remove("csdnpage");
      Cookies.remove("think");
      Cookies.remove("thinkpage");
      Cookies.remove("thinkdetail_reload");
      Cookies.remove("csdnsearch");
      Cookies.remove("thinksearch");
      Cookies.remove("travelsearch");
      Cookies.remove("zhihusearch");
      Cookies.remove("videosearch");

      let expiresdate = new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000);
      Cookies.remove("csdnReset");
      Cookies.set("csdnReset", 1, { expires: expiresdate });
      Cookies.remove("thinkReset");
      Cookies.set("thinkReset", 1, { expires: expiresdate });
      Cookies.remove("travelReset");
      Cookies.set("travelReset", 1, { expires: expiresdate });
      Cookies.remove("videoReset");
      Cookies.set("videoReset", 1, { expires: expiresdate });
      Cookies.remove("zhihuReset");
      Cookies.set("zhihuReset", 1, { expires: expiresdate });
      // this.LOGINVisible = false;
      // this.REGISTERVisible = false;
      // this.dialogLogOutVisible = true;
      this.logoutbutton = true;
      this.loginbutton = false;
      this.registerbutton = false;

      let index = document.getElementById("indexHtmlTitle")
      index.innerHTML = "邹九的个人页面";
      // this.nicknamestart = "邹九";
      this.zhihushow = true;
      
      // let zhihu = "<el-menu-item @click=\"clickzhihu\" id=\'el-menu-item-6\'> 知乎文篇 </el-menu-item>";
      // let all = document.getElementById("elaside");
      // let allchild = all.children[0];
      // allchild.insertAdjacentHTML(4, zhihu);
      let img = document.getElementById("APPgeren");
      if(img) {
        img.hidden = false;
      }
      // this.$router.push({ path: '/'});
      // location.reload();
      this.returnback = true;
      window.location.replace("/");
      // location.reload();
      // this.$router.push({ path: '/'});
    },
    resetForm() {
      this.ruleForm.pass = '';
      this.ruleForm.checkPass = '';
      this.ruleForm.email = '';
    },
    resetLoginForm() {
      this.LoginForm.password = "";
      this.LoginForm.username = "";
    },
    async clickzhihu() {
      let gu, index;
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
        this.$router.push({ path: '/zhihu/'+gu.urlmail, query:{"currentpage": 1, "pagesize":30}})
      } else {
        // this.$router.push({ path: '/csdn/zj'}); //, query:{"currentpage": 1, "pagesize":20}
        this.$router.push({ path: '/zhihu/homepage'}); //, query:{"currentpage": 1, "pagesize":20}
      }
    },
    async clickhome() {
      let gu, index;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      // let urlrul = document.URL;
      // if(gu && gu.ret > 0) {
      //   index = urlrul.indexOf(gu.mail);
      // }
      // if(gu && gu.ret > 0 && index < 0) {
      //   this.$router.push({ path: '/' + this.findmail(urlrul)});
      // }
      if(gu && gu.ret > 0) {
        this.$router.push({ path: '/'+gu.urlmail});
      } else {  
        // this.$router.push("/zj");
        this.$router.push("/homepage");
      }
    },
    async clickbook() {
      let gu, index;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      // let urlrul = document.URL;
      // if(gu && gu.ret > 0) {
      //   index = urlrul.indexOf(gu.mail);
      // }
      // if(gu && gu.ret > 0 && index < 0) {
      //   this.$router.push({ path: '/book/' + this.findmail(urlrul)});
      // }
      if(gu && gu.ret > 0) {
        this.$router.push({ path: '/book/'+gu.urlmail});
      } else {
        // this.$router.push({ path: '/book/zj'});
        this.$router.push({ path: '/book/homepage'});
      }
    },
    async clickcsdn() {
      let gu, index;
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
        this.$router.push({ path: '/csdn/'+gu.urlmail, query:{"currentpage": 1, "pagesize":30}})
      } else {
        // this.$router.push({ path: '/csdn/zj'}); //, query:{"currentpage": 1, "pagesize":20}
        this.$router.push({ path: '/csdn/homepage'}); //, query:{"currentpage": 1, "pagesize":20}
      }
    },
    async clickthink() {
      let gu, index;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      // let urlrul = document.URL;
      // if(gu && gu.ret > 0) {
      //   index = urlrul.indexOf(gu.mail);
      // }
      // if(gu && gu.ret > 0 && index < 0) {
      //   this.$router.push({ path: '/think/' + this.findmail(urlrul)});
      // }
      if(gu && gu.ret > 0) {
        this.$router.push({ path: '/think/'+gu.urlmail, query:{"currentpage": 1, "pagesize":9}});
      } else {
        // this.$router.push({ path: '/think/zj'});
        this.$router.push({ path: '/think/homepage'});
      }
    },
    async clickvideo() {
      let gu, index;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      // let urlrul = document.URL;
      // if(gu && gu.ret > 0) {
      //   index = urlrul.indexOf(gu.mail);
      // }
      // if(gu && gu.ret > 0 && index < 0) {
      //   this.$router.push({ path: '/video/' + this.findmail(urlrul)});
      // }
      if(gu && gu.ret > 0) {
        this.$router.push({ path: '/video/'+gu.urlmail, query:{"currentpage": 1, "pagesize":6}});
      } else {
        // this.$router.push({ path: '/video/zj'});
        this.$router.push({ path: '/video/homepage'});
      }
    },
    async clicktravel() {
      let gu, index;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      // let urlrul = document.URL;
      // if(gu && gu.ret > 0) {
      //   index = urlrul.indexOf(gu.mail);
      // }
      // if(gu && gu.ret > 0 && index < 0) {
      //   this.$router.push({ path: '/travel/' + this.findmail(urlrul)});
      // }
      if(gu && gu.ret > 0) {
        this.$router.push({ path: '/travel/'+gu.urlmail, query:{"currentpage": 1, "pagesize":30}});
      } else {
        // this.$router.push({ path: '/travel/zj'});
        this.$router.push({ path: '/travel/homepage'});
      }
    },
    async clickcommon() {
      let gu, index;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      // let urlrul = document.URL;
      // if(gu && gu.ret > 0) {
      //   index = urlrul.indexOf(gu.mail);
      // }
      // if(gu && gu.ret > 0 && index < 0) {
      //   this.$router.push({ path: '/commonuse/' + this.findmail(urlrul)});
      // }
      if(gu && gu.ret > 0) {
        this.$router.push({ path: '/commonuse/'+gu.urlmail});
      } else {
        // this.$router.push({ path: '/commonuse/zj'});
        this.$router.push({ path: '/commonuse/homepage'});
      }
    },
    async clickeverydayimg() {
      let gu, index;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      // let urlrul = document.URL;
      // if(gu && gu.ret > 0) {
      //   index = urlrul.indexOf(gu.mail);
      // }
      // if(gu && gu.ret > 0 && index < 0) {
      //   this.$router.push({ path: '/everydayimg/' + this.findmail(urlrul)});
      // }
      if(gu && gu.ret > 0) {
        this.$router.push({ path: '/everydayimg/'+gu.urlmail});
      } else {
        // this.$router.push({ path: '/everydayimg/zj'});
        this.$router.push({ path: '/everydayimg/homepage'});
      }
    },
  },
}
</script>

<style scoped>
html,body,#app{
  height:100%;
  width:100%;
  margin: 0px;
  padding: 0px;
}

/* .el-header {
  font-size: 24px;
  background-color: rgb(136, 187, 250); */
  /* linear-gradient(rgba(0, 0, 255, 0.5), rgba(255, 255, 0, 0.5)), */
  /* background-image: url('/article/shengdan.png'); */
  /* background-image: url('/article/themeImg/anhei/csdn_anHei.png');
  height: auto;
} */

/* .el-aside {
  width:7vh;
  font-size:30px;
  background-color:rgb(136, 187, 250);
  background-image: url('/article/themeImg/anhei/csdn_anHei_vertical.png');
} */

.layout-container-demo{
  height:calc(99vh); /*https://blog.csdn.net/qq_41499782/article/details/102624538*/
}
.layout-container-demo .el-header {
  position: relative;
  /* background-color: var(--el-color-primary-light-3); */
  /* color: var(--el-text-color-primary); */
  font-size: 24px;
  background-color: rgb(136, 187, 250);
  /* linear-gradient(rgba(0, 0, 255, 0.5), rgba(255, 255, 0, 0.5)), */
  /* background-image: url('/article/shengdan.png'); */
  /* background-image: url('/article/themeImg/anhei/csdn_anHei.png'); */
  height: 50px;
}
.layout-container-demo .el-aside {
  /* color: var(--el-text-color-primary); */
  /* background: var(--el-color-primary-light-3); */
  width:10vh;
  font-size:30px;
  background-color:rgb(136, 187, 250);
  /* background-image: url('/article/themeImg/anhei/csdn_anHei_vertical.png'); */
}
.layout-container-demo .el-menu {
  --el-menu-bg-color: #545c64;
  --el-menu-text-color: #ffffff;
  --el-menu-active-color: #000000;
  border-right: none;
}
.layout-container-demo .el-main {
  padding: 0;
  background-color: #ffffff;
}
.layout-container-demo .el-menu-item {
  font-size:16px;
  color:#ffffff; 
  height:6vh;
  background-color: rgb(86,92, 99);
  font-weight: 600;
  margin-left:-0.3vh;
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
.layout-container-demo .el-menu-item:hover { /*https://blog.csdn.net/lannieZ/article/details/124007821*/
  outline: 1 !important;
  color: #6681fa !important;
  background: #eeffff !important;
}
.layout-container-demo .el-menu-item.is-active { /*https://blog.csdn.net/lannieZ/article/details/124007821*/
  color: #6681fa !important;
  background: #ff0000 !important;
}
.layout-container-demo .toolbar{
  color: #ffffff;
}
/*https://developer.mozilla.org/zh-CN/docs/Web/CSS/:active#%E8%A7%84%E8%8C%83*/
a:link {
  /* 未访问链接 */
  color: blue;
}
.gonganbeian {
  --tw-text-opacity: 1;
  line-height:20px;
  font-size:16px;
  color: rgba(116,154,227,var(--tw-text-opacity));
}
a:visited {
  /* 已访问链接 */
  color: purple;
}
a:hover {
  /* 用户鼠标悬停 */
  background: #aafaaa;
}

button:visited {
  background: purple;
}

button:hover {
  background: #aafaaa;
}

button:active {
  background: red;
}

a:active {
  /* 激活链接 */
  color: red;
}

p:active {
  /* 激活段落 */
  background: #eee;
}
</style>
