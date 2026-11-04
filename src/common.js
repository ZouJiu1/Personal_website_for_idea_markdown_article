import axios from 'axios'
import Cookies from 'js-cookie'

// 三级权限值，与后端 mysite/csdn/views.py 中的常量保持一致，前端统一引用，避免硬编码
//   超级管理员：管理所有用户（含普通管理员）
//   普通管理员：管理所有普通用户，但不能动超级管理员
//   普通用户  ：只能管理自己的内容
// 站长权限：999999999，仅按权限值识别站长（与邮箱/昵称无关），
//   任何管理员都不能删除/降权/重置站长账号
export const SUPER_ADMIN_QUANXIAN = '1000000';
export const ADMIN_QUANXIAN = '100';
export const NORMAL_QUANXIAN = '1';
export const OWNER_QUANXIAN = '999999999';

// 是否管理员（站长、超级管理员或普通管理员）
// 站长（999999999）视为最高管理员：首页管理按钮、admin 页守卫均走此判断
export function isAdminQuanxian(qx) {
  const v = parseInt(qx);
  return v === parseInt(OWNER_QUANXIAN)
    || v === parseInt(SUPER_ADMIN_QUANXIAN)
    || v === parseInt(ADMIN_QUANXIAN);
}

// 是否超级管理员
export function isSuperAdminQuanxian(qx) {
  return parseInt(qx) === parseInt(SUPER_ADMIN_QUANXIAN);
}

// 是否站长（仅按权限值 999999999 识别）
export function isOwnerQuanxian(qx) {
  return parseInt(qx) === parseInt(OWNER_QUANXIAN);
}

// 当前是否处于站长主页：按 URL 隐私方案下的站长 36 位 uid 判断，
// uid 由 App.vue 初始化时缓存到 localStorage 的 site_owner_uid。
// 站长主页对未登录访客开放点赞/评论/收藏入口，其他用户的主页要求先登录。
export function isOwnerPage() {
  const raw = (window.location.hash || '').replace(/^#\/?/, '');
  if (!raw) return false;
  const segs = raw.split('?')[0].split('/').filter(Boolean);
  // 跳过模块前缀（#/csdn/<uid>、#/think/<uid> 等），取真正的用户段
  const skip = ['think', 'csdn', 'book', 'zhihu', 'video', 'travel', 'commonuse',
    'everydayimg', 'admin', 'people', 'article', 'markdown_detail', 'post_article', 'detail'];
  while (segs.length && skip.includes(segs[0].toLowerCase())) segs.shift();
  const seg = segs[0] || '';
  const ownerUid = localStorage.getItem('site_owner_uid') || '';
  return !!seg && !!ownerUid && seg === ownerUid;
}

export async function saveFile() {
  try {
    // 创建一个新句柄
    //   const newHandle = await window.showSaveFilePicker();

    const newHandle = currentDirHandle.getDirectoryHandle("/home/zj/article_tmp.md", { create: true });

    // 创建一个 FileSystemWritableFileStream 用于写入
    const writableStream = await newHandle.createWritable();

    // 写入我们的文件
    await writableStream.write("This is my file content");

    // 关闭文件并将内容写入磁盘
    await writableStream.close();
  } catch (err) {
    console.error(err.name, err.message);
  }
}
export function create_cookie(mail, passw, expires) {
  let meg = "";
  try {
    meg = encodeURIComponent("expires") + "=" + encodeURIComponent(expires) + ";" +
      encodeURIComponent("mail") + "=" + encodeURIComponent(mail) + ";" +
      encodeURIComponent("password") + "=" + encodeURIComponent(passw);
  } catch (err) {
    console.error(err.name, err.message);
  }
  return meg;
}

// 登录凭据 cookie 有效期（天）：统一配置在 mysite/site_config.json 的 cookie_login_days。
// 模块级缓存 + localStorage 兜底：initCookieDays 拉取一次配置后全站同步可用 getCookieDays()，
// 各组件不再各自硬编码 30 天
let _cookieDays = parseInt(localStorage.getItem('cookie_login_days')) || 30;

// 同步获取当前 cookie 有效期（天）；配置未拉到前返回 localStorage 缓存或默认 30
export function getCookieDays() {
  return _cookieDays;
}

// 从 /csdn/getSiteConfig 拉取并缓存 cookie 有效期；成功返回配置对象，失败返回 null
export async function initCookieDays() {
  try {
    const resp = await axios.get('/csdn/getSiteConfig');
    const cfg = resp.data || {};
    const d = parseInt(cfg.cookie_login_days);
    if (!isNaN(d) && d > 0) {
      _cookieDays = d;
      localStorage.setItem('cookie_login_days', String(d));
    }
    return cfg;
  } catch (e) {
    // 配置接口不可用时保持现有缓存值
    return null;
  }
}

async function getusername(url) {
  let mail = "";
  let password = "";
  mail = Cookies.get("mail");
  password = Cookies.get("password");
  // console.log('password: ', password, mail, Cookies.get("username"));
  const instance = axios.create({
    baseURL: '/csdn/getusername',
    timeout: 20000,
  });

  // console.log(this.search_param);
  let sendret;
  if (!mail) {
    mail = "";
  }
  if (!password) {
    password = "";
  }
  await instance({
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    },
    data: { 'url': url, 'mail': mail, 'password': password },
  }).then((response) => {
    sendret = response.data;
  });
  return sendret;
}

export default getusername