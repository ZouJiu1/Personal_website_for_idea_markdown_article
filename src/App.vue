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
          <img :src="'/article/imgbook/all/animal.jpg'" style="width:3em; margin-bottom: -2.3vh; scale:0.76;"/>
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
        <!-- 右侧按钮组：注册/登录/登出/返回/铃铛统一 flex 排列靠右。
             旧写法各 span 用 margin-left:40vh/44vh 硬凑，按钮组合一变
             （如他人主页返回+登出同时显示）就换行错位 -->
        <span class="header-actions">
          <span :hidden="registerbutton">
            <el-button
              style="margin-left:0px;text-align:center;"
              @click="register"
              type="primary"
              text
              bg
              >
              注册
            </el-button>   <!--bg-->
          </span>
          <span :hidden="loginbutton">
            <el-button
              style="margin-left:0px;text-align:center;"
              @click="login"
              type="primary"
              text
              bg
              >
              登录
            </el-button>  <!--bg-->
          </span>
          <span :hidden="logoutbutton">
            <el-button
              style="margin-left:0px;text-align:center;"
              @click="logout"
              type="info"
              text
              bg
              >
              登出
            </el-button>  <!--bg-->
          </span>
          <span :hidden="returnback">
            <el-button @click="returnbackhome" type="success">返回</el-button>
          </span>
          <!-- 通知铃铛固定在按钮组最右 -->
          <span style="cursor:pointer;" @click="openNotices" v-if="myMail" title="通知">
            <el-badge :value="unreadCount" :hidden="unreadCount === 0">
              <span style="font-size:20px;line-height:1;">🔔</span>
            </el-badge>
          </span>
        </span>
        <el-dialog v-model="dialogLoginVisible" title="登录" width="min(520px, 92%)">
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
                placeholder="邮箱 / 用户名"
                @change="usernameChange"
                @blur="usernameChange"
                @keyup.enter="submitLoginForm"
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
                @keyup.enter="submitLoginForm"
                />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitLoginForm" id="submitLoginForm">
                点击登录主页
              </el-button>
              <el-button @click="resetLoginForm">重置</el-button>
              <el-button @click="forgetVisible = true">修改密钥</el-button>
              <el-dialog v-model="forgetVisible" title="修改密钥" width="min(480px, 92%)">
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
                        <el-button type="primary" style="margin-left:10px;" @click="SendVerifyRevisePassword" >
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
        <el-dialog v-model="dialogRegisterVisible" title="注册" width="min(560px, 92%)">
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
                placeholder="用户名@example.com"
                @change="mailChange"
                @blur="mailChange"
                style="width:60%"/>
                <el-button type="primary" style="margin-left:10px;" @click="SendVerify" id="mailconfirmbutton">
                  点击发送邮箱验证
                </el-button>
              <div style="width:100%;font-size:12px;color:#909399;line-height:1.6;">
                提示：用户名（@ 前的部分）至少需要 7 个字符，短于 7 个字符的账号将无法登录
              </div>
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
          <!-- 左侧栏目：图标 + 文案两行居中的胶囊菜单，底色跟随主题系统（#elaside 动态换色） -->
          <el-menu
          active-text-color="#337ecc"
          class="el-menu-vertical-demo">
          <el-menu-item
          index="1"
          id='el-menu-item-1'
          @click="clickhome"
          >
            <span class="menu-ico">🏠</span>
            <span class="menu-label">首页</span>
          </el-menu-item>

          <el-menu-item
            index="2"
            @click="clickbook"
            id='el-menu-item-2'
            >
              <span class="menu-ico">📚</span>
              <span class="menu-label">图书</span>
          </el-menu-item>

          <el-menu-item
            index="3"
            @click="clickcsdn"
            id='el-menu-item-3'
            >
              <span class="menu-ico">📝</span>
              <span class="menu-label">文篇</span>
          </el-menu-item>

          <el-menu-item
            index="4"
            @click="clickvideo"
            id='el-menu-item-4'
            class="menu-plain"
            >
              <span class="menu-label">视频</span>
          </el-menu-item>

          <el-menu-item
            index="5"
            @click="clickzhihu"
            id='el-menu-item-5'
            v-if="zhihushow&&notrelease"
            >
              <span class="menu-ico">💡</span>
              <span class="menu-label">知乎</span>
          </el-menu-item>

          <el-menu-item
            index="6"
            @click="clickthink"
            id='el-menu-item-6'
            >
              <span class="menu-ico">🧩</span>
              <span class="menu-label">片段</span>
          </el-menu-item>
          <el-menu-item
            index="7"
            @click="clicktravel"
            id='el-menu-item-7'
            class="menu-plain"
            >
              <span class="menu-label">游客</span>
          </el-menu-item>
          <el-menu-item
            index="8"
            @click="clickcommon"
            id='el-menu-item-8'
            >
              <span class="menu-ico">🧰</span>
              <span class="menu-label">常用</span>
          </el-menu-item>
          <el-menu-item
            index="9"
            @click="clickeverydayimg"
            id='el-menu-item-9'
            class="menu-plain"
            >
              <span class="menu-label">图片</span>
          </el-menu-item>
          <el-menu-item
            index="10"
            @click="clickadmin"
            id='el-menu-item-10'
            v-if="isAdmin"
            class="menu-plain"
            >
              <span class="menu-label">管理</span>
          </el-menu-item>
          <el-menu-item
            index="11"
            @click="clickusers"
            id='el-menu-item-11'
            class="menu-plain"
            >
              <span class="menu-label">用户</span>
          </el-menu-item>
        </el-menu>
        <!-- 访客数量：紧跟【用户】下方显示 -->
        <el-text class="visitor-stat">{{ TravelerStatistics }}</el-text>
        <!-- 在线人数：访客数量下方，绿色与访客数（白色）区分 -->
        <el-text class="online-stat">在线 {{ onlineCount }}</el-text>
        <!-- 底部工具组：主题按钮，flex 自动沉底 -->
        <div class="aside-footer">
          <el-button
            class="theme-btn"
            @click="themeChangevisible = true"
            type='primary'
            round
          >
            主题
          </el-button>
        </div>
        <el-dialog v-model="themeChangevisible" title="配置" width="min(720px, 94%)">
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
          <div style="margin-top:12px;border-top:1px solid #eee;padding-top:10px;">
            <span style="font-size:16px;font-weight: 600;">节日特效</span>
            <el-switch :model-value="true" disabled style="margin-left:12px;" />
            <span style="font-size:13px;font-weight: 300;color:#888;margin-left:8px;">节日期间默认开启，不可关闭</span>
            <div style="margin-top:6px;display:flex;align-items:center;gap:8px;">
              <span style="font-size:13px;color:#666;white-space:nowrap;">节日特效大小</span>
              <el-slider v-model="fxFestivalBoost" :min="0.5" :max="4" :step="0.1"
                show-input :show-input-controls="false" input-size="small"
                style="width:220px;margin-right:8px;" @change="applyFestivalBoost" />
              <span style="font-size:12px;color:#999;">倍，默认 1.9</span>
            </div>
            <div style="margin-top:8px;display:flex;align-items:center;gap:8px;">
              <span style="font-size:16px;font-weight: 600;">平日特效</span>
              <el-switch v-model="weekdayFxEnabled" @change="toggleWeekdayFx" style="margin-left:12px;" />
              <span style="font-size:13px;font-weight: 300;color:#888;margin-left:8px;">非节日期间的全屏特效，可关闭</span>
            </div>
            <div v-if="weekdayFxEnabled" style="margin-top:6px;display:flex;align-items:center;gap:8px;">
              <span style="font-size:13px;color:#666;white-space:nowrap;">平日特效大小</span>
              <el-slider v-model="fxWeekdayBoost" :min="0.5" :max="4" :step="0.1"
                show-input :show-input-controls="false" input-size="small"
                style="width:220px;margin-right:8px;" @change="applyWeekdayBoost" />
              <span style="font-size:12px;color:#999;">倍，默认 1.8</span>
            </div>
            <div v-if="weekdayFxEnabled" style="margin-top:8px;display:flex;flex-wrap:wrap;align-items:center;gap:8px;">
              <el-switch v-model="fxCustom.enabled" @change="applyFxCustom" active-text="手动指定特效" />
              <template v-if="fxCustom.enabled">
                <span style="font-size:13px;color:#666;">元素</span>
                <el-input-number v-model="fxCustom.element" :min="0" :max="7032" :step="1"
                  controls-position="right" size="small" style="width:110px;" @change="applyFxCustom" />
                <span style="font-size:12px;color:#999;">0=随机</span>
                <span style="font-size:13px;color:#666;margin-left:6px;">配色</span>
                <el-select v-model="fxCustom.palette" size="small" style="width:86px;" @change="applyFxCustom">
                  <el-option v-for="o in fxPaletteOptions" :key="o.value" :label="o.label" :value="o.value" />
                </el-select>
                <span style="font-size:13px;color:#666;">速度</span>
                <el-select v-model="fxCustom.speed" size="small" style="width:86px;" @change="applyFxCustom">
                  <el-option v-for="o in fxSpeedOptions" :key="o.value" :label="o.label" :value="o.value" />
                </el-select>
                <span style="font-size:13px;color:#666;">尺寸</span>
                <el-slider v-model="fxCustom.sizeNum" :min="0.5" :max="3" :step="0.1"
                  :disabled="fxCustom.sizeRandom" style="width:150px;" @change="applyFxCustom" />
                <span style="font-size:12px;color:#999;">{{ fxCustom.sizeNum }} 倍</span>
                <el-checkbox v-model="fxCustom.sizeRandom" @change="applyFxCustom" style="margin-left:4px;">随机</el-checkbox>
                <span style="font-size:13px;color:#666;">密度</span>
                <el-select v-model="fxCustom.density" size="small" style="width:86px;" @change="applyFxCustom">
                  <el-option v-for="o in fxDensityOptions" :key="o.value" :label="o.label" :value="o.value" />
                </el-select>
              </template>
            </div>
          </div>
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
        <el-dialog v-model="usersVisible" title="其他用户" width="min(760px, 94%)" class="dialog-scroll">
          <el-input
            v-model="userSearch"
            placeholder="输入完整邮箱或用户名精确查找"
            clearable
            style="margin-bottom:12px;"
          />
          <div style="display:flex;flex-wrap:wrap;gap:10px;">
            <el-button
              v-for="u in filteredUsersList"
              :key="u.mail"
              :type="u.mail === myMail ? 'primary' : 'default'"
              @click="gotoUserPage(u.uid || u.mail)"
            >
              {{ u.nickname }}（{{ maskMail(u.mail) }}）{{ u.mail === myMail ? ' - 我' : '' }}
            </el-button>
          </div>
          <div v-if="userSearch && filteredUsersList.length === 0" style="color:#999;">没有匹配的用户</div>
        </el-dialog>
        <el-dialog v-model="noticeVisible" title="管理员通知" width="min(640px, 94%)" class="dialog-scroll">
          <div style="font-size:12px;color:#999;margin-bottom:4px;">仅显示最近 {{ noticeMax }} 条通知</div>
          <div v-if="notices.length === 0" style="color:#999;">暂无通知</div>
          <div
            v-for="(n, i) in notices"
            :key="i"
            style="border-bottom:1px solid #eee;padding:8px 0;"
          >
            <div style="font-size:12px;color:#888;">{{ n.time }} · 来自 {{ n.from }}</div>
            <div style="white-space:pre-wrap;color:#222;">{{ n.content }}</div>
          </div>
          <template #footer>
            <el-button @click="clearNotices" v-if="notices.length > 0">清空通知</el-button>
            <el-button type="primary" @click="noticeVisible = false">关闭</el-button>
          </template>
        </el-dialog>
      </el-aside>
      <el-main id='elmain'>
        <!-- 用 path 作为 key：/testuser 与 /homepage 虽然都匹配同一个路由组件，
             但切换时必须重建组件，否则 mounted 不再执行、页面数据停留在上一个用户 -->
        <router-view :key="$route.path" />
      </el-main>
    </el-container>
    <!-- 回到顶部：站点为 body 整页滚动，用默认监听 -->
    <!-- 回到顶部按钮上移到看板郎挂件上方，避免右下角重叠遮挡 -->
    <el-backtop :right="30" :bottom="320" />
    <div class="footer-bar" style="color:#666;padding:3px 0;width:100%;background-color: #f5f5f5;">
      <a 
      type="primary"
      href="https://beian.mps.gov.cn/#/query/webSearch?code=33078202002770" 
      rel="noreferrer" 
      target="_blank">
        <el-image 
        style="width:20px;"
        :src="'/article/logobeian.png'"
        :zoom-rate="1.0"
        :max-scale="10"
        :min-scale="0.1"
        :preview-src-list="logobeian"
        :initial-index="4"
        fit="cover"
        />
      </a>
      <a
        v-if="footerGonganCode || footerGonganText"
        :href="'https://beian.mps.gov.cn/#/query/webSearch?code=' + footerGonganCode"
        style="margin-left:3px;line-height:20px;font-size:16px;"
        target="_blank"
      >
        {{ footerGonganText }}
      </a>
      <span v-if="footerCopyright" style="margin-left:20px;line-height:20px;font-size:16px;color:#000000;">
        {{ footerCopyright }}
      </span>
      <span v-if="footerIcpText" style="margin-left:20px;line-height:20px;font-size:16px;color:#000000;">
        ICP证:
      </span>
      <a v-if="footerIcpText" type="primary" href="https://beian.miit.gov.cn/"
          style="margin-left:3px;line-height:20px;font-size:16px;" target="_blank" >
        {{ footerIcpText }}
      </a>
      <span v-if="footerReportEmail" style="margin-left:20px;line-height:20px;font-size:16px;color:#000000;">
        举报邮箱：
        <a :href="'mailto:' + footerReportEmail" style="color:#0000ee;">{{ footerReportEmail }}</a>
      </span>
      <!-- 右下角日期时间：按 site_config.json 的 display_timezone_offset_seconds 换算 -->
      <span class="footer-clock" v-if="nowText">{{ nowText }}</span>
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
import getusername, { getCookieDays, initCookieDays } from '/src/common.js'
import { isAdminQuanxian } from '/src/common.js'
import Cookies from 'js-cookie'
import notrelease from "/src/main.js"
export default {
  name: 'app',
  data() {
    return {
      dialogRegisterVisible: false,
      postkey:"",
      checked1:true,
      cookieDays: 30,   // 登录凭据 cookie 有效期（天），mounted 时经 /csdn/getSiteConfig 读取统一配置
      mailCooldown: 60, // 验证码重发间隔（秒），同样来自统一配置
      // 页脚备案信息：默认值为 site_config.json 的当前文案兜底（配置接口不可用时照常显示）
      footerGonganCode: '33078202002770',
      footerGonganText: '浙公网安备33078202002770号',
      footerCopyright: '© 2024-2026 zoujiu.com.cn 版权所有',
      footerIcpText: '湘ICP备2024086536号-1',
      footerReportEmail: '1069679911@qq.com',
      // 页脚右下角日期时间：偏移量来自 site_config.json 的 display_timezone_offset_seconds（28800 = UTC+8）
      displayTimezoneOffset: 28800,
      nowText: '',
      clockTimer: null,
      // 平日（非节日）特效开关，存 localStorage；节日特效始终开启
      weekdayFxEnabled: true,
      // 节日特效整体放大倍数（存 localStorage，看板郎脚本读取），默认 1.9
      fxFestivalBoost: 1.9,
      // 平日特效整体放大倍数（存 localStorage，看板郎脚本读取），默认 1.8
      fxWeekdayBoost: 1.8,
      // 平日特效手动配置：元素 1~7032（0=随机）、配色/速度/密度留空=随机；
      // 尺寸为滑块连续倍率 sizeNum（0.5~3），勾选 sizeRandom 则随机档位
      fxCustom: { enabled: false, element: 0, palette: '', speed: '', sizeNum: 1.5, sizeRandom: false, density: '' },
      fxPaletteOptions: [
        { value: '', label: '随机' }, { value: 'red', label: '红' }, { value: 'gold', label: '金' },
        { value: 'pink', label: '粉' }, { value: 'blue', label: '蓝' }, { value: 'green', label: '绿' },
        { value: 'purple', label: '紫' }, { value: 'warm', label: '暖' }, { value: 'white', label: '白' },
      ],
      fxSpeedOptions: [
        { value: '', label: '随机' }, { value: 'xslow', label: '极慢' }, { value: 'slow', label: '慢' },
        { value: 'normal', label: '标准' }, { value: 'fast', label: '快' }, { value: 'xfast', label: '极快' },
      ],
      fxDensityOptions: [
        { value: '', label: '随机' }, { value: 'sparse', label: '稀疏' },
        { value: 'normal', label: '普通' }, { value: 'dense', label: '密集' }, { value: 'xdense', label: '超密' },
      ],
      themeChangevisible: false,
      ruleFormRef: "",
      sendret: true,
      notrelease: notrelease,
      dialogLoginVisible: false,
      forgetVisible: false,
      // 其他用户列表
      usersVisible: false,
      usersList: [],
      userSearch: '',
      myMail: '',
      // 登录者自己的 uid（URL 隐私方案：URL 只出现 uid，不出现邮箱）
      myUid: '',
      // 通知
      noticeVisible: false,
      notices: [],
      noticeMax: 200,
      unreadCount: 0,
      color1: 'rgb(136, 187, 250)',
      color2: 'rgb(86, 92, 99)',
      color3: 'rgb(255, 255, 255)',
      input1: "",
      input2: "",
      input3: "",
      returnback: true,
      // 登录态三态：null=尚未向服务端确认，true=已登录，false=未登录/凭据失效
      logined: null,
      TravelerStatistics:3900,
      // 当前同时在线人数（左侧栏绿色「在线 N」，60 秒轮询刷新）
      onlineCount: 0,
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
      isAdmin: false,
    }
  },
  computed: {
    // 用户列表过滤：隐私保护——仅支持「完整邮箱」或「完整用户名」精确匹配，
    // 不做模糊/包含匹配；默认（无关键词）不展示任何账号
    filteredUsersList() {
      const s = (this.userSearch || '').trim().toLowerCase();
      if (!s) {
        return [];
      }
      return this.usersList.filter((u) =>
        (u.mail && u.mail.toLowerCase() === s)
        || (u.nickname && String(u.nickname).toLowerCase() === s));
    },
  },
  watch: {
    // 路由切换（hash 变化）时刷新"返回"按钮状态，
    // 否则从他人页面回到自己页面后按钮状态会残留
    '$route'() {
      this.updateReturnButton();
      this.myMail = Cookies.get('mail') || '';
      // 转发链等 <a> 链接跳转到其他用户空间时整页刷新，
      // 避免 banner 标题/侧栏统计残留上一个用户的数据（与 gotoUserPage 强刷策略一致）
      this.reloadIfUserChanged();
    },
  },
  mounted() {
    // if(this.first) {
    // let url = document.URL;
    // this.clickhome();
    this.loading();
    // 主题不要求登录，按"页面主人"应用：裸域名进入时路由初始跳转（/ → /#/homepage@gmail.com）
    // 尚未完成，document.URL 还不包含主人段，此时上报会被后端按匿名兜底返回默认主题；
    // 必须等路由就绪（isReady）后再取主题
    this.$router.isReady().then(() => { this.getColor(); });
    this.loadCookieConfig();
    this.startClock();
    // 恢复平日特效开关（默认开启）、大小滑块与手动配置
    try { this.weekdayFxEnabled = localStorage.getItem('waifu-fx-weekday') !== '0' } catch (e) {}
    try {
      const boost = parseFloat(localStorage.getItem('waifu-fx-festival-boost'));
      if (boost >= 0.5 && boost <= 4) this.fxFestivalBoost = boost;
    } catch (e) {}
    try {
      const boost = parseFloat(localStorage.getItem('waifu-fx-weekday-boost'));
      if (boost >= 0.5 && boost <= 4) this.fxWeekdayBoost = boost;
    } catch (e) {}
    try {
      const raw = localStorage.getItem('waifu-fx-custom');
      if (raw) {
        const cfg = Object.assign({}, this.fxCustom, JSON.parse(raw));
        // 旧版配置兼容：原「尺寸」下拉是小/中/大字符串（留空=随机），迁移为滑块数值
        if (typeof cfg.sizeNum !== 'number') {
          const legacy = { small: 0.7, normal: 1, large: 1.45 };
          cfg.sizeNum = legacy[cfg.size] || 1.5;
          cfg.sizeRandom = !cfg.size;   // 原来留空就是随机
        }
        this.fxCustom = cfg;
      }
    } catch (e) {}
    this.myMail = Cookies.get('mail') || '';
    this.updateReturnButton();
    this.loadNotices(false);
    // 在线人数：立即拉一次 + 每 60 秒轮询（失败静默，保持上次值）
    this.refreshOnline();
    this.onlineTimer = setInterval(() => { this.refreshOnline(); }, 60000);
    //   this.first = false;
    // }
  },
  beforeUnmount() {
    if (this.clockTimer) {
      clearInterval(this.clockTimer);
      this.clockTimer = null;
    }
    if (this.onlineTimer) {
      clearInterval(this.onlineTimer);
      this.onlineTimer = null;
    }
  },
  methods: {
    // 拉取当前同时在线人数（/csdn/online_count 只读内存计数，无鉴权无文件 IO）
    async refreshOnline() {
      try {
        const instance = axios.create({ baseURL: '/csdn/online_count', timeout: 10000 });
        const response = await instance({
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
          data: {},
        });
        if (response.data && response.data.ret === 1 && typeof response.data.online === 'number') {
          this.onlineCount = response.data.online;
        }
      } catch (e) {
        // 静默失败：保持上次值，下一轮再试
      }
    },
    // 从后端统一配置读取浏览器侧可调参数；失败时保持缺省值
    async loadCookieConfig() {
      // cookie 有效期由 common.js 的 initCookieDays 统一拉取（localStorage + 模块级缓存），
      // 全站组件经 getCookieDays() 读取，避免各处硬编码 30 天
      const cfg = await initCookieDays();
      if (cfg) {
        const cd = parseInt(cfg.mail_resend_cooldown_seconds);
        if (!isNaN(cd) && cd > 0) {
          this.mailCooldown = cd;
        }
        // 页脚备案信息（site_config.json 配置，空值隐藏对应片段）
        for (const [key, prop] of [
          ['footer_gongan_code', 'footerGonganCode'],
          ['footer_gongan_text', 'footerGonganText'],
          ['footer_copyright', 'footerCopyright'],
          ['footer_icp_text', 'footerIcpText'],
          ['footer_report_email', 'footerReportEmail'],
        ]) {
          if (cfg[key] !== undefined && cfg[key] !== null && cfg[key] !== '') {
            this[prop] = cfg[key];
          }
        }
        // 页脚时钟的显示时区偏移（秒），改配置后刷新页面即生效
        const tz = parseInt(cfg.display_timezone_offset_seconds);
        if (!isNaN(tz)) {
          this.displayTimezoneOffset = tz;
          this.nowText = this.formatClock();
        }
      }
      this.cookieDays = getCookieDays();
    },
    // 页脚右下角的时间：服务器时间戳 + 配置时区偏移，按 24 小时制输出【2026-11-01 10 周日】
    formatClock() {
      const t = new Date(Date.now() + this.displayTimezoneOffset * 1000);
      const pad = n => String(n).padStart(2, '0');
      const week = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][t.getUTCDay()];
      return `【${t.getUTCFullYear()}-${pad(t.getUTCMonth() + 1)}-${pad(t.getUTCDate())} ${pad(t.getUTCHours())} ${week}】`;
    },
    startClock() {
      // 右下角只显示到小时，每 60 分钟刷新一次即可；刷新页面会重新计算并重置计时
      if (this.clockTimer) clearInterval(this.clockTimer);
      this.nowText = this.formatClock();
      this.clockTimer = setInterval(() => { this.nowText = this.formatClock(); }, 60 * 60 * 1000);
    },
    // 平日特效开关：写入 localStorage 并通知看板郎脚本立即生效（节日特效不受影响）
    toggleWeekdayFx(val) {
      try { localStorage.setItem('waifu-fx-weekday', val ? '1' : '0') } catch (e) {}
      window.dispatchEvent(new CustomEvent('waifu-fx-config'));
    },
    // 保存节日特效放大倍数并立即生效
    applyFestivalBoost(val) {
      const v = Math.min(4, Math.max(0.5, parseFloat(val) || 1.9));
      try { localStorage.setItem('waifu-fx-festival-boost', String(v)) } catch (e) {}
      window.dispatchEvent(new CustomEvent('waifu-fx-config'));
    },
    // 保存平日特效整体放大倍数并立即生效（与节日滑块同机制）
    applyWeekdayBoost(val) {
      const v = Math.min(4, Math.max(0.5, parseFloat(val) || 1.8));
      try { localStorage.setItem('waifu-fx-weekday-boost', String(v)) } catch (e) {}
      window.dispatchEvent(new CustomEvent('waifu-fx-config'));
    },
    // 保存手动特效配置（元素/配色/速度/尺寸/密度）并立即生效
    applyFxCustom() {
      try { localStorage.setItem('waifu-fx-custom', JSON.stringify(this.fxCustom)) } catch (e) {}
      window.dispatchEvent(new CustomEvent('waifu-fx-config'));
    },
    // 根据"当前登录账号"与"当前页面主人"决定是否显示返回按钮
    updateReturnButton() {
      // loading() 已向服务端确认未登录/登录失效时，残留的 mail cookie 会让下面的
      // cookie 判断误显返回按钮（点击后无处可回、表现为"点了没反应"），直接隐藏
      if (this.logined === false) {
        this.returnback = true;
        return;
      }
      const myMail = Cookies.get('mail') || '';
      const pathOnly = (window.location.pathname.replace(/\/+$/, '') || '/');
      let urlmail = '';
      if (pathOnly !== '/') {
        urlmail = pathOnly.split('/')[1] || '';
      } else {
        const hash = window.location.hash.replace(/^#\/?/, '');
        urlmail = hash.split('/').filter(Boolean)[0] || '';
      }
      // 未登录，或在看自己的页面：不需要返回按钮。
      // uid 化后 URL 用户段是 36 位数字 uid，需同时与邮箱和 uid 比较
      // （myUid 首帧可能为空，用 localStorage 缓存兜底，避免闪烁误显）
      const myUid = this.myUid || localStorage.getItem('my_uid') || '';
      this.returnback = !(myMail && urlmail && urlmail !== myMail && urlmail !== myUid);
    },
    // 解析当前 hash 路由中的"用户段"（跳过模块前缀），失败返回空串
    findUrlUser() {
      const segs = window.location.hash.replace(/^#\/?/, '').split('?')[0].split('/').filter(Boolean);
      const skip = ['think', 'csdn', 'book', 'zhihu', 'video', 'travel', 'commonuse',
        'everydayimg', 'admin', 'people', 'article', 'markdown_detail', 'post_article', 'detail'];
      for (const s of segs) {
        if (skip.indexOf(s) < 0) {
          return s;
        }
      }
      return '';
    },
    // 用户空间变化时整页刷新，保证 banner/侧栏与 URL 一致
    reloadIfUserChanged() {
      const user = this.findUrlUser();
      const pre = Cookies.get('premail');
      if (!user || !pre || user === pre) {
        return;
      }
      // 先同步再刷新：旧 cookie（如历史前缀 'homepage'）与新全邮箱 URL 不一致时，
      // 只触发一次 reload 而不是无限循环。
      // expiresdate 必须在本方法内定义（与 login/logout 一致），
      // 否则引用未定义变量抛 ReferenceError：premail 不再更新、reload 不执行，
      // 强刷机制整体失效（表现为 URL 变了但页面数据停留在上一个用户空间）
      const expiresdate = new Date(new Date().getTime() + this.cookieDays * 24 * 60 * 60 * 1000);
      Cookies.set('premail', user, { expires: expiresdate });
      window.location.reload();
    },
    // 打开"其他用户"列表
    async clickusers() {
      this.myMail = Cookies.get('mail') || '';
      this.userSearch = '';
      const instance = axios.create({ baseURL: '/csdn/userlist', timeout: 20000 });
      await instance({
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
        data: {},
      }).then((response) => {
        if (response.data && response.data.ret === 1) {
          this.usersList = response.data.users || [];
          this.usersVisible = true;
        } else {
          ElMessage.error('获取用户列表失败！');
        }
      }).catch(() => {
        ElMessage.error('网络错误，获取用户列表失败！');
      });
    },
    // 跳转到指定用户的个人主页
    // 用户切换面板隐私保护：仅展示层把邮箱前缀（@ 之前的部分，含数字与字母）
    // 整体替换为 ****，只保留 @域名；搜索匹配、点击跳转、key 绑定仍用真实邮箱；
    // 管理员页面不受影响
    maskMail(mail) {
      return String(mail || '').replace(/[^@]+/, '****');
    },
    async gotoUserPage(mail) {
      if (!mail) {
        return;
      }
      this.usersVisible = false;
      // 已在目标主页时不重复跳转/刷新
      if (this.$route.path === '/' + mail) {
        this.updateReturnButton();
        return;
      }
      await this.$router.push({ path: '/' + mail });
      // 链接变化后强制整页刷新，确保页面内容与 URL 一致（整页刷新会按新路由重新挂载）
      window.location.reload();
    },
    // 拉取自己的通知（时间倒序），并计算未读数
    async loadNotices(markRead) {
      const mail = Cookies.get('mail');
      const password = Cookies.get('password');
      if (!mail || !password) {
        this.notices = [];
        this.unreadCount = 0;
        return;
      }
      const instance = axios.create({ baseURL: '/csdn/get_notice', timeout: 20000 });
      await instance({
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
        data: { mail, password },
      }).then((response) => {
        if (response.data && response.data.ret === 1) {
          // 后端已按时间倒序并按配置 notice_display_max 截取，这里再排一次保证稳定
          const list = (response.data.notices || []).slice();
          list.sort((a, b) => String(b.time).localeCompare(String(a.time)));
          this.noticeMax = response.data.max || 200;
          this.notices = list;
          const seen = localStorage.getItem('noticeSeen_' + mail) || '';
          this.unreadCount = list.filter((n) => String(n.time) > seen).length;
          if (markRead) {
            const newest = list.length ? String(list[0].time) : seen;
            localStorage.setItem('noticeSeen_' + mail, newest);
            this.unreadCount = 0;
          }
        }
      }).catch(() => {});
    },
    async openNotices() {
      this.noticeVisible = true;
      await this.loadNotices(true);
    },
    async clearNotices() {
      const instance = axios.create({ baseURL: '/csdn/clear_notice', timeout: 20000 });
      try {
        const response = await instance({
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
          data: { mail: Cookies.get('mail'), password: Cookies.get('password') },
        });
        if (response.data && response.data.ret === 1) {
          this.notices = [];
          this.unreadCount = 0;
          // 临时清空（notice_clear_temporary=true）时磁盘数据保留，刷新后通知恢复
          if (response.data.temporary) {
            ElMessage('已清空本次显示，刷新页面后通知仍可见');
          } else {
            ElMessage('通知已清空');
          }
        } else {
          ElMessage.error('清空失败，请重新登录后重试');
        }
      } catch (e) {
        ElMessage.error('清空失败，请重试');
      }
    },
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
              let ran = Math.floor(Math.random() * 124);
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
        baseURL: '/csdn/getThemeColor',
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
        baseURL: '/csdn/themeChange',
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
        baseURL: '/csdn/themeChange',
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
          baseURL: '/csdn/register',
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
      // 站长公共主页全邮箱标识；用全邮箱匹配可避免误伤前缀同名用户（如 homepage2@x.com）
      let ind = urlrul.indexOf("/homepage@gmail.com");
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
      // 登录态失效但 mail cookie 仍残留时，旧逻辑会试图跳回"自己主页"，
      // 随即被 loading() 的未登录兜底弹回当前公共主页，表现为"点了返回没反应"。
      // 这里显式识别失效：清掉残留凭据、复位按钮组并回公共主页，提示重新登录。
      if(!gu || !(gu.ret > 0) || !gu.mail) {
        this.logined = false;
        Cookies.remove("mail");
        Cookies.remove("password");
        Cookies.remove("username");
        Cookies.remove("quanxian");
        this.isAdmin = false;
        this.myMail = "";
        this.returnback = true;
        this.logoutbutton = true;
        this.loginbutton = false;
        this.registerbutton = false;
        ElMessage.warning("登录状态已失效，请重新登录");
        // 回公共主页：站长 uid，取不到回退站长邮箱
        const ownerhome = '/' + ((gu && gu.owneruid) || localStorage.getItem('site_owner_uid') || 'homepage@gmail.com');
        if(this.$route.path !== ownerhome) {
          await this.$router.push({ path: ownerhome });
        }
        return;
      }
      // 优先用服务端解析出的登录账号，其次退回 Cookie；都没有则回公共主页。
      // 原来直接用 Cookies.get("mail")，未登录/登录态失效时会跳到 /#/undefined。
      // uid 化后跳转目标用自己的 uid（后端 login/getusername 返回），避免 URL 泄漏邮箱
      const myMail = gu.mail || Cookies.get('mail') || '';
      const target = myMail ? '/' + (gu.uid || this.myUid || localStorage.getItem('my_uid') || myMail)
                            : '/' + (gu.owneruid || localStorage.getItem('site_owner_uid') || 'homepage@gmail.com');
      // 已在目标主页时不重复跳转/刷新
      if (this.$route.path === target) {
        this.updateReturnButton();
        return;
      }
      await this.$router.push({ path: target });
      // 链接变化后强制整页刷新，确保页面内容与 URL 一致（整页刷新会按新路由重新挂载）
      window.location.reload();
    },
    async loading() {
      Cookies.remove("mailsend");
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
      // URL 隐私方案：premail 存 URL 原始用户段（uid 形态存 uid），
      // 与 reloadIfUserChanged 比较的 findUrlUser() 语义一致，否则会无限刷新。
      // 旧邮箱形态 URL 由后端 urluid 升级为 uid 后再比较，推动 premail 自然迁移
      let rawseg = gu.urluid || gu.urlmail;
      // 同步缓存：登录者自己的 uid / 站长 uid（裸域名 redirect 用）
      if (gu && gu.uid) {
        this.myUid = gu.uid;
        localStorage.setItem('my_uid', gu.uid);
      }
      if (gu && gu.owneruid) {
        localStorage.setItem('site_owner_uid', gu.owneruid);
      }
      if(gu && rawseg) {
        let expiresdate = new Date(new Date().getTime() + this.cookieDays * 24 * 60 * 60 * 1000);
        if(rawseg!=premail) {
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
        Cookies.set("premail", rawseg, { expires: expiresdate });
      }
      // URL 隐私：邮箱形态 URL（如 /#/homepage@gmail.com）已彻底失效——
      // 后端不再把邮箱段解析为用户（findurlmail 返回空），这里直接同文档
      // replace 到站长 uid 主页，旧邮箱链接不再进入对应用户的页面。
      // uid 形态不含 @，不会再次触发本分支（无循环）
      const curseg = this.findUrlUser()
        || (window.location.pathname.replace(/^\/+/, '').split('/')[0] || '');
      if (gu && curseg && String(curseg).indexOf('@') >= 0) {
        const target = gu.owneruid || localStorage.getItem('site_owner_uid') || '';
        if (target) {
          const curpath = window.location.pathname.replace(/\/+$/, '') || '/';
          location.replace(curpath + '#/' + target);
          // 只改 hash 不会重新加载页面：主题/看板郎在脚本启动时已按"无主人"的旧 URL
          // 取过数据，必须整页刷新一次，让新地址重新初始化
          window.location.reload();
          return;
        }
        // 拿不到站长 uid（后端未升级到 uid 方案/接口异常）：不再跳转，
        // 避免与路由 redirect 形成 /#/↔ /#/邮箱 的无限循环；
        // 页面按匿名继续渲染，等后端正常后自然恢复
      }
      if(gu && gu.ret > 0) {
        this.logined = true;
        this.nicknamestart = gu.username;
        let username = gu.username;
        this.isAdmin = isAdminQuanxian(gu.quanxian);
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
        // uid 化后 URL 不再含邮箱文本，改用后端还原的页面主人邮箱判定
        if(gu.urlmail != 'homepage@gmail.com') {
          this.zhihushow = false;
        }

        let img = document.getElementById("APPgeren");
        // console.log(img);
        if(img && gu.urlmail != 'homepage@gmail.com') {
          img.hidden = true;
        }
        // console.log(gu);
        if(gu.ret > 0 && gu.mail && gu.mail!=gu.urlmail) {
          // console.log(222222, gu);
          this.returnback = false;
          this.loginbutton = true;
          // 有效登录（含 ret=2 看他人主页）必须显示登出：本分支是 ret=2 时
          // 唯一会碰到 logoutbutton 的地方，缺了这行登出按钮保持初始隐藏，
          // 造成"他人主页只有返回、没有登出"
          this.logoutbutton = false;
          this.registerbutton = true;
        }
        // 与主机无关的判断：当前地址是否为该用户的根页面（如 /<uid> 或 /#/<uid>#/）。
        // uid 化后用 URL 原始段（uid 形态）比较与跳转，避免把邮箱写回地址栏
        let rootseg = gu.urluid || gu.urlmail;
        let pathonly = window.location.pathname.replace(/\/+$/, '') || '/';
        let hashnow = window.location.hash;
        if(
          pathonly==('/' + rootseg)
          || (pathonly=='/' && (hashnow==('#/' + rootseg + '#/') || hashnow==('#/' + rootseg)))
        ) {
          this.$router.push({ path: '/' + rootseg});
        }
      } else {
        // 未登录/登录失效：复位按钮组（返回隐藏、登录/注册显示），清掉铃铛依赖的
        // myMail。注意不能在这里清登录 cookie——短名守卫场景（如 #/zj）下
        // getusername 不做鉴权直接返回 ret=0，误清会丢掉有效登录态；
        // cookie 残留导致的失效清理放在 returnbackhome 的显式失效分支里。
        this.logined = false;
        this.returnback = true;
        this.logoutbutton = true;
        this.loginbutton = false;
        this.registerbutton = false;
        this.myMail = "";
        // 未登录时统一跳转到公共主页（站长 uid，取不到回退站长邮箱）。
        // 本项目是 hash 路由，必须带上 "#"，否则每次加载都会再次触发本条跳转导致页面无限刷新闪烁。
        // 线上部署时服务器会把 "/" 302 到 "/homepage"（且 URL 的 # 片段不会发给服务器）：
        // 若这里写死固定串，浏览器会跨文档请求 "/"，被服务器再次 302 回
        // "/homepage"，应用加载后本分支再次执行 —— 无限循环。
        // 改为在「当前 pathname」上设置 hash（同文档导航，不经过服务器），本地（/）与线上（/homepage）都一次到位。
        const owneruid = (gu && gu.owneruid) || localStorage.getItem('site_owner_uid') || 'homepage@gmail.com';
        const curpath = window.location.pathname.replace(/\/+$/, '') || '/';
        const onPublicHome = (curpath === '/' || curpath === '/homepage')
          && window.location.hash === '#/' + owneruid;
        if(!onPublicHome) {
          location.replace(curpath + '#/' + owneruid);
          // 同上：hash 变更不触发整页加载，主题与看板郎会停留在"无主人"的默认值，
          // 刷新一次让新地址（站长 uid）重新初始化
          window.location.reload();
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
        baseURL: '/csdn/sendverify',
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
        else if(this.sendret==4){
          // 服务端限流：同邮箱 60 秒 1 封 / 同 IP 每小时 10 封
          ElMessage("发送太频繁了，请稍后再试！");
        }
        else if(!this.sendret){
          ElMessage("send mail failed, please check email address！");
        } else {
          ElMessage("已经发送到邮箱了，有效期1天！");
        }
      });
    },
    sleep(delay) { 
      let num = Cookies.get("mailsendNum");
      if(!num || num <= 0) {
        Cookies.remove("mailsend");
        let mailconfirmbutton = document.getElementById("mailconfirmbutton");
        let mailsend = mailconfirmbutton.getElementsByTagName("span")[0];
        mailsend.innerHTML = "<span> 点击发送邮箱验证 </span>";
        return;
      }
      // console.log(delay, num);
      setTimeout(()=>{
        let mailconfirmbutton = document.getElementById("mailconfirmbutton");
        let mailsend = mailconfirmbutton.getElementsByTagName("span")[0];
        // console.log(1, mailsend, mailsend.innerText);
        let remain = parseInt( (num * delay) / 1000 );
        mailsend.innerHTML = "<span> 点击发送邮箱验证 " + remain.toString() + " </span>";
        // console.log(2, mailsend, mailsend.innerText.toString(), remain.toString());
        num = num - 1;
        let expiresdate = new Date(new Date().getTime() + num * 1000);
        Cookies.set("mailsendNum", num, { expires: expiresdate });
        this.sleep(delay);
      }, delay); 
    },
    async SendVerify() {
      if( !this.mailChange() ) {
        ElMessage("邮箱格式不对不能发送！");
        return;
      }
      if( !this.pFirstChange() || !this.pSecondChange() || !this.nicknameChange() ) {
        return;
      }
      if(Cookies.get("mailsendNum") && Cookies.get("mailsendNum")>=0) {
        let n = parseInt(Cookies.get("mailsendNum"));
        ElMessage(n.toString() + "s后可以再次发送!");
        return;
      }
      // 重发间隔统一配置在 mysite/site_config.json 的 mail_resend_cooldown_seconds（+3s 缓冲）
      let expiresdate = new Date(new Date().getTime() + (this.mailCooldown + 3) * 1000);
      Cookies.set("mailsendNum", this.mailCooldown, { expires: expiresdate });
      const instance = axios.create({
        baseURL: '/csdn/sendverify',
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
        else if(this.sendret==3){
          ElMessage("login administer's email address 1069679911@qq.com failed! please connect administer with 1069679911@qq.com");
        }
        else if(this.sendret==4){
          // 服务端限流：同邮箱 60 秒 1 封 / 同 IP 每小时 10 封
          ElMessage("发送太频繁了，请稍后再试！");
        }
        else if(this.sendret==0){
          ElMessage("send mail failed, please check email address！");
        } else {
          ElMessage("已经发送到邮箱了，有效期1天！");
        }
      });
      this.sleep(1000, 0); //ms
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
        if(pass[i]>='0' && pass[i]<='9') {
          digit = true;
        }
        // if(sl.indexOf(pass[i]) > 0 || (sl.indexOf(pass[i])==0 && pass[i]==".")) {
        //   // console.log(pass, pass[i]);
        //   special = true;
        // }
      }
      if(alpha && digit) {
      // && special) {
        return true;
      } else {
        ElMessage("需要同时包含数字和英文字母！");
        return false;
      }
    }, 
    nicknameChange() {
      if(this.ruleForm.nickname.length==0) {
        ElMessage("昵称至少包含一个字符，当前昵称是空的！");
        return false;
      }
      return true;
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
      let r = this.ruleForm.email;
      // 用户名（@前的部分）至少7个字符：系统会把 <=6 的短名按匿名访客处理，短名注册后将无法登录
      let at = r.indexOf("@");
      if( at < 7 ) {
        ElMessage("用户名（@前的部分）至少7个字符，且需包含@！");
        return false;
      }
      return true;
    },
    async submitForm() {
      if(this.mailChange() && this.pFirstChange() && 
        this.pSecondChange() && this.nicknameChange() 
        && this.sendret){
        ElMessage("passed!");
        const instance = axios.create({
          baseURL: '/csdn/register',
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
          } else if(ret==-7) {
            // 服务端防攻击限流（每 IP 注册频次 / 每邮箱验证码校验次数）
            ElMessage.error(response.data.msg || "操作过于频繁，请稍后再试！");
          } else {
            ElMessage("验证失败了的！");
          }
        });
      } else {
        ElMessage('请检查password和邮箱地址的!');
      }
    },
    async submitLoginForm() {
      // 密码先做 sha256 再传输（与 member.txt 存储值一致；后端登录接口不再二次哈希）
      const textEncoder = new TextEncoder();
      const message = textEncoder.encode(this.LoginForm.password);
      const messageDigest = await crypto.subtle.digest('SHA-256', message);
      const hexDigest = Array.from(new Uint8Array(messageDigest))
        .map((x) => x.toString(16).padStart(2, '0'))
        .join('');
      const instance = axios.create({
        baseURL: '/csdn/login',
        timeout: 20000,
      });
      // console.log(this.search_param);
      await instance({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        data: {'LoginForm' : {'username': this.LoginForm.username, 'password': hexDigest}},
      }).then(async (response) => {
        let result = response.data;
        // 服务端防爆破限流：每 IP 10 分钟最多 20 次登录尝试
        if (result.ret === -50) {
          ElMessage.error(result.msg || "登录尝试过于频繁，请 10 分钟后再试！");
          return;
        }
        if(result.ret) {
          let mail = result.mail;
          let password = result.password;
          let username = result.username;
          ElMessage("登录成功了的!");
          // cookie 有效期统一配置在 mysite/site_config.json 的 cookie_login_days
          let expiresdate = new Date(new Date().getTime() + this.cookieDays * 24 * 60 * 60 * 1000);
          // console.log('99999999999', document.cookie, mail, password);
          Cookies.set("mail", mail, { expires: expiresdate });
          Cookies.set("password", password, { expires: expiresdate });
          Cookies.set("username", username, { expires: expiresdate });
          let qx = parseInt(result.quanxian);
          if(!isNaN(qx)) {
            Cookies.set("quanxian", qx, { expires: expiresdate });
            this.isAdmin = isAdminQuanxian(qx);
          }

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
          // let LOGINVisible = true;
          // this.REGISTERVisible = true;
          this.logined = true;
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
          // 仅改 hash 的 location.replace 不会整页刷新：会先走 SPA 导航，
          // 再被 $route 监听里的 reloadIfUserChanged 强制 reload，双重导航卡死页面。
          // 改为纯 SPA 跳转并提前同步 premail，避免触发强制 reload。
          // uid 化后跳转目标用登录响应里的 uid，URL 不再暴露邮箱
          const myuid = result.uid || localStorage.getItem('my_uid') || mail;
          if (result.uid) {
            localStorage.setItem('my_uid', result.uid);
            this.myUid = result.uid;
          }
          Cookies.set("premail", myuid, { expires: expiresdate });
          await this.$router.push({ path: '/' + myuid });
          this.returnback = true;
          window.location.reload();
        } else {
          ElMessage("登录失败了的！");
        }
      });
      // this.$alert("登录以后请点击上方的【重置】按钮，获取个人资料！");
    },
    async logout() {
      Cookies.remove("mail");
      Cookies.remove("password");
      Cookies.remove("username");
      Cookies.remove("quanxian");
      this.isAdmin = false;
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

      this.logined = false;
      let expiresdate = new Date(new Date().getTime() + getCookieDays() * 24 * 60 * 60 * 1000);
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
      // 恢复 banner 标题，避免登出后仍显示上一用户的昵称
      this.nicknamestart = "邹九";
      this.zhihushow = true;
      
      // let zhihu = "<el-menu-item @click=\"clickzhihu\" id=\'el-menu-item-6\'> 知乎文篇 </el-menu-item>";
      // let all = document.getElementById("elaside");
      // let allchild = all.children[0];
      // allchild.insertAdjacentHTML(4, zhihu);
      let img = document.getElementById("APPgeren");
      if(img) {
        img.hidden = false;
      }
      this.returnback = true;
      // 登出后回到公共主页：纯 SPA 跳转并同步 premail，
      // 避免 hash 导航后再被 reloadIfUserChanged 强制 reload 卡死。
      // uid 化后回站长 uid 页面，并清掉自己的 uid 缓存
      localStorage.removeItem('my_uid');
      this.myUid = '';
      const owneruid = localStorage.getItem('site_owner_uid') || 'homepage@gmail.com';
      Cookies.set("premail", owneruid, { expires: expiresdate });
      await this.$router.push({ path: '/' + owneruid });
      // 背景配色/主题等页面状态是按登录用户渲染的，SPA 路由切换不会重置；
      // premail 已同步为公共主页，这里整页刷新一次即可恢复公共默认外观
      // window.location.replace(window.location.href);
      window.location.reload();
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
      this.getColor();
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
        // uid 化后用 URL 原始段（uid）建链接，避免把邮箱写回地址栏
        this.$router.push({ path: '/zhihu/'+(gu.urluid || gu.urlmail), query:{"currentpage": 1, "pagesize":30}})
      } else {
        this.$router.push({ path: '/zhihu/'+(gu.owneruid || localStorage.getItem('site_owner_uid') || 'homepage@gmail.com')}); //, query:{"currentpage": 1, "pagesize":20}
      }
    },
    async clickhome() {
      let gu, index;
      this.getColor();
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
        this.$router.push({ path: '/'+(gu.urluid || gu.urlmail)});
      } else {
        this.$router.push('/' + (gu.owneruid || localStorage.getItem('site_owner_uid') || 'homepage@gmail.com'));
      }
    },
    async clickbook() {
      let gu, index;
      this.getColor();
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
        this.$router.push({ path: '/book/'+(gu.urluid || gu.urlmail)});
      } else {
        this.$router.push({ path: '/book/'+(gu.owneruid || localStorage.getItem('site_owner_uid') || 'homepage@gmail.com')});
      }
    },
    async clickcsdn() {
      this.getColor();
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
        this.$router.push({ path: '/csdn/'+(gu.urluid || gu.urlmail), query:{"currentpage": 1, "pagesize":30}})
      } else {
        this.$router.push({ path: '/csdn/'+(gu.owneruid || localStorage.getItem('site_owner_uid') || 'homepage@gmail.com')}); //, query:{"currentpage": 1, "pagesize":20}
      }
    },
    async clickthink() {
      let gu, index;
      this.getColor();
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
        this.$router.push({ path: '/think/'+(gu.urluid || gu.urlmail), query:{"currentpage": 1, "pagesize":9}});
      } else {
        this.$router.push({ path: '/think/'+(gu.owneruid || localStorage.getItem('site_owner_uid') || 'homepage@gmail.com')});
      }
    },
    async clickvideo() {
      let gu, index;
      this.getColor();
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
        this.$router.push({ path: '/video/'+(gu.urluid || gu.urlmail), query:{"currentpage": 1, "pagesize":6}});
      } else {
        this.$router.push({ path: '/video/'+(gu.owneruid || localStorage.getItem('site_owner_uid') || 'homepage@gmail.com')});
      }
    },
    async clicktravel() {
      let gu, index;
      this.getColor();
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
        this.$router.push({ path: '/travel/'+(gu.urluid || gu.urlmail), query:{"currentpage": 1, "pagesize":30}});
      } else {
        this.$router.push({ path: '/travel/'+(gu.owneruid || localStorage.getItem('site_owner_uid') || 'homepage@gmail.com')});
      }
    },
    async clickcommon() {
      let gu, index;
      this.getColor();
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
        this.$router.push({ path: '/commonuse/'+(gu.urluid || gu.urlmail)});
      } else {
        this.$router.push({ path: '/commonuse/'+(gu.owneruid || localStorage.getItem('site_owner_uid') || 'homepage@gmail.com')});
      }
    },
    async clickeverydayimg() {
      let gu, index;
      this.getColor();
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      if(gu && gu.ret > 0) {
        this.$router.push({ path: '/everydayimg/'+(gu.urluid || gu.urlmail)});
      } else {
        this.$router.push({ path: '/everydayimg/'+(gu.owneruid || localStorage.getItem('site_owner_uid') || 'homepage@gmail.com')});
      }
    },
    async clickadmin() {
      let gu;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      if(gu && gu.ret > 0 && isAdminQuanxian(gu.quanxian)) {
        this.$router.push({ path: '/admin/' + (gu.urluid || gu.urlmail) });
      } else {
        ElMessage("只有管理员才能访问管理页面！");
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
  /* 高度自适应：窄视口 toolbar 换行时 header 跟着变高，
     避免固定 50px 导致第二行按钮溢出、遮挡下方内容 */
  height: auto;
  min-height: 50px;
}
.layout-container-demo .el-aside {
  /* color: var(--el-text-color-primary); */
  /* background: var(--el-color-primary-light-3); */
  width:10vh;
  min-width:76px;
  font-size:30px;
  background-color:rgb(136, 187, 250);
  /* background-image: url('/article/themeImg/anhei/csdn_anHei_vertical.png'); */
  /* flex 纵向布局：菜单在上、底部工具组自动沉底；矮屏可滚动不溢出 */
  display:flex;
  flex-direction:column;
  overflow-y:auto;
  overflow-x:hidden;
  transition:background-color .3s;
}
.layout-container-demo .el-menu {
  /* 菜单容器透明，让主题系统给 #elaside 换的底色透出来 */
  --el-menu-bg-color: transparent;
  --el-menu-text-color: #ffffff;
  --el-menu-active-color: #337ecc;
  --el-menu-hover-bg-color: rgba(255,255,255,0.28);
  border-right: none;
  background: transparent;
  padding-top:10px;
}
.layout-container-demo .el-main {
  padding: 0;
  background-color: #ffffff;
}
/* 菜单项：主题色上的半透明胶囊（毛玻璃感），图标在上文案在下 */
.layout-container-demo .el-menu-item {
  display:flex;
  flex-direction:column;
  justify-content:center;
  align-items:center;
  gap:2px;
  height:52px;
  margin:5px 8px;
  padding:0 !important;
  border-radius:12px;
  font-size:16px;
  color:#ffffff;
  /* !important：主题系统会用 JS 行内样式给菜单项上纯色，这里统一为半透明胶囊，
     让 #elaside 的主题底色透出来（纯色/节日/自定义三套主题都一致生效） */
  background-color:rgba(255,255,255,0.14) !important;
  font-weight: 700;
  line-height:1.2;
  text-shadow:0 1px 2px rgba(0,0,0,0.18);
  transition:background-color .25s, transform .25s, box-shadow .25s;
}
.layout-container-demo .el-menu-item .menu-ico {
  font-size:22px;
  line-height:1;
  filter:drop-shadow(0 1px 1px rgba(0,0,0,0.2));
}
.layout-container-demo .el-menu-item .menu-label {
  letter-spacing:2px;
  margin-left:2px; /* 抵消 letter-spacing 造成的视觉偏移 */
}
/* 纯文字菜单项：不要图标、不要胶囊容器，直接文字显示（视频/游客/图片/管理/用户）
   压缩占用高度紧挨上下项；悬浮/激活时底部出现色条 */
.layout-container-demo .el-menu-item.menu-plain {
  background-color:transparent !important;
  text-shadow:none;
  color:rgba(255,255,255,0.88);
  height:30px;
  margin:0 8px;
  font-size:15px;
  font-weight:700;
  border-radius:0;
  box-shadow:inset 0 -2px 0 transparent; /* 占位，避免悬浮时跳动 */
  transition:box-shadow .2s, color .2s;
}
.layout-container-demo .el-menu-item.menu-plain:hover {
  background-color:transparent !important;
  transform:none;
  color:#ffffff !important;
  text-shadow:0 0 10px rgba(255,255,255,0.75); /* 悬浮：文字发光 */
  box-shadow:inset 0 -2px 0 #67c23a; /* 悬浮：底部绿色条 */
}
.layout-container-demo .el-menu-item.menu-plain.is-active {
  background-color:transparent !important;
  color:#ffffff !important;
  text-shadow:0 0 12px rgba(255,255,255,0.95); /* 激活：文字常亮发光 */
  box-shadow:inset 0 -2px 0 #67c23a;
}
/* 访客数量：紧跟【用户】菜单项下方，字号与菜单协调并加粗 */
.layout-container-demo .visitor-stat {
  display:block;
  font-size:14px;
  font-weight:700;
  color:rgba(255,255,255,0.92);
  text-align:center;
  line-height:1.5;
  margin-top:4px;
  padding:0 4px;
  text-shadow:0 1px 2px rgba(0,0,0,0.25);
  word-break:break-all;
}
/* 在线人数：访客数量下方，亮绿色与访客数（白色）区分，带呼吸光点动效 */
.layout-container-demo .online-stat {
  display:block;
  font-size:13px;
  font-weight:700;
  color:#7bed9f;
  text-align:center;
  line-height:1.4;
  margin:2px 0 4px;
  padding:0 4px;
  text-shadow:0 0 6px rgba(123,237,159,0.55);
  word-break:break-all;
}
.layout-container-demo .online-stat::before {
  content:'●';
  font-size:9px;
  margin-right:4px;
  vertical-align:1px;
  animation:online-blink 2.4s ease-in-out infinite;
}
@keyframes online-blink {
  0%, 100% { opacity:1; }
  50% { opacity:0.35; }
}
/* 底部工具组：主题按钮，flex 自动沉底 */
.layout-container-demo .aside-footer {
  margin-top:auto;
  padding:10px 8px 14px;
  display:flex;
  flex-direction:column;
  align-items:center;
}
.layout-container-demo .theme-btn {
  width:82%;
  margin:0;
  font-weight:600;
  box-shadow:0 2px 6px rgba(0,0,0,0.2);
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
  color:#ffffff !important;
  background-color:rgba(255,255,255,0.30) !important;
  transform:translateY(-1px);
}
.layout-container-demo .el-menu-item.is-active { /*https://blog.csdn.net/lannieZ/article/details/124007821*/
  color:#337ecc !important;
  background-color:rgba(255,255,255,0.92) !important;
  text-shadow:none;
  box-shadow:0 2px 10px rgba(0,0,0,0.25);
}
.layout-container-demo .toolbar{
  color: #ffffff;
  /* 任意视口宽度下允许换行，配合 header 自适应高度，不再遮挡按钮行 */
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  row-gap: 4px;
}
/* 顶栏右侧按钮组：注册/登录/登出/返回/铃铛一行靠右、间距一致 */
.layout-container-demo .header-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  padding-right: 12px;
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

/* ============ 移动端 / 窄屏适配（手机、浏览器拖窄、窗口大小变化） ============ */
.footer-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}
/* 页脚右下角日期时间：靠右对齐，移动端另起一行 */
.footer-clock {
  color: #000000;
  font-size: 16px;
  line-height: 20px;
  margin-left: auto;
  margin-right: 20px;
  white-space: nowrap;
}
@media (max-width: 768px) {
  .layout-container-demo {
    height: auto;
    min-height: 99vh;
  }
  .layout-container-demo .el-header {
    height: auto;
    min-height: 44px;
    font-size: 16px;
    padding: 0 4px;
  }
  .layout-container-demo .toolbar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    row-gap: 4px;
  }
  #headerTitle {
    font-size: 16px !important;
    margin-left: 4px !important;
    margin-right: 4px !important;
    margin-top: 4px !important;
    flex: 1 1 auto;
  }
  /* 顶栏按钮（注册/登录/登出/返回）在窄屏下取消 40vh 的大 margin */
  .layout-container-demo .toolbar > span {
    margin-left: 4px !important;
  }
  /* 按钮组保持靠右，组内间距在窄屏下收紧 */
  .layout-container-demo .toolbar > span.header-actions {
    margin-left: auto !important;
    gap: 6px;
    padding-right: 6px;
  }
  /* 侧边栏收窄，菜单字号缩小 */
  .layout-container-demo .el-aside {
    width: 64px !important;
    min-width: 64px !important;
    font-size: 14px;
  }
  .layout-container-demo .el-menu-item {
    font-size: 12px !important;
    height: 44px !important;
    margin: 4px 5px !important;
    padding: 0 !important;
  }
  /* 纯文字项在窄屏下保持紧凑 */
  .layout-container-demo .el-menu-item.menu-plain {
    height: 22px !important;
    margin: 0 5px !important;
    font-size: 11px !important;
  }
  .layout-container-demo .el-menu-item .menu-ico {
    font-size: 16px;
  }
  /* 底部工具组紧凑化（flex 沉底后无需再留 23vh） */
  .layout-container-demo .aside-footer {
    padding: 8px 4px 10px;
  }
  .layout-container-demo .theme-btn {
    width: 88% !important;
    margin: 0 !important;
  }
  /* 页脚备案信息小字号、可换行 */
  .footer-bar,
  .footer-bar a,
  .footer-bar span {
    font-size: 12px !important;
    line-height: 18px !important;
  }
  .footer-bar > span,
  .footer-bar > a {
    margin-left: 6px !important;
  }
}
@media (max-width: 480px) {
  .layout-container-demo .el-aside {
    width: 52px !important;
    min-width: 52px !important;
  }
  .layout-container-demo .el-menu-item {
    font-size: 11px !important;
    margin: 3px 4px !important;
  }
  .layout-container-demo .el-menu-item .menu-label {
    letter-spacing: 1px;
  }
}
</style>

<style>
/* 全局（非 scoped）兜底：el-dialog 会 teleport 到 body，scoped 样式够不到。
   1) 任何视口下弹窗都不超过屏幕（防止固定像素宽度的弹窗在小屏溢出）；
   2) 手机端所有弹窗统一接近全屏宽。
   桌面端（>768px）宽度按各视图自带的 min(…) 生效。 */
.el-dialog {
  max-width: 96vw;
}
/* 通用滚动弹窗：评论等长列表内容区限高滚动，不再把弹窗撑出屏幕 */
.el-dialog.dialog-scroll .el-dialog__body {
  max-height: 68vh;
  overflow-y: auto;
}
@media (max-width: 768px) {
  .el-dialog {
    width: 95% !important;
    max-width: 95% !important;
  }
}

/* ---------- 全站弹窗美化 ---------- */
/* 弹窗本体：大圆角 + 柔和立体阴影 + 顶部渐变标题栏 */
.el-dialog {
  border-radius: 16px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.18), 0 4px 16px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}
.el-dialog .el-dialog__header {
  background: linear-gradient(135deg, #f8faff 0%, #f0f5ff 100%);
  border-bottom: 1px solid #ebeef5;
  margin-right: 0;
  padding: 13px 24px;
}
.el-dialog .el-dialog__title {
  font-weight: 600;
  font-size: 18px;
  color: #303133;
  letter-spacing: 0.5px;
  line-height: 1.4;
}
.el-dialog .el-dialog__headerbtn {
  top: 12px;
  right: 20px;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  transition: background 0.2s;
}
.el-dialog .el-dialog__headerbtn:hover {
  background: #e8ecf3;
}
.el-dialog .el-dialog__body {
  padding: 20px 24px;
}
.el-dialog .el-dialog__footer {
  padding: 14px 24px 18px;
  border-top: 1px solid #f0f2f5;
}
/* 遮罩加深一点，弹窗更聚焦 */
.el-overlay {
  background-color: rgba(17, 20, 28, 0.5) !important;
  backdrop-filter: blur(2px);
}
/* ---------- 全站按钮微交互 ---------- */
/* 悬停轻浮 + 按下回弹：所有 el-button / 常见自绘按钮统一手感 */
.el-button {
  transition: transform 0.15s ease, box-shadow 0.2s ease, background-color 0.2s ease, border-color 0.2s ease;
}
.el-button:not(.is-disabled):hover {
  transform: translateY(-1px);
}
.el-button:not(.is-disabled):active {
  transform: translateY(0) scale(0.97);
}
/* 主按钮：柔和投影强调层级 */
.el-button--primary:not(.is-disabled):hover {
  box-shadow: 0 6px 16px rgba(64, 128, 255, 0.35);
}
/* 危险按钮：红色系投影 */
.el-button--danger:not(.is-disabled):hover {
  box-shadow: 0 6px 16px rgba(245, 74, 69, 0.3);
}
/* 圆角统一 */
.el-button {
  border-radius: 8px;
}
/* 输入类控件圆角与按钮统一，弹窗内表单视觉一致 */
.el-input__wrapper,
.el-textarea__inner,
.el-select__wrapper {
  border-radius: 8px;
}
@media (max-width: 768px) {
  /* 手机端按钮更大更好按 */
  .el-button {
    min-height: 36px;
    padding-left: 14px;
    padding-right: 14px;
  }
}

/* ---------- 1) 页面/区块占比与卡片美化（文章/想法/游记等列表与详情页通用） ---------- */
/* 内容卡片：大圆角 + 轻边框去重影 + 悬停微浮，列表页的 block 从"色块"变成"卡片" */
.el-card {
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 2px 10px rgba(15, 27, 61, 0.06);
  transition: box-shadow 0.25s ease, transform 0.25s ease;
}
.el-card:hover {
  box-shadow: 0 8px 22px rgba(15, 27, 61, 0.1);
}
/* 正文类卡片（含 markdown 渲染的详情页）内边距更舒展，长文阅读不憋屈 */
.el-card__body {
  padding: 18px 20px;
}
@media (max-width: 768px) {
  .el-card__body {
    padding: 14px;   /* 手机端卡片内边距收紧，内容占比更大 */
  }
}
/* 卡片头：细分割线 + 适中留白 */
.el-card__header {
  padding: 14px 20px;
  border-bottom: 1px solid #f0f2f5;
  font-weight: 600;
}
/* 分页器：胶囊化，间距统一 */
.el-pagination {
  --el-pagination-border-radius: 8px;
  --el-pagination-button-spacing: 6px;
  padding: 10px 0;
}
/* 空状态：弱化灰色，不抢内容视觉 */
.el-empty__description p {
  color: #a8abb2;
  font-size: 13px;
}
/* 媒体兜底：详情页长文里的图片/视频/代码块不撑破卡片 */
.el-card img,
.el-card video {
  max-width: 100%;
  border-radius: 8px;
}
.el-card pre {
  overflow-x: auto;
  border-radius: 8px;
}
/* ---------- 2) 文本输入框与表单美化 ---------- */
/* 输入框：悬停边框加深、聚焦品牌色光圈，输入状态一目了然 */
.el-input__wrapper,
.el-textarea__inner,
.el-select__wrapper {
  transition: box-shadow 0.2s ease, background-color 0.2s ease;
}
.el-input__wrapper:not(.is-focus):hover,
.el-select__wrapper:not(.is-focus):hover {
  box-shadow: 0 0 0 1px #b1b8c4 inset;
}
.el-input__wrapper.is-focus,
.el-select__wrapper.is-focus,
.el-textarea__inner:focus {
  box-shadow: 0 0 0 1px #409eff inset, 0 0 0 3px rgba(64, 158, 255, 0.12);
}
/* placeholder：更浅更轻，与正文区分 */
.el-input__inner::placeholder,
.el-textarea__inner::placeholder {
  color: #b8bdc7;
}
/* 表单项：统一垂直节奏，弹窗/页面里的表单间距不再忽大忽小 */
.el-form-item {
  margin-bottom: 18px;
}
.el-form-item__label {
  font-weight: 500;
  color: #606266;
}
/* 表单内最后的项不留多余底距（弹窗 footer 间距更匀称） */
.el-form-item:last-child {
  margin-bottom: 0;
}
/* ---------- 3) 文字/文本排版美化 ---------- */
/* 全局正文字色与行高：长文阅读更舒适（用 Element 变量，跟随主题） */
body {
  --el-text-color-primary: #303133;
  --el-text-color-regular: #4e5969;
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
/* 标题层级：字重与间距统一 */
h1, h2, h3, h4 {
  font-weight: 600;
  line-height: 1.4;
  color: var(--el-text-color-primary);
}
h1 { font-size: 24px; margin: 0.6em 0 0.4em; }
h2 { font-size: 20px; margin: 0.7em 0 0.4em; }
h3 { font-size: 17px; margin: 0.7em 0 0.4em; }
h4 { font-size: 15px; margin: 0.6em 0 0.3em; }
/* 正文段落：行高与段距，长文（详情页）不再挤成一坨 */
p {
  line-height: 1.75;
  margin: 0.5em 0;
  color: var(--el-text-color-regular);
  word-break: break-word;
}
/* 链接：品牌色 + 悬停下划线 */
a {
  color: #409eff;
  text-decoration: none;
  transition: color 0.2s ease;
}
a:hover {
  color: #66b1ff;
  text-decoration: underline;
  text-underline-offset: 3px;
}
/* 选中文字：品牌色底 */
::selection {
  background: rgba(64, 158, 255, 0.18);
}
/* 全局滚动条：细窄圆角，深浅两套 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-thumb {
  background: rgba(144, 147, 153, 0.35);
  border-radius: 8px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(144, 147, 153, 0.55);
}
::-webkit-scrollbar-track {
  background: transparent;
}

/* ---------- el-card 手机/电脑适配 ---------- */
/* 手机/平板（<=768px）：卡片更紧凑、阴影收淡、长文字防溢出 */
@media (max-width: 768px) {
  .el-card {
    border-radius: 10px;
    box-shadow: 0 1px 6px rgba(15, 27, 61, 0.08);
  }
  .el-card__header {
    padding: 10px 14px;
    font-size: 15px;
  }
  .el-card__body {
    padding: 12px;
    overflow-wrap: break-word;
    word-break: break-word;
  }
  .el-card img,
  .el-card video {
    border-radius: 6px;
  }
}
/* 小屏手机（<=480px）：进一步收紧留白，内容占比更大 */
@media (max-width: 480px) {
  .el-card__body {
    padding: 10px;
  }
  .el-card__header {
    padding: 8px 12px;
    font-size: 14px;
  }
}
/* 触屏设备（无悬停）：关闭卡片/按钮的悬停浮起与投影，避免点击后"粘住"悬停态 */
@media (hover: none) {
  .el-card:hover {
    box-shadow: 0 2px 10px rgba(15, 27, 61, 0.06);
  }
  .el-button:not(.is-disabled):hover {
    transform: none;
    box-shadow: none;
  }
}
</style>
