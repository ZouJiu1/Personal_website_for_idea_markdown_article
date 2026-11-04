<template>
  <div class="admin-page">
    <div class="admin-header">
      <span class="admin-title">注册管理</span>
      <el-input
        v-model="search"
        placeholder="搜索 用户名 / 邮箱 / 昵称"
        class="admin-search"
        clearable
      />
      <el-button type="primary" @click="loadUsers">刷新</el-button>
      <!-- 访客数批量保存：有未保存修改才可点，点击后弹确认，确认才真正生效 -->
      <el-button v-if="canCreateUser" type="primary" plain :disabled="travelerDirtyCount === 0" @click="confirmSaveTravelers">
        保存访客修改<template v-if="travelerDirtyCount > 0">（{{ travelerDirtyCount }}）</template>
      </el-button>
      <el-button v-if="canCreateUser" type="warning" @click="openCreateUser">新建用户</el-button>
      <!-- 站点配置：仅站长可见可配置（超级管理员/普通管理员后端与前端双层隐藏） -->
      <el-button v-if="isOwner" type="danger" @click="openSiteConfig">站点配置</el-button>
      <el-button type="success" @click="openNotice">通知用户</el-button>
    </div>
    <el-dialog v-model="noticeVisible" title="发送通知" class="admin-dialog" width="min(600px, 92%)">
      <div style="margin-bottom:10px;">
        <el-checkbox v-model="noticeAll">发送给全部用户</el-checkbox>
      </div>
      <el-select
        v-if="!noticeAll"
        v-model="noticeTargets"
        multiple
        filterable
        placeholder="选择一个或多个用户"
        style="width:100%;margin-bottom:10px;"
      >
        <el-option
          v-for="u in users"
          :key="u.mail"
          :label="u.nickname + '（' + u.mail + '）'"
          :value="u.mail"
        />
      </el-select>
      <el-input
        v-model="noticeContent"
        type="textarea"
        :autosize="{ minRows: 4, maxRows: 10 }"
        placeholder="通知内容"
      />
      <span class="admin-tip">通知会显示在对方的 🔔 通知里，按时间倒序排列</span>
      <template #footer>
        <el-button @click="noticeVisible = false">取消</el-button>
        <el-button type="primary" @click="submitNotice">发送</el-button>
      </template>
    </el-dialog>

    <el-table
      :data="filteredUsers"
      border
      stripe
      class="admin-table"
      v-loading="loading"
      empty-text="暂无用户"
    >
      <el-table-column prop="mail" label="用户名" min-width="110" />
      <el-table-column prop="truemail" label="邮箱" min-width="180" show-overflow-tooltip />
      <el-table-column prop="nickname" label="昵称" min-width="110" show-overflow-tooltip />
      <el-table-column label="权限" width="130">
        <template #default="scope">
          <el-tag v-if="scope.row.is_owner" type="danger" effect="dark">站长</el-tag>
          <el-tag v-else-if="scope.row.is_super" type="danger" effect="dark">超级管理员</el-tag>
          <el-tag v-else-if="scope.row.is_admin" type="warning">普通管理员</el-tag>
          <el-tag v-else type="info">普通用户</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="数据目录" width="90">
        <template #default="scope">
          <el-tag v-if="scope.row.hasdata" type="success">有</el-tag>
          <el-tag v-else type="warning">无</el-tag>
        </template>
      </el-table-column>
      <!-- 访客数量：仅站长/超级管理员可见可编辑（后端同权限校验）；
           只改本地值，点头部「保存访客修改」确认后才生效 -->
      <el-table-column v-if="canCreateUser" label="访客" width="150">
        <template #default="scope">
          <el-input-number
            v-model="scope.row.traveler"
            size="small"
            :min="0"
            :max="999999999"
            :step="1"
            step-strictly
            controls-position="right"
            style="width: 120px"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250">
        <template #default="scope">
          <el-button
            size="small"
            type="primary"
            :disabled="!canManage(scope.row)"
            @click="openResetPass(scope.row)"
          >重置密码</el-button>
          <el-button
            size="small"
            type="warning"
            :disabled="!canManage(scope.row)"
            @click="openSetQuanxian(scope.row)"
          >权限</el-button>
          <el-button
            size="small"
            type="danger"
            :disabled="!canManage(scope.row)"
            @click="confirmDelete(scope.row)"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="resetPassVisible" :title="'重置密码：' + currentUser.mail" class="admin-dialog" width="min(500px, 92%)">
      <el-input
        v-model="newpass"
        type="password"
        placeholder="新密码（至少 6 位，包含数字和字母）"
        show-password
      />
      <template #footer>
        <el-button @click="resetPassVisible = false">取消</el-button>
        <el-button type="primary" @click="submitResetPass">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="quanxianVisible" :title="'修改权限：' + currentUser.mail" class="admin-dialog" width="min(500px, 92%)">
      <el-select v-model="newRole" placeholder="选择权限">
        <el-option label="超级管理员（管理所有用户）" :value="superQx" />
        <el-option label="普通管理员（管理普通用户）" :value="adminQx" />
        <el-option label="普通用户" :value="normalQx" />
      </el-select>
      <span class="admin-tip">超级管理员可管理全部用户；普通管理员不能操作超级管理员</span>
      <template #footer>
        <el-button @click="quanxianVisible = false">取消</el-button>
        <el-button type="primary" @click="submitSetQuanxian">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="createVisible" title="新建用户" class="admin-dialog" width="min(520px, 92%)">
      <div style="display:flex; flex-direction:column; gap:12px;">
        <el-input v-model="createForm.email" placeholder="邮箱（登录账号，如 someone@example.com）" clearable />
        <el-input v-model="createForm.nickname" placeholder="用户名 / 昵称" clearable />
        <el-input v-model="createForm.password" type="password" placeholder="密码（至少 6 位，包含数字和字母）" show-password />
        <span class="admin-tip">创建后即可用该邮箱和密码登录；仅站长与超级管理员可以新建用户</span>
      </div>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreateUser">确定创建</el-button>
      </template>
    </el-dialog>

    <!-- 站点配置弹窗：site_config.json 全部可编辑项，仅站长（按钮/入口已隐藏，后端再校验）；
         桌面宽弹窗（1100px），手机端 CSS 强制全宽（见底部媒体查询） -->
    <el-dialog v-model="siteConfigVisible" title="站点配置（site_config.json）" class="admin-dialog siteconfig-dialog" width="min(1100px, 96%)">
      <!-- 顶部工具条：搜索过滤 + 统计 -->
      <div class="siteconfig-toolbar">
        <el-input
          v-model="siteConfigSearch"
          placeholder="搜索配置项（键名 / 说明）"
          clearable
          class="siteconfig-search"
        />
        <span class="siteconfig-count">
          {{ filteredSiteConfigItems.length }} 项
          <template v-if="siteConfigDirtyCount > 0">· 已修改 {{ siteConfigDirtyCount }} 项</template>
        </span>
      </div>
      <!-- 分类折叠面板：按功能分组，标题带条数与未保存数 -->
      <div v-loading="siteConfigLoading" class="siteconfig-list">
        <el-collapse v-model="siteConfigOpenCats">
          <el-collapse-item v-for="cat in siteConfigCats" :key="cat.name" :name="cat.name">
            <template #title>
              <span class="siteconfig-cat-title">{{ cat.name }}</span>
              <span class="siteconfig-cat-count">
                {{ cat.items.length }} 项<template v-if="cat.dirty > 0"> · 已改 {{ cat.dirty }}</template>
              </span>
            </template>
            <div
              v-for="it in cat.items"
              :key="it.key"
              class="siteconfig-item"
              :class="{ 'siteconfig-item-dirty': isSiteConfigDirty(it) }"
            >
              <div class="siteconfig-key">
                {{ it.key }}
                <el-tooltip :content="it.doc || '（无说明）'" placement="top" :disabled="!it.doc">
                  <span class="siteconfig-help">?</span>
                </el-tooltip>
                <span v-if="it.readonly" class="siteconfig-tag siteconfig-tag-readonly">只读</span>
                <span v-if="isSiteConfigDirty(it)" class="siteconfig-tag siteconfig-tag-dirty">已修改</span>
                <!-- 单项还原：回到服务端原值 -->
                <el-button
                  v-if="isSiteConfigDirty(it) && !it.readonly"
                  link
                  type="primary"
                  size="small"
                  class="siteconfig-restore"
                  @click="resetSiteConfigItem(it)"
                >还原</el-button>
              </div>
              <!-- 说明全文显示（不截断）：含义/怎么改/后果是站长改配置的主要依据 -->
              <div v-if="it.doc" class="siteconfig-doc">{{ it.doc }}</div>
              <!-- 只读项（如 traveler_filename，改名会丢历史统计）：置灰仅展示 -->
              <el-input v-if="it.readonly" v-model="it.edit" disabled />
              <el-switch v-else-if="it.type === 'bool'" v-model="it.edit" />
              <el-input-number
                v-else-if="it.type === 'int' || it.type === 'float'"
                v-model="it.edit"
                class="siteconfig-number"
                :step="1"
                controls-position="right"
              />
              <el-input v-else-if="it.type === 'str'" v-model="it.edit" clearable />
              <!-- 数组/对象（music_sources / music_apis 等）：按 JSON 文本编辑 -->
              <el-input
                v-else-if="it.type === 'json'"
                v-model="it.edit"
                type="textarea"
                :autosize="{ minRows: 4, maxRows: 14 }"
                class="siteconfig-json"
              />
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
      <span class="admin-tip">绝大多数项保存即生效；说明里标注「需重启」的项（如 display_timezone_offset_seconds、server_request_queue_size）改后要重启后端才生效</span>
      <template #footer>
        <el-button @click="siteConfigVisible = false">关闭</el-button>
        <el-button
          type="primary"
          :loading="siteConfigSaving"
          :disabled="siteConfigDirtyCount === 0"
          @click="saveSiteConfig"
        >保存修改<template v-if="siteConfigDirtyCount > 0">（{{ siteConfigDirtyCount }}）</template></el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'
import Cookies from 'js-cookie'
import { ElMessage, ElMessageBox } from 'element-plus'
import getusername from '/src/common.js'
import { ADMIN_QUANXIAN, NORMAL_QUANXIAN, SUPER_ADMIN_QUANXIAN, isAdminQuanxian, isSuperAdminQuanxian, isOwnerQuanxian } from '/src/common.js'

// 站点配置分组：键名 -> 类别（site_config.json 现有键的固定归类，新增未识别键归「其他」）
const SITE_CONFIG_CATEGORIES = [
  { name: '访客统计', keys: ['traveler_dedup_window_seconds', 'traveler_cleanup_seconds', 'traveler_default_init', 'traveler_filename'] },
  { name: '邮箱与通知', keys: ['smtp_host', 'smtp_port', 'smtp_user', 'smtp_password', 'site_domain', 'site_name', 'mail_resend_cooldown_seconds', 'verify_code_ttl_seconds', 'notice_display_max', 'notice_clear_temporary'] },
  { name: '音乐播放器', keys: ['music_enabled', 'music_api', 'music_apis', 'music_server', 'music_type', 'music_id', 'music_sources'] },
  { name: '登录与账号', keys: ['cookie_login_days', 'min_username_prefix_length', 'short_name_guard_max_length', 'nickname_max_len'] },
  { name: '内容长度限制', keys: ['modified_label_seconds', 'travel_min_email_len', 'travel_min_contact_len', 'travel_min_content_len', 'travel_max_content_len', 'travel_max_field_len', 'setting_max_items', 'setting_max_field_len', 'book_max_field_len', 'book_max_items', 'book_default_pagesize', 'book_max_pagesize'] },
  { name: '列表分页', keys: ['default_currentpage', 'default_pagesize_csdn', 'default_pagesize_think', 'default_pagesize_travel', 'default_pagesize_video'] },
  { name: '站点与页脚', keys: ['site_owner_mail', 'footer_gongan_code', 'footer_gongan_text', 'footer_copyright', 'footer_icp_text', 'footer_report_email'] },
  { name: '服务与性能', keys: ['display_timezone_offset_seconds', 'server_request_queue_size'] },
]

export default {
  name: 'admin',
  data() {
    return {
      users: [],
      search: '',
      loading: false,
      resetPassVisible: false,
      quanxianVisible: false,
      currentUser: {},
      newpass: '',
      newRole: NORMAL_QUANXIAN,
      superQx: SUPER_ADMIN_QUANXIAN,
      adminQx: ADMIN_QUANXIAN,
      normalQx: NORMAL_QUANXIAN,
      currentMail: '',
      // 当前登录者的权限值（超级管理员 / 普通管理员）
      myLevel: 0,
      // 通知
      noticeVisible: false,
      noticeAll: true,
      noticeTargets: [],
      noticeContent: '',
      // 新建用户（仅站长/超级管理员）
      createVisible: false,
      createForm: { email: '', nickname: '', password: '' },
      // 站点配置（仅站长）
      siteConfigVisible: false,
      siteConfigItems: [],
      siteConfigLoading: false,
      siteConfigSaving: false,
      siteConfigSearch: '',
      siteConfigOpenCats: [],
    }
  },
  computed: {
    isSuper() {
      return isSuperAdminQuanxian(this.myLevel);
    },
    // 站长本人（权限 999999999）：站点配置仅其可见可改
    isOwner() {
      return isOwnerQuanxian(this.myLevel);
    },
    // 新建用户：仅站长与超级管理员
    canCreateUser() {
      return isOwnerQuanxian(this.myLevel) || isSuperAdminQuanxian(this.myLevel);
    },
    // 访客数未保存的修改条数（仅站长/超级管理员能看到访客列，普通管理员恒为 0）
    travelerDirtyCount() {
      return this.users.filter((u) => u.traveler !== u._travelerOrig).length;
    },
    // ---------- 站点配置 ----------
    // 搜索过滤后的配置项（按键名/说明模糊匹配）
    filteredSiteConfigItems() {
      const s = (this.siteConfigSearch || '').trim().toLowerCase();
      if (!s) {
        return this.siteConfigItems;
      }
      return this.siteConfigItems.filter((it) =>
        it.key.toLowerCase().includes(s) || (it.doc || '').toLowerCase().includes(s)
      );
    },
    // 站点配置未保存修改条数
    siteConfigDirtyCount() {
      return this.siteConfigItems.filter((it) => this.isSiteConfigDirty(it)).length;
    },
    // 站点配置按类别分组（未识别键归「其他」；搜索时只显示命中的项，空分组隐藏）
    siteConfigCats() {
      const s = (this.siteConfigSearch || '').trim().toLowerCase();
      const match = (it) => !s || it.key.toLowerCase().includes(s) || (it.doc || '').toLowerCase().includes(s);
      const key2cat = {};
      SITE_CONFIG_CATEGORIES.forEach((c) => c.keys.forEach((k) => { key2cat[k] = c.name; }));
      const groups = {};
      for (const it of this.siteConfigItems) {
        const name = key2cat[it.key] || '其他';
        (groups[name] = groups[name] || []).push(it);
      }
      const names = SITE_CONFIG_CATEGORIES.map((c) => c.name).filter((n) => groups[n]);
      if (groups['其他']) {
        names.push('其他');
      }
      return names.map((name) => {
        const items = groups[name].filter(match);
        return { name, items, dirty: items.filter((it) => this.isSiteConfigDirty(it)).length };
      }).filter((c) => c.items.length > 0);
    },
    filteredUsers() {
      if (!this.search) {
        return this.users;
      }
      let s = this.search.toLowerCase();
      return this.users.filter((u) => {
        return (u.mail && u.mail.toLowerCase().includes(s))
          || (u.truemail && u.truemail.toLowerCase().includes(s))
          || (u.nickname && u.nickname.toLowerCase().includes(s));
      });
    },
  },
  watch: {
    // 搜索站点配置时自动展开全部分组，避免命中的项藏在折叠里
    siteConfigSearch() {
      this.siteConfigOpenCats = this.siteConfigCats.map((c) => c.name);
    },
  },
  mounted() {
    this.checkAdminAndLoad();
  },
  methods: {
    authData() {
      return { mail: Cookies.get('mail'), password: Cookies.get('password') };
    },
    // 能否操作某一行：不能操作自己；站长账号（权限 999999999）任何管理员都不能操作；
    // 普通管理员不能操作超级管理员
    canManage(row) {
      if (row.mail === this.currentMail) {
        return false;
      }
      // 站长仅按权限值识别（后端 is_owner 字段 + 权限值双保险，与邮箱/昵称无关）
      if (row.is_owner || isOwnerQuanxian(row.quanxian)) {
        return false;
      }
      if (row.is_super && !isSuperAdminQuanxian(this.myLevel)) {
        return false;
      }
      return true;
    },
    async checkAdminAndLoad() {
      let gu;
      await getusername(document.URL).then((response) => {
        gu = response;
      });
      if (!gu || gu.ret <= 0 || !isAdminQuanxian(gu.quanxian)) {
        ElMessage.error('只有管理员才能访问管理页面！');
        // URL 隐私：回站长 uid 页面，取不到回退站长邮箱
        this.$router.push({ path: '/' + (gu.owneruid || localStorage.getItem('site_owner_uid') || 'homepage@gmail.com') });
        return;
      }
      this.myLevel = parseInt(gu.quanxian);
      this.currentMail = Cookies.get('mail') || gu.mail || '';
      this.loadUsers();
    },
    async loadUsers() {
      this.loading = true;
      const instance = axios.create({ baseURL: '/csdn/admin_userlist', timeout: 20000 });
      await instance({
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        data: this.authData(),
      }).then((response) => {
        this.loading = false;
        if (response.data.ret === 1) {
          // 访客数兜底：后端仅对站长/超级管理员返回该字段；
          // _travelerOrig 记录服务端原值，用于「保存访客修改」的未保存计数
          this.users = response.data.users.map((u) => {
            const t = typeof u.traveler === 'number' ? u.traveler : 0;
            return { ...u, traveler: t, _travelerOrig: t };
          });
          if (response.data.my_level) {
            this.myLevel = response.data.my_level;
          }
        } else if (response.data.ret === -100) {
          ElMessage.error('没有管理员权限！');
          // URL 隐私：回站长 uid 页面，取不到回退站长邮箱
          this.$router.push({ path: '/' + (localStorage.getItem('site_owner_uid') || 'homepage@gmail.com') });
        } else {
          ElMessage.error('获取用户列表失败！');
        }
      }).catch(() => {
        this.loading = false;
        ElMessage.error('网络错误，获取用户列表失败！');
      });
    },
    openResetPass(row) {
      this.currentUser = row;
      this.newpass = '';
      this.resetPassVisible = true;
    },
    // ---------- 访客数修改（仅站长/超级管理员；后端 admin_settraveler 同权限校验） ----------
    // 弹窗列出全部待保存修改，确认后才逐条提交（修改不会即时生效）
    confirmSaveTravelers() {
      const dirty = this.users.filter((u) => u.traveler !== u._travelerOrig);
      if (dirty.length === 0) {
        return;
      }
      const lines = dirty.map((u) => '　' + (u.nickname || u.mail) + '：' + u._travelerOrig + ' → ' + u.traveler).join('\n');
      ElMessageBox.confirm(
        '以下 ' + dirty.length + ' 项访客数量修改将被保存：\n' + lines,
        '保存访客修改',
        { confirmButtonText: '确认保存', cancelButtonText: '取消', type: 'warning' }
      ).then(() => {
        this.submitSaveTravelers(dirty);
      }).catch(() => {});
    },
    async submitSaveTravelers(dirty) {
      // 防连点
      if (this._busy) {
        return;
      }
      this._busy = true;
      let okCount = 0;
      let failCount = 0;
      const instance = axios.create({ baseURL: '/csdn/admin_settraveler', timeout: 20000 });
      // 逐条提交（避免并发打后端），单条失败不影响其余
      for (const row of dirty) {
        const value = parseInt(row.traveler, 10);
        if (isNaN(value) || value < 0) {
          failCount += 1;
          continue;
        }
        try {
          const response = await instance({
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            data: { ...this.authData(), target: row.mail, value },
          });
          if (response.data.ret === 1) {
            // 以后端回读值为准，同步原值标记（该行不再算未保存）
            row.traveler = response.data.traveler;
            row._travelerOrig = row.traveler;
            okCount += 1;
          } else {
            failCount += 1;
          }
        } catch (e) {
          failCount += 1;
        }
      }
      this._busy = false;
      if (failCount === 0) {
        ElMessage.success('已保存 ' + okCount + ' 项访客数量修改！');
      } else {
        ElMessage.error('保存完成：成功 ' + okCount + ' 项，失败 ' + failCount + ' 项（已重新拉取列表）！');
        this.loadUsers();
      }
    },
    openNotice() {
      this.noticeVisible = true;
      this.noticeAll = true;
      this.noticeTargets = [];
      this.noticeContent = '';
    },
    openCreateUser() {
      this.createForm = { email: '', nickname: '', password: '' };
      this.createVisible = true;
    },
    // ---------- 站点配置（仅站长；后端 siteconfig_list/siteconfig_save 同权限校验） ----------
    async openSiteConfig() {
      this.siteConfigVisible = true;
      await this.loadSiteConfig();
    },
    async loadSiteConfig() {
      this.siteConfigLoading = true;
      const instance = axios.create({ baseURL: '/csdn/siteconfig_list', timeout: 20000 });
      await instance({
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        data: this.authData(),
      }).then((response) => {
        this.siteConfigLoading = false;
        if (response.data.ret === 1 && Array.isArray(response.data.items)) {
          this.siteConfigItems = response.data.items.map((it) => {
            // 编辑值：json 类型转成可编辑文本（smtp_password 按站长要求明文显示可改）
            const edit = it.type === 'json' ? JSON.stringify(it.value, null, 2) : it.value;
            // orig 记录服务端原值（与 edit 同形态），用于「已修改」高亮与单项还原
            return { ...it, edit, orig: edit };
          });
          // 默认展开全部分组
          this.siteConfigOpenCats = this.siteConfigCats.map((c) => c.name);
        } else {
          ElMessage.error('没有权限读取站点配置！');
          this.siteConfigVisible = false;
        }
      }).catch(() => {
        this.siteConfigLoading = false;
        ElMessage.error('网络错误，读取站点配置失败！');
      });
    },
    // 某配置项是否有未保存修改（edit 与服务端原值 orig 逐字比较）
    isSiteConfigDirty(it) {
      return String(it.edit) !== String(it.orig);
    },
    // 单项还原到服务端原值
    resetSiteConfigItem(it) {
      it.edit = it.orig;
    },
    // 确认弹窗里的值摘要：压掉换行并截断
    shortSiteConfigVal(v) {
      const s = String(v).replace(/\s+/g, ' ').trim();
      return s.length > 60 ? s.slice(0, 60) + '…' : s;
    },
    async saveSiteConfig() {
      // 防连点
      if (this._busy) {
        return;
      }
      // 只提交真正改动的项（未改动的不重写，降低误伤面）
      const dirty = this.siteConfigItems.filter((it) => !it.readonly && this.isSiteConfigDirty(it));
      if (dirty.length === 0) {
        ElMessage('没有修改任何配置');
        return;
      }
      // 保存前确认：列出每项 原值 -> 新值
      const lines = dirty.slice(0, 8).map((it) =>
        '　' + it.key + '：' + this.shortSiteConfigVal(it.orig) + ' → ' + this.shortSiteConfigVal(it.edit)
      ).join('\n') + (dirty.length > 8 ? '\n　… 等共 ' + dirty.length + ' 项' : '');
      try {
        await ElMessageBox.confirm(
          '以下 ' + dirty.length + ' 项配置修改将被保存：\n' + lines + '\n\n确认保存？',
          '保存站点配置',
          { confirmButtonText: '确认保存', cancelButtonText: '取消', type: 'warning' }
        );
      } catch (e) {
        return;
      }
      const updates = {};
      for (const it of dirty) {
        let v = it.edit;
        if (it.type === 'json') {
          try {
            v = JSON.parse(v);
          } catch (e) {
            ElMessage.error(it.key + ' 不是合法的 JSON！');
            return;
          }
          updates[it.key] = v;
        } else if (it.type === 'bool') {
          updates[it.key] = !!v;
        } else if (it.type === 'int' || it.type === 'float') {
          const n = Number(v);
          if (v === null || v === '' || isNaN(n)) {
            ElMessage.error(it.key + ' 必须是数字！');
            return;
          }
          updates[it.key] = n;
        } else {
          updates[it.key] = String(v === null || v === undefined ? '' : v);
        }
      }
      this._busy = true;
      this.siteConfigSaving = true;
      const instance = axios.create({ baseURL: '/csdn/siteconfig_save', timeout: 20000 });
      await instance({
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
        data: { ...this.authData(), updates },
      }).then((response) => {
        if (response.data.ret === 1) {
          ElMessage.success('站点配置已保存！');
          // 重新拉取：回显服务器端最终值并重置「已修改」状态
          this.loadSiteConfig();
        } else {
          ElMessage.error(response.data.msg || '保存失败（ret=' + response.data.ret + '）！');
        }
      }).catch(() => {
        ElMessage.error('网络错误，保存站点配置失败！');
      }).finally(() => {
        this._busy = false;
        this.siteConfigSaving = false;
      });
    },
    async submitCreateUser() {
      const email = (this.createForm.email || '').trim();
      const nickname = (this.createForm.nickname || '').trim();
      const password = this.createForm.password || '';
      if (!email || !nickname || !password) {
        ElMessage.error('邮箱、用户名、密码都必须填写！');
        return;
      }
      if (!(/[A-Za-z]/.test(password) && /\d/.test(password)) || password.length < 6) {
        ElMessage.error('密码至少 6 位，且必须同时包含数字和字母！');
        return;
      }
      // 防连点：上一次请求未完成时忽略本次点击
      if (this._busy) {
        return;
      }
      this._busy = true;
      const instance = axios.create({ baseURL: '/csdn/admin_createuser', timeout: 20000 });
      await instance({
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
        data: { ...this.authData(), email, nickname, newpass: password },
      }).then((response) => {
        const ret = response.data.ret;
        if (ret === 1) {
          ElMessage.success('用户【' + email + '】创建成功！');
          this.createVisible = false;
          this.loadUsers();
        } else {
          // 后端 msg 优先（邮箱格式/最短长度/重复等），无 msg 时按错误码兜底
          ElMessage.error(response.data.msg || {
            '-100': '只有站长或超级管理员才能新建用户！',
            '-1': '邮箱、用户名、密码都必须填写！',
            '-2': '邮箱格式不合法！',
            '-3': '用户名（@前的部分）太短！',
            '-4': '该邮箱已被注册！',
          }[String(ret)] || '创建失败！');
        }
      }).catch(() => {
        ElMessage.error('网络错误，创建失败！');
      }).finally(() => {
        this._busy = false;
      });
    },
    async submitNotice() {
      if (!this.noticeContent || !this.noticeContent.trim()) {
        ElMessage.error('通知内容不能为空！');
        return;
      }
      if (!this.noticeAll && this.noticeTargets.length === 0) {
        ElMessage.error('请选择要通知的用户！');
        return;
      }
      // 防连点：上一次请求未完成时忽略本次点击
      if (this._busy) {
        return;
      }
      this._busy = true;
      const instance = axios.create({ baseURL: '/csdn/send_notice', timeout: 20000 });
      await instance({
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
        data: {
          ...this.authData(),
          content: this.noticeContent.trim(),
          targets: this.noticeAll ? [] : this.noticeTargets,
        },
      }).then((response) => {
        if (response.data.ret === 1) {
          ElMessage('已通知 ' + response.data.sent + ' 个用户');
          this.noticeVisible = false;
        } else if (response.data.ret === -100) {
          ElMessage.error('没有管理员权限！');
        } else if (response.data.ret === -1) {
          ElMessage.error('通知内容不能为空！');
        } else {
          ElMessage.error('发送失败，没有可通知的用户！');
        }
      }).catch(() => {
        ElMessage.error('网络错误，发送失败！');
      }).finally(() => {
        this._busy = false;
      });
    },
    async submitResetPass() {
      if (!this.newpass || this.newpass.length < 6) {
        ElMessage('新密码长度至少 6 位！');
        return;
      }
      // 与占位提示一致：必须同时包含数字和字母（后端同规则校验）
      if (!(/[A-Za-z]/.test(this.newpass) && /\d/.test(this.newpass))) {
        ElMessage.error('新密码必须同时包含数字和字母！');
        return;
      }
      // 防连点：上一次请求未完成时忽略本次点击
      if (this._busy) {
        return;
      }
      this._busy = true;
      const instance = axios.create({ baseURL: '/csdn/admin_resetpass', timeout: 20000 });
      await instance({
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        data: { ...this.authData(), target: this.currentUser.mail, newpass: this.newpass },
      }).then((response) => {
        if (response.data.ret === 1) {
          ElMessage('已重置【' + this.currentUser.mail + '】的密码！');
          this.resetPassVisible = false;
        } else if (response.data.ret === -6) {
          ElMessage.error('站长账号受保护，不能重置其密码！');
        } else if (response.data.ret === -100) {
          ElMessage.error('没有管理员权限！');
        } else {
          ElMessage.error('重置失败，用户不存在或密码格式不对！');
        }
      }).catch(() => {
        ElMessage.error('网络错误，重置失败！');
      }).finally(() => {
        this._busy = false;
      });
    },
    openSetQuanxian(row) {
      this.currentUser = row;
      this.newRole = String(row.quanxian);
      this.quanxianVisible = true;
    },
    async submitSetQuanxian() {
      if (this.currentUser.mail === this.currentMail) {
        ElMessage.error('不能修改自己的权限！');
        return;
      }
      // 防连点：上一次请求未完成时忽略本次点击
      if (this._busy) {
        return;
      }
      this._busy = true;
      const instance = axios.create({ baseURL: '/csdn/admin_setquanxian', timeout: 20000 });
      await instance({
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        data: { ...this.authData(), target: this.currentUser.mail, quanxian: parseInt(this.newRole) },
      }).then((response) => {
        if (response.data.ret === 1) {
          ElMessage('已修改【' + this.currentUser.mail + '】的权限！');
          this.quanxianVisible = false;
          this.loadUsers();
        } else if (response.data.ret === -4) {
          ElMessage.error('不能修改自己的权限！');
        } else if (response.data.ret === -6) {
          ElMessage.error('站长账号受保护，不能修改其权限！');
        } else if (response.data.ret === -3) {
          ElMessage.error('普通管理员不能操作超级管理员，也不能授予超级管理员！');
        } else if (response.data.ret === -100) {
          ElMessage.error('没有管理员权限！');
        } else {
          ElMessage.error('修改失败，用户不存在！');
        }
      }).catch(() => {
        ElMessage.error('网络错误，修改失败！');
      }).finally(() => {
        this._busy = false;
      });
    },
    // 删除用户：三次连环确认（任何一步取消即中止）
    confirmDelete(row) {
      const who = '【' + (row.nickname || row.mail) + '（' + row.mail + '）】';
      ElMessageBox.confirm(
        '确定要删除用户' + who + '吗？',
        '删除确认（第 1 / 3 次）',
        { confirmButtonText: '继续', cancelButtonText: '取消', type: 'warning' }
      ).then(() => {
        return ElMessageBox.confirm(
          '第 2 次确认：删除后其个人数据目录会移动到 article/deleted_users 备份，该账号将无法登录。真的要删除' + who + '吗？',
          '删除确认（第 2 / 3 次）',
          { confirmButtonText: '继续', cancelButtonText: '取消', type: 'warning' }
        );
      }).then(() => {
        return ElMessageBox.confirm(
          '第 3 次确认（最后一次）：删除操作不可在线恢复！确定删除' + who + '？',
          '删除确认（第 3 / 3 次）',
          { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'error' }
        );
      }).then(() => {
        this.submitDelete(row);
      }).catch(() => {});
    },
    async submitDelete(row) {
      // 防连点：上一次请求未完成时忽略本次点击
      if (this._busy) {
        return;
      }
      this._busy = true;
      const instance = axios.create({ baseURL: '/csdn/admin_deleteuser', timeout: 20000 });
      await instance({
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        data: { ...this.authData(), target: row.mail },
      }).then((response) => {
        if (response.data.ret === 1) {
          ElMessage('已删除用户【' + row.mail + '】！');
          this.loadUsers();
        } else if (response.data.ret === -6) {
          ElMessage.error('站长账号受保护，不能删除！');
        } else if (response.data.ret === -3) {
          ElMessage.error('普通管理员不能删除管理员账号！');
        } else if (response.data.ret === -100) {
          ElMessage.error('没有管理员权限！');
        } else {
          ElMessage.error('删除失败，用户不存在！');
        }
      }).catch(() => {
        ElMessage.error('网络错误，删除失败！');
      }).finally(() => {
        this._busy = false;
      });
    },
  },
}
</script>

<style scoped>
.admin-page {
  padding: 16px;
}
.admin-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}
.admin-title {
  font-size: 20px;
  font-weight: 600;
}
.admin-search {
  width: 260px;
}
.admin-tip {
  margin-left: 10px;
  font-size: 13px;
  color: #888;
}
.admin-table {
  width: 100%;
}
/* 站点配置弹窗：搜索工具条 + 分类折叠 + 卡片化条目 + 未保存高亮 */
.siteconfig-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}
.siteconfig-search {
  width: 320px;
  flex-shrink: 0;
}
.siteconfig-count {
  font-size: 12px;
  color: #999;
}
.siteconfig-list {
  max-height: 66vh;
  overflow-y: auto;
  padding-right: 6px;
}
.siteconfig-cat-title {
  font-weight: 600;
  font-size: 14px;
}
.siteconfig-cat-count {
  font-size: 12px;
  color: #999;
  margin-left: 10px;
}
.siteconfig-item {
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 10px 12px;
  margin-bottom: 10px;
  background: #fafbfc;
}
/* 有未保存修改的条目：橙色描边 + 浅橙底，一眼可见 */
.siteconfig-item-dirty {
  border-color: #e6a23c;
  background: #fdf6ec;
}
.siteconfig-key {
  font-family: monospace;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.siteconfig-restore {
  margin-left: auto;
}
.siteconfig-help {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 15px;
  height: 15px;
  border: 1px solid #bbb;
  border-radius: 50%;
  font-size: 11px;
  font-weight: 400;
  color: #888;
  cursor: help;
  flex-shrink: 0;
}
.siteconfig-tag {
  font-size: 11px;
  color: #e6a23c;
  border: 1px solid #e6a23c;
  border-radius: 3px;
  padding: 0 4px;
}
/* 只读项标签（置灰，与可编辑项区分） */
.siteconfig-tag-readonly {
  color: #909399;
  border-color: #c0c4cc;
}
/* 已修改标签（橙色实底） */
.siteconfig-tag-dirty {
  background: #e6a23c;
  color: #fff;
  border-color: #e6a23c;
}
/* 说明全文：含义/怎么改/后果是改配置的主要依据，不做行数截断 */
.siteconfig-doc {
  font-size: 12px;
  color: #999;
  line-height: 1.6;
  margin: 2px 0 6px;
  word-break: break-all;
}
/* 数字输入统一宽度（桌面），手机端在媒体查询里放开为 100% */
.siteconfig-number {
  width: 260px;
}
.siteconfig-json :deep(textarea) {
  font-family: monospace;
  font-size: 12px;
}
/* 移动端适配：表格可横向滚动，弹窗加宽 */
@media (max-width: 768px) {
  .admin-page {
    padding: 8px;
  }
  .admin-title {
    font-size: 16px;
  }
  .admin-search {
    width: 100%;
  }
  .admin-table {
    font-size: 12px;
  }
  .admin-dialog {
    width: 95% !important;
  }
  /* 站点配置弹窗手机端：近全屏 + 搜索/输入全宽 + 说明可读 */
  .siteconfig-dialog {
    width: 98% !important;
    margin-top: 3vh !important;
  }
  .siteconfig-dialog .siteconfig-list {
    max-height: 68vh;
  }
  .siteconfig-dialog .siteconfig-search {
    width: 100%;
    flex: 1 1 100%;
  }
  .siteconfig-dialog .siteconfig-number {
    width: 100%;
  }
  .siteconfig-dialog .siteconfig-restore {
    margin-left: 0;
  }
  .siteconfig-dialog .admin-tip {
    display: block;
    margin: 8px 0 0;
    font-size: 12px;
    line-height: 1.5;
  }
}
</style>
