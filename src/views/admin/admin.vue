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
      <el-button v-if="canCreateUser" type="warning" @click="openCreateUser">新建用户</el-button>
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
  </div>
</template>

<script>
import axios from 'axios'
import Cookies from 'js-cookie'
import { ElMessage, ElMessageBox } from 'element-plus'
import getusername from '/src/common.js'
import { ADMIN_QUANXIAN, NORMAL_QUANXIAN, SUPER_ADMIN_QUANXIAN, isAdminQuanxian, isSuperAdminQuanxian, isOwnerQuanxian } from '/src/common.js'

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
    }
  },
  computed: {
    isSuper() {
      return isSuperAdminQuanxian(this.myLevel);
    },
    // 新建用户：仅站长与超级管理员
    canCreateUser() {
      return isOwnerQuanxian(this.myLevel) || isSuperAdminQuanxian(this.myLevel);
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
        this.$router.push({ path: '/homepage@gmail.com' });
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
          this.users = response.data.users;
          if (response.data.my_level) {
            this.myLevel = response.data.my_level;
          }
        } else if (response.data.ret === -100) {
          ElMessage.error('没有管理员权限！');
          this.$router.push({ path: '/homepage@gmail.com' });
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
    confirmDelete(row) {
      ElMessageBox.confirm(
        '确定删除用户【' + row.mail + '】吗？其个人数据目录会移动到 article/deleted_users 备份。',
        '删除确认',
        { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
      ).then(() => {
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
}
</style>
